#!/usr/bin/env python3
"""门D · 质量校验与报告生成（tri-xlsx2md）

确定性计算：单元格覆盖率（源非空单元格 vs MD 表格单元格）/ 工作表数对比
（源 vs MD `## <工作表名>` 块）/ 行数对比 / 异常清单 → 置信度 A/B/C → 生成 report.md
（报告 MUST 含单元格覆盖率、工作表数对比等关键数据——用户硬要求，NEVER 省略）。

用法：
    python scripts/quality_check.py --xlsx a.xlsx --md a.md --report-dir <dir> \
        [--backend openpyxl --grade L0 --elapsed 3.2] --json

源提取优先 openpyxl/xlrd；不可用时降级 zipfile 解 xl/worksheets/*.xml + sharedStrings 提取。
退出码：0 校验完成（置信度见输出）；2 参数错误。
"""
from _io_safe import safe_print
import argparse
import datetime as _dt
import json
import re
import sys
import time
import zipfile
from pathlib import Path

FIDELITY_A = 0.95
FIDELITY_B = 0.85
TRUNCATE_FLAG = 0.85          # MD 单元格数低于源非空单元格此比例 → 截断信号
_MD_SHEET = re.compile(r"^##\s+\S", re.MULTILINE)      # 任意工作表名块（`## <名称>`，非仅 Sheet 前缀）
_ASSET_HEAD = re.compile(r"^##\s*图片资产清单\s*$", re.MULTILINE)  # 资产清单段不算工作表
_MD_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}.*\|", re.MULTILINE)
_XLSX_MAGIC = b"PK\x03\x04"
_XLS_MAGIC = b"\xd0\xcf\x11\xe0"
_SHEET_RE = re.compile(r"<sheet\b[^>]*>")
_ROW_RE = re.compile(r"<row\b[^>]*>")
_CELL_BLOCK = re.compile(r"<c\b[^>]*>.*?</c>", re.DOTALL)


def detect_type(path: Path) -> str:
    with open(path, "rb") as fh:
        magic = fh.read(8)
    if magic.startswith(_XLSX_MAGIC):
        return "xlsx"
    if magic.startswith(_XLS_MAGIC):
        return "xls"
    return "unknown"


def extract_source(xlsx_path: Path) -> dict:
    """返回 (sheet_count, non_empty_cells, data_rows, source_kind)。"""
    ftype = detect_type(xlsx_path)
    out = {"file_type": ftype, "sheet_count": None, "non_empty_cells": None,
           "data_rows": None, "source_kind": None}
    if ftype == "xlsx":
        try:
            import openpyxl
            wb = openpyxl.load_workbook(str(xlsx_path), read_only=True, data_only=True)
            out["source_kind"] = "openpyxl"
            out["sheet_count"] = len(wb.sheetnames)
            non_empty, rows = 0, 0
            for ws in wb.worksheets:
                for row in ws.iter_rows():
                    vals = [c.value for c in row]
                    if any(v is not None for v in vals):
                        rows += 1
                        non_empty += sum(1 for v in vals if v is not None)
            out["non_empty_cells"] = non_empty
            out["data_rows"] = rows
            return out
        except ImportError:
            pass
        # 降级：zipfile 解 XML
        try:
            with zipfile.ZipFile(str(xlsx_path)) as zf:
                names = set(zf.namelist())
                wb_xml = zf.read("xl/workbook.xml").decode("utf-8", errors="replace")
                out["source_kind"] = "zipfile"
                out["sheet_count"] = len(_SHEET_RE.findall(wb_xml))
                non_empty, rows = 0, 0
                for n in names:
                    if re.match(r"xl/worksheets/sheet\d+\.xml$", n):
                        xml = zf.read(n).decode("utf-8", errors="replace")
                        rows += len(_ROW_RE.findall(xml))
                        non_empty += sum(
                            1 for m in _CELL_BLOCK.findall(xml) if "<v>" in m or "<is>" in m
                        )
                out["non_empty_cells"] = non_empty
                out["data_rows"] = rows
                return out
        except (zipfile.BadZipFile, KeyError):
            out["source_kind"] = "unavailable"
            return out
    else:
        try:
            import xlrd
            book = xlrd.open_workbook(str(xlsx_path), on_demand=True)
            out["source_kind"] = "xlrd"
            out["sheet_count"] = book.nsheets
            non_empty, rows = 0, 0
            for sh in book.sheets():
                for r in range(sh.nrows):
                    vals = sh.row_values(r)
                    if any(v not in (None, "") for v in vals):
                        rows += 1
                        non_empty += sum(1 for v in vals if v not in (None, ""))
            out["non_empty_cells"] = non_empty
            out["data_rows"] = rows
            return out
        except ImportError:
            out["source_kind"] = "unavailable"
            return out
        except Exception as exc:
            out["source_kind"] = "error"
            out["error"] = str(exc)
            return out


def parse_md(md_text: str) -> dict:
    md_sheets = max(0, len(_MD_SHEET.findall(md_text)) - len(_ASSET_HEAD.findall(md_text)))
    md_cells = 0
    md_data_rows = 0
    for line in md_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        if _MD_TABLE_SEP.match(s):
            continue
        parts = s.strip("|").split("|")
        md_cells += len(parts)
        md_data_rows += 1
    return {"md_sheets": md_sheets, "md_cells": md_cells, "md_data_rows": md_data_rows}


def compute_metrics(xlsx_path: Path, md_path: Path) -> dict:
    md_text = md_path.read_text(encoding="utf-8-sig", errors="replace")
    src = extract_source(xlsx_path)
    md = parse_md(md_text)

    m = {
        "xlsx_path": str(xlsx_path),
        "md_path": str(md_path),
        "file_type": src["file_type"],
        "source_kind": src["source_kind"],
        "source_sheets": src["sheet_count"],
        "source_non_empty_cells": src["non_empty_cells"],
        "source_data_rows": src["data_rows"],
        "md_sheets": md["md_sheets"],
        "md_cells": md["md_cells"],
        "md_data_rows": md["md_data_rows"],
        "cell_coverage": None,
        "sheet_match": None,
        "anomalies": [],
    }

    non_empty = src["non_empty_cells"]
    if non_empty is None:
        m["anomalies"].append("源单元格数无法提取（后端不可用且非 zip 可解）——覆盖率不适用")
    elif non_empty == 0:
        m["cell_coverage"] = 1.0
        m["anomalies"].append("源文件无非空单元格（空表）——覆盖率按 1.0 计，MD 为空属正常")
    else:
        m["cell_coverage"] = round(min(md["md_cells"], non_empty) / non_empty, 4)

    if src["sheet_count"] is not None:
        m["sheet_match"] = m["md_sheets"] == src["sheet_count"]
        if m["md_sheets"] < src["sheet_count"]:
            m["anomalies"].append(
                f"工作表缺失：源 {src['sheet_count']} 个 vs MD {m['md_sheets']} 个 `## <工作表名>` 块"
            )
        elif m["md_sheets"] > src["sheet_count"]:
            m["anomalies"].append(
                f"MD 工作表数多于源（{m['md_sheets']} > {src['sheet_count']}）——疑似幻影块"
            )

    # 异常清单
    n_replace = md_text.count("\ufffd")
    if n_replace:
        m["anomalies"].append(f"检测到 {n_replace} 处乱码替换符（U+FFFD）——疑似编码问题")
    if len(md_text.strip()) == 0:
        m["anomalies"].append("MD 输出为空——转换失败")
    if non_empty and md["md_cells"] < non_empty * TRUNCATE_FLAG:
        m["anomalies"].append(
            f"MD 单元格数（{md['md_cells']}）显著小于源非空单元格（{non_empty}）——疑似截断"
        )
    return m


def grade_confidence(m: dict) -> dict:
    """置信度 A/B/C 判定（阈值唯一真源：references/fidelity-spec.md）。"""
    reasons = []
    cov = m["cell_coverage"]
    if cov is None:
        return {"confidence": "C", "reasons": ["单元格覆盖率无法计算"]}
    if cov < FIDELITY_B:
        reasons.append(f"单元格覆盖率 {cov:.1%} < 85%")
        conf = "C"
    elif cov < FIDELITY_A:
        reasons.append(f"单元格覆盖率 {cov:.1%} 处于 85–95% 区间")
        conf = "B"
    else:
        conf = "A"
    if m["sheet_match"] is False:
        reasons.append(f"工作表数不吻合（源 {m['source_sheets']} vs MD {m['md_sheets']}）")
        conf = "C" if conf == "A" else conf
    if m["anomalies"]:
        reasons.extend(m["anomalies"])
        conf = "C"
    if not reasons:
        reasons.append(f"单元格覆盖率 {cov:.1%} ≥ 95% 且工作表数吻合、无异常")
    return {"confidence": conf, "reasons": reasons}


def fmt_pct(v):
    return "不适用" if v is None else f"{v:.1%}"


def build_report(m: dict, g: dict, meta: dict) -> str:
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "---",
        f"generated_at: {now}",
        f"backend: {meta.get('backend') or 'unknown'}",
        f"grade: {meta.get('grade') or 'unknown'}",
        f"confidence: {g['confidence']}",
        "---",
        "",
        "# Excel → Markdown 转换质量报告",
        "",
        "> 诚实声明：Excel→MD 是结构降维而非格式复制，本报告承诺「可验证的分级保真」而非绝对无损。",
        "",
        "## 关键数据（必读）",
        "",
        "| 关键数据 | 数值 |",
        "|---|---|",
        f"| **单元格覆盖率** | **{fmt_pct(m['cell_coverage'])}** |",
        f"| **工作表数对比** | 源 {m['source_sheets']} 个 vs MD {m['md_sheets']} 个 `## <工作表名>` 块（{'吻合' if m['sheet_match'] else '不吻合'}） |",
        f"| 行数对比 | 源 {m['source_data_rows']} 行 vs MD {m['md_data_rows']} 行 |",
        f"| 置信度等级 | **{g['confidence']}**（{'直接可用' if g['confidence'] == 'A' else '抽查复核' if g['confidence'] == 'B' else '强制人工复核'}） |",
        f"| 转换后端 / 档位 | {meta.get('backend') or 'unknown'} / {meta.get('grade') or 'unknown'} |",
        f"| 文件类型 / 源提取 | {m['file_type']} / {m['source_kind']} |",
        f"| 耗时 | {meta.get('elapsed') or 'unknown'}s |",
        f"| 降级轨迹 | {meta.get('downgrades') or '无'} |",
        "",
        "## 置信度判定原因",
        "",
    ]
    lines += [f"- {r}" for r in g["reasons"]]
    lines += ["", "## 异常清单", ""]
    if m["anomalies"]:
        lines += [f"- {a}" for a in m["anomalies"]]
    else:
        lines += ["- 无"]
    lines += [
        "",
        "## 固定复核项（永不消失，即使 A 级）",
        "",
        "- [ ] 合并单元格（展开为左上角值 + 其余空，复核展开是否正确）",
        "- [ ] 公式 vs 值（默认取缓存值，公式语义丢失；复核缓存值是否为最终值）",
        "- [ ] 多行表头（表头跨多行时 MD 表头仅取首行，复核表头完整性）",
        "- [ ] .xls 旧格式兼容（BIFF 解析差异，复核单元格内容）",
        "- [ ] 超大数据集截断（>100k 行时 MD 可能截断，复核行数）",
        "- [ ] 日期/数字格式（Excel 日期序列号 vs 显示格式，复核格式语义）",
        "",
        "## 复核结果回填（用户填写，反哺进化契约）",
        "",
        "- 实际丢失内容：",
        "- 复核结论（采信 / 需重转 / 需换档）：",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-xlsx2md 门D 质量校验与报告")
    ap.add_argument("--xlsx", required=True, help="输入 Excel 文件路径（.xlsx/.xls）")
    ap.add_argument("--md", required=True, help="输出 Markdown 文件路径")
    ap.add_argument("--report-dir", default=None, help="report.md 输出目录（缺省为 MD 同目录）")
    ap.add_argument("--backend", default=None, help="转换后端名（写入报告元数据）")
    ap.add_argument("--grade", default=None, help="转换档位（写入报告元数据）")
    ap.add_argument("--elapsed", type=float, default=None, help="转换耗时秒数")
    ap.add_argument("--downgrades", default=None, help="降级轨迹描述，如 'pandas→openpyxl'")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    xlsx_path, md_path = Path(args.xlsx), Path(args.md)
    for p, label in ((xlsx_path, "Excel"), (md_path, "MD")):
        if not p.is_file():
            safe_print(json.dumps({"ok": False, "errors": [f"{label} 文件不存在：{p}"]}, ensure_ascii=False))
            return 2

    t0 = time.time()
    m = compute_metrics(xlsx_path, md_path)
    g = grade_confidence(m)
    meta = {"backend": args.backend, "grade": args.grade, "elapsed": args.elapsed,
            "downgrades": args.downgrades, "check_elapsed": round(time.time() - t0, 2)}
    report = build_report(m, g, meta)

    report_dir = Path(args.report_dir) if args.report_dir else md_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")

    payload = {"ok": True, "metrics": m, "grading": g, "meta": meta, "report_path": str(report_path)}
    if args.json:
        safe_print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        safe_print(f"单元格覆盖率：{fmt_pct(m['cell_coverage'])} ｜ 工作表数：源 {m['source_sheets']} vs MD {m['md_sheets']} ｜ 置信度：{g['confidence']}")
        safe_print(f"报告：{report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
