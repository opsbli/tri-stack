#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sniffer.py · 内容真身二次校验 + charset 嗅探（每 skill 独立完整副本，单 skill 可单独运行）

MIT 归属：设计迁移自 Microsoft markitdown _get_stream_info_guesses / charset_normalizer
用法（MIT）。见 docs/markitdown-analysis-migration-20260909.md M9。

自包含约束：charset_normalizer 为可选依赖（不可用时回退 utf-8），其余仅标准库；
NEVER import 其它 skill 模块。

校验族按**扩展名**映射（家族多扩展名现实：.doc/.xls/.ppt 为 OLE 复合文档，
.docx/.xlsx/.pptx 族为 OPC zip，.csv 为无可靠特征的文本 → 跳过校验）。
仅做「防错路径」校验，不做家族统一 SKIP 五格式识别（该决策由既有守卫负责）。
"""
import re
import zipfile
from pathlib import Path

# 泛化标签特征（实现细化，偏离报告代码样例处，已记录于批次二报告）：
# 纯 <html>/<!doctype html> 特征会误伤无骨架的片段 HTML（如 <div>x</div>.html），
# 命中任意「<标签名」形态即视为 HTML 特征，防止有效输入被误 BLOCK。
_ANY_TAG_RE = re.compile(rb"<[a-zA-Z][a-zA-Z0-9]*(\s|>|/)")
_HTML_FEATURES = (b"<html", b"<!doctype html")
_OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # OLE2 复合文档（CFB）签名


def detect_charset(data: bytes) -> str:
    """前 64KB 编码探测；charset_normalizer 不可用时回退 utf-8。"""
    try:
        from charset_normalizer import from_bytes
        best = from_bytes(data[:65536]).best()
        return best.encoding if best else "utf-8"
    except ImportError:
        return "utf-8"


def _head(path: Path) -> bytes:
    with path.open("rb") as f:
        return f.read(4096)


def _zip_has(path: Path, member: str) -> bool:
    try:
        with zipfile.ZipFile(str(path)) as z:
            return member in z.namelist()
    except Exception:
        return False


def _check_opc_content_types(path: Path, head: bytes) -> bool:
    """OPC 容器（docx/docm）：zip 内必有 [Content_Types].xml（区别于普通 zip）。"""
    return b"[Content_Types].xml" in head or _zip_has(path, "[Content_Types].xml")


def _check_xlsx(path: Path, head: bytes) -> bool:
    """xlsx/xlsm：zip 内必有 xl/workbook.xml。"""
    return _zip_has(path, "xl/workbook.xml")


def _check_pptx(path: Path, head: bytes) -> bool:
    """pptx 族：zip 内必有 ppt/presentation.xml。"""
    return _zip_has(path, "ppt/presentation.xml")


def _check_ole(path: Path, head: bytes) -> bool:
    """OLE 复合文档（doc/xls/xlsb）：CFB 签名。"""
    return head.startswith(_OLE_MAGIC)


def _check_ppt_legacy(path: Path, head: bytes) -> bool:
    """ppt/pps/pot 旧格式：OLE 签名或 OPC 结构二选一（并集防误伤）。"""
    return _check_ole(path, head) or _check_pptx(path, head)


def _check_html(head: bytes) -> bool:
    low = head.lower()
    return any(f in low for f in _HTML_FEATURES) or _ANY_TAG_RE.search(head) is not None


def _check_pdf(head: bytes) -> bool:
    return head.startswith(b"%PDF-")


# 扩展名 → 校验函数（fn(path, head)；csv 等无可靠特征格式不校验）
_CHECKS = {
    ".docx": _check_opc_content_types, ".docm": _check_opc_content_types,
    ".xlsx": _check_xlsx, ".xlsm": _check_xlsx,
    ".pptx": _check_pptx, ".pptm": _check_pptx, ".ppsx": _check_pptx, ".ppsm": _check_pptx,
    ".doc": _check_ole, ".xls": _check_ole, ".xlsb": _check_ole,
    ".ppt": _check_ppt_legacy, ".pps": _check_ppt_legacy, ".pot": _check_ppt_legacy,
    ".html": lambda p, h: _check_html(h), ".htm": lambda p, h: _check_html(h),
    ".pdf": lambda p, h: _check_pdf(h),
}


def verify_content_matches_extension(path, detected_magic: str = "") -> dict:
    """魔数之外的轻量特征二次校验（迁移自 markitdown IpynbConverter.accepts 的
    「认得 MIME 再验内容」模式）。

    返回 {"match": bool, "evidence": str}。detected_magic 为可选提示（调试用），
    实际按文件扩展名映射校验族。
    """
    path = Path(path)
    try:
        head = _head(path)
    except OSError:
        return {"match": True, "evidence": "unreadable, skip verify"}
    fn = _CHECKS.get(path.suffix.lower())
    if fn is None:
        return {"match": True, "evidence": "no extra check for this type"}
    try:
        ok = bool(fn(path, head))
    except Exception:
        ok = False
    return {"match": ok, "evidence": f"feature-check {path.suffix.lower()} -> {ok}"}
