#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pdf_form_extract.py · PDF 无边框表格/表单词坐标聚类提取（tri-pdf2md · 自包含单文件）

MIT 归属：整函数级迁移自 Microsoft markitdown _pdf_converter.py
_extract_form_content_from_words（MIT），三重防误判启发式提炼为顶部常量。
见 docs/markitdown-analysis-migration-20260909.md M6。

能力：发票/报表类**无边框表格**——extract_text 会把多列拍成乱序行，本工具用词坐标
做自适应列聚类（70 分位 gap 容差 + 列密度上限 + 表行占比下限三重启发式防误判），
产出对齐 MD 表；非表格页回退普通文本提取。

三重防误判（markitdown 实测归纳，常量化便于调优）：
  1. GAP_PERCENTILE=0.70：列间隙 70 分位作为聚类容差（平衡精度/召回），夹在 [25,50]
  2. MAX_COLS_PER_INCH=10：列密度 >10 列/英寸判定为密集文本而非表单
  3. MIN_TABLE_ROW_RATIO=0.20：表行占比 <20% 判定整页非表单
另含：段落行判定（宽 >55% 页宽且 >60 字符）、窄列保护（均宽 <30pt → None）、
MasterFormat 部分编号行（".1"/".2"）按列表项处理不算表行。

自产表输出经 md_table.build_md_table（M8）保证生成即合规（转义）。
依赖：pdfplumber（extract_words 输出）；作为门C 由 Agent 视 NeedsOcr/表格信号调用，
或由 convert_pipeline 的 pdfplumber runner 自动调用（每页先试本工具、失败回退文本）。
"""
import argparse
import json
import re
import sys

from _io_safe import safe_print
from md_table import build_md_table

# ---------------- 三重防误判启发式常量（迁移自 markitdown，可调优） ----------------
GAP_PERCENTILE = 0.70        # 列间隙分位数 → 聚类容差
TOLERANCE_MIN, TOLERANCE_MAX = 25, 50   # 容差夹取范围（pt）
DEFAULT_TOLERANCE = 35       # gap 样本不足时的保守容差
X_GROUP_GAP = 50             # 行内列组初判 gap（pt）
ALIGN_TOLERANCE = 40         # 词 x0 与全局列对齐容差（pt）
COL_BOUNDARY_SLACK = 20      # 列边界归属判定的前移余量（pt）
MIN_AVG_COL_WIDTH = 30       # 平均列宽下限（pt），过窄 → 密集文本
MAX_COLS_PER_INCH = 10       # 列密度上限（列/英寸）
MAX_COLUMNS_BASE = 20        # 612pt（Letter）页宽基准最大列数，按页宽缩放
MIN_TABLE_ROW_RATIO = 0.20   # 表行占比下限
PARA_WIDTH_RATIO = 0.55      # 段落行宽度比阈值
PARA_MIN_CHARS = 60          # 段落行最小字符数
ROW_Y_TOLERANCE = 5          # 行归并 y 容差（pt）
WORD_X_TOLERANCE = 3         # extract_words x 容差
WORD_Y_TOLERANCE = 3         # extract_words y 容差

# MasterFormat 部分编号（如 ".1"、".2"）——列表项而非表行
PARTIAL_NUMBERING_PATTERN = re.compile(r"^\.\d+$")


def extract_form_content_from_words(page) -> str | None:
    """按词坐标聚类提取表单式内容（迁移自 markitdown _extract_form_content_from_words）。

    返回含 MD 表格的 Markdown 文本；页面不像表单时返回 None（调用方回退普通文本提取）。
    """
    words = page.extract_words(keep_blank_chars=True,
                               x_tolerance=WORD_X_TOLERANCE, y_tolerance=WORD_Y_TOLERANCE)
    if not words:
        return None

    # 按行归并（Y 容差）
    rows_by_y: dict[float, list] = {}
    for word in words:
        y_key = round(word["top"] / ROW_Y_TOLERANCE) * ROW_Y_TOLERANCE
        rows_by_y.setdefault(y_key, []).append(word)

    sorted_y_keys = sorted(rows_by_y.keys())
    page_width = page.width if hasattr(page, "width") else 612

    # 第一遍：逐行分析
    row_info: list[dict] = []
    for y_key in sorted_y_keys:
        row_words = sorted(rows_by_y[y_key], key=lambda w: w["x0"])
        if not row_words:
            continue
        first_x0 = row_words[0]["x0"]
        last_x1 = row_words[-1]["x1"]
        line_width = last_x1 - first_x0
        combined_text = " ".join(w["text"] for w in row_words)

        # 行内列组数初判
        x_positions = [w["x0"] for w in row_words]
        x_groups: list[float] = []
        for x in sorted(x_positions):
            if not x_groups or x - x_groups[-1] > X_GROUP_GAP:
                x_groups.append(x)

        is_paragraph = line_width > page_width * PARA_WIDTH_RATIO \
            and len(combined_text) > PARA_MIN_CHARS

        has_partial_numbering = bool(PARTIAL_NUMBERING_PATTERN.match(
            row_words[0]["text"].strip())) if row_words else False

        row_info.append({
            "y_key": y_key, "words": row_words, "text": combined_text,
            "x_groups": x_groups, "is_paragraph": is_paragraph,
            "num_columns": len(x_groups), "has_partial_numbering": has_partial_numbering,
        })

    # 收集所有「3+ 列且非段落」行的 x 坐标 → 全局列结构
    all_table_x_positions: list[float] = []
    for info in row_info:
        if info["num_columns"] >= 3 and not info["is_paragraph"]:
            all_table_x_positions.extend(info["x_groups"])
    if not all_table_x_positions:
        return None

    # 自适应聚类容差：gap 70 分位
    all_table_x_positions.sort()
    gaps = []
    for i in range(len(all_table_x_positions) - 1):
        gap = all_table_x_positions[i + 1] - all_table_x_positions[i]
        if gap > 5:
            gaps.append(gap)
    if gaps and len(gaps) >= 3:
        sorted_gaps = sorted(gaps)
        adaptive_tolerance = sorted_gaps[int(len(sorted_gaps) * GAP_PERCENTILE)]
        adaptive_tolerance = max(TOLERANCE_MIN, min(TOLERANCE_MAX, adaptive_tolerance))
    else:
        adaptive_tolerance = DEFAULT_TOLERANCE

    # 全局列边界
    global_columns: list[float] = []
    for x in all_table_x_positions:
        if not global_columns or x - global_columns[-1] > adaptive_tolerance:
            global_columns.append(x)

    # 防误判 2/3：平均列宽 + 列密度 + 页宽缩放最大列数
    if len(global_columns) > 1:
        content_width = global_columns[-1] - global_columns[0]
        avg_col_width = content_width / len(global_columns)
        if avg_col_width < MIN_AVG_COL_WIDTH:
            return None
        columns_per_inch = len(global_columns) / (content_width / 72)
        if columns_per_inch > MAX_COLS_PER_INCH:
            return None
        adaptive_max_columns = max(15, int(MAX_COLUMNS_BASE * (page_width / 612)))
        if len(global_columns) > adaptive_max_columns:
            return None
    else:
        return None  # 单列，非表单

    # 第二遍：行分类（对齐 2+ 全局列 → 表行；段落/部分编号行排除）
    for info in row_info:
        if info["is_paragraph"] or info["has_partial_numbering"]:
            info["is_table_row"] = False
            continue
        aligned_columns: set[int] = set()
        for word in info["words"]:
            word_x = word["x0"]
            for col_idx, col_x in enumerate(global_columns):
                if abs(word_x - col_x) < ALIGN_TOLERANCE:
                    aligned_columns.add(col_idx)
                    break
        info["is_table_row"] = len(aligned_columns) >= 2

    # 表区域（连续表行段）
    table_regions: list[tuple[int, int]] = []
    i = 0
    while i < len(row_info):
        if row_info[i]["is_table_row"]:
            start_idx = i
            while i < len(row_info) and row_info[i]["is_table_row"]:
                i += 1
            table_regions.append((start_idx, i))
        else:
            i += 1

    # 防误判 3：表行占比下限
    total_table_rows = sum(end - start for start, end in table_regions)
    if row_info and total_table_rows / len(row_info) < MIN_TABLE_ROW_RATIO:
        return None

    # 输出组装（表格经 md_table.build_md_table 保证自产表合规）
    num_cols = len(global_columns)

    def extract_cells(info: dict) -> list[str]:
        cells: list[str] = ["" for _ in range(num_cols)]
        for word in info["words"]:
            word_x = word["x0"]
            assigned_col = num_cols - 1
            for col_idx in range(num_cols - 1):
                if word_x < global_columns[col_idx + 1] - COL_BOUNDARY_SLACK:
                    assigned_col = col_idx
                    break
            cells[assigned_col] = (cells[assigned_col] + " " + word["text"]).strip()
        return cells

    result_lines: list[str] = []
    idx = 0
    region_starts = {start: (start, end) for start, end in table_regions}
    while idx < len(row_info):
        if idx in region_starts:
            start, end = region_starts[idx]
            table_data = [extract_cells(row_info[t]) for t in range(start, end)]
            if table_data:
                table_md = build_md_table(table_data, header=True)
                if table_md:
                    result_lines.append(table_md)
            idx = end
        else:
            # 表区域中部（非段首）不算非表内容；区域外输出原行文本
            in_table = any(start < idx < end for start, end in table_regions)
            if not in_table:
                result_lines.append(row_info[idx]["text"])
            idx += 1
    return "\n".join(result_lines)


def extract_pdf(pdf_path: str) -> dict:
    """整文档提取：逐页先试表单聚类，失败回退普通文本。返回 {"md", "meta"}。"""
    import pdfplumber
    parts = []
    pages_with_tables = 0
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            try:
                form = extract_form_content_from_words(page)
            except Exception:
                form = None
            if form and form.strip():
                parts.append(form.strip())
                pages_with_tables += 1
            else:
                t = page.extract_text()
                if t and t.strip():
                    parts.append(t.strip())
            page.close()
    meta = {"pages_with_form_tables": pages_with_tables}
    return {"md": "\n\n".join(parts), "meta": meta}


def main() -> int:
    ap = argparse.ArgumentParser(description="PDF 无边框表格/表单提取（M6）")
    ap.add_argument("--pdf", required=True, help="输入 PDF 路径")
    ap.add_argument("--md", required=True, help="输出 Markdown 路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON 元信息")
    args = ap.parse_args()
    from pathlib import Path
    if not Path(args.pdf).is_file():
        safe_print(json.dumps({"ok": False, "errors": [f"文件不存在：{args.pdf}"]}, ensure_ascii=False))
        return 2
    r = extract_pdf(args.pdf)
    Path(args.md).write_text(r["md"], encoding="utf-8")
    if args.json:
        safe_print(json.dumps({"ok": True, "md_path": args.md, **r["meta"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
