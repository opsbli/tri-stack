#!/usr/bin/env python3
"""tri-sdlc 门禁自动审计（确定性逻辑脚本）.

实现闸门① 的 68 必检项逐条审计算法。SKILL.md 仅保留审计规则摘要与本脚本指针，
逐条判定/证据定位/汇总逻辑在此。

数据源: gates/acceptance-criteria.md（68 必检 + 21 建议，门禁单一事实源）。
用法:
    python scripts/gate_audit.py --stage P1 --deliverables-dir .tribro/sdlc/<命名>/P1-requirements
    python scripts/gate_audit.py --list-criteria P1
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

# 九阶段必检项 ID 区间（与 gates/acceptance-criteria.md 一致）
STAGE_MILESTONES = {
    "P0": ("M0", "M5"),
    "P1": ("M0", "M7"),
    "P2": ("M0", "M8"),
    "P3": ("M0", "M6"),
    "P4": ("M0", "M7"),
    "P5": ("M0", "M6"),
    "P6": ("M0", "M6"),
    "P7": ("M0", "M8"),
    "P8": ("M0", "M6"),
}

VERDICTS = ("PASS", "FAIL", "WARN", "N/A")


def list_criteria(stage: str) -> list[str]:
    """枚举某阶段的全部必检项 ID（Pn-M0..Mk）。"""
    if stage not in STAGE_MILESTONES:
        raise ValueError(f"未知阶段 {stage}，合法: {list(STAGE_MILESTONES)}")
    lo, hi = STAGE_MILESTONES[stage]
    lo_n = int(lo[1:])
    hi_n = int(hi[1:])
    return [f"{stage}-M{i}" for i in range(lo_n, hi_n + 1)]


def audit_stage(stage: str, deliverables: dict[str, str]) -> dict:
    """对某阶段执行门禁审计。

    deliverables: {必检项ID: 判定} 或 {必检项ID: (判定, 证据/原因)}。
    返回 gate-report 结构（含汇总 + 修订意见）。
    """
    required = list_criteria(stage)
    results = []
    fail_items = []
    for cid in required:
        entry = deliverables.get(cid)
        if entry is None:
            # 缺失判定 = 无理由 N/A = FAIL
            results.append({"id": cid, "verdict": "FAIL", "evidence": "未判定（缺失视为无理由 N/A → FAIL）"})
            fail_items.append({"id": cid, "问题": "未给出判定", "修订要求": "必须逐条判定并附证据位置"})
            continue
        verdict, evidence = (entry if isinstance(entry, tuple) else (entry, ""))
        verdict = verdict.upper()
        if verdict not in VERDICTS:
            raise ValueError(f"{cid} 非法判定 {verdict}，合法: {VERDICTS}")
        if verdict == "N/A" and not evidence:
            verdict = "FAIL"
            evidence = "无理由 N/A 视为 FAIL"
            fail_items.append({"id": cid, "问题": "N/A 未附理由", "修订要求": "N/A MUST 附不适用理由"})
        results.append({"id": cid, "verdict": verdict, "evidence": evidence})
        if verdict == "FAIL":
            fail_items.append({"id": cid, "问题": evidence or "FAIL", "修订要求": "回炉对应子SKILL 修订"})
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    total = len(results)
    gate = "FAIL" if fail_items else "PASS"
    return {
        "stage": stage,
        "required_total": total,
        "passed": passed,
        "fail_count": len(fail_items),
        "gate_verdict": gate,
        "items": results,
        "revision_notes": fail_items,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-sdlc 门禁自动审计（68 必检项）")
    ap.add_argument("--list-criteria", metavar="STAGE", help="枚举某阶段必检项 ID")
    ap.add_argument("--stage", help="审计阶段（如 P1）")
    ap.add_argument("--deliverables-json", help="交付物判定 JSON 文件（{必检项ID: [判定, 证据]}）")
    args = ap.parse_args()

    if args.list_criteria:
        print(json.dumps(list_criteria(args.list_criteria), ensure_ascii=False))
        return 0
    if args.stage:
        deliverables = {}
        if args.deliverables_json:
            raw = json.loads(Path(args.deliverables_json).read_text(encoding="utf-8"))
            for k, v in raw.items():
                deliverables[k] = tuple(v) if isinstance(v, list) else v
        print(json.dumps(audit_stage(args.stage, deliverables), ensure_ascii=False, indent=2))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
