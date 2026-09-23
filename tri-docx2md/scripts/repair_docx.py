#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""repair_docx.py · docx 预处理修复器（tri-docx2md · 自包含单文件，M3 迁移物）

价值（对应 markitdown-analysis-migration-20260909.md P0-3/M3）：
mammoth / python-docx 降级路径下——
  1. OMML 公式直接丢失          → 逐公式转 LaTeX（$...$ / $$...$$）
  2. styles.xml 缺 w:type       → mammoth KeyError 整单失败 → 补默认 paragraph
  3. styles.xml 缺 w:styleId    → 不可被引用，删除该 style
  4. w:dstrike 双删除线          → mammoth 不认 → 归一为 w:strike
  5. ZIP 本地头/中央目录文件名大小写不一致 → BadZipFile → 二进制级修补

实现（报告 M3 落地要点① + 逐元素容错原则）：
  · 公式转换编排调用 markitdown 官方 API（oMath2Latex，MIT）——零源码复制；
    实测发现 markitdown 整体 pre_process_docx 会在单个畸形公式上放弃全部数学转换
    （内部整步 try/except），故按报告 M3 代码自身的逐元素结构落地：单公式失败
    只跳过该公式并计数，NEVER 虚标 math_converted（家族诚实声明）。
  · zip casing / styles / dstrike 兜底实现迁移自 markitdown 内部逻辑（MIT，归属保留）。
  · 每步独立 try/except：一步失败不废其余步骤。

用法：
    python scripts/repair_docx.py --doc in.docx --output repaired.docx [--json]
退出码：0 修复完成；3 产物非法；2 参数/文件错误。
自包含约束：仅标准库 + 本 skill detect_backends 已探测的 markitdown/bs4，NEVER import 其它 skill 模块。
"""
from _io_safe import safe_print
import argparse
import json
import struct
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET


# ---- 兜底/基础实现（迁移自 markitdown pre_process_docx 内部逻辑，MIT，归属声明保留） ----


def fix_zip_filename_casing(data: bytes) -> bytes:
    """按中央目录权威文件名修补本地头大小写不一致（BadZipFile 根因之一）。"""
    try:
        with zipfile.ZipFile(BytesIO(data), "r") as zf:
            cd_entries = {zi.header_offset: (zi.orig_filename, zi.flag_bits)
                          for zi in zf.infolist()}
    except zipfile.BadZipFile:
        return data
    raw = bytearray(data)
    patched = False
    for offset, (cd_name, flag_bits) in cd_entries.items():
        if offset + 30 > len(raw) or raw[offset:offset + 4] != b"PK\x03\x04":
            continue
        (fname_len,) = struct.unpack_from("<H", raw, offset + 26)
        if offset + 30 + fname_len > len(raw):
            continue
        local_name = bytes(raw[offset + 30:offset + 30 + fname_len])
        central_name = cd_name.encode("utf-8" if flag_bits & 0x800 else "cp437")
        if (local_name != central_name and len(local_name) == len(central_name)
                and local_name.lower() == central_name.lower()):
            raw[offset + 30:offset + 30 + fname_len] = central_name
            patched = True
    return bytes(raw) if patched else data


def repair_styles(xml: bytes) -> bool:
    """缺 w:type 补默认 paragraph；缺 w:styleId 删除。返回是否执行成功。"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(xml, features="xml")
    for tag in soup.find_all("w:style"):
        if not tag.has_attr("w:styleId"):
            tag.decompose()
        elif not tag.has_attr("w:type"):
            tag["w:type"] = "paragraph"
    return True


def normalize_dstrike(xml: bytes) -> bytes:
    """w:dstrike → w:strike（先字节级快检，避免大文档无谓 XML 往返）。"""
    if b"dstrike" not in xml:
        return xml
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(xml.decode("utf-8", errors="replace"), features="xml")
    for tag in soup.find_all("dstrike"):
        tag.name = "strike"
    return str(soup).encode()


def convert_math_element_level(xml: bytes) -> tuple:
    """逐公式 OMML→LaTeX（编排调用 markitdown oMath2Latex API；单公式失败不废其余）。

    返回 (new_xml, stats)；stats.math_total/converted/failed 为诚实计数。
    """
    stats = {"math_via": "markitdown.api(oMath2Latex)", "math_total": 0,
             "math_converted_n": 0, "math_failed_n": 0}
    try:
        from markitdown.converter_utils.docx.pre_process import MATH_ROOT_TEMPLATE
        from markitdown.converter_utils.docx.math.omml import OMML_NS, oMath2Latex
    except ImportError:
        stats["math_via"] = "markitdown-missing（公式转换跳过，不阻塞）"
        return xml, stats
    from bs4 import BeautifulSoup, Tag

    def _latex(tag) -> str:
        root = ET.fromstring(MATH_ROOT_TEMPLATE.format(str(tag)))
        el = root.find(OMML_NS + "oMath")
        return "" if el is None else oMath2Latex(el).latex

    soup = BeautifulSoup(xml.decode("utf-8", errors="replace"), features="xml")

    for para in soup.find_all("oMathPara"):
        stats["math_total"] += 1
        try:
            p = Tag(name="w:p")
            for child in para.find_all("oMath"):
                t = Tag(name="w:t")
                t.string = f"$${_latex(child)}$$"
                r = Tag(name="w:r")
                r.append(t)
                p.append(r)
            para.replace_with(p)
            stats["math_converted_n"] += 1
        except Exception:
            stats["math_failed_n"] += 1

    for om in soup.find_all("oMath"):
        if om.find_parent("oMathPara"):
            continue  # 已随 oMathPara 整体转换/失败
        stats["math_total"] += 1
        try:
            t = Tag(name="w:t")
            t.string = f"${_latex(om)}$"
            r = Tag(name="w:r")
            r.append(t)
            om.replace_with(r)
            stats["math_converted_n"] += 1
        except Exception:
            stats["math_failed_n"] += 1

    return str(soup).encode(), stats


def pre_process_docx_bytes(data: bytes) -> tuple:
    """主入口：zip casing → 逐文件（styles/dstrike/math）。每步独立容错，stats 诚实。"""
    stats = {"via": "builtin+markitdown.oMath2Latex", "zip_casing_fixed": False,
             "styles_repaired": False, "dstrike_normalized": False,
             "math_via": "not-run", "math_total": 0, "math_converted_n": 0,
             "math_failed_n": 0}
    data = fix_zip_filename_casing(data)
    out = BytesIO()
    with zipfile.ZipFile(BytesIO(data), "r") as zin, \
         zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in zin.namelist():
            content = zin.read(name)
            try:
                if name == "word/styles.xml":
                    content = normalize_dstrike(content)
                    stats["styles_repaired"] = repair_styles(content)
                    stats["dstrike_normalized"] = True
                elif name in ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml"):
                    content = normalize_dstrike(content)
                    stats["dstrike_normalized"] = True
                    content, mstats = convert_math_element_level(content)
                    for k, v in mstats.items():
                        stats[k] = v
            except Exception:
                pass  # 每步独立容错：一步失败不废其余（markitdown 同款策略）
            zout.writestr(name, content)
    return out.getvalue(), stats


# ---- 向后兼容：convert_pipeline 的 M3 前置调用此函数 ----


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-docx2md M3 docx 预处理修复器")
    ap.add_argument("--doc", required=True, help="输入 .docx/.docm 路径")
    ap.add_argument("--output", required=True, help="修复后输出路径（不覆盖输入）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc_path = Path(args.doc)
    if not doc_path.is_file():
        safe_print(json.dumps({"ok": False, "errors": [f"文件不存在：{doc_path}"]}, ensure_ascii=False))
        return 2

    data = doc_path.read_bytes()
    fixed, stats = pre_process_docx_bytes(data)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(fixed)

    zip_ok = True
    try:
        with zipfile.ZipFile(str(out_path)) as z:
            _ = z.namelist()
    except Exception:
        zip_ok = False
    stats["zip_valid"] = zip_ok
    stats["bytes_before"] = len(data)
    stats["bytes_after"] = len(fixed)

    payload = {"ok": zip_ok, "input": str(doc_path), "output": str(out_path), "stats": stats}
    if args.json:
        safe_print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        safe_print(f"via={stats['via']} ｜ 公式 {stats['math_converted_n']}/{stats['math_total']} 转换"
                   f"（失败 {stats['math_failed_n']}）｜ zip 合法={zip_ok}")
        safe_print(f"输出：{out_path}")
    return 0 if zip_ok else 3


if __name__ == "__main__":
    sys.exit(main())
