#!/usr/bin/env python3
"""门A · PPT 预检分级（tri-pptx2md）

确定性预检：文件类型魔数判定（.pptx=PK zip 头 / .ppt=OLE 复合文档头 D0CF11E0）/
页数（slide 数）/ 备注存在性 / 图片计数 / 旧格式标记 → 等级建议 L0/L1/PPT 或 BLOCK。

用法：
    python scripts/preflight.py --ppt <路径> --json
    python scripts/preflight.py --ppt <路径> --pretty

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

OLE_MAGIC = bytes.fromhex("D0CF11E0A1B11AE1")   # .ppt OLE 复合文档头
ZIP_MAGIC = b"PK"                                # .pptx OOXML zip 头
COMPLEX_IMAGE_THRESHOLD = 5                      # 图片数 ≥ 此值 → 复杂版式信号
COMPLEX_NOTES_RATIO = 0.5                        # 备注页占比 ≥ 此值 → 复杂版式信号


def sniff_type(path: Path) -> str:
    """魔数判定：pptx / ppt / unknown。"""
    with open(path, "rb") as f:
        head = f.read(8)
    if head.startswith(ZIP_MAGIC):
        return "pptx"
    if head.startswith(OLE_MAGIC):
        return "ppt"
    return "unknown"


def count_pptx_zip(path: Path) -> dict:
    """zipfile 探测 .pptx/.pptm/.ppsx/.ppsm（同为 OPC zip）：slide 数 / 备注页数 / 图片计数。"""
    # P1-5 判定路径：.pptm/.ppsx/.ppsm 与 .pptx 同为 OPC 容器，slide 探测通用；.pps/.pot 与 .ppt 同为 OLE
    out = {"slide_count": None, "notes_count": 0, "image_count": 0, "error": None}
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            slides = [n for n in names
                      if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
            notes = [n for n in names
                     if n.startswith("ppt/notesSlides/notesSlide") and n.endswith(".xml")]
            media = [n for n in names if n.startswith("ppt/media/")]
            out["slide_count"] = len(slides)
            out["notes_count"] = len(notes)
            out["image_count"] = len(media)
    except (zipfile.BadZipFile, zlib.error, OSError) as exc:
        out["error"] = str(exc)
    return out


# ---- 家族统一五格式优雅跳过守卫（用户指令 2026-09-08）----
# tri-xx2md 家族统一不支持 .odt/.ods/.odp/.rtf/.epub 转换：命中 MUST 明确提示
# 无法转换并跳过，NEVER 强行转换，NEVER 报错中断（exit 0，status=SKIP）。
UNSUPPORTED_EXTENSIONS = {".odt", ".ods", ".odp", ".rtf", ".epub"}
RTF_MAGIC = b"{\\rtf"
SKIP_MIME_PREFIXES = (b"application/vnd.oasis.opendocument.", b"application/epub+zip")
SUPPORTED_EXTENSIONS = ['.pptx', '.pptm', '.pps', '.pot', '.ppsx', '.ppsm', '.ppt']  # 同族 7 扩展名（P1-1 矩阵）


# P1-1 归属仲裁规则（确定性）：1) SKIP 守卫先行——扩展名命中五不支持格式即 SKIP；2) 内容探测
# （RTF 魔数 / zip mimetype）优先于扩展名；3) 受支持格式间冲突 → BLOCK + 证据；4) 都失败 → BLOCK。
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


def run_preflight(ppt_path: Path) -> dict:
    result = {
        "file": str(ppt_path),
        "size_bytes": ppt_path.stat().st_size,
        "file_type": None,
        "old_format": False,
        "slide_count": None,
        "notes_present": False,
        "notes_count": 0,
        "image_count": 0,
        "grade_suggestion": None,
        "risks": [],
        "content_check": None,  # M9 内容真身二次校验
        "ok": False,
    }

    # M9 内容真身二次校验：魔数之外的轻量特征核验（防「扩展名对、内容不对」走错路径）
    content_check = verify_content_matches_extension(ppt_path)
    result["content_check"] = content_check
    if not content_check["match"]:
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(
            f"扩展名与内容不符（{content_check['evidence']}）——请确认文件真实格式")
        return result

    result["file_type"] = sniff_type(ppt_path)
    if result["file_type"] == "unknown":
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append("魔数既非 PK（.pptx/.pptm/.ppsx/.ppsm）也非 D0CF11E0（.ppt/.pps/.pot）——非 PPT 家族文件，请确认输入")
        return result
    if result["file_type"] == "ppt":
        result["old_format"] = True
        result["grade_suggestion"] = "PPT"
        result["risks"].append(".ppt/.pps/.pot 旧格式（OLE）——anydoc 可用时直读首选，anydoc 缺失时才 LibreOffice headless 转中间 .pptx 再走标准链")
        apply_scale_guard(result, ppt_path)
        result["ok"] = True
        return result
    # .pptx：zipfile 探测
    info = count_pptx_zip(ppt_path)
    if info.get("error"):
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(f".pptx 无法解包：{info['error']}")
        return result
    result["slide_count"] = info["slide_count"]
    result["notes_count"] = info["notes_count"]
    result["notes_present"] = info["notes_count"] > 0
    result["image_count"] = info["image_count"]
    # 等级建议：复杂版式信号
    notes_ratio = (info["notes_count"] / info["slide_count"]
                   if info["slide_count"] else 0.0)
    complex_signal = (
        info["image_count"] >= COMPLEX_IMAGE_THRESHOLD
        or notes_ratio >= COMPLEX_NOTES_RATIO
    )
    if complex_signal:
        result["grade_suggestion"] = "L1"
        result["risks"].append(
            f"复杂版式信号（图片 {info['image_count']} 张、备注页占比 {notes_ratio:.0%}）——建议标准档"
        )
    else:
        result["grade_suggestion"] = "L0"
    if (info["slide_count"] or 0) > 80:
        result["risks"].append(f"大演示文稿（{info['slide_count']} 页）——L1 耗时较长，可考虑分批")

    # 输入规模守卫（P2-2）：硬上限超限 → BLOCK；详见 result["scale_guard"]
    apply_scale_guard(result, ppt_path)

    result["ok"] = result["grade_suggestion"] != "BLOCK"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-pptx2md 门A 预检分级")
    ap.add_argument("--ppt", required=True, help="PPT 文件路径（.pptx/.ppt）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--pretty", action="store_true", help="输出人类可读摘要")
    args = ap.parse_args()

    ppt_path = Path(args.ppt)
    if not ppt_path.is_file():
        safe_print(json.dumps({"ok": False, "errors": [f"文件不存在：{ppt_path}"]}, ensure_ascii=False))
        return 2

    skip = check_unsupported(ppt_path)
    if skip is not None:
        if args.json or not args.pretty:
            safe_print(json.dumps(skip, ensure_ascii=False, indent=2))
        else:
            safe_print("状态：SKIP（无法转换，已跳过，未做任何转换尝试）")
            safe_print(f"原因：{skip['message']}")
            safe_print(f"本 skill 支持格式：{', '.join(skip['supported_formats'])}")
            safe_print(f"建议：{skip['suggestion']}")
        return 0

    result = run_preflight(ppt_path)
    if args.json or not args.pretty:
        safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        safe_print(f"文件：{result['file']}")
        safe_print(f"类型：{result['file_type']} ｜ 旧格式：{result['old_format']}")
        safe_print(f"页数：{result['slide_count']} ｜ 备注：{result['notes_present']} ｜ 图片：{result['image_count']}")
        safe_print(f"等级建议：{result['grade_suggestion']}")
        for r in result["risks"]:
            safe_print(f"  - 风险：{r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
