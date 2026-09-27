#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门④.5 变更验收 · 案级条款集 diff

判据唯一真源：references/change-acceptance-gate.md
本脚本 ONLY 承担可机械判定部分；`need_manual` 项 MUST 由人裁定，NEVER 臆断。

用法：
    python scripts/acceptance_diff.py --before before.json --after after.json
    python scripts/acceptance_diff.py --before b.json --after a.json --ops ops.json --out report.md
    python scripts/acceptance_diff.py --before b.json --after a.json --repo-root <skill-dir>

退出码：
    0 = 三条硬门全过（含 N-A / 无 FAIL）
    1 = 存在 FAIL（B1/B2/B3 任一不过）
    2 = 输入错误（文件缺失 / JSON 非法 / 必填字段缺失）
"""

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_CASE_FIELDS = ("case_id", "verdict", "clauses")
QUOTE_RE = re.compile(r"[「『\"'\u201c]([^」』\"'\u201d]{4,})[」』\"'\u201d]")


def die(msg, code=2):
    print("ERROR: " + msg, file=sys.stderr)
    return code


def load_json(path):
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError("台账文件不存在：" + str(p))
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def norm_clauses(raw):
    """条款集归一：去空白、去重、排序 —— 位置/顺序差异不是行为差异。"""
    if raw is None:
        return []
    if not isinstance(raw, list):
        raw = [raw]
    return sorted({str(x).strip() for x in raw if str(x).strip()})


def index_cases(ledger, label):
    """按 case_id 建索引；必填字段缺失即整条作废。

    `clauses` 的口径（2026-09-27 修正）：MUST **存在该键**，但**允许空列表**——
    一个全 PASS 的干净 case 本来就没有非 PASS 条款。早期版本用 `not c.get(f)` 判缺失，
    把空列表当缺失 ⇒ 干净 case 被判「字段缺失作废」，实测使 C-007（从干净变为带建议项失败）
    这条**真实翻转被漏记**，且错报为「两侧不齐」。
    """
    idx, invalid = {}, []
    for c in ledger.get("cases", []) or []:
        cid = str(c.get("case_id", "")).strip()
        missing = [f for f in REQUIRED_CASE_FIELDS
                   if f not in c or (f != "clauses" and not c.get(f))]
        if not cid or missing:
            invalid.append({"side": label, "case_id": cid or "<空>", "missing": missing})
            continue
        idx[cid] = c
    return idx, invalid


def extract_needles(evidence):
    """从 evidence 引句里抽出可回验片段（引号内文本）。"""
    needles = []
    for ev in evidence or []:
        found = QUOTE_RE.findall(str(ev))
        needles.extend(found if found else [str(ev).strip()])
    return [n.strip() for n in needles if len(n.strip()) >= 4]


def verify_evidence(case, repo_files):
    """尽力而为的原文回验：任一 needle 在目标 skill 的 *.md 中命中即视为 verified。"""
    needles = extract_needles(case.get("evidence"))
    if not needles:
        return "unverified", []
    hits = [n for n in needles if any(n in text for text in repo_files)]
    # 未命中是「待复核」而非「无效」——见调用点说明。
    return ("verified" if hits else "unverified"), hits


def load_repo_texts(repo_root):
    if not repo_root:
        return None
    root = Path(repo_root)
    if not root.is_dir():
        raise FileNotFoundError("--repo-root 不是目录：" + str(root))
    texts = []
    for f in sorted(root.rglob("*.md")):
        try:
            texts.append(f.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return texts


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="acceptance_diff.py",
        description="门④.5 变更验收：比对两份案级台账，判定三条硬门 B1/B2/B3。",
    )
    ap.add_argument("--before", required=True, help="变更前台账 JSON")
    ap.add_argument("--after", required=True, help="变更后台账 JSON")
    ap.add_argument("--ops", help="可选：声明的变更点清单 JSON（[{\"op_id\":..,\"claim\":\"behavior_change|cosmetic|out_of_scope\",\"note\":..}]）")
    ap.add_argument("--repo-root", dest="repo_root", help="可选：被测 skill 目录，用于 evidence 原文回验")
    ap.add_argument("--out", help="可选：把 Markdown 报告写入该文件（同时仍打印到 stdout）")
    ap.add_argument("--json", action="store_true", help="额外打印机器可读 JSON")
    args = ap.parse_args(argv)

    try:
        before = load_json(args.before)
        after = load_json(args.after)
        ops = load_json(args.ops) if args.ops else None
        repo_texts = load_repo_texts(args.repo_root)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return die(str(exc))

    b_idx, b_invalid = index_cases(before, "before")
    a_idx, a_invalid = index_cases(after, "after")

    all_ids = sorted(set(b_idx) | set(a_idx))
    changed, unchanged, need_manual, invalidated, absent = [], [], [], [], []

    for cid in all_ids:
        b, a = b_idx.get(cid), a_idx.get(cid)
        if b is None or a is None:
            absent.append({"case_id": cid, "side": "after" if b else "before"})
            continue

        b_cl, a_cl = norm_clauses(b.get("clauses")), norm_clauses(a.get("clauses"))
        b_tok, a_tok = (b.get("verdict_token") or "").strip(), (a.get("verdict_token") or "").strip()

        # 防自相矛盾（取代早期「clauses 为空即作废」的粗口径——那会误伤干净 case）：
        # token 声称存在必检失败，条款集却为空 ⇒ 台账自相矛盾，作废。
        if (b_tok.startswith("FAIL") and not b_cl) or (a_tok.startswith("FAIL") and not a_cl):
            invalidated.append(cid)
            continue

        clauses_added = sorted(set(a_cl) - set(b_cl))
        clauses_dropped = sorted(set(b_cl) - set(a_cl))

        # 主判据 = verdict_token（结论本身）。
        # clauses ONLY 用于解释「因为哪条改了」—— NEVEL 用字符串比对判翻转：
        # 同一节在两版常被引成不同粒度（实测：同一节在两侧引用字符串不同但结论一致），
        # 纯字符串比对会系统性误报（详见 change-acceptance-gate.md §七）。
        if not (b_tok and a_tok):
            need_manual.append({
                "case_id": cid,
                "reason": "verdict_token 缺失，无法机械判定（clauses 字符串漂移不可作为判据）",
            })
            continue

        if b_tok == a_tok:
            # B3 的结构性保证：结论无差异 ⇒ 绝不入变更清单
            unchanged.append(cid)
            continue

        verif = "skipped"
        if repo_texts is not None:
            verif, _hits = verify_evidence(a, repo_texts)
            # 回验是「软信号」：未命中只标待复核，NEVER 因此作废整条 ——
            # evidence 的书写粒度因撰写者而异，硬作废会系统性抹掉真实翻转（已实测）。
        changed.append(
            {
                "case_id": cid,
                "before_clauses": b_cl,
                "after_clauses": a_cl,
                "before_token": b_tok,
                "after_token": a_tok,
                "direction": "before→after",
                "delta": sorted(set(a_cl) ^ set(b_cl)),
                "added": clauses_added,
                "dropped": clauses_dropped,
                "clauses_same": b_cl == a_cl,
                "changed_by": a.get("changed_by") or b.get("changed_by") or [],
                "evidence_verify": verif,
            }
        )

    # ---- 硬门判定 ----
    gate = {"B1": "N-A", "B2": "N-A", "B3": "PASS"}
    notes = []
    changed_ids = {c["case_id"] for c in changed}

    if ops:
        claimed_behavior, claimed_cosmetic, claimed_oos = [], [], []
        for op in ops:
            oid = str(op.get("op_id", "")).strip()
            claim = str(op.get("claim", "")).strip()
            touched = {c["case_id"] for c in changed if oid in (c.get("changed_by") or [])}
            if claim == "behavior_change":
                if touched:
                    claimed_behavior.append((oid, sorted(touched)))
                else:
                    claimed_behavior.append((oid, []))
            elif claim == "cosmetic":
                claimed_cosmetic.append((oid, sorted(touched)))
            elif claim == "out_of_scope":
                # 变更不在电池覆盖范围内（如改的是测试脚本而非判据）。
                # 不参与 B1/B2，但 MUST 附 note 说明为何超范围 —— 否则就是「用超范围掩盖未翻转」。
                claimed_oos.append((oid, str(op.get("note", "")).strip()))
            elif claim:
                notes.append(f"未知 claim（已忽略）：{oid} → {claim!r}；合法值 behavior_change / cosmetic / out_of_scope")
        b1_fail = [o for o, t in claimed_behavior if not t]
        b2_fail = [o for o, t in claimed_cosmetic if t]
        gate["B1"] = "FAIL" if b1_fail else ("PASS" if claimed_behavior else "N-A")
        gate["B2"] = "FAIL" if b2_fail else ("PASS" if claimed_cosmetic else "N-A")
        if b1_fail:
            notes.append("B1 FAIL：以下 op 声称行为变更但未翻转任何 case → " + ", ".join(b1_fail))
        if b2_fail:
            notes.append("B2 FAIL：以下 op 标 cosmetic 却翻转了 case → " + ", ".join(b2_fail))
        if claimed_oos:
            no_note = [o for o, n in claimed_oos if not n]
            notes.append("out_of_scope（不计入 B1/B2，超出电池覆盖范围）："
                         + ", ".join(f"{o}（{n[:50]}）" if n else o for o, n in claimed_oos))
            if no_note:
                notes.append("⚠️ 以下 out_of_scope 未附 note，属未说明的超范围声明 → " + ", ".join(no_note))
    else:
        notes.append("未提供 --ops，B1/B2 转 N-A（仅判定 B3）")

    # 判定不完整 ≠ 通过：存在 need_manual 时 B1/B2 绝不能报 PASS（防假阳性）。
    # 判定不完整 ≠ 通过，也不等于「不适用」：两种情形都升为 INCOMPLETE 并阻断。
    if need_manual:
        notes.append("存在 {} 项 need_manual，B1/B2 判定不完整".format(len(need_manual)))
        for k in ("B1", "B2"):
            if gate[k] in ("PASS", "N-A"):
                gate[k] = "INCOMPLETE"

    failed = [k for k, v in gate.items() if v in ("FAIL", "INCOMPLETE")]

    # ---- 报告 ----
    lines = []
    lines.append("## 门④.5 变更验收 · {} {} → {}".format(
        after.get("skill") or before.get("skill") or "<skill>",
        before.get("version") or "?",
        after.get("version") or "?"))
    lines.append("")
    lines.append("| case_id | 前版条款集 | 后版条款集 | 翻转? | 方向 | 条款差 |")
    lines.append("|---|---|---|---|---|---|")
    if changed:
        for c in changed:
            lines.append("| {} | {} | {} | ✅ | {} | {} |".format(
                c["case_id"], " / ".join(c["before_clauses"]), " / ".join(c["after_clauses"]),
                c["direction"], " / ".join(c["delta"]) or "（仅结论 token 变）"))
    if not changed:
        lines.append("| — | — | — | ❌ | — | 无（无可机械判定的行为变更） |")
    lines.append("")
    lines.append("**硬门判定**：B1 {} / B2 {} / B3 {}".format(gate["B1"], gate["B2"], gate["B3"]))
    lines.append("")
    lines.append("**变更清单**：" + (", ".join(sorted(changed_ids)) or "无"))
    lines.append("**未变清单（B3 保证不入变更清单）**：" + (", ".join(sorted(set(unchanged))) or "无"))
    lines.append("**need_manual**：" + (", ".join(x["case_id"] for x in need_manual) or "无"))
    lines.append("**作废（token 声称失败但条款集为空，自相矛盾）**：" + (", ".join(invalidated) or "无"))
    unverified = [c["case_id"] for c in changed if c.get("evidence_verify") == "unverified"]
    if unverified:
        lines.append("**evidence 待复核（软信号，不影响计入）**：" + ", ".join(unverified))
    if absent:
        lines.append("**两侧不齐**：" + ", ".join(
            "{}（缺 {} 侧）".format(x["case_id"], x["side"]) for x in absent))
    if b_invalid or a_invalid:
        lines.append("**字段缺失作废**：" + json.dumps(b_invalid + a_invalid, ensure_ascii=False))
    if notes:
        lines.append("")
        for n in notes:
            lines.append("- " + n)

    report = "\n".join(lines)
    print(report)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report + "\n", encoding="utf-8")
        print("\n[written] " + str(out), file=sys.stderr)

    if args.json:
        print(json.dumps(
            {"gate": gate, "changed": changed, "unchanged": sorted(set(unchanged)),
             "need_manual": need_manual, "invalidated": invalidated, "absent": absent,
             "failed": failed},
            ensure_ascii=False, indent=2))

    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
