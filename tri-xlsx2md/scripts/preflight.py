#!/usr/bin/env python3
"""门A · Excel 预检分级（tri-xlsx2md）

确定性预检：文件类型魔数判定（xlsx=PK zip 头 / xls=OLE 复合文档头 D0CF11E0）、
工作表数（zipfile 解 xl/workbook.xml 数 <sheet>）、单元格规模估算（行×列）、
加密检测（xlsx OOXML 加密标记 / xls BIFF FILEPASS）、旧格式标记（.xls）、
超大文件警告（>10MB 或 >100k 行）→ 等级建议 L0/L1 或 BLOCK。

用法：
    python scripts/preflight.py --xlsx <路径> --json
    python scripts/preflight.py --xlsx <路径> --pretty

退出码：0 正常出报告（含 BLOCK/SKIP 建议）；2 参数/文件错误。
"""
from _io_safe import safe_print
import argparse
import json
import re
import sys
import zipfile
import zlib
from pathlib import Path

from scale_guard import apply_scale_guard  # P2-2 输入规模守卫（anydoc limits.rs 口径）
from sniffer import verify_content_matches_extension  # M9 内容真身二次校验（家族同源副本）

XLSX_MAGIC = b"PK\x03\x04"          # OOXML zip 头
XLS_MAGIC = b"\xd0\xcf\x11\xe0"     # OLE 复合文档头（.xls 与加密 OOXML 共用）
SHEET_RE = re.compile(r"<sheet\b[^>]*>")
ROW_RE = re.compile(r"<row\b[^>]*>")
FORMULA_RE = re.compile(r"<f\b[^>]*>")
MERGECELL_RE = re.compile(r"<mergeCell\b[^>]*>")
COL_RE = re.compile(r'<c\b[^>]*r="([A-Z]+)\d+"')


def col_letters_to_index(letters: str) -> int:
    """列字母转列号：A=1, B=2, ..., Z=26, AA=27。"""
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n

BIG_SIZE_BYTES = 10 * 1024 * 1024   # >10MB 超大警告
BIG_ROW_COUNT = 100_000             # >100k 行超大警告


def read_magic(path: Path) -> bytes:
    with open(path, "rb") as fh:
        return fh.read(8)


def detect_type(path: Path, magic: bytes) -> str:
    """魔数判定：xlsx/xlsm/xlsb / xls / csv / unknown。WPS 生成的 .xlsx/.xls 同格式兼容（魔数一致）。
P1-5 判定路径明细：.xlsm 与 .xlsx 同为 OPC zip；.xlsb=ZIP 且含 xl/workbook.bin；
.csv=无魔数 → 扩展名 + 分隔符试验解析（P1-7）。"""
    if magic.startswith(XLSX_MAGIC):
        # P1-5：.xlsb = ZIP 容器且含 xl/workbook.bin；否则按 OPC（.xlsx/.xlsm）
        try:
            with zipfile.ZipFile(str(path)) as z:
                if "xl/workbook.bin" in z.namelist():
                    return "xlsb"
        except Exception:
            pass
        return "xlsx"
    if magic.startswith(XLS_MAGIC):
        return "xls"
    if not magic.startswith(XLSX_MAGIC) and not magic.startswith(XLS_MAGIC):
        # P1-5/P1-7：.csv 无魔数 → 扩展名 + 分隔符试验解析（probe_csv 内做一致性校验）
        if path.suffix.lower() == ".csv":
            return "csv"
    return "unknown"


def probe_xlsx(path: Path, result: dict) -> None:
    """zipfile 探测 xlsx：工作表数 / 行数估算 / 公式 / 合并单元格 / 加密标记。"""
    try:
        with zipfile.ZipFile(str(path)) as zf:
            names = set(zf.namelist())
            if "EncryptionInfo" in names:
                result["encrypted"] = True
                result["encryption_kind"] = "ooxml-agile"
                result["grade_suggestion"] = "BLOCK"
                result["risks"].append("xlsx 为 OOXML 加密（EncryptionInfo）——NEVER 破解，请合法解密后重试")
                return
            if "[Content_Types].xml" not in names:
                result["risks"].append("zip 内缺 [Content_Types].xml——疑似非标准 OOXML 或损坏文件")
                result["grade_suggestion"] = "BLOCK"
                return
            # 工作表数
            wb = zf.read("xl/workbook.xml").decode("utf-8", errors="replace")
            result["sheet_count"] = len(SHEET_RE.findall(wb))
            # 单元格规模估算 + 公式/合并单元格
            total_rows = 0
            max_cols = 0
            formula_cells = 0
            merged_cells = 0
            ws_names = [n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n)]
            for n in ws_names:
                xml = zf.read(n).decode("utf-8", errors="replace")
                total_rows += len(ROW_RE.findall(xml))
                formula_cells += len(FORMULA_RE.findall(xml))
                merged_cells += len(MERGECELL_RE.findall(xml))
                for col in COL_RE.findall(xml):
                    max_cols = max(max_cols, col_letters_to_index(col))
            result["estimated_rows"] = total_rows
            result["estimated_cols"] = max_cols
            result["formula_cells"] = formula_cells
            result["merged_cells"] = merged_cells
    except (zipfile.BadZipFile, zlib.error, OSError) as exc:
        result["risks"].append(f"zip 解析失败：{exc}")
        result["grade_suggestion"] = "BLOCK"


def probe_xls(path: Path, result: dict) -> None:
    """xlrd 探测 xls：工作表数 / 加密（FILEPASS）/ 规模。xlrd 不可用时降级标记。"""
    try:
        import xlrd  # noqa: F401
    except ImportError:
        result["risks"].append("本地无 xlrd，无法精确探测 .xls——请安装：pip install xlrd")
        result["grade_suggestion"] = "L1"
        return
    try:
        # xlrd compdoc 对畸形/截断 OLE 会 print WARNING 污染 --json 输出（批次二发现：
        # 截断 .xls 触发「preflight JSON 不可解析」）。compdoc 的 logfile 默认参数在
        # 导入时绑定原始 sys.stdout，redirect_stdout 换不掉 → 显式传 logfile 吞掉。
        import io as _io
        book = xlrd.open_workbook(str(path), on_demand=True, logfile=_io.StringIO())
        result["sheet_count"] = book.nsheets
        result["estimated_rows"] = None
        result["estimated_cols"] = None
        result["risks"].append(".xls 旧二进制格式（BIFF）——建议标准档 L1，需 xlrd/pandas/LibreOffice 链")
    except Exception as exc:
        msg = str(exc)
        if "encrypted" in msg.lower() or "password" in msg.lower():
            result["encrypted"] = True
            result["encryption_kind"] = "biff-filepass"
            result["grade_suggestion"] = "BLOCK"
            result["risks"].append(".xls 已加密（BIFF FILEPASS）——NEVER 破解，请合法解密后重试")
        else:
            result["risks"].append(f".xls 无法打开：{exc}")
            result["grade_suggestion"] = "BLOCK"


# ---- 家族统一五格式优雅跳过守卫（用户指令 2026-09-08）----
# tri-xx2md 家族统一不支持 .odt/.ods/.odp/.rtf/.epub 转换：命中 MUST 明确提示
# 无法转换并跳过，NEVER 强行转换，NEVER 报错中断（exit 0，status=SKIP）。
UNSUPPORTED_EXTENSIONS = {".odt", ".ods", ".odp", ".rtf", ".epub"}
RTF_MAGIC = b"{\\rtf"
SKIP_MIME_PREFIXES = (b"application/vnd.oasis.opendocument.", b"application/epub+zip")
SUPPORTED_EXTENSIONS = ['.xlsx', '.xlsm', '.xls', '.xlsb', '.csv']  # P1-1 矩阵 5 扩展名


CSV_DELIMS = (",", ";", "\t", "|")

# P1-7 CSV 场景专项：编码检测 BOM→UTF-16LE/BE→UTF-8→CP1252；分隔符试验解析（逗号/分号/制表/竖线计数取最大）
def detect_csv_encoding(path: Path) -> str:
    with open(path, "rb") as f:
        head = f.read(4)
    if head.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if head.startswith(b"\xff\xfe") or head.startswith(b"\xfe\xff"):
        return "utf-16"
    try:
        head.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "cp1252"


def probe_csv(path: Path, result: dict) -> None:
    """CSV 预检：分隔符判定 + 行列规模估算（等级固定 L0）。"""
    enc = detect_csv_encoding(path)
    kwargs = {"encoding": "utf-16" if enc == "utf-16" else ("cp1252" if enc == "cp1252" else "utf-8-sig" if enc == "utf-8-sig" else "utf-8")}
    if enc == "utf-8":
        kwargs["encoding"] = "utf-8"
    try:
        text = path.read_text(**kwargs)
    except (UnicodeDecodeError, OSError) as exc:
        result["risks"].append(f"CSV 读取失败（编码 {enc}）：{exc}")
        return
    lines = [ln for ln in text.splitlines() if ln.strip()]
    counts = {d: sum(1 for ln in lines[:50] if d in ln) for d in CSV_DELIMS}
    delim = max(counts, key=counts.get) if any(counts.values()) else ","
    result["csv_encoding"] = enc
    result["csv_delimiter"] = "\t" if delim == "\t" else delim
    result["estimated_rows"] = len(lines)
    result["estimated_cols"] = (max((ln.count(delim) + 1) for ln in lines[:50]) if lines and delim in "\n".join(lines[:50]) else 1)
    result["sheet_count"] = 1
    result["risks"].append(f"CSV（P1-7）：编码 {enc} / 分隔符 {'TAB' if delim == chr(9) else repr(delim)}——anydoc 直转（RFC 4180 保守解析）")


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


def run_preflight(path: Path) -> dict:
    result = {
        "file": str(path),
        "size_bytes": path.stat().st_size,
        "file_type": None,
        "sheet_count": None,
        "estimated_rows": None,
        "estimated_cols": None,
        "formula_cells": 0,
        "merged_cells": 0,
        "encrypted": False,
        "encryption_kind": None,
        "old_format": False,
        "oversized": False,
        "grade_suggestion": None,
        "risks": [],
        "content_check": None,  # M9 内容真身二次校验
        "ok": False,
    }

    # M9 内容真身二次校验：魔数之外的轻量特征核验（防「扩展名对、内容不对」走错路径）
    content_check = verify_content_matches_extension(path)
    result["content_check"] = content_check
    if not content_check["match"]:
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(
            f"扩展名与内容不符（{content_check['evidence']}）——请确认文件真实格式")
        return result

    magic = read_magic(path)
    ftype = detect_type(path, magic)
    result["file_type"] = ftype

    if ftype == "unknown":
        result["grade_suggestion"] = "BLOCK"
        result["risks"].append(f"无法识别的文件魔数（{magic[:4].hex()}）——非 .xlsx/.xls，请确认文件类型")
        return result

    if ftype == "xlsx":
        probe_xlsx(path, result)
    elif ftype == "xlsb":
        # .xlsb：二进制 workbook，zip 解析不适用——仅规模/等级判定（anydoc 直读，P1-5）
        result["risks"].append(".xlsb（BIFF12 二进制）——anydoc 直读首选；本地探测仅规模估计")
        result["grade_suggestion"] = "L0"
    elif ftype == "csv":
        probe_csv(path, result)
        result["grade_suggestion"] = "L0"
        apply_scale_guard(result, path)
        result["ok"] = True
        return result
    else:
        result["old_format"] = True
        probe_xls(path, result)

    if result["grade_suggestion"] == "BLOCK":
        result["ok"] = False
        return result

    # 超大警告
    if result["size_bytes"] > BIG_SIZE_BYTES:
        result["oversized"] = True
        result["risks"].append(f"超大文件（{result['size_bytes'] / 1024 / 1024:.1f}MB > 10MB）——建议标准档 L1")
    if (result["estimated_rows"] or 0) > BIG_ROW_COUNT:
        result["oversized"] = True
        result["risks"].append(f"超大表格（估算 {result['estimated_rows']} 行 > 100k 行）——建议标准档 L1，注意截断风险")

    # 等级建议
    if ftype == "xlsb":
        pass  # 已置 L0（anydoc 直读）
    elif ftype == "xls":
        result["grade_suggestion"] = "L1"
    elif result["formula_cells"] > 0 or result["merged_cells"] > 0 or result["oversized"]:
        result["grade_suggestion"] = "L1"
        if result["formula_cells"] > 0:
            result["risks"].append(f"检出 {result['formula_cells']} 个公式单元格——默认取缓存值，公式语义丢失（--evaluate 可求值）")
        if result["merged_cells"] > 0:
            result["risks"].append(f"检出 {result['merged_cells']} 处合并单元格——展开为左上角值 + 其余空")
    else:
        result["grade_suggestion"] = "L0"

    # 输入规模守卫（P2-2）：网格槽位超预算 → 固定走 L1 流式路径；硬上限超限 → BLOCK
    apply_scale_guard(result, path, force_grade_on_slots_over="L1")

    result["ok"] = result["grade_suggestion"] != "BLOCK"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-xlsx2md 门A 预检分级")
    ap.add_argument("--xlsx", required=True, help="Excel 文件路径（.xlsx/.xls，含 WPS 生成文件）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--pretty", action="store_true", help="输出人类可读摘要")
    args = ap.parse_args()

    path = Path(args.xlsx)
    if not path.is_file():
        safe_print(json.dumps({"ok": False, "errors": [f"文件不存在：{path}"]}, ensure_ascii=False))
        return 2

    skip = check_unsupported(path)
    if skip is not None:
        if args.json or not args.pretty:
            safe_print(json.dumps(skip, ensure_ascii=False, indent=2))
        else:
            safe_print("状态：SKIP（无法转换，已跳过，未做任何转换尝试）")
            safe_print(f"原因：{skip['message']}")
            safe_print(f"本 skill 支持格式：{', '.join(skip['supported_formats'])}")
            safe_print(f"建议：{skip['suggestion']}")
        return 0

    result = run_preflight(path)
    if args.json or not args.pretty:
        safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        safe_print(f"文件：{result['file']}")
        safe_print(f"类型：{result['file_type']} ｜ 工作表数：{result['sheet_count']} ｜ 加密：{result['encrypted']}")
        safe_print(f"估算规模：{result['estimated_rows']} 行 × {result['estimated_cols']} 列 ｜ 公式：{result['formula_cells']} ｜ 合并：{result['merged_cells']}")
        safe_print(f"等级建议：{result['grade_suggestion']}")
        for r in result["risks"]:
            safe_print(f"  - 风险：{r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
