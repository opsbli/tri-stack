#!/usr/bin/env python3
"""门A · HTML 预检分级（tri-html2md）

确定性预检：文件类型/编码检测/HTML 合法性/文件大小/内嵌资源计数（img/script/style）/
表格表单计数 → 等级建议 L0/L1 或 BLOCK。

编码检测策略（确定性，不猜测）：
  1. 二进制嗅探（NUL 字节 / 高比例控制字符 → 非文本 HTML，直接 BLOCK）
  2. BOM 探测（utf-8-sig / utf-16 / utf-32）
  3. <meta charset> / <meta http-equiv="Content-Type"> 声明
  4. 候选解码探测（utf-8 → gbk → gb18030 → big5 → shift_jis），以「无解码错误且无 U+FFFD」为通过标准
  5. 全部失败 → BLOCK（提示用户提供正确编码或先转码，NEVER 猜测解码）

用法：
    python scripts/preflight.py --html <路径> --json
    python scripts/preflight.py --html <路径> --pretty

退出码：0 正常出报告（含 BLOCK/SKIP 建议）；2 参数/文件错误。
"""
from _io_safe import safe_print
import argparse
import json
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path

from scale_guard import apply_scale_guard  # P2-2 输入规模守卫（anydoc limits.rs 口径）
from sniffer import verify_content_matches_extension  # M9 内容真身二次校验（家族同源副本）

COMPLEX_TABLE_THRESHOLD = 3        # 表格+表单 ≥3 → L1
COMPLEX_RESOURCE_THRESHOLD = 10    # img+script+style ≥10 → L1
LARGE_FILE_BYTES = 2 * 1024 * 1024  # ≥2MB → L1
MOJIBAKE_RE = re.compile(r"锟斤拷|烫烫烫|锘|�|Ã|â€")

# 候选解码顺序（确定性）。latin-1 是 catch-all（任何字节都能解），会击穿 BLOCK 判定，故不列入。
CANDIDATE_ENCODINGS = ["utf-8", "gbk", "gb18030", "big5", "shift_jis"]


class PreflightParser(HTMLParser):
    """统计内嵌资源与表格/表单计数；同时收集解析错误。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.img_count = 0
        self.script_count = 0
        self.style_count = 0
        self.table_count = 0
        self.form_count = 0
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.img_count += 1
        elif tag == "script":
            self.script_count += 1
        elif tag == "style":
            self.style_count += 1
        elif tag == "table":
            self.table_count += 1
        elif tag == "form":
            self.form_count += 1

    def handle_startendtag(self, tag, attrs):
        if tag == "img":
            self.img_count += 1

    def error(self, message):
        self.errors.append(message)


def is_binary_sniff(raw: bytes) -> bool:
    """二进制嗅探：NUL 字节或高比例控制字符 → 判定为非文本（非 HTML）。

    有 BOM 的文本文件（含 UTF-16/32）不嗅探，避免误伤。控制字符统计排除
    常见空白（0x09 tab / 0x0A LF / 0x0D CR），其余 0x00-0x08、0x0B-0x0C、
    0x0E-0x1F 计入。
    """
    if raw.startswith(b"\xef\xbb\xbf") or raw.startswith(b"\xff\xfe") \
            or raw.startswith(b"\xfe\xff") or raw.startswith(b"\x00\x00\xfe\xff") \
            or raw.startswith(b"\xff\xfe\x00\x00"):
        return False
    chunk = raw[:1024]
    if b"\x00" in chunk:
        return True
    if not chunk:
        return False
    control = sum(1 for b in chunk if b < 0x09 or (0x0E <= b <= 0x1F))
    return control / len(chunk) > 0.30


def detect_encoding(raw: bytes) -> dict:
    """BOM → meta charset → 候选解码探测。返回 {encoding, confidence, sample}。"""
    # 1. BOM 探测
    if raw.startswith(b"\xef\xbb\xbf"):
        return {"encoding": "utf-8-sig", "confidence": "bom", "sample": ""}
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return {"encoding": "utf-16", "confidence": "bom", "sample": ""}
    if raw.startswith(b"\x00\x00\xfe\xff") or raw.startswith(b"\xff\xfe\x00\x00"):
        return {"encoding": "utf-32", "confidence": "bom", "sample": ""}

    head = raw[:4096]
    # 2. meta charset 声明
    try:
        head_text = head.decode("ascii", errors="ignore")
    except Exception:
        head_text = ""
    m = re.search(r'<meta[^>]+charset\s*=\s*["\']?([A-Za-z0-9_\-]+)', head_text, re.IGNORECASE)
    if m:
        return {"encoding": m.group(1), "confidence": "meta", "sample": ""}

    # 3. 候选解码探测：接受第一个「无解码错误且无 U+FFFD」的候选。
    #    utf-8/gbk 等对非法字节序列严格报错，首个干净解码即大概率正确；
    #    误判场景（如 gbk 解 utf-8 字节）由门D 的编码误判特征（锟斤拷/Ã/â€）兜底检出。
    for enc in CANDIDATE_ENCODINGS:
        try:
            text = raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
        if "\ufffd" in text:
            continue
        return {"encoding": enc, "confidence": "probe", "sample": text[:80]}
    return {"encoding": None, "confidence": None, "sample": ""}


# ---- 家族统一五格式优雅跳过守卫（用户指令 2026-09-08）----
# tri-xx2md 家族统一不支持 .odt/.ods/.odp/.rtf/.epub 转换：命中 MUST 明确提示
# 无法转换并跳过，NEVER 强行转换，NEVER 报错中断（exit 0，status=SKIP）。
UNSUPPORTED_EXTENSIONS = {".odt", ".ods", ".odp", ".rtf", ".epub"}
RTF_MAGIC = b"{\\rtf"
SKIP_MIME_PREFIXES = (b"application/vnd.oasis.opendocument.", b"application/epub+zip")
SUPPORTED_EXTENSIONS = ['.html', '.htm']


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


def run_preflight(html_path: Path) -> dict:
    result = {
        "file": str(html_path),
        "size_bytes": html_path.stat().st_size,
        "file_type_ok": html_path.suffix.lower() in (".html", ".htm"),
        "encoding": None,
        "encoding_confidence": None,
        "decode_ok": False,
        "parse_errors": 0,
        "img_count": 0,
        "script_count": 0,
        "style_count": 0,
        "table_count": 0,
        "form_count": 0,
        "grade_suggestion": None,
        "risks": [],
        "content_check": None,  # M9 内容真身二次校验
        "ok": False,
    }

    if not result["file_type_ok"]:
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(f"文件类型非 HTML（{html_path.suffix or '无扩展名'}）——仅支持 .html/.htm")
        return result

    # M9 内容真身二次校验：魔数之外的轻量特征核验（防「扩展名对、内容不对」走错路径）
    content_check = verify_content_matches_extension(html_path)
    result["content_check"] = content_check
    if not content_check["match"]:
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(
            f"扩展名与内容不符（{content_check['evidence']}）——请确认文件为 HTML 文本内容")
        return result

    raw = html_path.read_bytes()
    if is_binary_sniff(raw):
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(
            "检测到二进制内容（NUL 字节或高比例控制字符）——疑似非文本文件，"
            "仅支持文本 HTML，请确认文件为 .html/.htm 文本格式"
        )
        return result

    enc = detect_encoding(raw)
    result["encoding"] = enc["encoding"]
    result["encoding_confidence"] = enc["confidence"]
    if enc["encoding"] is None:
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(
            "编码无法确定且候选解码全部失败——NEVER 猜测解码，请提供正确编码或先转码为 utf-8 后重试"
        )
        return result

    try:
        text = raw.decode(enc["encoding"])
        result["decode_ok"] = True
    except (UnicodeDecodeError, LookupError) as exc:
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(f"按 {enc['encoding']} 解码失败：{exc}——请提供正确编码")
        return result

    parser = PreflightParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        result["risks"].append(f"HTML 解析异常：{exc}")
    result["parse_errors"] = len(parser.errors)
    result["img_count"] = parser.img_count
    result["script_count"] = parser.script_count
    result["style_count"] = parser.style_count
    result["table_count"] = parser.table_count
    result["form_count"] = parser.form_count

    if result["parse_errors"] > 0:
        result["risks"].append(f"HTML 解析出现 {result['parse_errors']} 处错误——文档可能不合法，转换需抽查")

    # 等级建议
    tables_forms = result["table_count"] + result["form_count"]
    resources = result["img_count"] + result["script_count"] + result["style_count"]
    if tables_forms >= COMPLEX_TABLE_THRESHOLD or resources >= COMPLEX_RESOURCE_THRESHOLD \
            or result["size_bytes"] >= LARGE_FILE_BYTES:
        result["grade_suggestion"] = "L1"
        reasons = []
        if tables_forms >= COMPLEX_TABLE_THRESHOLD:
            reasons.append(f"表格/表单 {tables_forms} 处")
        if resources >= COMPLEX_RESOURCE_THRESHOLD:
            reasons.append(f"内嵌资源 {resources} 个")
        if result["size_bytes"] >= LARGE_FILE_BYTES:
            reasons.append(f"文件 {result['size_bytes'] / 1024 / 1024:.1f}MB")
        result["risks"].append(f"复杂 HTML 信号（{'、'.join(reasons)}）——建议标准档 L1")
    else:
        result["grade_suggestion"] = "L0"

    # 输入规模守卫（P2-2）：硬上限超限 → BLOCK；详见 result["scale_guard"]
    apply_scale_guard(result, html_path)

    result["ok"] = result["grade_suggestion"] != "BLOCK"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-html2md 门A 预检分级")
    ap.add_argument("--html", required=True, help="HTML 文件路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--pretty", action="store_true", help="输出人类可读摘要")
    args = ap.parse_args()

    html_path = Path(args.html)
    if not html_path.is_file():
        safe_print(json.dumps({"ok": False, "errors": [f"文件不存在：{html_path}"]}, ensure_ascii=False))
        return 2

    skip = check_unsupported(html_path)
    if skip is not None:
        if args.json or not args.pretty:
            safe_print(json.dumps(skip, ensure_ascii=False, indent=2))
        else:
            safe_print("状态：SKIP（无法转换，已跳过，未做任何转换尝试）")
            safe_print(f"原因：{skip['message']}")
            safe_print(f"本 skill 支持格式：{', '.join(skip['supported_formats'])}")
            safe_print(f"建议：{skip['suggestion']}")
        return 0

    result = run_preflight(html_path)
    if args.json or not args.pretty:
        safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        safe_print(f"文件：{result['file']}")
        safe_print(f"大小：{result['size_bytes']} 字节 ｜ 类型：{'OK' if result['file_type_ok'] else '非 HTML'}")
        safe_print(f"编码：{result['encoding']}（{result['encoding_confidence']}） ｜ 解码：{result['decode_ok']}")
        safe_print(f"解析错误：{result['parse_errors']} ｜ img/script/style："
              f"{result['img_count']}/{result['script_count']}/{result['style_count']}")
        safe_print(f"表格/表单：{result['table_count']}/{result['form_count']} ｜ 等级建议：{result['grade_suggestion']}")
        for r in result["risks"]:
            safe_print(f"  - 风险：{r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
