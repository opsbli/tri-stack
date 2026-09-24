#!/usr/bin/env python3
"""Tri-Evolve 批量学习执行体（EVOLVE_LEARN · `tri-evolve learn --batch` 的实现）。

边界（对齐 SKILL.md §调度安全门）：
  - 默认手动；定时须 --from-schedule 且 config.schedule.enabled=true，否则拒绝（退出码 3）
  - 批次幂等：水位取 run-log.jsonl 的 last_processed_offset
  - 不伪造验证：批处理只产 pending。verified 只能来自 ① A/B 门（需配对观测，批处理恒不满足）
    或 ② 人工采纳（--approve，举证方是人）。自动化 NEVER 自行标 verified
  - 未验证经验 NEVER 注入下游；只写 .tribro/evolve/

用法：
    --batch [--from-schedule] [--dry-run] [--json]
    --list [--status pending|verified|rejected]
    --approve <cand_id> [--note ...]   /   --reject <cand_id> [--note ...]
退出码：0 成功 / 2 环境错误 / 3 调度未开启被拒 / 4 候选不存在
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

DEFAULTS = {"config_ab_min_sample": 30, "config_signal_window": 100, "schedule": {"enabled": False}}


def sha8(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:8]


def load_meta(ed: Path) -> dict:
    cfg = dict(DEFAULTS)
    f = ed / "meta.json"
    if f.is_file():
        try:
            cfg.update(json.loads(f.read_text(encoding="utf-8")).get("config", {}))
        except (OSError, json.JSONDecodeError):
            print(f"[warn] meta.json 不可解析，退回默认：{f}", file=sys.stderr)
    return cfg


def read_jsonl(p: Path) -> list:
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def last_watermark(run_log: list) -> int:
    for e in reversed(run_log):
        if isinstance(e.get("last_processed_offset"), int):
            return e["last_processed_offset"]
    return 0


def cand_id(scope: str, dom: str) -> str:
    return "cand_" + sha8(f"{scope}|{dom}")


def status_map(lessons: list) -> dict:
    st = {}
    for e in lessons:
        cid = e.get("candidate_id")
        if not cid:
            continue
        if e.get("kind") == "verification":
            st[cid] = {"status": e.get("status"), "by": e.get("verified_by"),
                       "at": e.get("verified_at"), "note": e.get("note", "")}
        elif "status" in e:
            st.setdefault(cid, {"status": e["status"], "by": "batch",
                                "at": e.get("created_at"), "note": ""})
    return st


def feedback_index(signals: list) -> dict:
    idx = defaultdict(list)
    for s in signals:
        if s.get("kind") == "feedback" and s.get("target_exchange_id"):
            idx[str(s["target_exchange_id"])].append(s)
    return idx


def attribute(signals: list, cfg: dict, fb: dict) -> list:
    eps = [s for s in signals if s.get("kind") != "feedback"]
    if not eps:
        return []
    by_scope = defaultdict(list)
    for s in eps:
        by_scope[str(s.get("source_skill") or "(unknown)")].append(s)
    out, min_n = [], int(cfg.get("config_ab_min_sample", 30) or 30)
    for scope, items in sorted(by_scope.items()):
        h = Counter(str(i.get("answer_hash") or "") for i in items)
        dom, top = (h.most_common(1) or [("", 0)])[0]
        neg = sum(1 for i in items
                  for f in fb.get(str(i.get("exchange_id") or ""), [])
                  if f.get("polarity") == "negative")
        out.append({
            "kind": "candidate", "candidate_id": cand_id(scope, dom), "scope": scope,
            "signals_in_window": len(items),
            "window_limit": int(cfg.get("config_signal_window", 100) or 100),
            "dominant_answer_hash": dom,
            "repeat_ratio": round(top / len(items), 4) if items else 0.0,
            "negative_feedback": neg,
            "ab_gate": {"lift": None, "p_value": None, "sample": len(items), "min_sample": min_n,
                        "passed": False,
                        "blocked_reason": "signals carry no paired observation; A/B gate cannot be evaluated in batch mode",
                        "manual_path": "use --approve <candidate_id> (human is the evidence provider)"},
            "status": "pending",
        })
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="tri-evolve EVOLVE_LEARN 执行体")
    m = ap.add_mutually_exclusive_group(required=True)
    m.add_argument("--batch", action="store_true")
    m.add_argument("--list", action="store_true")
    m.add_argument("--approve", metavar="CAND_ID")
    m.add_argument("--reject", metavar="CAND_ID")
    ap.add_argument("--from-schedule", action="store_true")
    ap.add_argument("--note", default="")
    ap.add_argument("--status", default=None)
    ap.add_argument("--evolve-dir", default=".tribro/evolve")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    ed = Path(a.evolve_dir)
    cfg = load_meta(ed)
    sig_path, rl_path, lock_path, ls_path = (ed / "signals.jsonl", ed / "run-log.jsonl",
                                             ed / "run.lock", ed / "lessons.jsonl")

    if a.approve or a.reject:
        st = status_map(read_jsonl(ls_path))
        cid = a.approve or a.reject
        if cid not in st:
            print(f"[error] 候选不存在：{cid}（用 --list 查看）", file=sys.stderr)
            return 4
        rec = {"kind": "verification", "candidate_id": cid,
               "status": "verified" if a.approve else "rejected", "verified_by": "human",
               "verified_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "note": a.note}
        if a.dry_run:
            print(json.dumps({**rec, "dry_run": True}, ensure_ascii=False))
            return 0
        ed.mkdir(parents=True, exist_ok=True)
        with ls_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(("已采纳为 verified：" if a.approve else "已否掉：") + cid)
        return 0

    if a.list:
        rows = [{"candidate_id": k, **v} for k, v in status_map(read_jsonl(ls_path)).items()
                if not a.status or v.get("status") == a.status]
        if a.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print(f"# 候选 {len(rows)} 条" + (f"（status={a.status}）" if a.status else ""))
            for r in sorted(rows, key=lambda x: x["candidate_id"]):
                print(f"  {r['candidate_id']}  {r.get('status','?'):9} by={r.get('by','?'):6} {r.get('note','')}")
        return 0

    if a.from_schedule and not (cfg.get("schedule") or {}).get("enabled"):
        print("[blocked] 调度触发被拒：config.schedule.enabled != true（默认 false，定时为 opt-in）",
              file=sys.stderr)
        return 3

    signals, run_log = read_jsonl(sig_path), read_jsonl(rl_path)
    wm = last_watermark(run_log)
    new = signals[wm:][:int((cfg.get("schedule") or {}).get("max_signals_per_run", 500) or 500)]
    run_id = f"learn_{time.strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    cands = attribute(new, cfg, feedback_index(signals))
    result = {"run_id": run_id, "mode": "batch",
              "trigger": "schedule" if a.from_schedule else "manual", "started_at": started,
              "signals_total": len(signals), "watermark_in": wm, "processed": len(new),
              "last_processed_offset": wm + len(new), "watermark_out": wm + len(new),
              "candidates": cands, "verified": 0,
              "note": "candidates are pending by design; verified requires A/B gate or human approval",
              "dry_run": bool(a.dry_run)}

    if a.dry_run:
        result["status"] = "dry_run"
    else:
        try:
            ed.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(run_id + "\n", encoding="utf-8")
            with ls_path.open("a", encoding="utf-8") as fh:
                for c in cands:
                    fh.write(json.dumps({"run_id": run_id, "created_at": started, **c},
                                        ensure_ascii=False) + "\n")
            with rl_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({**result, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                                     "status": "ok"}, ensure_ascii=False) + "\n")
            result["status"] = "ok"
        except OSError as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"[error] 写盘失败：{e}", file=sys.stderr)
        finally:
            try:
                lock_path.unlink(missing_ok=True)
            except OSError:
                pass

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# EVOLVE_LEARN · {result['trigger']} · {result['status']}")
        print(f"信号总数 {result['signals_total']}｜水位 {wm} → {result['watermark_out']}｜本轮处理 {result['processed']}")
        print(f"候选 {len(cands)} 条（全部 pending；verified = 0）")
        for c in cands:
            print(f"  - {c['candidate_id']}  scope={c['scope']}  信号={c['signals_in_window']}  "
                  f"重复度={c['repeat_ratio']}  负反馈={c['negative_feedback']}")
        print("> 未验证经验 NEVER 注入下游。采纳请用 --approve <candidate_id>（人或 A/B 门举证）。")
    return 0 if result["status"] in ("ok", "dry_run") else 2


if __name__ == "__main__":
    sys.exit(main())
