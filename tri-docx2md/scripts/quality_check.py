#!/usr/bin/env python3
"""门D · 质量校验与报告生成（tri-docx2md）

确定性计算：保真率（文本召回率）/ 丢失率 / 噪声率 / 结构对比（标题·表格·图片）/
异常清单 → 置信度 A/B/C → 生成 report.md
（报告 MUST 含保真率、丢失率等关键数据——用户硬要求，NEVER 省略）。

用法：
    python scripts/quality_check.py --doc a.docx --md a.md --report-dir <dir> \
        [--backend mammoth --grade L0 --elapsed 12.3 --assets-dir assets] --json

源文本提取：优先 python-docx → mammoth extract_raw_text → zipfile 解 word/document.xml 降级。
源文本不可提取（<50 字符）时召回率显式标注「不适用」，NEVER 编造数值。
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
SRC_TEXT_MIN_CHARS = 50        # 源文本总字符低于此值视为不可提取
_MD_IMG = re.compile(r"!\[[^\]]*\]\([^)]+\)|<img\s[^>]*>", re.IGNORECASE)
_MD_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_MD_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}.*\|", re.MULTILINE)
_MD_FENCE = re.compile(r"^```", re.MULTILINE)
_XML_TAG = re.compile(r"<[^>]+>")


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


def extract_source_text(doc_path: Path):
    """返回 (text, via)。优先 python-docx → mammoth → zipfile 降级。"""
    try:
        import docx  # python-docx
        d = docx.Document(str(doc_path))
        parts = [p.text for p in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                for cell in row.cells:
                    parts.append(cell.text)
        return "\n".join(parts), "python-docx"
    except ImportError:
        pass
    except Exception:
        pass
    try:
        import mammoth
        with open(str(doc_path), "rb") as f:
            r = mammoth.extract_raw_text(f)
        return r.value, "mammoth"
    except ImportError:
        pass
    except Exception:
        pass
    try:
        with zipfile.ZipFile(str(doc_path)) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        text = _XML_TAG.sub("", xml)
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        return text, "zipfile-xml"
    except Exception:
        return "", "none"


def count_source_structure(doc_path: Path) -> dict:
    """源侧结构计数（标题/表格/图片）。python-docx 优先，zipfile 降级。"""
    counts = {"src_headings": None, "src_tables": None, "src_images": None, "via": None}
    try:
        import docx  # python-docx
        d = docx.Document(str(doc_path))
        counts["src_headings"] = sum(
            1 for p in d.paragraphs
            if p.style and p.style.name and "Heading" in p.style.name
        )
        counts["src_tables"] = len(d.tables)
        counts["src_images"] = len(d.inline_shapes)
        counts["via"] = "python-docx"
        return counts
    except ImportError:
        pass
    except Exception:
        pass
    try:
        with zipfile.ZipFile(str(doc_path)) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        counts["src_headings"] = len(re.findall(r'<w:pStyle[^>]*w:val="Heading\d+"', xml))
        counts["src_tables"] = xml.count("<w:tbl>")
        counts["src_images"] = xml.count("<w:drawing>") + xml.count("<pic:pic>")
        counts["via"] = "zipfile-xml"
    except Exception:
        pass
    return counts


def count_source_omml(doc_path: Path):
    """M3 公式源侧计数：word/document.xml 的 <m:oMath 出现次数（zipfile 独立计数）。"""
    try:
        with zipfile.ZipFile(str(doc_path)) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        return xml.count("<m:oMath>")
    except Exception:
        return None


def compute_metrics(doc_path: Path, md_path: Path) -> dict:
    md_text = md_path.read_text(encoding="utf-8", errors="replace")
    src_text, src_via = extract_source_text(doc_path)
    src_norm = normalize(src_text)
    md_norm = normalize(md_text)

    m = {
        "doc_path": str(doc_path),
        "md_path": str(md_path),
        "src_total_chars": len(src_norm),
        "md_total_chars": len(md_norm),
        "src_extract_via": src_via,
        "has_text": len(src_norm) >= SRC_TEXT_MIN_CHARS,
        "recall": None,
        "loss_rate": None,
        "noise_rate": None,
    }

    # MD 侧结构计数
    md_counts = {
        "md_headings": len(_MD_HEADING.findall(md_text)),
        "md_tables": len(_MD_TABLE_SEP.findall(md_text)),
        "md_images": len(_MD_IMG.findall(md_text)),
    }
    m.update(md_counts)

    # P1-3 元素级计数指标（蒸馏报告 v1.3.0 元素×skill 矩阵 · docx2md 列）
    m["elem_formulas"] = len(re.findall(r"\$[^$\n]+\$|\$\$[^$]+\$\$", md_text))
    m["elem_footnotes"] = len(set(re.findall(r"\[\^\d+\]", md_text)))
    m["elem_anchor_refs"] = len(re.findall(r"\]\(#", md_text))
    m["elem_task_items"] = len(re.findall(r"^\s*[-*+] \[[xX ]\]", md_text, re.MULTILINE))
    m.update(count_source_structure(doc_path))
    m["src_omml"] = count_source_omml(doc_path)  # M3 源侧 OMML 公式计数

    if m["has_text"]:
        src_bg = bigrams(src_norm)
        md_bg = bigrams(md_norm)
        if src_bg:
            m["recall"] = round(len(src_bg & md_bg) / len(src_bg), 4)
            m["loss_rate"] = round(1.0 - m["recall"], 4)
        if md_bg:
            m["noise_rate"] = round(len(md_bg - src_bg) / len(md_bg), 4)

    # 异常清单
    anomalies = []
    n_replace = md_text.count("\ufffd")
    if n_replace:
        anomalies.append(f"检测到 {n_replace} 处乱码替换符（U+FFFD）——疑似编码问题")
    if len(md_norm.strip()) == 0:
        anomalies.append("MD 输出为空——转换失败")
    if m["has_text"] and m["md_total_chars"] < len(src_norm) * 0.3:
        anomalies.append("MD 内容量显著小于源文档（<30%）——疑似截断或漏段")
    if len(_MD_FENCE.findall(md_text)) % 2 != 0:
        anomalies.append("代码块围栏不成对——MD 语法破损")
    # M3 公式保真对比：源侧 OMML 有而 MD 侧无 LaTeX → 公式丢失信号
    if m.get("src_omml") and m["elem_formulas"] == 0:
        anomalies.append(
            f"源文档检出公式（{m['src_omml']} 处 OMML）而 MD 无 LaTeX 公式——疑似公式丢失"
            "（建议确认是否经过 repair_docx 预处理）")
    m["anomalies"] = anomalies
    return m


def grade_confidence(m: dict) -> dict:
    """置信度 A/B/C 判定（阈值唯一真源：references/fidelity-spec.md）。"""
    reasons = []
    if not m["has_text"]:
        return {"confidence": "C",
                "reasons": ["源文档文本提取不足（<50 字符）——文本召回率不适用，需人工复核"]}
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
    if m["src_tables"] and m["md_tables"] == 0:
        reasons.append(f"源文档检出表格（{m['src_tables']} 处）而 MD 无表格语法")
        conf = "C" if conf == "A" else conf
    if m["src_images"] and m["md_images"] == 0:
        reasons.append(f"源文档检出图片（{m['src_images']} 张）而 MD 无图片引用")
        if conf == "A":
            conf = "B"
    if m["anomalies"]:
        reasons.extend(m["anomalies"])
        conf = "C"
    if not reasons:
        reasons.append(f"保真率 {r:.1%} ≥ 95% 且结构计数吻合、无异常")
    return {"confidence": conf, "reasons": reasons}


def fmt_pct(v):
    return "不适用（源文本不可提取）" if v is None else f"{v:.1%}"


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
        "# Word → Markdown 转换质量报告",
        "",
        f"> 诚实声明：Word→MD 是「结构降维」（批注/修订/页眉页脚/嵌入对象必然丢失），本报告承诺「可验证的分级保真」而非绝对无损。",
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
        f"| 源文本提取方式 | {m['src_extract_via']} |",
        f"| 耗时 | {meta.get('elapsed') or 'unknown'}s |",
        f"| 图片资产 | {meta.get('assets') if meta.get('assets') is not None else m['md_images']} |",
        f"| 降级轨迹 | {meta.get('downgrades') or '无'} |",
        "",
        "## 置信度判定原因",
        "",
    ]
    lines += [f"- {r}" for r in g["reasons"]]
    lines += ["", "## 结构对比", "", "| 结构 | 源侧 | MD 侧 | 口径 |", "|---|---|---|---|",
              f"| 标题 | {m['src_headings'] if m['src_headings'] is not None else '未检测'} | {m['md_headings']} | 源侧为 python-docx/zipfile 计数 |",
              f"| 表格 | {m['src_tables'] if m['src_tables'] is not None else '未检测'} | {m['md_tables']} | 源侧为 python-docx/zipfile 计数 |",
              f"| 图片 | {m['src_images'] if m['src_images'] is not None else '未检测'} | {m['md_images']} | 源侧为 python-docx/zipfile 计数 |",
              f"| 公式 | {m['src_omml'] if m.get('src_omml') is not None else '未检测'} | {m['elem_formulas']} | 源侧为 OMML 计数，MD 侧为 $...$ 计数（M3） |"]
    lines += ["", "## 异常清单", ""]
    if m["anomalies"]:
        lines += [f"- {a}" for a in m["anomalies"]]
    else:
        lines += ["- 无"]
    lines += [
        "",
        "## 固定复核项（永不消失，即使 A 级）",
        "",
        "- [ ] 批注与修订丢失（Word 批注/修订痕迹在 MD 中必然不呈现）",
        "- [ ] 页眉页脚（页眉页脚内容可能被并入正文或丢失）",
        "- [ ] 嵌入对象（OLE 嵌入对象/图表仅保留占位或丢失）",
        "- [ ] 中文字体（字体嵌入缺失导致的字符/样式差异）",
        "- [ ] .doc 旧格式兼容（LibreOffice 中间转换的版式漂移）",
        "- [ ] 表格嵌套（嵌套表格在 MD 中可能被压平）",
        "",
        "## 复核结果回填（用户填写，反哺进化契约）",
        "",
        "- 实际丢失内容：",
        "- 复核结论（采信 / 需重转 / 需换档）：",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-docx2md 门D 质量校验与报告")
    ap.add_argument("--doc", required=True, help="输入 Word 文件路径（.docx/.docm/.doc）")
    ap.add_argument("--md", required=True, help="输出 Markdown 文件路径")
    ap.add_argument("--report-dir", default=None, help="report.md 输出目录（缺省为 MD 同目录）")
    ap.add_argument("--backend", default=None, help="转换后端名（写入报告元数据）")
    ap.add_argument("--grade", default=None, help="转换档位（写入报告元数据）")
    ap.add_argument("--elapsed", type=float, default=None, help="转换耗时秒数")
    ap.add_argument("--assets", type=int, default=None, help="图片资产文件数")
    ap.add_argument("--downgrades", default=None, help="降级轨迹描述，如 'pandoc→mammoth'")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc_path, md_path = Path(args.doc), Path(args.md)
    for p, label in ((doc_path, "Word"), (md_path, "MD")):
        if not p.is_file():
            safe_print(json.dumps({"ok": False, "errors": [f"{label} 文件不存在：{p}"]}, ensure_ascii=False))
            return 2

    t0 = time.time()
    m = compute_metrics(doc_path, md_path)
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
