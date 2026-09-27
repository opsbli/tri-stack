#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_eval.py —— 在 golden × split 上执行确定性 scorer，产出分数台账（trace_store 落盘）。

定位
--------------------------------------------------------------------
SkillOpt 式训练循环的「验证集执行器」。三条硬纪律：

  1. **只跑确定性 scorer**（command / gate_envelope）；`pending` 的 case
     只跳过并显式计数，NEVER 退化为 LLM judge 绝对分（SkillLens 实证
     judge 准确率 46.4%，绝对分 ±8 噪音是 false-revert 源）。
  2. **split 三分纪律**：val 可反复跑驱动迭代；test 只在优化循环终局跑
     一次，NEVER 用 test 分数调 skill（防过拟合）。
  3. **每 case 落盘 per-case trace**（复用 trace_store），台账只回传路径
     与分数，诊断「走到现场」用 `trace_store.py show`。

用法
--------------------------------------------------------------------
    python ops/eval-harness/run_eval.py --split val --run-id eval-20260927
    python ops/eval-harness/run_eval.py --split val --skills tri-verify,tri-html --json
    python ops/eval-harness/run_eval.py --split test --run-id final-20260927   # 终局一次

退出码：0 = 执行的 case 全过；1 = 存在 FAIL；2 = 环境/入参错误
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = next((p for p in (HERE, *HERE.parents) if (p / ".git").exists()), HERE)
PY = sys.executable
GOLDEN_DIR = HERE / "golden"
SPLIT_FILE = HERE / "split.json"

sys.path.insert(0, str(HERE))
import gate_adapter   # noqa: E402
import trace_store    # noqa: E402


def path_get(obj, dotted: str):
    cur = obj
    for seg in dotted.split("."):
        if not isinstance(cur, dict) or seg not in cur:
            raise KeyError(dotted)
        cur = cur[seg]
    return cur


def load_golden() -> dict:
    golden = {}
    for f in sorted(GOLDEN_DIR.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        golden[d["skill"]] = d
    return golden


def run_command_case(case: dict) -> list[dict]:
    argv = [PY, *case["scorer"]["argv"]]
    r = subprocess.run(argv, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(REPO), timeout=600)
    if r.returncode == 2:
        raise RuntimeError(f"探针环境错误 rc=2：{(r.stderr or '')[:160]}")
    actual = json.loads(r.stdout)
    asserts = []
    for a in case.get("asserts", []):
        if a["kind"] != "json_eq":
            asserts.append({"name": a["kind"], "passed": False,
                            "detail": f"未知断言 kind：{a['kind']}"})
            continue
        try:
            got = path_get(actual, a["path"])
            ok = got == a["value"]
            detail = f"{a['path']} 期望 {a['value']!r} 实得 {got!r}"
        except KeyError:
            ok = False
            detail = f"{a['path']} 不存在于输出"
        asserts.append({"name": f"json_eq:{a['path']}", "passed": ok, "detail": detail})
    case["_actual"] = json.dumps(actual, ensure_ascii=False)[:2000]
    return asserts


def run_envelope_case(case: dict) -> list[dict]:
    env = gate_adapter.run_gate(case["scorer"]["skill"])
    asserts = []
    for a in case.get("asserts", []):
        if a["kind"] == "verdict_eq":
            ok = env["verdict"] == a["value"]
            asserts.append({"name": f"verdict_eq:{a['value']}", "passed": ok,
                            "detail": f"实得 {env['verdict']}（token={env['token']}）"})
        elif a["kind"] == "items_min":
            ok = len(env["items"]) >= a["value"]
            asserts.append({"name": f"items_min:{a['value']}", "passed": ok,
                            "detail": f"实得 {len(env['items'])} 条"})
        elif a["kind"] == "token_eq":
            ok = env["token"] == a["value"]
            asserts.append({"name": f"token_eq:{a['value']}", "passed": ok,
                            "detail": f"实得 {env['token']}"})
        else:
            asserts.append({"name": a["kind"], "passed": False,
                            "detail": f"未知断言 kind：{a['kind']}"})
    case["_actual"] = json.dumps({"verdict": env["verdict"], "token": env["token"],
                                  "n_items": len(env["items"])}, ensure_ascii=False)
    return asserts


def record_case(run_id: str, root: Path, case: dict, skill: str,
                asserts: list[dict], status: str | None) -> None:
    n_pass = sum(1 for x in asserts if x.get("passed"))
    ns = argparse.Namespace(
        run_id=run_id, case_id=case["case_id"], skill=skill,
        prompt=case.get("prompt", ""), expected=case.get("expected", ""),
        actual=case.get("_actual", ""), actual_file=None,
        assertions=json.dumps(asserts, ensure_ascii=False), assertions_file=None,
        meta=None, status=status)
    trace_store.cmd_record(ns, root)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["train", "val", "test", "all"], default="val")
    ap.add_argument("--skills", default=None, help="逗号分隔，默认全部 golden")
    ap.add_argument("--run-id", default=f"eval-{time.strftime('%Y%m%d-%H%M')}")
    ap.add_argument("--root", default=None, help="trace_store 存储根（默认 .tribro/evals）")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    golden = load_golden()
    split = json.loads(SPLIT_FILE.read_text(encoding="utf-8"))
    skills = [s.strip() for s in a.skills.split(",")] if a.skills else sorted(golden)
    root = Path(a.root) if a.root else trace_store.default_root()

    trace_store.write_json(root / "_probe.tmp.json", {"probe": True})  # 确保 root 可写
    (root / "_probe.tmp.json").unlink()

    # 收集 case：split 引用 golden 没有的 case_id → fail-closed 可见（孤儿告警）
    cases, orphans = [], []
    for sk in skills:
        if sk not in golden:
            print(f"[error] golden 不存在：{sk}", file=sys.stderr)
            return 2
        by_id = {c["case_id"]: c for c in golden[sk]["cases"]}
        ids = (sorted(by_id) if a.split == "all"
               else split.get(sk, {}).get(a.split, []))
        for cid in ids:
            if cid in by_id:
                cases.append((sk, by_id[cid]))
            else:
                orphans.append(cid)

    rows, n_skip = [], 0
    fails = []
    for sk, case in cases:
        kind = case["scorer"]["kind"]
        if kind == "pending":
            n_skip += 1
            record_case(a.run_id, root, case, sk, [], status="unknown")
            rows.append((case["case_id"], "skipped", "-", kind))
            continue
        try:
            asserts = (run_command_case(case) if kind == "command"
                       else run_envelope_case(case))
        except Exception as e:  # noqa: BLE001
            asserts = [{"name": "scorer_error", "passed": False,
                        "detail": f"{type(e).__name__}: {e}"[:180]}]
        n_pass = sum(1 for x in asserts if x["passed"])
        status = "pass" if n_pass == len(asserts) and asserts else "fail"
        record_case(a.run_id, root, case, sk, asserts, status=None)
        rows.append((case["case_id"], status, f"{n_pass}/{len(asserts)}", kind))
        if status == "fail":
            fails.append(case["case_id"])

    if a.json:
        print(json.dumps({"run_id": a.run_id, "split": a.split,
                          "rows": [{"case_id": r[0], "status": r[1], "score": r[2]} for r in rows],
                          "skipped": n_skip, "failed": fails}, ensure_ascii=False, indent=1))
    else:
        rd = trace_store.run_dir(root, a.run_id)
        print(f"# run {a.run_id} · split={a.split} · {len(cases)} case"
              f"（台账：{rd / 'results.tsv'}）\n")
        print(f"{'case':26} {'status':9} {'score':7} scorer")
        for cid, st, sc, kind in rows:
            print(f"{cid:26} {st:9} {sc:7} {kind}")
        n_exec = len(cases) - n_skip
        n_ok = sum(1 for r in rows if r[1] == "pass")
        print(f"\n执行 {n_exec} · pass {n_ok} · fail {len(fails)} · "
              f"skipped(pending) {n_skip} · pass-rate "
              f"{(n_ok / n_exec * 100):.1f}%" if n_exec else "\n执行 0")
        if orphans:
            print(f"[warn] split 引用了 golden 不存在的 case_id（fail-closed 可见）：{orphans}")
        if fails:
            print(f"\n失败 case（诊断用 trace_store.py show --run-id {a.run_id} --case-id <id>）：")
            for f in fails:
                print(f"  - {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
