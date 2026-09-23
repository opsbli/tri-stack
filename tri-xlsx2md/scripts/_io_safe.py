#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_io_safe · Windows 控制台输出编码兜底（tri-xx2md 家族同源副本 · 每 skill 独立完整文件）

迁移自 Microsoft markitdown __main__._handle_output（MIT）的 errors="replace" 模式。
背景：家族脚本此前直接 print(json.dumps(..., ensure_ascii=False))，Windows GBK 控制
台输出含 GBK 外字符（emoji/生僻字/文件衍生内容）时会 UnicodeEncodeError 崩溃。
safe_print 对不可编码字符替换为 ?，保证任何脚本「NEVER 因输出崩溃」。

自包含约束：本文件仅依赖标准库 sys，NEVER import 其它 skill 的模块。
"""

import sys


def safe_print(text: str = "") -> None:
    """Windows GBK 控制台兜底：不可编码字符替换为 ?，NEVER 因输出崩溃。"""
    enc = sys.stdout.encoding or "utf-8"
    try:
        print(text.encode(enc, errors="replace").decode(enc))
    except Exception:
        print(text.encode("ascii", errors="replace").decode("ascii"))
