#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""电池运行器 —— 跑 case 电池，产出**案级台账**，供门④.5（acceptance_diff.py）消费。

判据唯一真源：references/case-battery-spec.md
本脚本 ONLY 负责「物化 case → 调门④ → 归一成案级台账」；不承担任何判据解释。

用法：
    python scripts/battery_run.py --split search            # 开发调试（可反复跑）
    python scripts/battery_run.py --i-am-accepting --split all
                                                            # 验收时才跑 eval 组（需显式开关）
    python scripts/battery_run.py --split all --ledger out.json
                                                            # 输出 acceptance_diff 可直接读的台账
    python scripts/battery_run.py --emit-expect out.json    # 重算全部 case 的裁决（校准用）

退出码：0 = 全部 case 与期望一致；1 = 存在不一致；2 = 环境 / 输入错误

split 纪律（硬性，见 spec §三）：
    search 组允许在开发期反复运行；eval 组**只允许在验收时运行**，
    故 `--split eval|all` 必须与 `--i-am-accepting` 同时出现，否则拒绝执行。
    这防的是「对着 eval 组调参」这一过拟合形态本身。
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TF = Path(__file__).resolve().parent.parent
REPO = TF.parent
GATE = TF / "scripts" / "compliance_check.py"
BATTERY = TF / "tests" / "battery" / "battery.json"
FIXTURES = TF / "tests" / "battery" / "fixtures.json"
SEALED = TF / "tests" / "battery" / "_sealed" / "eval-expect.json"

IGNORE = shutil.ignore_patterns("__pycache__", ".git", "node_modules", ".tribro")


def die(msg, code=2):
    print("ERROR: " + msg, file=sys.stderr)
    return code


def load(p):
    p = Path(p)
    if not p.is_file():
        raise FileNotFoundError(str(p))
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def tf_version():
    """取本包 frontmatter version，用于台账盖章。"""
    try:
        txt = (TF / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    m = re.search(r"(?m)^version:\s*(\S+)", txt)
    return m.group(1) if m else None


def token_of(res):
    """裁决归一 —— token 是**机械比对主键**，clauses 仅作解释（见门④.5 口径）。

    token 形态：`PASS` / `FAIL:<必检失败条目号,升序>`，末尾追加 `+adv<建议项失败条目号>`（若有）。

    为何 token 要带条目号（实测 2026-09-27）：新增**建议项**条目**不改变** PASS/FAIL 总判，
    只改变条目集 —— 若 token 只编码总判，这类变更会被归为「未翻转任何 case」而 B1 FAIL。
    MANUAL 项**不入 token**（它是待人工项，不是结论），只留在 clauses。
    """
    items = res.get("items", [])
    blocking = sorted(x["n"] for x in items if x["status"] == "FAIL" and not x.get("advisory"))
    adv = sorted(x["n"] for x in items if x["status"] == "FAIL" and x.get("advisory"))
    nonpass = sorted(x["n"] for x in items if x["status"] in ("FAIL", "MANUAL"))
    tok = "PASS" if not blocking else "FAIL:" + ",".join(str(n) for n in blocking)
    if adv:
        tok += "+adv" + ",".join(str(n) for n in adv)
    return tok, ["#%d" % n for n in nonpass], blocking


def run_gate(target_dir, gate):
    r = subprocess.run([sys.executable, str(gate), "--dir", str(target_dir), "--json"],
                       capture_output=True, text=True, timeout=180)
    if not r.stdout.strip():
        raise RuntimeError(f"门④ 无输出（rc={r.returncode}）：{r.stderr.strip()[:300]}")
    return json.loads(r.stdout)["results"][0]


def apply_ops(dst: Path, ops):
    for op in ops:
        p = dst / op["path"]
        kind = op["op"]
        if kind == "append":
            p.write_text(p.read_text(encoding="utf-8") + op["text"], encoding="utf-8")
        elif kind == "prepend":
            p.write_text(op["text"] + p.read_text(encoding="utf-8"), encoding="utf-8")
        elif kind == "regex_replace":
            txt = p.read_text(encoding="utf-8")
            p.write_text(re.sub(op["pattern"], op["repl"], txt,
                                count=op.get("count", 0), flags=re.M), encoding="utf-8")
        elif kind == "delete_file":
            p.unlink()
        elif kind == "add_file":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(op["text"], encoding="utf-8")
        else:
            raise ValueError("未知 op：" + kind)


def run_case(case, fixtures, tmp, gate) -> dict:
    """物化一个 case 并跑门④，返回归一后的案级记录。"""
    if case["kind"] == "real":
        target = REPO / case["target"]
        if not (target / "SKILL.md").is_file():
            raise FileNotFoundError(f"real case 目标不是 skill 包：{target}")
        res = run_gate(target, gate)
        origin = target.as_posix()
    elif case["kind"] == "fixture":
        spec = fixtures["fixtures"][case["target"]]
        base = spec["base"]
        dst = tmp / case["case_id"] / base
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(REPO / base, dst, ignore=IGNORE)
        apply_ops(dst, spec.get("ops", []))
        res = run_gate(dst, gate)
        origin = f"fixture:{case['target']}(base={base}, ops={len(spec.get('ops', []))})"
    else:
        raise ValueError("未知 kind：" + str(case["kind"]))

    tok, clauses, blocking = token_of(res)
    evidence = ["§判据清单 #%d %s：%s" % (x["n"], x["name"], x["evidence"])
                for x in res.get("items", []) if x["status"] == "FAIL"]
    return {
        "case_id": case["case_id"],
        "verdict": res.get("verdict"),
        "verdict_token": tok,
        "clauses": clauses,
        "evidence": evidence,
        "origin": origin,
        "split": case["split"],
        "failed_items": blocking,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", default=str(BATTERY))
    ap.add_argument("--fixtures", default=str(FIXTURES))
    ap.add_argument("--sealed", default=str(SEALED))
    ap.add_argument("--split", choices=["search", "eval", "all"], default="search")
    ap.add_argument("--i-am-accepting", action="store_true",
                    help="运行 eval 组所必需的显式开关（防对着 eval 组调参）")
    ap.add_argument("--gate", default=str(GATE),
                    help="门禁脚本路径（用于门④.5 对比改前/改后两版脚本；默认取本包的 compliance_check.py）")
    ap.add_argument("--attribute", default=None,
                    help="op_id=条目号 逗号分隔（如 'op-01=23,op-02=24'）：把 case 的结论变化机械归因到引入该条目的 op")
    ap.add_argument("--stamp-version", default=None,
                    help="覆盖台账里的 version 字段（对比改前/改后两版门禁时用，如 --stamp-version 1.0.6）")
    ap.add_argument("--ledger", default=None, help="输出 acceptance_diff 可直接读的台账 JSON")
    ap.add_argument("--emit-expect", default=None, help="重算全部 case 的裁决并写出（校准用）")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.split in ("eval", "all") and not a.i_am_accepting:
        return die("`--split eval|all` 只能在变更验收时运行，须同时给出 --i-am-accepting。\n"
                   "        开发调试请用 `--split search`（split 纪律见 case-battery-spec.md §三）。")

    try:
        battery = load(a.battery)
        fixtures = load(a.fixtures)
        sealed = load(a.sealed) if Path(a.sealed).is_file() else {"cases": []}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return die(str(e))

    cases = [c for c in battery["cases"] if a.split == "all" or c["split"] == a.split]
    if not cases:
        return die("没有匹配 split 的 case")

    # op → 该 op 引入的条目号。归因口径：仅当该条目号出现在 case 的条款集里时才算它引起。
    # 局限（MUST 随用随声明）：若某条目号在变更前已存在于该 case，本口径会误归因；
    # 故它只适用于「op 引入的条目号此前不存在于该 case 条款集」的情形（本次即如此）。
    attr = []
    if a.attribute:
        for pair in a.attribute.split(","):
            oid, _, num = pair.partition("=")
            if oid.strip() and num.strip():
                attr.append((oid.strip(), "#" + num.strip().lstrip("#")))

    expect = {c["case_id"]: c.get("expected") for c in battery["cases"]}
    for c in sealed.get("cases", []):
        expect[c["case_id"]] = {"verdict_token": c["verdict_token"], "clauses": c["clauses"]}

    tmp = Path(tempfile.mkdtemp(prefix="battery-"))
    records, mismatches, errors = [], [], []
    checked = 0
    try:
        for case in cases:
            try:
                rec = run_case(case, fixtures, tmp, a.gate)
            except Exception as e:  # noqa: BLE001
                errors.append((case["case_id"], f"{type(e).__name__}: {e}"))
                continue
            records.append(rec)
            rec["changed_by"] = [oid for oid, cl in attr if cl in rec["clauses"]]
            exp = expect.get(case["case_id"])
            if exp:
                checked += 1
            if exp and (exp.get("verdict_token") != rec["verdict_token"]
                        or sorted(exp.get("clauses") or []) != sorted(rec["clauses"])):
                mismatches.append({
                    "case_id": case["case_id"],
                    "expected": {"token": exp.get("verdict_token"), "clauses": exp.get("clauses")},
                    "actual": {"token": rec["verdict_token"], "clauses": rec["clauses"]},
                })
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if a.emit_expect:
        Path(a.emit_expect).write_text(json.dumps(
            {"spec": "battery_run.py --emit-expect",
             "cases": [{k: r[k] for k in ("case_id", "verdict", "verdict_token", "clauses", "split")}
                       for r in records]},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"期望候选已写出：{a.emit_expect}（{len(records)} 条）")

    if a.ledger:
        Path(a.ledger).write_text(json.dumps(
            {"label": f"battery:{a.split}", "skill": "tri-forge",
             "version": a.stamp_version or tf_version(),
             "battery_version": battery.get("version"),
             "gate": Path(a.gate).as_posix(),
             "cases": records}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"台账已写出：{a.ledger}（{len(records)} 条，可直接喂 acceptance_diff.py）")

    if a.json:
        print(json.dumps({"records": records, "mismatches": mismatches}, ensure_ascii=False, indent=2))
    else:
        print(f"# 电池运行 · split={a.split} · {len(records)} 条\n")
        print("| case_id | split | verdict_token | clauses |")
        print("|---|---|---|---|")
        for r in records:
            print(f"| {r['case_id']} | {r['split']} | `{r['verdict_token']}` | {' '.join(r['clauses']) or '—'} |")
        for cid, msg in errors:
            print(f"\n🔴 {cid} 运行异常：{msg}")
        if mismatches:
            print(f"\n**与期望不一致 {len(mismatches)} 条**")
            for m in mismatches:
                print(f"- {m['case_id']}：期望 {m['expected']} → 实际 {m['actual']}")
        elif checked and checked == len(records):
            print(f"\n✅ 已核对的 {checked}/{len(records)} 条全部与期望一致")
        elif checked:
            print(f"\n✅ 已核对的 {checked}/{len(records)} 条与期望一致；"
                  f"其余 {len(records) - checked} 条无期望，仅记录")
        else:
            print(f"\n⚠️ 本次 {len(records)} 条**均无期望可比** —— 只产出台账，未做一致性判定")

    return 1 if (mismatches or errors) else 0


if __name__ == "__main__":
    sys.exit(main())
