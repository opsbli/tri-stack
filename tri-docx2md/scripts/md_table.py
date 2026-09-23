#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""md_table.py · 自产 Markdown 表格生成器（每 skill 独立完整副本，单 skill 可单独运行）

MIT 归属：单元格转义逻辑迁移自 Microsoft markitdown _csv_converter._escape_table_cell（MIT）。
见 docs/markitdown-analysis-migration-20260909.md M8。

边界（M8 硬边界）：仅用于**自产表**（pipeline 诊断、pdf_form_extract、xlsx runner 等家族
自己生成的表格），NEVER 用于后端输出修复——后端产物的破表检测属 postprocess/quality_check
「只检测不修复」既有决策，本工具不得介入。
"""
import re

_PIPE_ESCAPE_RE = re.compile(r"(\\*)\|")


def escape_cell(value) -> str:
    """单元格进表前三件事：竖线转义（含前置反斜杠翻倍）、换行折空格、None→空。"""
    if value is None:
        return ""
    value = _PIPE_ESCAPE_RE.sub(lambda m: m.group(1) * 2 + r"\|", str(value))
    return value.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")


def build_md_table(rows, header: bool = True) -> str:
    """二维行列表 → 合规管道表：列数对齐补齐/截断 + 逐格转义。

    rows: 可迭代的行（每行为可迭代的单元格值）；
    header: True 时首行后插 | --- | 分隔行。
    """
    rows = [list(r) for r in rows]
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    norm = [(r + [""] * (width - len(r)))[:width] for r in rows]
    esc = [[escape_cell(c) for c in r] for r in norm]
    out = ["| " + " | ".join(esc[0]) + " |"]
    if header:
        out.append("| " + " | ".join(["---"] * width) + " |")
        body = esc[1:]
    else:
        body = esc
    out += ["| " + " | ".join(r) + " |" for r in body]
    return "\n".join(out)
