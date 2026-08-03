#!/usr/bin/env python3
"""
tri-checklist Markdown checklist 组装器（确定性算法下沉）

用法:
    python build_checklist.py --diff diff.json --template template.json --out checklist.md
    python build_checklist.py --diff diff.json --template template.json --out checklist.md --dry-run

功能:
    1. 读取 diff.json（parse_git_diff.py 输出）+ template.json（四维检查项模板）
    2. 生成 Markdown 骨架（标题 + 元数据 + 四维章节 + 汇总）
    3. 注入复选框（- [ ] 默认未勾选）
    4. 注入严重程度标签（[BLOCKER]/[MAJOR]/[MINOR]，与 tri-review 对齐）
    5. 三级分组（维度 → 检查类别 → 检查项）
    6. 输出单文件 Markdown checklist

零第三方依赖: 仅用 Python 标准库（json/sys/pathlib/datetime）

退出码:
    0 = 成功
    1 = 输入错误/校验失败
    2 = 输出写入失败
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# ============ 常量 ============

# 四维审计维度定义（与 references/audit-checklist-template.md 一致）
DIMENSIONS = [
    {"key": "changes", "title": "改动点", "icon": "📝"},
    {"key": "review", "title": "审查点", "icon": "🔍"},
    {"key": "test", "title": "测试点", "icon": "🧪"},
    {"key": "test_steps", "title": "测试步骤", "icon": "👣"},
]

# ============ 组装逻辑 ============

def validate_inputs(diff_data, template_data):
    """校验 diff.json 与 template.json 完整性"""
    if not isinstance(diff_data, dict) or "files" not in diff_data:
        raise ValueError("diff.json 缺少 files 字段")
    if not isinstance(template_data, dict) or "dimensions" not in template_data:
        raise ValueError("template.json 缺少 dimensions 字段")
    template_dims = template_data["dimensions"]
    missing = [d["key"] for d in DIMENSIONS if d["key"] not in template_dims]
    if missing:
        raise ValueError(f"template.json 四维缺失: {missing}")
    return True


def build_header(diff_data, meta):
    """构建 Markdown 头部"""
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats = diff_data.get("stats", {})
    mode_label = {"staged": "暂存区", "working": "工作区", "commit": "commit id"}.get(
        diff_data.get("mode"), diff_data.get("mode"))
    commit_info = f"\n- **Commit**: `{diff_data.get('commit')}`" if diff_data.get("commit") else ""
    return f"""# 审计 Checklist

> **生成工具**: tri-checklist（tri-xxx 家族 · I10 audit-checklist 子类）
> **生成时间**: {generated_at}

## 元数据

- **Git 输入模式**: {mode_label}
- **改动文件数**: {stats.get('files_changed', 0)}
- **增行**: +{stats.get('insertions', 0)}
- **删行**: -{stats.get('deletions', 0)}
- **敏感文件**: {len(diff_data.get('sensitive_files', []))} 个{' ⚠️ 需关注' if diff_data.get('sensitive_files') else ''}
- **测试文件**: {len(diff_data.get('test_files', []))} 个{commit_info}

---"""


def build_changes_section(diff_data):
    """构建改动点章节（基于实际 diff 数据）"""
    files = diff_data.get("files", [])
    if not files:
        return "## 1. 📝 改动点\n\n（无改动）\n"

    # 文件清单表
    table_rows = ["| 文件 | 类型 | 增行 | 删行 |", "|---|---|---|---|"]
    status_label = {"added": "新增", "modified": "修改", "deleted": "删除",
                    "renamed": "重命名", "copied": "复制", "untracked": "未跟踪",
                    "type-changed": "类型变更", "unmerged": "合并冲突"}
    for f in files:
        label = status_label.get(f["status"], f["status"])
        table_rows.append(f"| `{f['path']}` | {label} | +{f['insertions']} | -{f['deletions']} |")

    # 改动函数清单
    func_lines = []
    for f in files:
        if f.get("functions"):
            funcs = ", ".join(f"`{fn}()`" for fn in f["functions"])
            func_lines.append(f"- `{f['path']}` → {funcs}")

    # 检查项
    checklist = """### 1.1 改动文件清单

{table}

### 1.2 改动函数清单

{funcs}

### 1.3 改动检查项

- [ ] `[BLOCKER]` 改动文件清单已列出（共 {file_count} 个文件）
- [ ] `[BLOCKER]` 改动函数清单已列出（共 {func_count} 个函数）
- [ ] `[MAJOR]` 改动类型已标注（新增/修改/删除/重构）
- [ ] `[MAJOR]` 改动行数统计已列出
- [ ] `[MINOR]` 改动 commit 信息已记录""".format(
        table="\n".join(table_rows),
        funcs="\n".join(func_lines) if func_lines else "（无函数级改动或未识别）",
        file_count=len(files),
        func_count=sum(len(f.get("functions", [])) for f in files),
    )

    return f"## 1. 📝 改动点\n\n{checklist}\n"


def build_dimension_section(dim_key, dim_title, dim_icon, dim_template):
    """构建审查点/测试点/测试步骤章节（基于模板）"""
    sections = dim_template.get("sections", [])
    if not sections:
        return f"## {dim_index(dim_key)}. {dim_icon} {dim_title}\n\n（无检查项）\n"

    body = []
    for section in sections:
        section_title = section.get("title", "")
        items = section.get("items", [])
        body.append(f"### {section_title}\n")
        for item in items:
            severity = item.get("severity", "minor").upper()
            label = {"BLOCKER": "BLOCKER", "MAJOR": "MAJOR", "MINOR": "MINOR"}.get(severity, "MINOR")
            text = item.get("text", "")
            body.append(f"- [ ] `[{label}]` {text}")
        body.append("")  # 空行分隔

    return f"## {dim_index(dim_key)}. {dim_icon} {dim_title}\n\n" + "\n".join(body) + "\n"


def dim_index(dim_key):
    """维度编号"""
    mapping = {"changes": "1", "review": "2", "test": "3", "test_steps": "4"}
    return mapping.get(dim_key, "?")


def build_summary(diff_data, template_data):
    """构建汇总章节"""
    # 统计检查项总数与严重程度分布
    total = 0
    by_severity = {"BLOCKER": 0, "MAJOR": 0, "MINOR": 0}

    # 改动点检查项（5 项固定）
    total += 5
    by_severity["BLOCKER"] += 2
    by_severity["MAJOR"] += 2
    by_severity["MINOR"] += 1

    # 模板检查项
    for dim in DIMENSIONS[1:]:  # 跳过 changes（已单独处理）
        dim_template = template_data["dimensions"].get(dim["key"], {})
        for section in dim_template.get("sections", []):
            for item in section.get("items", []):
                total += 1
                sev = item.get("severity", "minor").upper()
                if sev in by_severity:
                    by_severity[sev] += 1

    return f"""## 汇总

| 维度 | 检查项数 |
|---|---|
| 1. 改动点 | 5 |
| 2. 审查点 | {sum(len(s.get('items', [])) for s in template_data['dimensions'].get('review', {}).get('sections', []))} |
| 3. 测试点 | {sum(len(s.get('items', [])) for s in template_data['dimensions'].get('test', {}).get('sections', []))} |
| 4. 测试步骤 | {sum(len(s.get('items', [])) for s in template_data['dimensions'].get('test_steps', {}).get('sections', []))} |
| **合计** | **{total}** |

### 严重程度分布

- 🚫 **BLOCKER**（阻塞提交）: {by_severity['BLOCKER']} 项
- ⚠️ **MAJOR**（应修复）: {by_severity['MAJOR']} 项
- 💡 **MINOR**（建议修复）: {by_severity['MINOR']} 项

### 维度关联

- 改动点 → 审查点：改动函数清单决定审查范围
- 改动点 → 测试点：改动函数清单决定测试覆盖范围
- 审查点 → 测试步骤：审查发现的功能场景决定测试步骤
- 测试点 → 测试步骤：边界条件决定异常场景

---

## 使用说明

1. 逐项执行检查，完成的将 `- [ ]` 改为 `- [x]`
2. `[BLOCKER]` 项未通过 MUST 阻塞提交/发布
3. `[MAJOR]` 项未通过应修复后再提交
4. `[MINOR]` 项未通过建议修复但不阻塞
5. 完成后可将本清单作为 tri-review 的审查依据

---

> Generated by tri-checklist @ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | License: follow project license
"""


def build_checklist(diff_data, template_data, meta):
    """组装单文件 Markdown checklist"""
    validate_inputs(diff_data, template_data)
    parts = [build_header(diff_data, meta)]
    # 维度 1: 改动点（基于实际 diff 数据）
    parts.append(build_changes_section(diff_data))
    # 维度 2-4: 基于模板
    for dim in DIMENSIONS[1:]:
        dim_template = template_data["dimensions"].get(dim["key"], {})
        parts.append(build_dimension_section(dim["key"], dim["title"], dim["icon"], dim_template))
    parts.append(build_summary(diff_data, template_data))
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="tri-checklist Markdown checklist 组装器")
    parser.add_argument("--diff", required=True, help="diff.json 路径（parse_git_diff.py 输出）")
    parser.add_argument("--template", required=True, help="template.json 路径（四维检查项模板）")
    parser.add_argument("--out", required=True, help="输出 Markdown checklist 路径")
    parser.add_argument("--dry-run", action="store_true", help="仅校验不输出")
    args = parser.parse_args()

    try:
        with open(args.diff, "r", encoding="utf-8") as f:
            diff_data = json.load(f)
        with open(args.template, "r", encoding="utf-8") as f:
            template_data = json.load(f)
    except Exception as e:
        print(f"[ERROR][读取] 输入文件读取失败: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        validate_inputs(diff_data, template_data)
    except ValueError as e:
        print(f"[ERROR][校验] 输入校验失败: {e}", file=sys.stderr)
        sys.exit(1)

    meta = diff_data.get("meta", {})

    if args.dry_run:
        print(f"[INFO][校验] 通过。文件数={diff_data['stats']['files_changed']}, 四维覆盖=完整", file=sys.stderr)
        sys.exit(0)

    checklist = build_checklist(diff_data, template_data, meta)

    try:
        Path(args.out).write_text(checklist, encoding="utf-8")
    except Exception as e:
        print(f"[ERROR][写入] checklist 写入失败: {e}", file=sys.stderr)
        sys.exit(2)

    size_kb = len(checklist.encode("utf-8")) / 1024
    print(f"[INFO][完成] checklist 已生成: {args.out} ({size_kb:.1f} KB)", file=sys.stderr)
    print(f"[INFO][摘要] 文件数={diff_data['stats']['files_changed']}, "
          f"+{diff_data['stats']['insertions']}/-{diff_data['stats']['deletions']}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
