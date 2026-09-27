#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""trace_store.py —— eval harness 的 per-case trace 落盘 + 「路径回传」机制。

为什么需要它（而不是只存分数）
--------------------------------------------------------------------
只回传总分时，诊断者只能「猜」哪里出了问题。改为把每个 case 的**完整执行记录**
落盘，再把**路径**（而非全文）交给下一轮诊断者，让它自己去现场看 —— 这正是
Meta-Harness 消融实验的结论：

    Scores Only 34.6  ->  Scores+Summary 34.9  ->  Full traces 50.0

本仓库沿用同一机制，并自带两条纪律：

  1. `results.tsv` 是 `cases/*.json` 的**投影**，每次重建 ⇒ 天然幂等
     （同一 run 重放任意次，字节不变；这是补丁层同款的「内容指纹」思路）。
  2. NEVER 把 trace 全文塞进 prompt —— `map` 只回传路径；`show` 供诊断步
     「走到现场」时按需读取单个 case。

目录结构（默认 <repo>/.tribro/evals/）
--------------------------------------------------------------------
    <root>/<run-id>/
      run.json                 运行元数据（任务集 / 起止 / harness 标识）
      cases/<case-id>.json     单 case 结构化 trace
      results.tsv              投影索引（case_id / skill / status / n_pass / n_fail / trace_path）

用法
--------------------------------------------------------------------
    python ops/eval-harness/trace_store.py init   --run-id R1 [--task-set <path>] [--harness <name>]
    python ops/eval-harness/trace_store.py record --run-id R1 --case-id tri-x-1 --skill tri-x \
        --prompt "..." --expected "..." --actual-file out.txt \
        --assertions '[{"name":"contains:X","passed":true}]'
    python ops/eval-harness/trace_store.py map    --run-id R1 [--json]
    python ops/eval-harness/trace_store.py show   --run-id R1 --case-id tri-x-1
    python ops/eval-harness/trace_store.py self-test

退出码：0 成功 / 1 自检失败 / 2 环境或入参错误
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

TSV_HEADER = ["case_id", "skill", "status", "n_pass", "n_fail", "trace_path"]


# --------------------------------------------------------------------------- #
# 基础设施
# --------------------------------------------------------------------------- #
def find_repo(start: Path) -> Path:
    """向上找含 .git 的目录；找不到则退回 start（与补丁层 apply.py 同法）。"""
    for cand in (start, *start.parents):
        if (cand / ".git").exists():
            return cand
    return start


def default_root() -> Path:
    return find_repo(Path(__file__).resolve().parent) / ".tribro" / "evals"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def write_json(p: Path, obj: dict) -> None:
    """字节级写入 UTF-8 + LF，保证可复现（不做行尾翻译）。"""
    p.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    p.write_bytes(data.encode("utf-8"))


def read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def run_dir(root: Path, run_id: str) -> Path:
    return root / run_id


def case_path(root: Path, run_id: str, case_id: str) -> Path:
    return run_dir(root, run_id) / "cases" / f"{case_id}.json"


def regen_index(root: Path, run_id: str) -> list[dict]:
    """由 cases/*.json 重建 results.tsv —— 投影即索引，天然幂等。"""
    rd = run_dir(root, run_id)
    cases_dir = rd / "cases"
    rows: list[dict] = []
    if cases_dir.is_dir():
        for f in sorted(cases_dir.glob("*.json")):
            try:
                c = read_json(f)
            except (OSError, json.JSONDecodeError):
                continue
            rows.append({
                "case_id": c.get("case_id", f.stem),
                "skill": c.get("skill", ""),
                "status": c.get("status", ""),
                "n_pass": c.get("n_pass", 0),
                "n_fail": c.get("n_fail", 0),
                "trace_path": (cases_dir / f.name).relative_to(rd).as_posix(),
            })
    lines = ["\t".join(TSV_HEADER)]
    for r in rows:
        lines.append("\t".join(str(r[k]) for k in TSV_HEADER))
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "results.tsv").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    return rows


# --------------------------------------------------------------------------- #
# 子命令
# --------------------------------------------------------------------------- #
def cmd_init(a, root: Path) -> int:
    rd = run_dir(root, a.run_id)
    if (rd / "run.json").is_file() and not a.force:
        print(f"[skip] run 已存在：{a.run_id}（用 --force 重写元数据）")
    else:
        write_json(rd / "run.json", {
            "run_id": a.run_id,
            "harness": a.harness,
            "task_set": a.task_set,
            "started_at": now_iso(),
        })
    regen_index(root, a.run_id)
    print(f"初始化完成：{rd.as_posix()}")
    return 0


def cmd_record(a, root: Path) -> int:
    if a.actual_file:
        actual = Path(a.actual_file).read_text(encoding="utf-8", errors="replace")
    else:
        actual = a.actual or ""

    if a.assertions_file:
        raw = Path(a.assertions_file).read_text(encoding="utf-8")
    else:
        raw = a.assertions or "[]"
    try:
        assertions = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[error] --assertions 不是合法 JSON：{e}", file=sys.stderr)
        return 2
    if not isinstance(assertions, list):
        print("[error] --assertions 必须是数组", file=sys.stderr)
        return 2

    n_pass = sum(1 for x in assertions if x.get("passed"))
    n_fail = len(assertions) - n_pass
    status = a.status or ("pass" if assertions and n_fail == 0 else ("fail" if assertions else "unknown"))

    meta = {}
    if a.meta:
        try:
            meta = json.loads(a.meta)
        except json.JSONDecodeError as e:
            print(f"[warn] --meta 不是合法 JSON，已忽略：{e}", file=sys.stderr)

    # 「不可修 case」出口：GT 有争议时不许无限重试，必须标记 + 记理由，供移入回归集做防护。
    if status == "unrepairable" and not str(meta.get("note", "")).strip():
        print("[error] status=unrepairable 必须附 --meta '{\"note\":\"<不可修理由与 GT 争议点>\"}'"
              "\n        （来源纪律：GT 本身有争议时，无论怎么改 skill 都过不了 —— 标「不可修」"
              "移入回归集，而非反复重试）", file=sys.stderr)
        return 2

    cp = case_path(root, a.run_id, a.case_id)
    prev = read_json(cp) if cp.is_file() else {}
    rec = {
        "case_id": a.case_id,
        "run_id": a.run_id,
        "skill": a.skill or "",
        "recorded_at": prev.get("recorded_at") or now_iso(),
        "prompt": a.prompt or "",
        "expected": a.expected or "",
        "actual": actual,
        "assertions": assertions,
        "n_pass": n_pass,
        "n_fail": n_fail,
        "status": status,
        "meta": meta,
    }
    write_json(cp, rec)
    regen_index(root, a.run_id)
    print(cp.as_posix())
    return 0


def cmd_map(a, root: Path) -> int:
    rd = run_dir(root, a.run_id)
    rows = regen_index(root, a.run_id)
    if a.json:
        print(json.dumps({
            "run_id": a.run_id,
            "run_dir": rd.as_posix(),
            "n_cases": len(rows),
            "trace_paths": {r["case_id"]: f"{rd.as_posix()}/{r['trace_path']}" for r in rows},
        }, ensure_ascii=False, indent=2))
        return 0
    print(f"# run {a.run_id} · {len(rows)} 个 case（以下仅为**路径**，全文请用 show）")
    for r in rows:
        print(f"  {r['case_id']:28} {r['status']:7} {r['n_pass']}/{r['n_pass'] + r['n_fail']}  "
              f"{rd.as_posix()}/{r['trace_path']}")
    return 0


def cmd_show(a, root: Path) -> int:
    cp = case_path(root, a.run_id, a.case_id)
    if not cp.is_file():
        print(f"[error] case 不存在：{a.case_id}", file=sys.stderr)
        return 2
    print(cp.read_text(encoding="utf-8"))
    return 0


def cmd_self_test(a, root: Path) -> int:
    """端到端自检：落盘 -> 投影重建 -> 幂等（重放两次字节一致）-> 路径回传。"""
    tmp = Path(tempfile.mkdtemp(prefix="trace_store_selftest_"))
    fails: list[str] = []
    try:
        rid = "selftest"
        cases = [
            ("tri-x-1", "tri-x", [{"name": "contains:A", "passed": True}, {"name": "regex:B", "passed": True}], "pass"),
            ("tri-x-2", "tri-x", [{"name": "contains:C", "passed": False}, {"name": "regex:D", "passed": True}], "fail"),
            ("tri-y-1", "tri-y", [{"name": "json_schema:E", "passed": True}], "pass"),
        ]
        for cid, sk, asrt, _st in cases:
            ns = argparse.Namespace(run_id=rid, case_id=cid, skill=sk, prompt="p", expected="e",
                                    actual="a", actual_file=None,
                                    assertions=json.dumps(asrt), assertions_file=None,
                                    meta=None, status=None)
            with contextlib.redirect_stdout(io.StringIO()):
                cmd_record(ns, tmp)

        rd = run_dir(tmp, rid)
        tsv = rd / "results.tsv"
        if not tsv.is_file():
            fails.append("results.tsv 未生成")
        body = tsv.read_text(encoding="utf-8").strip().splitlines()
        if len(body) != len(cases) + 1:
            fails.append(f"results.tsv 行数应为 {len(cases)+1}，实为 {len(body)}")

        # 幂等：快照 -> 原样重放 -> 字节必须一致
        snap = {p.name: p.read_bytes() for p in sorted(rd.rglob("*")) if p.is_file()}
        for cid, sk, asrt, _st in cases:
            ns = argparse.Namespace(run_id=rid, case_id=cid, skill=sk, prompt="p", expected="e",
                                    actual="a", actual_file=None,
                                    assertions=json.dumps(asrt), assertions_file=None,
                                    meta=None, status=None)
            with contextlib.redirect_stdout(io.StringIO()):
                cmd_record(ns, tmp)
        snap2 = {p.name: p.read_bytes() for p in sorted(rd.rglob("*")) if p.is_file()}
        if snap != snap2:
            fails.append("幂等失败：重放后字节发生变化")

        # 状态判定
        c2 = read_json(case_path(tmp, rid, "tri-x-2"))
        if c2["status"] != "fail" or c2["n_fail"] != 1 or c2["n_pass"] != 1:
            fails.append(f"tri-x-2 状态判定错误：{c2['status']} {c2['n_pass']}/{c2['n_fail']}")

        # 路径回传：map 的路径必须真实存在，且不含全文
        rows = regen_index(tmp, rid)
        for r in rows:
            p = rd / r["trace_path"]
            if not p.is_file():
                fails.append(f"trace 路径不存在：{r['trace_path']}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        print("[self-test] FAIL")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"[self-test] PASS · {len(cases)} 个 case，幂等（重放字节一致），路径回传可达")
    return 0


# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="eval harness per-case trace 落盘 + 路径回传")
    ap.add_argument("--root", default=None, help=f"存储根（默认 {default_root().as_posix()}）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init"); p.add_argument("--run-id", required=True)
    p.add_argument("--task-set", default=""); p.add_argument("--harness", default="darwin")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("record")
    p.add_argument("--run-id", required=True); p.add_argument("--case-id", required=True)
    p.add_argument("--skill", default="")
    p.add_argument("--prompt", default=""); p.add_argument("--expected", default="")
    p.add_argument("--actual", default=""); p.add_argument("--actual-file", default=None)
    p.add_argument("--assertions", default=None); p.add_argument("--assertions-file", default=None)
    p.add_argument("--meta", default=None); p.add_argument("--status", default=None)

    p = sub.add_parser("map"); p.add_argument("--run-id", required=True)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("show")
    p.add_argument("--run-id", required=True); p.add_argument("--case-id", required=True)

    sub.add_parser("self-test")

    a = ap.parse_args(argv)
    root = Path(a.root) if a.root else default_root()
    fn = {"init": cmd_init, "record": cmd_record, "map": cmd_map,
          "show": cmd_show, "self-test": cmd_self_test}[a.cmd]
    return fn(a, root)


if __name__ == "__main__":
    sys.exit(main())
