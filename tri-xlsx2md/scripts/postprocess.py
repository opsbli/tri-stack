#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门C · 转换后处理（tri-xlsx2md）

确定性清理后端（mammoth/markitdown/pandoc）输出的 Markdown：
1. 去除 Word 书签锚点等 HTML 标签（<a id="...">、</a>、<span>、<div>、<o:p> 等），保留标签内内容
2. 白名单保留对 MD 渲染有意义的 HTML（br/sub/sup/kbd/code/img/table 系）
3. HTML 实体解码（&amp; &lt; &gt; &quot; &#39; &nbsp;）
4. 围栏感知清理：锚点删除后产生的多余空行与行尾空白（代码块内不动）
5. 保留标题层级（#）、加粗/斜体、有序/无序列表序号、表格语法等 MD 格式化信息

用法：
    python scripts/postprocess.py --md a.md [--output a.md] [--json]

退出码：0 后处理完成；2 参数错误。
"""
from _io_safe import safe_print
import argparse
import json
import re
import sys
from pathlib import Path

# 白名单：MD 中合法的内联/块级 HTML（保留不删）
KEEP_TAGS = {
    "br", "sub", "sup", "kbd", "code", "samp", "var", "mark", "ins", "del",
    "img", "table", "thead", "tbody", "tfoot", "tr", "td", "th", "caption",
    "col", "colgroup", "hr", "details", "summary", "figure", "figcaption",
}

# 成对空锚点：<a id="OLE_LINK19"></a>（中间仅空白）
_EMPTY_ANCHOR = re.compile(r"<a\s+[^>]*id\s*=\s*[\"'][^\"']*[\"'][^>]*>\s*</a>", re.IGNORECASE)
# 任意 <a ...> 开标签 / </a> 闭标签
_A_OPEN = re.compile(r"<a\s+[^>]*>", re.IGNORECASE)
_A_CLOSE = re.compile(r"</a\s*>", re.IGNORECASE)
# 其它非白名单标签（保留内容）
_OTHER_TAG = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")
# HTML 实体
_ENTITY_MAP = {
    "amp": "&", "lt": "<", "gt": ">", "quot": '"',
    "#39": "'", "apos": "'", "nbsp": " ",
}
_ENTITY_RE = re.compile(r"&(amp|lt|gt|quot|#39|apos|nbsp);", re.IGNORECASE)


def collect_anchor_refs(text: str) -> set:
    """P1-6 第一遍：收集 MD 内链引用集合 [text](#anchor) / []( #anchor) 中被引用的锚点名。"""
    return set(m.group(1) for m in re.finditer(r"\]\(#([^)\s]+)\)", text))


def strip_tags(text: str) -> tuple[str, dict]:
    """去 HTML 标签 + 实体解码。返回 (清理后文本, 统计)。

    P1-6 锚点两遍式（脚本逻辑，NEVER Agent 裁量）：先收集 [](#...) 引用集合，
    仅删除未被引用的锚点标签；被引用的锚点保留（交叉引用存活）。
    """
    stats = {"anchors_removed": 0, "anchors_kept": 0, "tags_removed": 0, "entities_decoded": 0}
    refs = collect_anchor_refs(text)
    protected = []

    def _element_repl(m):
        # P1-6 元素级两遍式：id 命中引用集合 → 占位保护；否则删标签保内容
        ids = re.findall(r"id\s*=\s*[\"']([^\"']*)[\"']", m.group(1), re.IGNORECASE)
        if any(i in refs for i in ids):
            stats["anchors_kept"] += 1
            protected.append(m.group(0))
            return f"\x00A{len(protected) - 1}\x00"
        stats["anchors_removed"] += 1
        return m.group(2)

    # 1. 锚点元素（含成对空锚点与带内容锚点）按引用集合决定去留
    text = re.sub(r"(<a\s+[^>]*id\s*=\s*[\"'][^\"']*[\"'][^>]*>)(.*?)(</a\s*>)",
                  _element_repl, text, flags=re.IGNORECASE | re.DOTALL)
    # 2. 残余 a 开/闭标签（无 id，如纯 href 链接壳）——删标签保内容
    text, n1 = _A_OPEN.subn("", text)
    text, n2 = _A_CLOSE.subn("", text)
    stats["anchors_removed"] += n1 + n2
    # 3. 其它非白名单标签（保留内容；\x00An 占位符不匹配标签正则，受保护锚点安全通过）
    def _repl(m):
        tag = m.group(1).lower()
        if tag in KEEP_TAGS:
            return m.group(0)
        stats["tags_removed"] += 1
        return ""
    text = _OTHER_TAG.sub(_repl, text)
    # 4. 实体解码（在标签清理之后，避免解码出的 <> 被误当标签）
    def _ent(m):
        stats["entities_decoded"] += 1
        return _ENTITY_MAP[m.group(1).lower()]
    text = _ENTITY_RE.sub(_ent, text)
    # 5. 还原受保护锚点（P1-6：被引用的锚点存活）
    for i, s in enumerate(protected):
        text = text.replace(f"\x00A{i}\x00", s)
    return text, stats


def cleanup_lines(text: str) -> tuple[str, dict]:
    """围栏感知：行尾空白清理 + 连续空行合并（代码块内不动）。"""
    stats = {"trailing_ws": 0, "blank_lines_merged": 0}
    out = []
    blank = 0
    in_fence = False
    for ln in text.split("\n"):
        stripped = ln.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(ln)
            blank = 0
            continue
        if in_fence:
            out.append(ln)
            continue
        cleaned = re.sub(r"[ \t]+$", "", ln)
        if cleaned != ln:
            stats["trailing_ws"] += 1
        if cleaned.strip() == "":
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(cleaned)
    if blank > 1:
        stats["blank_lines_merged"] += blank - 1
    return "\n".join(out).rstrip("\n") + "\n", stats


def backtick_fence(text: str) -> tuple[str, int]:
    """P1-2 动态围栏：代码块内容含更长反引号串时，围栏加长到超过它。返回 (文本, 调整数)。"""
    fixed = 0
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^(\s*)(`{3,})(.*)$", ln)
        if m and not m.group(2).startswith("    "):
            fence_len = len(m.group(2))
            # 向后找闭合围栏，检查内容中最长反引号串
            j = i + 1
            content_max = 0
            while j < len(lines) and not re.match(r"^\s*`{3,}", lines[j]):
                for run in re.finditer(r"`+", lines[j]):
                    content_max = max(content_max, len(run.group(0)))
                j += 1
            if j < len(lines) and content_max >= fence_len:
                need = content_max + 1
                lines[i] = m.group(1) + "`" * need + m.group(3)
                lines[j] = re.sub(r"`{%d}" % fence_len, "`" * need, lines[j], count=1)
                fixed += 1
        out.append(lines[i])
        i += 1
    return "\n".join(out), fixed


def fix_table_cells(text: str) -> tuple[str, dict]:
    """P1-2 表格保真检查（检测型，确定性）。

    边界事实（诚实声明）：单元格内裸竖线在纯 MD 侧无法与列分隔竖线确定性区分
    （`| x|y | z |` 是合法 3 列行），盲目重转义会误伤正常表格——NEVER 假装修复。
    破表防线分工：anydoc 主链输出本身已按上下文敏感最小转义规则转义数据竖线（唯一
    修复路径）；本函数仅**检测**「数据行竖线数与分隔行不一致」的疑似破表行并计数，
    供门D 报告与 fidelity 复核项使用。
    """
    stats = {"suspect_broken_rows": 0}
    lines = text.split("\n")
    in_fence = False
    sep_cols = None
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r"^\s*\|[\s:\-|]+\|\s*$", ln):
            sep_cols = len(re.split(r"(?<!\\)\|", ln)) - 2
            continue
        if ln.lstrip().startswith("|") and ln.rstrip().endswith("|"):
            cols = len(re.split(r"(?<!\\)\|", ln)) - 2
            if sep_cols is not None and cols != sep_cols:
                stats["suspect_broken_rows"] += 1
    return text, stats


def postprocess(md_text: str) -> tuple[str, dict]:
    text, s1 = strip_tags(md_text)
    text, s2 = cleanup_lines(text)
    s1.update(s2)
    # P1-2 表格保真规则族（确定性，修降级后端输出；anydoc 输出本身已合规，此步幂等）
    text, n_fence = backtick_fence(text)
    _, s_cell = fix_table_cells(text)
    s1["fence_fixed"] = n_fence
    s1["suspect_broken_rows"] = s_cell["suspect_broken_rows"]
    s1["chars_before"] = len(md_text)
    s1["chars_after"] = len(text)
    return text, s1


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-docx2md 门C 转换后处理（去 HTML 标签）")
    ap.add_argument("--md", required=True, help="后端输出的 Markdown 路径")
    ap.add_argument("--output", default=None, help="清理后写入路径（缺省就地覆盖 --md）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    md_path = Path(args.md)
    if not md_path.is_file():
        safe_print(json.dumps({"ok": False, "errors": [f"MD 文件不存在：{md_path}"]}, ensure_ascii=False))
        return 2

    text, stats = postprocess(md_path.read_text(encoding="utf-8", errors="replace"))
    out_path = Path(args.output) if args.output else md_path
    out_path.write_text(text, encoding="utf-8")

    payload = {"ok": True, "input": str(md_path), "output": str(out_path), "stats": stats}
    if args.json:
        safe_print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        safe_print(f"锚点清理 {stats['anchors_removed']} ｜ 标签清理 {stats['tags_removed']} ｜ "
              f"实体解码 {stats['entities_decoded']} ｜ 字符 {stats['chars_before']}→{stats['chars_after']}")
        safe_print(f"输出：{out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
