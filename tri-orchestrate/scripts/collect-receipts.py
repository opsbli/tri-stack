#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回执收集器：读取 receipt-*.json → 校验 → 回写 master-todo → 冲突检测 → 进度看板。

用法：
    python scripts/collect-receipts.py --specs-dir <specs目录>
    python scripts/collect-receipts.py --specs-dir <specs目录> --dashboard
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = {"spec_id": str, "status": str, "assignee": str,
                   "files_changed": list, "tests_passed": bool,
                   "blockers": list, "completed_at": str}


def collect_receipts(specs_dir: Path) -> list[dict]:
    receipts = []
    for f in sorted(specs_dir.glob("receipt-*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            missing = [k for k in REQUIRED_FIELDS if k not in d]
            if missing:
                print(f"  ⚠ {f.name}: 缺字段 {missing}，跳过")
                continue
            receipts.append(d)
        except json.JSONDecodeError as e:
            print(f"  ⚠ {f.name}: JSON 解析失败，跳过")
    return receipts


def detect_conflicts(receipts: list[dict]) -> list[tuple[str, str, list[str]]]:
    conflicts = []
    for i in range(len(receipts)):
        for j in range(i + 1, len(receipts)):
            a, b = receipts[i], receipts[j]
            overlap = set(a["files_changed"]) & set(b["files_changed"])
            if overlap:
                conflicts.append((a["spec_id"], b["spec_id"], sorted(overlap)))
    return conflicts


def update_master_todo(specs_dir: Path, receipts: list[dict], dry: bool) -> str:
    todo_path = specs_dir / "master-todo.md"
    if not todo_path.is_file():
        return "master-todo.md 不存在"
    t = todo_path.read_text(encoding="utf-8")

    completed = {r["spec_id"] for r in receipts if r["status"] == "completed"}
    for spec_id in completed:
        # 找到该 spec 的区域并勾选
        pattern = rf"(## {spec_id}[^\n]*\n(?:[^\n]*\n)*?)(- \[ \])"
        t = re.sub(pattern, rf"\1- [x]", t, count=0)

    # 简化：直接勾选所有该 spec 下的 [ ]
    lines = t.splitlines()
    in_spec = None
    for i, line in enumerate(lines):
        m = re.match(r"^## (Spec-\d+)", line)
        if m:
            in_spec = m.group(1)
        if in_spec and in_spec in completed and "- [ ]" in line:
            lines[i] = line.replace("- [ ]", "- [x]")
    t = "\n".join(lines) + "\n"

    if not dry:
        todo_path.write_text(t, encoding="utf-8")
    return "已回写"


def dashboard(receipts: list[dict], conflicts: list) -> str:
    lines = ["\n## 进度看板\n"]
    lines.append("| Spec | 负责人 | 状态 | 文件变更数 | 阻塞 |")
    lines.append("|---|---|---|---|---|")
    for r in receipts:
        mark = {"completed": "✅", "blocked": "🔴", "partial": "🟡"}.get(r["status"], "?")
        lines.append(f"| {r['spec_id']} | {r['assignee']} | {mark} {r['status']} "
                     f"| {len(r['files_changed'])} | {'; '.join(r['blockers']) or '—'} |")

    if conflicts:
        lines.append("\n### ⚠ 潜在合并冲突\n")
        lines.append("| Spec A | Spec B | 冲突文件 |")
        lines.append("|---|---|---|")
        for a, b, files in conflicts:
            lines.append(f"| {a} | {b} | {', '.join(files[:5])} |")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs-dir", required=True)
    ap.add_argument("--dashboard", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    specs_dir = Path(args.specs_dir).resolve()
    if not specs_dir.is_dir():
        print(f"目录不存在: {specs_dir}", file=sys.stderr)
        return 2

    receipts = collect_receipts(specs_dir)
    conflicts = detect_conflicts(receipts)
    result = update_master_todo(specs_dir, receipts, args.dry_run)

    if args.json:
        print(json.dumps({"receipts": receipts, "conflicts": conflicts,
                          "todo_update": result}, ensure_ascii=False, indent=2))
    else:
        print(f"# 回执收集\n")
        print(f"收到 {len(receipts)} 个回执")
        print(f"master-todo: {result}")
        if conflicts:
            print(f"⚠ 潜在合并冲突: {len(conflicts)} 组")
            for a, b, files in conflicts:
                print(f"  {a} ↔ {b}: {', '.join(files[:3])}")
        if args.dashboard:
            print(dashboard(receipts, conflicts))

    return 0


if __name__ == "__main__":
    sys.exit(main())
