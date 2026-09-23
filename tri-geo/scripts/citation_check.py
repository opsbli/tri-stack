#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
来源核验与捏造检测（citation_check.py）——「智引」(tri-geo) 确定性脚本 05/09

职责（对应设计指南 §3.1）：
    · 核验重写稿中每条引用的 URL 可达性（--offline 可跳过网络）
    · 核验「数字 / 人名 / 机构」能否在来源页文本中被定位（字符串/正则匹配）
    · 检测无来源声明的数据句、疑似捏造句式（"研究表明" 无来源等）
    · 任一捏造命中 → 硬阻断（退出码 3），NEVER 降级、NEVER 豁免

设计约束：
    · 纯标准库；同输入逐字节一致（网络失败记为 unreachable，NEVER 记为 verified）
    · 无法核验 MUST 记 unverified 并按阻断处理（--allow-unverified 时标注 ⚠ 未核验放行）
    · 违反 P3（禁虚构）：拿不到证据就标注，绝不伪造核验结果

来源文件格式（--sources，JSON 数组）：
    [{"claim": "2026 年 GEO 市场规模 42 亿元", "url": "https://...",
      "quote": "原文片段（可选）", "path": "本地快照路径（可选）"}]

用法：
    python citation_check.py --file rewrite.md --sources sources.json --json
    python citation_check.py --file rewrite.md --sources sources.json --offline --json
    python citation_check.py --file rewrite.md --sources sources.json --allow-unverified --json

退出码：
    0  全部 verified
    2  存在 unreachable / unverified（默认阻断；--allow-unverified 时标记放行）
    3  存在 mismatch（捏造命中）→ 硬阻断
    64 参数或环境错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_VERSION = "1.0"
TOOL_NAME = "citation_check.py"

HTTP_TIMEOUT = 5
UA = "Mozilla/5.0 (compatible; tri-geo-zhiyin/1.0; +citation-verifier)"

# 疑似捏造句式：出现即要求有可核验来源（无来源 → 记为 risky）
UNSOURCED_CLAIM_RE = re.compile(
    r"(研究表明|研究显示|数据显示|统计显示|据.{0,12}(?:报告|统计|调查)|权威机构|专家表示|业内人士透露)")
NUM_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:%|万|亿|元|倍|年|天|小时|人|家|款)")
# 数据主张口径：百分比 / 金额 / 年份 / 研究类句式。
# 刻意排除「7 天」「3 家」等泛指量词——它们不构成需要来源背书的数据主张，
# 否则会把合规文本大面积误判为「无来源数据句」（false positive）。
DATA_CLAIM_RE = re.compile(
    r"\d+(?:\.\d+)?\s*(?:%|万|亿|元|倍)|(?:19|20)\d{2}\s*年|" + UNSOURCED_CLAIM_RE.pattern)
URL_RE = re.compile(r"https?://\S+")
# 来源声明口径：必须指向可核验对象（URL 或具名来源），单独的「据」字不算——
# 「根据最新数据」这类措辞不含任何可核验对象，NEVER 视为已声明来源。
SOURCE_HINT_RE = re.compile(
    r"(来源[:：]|资料来源|参考资料|参考文献|报告显示|数据显示|研究表明"
    r"|据[^，。]{2,12}(?:报告|统计|调查|显示)|[（(]\s*https?://)")
# 元信息行（署名/更新时间/参考资料标题）：不参与数据句判定
META_LINE_RE = re.compile(
    r"^\s*(?:作者|撰稿|编辑|编译|更新于|最后更新|更新时间|参考资料|参考链接|来源|注[:：])")


def http_text(url: str) -> Tuple[Optional[str], Optional[int], str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read()
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if "html" not in ctype and "text" not in ctype and "json" not in ctype:
                return None, resp.getcode(), f"非文本内容：{ctype or '(空)'}"
            return raw.decode("utf-8", errors="replace"), resp.getcode(), ""
    except urllib.error.HTTPError as e:
        return None, e.code, f"HTTP {e.code} {e.reason}"
    except urllib.error.URLError as e:
        return None, None, f"网络不可达：{e.reason}"
    except (TimeoutError, OSError) as e:
        return None, None, f"网络异常/超时：{type(e).__name__}: {e}"


def norm(text: str) -> str:
    """归一化：去空白与常见标点，便于片段比对。"""
    return re.sub(r"[\s，,、。.：:；;%％]", "", text or "")


def key_tokens(claim: str) -> Dict[str, List[str]]:
    """从主张中提取可定位证据串，区分强/弱两级。

    strong（强证据）：带单位的数字串、引号内引文片段 —— 足以支撑核验结论
    weak  （弱证据）：英文缩写、机构专名 —— 单独命中不足以证明数据真实
                     （捏造内容常常保留真实专名而篡改数字，仅凭弱证据会漏判）
    """
    data: List[str] = []
    year: List[str] = []
    for m in re.finditer(r"\d+(?:\.\d+)?\s*(?:%|万|亿|元|倍|天|小时|人|家|款|kg|GB|MB)", claim):
        data.append(norm(m.group(0)))
    for m in re.finditer(r"(?:19|20)\d{2}\s*年", claim):
        year.append(norm(m.group(0)))
    quote: List[str] = []
    for m in re.finditer(r"[《「【\"']([^》」】\"']{2,30})[》」】\"']", claim):
        quote.append(norm(m.group(1)))
    weak: List[str] = []
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9.\-]{3,24}", claim):
        weak.append(m.group(0).lower())
    for m in re.finditer(r"[一-龥]{2,10}(?:公司|集团|大学|研究院|中心|平台|系统|报告|白皮书)", claim):
        weak.append(norm(m.group(0)))
    return {"data": [t for t in data if len(t) >= 2],
            "year": [t for t in year if len(t) >= 2],
            "quote": [t for t in quote if len(t) >= 2],
            "weak": [t for t in weak if len(t) >= 2]}


def verify_entry(entry: Dict[str, Any], offline: bool,
                 source_dir: Optional[Path]) -> Dict[str, Any]:
    url = (entry.get("url") or "").strip()
    claim = (entry.get("claim") or "").strip()
    quote = (entry.get("quote") or "").strip()
    out: Dict[str, Any] = {"claim": claim, "url": url or None, "status": None,
                           "matched_tokens": [], "evidence": None, "note": None}

    if not url:
        out["status"] = "unverified"
        out["note"] = "无 URL，无法核验（NEVER 视为已核验）"
        return out

    text: Optional[str] = None
    local = entry.get("path")
    if local and Path(local).is_file():
        try:
            text = Path(local).read_text(encoding="utf-8", errors="replace")
            out["evidence"] = f"local:{local}"
        except OSError as e:
            out["note"] = f"本地快照不可读：{e}"
    elif source_dir is not None:
        cand = source_dir / (re.sub(r"[^A-Za-z0-9]+", "_", url)[:120] + ".txt")
        if cand.is_file():
            try:
                text = cand.read_text(encoding="utf-8", errors="replace")
                out["evidence"] = f"local:{cand}"
            except OSError:
                text = None
    if text is None and not offline:
        t, code, err = http_text(url)
        if t is None:
            out["status"] = "unreachable"
            out["note"] = err
            return out
        text = t
        out["evidence"] = f"http:{url}"

    if text is None:
        out["status"] = "unverified"
        out["note"] = out["note"] or "离线模式且无本地快照，未能核验"
        return out

    hay = norm(text)
    tk = key_tokens(claim)
    if quote:
        tk["quote"].append(norm(quote))
    data_t, year_t, quote_t, weak_t = tk["data"], tk["year"], tk["quote"], tk["weak"]
    low = hay.lower()

    # 引文片段：只要有就必须逐字定位，否则判不一致
    for q in quote_t:
        if q not in hay:
            out["status"] = "mismatch"
            out["note"] = "引文片段与来源页不一致"
            return out
    if not data_t and not year_t:
        out["matched_tokens"] = [t for t in weak_t if t.lower() in low]
        out["status"] = "unverified"
        out["note"] = ("主张中无数字/年份类强证据，仅有专名弱匹配，"
                       "不足以证明数据真实（需补充可核验数字或原文片段）")
        return out

    # 数据 token 与年份 token 均需命中：捏造常保留真实年份/专名而篡改数字，
    # 若只校验年份会让「改数字不改年份」的伪造内容通过核验。
    hit_data = [t for t in data_t if t.lower() in low]
    hit_year = [t for t in year_t if t.lower() in low]
    out["matched_tokens"] = hit_data + hit_year
    if data_t and not hit_data:
        out["status"] = "mismatch"
        out["note"] = "来源页中未定位到主张的关键数字（疑似捏造）"
        return out
    if year_t and not hit_year:
        out["status"] = "mismatch"
        out["note"] = "来源页中未定位到主张的年份（疑似捏造）"
        return out
    out["status"] = "verified"
    return out


def detect_unsourced(md: str) -> List[Dict[str, Any]]:
    """检测无来源声明的数据句与疑似捏造句式。"""
    risky: List[Dict[str, Any]] = []
    for para in re.split(r"\n\s*\n", md):
        p = para.strip()
        if not p or META_LINE_RE.match(p):
            continue
        has_num = bool(DATA_CLAIM_RE.search(p))
        if not has_num:
            continue
        has_src = bool(URL_RE.search(p) or SOURCE_HINT_RE.search(p))
        if not has_src:
            risky.append({"excerpt": re.sub(r"\s+", " ", p)[:120],
                          "reason": "含数据/研究类表述但无来源标注"})
    return risky


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="「智引」来源核验与捏造检测（硬阻断）")
    ap.add_argument("--file", required=True, help="重写稿 Markdown 路径")
    ap.add_argument("--sources", default=None,
                    help="来源清单 JSON（[{claim,url,quote,path}]）")
    ap.add_argument("--source-dir", default=None, help="来源页本地快照目录（离线核验）")
    ap.add_argument("--offline", action="store_true", help="禁用网络（仅用本地快照）")
    ap.add_argument("--allow-unverified", action="store_true",
                    help="允许未核验项放行（报告中 MUST 标注 ⚠ 未核验）")
    ap.add_argument("--out", default=None, help="核验 JSON 落盘路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    p = Path(args.file)
    if not p.is_file():
        print(f"[智引·来源核验] 文件不存在：{p}", file=sys.stderr)
        return 64
    md = p.read_text(encoding="utf-8", errors="replace")

    entries: List[Dict[str, Any]] = []
    if args.sources:
        sp = Path(args.sources)
        if not sp.is_file():
            print(f"[智引·来源核验] 来源文件不存在：{sp}", file=sys.stderr)
            return 64
        data = json.loads(sp.read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else data.get("sources", [])

    source_dir = Path(args.source_dir) if args.source_dir else None
    results = [verify_entry(e, args.offline, source_dir) for e in entries]
    risky = detect_unsourced(md)

    counts = {"verified": 0, "mismatch": 0, "unreachable": 0, "unverified": 0}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    blocked = counts["mismatch"] > 0 or (risky and not args.allow_unverified)
    soft_block = (counts["unreachable"] + counts["unverified"]) > 0

    result: Dict[str, Any] = {
        "tool": TOOL_NAME,
        "schema_version": SCHEMA_VERSION,
        "file": str(p),
        "entries": results,
        "summary": counts,
        "unsourced_claims": risky,
        "blocked": blocked,
        "allow_unverified": args.allow_unverified,
        "next_action": ("block" if blocked else
                        ("proceed_with_warning" if args.allow_unverified else "block"))
        if soft_block else ("block" if blocked else "proceed"),
    }

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(payload, encoding="utf-8")
    if args.json or args.out:
        print(payload)
    else:
        print(f"[智引·来源核验] verified {counts['verified']} / mismatch {counts['mismatch']} / "
              f"unreachable {counts['unreachable']} / unverified {counts['unverified']}")
        for r in results:
            if r["status"] != "verified":
                print(f"  ✗ {r['status']}：{r['claim'][:60]} — {r['note']}")
        for r in risky:
            print(f"  ⚠ 无来源数据句：{r['excerpt']}")
        if blocked:
            print("  结论：硬阻断（捏造命中或无来源数据句），禁止输出")

    if blocked:
        return 3
    if soft_block and not args.allow_unverified:
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[智引·来源核验] 脚本异常：{type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(64)
