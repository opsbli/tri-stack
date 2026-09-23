#!/usr/bin/env python3
"""门D · 质量校验与报告生成（tri-pptx2md）

确定性计算：页覆盖率（源 slide 数 vs MD `## Slide` 块数）/ 文本召回率（保真率）/
丢失率 / 缺页明细 / 结构对比（每页文本·图片·备注）/ 异常清单 → 置信度 A/B/C →
生成 report.md（报告 MUST 含页覆盖率、文本召回率等关键数据——用户硬要求，NEVER 省略）。

源文本提取：优先 python-pptx（逐页 shape 文本/图片/备注），不可用时降级
zipfile 解 ppt/slides/*.xml（正则提取 <a:t> 文本、<a:blip> 图片、notesSlides 备注）。

用法：
    python scripts/quality_check.py --ppt a.pptx --md a.md --report-dir <dir> \
        [--backend python-pptx --grade L0 --elapsed 3.2 --assets-dir assets] --json

纯图片 PPT（源文本为空）文本召回率显式标注「不适用」，NEVER 编造数值。
退出码：0 校验完成（置信度见输出）；2 参数错误。
"""
from _io_safe import safe_print
import argparse
import datetime as _dt
import json
import re
import sys
import time
import unicodedata
import zipfile
from pathlib import Path

FIDELITY_A = 0.95
FIDELITY_B = 0.85
PAGE_COVERAGE_A = 1.00          # A 级要求页覆盖 100%
PAGE_COVERAGE_B = 0.90          # B 级要求页覆盖 ≥90%
SOURCE_TEXT_MIN_CHARS = 1       # 源文本总字符低于此值视为无文本（纯图片 PPT）
_MD_IMG = re.compile(r"!\[[^\]]*\]\([^)]+\)|<img\s[^>]*>", re.IGNORECASE)
_MD_SLIDE = re.compile(r"^##\s+Slide\s+(\d+)", re.MULTILINE)
_MD_FENCE = re.compile(r"^```", re.MULTILINE)
_XML_TEXT = re.compile(r"<a:t>(.*?)</a:t>", re.DOTALL)
_XML_BLIP = re.compile(r"<a:blip\b[^>]*r:embed=", re.IGNORECASE)


def normalize(text: str) -> str:
    """保留字母（小写化）/数字/CJK 汉字，其余剔除——跨格式公平比较的最小归一化。

    v1.4.4 起先做 NFKC 折叠：全角字母数字（２０２６ / ＡＢＣ）与兼容字符归一到半角后再
    参与统计。否则源侧全角被剔除、MD 侧半角被计数，同一语义内容两侧口径不一致
    （表现：全角数字整段丢失而召回率不变）。
    """
    out = []
    for ch in unicodedata.normalize("NFKC", text):
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


def _shape_text(shape) -> str:
    """递归提取 shape 内全部文本。"""
    parts = []
    if shape.has_text_frame:
        parts.append(shape.text_frame.text or "")
    if shape.shape_type == 13:  # PICTURE
        return "".join(parts)
    if getattr(shape, "shapes", None) is not None:
        for child in shape.shapes:
            parts.append(_shape_text(child))
    return "".join(parts)


def extract_with_pptx(ppt_path: Path) -> dict:
    """python-pptx 提取：每页文本/图片数/备注。"""
    from pptx import Presentation
    prs = Presentation(str(ppt_path))
    slides = []
    total_images = 0
    total_notes = 0
    for slide in prs.slides:
        texts = []
        images = 0
        for shape in slide.shapes:
            if shape.shape_type == 13:  # PICTURE
                images += 1
            texts.append(_shape_text(shape))
        has_notes = False
        if slide.has_notes_slide:
            notes_text = slide.notes_slide.notes_text_frame.text or ""
            if notes_text.strip():
                has_notes = True
                total_notes += 1
        slides.append({"text": "".join(texts), "images": images, "has_notes": has_notes})
        total_images += images
    return {"slide_count": len(slides), "slides": slides,
            "total_images": total_images, "total_notes": total_notes, "via": "python-pptx"}


def extract_with_zip(ppt_path: Path) -> dict:
    """zipfile 降级提取：解 ppt/slides/*.xml 正则抽文本/图片，notesSlides 判备注。"""
    slides = []
    total_images = 0
    total_notes = 0
    with zipfile.ZipFile(ppt_path) as z:
        names = z.namelist()
        slide_names = sorted(
            [n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml")],
            key=lambda n: int(re.search(r"slide(\d+)\.xml", n).group(1)))
        notes_names = {n for n in names if n.startswith("ppt/notesSlides/notesSlide")}
        for sn in slide_names:
            xml = z.read(sn).decode("utf-8", errors="replace")
            text = "".join(_XML_TEXT.findall(xml))
            images = len(_XML_BLIP.findall(xml))
            m = re.search(r"slide(\d+)\.xml", sn)
            has_notes = f"ppt/notesSlides/notesSlide{m.group(1)}.xml" in notes_names
            slides.append({"text": text, "images": images, "has_notes": has_notes})
            total_images += images
            if has_notes:
                total_notes += 1
    return {"slide_count": len(slides), "slides": slides,
            "total_images": total_images, "total_notes": total_notes, "via": "zipfile"}


def extract_source(ppt_path: Path) -> dict:
    """优先 python-pptx，回退 zipfile。"""
    try:
        return extract_with_pptx(ppt_path)
    except ImportError:
        pass
    except Exception:
        pass
    return extract_with_zip(ppt_path)


def count_md_structure(md_text: str) -> dict:
    slide_blocks = {}
    for m in _MD_SLIDE.finditer(md_text):
        slide_blocks[int(m.group(1))] = m.start()
    return {
        "md_slide_blocks": len(slide_blocks),
        "md_slide_numbers": sorted(slide_blocks.keys()),
        "md_images": len(_MD_IMG.findall(md_text)),
        "md_notes": len(re.findall(r"^>\s*备注", md_text, re.MULTILINE)),
    }


def compute_metrics(ppt_path: Path, md_path: Path) -> dict:
    md_text = md_path.read_text(encoding="utf-8", errors="replace")
    src = extract_source(ppt_path)
    md_struct = count_md_structure(md_text)

    md_norm = normalize(md_text)
    # 按页归一化后拼接（与逐页 bigram 口径一致；NFKC 后与整体归一化等价）
    source_norm = "".join(normalize(s["text"]) for s in src["slides"])

    m = {
        "ppt_path": str(ppt_path),
        "md_path": str(md_path),
        "extract_via": src["via"],
        "slide_count": src["slide_count"],
        "md_slide_blocks": md_struct["md_slide_blocks"],
        "page_coverage": None,
        "source_total_chars": len(source_norm),
        "md_total_chars": len(md_norm),
        "has_text": len(source_norm) >= SOURCE_TEXT_MIN_CHARS,
        "recall": None,
        "loss_rate": None,
        "missing_pages": [],
        "md_extra_blocks": 0,
        "structure": {
            "ppt_images": src["total_images"],
            "ppt_notes": src["total_notes"],
            "md_images": md_struct["md_images"],
            "md_notes": md_struct["md_notes"],
        },
    }

    # 页覆盖率
    if src["slide_count"]:
        m["page_coverage"] = round(
            min(md_struct["md_slide_blocks"], src["slide_count"]) / src["slide_count"], 4)
        present = set(md_struct["md_slide_numbers"])
        m["missing_pages"] = [i + 1 for i in range(src["slide_count"]) if (i + 1) not in present]
        # 多写的 Slide 块：页覆盖率用 min() 截断到 100%，多出的块不会体现在覆盖率里，
        # 需在异常清单单独暴露（v1.4.4）
        m["md_extra_blocks"] = max(0, md_struct["md_slide_blocks"] - src["slide_count"])

    # 文本召回率：源侧**逐页**切 bigram 再求并集，NEVER 把所有页拼成一个串再切——
    # 跨页边界不是真实邻接，拼接会凭空造出源侧存在、MD 侧永远匹配不到的伪 bigram，
    # 使完美转换也拿不到 100%（v1.4.4）
    if m["has_text"]:
        src_bg = set()
        for s in src["slides"]:
            src_bg |= bigrams(normalize(s["text"]))
        md_bg = bigrams(md_norm)
        if src_bg:
            m["recall"] = round(len(src_bg & md_bg) / len(src_bg), 4)
            m["loss_rate"] = round(1.0 - m["recall"], 4)

    # 异常清单
    anomalies = []
    n_replace = md_text.count("\ufffd")
    if n_replace:
        anomalies.append(f"检测到 {n_replace} 处乱码替换符（U+FFFD）——疑似编码问题")
    if len(md_norm.strip()) == 0:
        anomalies.append("MD 输出为空——转换失败")
    if m["missing_pages"]:
        anomalies.append(f"缺页：源有而 MD 无的 Slide {m['missing_pages']}")
    if m["md_extra_blocks"]:
        anomalies.append(f"MD Slide 块 {md_struct['md_slide_blocks']} 个，超过源 {src['slide_count']} 页"
                         f"（多出 {m['md_extra_blocks']} 个无对应页的块）")
    if len(_MD_FENCE.findall(md_text)) % 2 != 0:
        anomalies.append("代码块围栏不成对——MD 语法破损")
    m["anomalies"] = anomalies
    return m


def grade_confidence(m: dict) -> dict:
    """置信度 A/B/C 判定（阈值唯一真源：references/fidelity-spec.md）。"""
    reasons = []
    pc = m["page_coverage"]
    r = m["recall"]

    if not m["has_text"]:
        reasons.append("源文本为空（纯图片 PPT）——文本召回率不适用，按页覆盖率判定")
        if pc is not None and pc >= PAGE_COVERAGE_A:
            conf = "A"
        elif pc is not None and pc >= PAGE_COVERAGE_B:
            conf = "B"
        else:
            conf = "C"
        if m["anomalies"]:
            reasons.extend(m["anomalies"])
            conf = "C"
        return {"confidence": conf, "reasons": reasons}

    if pc is None or r is None:
        return {"confidence": "C", "reasons": ["页覆盖率或召回率无法计算"]}

    if pc >= PAGE_COVERAGE_A and r >= FIDELITY_A:
        conf = "A"
        reasons.append(f"页覆盖 {pc:.0%} 且文本召回 {r:.1%} ≥ 95%")
    elif r < FIDELITY_B:
        # v1.4.4：恢复 fidelity-spec §三 C 行「文本召回 <85%」的可达性——
        # 原实现由「页覆盖 ≥90% 或 召回 ≥85%」的 or 分支先行命中 B，该条件恒不可达
        conf = "C"
        reasons.append(f"文本召回 {r:.1%} < 85%——正文缺失过多，页覆盖 {pc:.0%} 达标也不放行，建议升档重转")
    elif pc >= PAGE_COVERAGE_B:
        conf = "B"
        reasons.append(f"页覆盖 {pc:.0%}（≥90%）且文本召回 {r:.1%}（≥85%）")
    else:
        conf = "B"
        reasons.append(f"文本召回 {r:.1%}（≥85%）达标，但页覆盖 {pc:.0%} 未达 90%——按召回放行，MUST 复核缺页")

    if m["structure"]["ppt_images"] and m["structure"]["md_images"] == 0:
        reasons.append(f"PPT 检出图片 {m['structure']['ppt_images']} 张而 MD 无图片引用")
        if conf == "A":
            conf = "B"
    if m["structure"]["ppt_notes"] and m["structure"]["md_notes"] == 0:
        reasons.append(f"PPT 检出备注 {m['structure']['ppt_notes']} 页而 MD 无备注引用块")
        if conf == "A":
            conf = "B"
    if m["anomalies"]:
        reasons.extend(m["anomalies"])
        conf = "C"
    return {"confidence": conf, "reasons": reasons}


def fmt_pct(v):
    return "不适用（无文本）" if v is None else f"{v:.1%}"


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
        f"# PPT → Markdown 转换质量报告",
        "",
        f"> 诚实声明：PPT→MD 是结构降维而非格式复制，本报告承诺「可验证的分级保真」而非绝对无损。",
        "",
        "## 关键数据（必读）",
        "",
        "| 关键数据 | 数值 |",
        "|---|---|",
        f"| **页覆盖率** | **{fmt_pct(m['page_coverage'])}**（MD Slide 块 {m['md_slide_blocks']} / 源 {m['slide_count']} 页） |",
        f"| **文本召回率（保真率）** | **{fmt_pct(m['recall'])}** |",
        f"| **丢失率** | **{fmt_pct(m['loss_rate'])}** |",
        f"| 置信度等级 | **{g['confidence']}**（{'直接可用' if g['confidence'] == 'A' else '抽查复核' if g['confidence'] == 'B' else '强制人工复核'}） |",
        f"| 转换后端 / 档位 | {meta.get('backend') or 'unknown'} / {meta.get('grade') or 'unknown'} |",
        f"| 页数 / 耗时 | {m['slide_count']} 页 / {meta.get('elapsed') or 'unknown'}s |",
        f"| 图片资产 | {meta.get('assets') if meta.get('assets') is not None else m['structure']['md_images']} |",
        f"| 降级轨迹 | {meta.get('downgrades') or '无'} |",
        f"| 源文本提取 | {m['extract_via']} |",
        "",
        "## 置信度判定原因",
        "",
    ]
    lines += [f"- {r}" for r in g["reasons"]]
    lines += ["", "## 结构对比", "", "| 结构 | PPT 侧 | MD 侧 | 口径 |", "|---|---|---|---|",
              f"| 图片 | {m['structure']['ppt_images']} | {m['structure']['md_images']} | PPT 侧为 python-pptx/zipfile 计数 |",
              f"| 备注 | {m['structure']['ppt_notes']} | {m['structure']['md_notes']} | MD 侧为 `> 备注` 引用块计数 |"]
    if m["missing_pages"]:
        lines += ["", "## 缺页明细（源有而 MD 无，优先人工复核）", ""]
        lines += [f"- Slide {p}" for p in m["missing_pages"]]
    lines += ["", "## 异常清单", ""]
    if m["anomalies"]:
        lines += [f"- {a}" for a in m["anomalies"]]
    else:
        lines += ["- 无"]
    lines += [
        "",
        "## 固定复核项（永不消失，即使 A 级）",
        "",
        "- [ ] 演讲者备注丢失（备注在 MD 中未保留或内容不全）",
        "- [ ] SmartArt/图表转图片（SmartArt 只能提图，文字内容可能丢失）",
        "- [ ] 母版占位符（母版/版式上的固定文本可能未进入正文）",
        "- [ ] .ppt 旧格式兼容（OLE 转换后版式/字体可能漂移）",
        "- [ ] 页内多文本框阅读顺序（同页多文本框的 z-order/坐标推断可能错序）",
        "",
        "## 复核结果回填（用户填写，反哺进化契约）",
        "",
        "- 实际丢失内容：",
        "- 复核结论（采信 / 需重转 / 需换档）：",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-pptx2md 门D 质量校验与报告")
    ap.add_argument("--ppt", required=True, help="输入 PPT 文件路径（.pptx/.ppt）")
    ap.add_argument("--md", required=True, help="输出 Markdown 文件路径")
    ap.add_argument("--report-dir", default=None, help="report.md 输出目录（缺省为 MD 同目录）")
    ap.add_argument("--backend", default=None, help="转换后端名（写入报告元数据）")
    ap.add_argument("--grade", default=None, help="转换档位（写入报告元数据）")
    ap.add_argument("--elapsed", type=float, default=None, help="转换耗时秒数")
    ap.add_argument("--assets", type=int, default=None, help="图片资产文件数")
    ap.add_argument("--downgrades", default=None, help="降级轨迹描述，如 'pandoc→python-pptx'")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ppt_path, md_path = Path(args.ppt), Path(args.md)
    for p, label in ((ppt_path, "PPT"), (md_path, "MD")):
        if not p.is_file():
            safe_print(json.dumps({"ok": False, "errors": [f"{label} 文件不存在：{p}"]}, ensure_ascii=False))
            return 2

    t0 = time.time()
    m = compute_metrics(ppt_path, md_path)
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
        safe_print(f"页覆盖率：{fmt_pct(m['page_coverage'])} ｜ 文本召回率：{fmt_pct(m['recall'])} ｜ 置信度：{g['confidence']}")
        safe_print(f"报告：{report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
