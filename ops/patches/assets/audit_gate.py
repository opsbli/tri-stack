#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-req-audit 门④ 机械守卫 —— 对抗维 / 独立性 / 可复算 / 单调性的「牙」。

存在的理由：本 skill 原有的判据集是**在场性**判据（齐备吗 / 清晰吗 / 标出处了吗），
通过方式是「确认存在」。若 D9 对抗维、`independence=` 独立性声明、可复算引文、
跨轮单调性**只写在 prompt 里**，它们就是装饰 —— 同一个 agent 可以写一份「看起来很完整」
的报告而四条全部跳过（本 skill 的原始缺陷正是「自审自过、多轮自我收敛」）。
本脚本把四条规则落成**可执行判据**，使「删掉对抗小节仍判通过」在机械上不可能。

用法：
    python scripts/audit_gate.py --report <req-audit-report.md> [--ledger round-ledger.jsonl]
    python scripts/audit_gate.py --self-test

退出码：0 = 全过；1 = 存在违规；2 = 用法或读文件错误。

判据编号（与 `references/audit-dimensions.md` 对应）：
    R1  D9 对抗维        —— 报告 MUST 含「对抗式审查结论」小节，且 ≥3 条可证伪场景
    R2  H2 独立性声明    —— 报告 MUST 含 `independence=<v>`，v 为三个合法取值之一
    R3  H2 同源禁自称独立 —— independence=same-agent 时 MUST 写「非独立」，且禁「独立审核 / 独立第三方」
    R4  H5 可复算证据    —— 问题清单中所有 P0 / P1 行的「证据位置」列 MUST 含 `文件:行号`
    L2  H3 跨轮单调性    —— 账本中 P0 / P1 下降而本轮 `new_evidence=0` ⇒ 判「收敛造假」违规
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

INDEP = ("same-agent", "cross-context", "cross-model")
SECT = re.compile(r"^#{2,4}[ \t]*.*对抗式审查结论.*$", re.M)
ANY_H = re.compile(r"^#{1,6}[ \t]", re.M)
SCEN = re.compile(r"^[ \t]*(?:[-*]|\d+\.)[ \t]")
CITE = re.compile(r":\s*\d+")


def _section(txt: str, rx: re.Pattern) -> str:
    """取标题命中行之后、到下一个标题之前的正文（标题本身不含在内）。"""
    m = rx.search(txt)
    if not m:
        return ""
    nxt = ANY_H.search(txt, m.end())
    return txt[m.end(): nxt.start() if nxt else len(txt)]


def check_report(txt: str) -> list[str]:
    bad: list[str] = []

    # ---- R1 · D9 对抗维 -------------------------------------------------
    sec = _section(txt, SECT)
    if not sec.strip():
        bad.append("R1 缺「对抗式审查结论」小节 —— 对抗维未执行"
                   "（判据：报告无该小节 = 违规，NEVER 以「既有维度全绿」代替「已尝试证伪」）")
    else:
        n = sum(1 for ln in sec.splitlines()
                if SCEN.match(ln) and ("→" in ln or "->" in ln))
        if n < 3:
            bad.append(f"R1 「对抗式审查结论」仅 {n} 条可证伪场景，要求 ≥3"
                       "（格式：`- 若按 §X 开工 → 下游会做出 Y → 证据位置`）")

    # ---- R2 / R3 · 独立性声明 -------------------------------------------
    vals = re.findall(r"independence[ \t]*=[ \t]*`?([A-Za-z-]+)`?", txt)
    if not vals:
        bad.append("R2 缺 `independence=` 声明（取值：" + " / ".join(INDEP) + "）")
    elif vals[0] not in INDEP:
        bad.append(f"R2 `independence={vals[0]}` 非法取值（合法：" + " / ".join(INDEP) + "）")
    elif vals[0] == "same-agent":
        if "非独立" not in txt:
            bad.append("R3 independence=same-agent 但报告未写明「本次审核非独立第三方」")
        if "独立审核" in txt:
            bad.append("R3 independence=same-agent 但报告出现「独立审核」"
                       "（同源不得自称独立；委派≠独立）")
        if re.search(r"(?<!非)独立第三方", txt):
            bad.append("R3 independence=same-agent 但报告出现未被「非」否定的「独立第三方」")

    # ---- R4 · P0 / P1 必须可复算（表头驱动定位，勿硬编码列号）-----------
    lines = txt.splitlines()
    for i, ln in enumerate(lines):
        if not ln.startswith("|"):
            continue
        # 只认「表头行」：本行含 级别 与 证据位置
        parts = ln.split("|")
        if len(parts) < 4:
            continue
        head = [c.strip() for c in parts[1:-1]]
        if "级别" not in head or "证据位置" not in head:
            continue
        li, ei = head.index("级别"), head.index("证据位置")
        # 往下读数据行，直到非表格行
        for row in lines[i + 2:]:
            if not row.startswith("|"):
                break
            cells = [c.strip() for c in row.split("|")[1:-1]]
            if len(cells) <= max(li, ei):
                continue
            lvl = cells[li].replace("*", "").strip()
            if not re.match(r"^P[01]\b", lvl):
                continue
            ev = cells[ei]
            if not CITE.search(ev):
                bad.append(f"R4 {lvl} 条目缺可复算引文：证据位置=`{ev}`"
                           "（P0 / P1 MUST 附 `文件:行号`；无引文须降为 P2 并标 `evidence=unverifiable`）")
    return bad


def check_ledger(txt: str) -> list[str]:
    """L2 · 跨轮单调性：P0/P1 下降而本轮 new_evidence=0 ⇒ 收敛造假。"""
    bad: list[str] = []
    rows: list[dict] = []
    for i, ln in enumerate(txt.splitlines(), 1):
        s = ln.strip()
        if not s:
            continue
        try:
            o = json.loads(s)
        except json.JSONDecodeError:
            bad.append(f"L1 账本第 {i} 行不是合法 JSON")
            continue
        for k in ("round", "p0", "p1", "new_evidence"):
            if k not in o:
                bad.append(f"L1 账本第 {i} 行缺字段 `{k}`")
        rows.append(o)
    prev = None
    for o in rows:
        if prev is not None:
            drop = (o.get("p0", 0) < prev.get("p0", 0)) or (o.get("p1", 0) < prev.get("p1", 0))
            if drop and not o.get("new_evidence"):
                bad.append(
                    f"L2 第 {o.get('round')} 轮：P0/P1 由 "
                    f"(P0={prev.get('p0')}, P1={prev.get('p1')}) 降至 "
                    f"(P0={o.get('p0')}, P1={o.get('p1')}) 而 new_evidence=0 —— "
                    "「多轮自我收敛」嫌疑，MUST 强制升级人审，本轮不得判「可开工 / 有条件开工」"
                )
        prev = o
    return bad


# ---------------------------------------------------------------------------
# 自证夹具（self-test）：每条判据都要有「正例通过 + 反例命中」两条
# ---------------------------------------------------------------------------
_OK = """## 四、问题清单

| # | 级别 | 维度 | 问题 | 证据位置 | 来源 | 修订建议 |
|---|---|---|---|---|---|---|
| 1 | P0 | D3 | 验收标准不可判定 | `requirements.md:88` 「界面友好」 | local | 改可判定 |

## 六、对抗式审查结论（D9）

- 若按 §二 开工 → 下游会把「最近 30 天」实现为自然日 → 证据位置 `requirements.md:41`
- 若按 §四 开工 → 下游会漏做并发扣减 → 证据位置 `requirements.md:77`
- 若按 §七 开工 → 下游会把手机号明文入库 → 证据位置 `requirements.md:120`

## 七、结论可信度

independence=same-agent（本次审核非独立第三方）
"""

_NO_D9 = _OK.replace("## 六、对抗式审查结论（D9）\n\n- 若按 §二 开工 → 下游会把「最近 30 天」实现为自然日 → 证据位置 `requirements.md:41`\n- 若按 §四 开工 → 下游会漏做并发扣减 → 证据位置 `requirements.md:77`\n- 若按 §七 开工 → 下游会把手机号明文入库 → 证据位置 `requirements.md:120`\n\n", "")
_FEW_SCEN = _OK.replace("- 若按 §四 开工 → 下游会漏做并发扣减 → 证据位置 `requirements.md:77`\n", "")
_NO_INDEP = _OK.replace("independence=same-agent（本次审核非独立第三方）\n", "")
_SELF_CLAIM = _OK.replace("independence=same-agent（本次审核非独立第三方）",
                          "independence=same-agent（本报告为独立审核，第三方视角）")
_NO_CITE = _OK.replace("| 1 | P0 | D3 | 验收标准不可判定 | `requirements.md:88` 「界面友好」 | local | 改可判定 |",
                       "| 1 | P0 | D3 | 验收标准不可判定 | 第二章 | local | 改可判定 |")

_LED_OK = "\n".join([
    '{"round":1,"p0":2,"p1":5,"p2":3,"new_evidence":0}',
    '{"round":2,"p0":0,"p1":5,"p2":3,"new_evidence":3}',
])
_LED_BAD = "\n".join([
    '{"round":1,"p0":2,"p1":5,"p2":3,"new_evidence":0}',
    '{"round":2,"p0":0,"p1":5,"p2":3,"new_evidence":0}',
])


def self_test() -> int:
    cases = [
        ("正例 · 合规报告",           check_report(_OK),          []),
        ("反例 · 删掉对抗小节",       check_report(_NO_D9),        ["R1"]),
        ("反例 · 对抗场景仅 2 条",     check_report(_FEW_SCEN),     ["R1"]),
        ("反例 · 缺独立性声明",       check_report(_NO_INDEP),     ["R2"]),
        ("反例 · 同源却自称独立",     check_report(_SELF_CLAIM),   ["R3"]),
        ("反例 · P0 无 file:line",    check_report(_NO_CITE),      ["R4"]),
        ("正例 · 账本有据下降",       check_ledger(_LED_OK),       []),
        ("反例 · 零新证据却降级",     check_ledger(_LED_BAD),      ["L2"]),
    ]
    fail = 0
    print("# audit_gate 自证（判据有牙）\n")
    print("| 用例 | 期望 | 实际 | 结果 |")
    print("|---|---|---|---|")
    for name, got, want in cases:
        codes = sorted({b.split()[0] for b in got})
        ok = codes == sorted(want)
        fail += 0 if ok else 1
        print(f"| {name} | {want or '无'} | {codes or '无'} | {'✅' if ok else '🔴'} |")
    if fail:
        print(f"\n🔴 自证**未通过**：{fail} 条判据无牙。")
        return 1
    print("\n✅ 自证通过：R1 / R2 / R3 / R4 / L2 五条判据均可被违反触发。")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-req-audit 门④ 机械守卫")
    ap.add_argument("--report", help="req-audit-report.md 路径")
    ap.add_argument("--ledger", help="round-ledger.jsonl 路径（可选）")
    ap.add_argument("--self-test", action="store_true", help="内置夹具自证判据有牙")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not args.report:
        ap.error("需给 --report，或使用 --self-test")
        return 2

    bad: list[str] = []
    try:
        bad += check_report(Path(args.report).read_text(encoding="utf-8", errors="replace"))
    except OSError as e:
        print(f"读报告失败：{e}")
        return 2
    if args.ledger:
        try:
            bad += check_ledger(Path(args.ledger).read_text(encoding="utf-8", errors="replace"))
        except OSError as e:
            print(f"读账本失败：{e}")
            return 2

    if bad:
        print(f"门④ 违规 {len(bad)} 条：\n")
        for b in bad:
            print(f"- {b}")
        return 1
    print("门④ 通过：对抗维 / 独立性 / 可复算 / 单调性 四类判据全过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
