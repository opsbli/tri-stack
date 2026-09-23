#!/usr/bin/env python3
"""门D · 质量校验与报告生成（tri-html2md）

确定性计算：文本召回率 / 丢失率 / 噪声率 / 结构对比（标题 h1-h6·表格·图片·链接）/
异常清单 → 置信度 A/B/C → 生成 report.md
（报告 MUST 含文本召回率、丢失率等关键数据——用户硬要求，NEVER 省略）。

HTML 无可见文本（纯脚本/纯样式页）召回率不可计算时显式标注「不适用」，NEVER 编造数值。
退出码：0 校验完成（置信度见输出）；2 参数错误。
"""
from _io_safe import safe_print
import argparse
import datetime as _dt
import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path

FIDELITY_A = 0.95
FIDELITY_B = 0.85
HTML_TEXT_MIN_CHARS = 50          # HTML 可见文本总字符低于此值视为无可见文本
SCRIPT_LEAK_MIN_CHARS = 200       # script/style 归一化字符低于此值不判泄漏
SCRIPT_LEAK_RATIO = 0.30          # script/style bigram 在 MD 中覆盖率高于此值 → 泄漏（warning 级）
_SCRIPT_LEAK_WINDOW = 80          # verbatim 连续窗口长度（空白归一后字符）——真实泄漏的结构证据
_SCRIPT_LEAK_STRIDE = 40          # 窗口步进
_SCRIPT_LEAK_WINDOW_HITS = 3      # 逐字命中窗口数 ≥ 此值 → 判真实泄漏（anomaly）
_MD_IMG = re.compile(r"!\[[^\]]*\]\([^)]+\)|<img\s[^>]*>", re.IGNORECASE)
_MD_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_MD_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}.*\|", re.MULTILINE)
_MD_FENCE = re.compile(r"^```", re.MULTILINE)
_MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\([^)]+\)", re.MULTILINE)  # 负向后顾排除图片语法
_MOJIBAKE = re.compile(r"锟斤拷|烫烫烫|锘|â€|Ã")


class HtmlTextExtractor(HTMLParser):
    """提取 HTML 可见文本（跳过 script/style 内容）+ 结构计数。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text_parts = []
        self.script_parts = []
        self.style_parts = []
        self.skip_depth = 0          # >0 表示在 script/style 内
        self.in_script = False
        self.in_style = False
        self.in_head = False         # <head> 内（title/meta 等元数据）不计入可见文本
        self.headings = 0
        self.tables = 0
        self.images = 0
        self.links = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            if tag == "script":
                self.in_script = True
            else:
                self.in_style = True
            self.skip_depth += 1
        elif tag == "head":
            self.in_head = True
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings += 1
        elif tag == "table":
            self.tables += 1
        elif tag == "img":
            self.images += 1
        elif tag == "a":
            self.links += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip_depth = max(0, self.skip_depth - 1)
            if self.skip_depth == 0:
                self.in_script = False
                self.in_style = False
        elif tag == "head":
            self.in_head = False

    def handle_data(self, data):
        if self.in_script:
            self.script_parts.append(data)
        elif self.in_style:
            self.style_parts.append(data)
        elif self.skip_depth == 0 and not self.in_head:
            self.text_parts.append(data)


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


def _ws_norm(s: str) -> str:
    """空白归一（保留词序与连续性，供逐字窗口匹配）。"""
    return re.sub(r"\s+", " ", s or "").strip()


def _verbatim_leak_hits(ss_raw: str, md_ws: str) -> int:
    """script/style 原文中 80 字符连续窗口逐字出现在 MD 的数量（真实泄漏的结构证据）。
    整块泄漏 → 几乎全部窗口命中；导航/JSON-LD 词汇与正文散点重叠 → 0 命中。"""
    ss = _ws_norm(ss_raw)
    if len(ss) < _SCRIPT_LEAK_WINDOW:
        return 0
    hits = 0
    for i in range(0, len(ss) - _SCRIPT_LEAK_WINDOW + 1, _SCRIPT_LEAK_STRIDE):
        if ss[i:i + _SCRIPT_LEAK_WINDOW] in md_ws:
            hits += 1
    return hits


def extract_html(html_path: Path) -> dict:
    """返回 {visible_text, script_text, style_text, counts}。"""
    raw = html_path.read_bytes()
    # 复用门A 编码探测逻辑：BOM → meta → 候选解码
    enc = "utf-8"
    if raw.startswith(b"\xef\xbb\xbf"):
        enc = "utf-8-sig"
    elif raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        enc = "utf-16"
    else:
        head = raw[:4096].decode("ascii", errors="ignore")
        m = re.search(r'<meta[^>]+charset\s*=\s*["\']?([A-Za-z0-9_\-]+)', head, re.IGNORECASE)
        if m:
            enc = m.group(1)
    try:
        text = raw.decode(enc, errors="replace")
    except (UnicodeDecodeError, LookupError):
        text = raw.decode("utf-8", errors="replace")

    parser = HtmlTextExtractor()
    try:
        parser.feed(text)
        parser.close()
    except Exception:
        pass
    return {
        "visible_text": "".join(parser.text_parts),
        "script_text": "".join(parser.script_parts),
        "style_text": "".join(parser.style_parts),
        "counts": {
            "html_headings": parser.headings,
            "html_tables": parser.tables,
            "html_images": parser.images,
            "html_links": parser.links,
        },
    }


def compute_metrics(html_path: Path, md_path: Path) -> dict:
    md_text = md_path.read_text(encoding="utf-8", errors="replace")
    html = extract_html(html_path)
    visible_norm = normalize(html["visible_text"])
    md_norm = normalize(md_text)

    m = {
        "html_path": str(html_path),
        "md_path": str(md_path),
        "html_visible_chars": len(visible_norm),
        "md_total_chars": len(md_norm),
        "has_visible_text": len(visible_norm) > 0,
        "low_text": 0 < len(visible_norm) < HTML_TEXT_MIN_CHARS,
        "recall": None,
        "loss_rate": None,
        "noise_rate": None,
    }
    m.update(html["counts"])

    # MD 侧结构计数
    md_counts = {
        "md_headings": len(_MD_HEADING.findall(md_text)),
        "md_tables": len(_MD_TABLE_SEP.findall(md_text)),
        "md_images": len(_MD_IMG.findall(md_text)),
        "md_links": len(_MD_LINK.findall(md_text)),
    }
    m.update(md_counts)

    if m["has_visible_text"]:
        html_bg = bigrams(visible_norm)
        md_bg = bigrams(md_norm)
        if html_bg:
            m["recall"] = round(len(html_bg & md_bg) / len(html_bg), 4)
            m["loss_rate"] = round(1.0 - m["recall"], 4)
        if md_bg:
            m["noise_rate"] = round(len(md_bg - html_bg) / len(md_bg), 4)

    # 异常清单（命中即 C 级）与警告清单（仅提示，不降级）
    anomalies = []
    warnings = []
    if m["low_text"]:
        warnings.append(
            f"HTML 可见文本较少（{m['html_visible_chars']} 字符）——多为结构/表格页，召回率参考价值有限"
        )
    n_replace = md_text.count("\ufffd")
    if n_replace:
        anomalies.append(f"检测到 {n_replace} 处乱码替换符（U+FFFD）——疑似编码误判")
    moji = _MOJIBAKE.findall(md_text)
    if moji:
        anomalies.append(f"检测到编码误判特征（{'、'.join(set(moji))}）——疑似 gbk/utf-8 混用")
    if len(md_norm.strip()) == 0:
        anomalies.append("MD 输出为空——转换失败")
    if m["has_visible_text"] and m["md_total_chars"] < len(visible_norm) * 0.3:
        anomalies.append("MD 内容量显著小于 HTML 可见文本（<30%）——疑似截断或漏段")
    if len(_MD_FENCE.findall(md_text)) % 2 != 0:
        anomalies.append("代码块围栏不成对——MD 语法破损")
    # 脚本/样式内容误入正文检测（两段式，质量测试轮 §六-1 降噪）：
    #   anomaly（强制 C）= 结构证据：80 字符连续窗口逐字出现在 MD → 真实整块泄漏；
    #   warning（仅提示，不降级）= bigram 覆盖率高但无逐字命中——多为导航/JSON-LD 文案与正文重叠。
    # 注：bigram 覆盖率在此独立计算 md_bg（原实现复用 has_visible_text 分支变量，纯脚本页有 NameError 隐患）。
    script_style = normalize(html["script_text"] + html["style_text"])
    if len(script_style) >= SCRIPT_LEAK_MIN_CHARS:
        md_bg_full = bigrams(md_norm)
        ss_bg = bigrams(script_style)
        cov = round(len(ss_bg & md_bg_full) / len(ss_bg), 4) if ss_bg else 0.0
        hits = _verbatim_leak_hits(html["script_text"] + html["style_text"], _ws_norm(md_text))
        m["script_style_cov"] = cov
        m["script_style_verbatim_windows"] = hits
        if hits >= _SCRIPT_LEAK_WINDOW_HITS:
            anomalies.append(
                f"脚本/样式内容误入正文（{hits} 个 {_SCRIPT_LEAK_WINDOW} 字符连续窗口逐字出现在 MD——真实泄漏）"
            )
        elif cov > SCRIPT_LEAK_RATIO:
            warnings.append(
                f"script/style bigram 在 MD 中覆盖率 {cov:.1%} > 30%，但无连续窗口逐字命中"
                "——多为导航/JSON-LD 文案与正文词汇重叠，非真实泄漏，不降级"
            )
    m["anomalies"] = anomalies
    m["warnings"] = warnings
    return m


def grade_confidence(m: dict) -> dict:
    """置信度 A/B/C 判定（阈值唯一真源：references/fidelity-spec.md）。"""
    reasons = []
    if not m["has_visible_text"]:
        return {"confidence": "C",
                "reasons": ["无可见文本（纯脚本/纯样式页）——文本召回率不适用，C 级口径"]}
    r = m["recall"]
    if r is None:
        return {"confidence": "C", "reasons": ["召回率无法计算"]}
    if r < FIDELITY_B:
        reasons.append(f"文本召回率 {r:.1%} < 85%")
        conf = "C"
    elif r < FIDELITY_A:
        reasons.append(f"文本召回率 {r:.1%} 处于 85–95% 区间")
        conf = "B"
    else:
        conf = "A"
    if m["html_tables"] and m["md_tables"] == 0:
        reasons.append(f"HTML 检出表格 {m['html_tables']} 处而 MD 无表格语法")
        conf = "C" if conf == "A" else conf
    if m["html_images"] and m["md_images"] == 0:
        reasons.append(f"HTML 检出图片 {m['html_images']} 张而 MD 无图片引用")
        if conf == "A":
            conf = "B"
    if m["html_links"] and m["md_links"] == 0:
        reasons.append(f"HTML 检出链接 {m['html_links']} 个而 MD 无链接语法")
        if conf == "A":
            conf = "B"
    if m["anomalies"]:
        reasons.extend(m["anomalies"])
        conf = "C"
    if not reasons:
        reasons.append(f"文本召回率 {r:.1%} ≥ 95% 且结构计数吻合、无异常")
    return {"confidence": conf, "reasons": reasons}


def fmt_pct(v):
    return "不适用（无可见文本）" if v is None else f"{v:.1%}"


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
        "# HTML → Markdown 转换质量报告",
        "",
        f"> 诚实声明：HTML→MD 是结构降维（内联样式/脚本/富交互必然丢失），本报告承诺「可验证的分级保真」而非绝对无损。",
        "",
        "## 关键数据（必读）",
        "",
        "| 关键数据 | 数值 |",
        "|---|---|",
        f"| **文本召回率** | **{fmt_pct(m['recall'])}** |",
        f"| **丢失率** | **{fmt_pct(m['loss_rate'])}** |",
        f"| 噪声率（MD 冗余内容占比） | {fmt_pct(m['noise_rate'])} |",
        f"| 置信度等级 | **{g['confidence']}**（{'直接可用' if g['confidence'] == 'A' else '抽查复核' if g['confidence'] == 'B' else '强制人工复核'}） |",
        f"| 转换后端 / 档位 | {meta.get('backend') or 'unknown'} / {meta.get('grade') or 'unknown'} |",
        f"| 文件大小 / 耗时 | {meta.get('size') or 'unknown'} / {meta.get('elapsed') or 'unknown'}s |",
        f"| 图片资产 | {meta.get('assets') if meta.get('assets') is not None else m['md_images']} |",
        f"| 降级轨迹 | {meta.get('downgrades') or '无'} |",
        "",
        "## 置信度判定原因",
        "",
    ]
    lines += [f"- {r}" for r in g["reasons"]]
    lines += ["", "## 结构对比", "", "| 结构 | HTML 侧 | MD 侧 | 口径 |", "|---|---|---|---|",
              f"| 标题 h1-h6 | {m['html_headings']} | {m['md_headings']} | HTML 侧为标签计数，MD 侧为 # 语法计数 |",
              f"| 表格 | {m['html_tables']} | {m['md_tables']} | HTML 侧为 <table> 计数 |",
              f"| 图片 | {m['html_images']} | {m['md_images']} | HTML 侧为 <img> 计数 |",
              f"| 链接 | {m['html_links']} | {m['md_links']} | HTML 侧为 <a> 计数 |"]
    lines += ["", "## 异常清单", ""]
    if m["anomalies"]:
        lines += [f"- {a}" for a in m["anomalies"]]
    else:
        lines += ["- 无"]
    lines += ["", "## 警告（不降级，仅提示）", ""]
    if m["warnings"]:
        lines += [f"- {w}" for w in m["warnings"]]
    else:
        lines += ["- 无"]
    lines += [
        "",
        "## 固定复核项（永不消失，即使 A 级）",
        "",
        "- [ ] 内联样式丢失（style 属性/class 样式在 MD 中不可见，确认无关键信息依赖样式）",
        "- [ ] script/style 内容误入正文（确认脚本/样式未泄漏进正文）",
        "- [ ] 相对链接失效（相对路径在 MD 中可能失效，确认引用完整性）",
        "- [ ] 嵌套表格（HTML 嵌套表格转 MD 后可能被压平，确认结构）",
        "- [ ] 编码误判（gbk 中文乱码，确认无 U+FFFD/锟斤拷）",
        "",
        "## 复核结果回填（用户填写，反哺进化契约）",
        "",
        "- 实际丢失内容：",
        "- 复核结论（采信 / 需重转 / 需换档）：",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-html2md 门D 质量校验与报告")
    ap.add_argument("--html", required=True, help="输入 HTML 文件路径（.html/.htm）")
    ap.add_argument("--md", required=True, help="输出 Markdown 文件路径")
    ap.add_argument("--report-dir", default=None, help="report.md 输出目录（缺省为 MD 同目录）")
    ap.add_argument("--backend", default=None, help="转换后端名（写入报告元数据）")
    ap.add_argument("--grade", default=None, help="转换档位（写入报告元数据）")
    ap.add_argument("--elapsed", type=float, default=None, help="转换耗时秒数")
    ap.add_argument("--assets", type=int, default=None, help="图片资产文件数")
    ap.add_argument("--downgrades", default=None, help="降级轨迹描述，如 'pandoc→markitdown'")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    html_path, md_path = Path(args.html), Path(args.md)
    for p, label in ((html_path, "HTML"), (md_path, "MD")):
        if not p.is_file():
            safe_print(json.dumps({"ok": False, "errors": [f"{label} 文件不存在：{p}"]}, ensure_ascii=False))
            return 2

    t0 = time.time()
    m = compute_metrics(html_path, md_path)
    g = grade_confidence(m)
    meta = {"backend": args.backend, "grade": args.grade, "elapsed": args.elapsed,
            "assets": args.assets, "downgrades": args.downgrades,
            "size": f"{html_path.stat().st_size} B",
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
        safe_print(f"文本召回率：{fmt_pct(m['recall'])} ｜ 丢失率：{fmt_pct(m['loss_rate'])} ｜ 置信度：{g['confidence']}")
        safe_print(f"报告：{report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
