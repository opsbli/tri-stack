#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`tri-verify` 确定性判定实现 —— 退出码归类 / 轮次判定 / 盖章生成。

定位（家族硬约束第 18 条：可执行实现与 prompt 分离）：
  退出码 → 归因的映射、轮次上限判定、判据印章生成，全部由本脚本承担；
  prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按结论处置」，
  NEVER 在 prompt 内联推断归因或自行判断轮次是否耗尽。

用法：
    python scripts/verify_gate.py classify --exit-code 7 [--json]
    python scripts/verify_gate.py round --log run-log.jsonl [--json]
    python scripts/verify_gate.py stamp --state fixed --engine local --cases 3/3 [--json]
    python scripts/verify_gate.py verdict --file <path>/verdict.md [--json]
    python scripts/verify_gate.py self-test

退出码：0 = 判定完成且未升级；1 = 判定结果需人工介入（升级人审 / 参数错误为 2）

真源：`references/attribution-rules.md`（归因判据）/ `references/engine-contract.md`（退出码语义）。
      修订归因口径时两处 MUST 同步修改（参考文件是标准，脚本是实现）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── 退出码 → 归因映射（真源：engine-contract.md §3.1） ──────────────────────
# C 类「环境抖动」不由语义判断，由退出码机械判定——这是本 skill 的核心机制：
# 从机制上排除「环境不稳定被误判成产品缺陷 → 自动修复制造缺陷」。
EXIT_MAP = {
    0:  {"attribution": "passed",    "counts": False, "action": "记为通过，无需归因"},
    1:  {"attribution": "pending",   "counts": True,  "action": "读证据包做 A/B 归因（动作数→需求对齐）"},
    3:  {"attribution": "C",         "counts": False, "action": "凭证/权限问题：降级到本地引擎并明示所需 scope"},
    4:  {"attribution": "B",         "counts": False, "action": "用例或运行不存在：修正 testId/runId 后重跑"},
    5:  {"attribution": "B",         "counts": False, "action": "校验错误（含证据包不同源）：修正契约或拒收证据包"},
    6:  {"attribution": "C",         "counts": False, "action": "冲突（已有运行中实例 / snapshot 生成中）：等待后重试"},
    7:  {"attribution": "C",         "counts": False, "action": "超时：先续等，不行则显式停止（避免持续计费）"},
    10: {"attribution": "C",         "counts": False, "action": "传输/网络失败：重试一次"},
    11: {"attribution": "C",         "counts": False, "action": "限流：遵守 Retry-After 后重试"},
}

ROUND_LIMIT = 2          # SKILL.md §有界循环：连续 2 轮同类失败即停
CONTRACT_REPEAT_LIMIT = 2  # 同一用例契约变更 ≥2 次 ⇒ 视为契约设计缺陷
TOTAL_ITER_LIMIT = 6     # 总迭代硬上限：防「A/B 跨用例交替」绕过"连续同类"判据而无界循环
STAMP_STATES = {
    "passed":       "功能验证: 通过（engine={engine}，用例 {cases}）",
    "fixed":        "功能验证: 修复后通过（轮次 {rounds}，归因 {attribution}）",
    "escalated":    "功能验证: 已升级人审（连续 {rounds} 轮同类失败，归因 {attribution}）",
    "not-run":      "功能验证: 未执行（{reason}）",
    "not-triggered": "功能验证: 未触发（可交付）",
}
TRIGGER_RULES = ("V1", "V2", "V3", "V4", "V5")

# ── verdict.md 判据校验（tt4 批 · 审计 M4a/M4b） ────────────────────────────
# SKILL.md §二 的三条 MUST（标签封闭 / 「修复后通过」commit 链 / 证据锚定）
# 此前只存在于 prompt 条文、**无任何可执行载体**；本块是它的可执行实现。
# 印章语法从 STAMP_STATES **单一真源派生**——新增或改名盖章态只需改 STAMP_STATES，
# 脚本校验不会与 SKILL.md 判据漂移。
VERDICT_DECL_RE = re.compile(r"(裁定|盖章|功能验证|verdict)", re.I)
# 只扫描「像声明」的行：既有裁定类关键词、又有结论类关键词。
# 否则 `## 门④·交付裁定` 这类纯节标题会被误判成表外标签（实测已踩过）。
VERDICT_VALUE_RE = re.compile(r"(通过|未执行|未触发|人审|部分|失败|阻塞|FAIL)")
COMMIT_HASH_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
EVIDENCE_RE = re.compile(
    r"(?i)\brunId\b|```|\.png\b|\.jpe?g\b|\.gif\b|\.webp\b|\b[0-9a-f]{7,40}\b")
_MD_PREFIX_RE = re.compile(r"^(?:#{1,6}|[-*>+]+|\|\s*)[\s:：]*")


def _lit(s: str) -> str:
    r"""字面量 → 正则片段：空格放宽为 `[ \t]*`、半角冒号放宽为 `[:：]`，其余逐字转义。

    逐字符处理，**不能**先 `re.escape` 再 `.replace(" ", ...)`——Python 3.14 的
    `re.escape` 会把空格转成 `\ `（反斜杠+空格），replace 命中的是那个反斜杠后面
    的空格，产物变成 `\[ \t]*`（字面 `[` + 空格 + `\t*`）而不是字符类 `[ \t]*`，
    五个盖章正则全部匹配失败（实测踩过，self-test 3 项红）。
    """
    out = []
    for ch in s:
        if ch == " ":
            out.append(r"[ \t]*")
        elif ch == ":":
            out.append("[:：]")
        else:
            out.append(re.escape(ch))
    return "".join(out)


def _stamp_pattern(tpl: str) -> "re.Pattern":
    """由 STAMP_STATES 模板派生校验正则——印章语法单一真源。

    `{var}` → `(?P<var>[^）)]+)`；其余按 `_lit` 转义。
    用 `re.finditer` 而非 `re.split`——双捕获组的 split 会把内层组名也当独立条目
    插回序列、打乱奇偶位序（实测踩过：组名变成 `{cases}` 报 bad character）。
    """
    out = []
    for m in re.finditer(r"\{(\w+)\}|([^{}]+)", tpl):
        if m.group(1):
            out.append("(?P<%s>[^）)]+)" % m.group(1))
        else:
            out.append(_lit(m.group(2)))
    return re.compile("".join(out))


STAMP_REGEXES = [(s, _stamp_pattern(t)) for s, t in STAMP_STATES.items()]


def classify(exit_code: int) -> dict:
    """退出码 → 归因归类。未知码归 C 并标记引擎契约偏离。"""
    e = int(exit_code)
    if e in EXIT_MAP:
        c = EXIT_MAP[e]
        return {"exitCode": e, "attribution": c["attribution"],
                "countsTowardRound": c["counts"], "action": c["action"],
                "deviation": False}
    # 未知退出码：按 C 类处置 + 记录契约偏离（NEVER 静默当作通过）
    return {"exitCode": e, "attribution": "C", "countsTowardRound": False,
            "action": "未知退出码：按环境抖动处置并记录「引擎契约偏离」",
            "deviation": True}


def _load_log(path: Path) -> list:
    """读 run-log.jsonl。**读前去尽 \\r** —— 本仓工作区存在 `\\r\\r\\n` 文件，
    先替 `\\r\\n` 再替 `\\r` 会把 `\\r\\r\\n` 拆成两次匹配，等于未归一化。"""
    if not path.is_file():
        return []
    raw = path.read_bytes().decode("utf-8", errors="ignore")
    out = []
    for ln in re.sub(r"\r", "", raw).split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return out


def evaluate_rounds(entries: list) -> dict:
    """轮次判定。硬规则：
      ① 连续 2 轮**同类**失败 ⇒ 升级人审；
      ② B 类（契约）与 C 类（重试）**不计入**产品轮次；
      ③ 同一用例契约变更 ≥2 次 ⇒ 视为契约设计缺陷，升级人审；
      ④ 环境抖动重试 >1 次 ⇒ 升级人审；
      ⑤ 总迭代 >6 次 ⇒ 升级人审（防「A/B 跨用例交替」绕过判据①而无界循环）。
    """
    product_rounds = 0            # 计入轮次的失败（仅 A 类）
    attr_seq = []                 # 需要计入的失败归因序列（A / uncertain）
    contract_by_case = {}         # caseId -> B 类次数
    retries = 0                   # C 类重试次数
    last_status = None

    for it in entries:
        a = (it.get("attribution") or "").strip()
        st = (it.get("status") or "").strip()
        if st:
            last_status = st
        if a == "A":
            product_rounds += 1
            attr_seq.append("A")
        elif a == "uncertain":
            attr_seq.append("uncertain")
        elif a == "B":
            # B 类虽不计入产品轮次，但**必须打断"连续同类"链**——
            # 否则 A→B→A 会被误判为「连续 2 轮 A」而提前升级（实测踩过）。
            attr_seq.append(None)
            cid = it.get("caseId") or it.get("testId") or "?"
            contract_by_case[cid] = contract_by_case.get(cid, 0) + 1
        elif a == "C":
            attr_seq.append(None)
            retries += 1

    # 连续同类（只对 A / uncertain 这类"需修复"的失败计数；B / C 作打断）
    max_consec = 0
    cur, prev = 0, object()
    for a in attr_seq:
        if a is None:
            cur, prev = 0, object()      # B / C 打断连续链
            continue
        cur = cur + 1 if a == prev else 1
        prev = a
        max_consec = max(max_consec, cur)

    repeated_contract = sorted([c for c, n in contract_by_case.items()
                                if n >= CONTRACT_REPEAT_LIMIT])

    reasons = []
    if max_consec >= ROUND_LIMIT:
        reasons.append(f"连续 {max_consec} 轮同类失败（上限 {ROUND_LIMIT}）")
    if repeated_contract:
        reasons.append(f"同一用例契约变更达 {CONTRACT_REPEAT_LIMIT} 次：{','.join(repeated_contract)}")
    if len(entries) > TOTAL_ITER_LIMIT:
        reasons.append(f"总迭代达 {len(entries)} 次（硬上限 {TOTAL_ITER_LIMIT}）")
    if retries > 1:
        reasons.append(f"环境抖动重试达 {retries} 次（上限 1）")

    escalate = bool(reasons)
    if escalate:
        state = "escalated"
    elif last_status == "passed":
        state = "fixed" if (product_rounds or retries or contract_by_case) else "passed"
    else:
        state = "passed" if last_status == "passed" else "inconclusive"

    return {
        "entries": len(entries),
        "productRounds": product_rounds,
        "contractChanges": sum(contract_by_case.values()),
        "contractChangesByCase": contract_by_case,
        "retries": retries,
        "maxConsecutiveSameAttribution": max_consec,
        "roundLimit": ROUND_LIMIT,
        "escalate": escalate,
        "escalationReasons": reasons,
        "verdictState": state,
        "lastStatus": last_status,
    }


def make_stamp(state: str, **kw) -> dict:
    """生成判据印章。MUST 从五态中恰好选一个，NEVER 自造态名。"""
    if state not in STAMP_STATES:
        raise SystemExit(f"未知盖章态：{state}；合法值：{','.join(STAMP_STATES)}")
    tpl = STAMP_STATES[state]
    need = set(re.findall(r"\{(\w+)\}", tpl))
    defaults = {"engine": "local", "cases": "n/n", "rounds": "1", "attribution": "—",
                "reason": "未指定原因"}
    ctx = {k: (kw.get(k) or defaults.get(k, "")) for k in need}
    return {"state": state, "stamp": tpl.format(**ctx),
            "blocksDelivery": state == "escalated",
            "countsAsPass": state in ("passed", "fixed")}


# ── 自检（含 mutation 断言：证明判据真的能抓住错误分类） ──────────────────────
def self_test() -> int:
    fails = []
    def eq(actual, expected, label):
        if actual != expected:
            fails.append(f"{label}: 期望 {expected!r}，实际 {actual!r}")

    # 退出码归类
    eq(classify(0)["attribution"], "passed", "exit 0")
    for code in (3, 6, 7, 10, 11):
        eq(classify(code)["attribution"], "C", f"exit {code} 应为 C")
        eq(classify(code)["countsTowardRound"], False, f"exit {code} 不应计轮次")
    eq(classify(1)["attribution"], "pending", "exit 1 应待归因")
    eq(classify(1)["countsTowardRound"], True, "exit 1 应计轮次")
    eq(classify(99)["deviation"], True, "未知退出码应标契约偏离")
    eq(classify(99)["attribution"], "C", "未知退出码应归 C")

    # mutation：若把 C 类误判为需修复（counts=True），下面这条必须变红
    eq(classify(7)["countsTowardRound"] is False, True, "mutation: C 类不得计入轮次")

    # 轮次：连续 2 轮同类 ⇒ 升级
    r = evaluate_rounds([{"round": 1, "attribution": "A", "status": "failed", "caseId": "C01"},
                         {"round": 2, "attribution": "A", "status": "failed", "caseId": "C01"}])
    eq(r["escalate"], True, "连续 2 轮 A 应升级")
    eq(r["verdictState"], "escalated", "应盖 escalated")
    # 单轮不升级
    r1 = evaluate_rounds([{"round": 1, "attribution": "A", "status": "failed", "caseId": "C01"}])
    eq(r1["escalate"], False, "单轮 A 不应升级")
    # B/C 不消耗轮次：A→B→A 不是"连续同类"
    r2 = evaluate_rounds([{"round": 1, "attribution": "A", "status": "failed", "caseId": "C01"},
                          {"round": 2, "attribution": "B", "status": "failed", "caseId": "C01"},
                          {"round": 3, "attribution": "A", "status": "failed", "caseId": "C01"}])
    eq(r2["productRounds"], 2, "A 计数应为 2")
    eq(r2["contractChanges"], 1, "B 计数应为 1")
    eq(r2["escalate"], False, "A/B 交替不构成连续同类，不应升级")
    # 契约变更 ≥2 次 ⇒ 升级
    r3 = evaluate_rounds([{"round": 1, "attribution": "B", "status": "failed", "caseId": "C01"},
                          {"round": 2, "attribution": "B", "status": "failed", "caseId": "C01"}])
    eq(r3["escalate"], True, "同用例契约变更 2 次应升级")
    # 环境重试 >1 次 ⇒ 升级
    r3b = evaluate_rounds([{"attribution": "C", "status": "failed", "caseId": "C01"},
                           {"attribution": "C", "status": "failed", "caseId": "C01"}])
    eq(r3b["escalate"], True, "环境重试 2 次应升级")
    # 总迭代硬上限 ⇒ 升级（防跨用例 A/B 交替无界）
    r3c = evaluate_rounds([{"attribution": a, "status": "failed", "caseId": f"C0{i}"}
                           for i, a in enumerate(["A", "B", "A", "B", "A", "B", "A"])])
    eq(r3c["escalate"], True, "总迭代超硬上限应升级")
    # 通过态
    r4 = evaluate_rounds([{"round": 1, "attribution": "passed", "status": "passed", "caseId": "C01"}])
    eq(r4["verdictState"], "passed", "全过应盖 passed")
    r5 = evaluate_rounds([{"round": 1, "attribution": "A", "status": "failed", "caseId": "C01"},
                          {"round": 2, "attribution": "passed", "status": "passed", "caseId": "C01"}])
    eq(r5["verdictState"], "fixed", "修后通过应盖 fixed")

    # 盖章：五态封闭
    eq(make_stamp("passed", engine="local", cases="3/3")["stamp"],
       "功能验证: 通过（engine=local，用例 3/3）", "passed 印章")
    eq(make_stamp("escalated", rounds="2", attribution="A")["blocksDelivery"], True,
       "escalated 应阻断交付")
    eq(make_stamp("not-run", reason="无可用引擎")["countsAsPass"], False,
       "not-run 不得当作通过")
    eq(make_stamp("not-triggered")["countsAsPass"], False,
       "not-triggered 不得当作通过")
    try:
        make_stamp("bogus")
        fails.append("未知盖章态应报错")
    except SystemExit:
        pass

    # verdict.md 判据校验（tt4 批 · tri-stack-train M4a/M4b 实证反例夹具）
    eq(audit_verdict_text(
        "## 最终裁定：功能验证: 通过（engine=local，用例 83/83）\n"
        "\n证据：runId r-20260928-a1b2\n")["violations"], 0, "合法盖章 + 证据锚定应零违规")
    # 反例 1：M4a/M4b 实测的表外标签「✅ 完全通过」
    v_off = audit_verdict_text("## 门④ 最终裁定：✅ 完全通过\n")
    eq(v_off["violations"], 1, "表外标签「✅ 完全通过」必须被拦")
    eq(v_off["violationDetails"][0]["type"], "off-set-label", "违规类型应为 off-set-label")
    eq(v_off["violationDetails"][0]["label"], "✅ 完全通过", "违规标签应原样回显")
    # 反例 2：M4a 实证的自相矛盾形态「✅ 通过（附本机冒烟待用户确认）」
    v2 = audit_verdict_text(
        "## 裁定：✅ 通过（附本机冒烟待用户确认）\n\n证据：runId r-1\n")
    eq(v2["violations"], 1, "「✅ 通过（附…待确认）」不是合法盖章")
    # 反例 3：「修复后通过」无 commit 链
    v3 = audit_verdict_text(
        "## 最终裁定：功能验证: 修复后通过（轮次 1，归因 C）\n\n证据：runId r-1\n")
    eq(any(d["type"] == "missing-commit-chain" for d in v3["violationDetails"]), True,
       "「修复后通过」无 commit hash 必须被拦")
    # 反例 4：「通过」无证据锚定（M4b-AC6 实证的「用户确认通过」一句话盖章）
    v4 = audit_verdict_text(
        "## 最终裁定：功能验证: 通过（engine=local，用例 3/3）\n\n用户确认通过。\n")
    eq(any(d["type"] == "missing-evidence-anchor" for d in v4["violationDetails"]), True,
       "「通过」无 runId/输出/截图必须被拦")
    # 反例 5：全文无盖章行
    v5 = audit_verdict_text("# 交付裁定\n\n一切正常。\n")
    eq(any(d["type"] == "missing-verdict" for d in v5["violationDetails"]), True,
       "无盖章行必须报 missing-verdict")
    # 纯节标题 `## 门④·交付裁定` 不是表外标签（防误报，实测已踩）
    eq(audit_verdict_text("## 门④·交付裁定\n\n一切正常。\n")["offSetLabels"], [],
       "纯节标题不得误判为表外标签")
    # mutation：若把 off-set 判成 OK，上面「✅ 完全通过」那条必须变红
    eq(v_off["violations"] > 0, True, "mutation: 表外标签不得被当作通过")

    if fails:
        print("self-test FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"self-test OK（{len(EXIT_MAP)} 个退出码映射 · 轮次上限 {ROUND_LIMIT} · {len(STAMP_STATES)} 个盖章态）")
    return 0


def audit_verdict_text(text: str) -> dict:
    """校验 verdict.md 文本。返回 {file?, states, offSetLabels, violations, violationDetails}。

    三条判据逐条对应 SKILL.md §二 条文（**非本脚本自创**）：
      ① 标签封闭——每个「裁定/盖章」声明行的标签 MUST ∈ STAMP_STATES 五态；
         命中表外标签（如「✅ 完全通过」）即判违规。
      ② commit 链——`修复后通过` MUST 引用 ≥1 个 commit hash（7-40 位 hex）。
      ③ 证据锚定——`通过` / `修复后通过` MUST 引用 runId、用例输出代码块或截图路径。
    """
    states, off_set = [], []
    in_fence = False
    for ln in re.sub(r"\r", "", text).split("\n"):
        s = ln.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not VERDICT_DECL_RE.search(s) or not VERDICT_VALUE_RE.search(s):
            continue
        hit = None
        for st, pat in STAMP_REGEXES:
            if pat.search(s):
                hit = st
                break
        if hit:
            if hit not in states:
                states.append(hit)
        else:
            lbl = _MD_PREFIX_RE.sub("", re.split(r"[:：]", s)[-1].strip() or s)
            off_set.append({"line": ln.rstrip(), "label": lbl.replace("**", "").strip()[:60]})

    vios = [{"type": "off-set-label", "detail": "标签不在封闭集内", **x} for x in off_set]
    if not states and not off_set:
        vios.append({"type": "missing-verdict",
                     "detail": "全文无「裁定/盖章」声明行——判据未产出"})
    if "fixed" in states and not COMMIT_HASH_RE.search(text):
        vios.append({"type": "missing-commit-chain",
                     "detail": "「修复后通过」未引用任何 commit hash"})
    if ("passed" in states or "fixed" in states) and not EVIDENCE_RE.search(text):
        vios.append({"type": "missing-evidence-anchor",
                     "detail": "「通过/修复后通过」未引用 runId / 用例输出代码块 / 截图路径"})
    return {"states": states, "matchedStamps": len(states),
            "offSetLabels": off_set, "violations": len(vios),
            "violationDetails": vios}


def audit_verdict(path: Path) -> dict:
    """校验单个 verdict.md 文件（`verdict --file` 入口）。"""
    res = audit_verdict_text(path.read_bytes().decode("utf-8", errors="replace"))
    res["file"] = str(path)
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-verify 确定性判定")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    sub = ap.add_subparsers(dest="cmd")

    p1 = sub.add_parser("classify", help="退出码 → 归因归类")
    p1.add_argument("--exit-code", type=int, required=True)

    p2 = sub.add_parser("round", help="轮次判定")
    p2.add_argument("--log", required=True)

    p3 = sub.add_parser("stamp", help="生成判据印章")
    p3.add_argument("--state", required=True, choices=list(STAMP_STATES))
    p3.add_argument("--engine", default=None)
    p3.add_argument("--cases", default=None)
    p3.add_argument("--rounds", default=None)
    p3.add_argument("--attribution", default=None)
    p3.add_argument("--reason", default=None)

    sub.add_parser("self-test", help="内置自检（含 mutation 断言）")

    p4 = sub.add_parser("verdict", help="校验 verdict.md：标签封闭 + commit 链 + 证据锚定")
    p4.add_argument("--file", required=True)

    args = ap.parse_args()
    if args.cmd == "self-test":
        return self_test()
    if args.cmd == "classify":
        res = classify(args.exit_code)
    elif args.cmd == "round":
        res = evaluate_rounds(_load_log(Path(args.log)))
    elif args.cmd == "stamp":
        res = make_stamp(args.state, engine=args.engine, cases=args.cases,
                         rounds=args.rounds, attribution=args.attribution, reason=args.reason)
    elif args.cmd == "verdict":
        res = audit_verdict(Path(args.file))
    else:
        ap.print_help()
        return 2

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for k, v in res.items():
            print(f"{k}: {v}")
    return 1 if (res.get("escalate") or res.get("deviation")
                 or res.get("violations")) else 0


if __name__ == "__main__":
    sys.exit(main())
