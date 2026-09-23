#!/usr/bin/env python3
"""门A · PDF 预检分级（tri-pdf2md）

确定性预检：加密/页数/文本层抽样密度/扫描件判定/混合类型/表格图片信号 → 等级建议 L0/L1/L2 或 BLOCK。

用法：
    python scripts/preflight.py --pdf <路径> [--sample-pages 12] --json
    python scripts/preflight.py --pdf <路径> --pretty

退出码：0 正常出报告（含 BLOCK/SKIP 建议）；2 参数/文件错误。
"""
from _io_safe import safe_print
import argparse
import json
import sys
import zipfile
from pathlib import Path

from scale_guard import apply_scale_guard  # P2-2 输入规模守卫（anydoc limits.rs 口径）
from sniffer import verify_content_matches_extension  # M9 内容真身二次校验（家族同源副本）

SCAN_CHAR_THRESHOLD = 50      # 平均字符/页低于此值视为无文本层（扫描件）
SAMPLE_PAGES_DEFAULT = 12     # 抽样页数上限
COMPLEX_TABLE_PAGES = 2       # 抽样中 ≥2 页含表格 → 复杂版面信号
COMPLEX_IMAGE_RATIO = 0.5     # 抽样中 ≥50% 页含图片 → 复杂版面信号


def probe_reader(pdf_path: Path):
    """优先 pypdf，回退 pdfplumber，最后报不可用。返回 (reader_kind, opener)。"""
    try:
        import pypdf  # noqa: F401
        return "pypdf", None
    except ImportError:
        pass
    try:
        import pdfplumber  # noqa: F401
        return "pdfplumber", None
    except ImportError:
        pass
    return None, None


def extract_page_text_pypdf(reader, idx: int) -> str:
    try:
        return reader.pages[idx].extract_text() or ""
    except Exception:
        return ""


# ---- 家族统一五格式优雅跳过守卫（用户指令 2026-09-08）----
# tri-xx2md 家族统一不支持 .odt/.ods/.odp/.rtf/.epub 转换：命中 MUST 明确提示
# 无法转换并跳过，NEVER 强行转换，NEVER 报错中断（exit 0，status=SKIP）。
UNSUPPORTED_EXTENSIONS = {".odt", ".ods", ".odp", ".rtf", ".epub"}
RTF_MAGIC = b"{\\rtf"
SKIP_MIME_PREFIXES = (b"application/vnd.oasis.opendocument.", b"application/epub+zip")
SUPPORTED_EXTENSIONS = ['.pdf']


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


def run_preflight(pdf_path: Path, sample_pages: int) -> dict:
    result = {
        "file": str(pdf_path),
        "size_bytes": pdf_path.stat().st_size,
        "page_count": None,
        "encrypted": False,
        "decryptable_with_empty": None,
        "sampled_pages": [],
        "avg_chars_per_page": None,
        "text_pages": 0,
        "empty_pages": 0,
        "table_pages": 0,
        "image_pages": 0,
        "scanned": False,
        "mixed": False,
        "grade_suggestion": None,
        "risks": [],
        "content_check": None,  # M9 内容真身二次校验
        "ok": False,
    }

    # M9 内容真身二次校验：魔数之外的轻量特征核验（防「扩展名对、内容不对」走错路径）
    content_check = verify_content_matches_extension(pdf_path)
    result["content_check"] = content_check
    if not content_check["match"]:
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(
            f"扩展名与内容不符（{content_check['evidence']}）——请确认文件为 %PDF- 头的 PDF")
        return result

    kind, _ = probe_reader(pdf_path)
    if kind is None:
        result["risks"].append("本地无 pypdf/pdfplumber，无法预检——请安装：pip install pypdf pdfplumber")
        return result

    if kind == "pypdf":
        import pypdf
        try:
            reader = pypdf.PdfReader(str(pdf_path))
        except Exception as exc:
            result["risks"].append(f"PDF 无法打开：{exc}")
            return result
        if reader.is_encrypted:
            result["encrypted"] = True
            try:
                ok = reader.decrypt("")
                result["decryptable_with_empty"] = bool(ok)
            except Exception:
                result["decryptable_with_empty"] = False
            if not result["decryptable_with_empty"]:
                result["grade_suggestion"] = "BLOCK"
                result["risks"].append("PDF 已加密且空口令不可解——NEVER 破解，请合法解密后重试")
                return result
        result["page_count"] = len(reader.pages)
        pages = list(range(len(reader.pages)))
        step = max(1, len(pages) // sample_pages)
        sample = pages[::step][:sample_pages]
        if pages and pages[-1] not in sample:
            sample.append(pages[-1])
        for idx in sample:
            text = extract_page_text_pypdf(reader, idx)
            n_img = 0
            try:
                res = reader.pages[idx].get("/Resources") or {}
                xobj = res.get("/XObject")
                if xobj is not None:
                    xobj = xobj.get_object()
                    n_img = sum(
                        1 for k in xobj
                        if getattr(xobj[k].get_object(), "get", lambda _k, _d=None: None)("/Subtype") == "/Image"
                    )
            except Exception:
                pass
            result["sampled_pages"].append({"page": idx + 1, "chars": len(text), "images": n_img})
            if len(text.strip()) >= SCAN_CHAR_THRESHOLD:
                result["text_pages"] += 1
            else:
                result["empty_pages"] += 1
            if n_img > 0:
                result["image_pages"] += 1
    else:
        import pdfplumber
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                if getattr(pdf, "is_encrypted", False):
                    # pdfplumber 打开成功即空口令可解；此处仅记录标记
                    result["encrypted"] = True
                    result["decryptable_with_empty"] = True
                result["page_count"] = len(pdf.pages)
                pages = list(range(len(pdf.pages)))
                step = max(1, len(pages) // sample_pages)
                sample = pages[::step][:sample_pages]
                if pages and pages[-1] not in sample:
                    sample.append(pages[-1])
                for idx in sample:
                    page = pdf.pages[idx]
                    text = page.extract_text() or ""
                    n_img = len(page.images)
                    n_tab = len(page.find_tables())
                    result["sampled_pages"].append(
                        {"page": idx + 1, "chars": len(text), "images": n_img, "tables": n_tab}
                    )
                    if len(text.strip()) >= SCAN_CHAR_THRESHOLD:
                        result["text_pages"] += 1
                    else:
                        result["empty_pages"] += 1
                    if n_img > 0:
                        result["image_pages"] += 1
                    if n_tab > 0:
                        result["table_pages"] += 1
        except Exception as exc:
            result["risks"].append(f"PDF 无法打开：{exc}")
            return result

    total = result["text_pages"] + result["empty_pages"]
    if total > 0:
        sampled_chars = sum(p["chars"] for p in result["sampled_pages"])
        result["avg_chars_per_page"] = round(sampled_chars / len(result["sampled_pages"]), 1)
        result["scanned"] = result["text_pages"] == 0
        result["mixed"] = 0 < result["text_pages"] < total

    n_sample = len(result["sampled_pages"])
    if result["scanned"]:
        result["grade_suggestion"] = "L2"
        result["risks"].append("扫描件（抽样页全部无文本层）——需 OCR 精细档，质量预期 C 级起步")
    elif result["mixed"]:
        result["grade_suggestion"] = "L1"
        result["risks"].append(f"混合类型（{result['text_pages']}/{total} 抽样页有文本层）——无文本层页需 OCR")
    else:
        complex_signal = (
            result["table_pages"] >= COMPLEX_TABLE_PAGES
            or (n_sample > 0 and result["image_pages"] / n_sample >= COMPLEX_IMAGE_RATIO)
        )
        if complex_signal:
            result["grade_suggestion"] = "L1"
            result["risks"].append(
                f"复杂版面信号（表格页 {result['table_pages']}、图片页 {result['image_pages']}/{n_sample}）——建议标准档"
            )
        else:
            result["grade_suggestion"] = "L0"
    if (result["page_count"] or 0) > 300:
        result["risks"].append(f"大文档（{result['page_count']} 页）——L1/L2 耗时较长，可考虑分批")

    # 输入规模守卫（P2-2）：硬上限超限 → BLOCK；详见 result["scale_guard"]
    apply_scale_guard(result, pdf_path)

    result["ok"] = result["grade_suggestion"] != "BLOCK"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-pdf2md 门A 预检分级")
    ap.add_argument("--pdf", required=True, help="PDF 文件路径")
    ap.add_argument("--sample-pages", type=int, default=SAMPLE_PAGES_DEFAULT, help="抽样页数上限")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--pretty", action="store_true", help="输出人类可读摘要")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_file():
        safe_print(json.dumps({"ok": False, "errors": [f"文件不存在：{pdf_path}"]}, ensure_ascii=False))
        return 2

    skip = check_unsupported(pdf_path)
    if skip is not None:
        if args.json or not args.pretty:
            safe_print(json.dumps(skip, ensure_ascii=False, indent=2))
        else:
            safe_print("状态：SKIP（无法转换，已跳过，未做任何转换尝试）")
            safe_print(f"原因：{skip['message']}")
            safe_print(f"本 skill 支持格式：{', '.join(skip['supported_formats'])}")
            safe_print(f"建议：{skip['suggestion']}")
        return 0

    result = run_preflight(pdf_path, max(1, args.sample_pages))
    if args.json or not args.pretty:
        safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        safe_print(f"文件：{result['file']}")
        safe_print(f"页数：{result['page_count']} ｜ 加密：{result['encrypted']}")
        safe_print(f"平均字符/页：{result['avg_chars_per_page']} ｜ 扫描件：{result['scanned']} ｜ 混合：{result['mixed']}")
        safe_print(f"等级建议：{result['grade_suggestion']}")
        for r in result["risks"]:
            safe_print(f"  - 风险：{r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
