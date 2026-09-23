#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""repair_xlsx.py · xlsx 非规范属性二进制级修复（tri-xlsx2md · 自包含单文件）

MIT 归属：迁移自 Microsoft markitdown _xlsx_converter._repair_sheetview_show_zeroes（MIT）。
见 docs/markitdown-analysis-migration-20260909.md M5。

背景：部分生成器在 <sheetView> 写 showZeroes（规范拼写是 showZeros），
openpyxl 加载时按未知属性构造 SheetView 直接抛 TypeError 拒载整个工作簿
（read_only 模式延迟到 iter_rows 才抛，非 read_only 模式在 load 即抛）。
本修复只把该属性改名为规范拼写，不动任何其它内容（幂等、零误伤）。
"""
import io
import re
import zipfile

_SHEET_VIEW_TAG = re.compile(rb"<sheetView(?=[\s/>])[^>]*>")
_SHOW_ZEROES_ATTR = re.compile(rb"(?<=\s)showZeroes(\s*=)")


def repair_show_zeroes(xlsx_bytes: bytes) -> bytes:
    """把 <sheetView> 内的 showZeroes 改名为规范拼写 showZeros，仅此一处，不动其它内容。"""
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as src, \
         zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if (item.filename.startswith("xl/worksheets/")
                    and item.filename.endswith(".xml")
                    and b"showZeroes" in data):
                data = _SHEET_VIEW_TAG.sub(
                    lambda m: _SHOW_ZEROES_ATTR.sub(rb"showZeros\1", m.group(0)), data)
            dst.writestr(item, data)
    return out.getvalue()


if __name__ == "__main__":
    import argparse
    from _io_safe import safe_print
    ap = argparse.ArgumentParser(description="xlsx showZeroes 非规范属性修复（M5）")
    ap.add_argument("--xlsx", required=True, help="输入 xlsx 路径")
    ap.add_argument("--out", required=True, help="修复后输出路径")
    args = ap.parse_args()
    fixed = repair_show_zeroes(open(args.xlsx, "rb").read())
    with open(args.out, "wb") as f:
        f.write(fixed)
    safe_print(f"修复完成：{args.out}（{len(fixed)} 字节）")
