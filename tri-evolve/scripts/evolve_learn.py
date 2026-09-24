#!/usr/bin/env python3
"""Tri-Evolve 批量学习执行体（EVOLVE_LEARN · `tri-evolve learn --batch` 的实现）。

职责边界（与 SKILL.md §调度安全门 严格对齐）：
  - **默认手动**：仅接受用户显式调用；定时触发须 `--from-schedule` 且
    `meta.json` 的 `config.schedule.enabled == true`，否则拒绝（退出码 3）。
  - **批次幂等**：以 run-log.jsonl 的 `last_processed_offset` 为水位，同窗口重跑按水位续跑。
  - **不伪造验证**：本脚本只产出 **pending** 候选经验，**绝不**自行标 `verified`。
    `verified` 只能由 A/B 验证门给出（lift ≥ 阈值 且 p < 显著性阈值 且 样本 ≥ 最小值）。
    信号本身不含配对观测，故本脚本恒不满足该门 —— 这是设计，不是缺陷。
  - **未验证经验 NEVER 注入下游**：本脚本只写 `.tribro/evolve/`。

用法：
    python tri-evolve/scripts/evolve_learn.py --batch
    python tri-evolve/scripts/evolve_learn.py --batch --dry-run --json
    python tri-evolve/scripts/evolve_learn.py --batch --from-schedule   # 需先开启开关

退出码：0 成功 / 2 参数或环境错误 / 3 调度未开启被拒
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

DEFAULTS = {
    "config_ab_min_sample": 30,
    "config_ab_lift_threshold": 0.05,
    "config_ab_significance": 0.05,
    "config_signal_window": 100,
    "schedule": {"enabled": False},
}


def load_meta(evolve_dir: Path) -> dict:
    """读运行时 meta.json；缺失则用模板默认，并明确告知。"""
    cfg = dict(DEFAULTS)
    for cand in (evolve_dir / "meta.json",):
        if cand.is_file():
            try:
                cfg.update(json.loads(cand.read_text(encoding="utf-8")).get("config", {}))
            except (OSError, json.JSONDecodeError):
                print(f"[warn] meta.json 不可解析，退回默认配置：{cand}", file=sys.stderr)
    return cfg


def read_jsonl(p: Path) -> list:
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def last_watermark(run_log: list) -> int:
    for e in reversed(run_log):
        if isinstance(e.get("last_processed_offset"), int):
            return e["last_processed_offset"]
    return 0


def attribute(signals: list, cfg: dict) -> list:
    """把新增信号归因为**候选**经验（status=pending）。

    诚实说明：当前信号只有 ts/session_id/exchange_id/answer_hash/source_skill，
    不含配对观测（无 A/B 对照组），**无法计算 lift/显著性**。
    故此处只做频次与重复度归因，产出一律 pending，等待 A/B 门。
    """
    if not signals:
        return []
    by_skill = defaultdict(list)
    for s in signals:
        by_skill[str(s.get("source_skill") or "(unknown)")].append(s)

    candidates = []
    window = int(cfg.get("config_signal_window", 100) or 100)
    min_sample = int(cfg.get("config_ab_min_sample", 30) or 30)
    for skill, items in sorted(by_skill.items()):
        hashes = Counter(str(i.get("answer_hash") or "") for i in items)
        top_hash, top_n = (hashes.most_common(1) or [("", 0)])[0]
        repeat_ratio = round(top_n / len(items), 4) if items else 0.0
        # A/B 门恒不满足（无配对观测）—— 显式记录原因，避免将来误读为「通过」
        gate = {
            "lift": None,
            "p_value": None,
            "sample": len(items),
            "min_sample": min_sample,
            "passed": False,
            "blocked_reason": "signals carry no paired observation; A/B gate cannot be evaluated in batch mode",
        }
        candidates.append({
            "scope": skill,
            "signals_in_window": len(items),
            "window_limit": window,
            "dominant_answer_hash": top_hash,
            "repeat_ratio": repeat_ratio,
            "ab_gate": gate,
            "status": "pending",
        })
    return candidates


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="tri-evolve EVOLVE_LEARN 批量执行体")
    ap.add_argument("--batch", action="store_true", required=True, help="批量模式（本脚本唯一模式）")
    ap.add_argument("--from-schedule", action="store_true",
                    help="由调度器触发：须 meta.json 的 config.schedule.enabled=true，否则拒绝")
    ap.add_argument("--evolve-dir", default=".tribro/evolve", help="运行时目录（默认 .tribro/evolve）")
    ap.add_argument("--dry-run", action="store_true", help="只报告将发生什么，不写盘")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    a = ap.parse_args(argv)

    ed = Path(a.evolve_dir)
    cfg = load_meta(ed)

    if a.from_schedule and not (cfg.get("schedule") or {}).get("enabled"):
        print("[blocked] 调度触发被拒：config.schedule.enabled != true（默认 false，定时为 opt-in）",
              file=sys.stderr)
        return 3

    sig_path = ed / "signals.jsonl"
    run_log_path = ed / "run-log.jsonl"
    lock_path = ed / "run.lock"
    lessons_path = ed / "lessons.jsonl"

    signals = read_jsonl(sig_path)
    run_log = read_jsonl(run_log_path)
    wm = last_watermark(run_log)
    new = signals[wm:]
    max_n = int((cfg.get("schedule") or {}).get("max_signals_per_run", 500) or 500)
    new = new[:max_n]

    run_id = f"learn_{time.strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    candidates = attribute(new, cfg)

    result = {
        "run_id": run_id,
        "mode": "batch",
        "trigger": "schedule" if a.from_schedule else "manual",
        "started_at": started,
        "signals_total": len(signals),
        "watermark_in": wm,
        "processed": len(new),
        "last_processed_offset": wm + len(new),   # 水位键：与 last_watermark() 读取的键名必须一致
        "watermark_out": wm + len(new),
        "candidates": candidates,
        "verified": 0,
        "note": "candidates are pending by design; verified requires the A/B gate, which batch mode cannot satisfy",
        "dry_run": bool(a.dry_run),
    }

    if a.dry_run:
        result["status"] = "dry_run"
    else:
        try:
            ed.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(run_id + "\n", encoding="utf-8")
            with lessons_path.open("a", encoding="utf-8") as fh:
                for c in candidates:
                    fh.write(json.dumps({"run_id": run_id, "created_at": started, **c},
                                        ensure_ascii=False) + "\n")
            with run_log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({**result, "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                                     "status": "ok"}, ensure_ascii=False) + "\n")
            result["status"] = "ok"
        except OSError as e:
            result["status"] = "failed"
            result["error"] = str(e)
            print(f"[error] 写盘失败：{e}", file=sys.stderr)
        finally:
            try:
                lock_path.unlink(missing_ok=True)   # run.lock 只用于并发互斥，不残留
            except OSError:
                pass

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# EVOLVE_LEARN · {result['trigger']} · {result['status']}")
        print(f"信号总数 {result['signals_total']}｜水位 {wm} → {result['watermark_out']}｜本轮处理 {result['processed']}")
        print(f"候选经验 {len(candidates)} 条（全部 pending；verified = 0）")
        for c in candidates:
            print(f"  - {c['scope']}: {c['signals_in_window']} 信号, 重复度 {c['repeat_ratio']}")
        print("> 未验证经验 NEVER 注入下游。A/B 门需配对观测，批处理模式无法满足。")
    return 0 if result["status"] in ("ok", "dry_run", "dry_run") else 2


if __name__ == "__main__":
    sys.exit(main())
