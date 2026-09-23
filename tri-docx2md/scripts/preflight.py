#!/usr/bin/env python3
"""门A · Word 预检分级（tri-docx2md）

确定性预检：文件类型判定（魔数/扩展名）/ OOXML 加密检测 / 文件大小 /
段落·图片·表格计数（python-docx 可用时，否则 zipfile 降级）/ 旧格式标记
→ 等级建议 L0/L1 或 BLOCK。

用法：
    python scripts/preflight.py --doc <路径> --json
    python scripts/preflight.py --doc <路径> --pretty

退出码：0 正常出报告（含 BLOCK/SKIP 建议）；2 参数/文件错误。
"""
from _io_safe import safe_print
import argparse
import json
import sys
import zipfile
import zlib
from pathlib import Path

from scale_guard import apply_scale_guard  # P2-2 输入规模守卫（anydoc limits.rs 口径）
from sniffer import verify_content_matches_extension  # M9 内容真身二次校验（家族同源副本）

COMPLEX_TABLE_COUNT = 5      # 表格数 ≥ 此值 → 复杂版式（L1）
COMPLEX_IMAGE_COUNT = 10     # 图片数 ≥ 此值 → 复杂版式（L1）
LARGE_SIZE_MB = 50           # 文件大小 > 此值（MB）→ 大文档风险提示

ZIP_MAGIC = b"PK\x03\x04"                                  # docx（OOXML zip 容器）
OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"            # doc（OLE 复合文档）


def detect_type(path: Path) -> str:
    """魔数判定文件类型：docx / doc / unknown。"""
    try:
        with open(path, "rb") as f:
            head = f.read(8)
    except OSError:
        return "unknown"
    if head.startswith(ZIP_MAGIC):
        return "docx"
    if head.startswith(OLE_MAGIC):
        return "doc"
    return "unknown"


def is_ooxml_encrypted(path: Path) -> bool:
    """docx OOXML 加密标记：zip 内含 EncryptionInfo / EncryptedPackage 条目。"""
    try:
        with zipfile.ZipFile(str(path)) as z:
            names = z.namelist()
    except (zipfile.BadZipFile, zlib.error, OSError):
        return False
    return any(n in ("EncryptionInfo", "EncryptedPackage") for n in names)


def count_docx_structure(path: Path) -> dict:
    """python-docx 可用时统计段落/图片/表格；否则 zipfile 解 document.xml 降级。"""
    counts = {"paragraph_count": None, "image_count": None,
              "table_count": None, "via": None}
    try:
        import docx  # python-docx
        d = docx.Document(str(path))
        counts["paragraph_count"] = len(d.paragraphs)
        counts["table_count"] = len(d.tables)
        counts["image_count"] = len(d.inline_shapes)
        counts["via"] = "python-docx"
        return counts
    except ImportError:
        pass
    except Exception:
        pass
    try:
        with zipfile.ZipFile(str(path)) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        counts["paragraph_count"] = xml.count("<w:p ")
        counts["table_count"] = xml.count("<w:tbl>")
        counts["image_count"] = xml.count("<w:drawing>") + xml.count("<pic:pic>")
        counts["via"] = "zipfile-xml"
    except Exception:
        pass
    return counts


# ---- 家族统一五格式优雅跳过守卫（用户指令 2026-09-08）----
# tri-xx2md 家族统一不支持 .odt/.ods/.odp/.rtf/.epub 转换：命中 MUST 明确提示
# 无法转换并跳过，NEVER 强行转换，NEVER 报错中断（exit 0，status=SKIP）。
UNSUPPORTED_EXTENSIONS = {".odt", ".ods", ".odp", ".rtf", ".epub"}
RTF_MAGIC = b"{\\rtf"
SKIP_MIME_PREFIXES = (b"application/vnd.oasis.opendocument.", b"application/epub+zip")
SUPPORTED_EXTENSIONS = ['.docx', '.doc', '.docm']  # .docm 与 .docx 同为 OPC zip（P1-1 矩阵）


# P1-1 归属仲裁规则（确定性）：1) SKIP 守卫先行——扩展名命中五不支持格式即 SKIP（纯扩展名判定，
# 刻意不做内容核验，见蒸馏报告 v1.3.0 P0-5 边界取舍）；2) 未命中则内容探测（RTF 魔数 / zip mimetype）
# 优先于扩展名；3) 内容与扩展名均为受支持格式但冲突 → BLOCK + 双方证据；4) 都失败 → BLOCK。
def check_unsupported(path: Path):
    """命中家族统一不支持格式时返回 SKIP 结果 dict；否则返回 None。"""
    ext = path.suffix.lower()
    reason = None
    if ext in UNSUPPORTED_EXTENSIONS:
        reason = f"扩展名 {ext} 属 tri-xx2md 家族统一不支持格式（.odt/.ods/.odp/.rtf/.epub）"
    else:
        try:
            with open(path, "rb") as f:
                head = f.read(8)
        except OSError:
            head = b""
        if head.startswith(RTF_MAGIC):
            reason = "内容为 RTF（{\\rtf 魔数）——tri-xx2md 家族统一不支持格式"
        elif head.startswith(b"PK\x03\x04"):
            # 误标守卫：ODF/EPUB 同为 zip 容器，读 mimetype 条目识别真实身份
            try:
                with zipfile.ZipFile(str(path)) as z:
                    mime = z.read("mimetype") if "mimetype" in z.namelist() else b""
            except Exception:
                mime = b""
            if mime.startswith(SKIP_MIME_PREFIXES):
                reason = "内容为 ODF/EPUB 包（zip mimetype）——tri-xx2md 家族统一不支持格式"
    if reason is None:
        return None
    return {
        "status": "SKIP",
        "reason_code": "unsupported_format",
        "file": str(path),
        "extension": ext,
        "grade_suggestion": "SKIP",
        "ok": True,
        "message": reason + "。本 skill 不支持该格式转换，已跳过（未做任何转换尝试）。",
        "supported_formats": SUPPORTED_EXTENSIONS,
        "suggestion": "如需转换该文件，可改用支持该格式的独立工具"
                      "（如 anydoc CLI：npx -y @firecrawl/anydoc <文件> -o out.md），"
                      "或先另存为受支持格式后重试。",
    }


def run_preflight(doc_path: Path) -> dict:
    result = {
        "file": str(doc_path),
        "size_bytes": doc_path.stat().st_size,
        "detected_type": None,
        "extension": doc_path.suffix.lower(),
        "doc_format": False,
        "encrypted": False,
        "paragraph_count": None,
        "image_count": None,
        "table_count": None,
        "grade_suggestion": None,
        "risks": [],
        "content_check": None,  # M9 内容真身二次校验
        "ok": False,
    }

    # M9 内容真身二次校验：魔数之外的轻量特征核验（防「扩展名对、内容不对」走错路径）
    content_check = verify_content_matches_extension(doc_path)
    result["content_check"] = content_check
    if not content_check["match"]:
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(
            f"扩展名与内容不符（{content_check['evidence']}）——请确认文件真实格式")
        return result

    detected = detect_type(doc_path)
    result["detected_type"] = detected
    if detected == "unknown":
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(
            "文件类型无法判定（魔数非 PK zip 头 / OLE 复合文档头）——请确认是 .docx/.docm/.doc 文件")
        return result

    if detected == "doc":
        result["doc_format"] = True
        result["risks"].append(
            "旧格式 .doc（OLE 复合文档）——anydoc 可用时直读首选（detect_backends JSON doc_convert.mode 决定），anydoc 缺失时才经 LibreOffice 中转"
            "（或 antiword 纯文本兜底），结构保真取决于转换质量；加密检测需 olefile 专用工具")

    if detected == "docx":
        result["encrypted"] = is_ooxml_encrypted(doc_path)
        if result["encrypted"]:
            result["grade_suggestion"] = "BLOCK"
            result["risks"].append(
                "OOXML 加密文档（检测到 EncryptionInfo/EncryptedPackage）——NEVER 破解，请合法解密后重试")
            return result
        counts = count_docx_structure(doc_path)
        result["paragraph_count"] = counts["paragraph_count"]
        result["image_count"] = counts["image_count"]
        result["table_count"] = counts["table_count"]
        if counts["via"] is None:
            result["risks"].append(
                "本地无 python-docx 且 document.xml 解析失败，无法统计段落/图片/表格"
                "——建议 pip install python-docx")

    if (result["size_bytes"] / (1024 * 1024)) > LARGE_SIZE_MB:
        result["risks"].append(
            f"大文档（{result['size_bytes'] / (1024 * 1024):.1f} MB）——转换耗时较长，可考虑分批")

    # 等级建议
    if result["doc_format"]:
        result["grade_suggestion"] = "L1"
    elif result["detected_type"] == "docx":
        complex_signal = (
            (result["table_count"] or 0) >= COMPLEX_TABLE_COUNT
            or (result["image_count"] or 0) >= COMPLEX_IMAGE_COUNT
        )
        if complex_signal:
            result["grade_suggestion"] = "L1"
            result["risks"].append(
                f"复杂版式信号（表格 {result['table_count']}、图片 {result['image_count']}）——建议标准档")
        else:
            result["grade_suggestion"] = "L0"

    # 输入规模守卫（P2-2）：硬上限超限 → BLOCK；详见 result["scale_guard"]
    apply_scale_guard(result, doc_path)

    result["ok"] = result["grade_suggestion"] != "BLOCK"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-docx2md 门A 预检分级")
    ap.add_argument("--doc", required=True, help="Word 文件路径（.docx/.docm/.doc）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--pretty", action="store_true", help="输出人类可读摘要")
    args = ap.parse_args()

    doc_path = Path(args.doc)
    if not doc_path.is_file():
        safe_print(json.dumps({"ok": False, "errors": [f"文件不存在：{doc_path}"]}, ensure_ascii=False))
        return 2

    skip = check_unsupported(doc_path)
    if skip is not None:
        if args.json or not args.pretty:
            safe_print(json.dumps(skip, ensure_ascii=False, indent=2))
        else:
            safe_print("状态：SKIP（无法转换，已跳过，未做任何转换尝试）")
            safe_print(f"原因：{skip['message']}")
            safe_print(f"本 skill 支持格式：{', '.join(skip['supported_formats'])}")
            safe_print(f"建议：{skip['suggestion']}")
        return 0

    result = run_preflight(doc_path)
    if args.json or not args.pretty:
        safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        safe_print(f"文件：{result['file']}")
        safe_print(f"类型：{result['detected_type']}（扩展名 {result['extension']}）｜ 旧格式 .doc：{result['doc_format']}")
        safe_print(f"加密：{result['encrypted']} ｜ 段落：{result['paragraph_count']} ｜ 图片：{result['image_count']} ｜ 表格：{result['table_count']}")
        safe_print(f"等级建议：{result['grade_suggestion']}")
        for r in result["risks"]:
            safe_print(f"  - 风险：{r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
