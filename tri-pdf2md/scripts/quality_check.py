#!/usr/bin/env python3
"""门D · 质量校验与报告生成（tri-pdf2md）

确定性计算：保真率（文本召回率）/ 丢失率 / 噪声率 / 分页丢失明细 /
结构对比（标题·表格·图片）/ 异常清单 → 置信度 A/B/C → 生成 report.md
（报告 MUST 含保真率、丢失率等关键数据——用户硬要求，NEVER 省略）。

用法：
    python scripts/quality_check.py --pdf a.pdf --md a.md --report-dir <dir> \
        [--backend pymupdf4llm --grade L0 --elapsed 12.3 --assets-dir assets] --json

扫描件（无文本层）召回率不可计算时显式标注「不适用」，NEVER 编造数值。
退出码：0 校验完成（置信度见输出）；2 参数错误。
"""
from _io_safe import safe_print
import argparse
import datetime as _dt
import json
import re
import sys
import time
from pathlib import Path

FIDELITY_A = 0.95
FIDELITY_B = 0.85
LOSS_PAGE_FLAG = 0.80          # 单页召回低于此值计入「丢失集中页」
PDF_TEXT_MIN_CHARS = 50        # PDF 文本层总字符低于此值视为无文本层（扫描件）
_MD_IMG = re.compile(r"!\[[^\]]*\]\([^)]+\)|<img\s[^>]*>", re.IGNORECASE)
_MD_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_MD_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}.*\|", re.MULTILINE)
_MD_FENCE = re.compile(r"^```", re.MULTILINE)


def normalize(text: str) -> str:
    """保留字母/数字/CJK/CJK标点，小写化——跨格式公平比较的最小归一化。"""
    out = []
    for ch in text:
        o = ord(ch)
        if 0x30 <= o <= 0x39 or 0x41 <= o <= 0x5A or 0x61 <= o <= 0x7A:
            out.append(ch.lower())
        elif 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF:
            out.append(ch)
    return "".join(out)


def bigrams(s: str) -> set:
    if len(s) < 2:
        return {s} if s else set()
    return {s[i:i + 2] for i in range(len(s) - 1)}


def extract_pdf_pages(pdf_path: Path):
    """返回每页文本列表。优先 pypdf，回退 pdfplumber。"""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                pass
        return [(p.extract_text() or "") for p in reader.pages]
    except ImportError:
        pass
    import pdfplumber
    with pdfplumber.open(str(pdf_path)) as pdf:
        return [(p.extract_text() or "") for p in pdf.pages]


def count_pdf_structure(pdf_path: Path, max_pages: int = 40) -> dict:
    """PDF 侧结构计数（表格/图片）——pdfplumber 可用时统计抽样页。"""
    counts = {"pdf_tables": None, "pdf_images": None, "sampled": 0}
    try:
        import pdfplumber
    except ImportError:
        return counts
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            pages = pdf.pages
            step = max(1, len(pages) // max_pages)
            sample = pages[::step][:max_pages]
            counts["sampled"] = len(sample)
            counts["pdf_tables"] = sum(len(p.find_tables()) for p in sample)
            counts["pdf_images"] = sum(len(p.images) for p in sample)
    except Exception:
        pass
    return counts


def compute_metrics(pdf_path: Path, md_path: Path) -> dict:
    md_text = md_path.read_text(encoding="utf-8", errors="replace")
    pages = extract_pdf_pages(pdf_path)
    page_norms = [normalize(t) for t in pages]
    pdf_all = "".join(page_norms)
    md_norm = normalize(md_text)

    m = {
        "pdf_path": str(pdf_path),
        "md_path": str(md_path),
        "page_count": len(pages),
        "pdf_total_chars": len(pdf_all),
        "md_total_chars": len(md_norm),
        "has_text_layer": len(pdf_all) >= PDF_TEXT_MIN_CHARS,
        "recall": None,
        "loss_rate": None,
        "noise_rate": None,
        "page_recall": [],
        "loss_pages": [],
    }

    # MD 侧结构计数
    md_counts = {
        "md_headings": len(_MD_HEADING.findall(md_text)),
        "md_tables": len(_MD_TABLE_SEP.findall(md_text)),
        "md_images": len(_MD_IMG.findall(md_text)),
    }
    m.update(md_counts)
    m.update(count_pdf_structure(pdf_path))

    if m["has_text_layer"]:
        pdf_bg = bigrams(pdf_all)
        md_bg = bigrams(md_norm)
        if pdf_bg:
            m["recall"] = round(len(pdf_bg & md_bg) / len(pdf_bg), 4)
            m["loss_rate"] = round(1.0 - m["recall"], 4)
        if md_bg:
            m["noise_rate"] = round(len(md_bg - pdf_bg) / len(md_bg), 4)
        for i, pn in enumerate(page_norms):
            if not pn:
                continue
            pbg = bigrams(pn)
            r = round(len(pbg & md_bg) / len(pbg), 4) if pbg else None
            m["page_recall"].append({"page": i + 1, "recall": r})
            if r is not None and r < LOSS_PAGE_FLAG:
                m["loss_pages"].append({"page": i + 1, "recall": r})

    # 异常清单
    anomalies = []
    n_replace = md_text.count("\ufffd")
    if n_replace:
        anomalies.append(f"检测到 {n_replace} 处乱码替换符（U+FFFD）——疑似编码/OCR 问题")
    if len(md_norm.strip()) == 0:
        anomalies.append("MD 输出为空——转换失败")
    if m["has_text_layer"] and m["md_total_chars"] < len(pdf_all) * 0.3:
        anomalies.append("MD 内容量显著小于 PDF 文本层（<30%）——疑似截断或漏页")
    if len(_MD_FENCE.findall(md_text)) % 2 != 0:
        anomalies.append("代码块围栏不成对——MD 语法破损")
    m["anomalies"] = anomalies
    return m


def grade_confidence(m: dict) -> dict:
    """置信度 A/B/C 判定（阈值唯一真源：references/fidelity-spec.md）。"""
    reasons = []
    if not m["has_text_layer"]:
        return {"confidence": "C",
                "reasons": ["无文本层（扫描件）——文本召回率不适用，OCR 质量 C 级口径"]}
    r = m["recall"]
    if r is None:
        return {"confidence": "C", "reasons": ["召回率无法计算"]}
    if r < FIDELITY_B:
        reasons.append(f"保真率 {r:.1%} < 85%")
        conf = "C"
    elif r < FIDELITY_A:
        reasons.append(f"保真率 {r:.1%} 处于 85–95% 区间")
        conf = "B"
    else:
        conf = "A"
    if m["pdf_tables"] and m["md_tables"] == 0:
        reasons.append(f"PDF 检出表格（抽样 {m['pdf_tables']} 处）而 MD 无表格语法")
        conf = "C" if conf == "A" else conf
    if m["pdf_images"] and m["md_images"] == 0:
        reasons.append(f"PDF 检出图片（抽样 {m['pdf_images']} 张）而 MD 无图片引用")
        if conf == "A":
            conf = "B"
    if m["anomalies"]:
        reasons.extend(m["anomalies"])
        conf = "C"
    if not reasons:
        reasons.append(f"保真率 {r:.1%} ≥ 95% 且结构计数吻合、无异常")
    return {"confidence": conf, "reasons": reasons}


def fmt_pct(v):
    return "不适用（无文本层）" if v is None else f"{v:.1%}"


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
        f"# PDF → Markdown 转换质量报告",
        "",
        f"> 诚实声明：PDF→MD 是推断重建而非格式复制，本报告承诺「可验证的分级保真」而非绝对无损。",
        "",
        "## 关键数据（必读）",
        "",
        "| 关键数据 | 数值 |",
        "|---|---|",
        f"| **保真率（文本召回率）** | **{fmt_pct(m['recall'])}** |",
        f"| **丢失率** | **{fmt_pct(m['loss_rate'])}** |",
        f"| 噪声率（MD 冗余内容占比） | {fmt_pct(m['noise_rate'])} |",
        f"| 置信度等级 | **{g['confidence']}**（{'直接可用' if g['confidence'] == 'A' else '抽查复核' if g['confidence'] == 'B' else '强制人工复核'}） |",
        f"| 转换后端 / 档位 | {meta.get('backend') or 'unknown'} / {meta.get('grade') or 'unknown'} |",
        f"| 页数 / 耗时 | {m['page_count']} 页 / {meta.get('elapsed') or 'unknown'}s |",
        f"| 图片资产 | {meta.get('assets') if meta.get('assets') is not None else m['md_images']} |",
        f"| 降级轨迹 | {meta.get('downgrades') or '无'} |",
        "",
        "## 置信度判定原因",
        "",
    ]
    lines += [f"- {r}" for r in g["reasons"]]
    lines += ["", "## 结构对比", "", "| 结构 | PDF 侧（抽样） | MD 侧 | 口径 |", "|---|---|---|---|",
              f"| 标题 | — | {m['md_headings']} | PDF 侧标题需版面语义，无法精确计数 |",
              f"| 表格 | {m['pdf_tables'] if m['pdf_tables'] is not None else '未检测'} | {m['md_tables']} | PDF 侧为 pdfplumber 抽样计数 |",
              f"| 图片 | {m['pdf_images'] if m['pdf_images'] is not None else '未检测'} | {m['md_images']} | PDF 侧为抽样计数 |"]
    if m["page_recall"]:
        lines += ["", "## 分页保真明细", "", "| 页 | 召回率 |", "|---|---|"]
        lines += [f"| {p['page']} | {p['recall']:.1%} |" for p in m["page_recall"] if p["recall"] is not None]
    if m["loss_pages"]:
        lines += ["", "## 丢失集中页（召回 <80%，优先人工复核）", ""]
        lines += [f"- 第 {p['page']} 页（召回 {p['recall']:.1%}）" for p in m["loss_pages"]]
    lines += ["", "## 异常清单", ""]
    if m["anomalies"]:
        lines += [f"- {a}" for a in m["anomalies"]]
    else:
        lines += ["- 无"]
    lines += [
        "",
        "## 固定复核项（永不消失，即使 A 级）",
        "",
        "- [ ] 跨页表格完整性（PDF 分页可能截断同一表格）",
        "- [ ] 图表题注与图片对应关系",
        "- [ ] 脚注归属（脚注可能被并入正文）",
        "- [ ] 多栏阅读顺序（双栏 PDF 的段落衔接）",
        "- [ ] 中文字体嵌入缺失导致的字符缺失",
        "",
        "## 复核结果回填（用户填写，反哺进化契约）",
        "",
        "- 实际丢失内容：",
        "- 复核结论（采信 / 需重转 / 需换档）：",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-pdf2md 门D 质量校验与报告")
    ap.add_argument("--pdf", required=True, help="输入 PDF 文件路径")
    ap.add_argument("--md", required=True, help="输出 Markdown 文件路径")
    ap.add_argument("--report-dir", default=None, help="report.md 输出目录（缺省为 MD 同目录）")
    ap.add_argument("--backend", default=None, help="转换后端名（写入报告元数据）")
    ap.add_argument("--grade", default=None, help="转换档位（写入报告元数据）")
    ap.add_argument("--elapsed", type=float, default=None, help="转换耗时秒数")
    ap.add_argument("--assets", type=int, default=None, help="图片资产文件数")
    ap.add_argument("--downgrades", default=None, help="降级轨迹描述，如 'mineru→docling'")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    pdf_path, md_path = Path(args.pdf), Path(args.md)
    for p, label in ((pdf_path, "PDF"), (md_path, "MD")):
        if not p.is_file():
            safe_print(json.dumps({"ok": False, "errors": [f"{label} 文件不存在：{p}"]}, ensure_ascii=False))
            return 2

    t0 = time.time()
    m = compute_metrics(pdf_path, md_path)
    g = grade_confidence(m)
    meta = {"backend": args.backend, "grade": args.grade, "elapsed": args.elapsed,
            "assets": args.assets, "downgrades": args.downgrades,
            "check_elapsed": round(time.time() - t0, 2)}
    report = build_report(m, g, meta)

    report_dir = Path(args.report_dir) if args.report_dir else md_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")

    payload = {"ok": True, "metrics": m, "grading": g, "meta": meta, "report_path": str(report_path)}
    if args.json:
        safe_print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        safe_print(f"保真率：{fmt_pct(m['recall'])} ｜ 丢失率：{fmt_pct(m['loss_rate'])} ｜ 置信度：{g['confidence']}")
        safe_print(f"报告：{report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
