#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
站内信号确定性评分（site_signal.py）——「智引」(tri-geo) 确定性脚本 03/09

职责（对应设计指南 §3.1 / §4.1）：
    · 可引用性五维评分（中文规则）：答案块质量 / 段落自包含 / 结构可读性 /
      统计密度 / 独特性
    · 技术基建（SSR/可索引/站点地图/URL/语言）、Schema 完整度、权威信号、
      爬虫与 llms.txt 访问矩阵
    · 复合站内信号分 + veto 一票否决（阻断/封顶）

设计约束：
    · 纯标准库；同输入多次运行逐字节一致（默认无时间戳）
    · 未提供的输入维度（如 robots.txt）不计分也不猜测，标注 status=missing
    · 爬虫清单区分 verified / unverified：未公开 UA 的厂商爬虫 NEVER 参与封顶判定

用法：
    python site_signal.py --content page.json --robots raw/robots.txt --llmstxt raw/llms.txt --json
    python site_signal.py --content page.json --out scores.json --json

退出码：
    0  评分完成
    1  存在封顶类 veto（评分有效但上限 60）
    2  存在阻断类 veto（无法评分）
    64 参数或环境错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_VERSION = "1.0"
TOOL_NAME = "site_signal.py"

# 复合权重（设计指南 §4.1 未给出复合权重，本处按「删除海外 Platform 维度后重分配」
# 固化于 references/scoring-spec.md，脚本注释与文档 MUST 保持一致）
COMPOSITE_WEIGHTS = {
    "citability": 0.40,
    "infra": 0.20,
    "schema": 0.15,
    "authority": 0.15,
    "crawl_llms": 0.10,
}

DEF_RE = re.compile(r"[^\s。！？；：，、]{2,24}(?:是|指的是|指|包括|定义为|即)\s")
Q_HEAD_RE = re.compile(r"(什么是|如何|怎么|哪些|为什么|多久|多少钱|哪个好|吗[？?]|？)")
PRON_RE = re.compile(r"[他她它其该此这那]")
ORIGINAL_RE = re.compile(r"(我们(?:统计|实测|调研|分析|测试|发现)|本文|本(?:报告|研究|实测)|调研显示|实测数据|案例分析)")
ENTITY_SUFFIX_RE = re.compile(r"[A-Za-z][A-Za-z0-9.-]{1,20}|[一-龥]{2,8}(?:公司|集团|平台|系统|模型|协议|标准|大学|研究院|实验室|中心|机构|银行|医院)")
TERM_RE = re.compile(r"[《「【\"']([^》」】\"']{2,20})[》」】\"']")
PCT_RE = re.compile(r"\d+(?:\.\d+)?\s*%|百分之\s*\d+")
MONEY_RE = re.compile(r"[￥¥$]\s?\d+(?:\.\d+)?(?:万|亿|元)?|\d+(?:\.\d+)?\s?(?:万元|亿元|元|美元)")
YEAR_RE = re.compile(r"(?:19|20)\d{2}\s*年")
UNIT_RE = re.compile(r"\d+(?:\.\d+)?\s?(?:天|小时|分钟|秒|倍|人|家|款|台|件|次|万|亿|公斤|kg|ms|GB|MB)")
AUTHOR_RE = re.compile(r"(作者|撰稿|编辑)[：: ]\s*\S{2,12}|By\s+[A-Za-z ]{2,24}")
UPDATE_RE = re.compile(r"(更新于|最后更新|更新日期|修改时间)[：: ]?\s*((?:19|20)\d{2}[-/年]\d{1,2}[-/月]\d{1,2})")

# 公开可核验的爬虫 UA（verified=True 才参与封顶判定）
CRAWLERS: List[Tuple[str, str, bool]] = [
    ("Bytespider", "字节（豆包/头条系）内容抓取", True),
    ("Baiduspider", "百度搜索（含 AI 搜索召回）", True),
    ("360Spider", "360 搜索", True),
    ("Sogou web spider", "搜狗搜索", True),
    ("YisouSpider", "神马/夸克搜索", True),
]
# 厂商未公开专用爬虫 UA：NEVER 参与评分，仅作核查提示（P3 禁虚构）
CRAWLERS_UNVERIFIED = ["DeepSeek（未公开专用 UA）", "Kimi（未公开专用 UA）",
                       "智谱 GLM（未公开专用 UA）", "元宝/腾讯（未公开专用 UA）"]


def clamp(v: float, lo: int = 0, hi: int = 100) -> int:
    return int(max(lo, min(hi, round(v))))


def load_json(path: str) -> Dict[str, Any]:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def read_text_maybe(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


# ---------------------------------------------------------------------------
# 五维可引用性（块级）
# ---------------------------------------------------------------------------


def score_answer_quality(block: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    text = block.get("text", "") or ""
    head = re.sub(r"\s+", "", text)[:120]
    pts = 0
    detail: Dict[str, Any] = {}
    has_def = bool(DEF_RE.search(head)) or block.get("has_definition_pattern")
    detail["定义句式"] = has_def
    pts += 30 if has_def else 0
    first60 = bool(block.get("first60_standalone"))
    detail["首60字可独立成答"] = first60
    pts += 25 if first60 else 0
    q = bool(Q_HEAD_RE.search(block.get("heading", "") or ""))
    detail["问句式标题"] = q
    pts += 20 if q else 0
    sents = [s for s in re.split(r"[。！？；]", text) if s.strip()]
    if sents:
        short = sum(1 for s in sents if 20 <= len(re.sub(r"\s+", "", s)) <= 40)
        ratio = short / len(sents)
        detail["短句占比"] = round(ratio, 2)
        if ratio >= 0.5:
            pts += 15
        elif ratio >= 0.3:
            pts += 8
    first_sent = sents[0] if sents else ""
    direct = bool(re.search(r"\d", first_sent) or DEF_RE.search(first_sent[:40]))
    detail["首句直接作答"] = direct
    pts += 10 if direct else 0
    return clamp(pts), detail


def score_self_containment(block: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    text = block.get("text", "") or ""
    chars = block.get("char_count", 0) or len(re.sub(r"\s+", "", text))
    pts = 0
    detail: Dict[str, Any] = {"字数": chars}
    if 120 <= chars <= 200:
        pts += 40
    elif 100 <= chars <= 250:
        pts += 28
    elif 80 <= chars <= 300:
        pts += 16
    else:
        pts += 6
    pron = len(PRON_RE.findall(text))
    density = (pron / chars) if chars else 0.0
    detail["代词密度"] = round(density, 4)
    if density < 0.02:
        pts += 30
    elif density < 0.04:
        pts += 18
    nouns = len(set(ENTITY_SUFFIX_RE.findall(text)))
    detail["专名数"] = nouns
    pts += 30 if nouns >= 3 else (15 if nouns >= 1 else 0)
    return clamp(pts), detail


def score_structure(block: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    detail: Dict[str, Any] = {}
    pts = 0
    level = block.get("level", 0) or 0
    detail["标题层级"] = level if level else "无标题"
    pts += 30 if level in (1, 2, 3) else 12
    has_media = (block.get("lists", 0) or 0) + (block.get("tables", 0) or 0)
    detail["列表或表格"] = has_media
    pts += 25 if has_media else 0
    sents = [s for s in re.split(r"[。！？；]", block.get("text", "") or "") if s.strip()]
    ok_len = all(len(re.sub(r"\s+", "", s)) <= 60 for s in sents) if sents else False
    detail["句长可控"] = ok_len
    pts += 25 if ok_len else 8
    paras = block.get("paragraphs", 0) or 0
    detail["段落数"] = paras
    pts += 20 if 2 <= paras <= 4 else (10 if paras >= 1 else 0)
    return clamp(pts), detail


def score_stats_density(block: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    text = block.get("text", "") or ""
    chars = block.get("char_count", 0) or len(re.sub(r"\s+", "", text))
    count = (len(PCT_RE.findall(text)) + len(MONEY_RE.findall(text))
             + len(YEAR_RE.findall(text)) + len(UNIT_RE.findall(text)))
    per500 = (count / (chars / 500)) if chars >= 100 else count
    detail = {"统计点": count, "每500字密度": round(per500, 2)}
    # 配额：每 500 字 ≥3 个具体统计点（references/scoring-spec.md §2.4）
    return clamp(min(100, per500 / 3.0 * 100)), detail


def score_uniqueness(block: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    text = block.get("text", "") or ""
    pts = 0
    orig = bool(ORIGINAL_RE.search(text))
    terms = len(TERM_RE.findall(text))
    case = bool(re.search(r"(案例|客户|实测|样本|样本量|样本数)", text))
    detail = {"原创研究句式": orig, "专有术语": terms, "案例/样本": case}
    pts += 40 if orig else 0
    pts += 30 if case else 0
    pts += 30 if terms >= 1 else 0
    return clamp(pts), detail


DIM_FUNCS = [
    ("answer_quality", score_answer_quality, 0.30),
    ("self_containment", score_self_containment, 0.25),
    ("structure", score_structure, 0.20),
    ("stats_density", score_stats_density, 0.15),
    ("uniqueness", score_uniqueness, 0.10),
]


def score_citability(content: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    blocks = [b for b in content.get("blocks", []) if (b.get("char_count", 0) or 0) >= 40]
    if not blocks:
        return 0, {"blocks": [], "note": "无有效内容块（正文 <40 字）"}
    scored = []
    for b in blocks:
        total = 0.0
        dims: Dict[str, Any] = {}
        for name, fn, w in DIM_FUNCS:
            s, d = fn(b)
            dims[name] = {"score": s, "detail": d}
            total += s * w
        scored.append({
            "heading": b.get("heading", ""),
            "level": b.get("level", 0),
            "char_count": b.get("char_count", 0),
            "block_score": clamp(total),
            "dims": dims,
        })
    scored.sort(key=lambda x: x["block_score"], reverse=True)
    top = scored[:5]
    page = clamp(sum(x["block_score"] for x in top) / len(top))
    heading_skip = detect_heading_skip(blocks)
    return page, {
        "blocks": scored,
        "top5_avg": page,
        "heading_skip": heading_skip,
        "coverage_above70": round(
            100.0 * sum(1 for x in scored if x["block_score"] >= 70) / len(scored), 1),
    }


def detect_heading_skip(blocks: List[Dict[str, Any]]) -> bool:
    levels = [b.get("level", 0) for b in blocks if (b.get("level") or 0) > 0]
    for a, b in zip(levels, levels[1:]):
        if b - a > 1:
            return True
    return False


# ---------------------------------------------------------------------------
# 其余维度
# ---------------------------------------------------------------------------


def score_infra(content: Dict[str, Any], robots: Optional[str]) -> Tuple[int, Dict[str, Any]]:
    stats = content.get("stats", {})
    body = stats.get("body_text_chars", 0) or 0
    detail: Dict[str, Any] = {"正文字符": body}
    if body >= 800:
        ssr = 100
    elif body >= 300:
        ssr = 70
    elif body >= 100:
        ssr = 40
    else:
        ssr = 0
    detail["SSR/可解析正文"] = ssr
    title = content.get("title", "")
    desc = (content.get("meta", {}) or {}).get("description", "")
    idx = 100 if (title and desc) else (60 if (title or desc) else 20)
    detail["标题与描述可索引"] = idx
    sitemap = 100 if (robots and re.search(r"(?im)^\s*Sitemap\s*:", robots)) else 40
    detail["robots 声明站点地图"] = sitemap
    url = content.get("url", "") or ""
    ustruct = 100 if ("?" not in url and url.count("/") <= 4) else 60
    detail["URL 结构"] = ustruct
    lang = (content.get("lang") or "").lower()
    lscore = 100 if lang.startswith("zh") else 60
    detail["语言声明"] = lscore
    total = ssr * 0.40 + idx * 0.20 + sitemap * 0.20 + ustruct * 0.10 + lscore * 0.10
    return clamp(total), detail


def score_schema(content: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    raws = content.get("jsonld_raw", []) or []
    types: List[str] = []
    parsed: List[Dict[str, Any]] = []
    for r in raws:
        try:
            data = json.loads(r)
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for it in items:
            if isinstance(it, dict):
                parsed.append(it)
                t = it.get("@type")
                if isinstance(t, list):
                    types.extend([str(x) for x in t])
                elif t:
                    types.append(str(t))
    detail: Dict[str, Any] = {"types": sorted(set(types))}
    pts = 0
    if types:
        pts += 25
    org = next((p for p in parsed if str(p.get("@type", "")).lower() == "organization"), None)
    if org:
        pts += 15
        same = org.get("sameAs") or []
        if isinstance(same, str):
            same = [same]
        if len(same) >= 3:
            pts += 15
        elif same:
            pts += 8
        detail["organization_sameAs"] = len(same)
    art = next((p for p in parsed if str(p.get("@type", "")).lower()
                in ("article", "blogposting", "newsarticle")), None)
    if art:
        pts += 10
        if art.get("author"):
            pts += 10
        if art.get("dateModified"):
            pts += 10
        detail["article_fields"] = {"author": bool(art.get("author")),
                                    "dateModified": bool(art.get("dateModified"))}
    person = next((p for p in parsed if str(p.get("@type", "")).lower() == "person"), None)
    if person:
        pts += 10
        if person.get("sameAs"):
            pts += 5
    if any(str(p.get("@type", "")).lower() == "breadcrumblist" for p in parsed):
        pts += 5
    if not types:
        pts = 0
    return clamp(pts), detail


def score_authority(content: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    text = " ".join(b.get("text", "") for b in content.get("blocks", []))
    pts = 0
    detail: Dict[str, Any] = {}
    author_hit = bool(AUTHOR_RE.search(text))
    detail["作者署名"] = author_hit
    pts += 30 if author_hit else 0
    upd = UPDATE_RE.search(text)
    detail["更新时间可见"] = bool(upd)
    pts += 25 if upd else 0
    cite = len(re.findall(r"https?://", text))
    detail["外链引用数"] = cite
    if cite >= 3:
        pts += 25
    elif cite >= 1:
        pts += 12
    orig = bool(ORIGINAL_RE.search(text))
    detail["一手数据/原创研究"] = orig
    pts += 20 if orig else 0
    return clamp(pts), detail


def score_crawl_llms(robots: Optional[str], llmstxt: Optional[str]) -> Tuple[int, Dict[str, Any]]:
    detail: Dict[str, Any] = {"crawlers": {}, "llmstxt": None}
    if robots is None:
        detail["status"] = "missing"
        detail["note"] = "未提供 robots.txt，爬虫维度不计分（NEVER 猜测）"
        return 0, detail
    blocked = 0
    for ua, desc, verified in CRAWLERS:
        allowed = judge_ua(robots, ua)
        detail["crawlers"][ua] = {"desc": desc, "verified": verified, "allowed": allowed}
        if verified and not allowed:
            blocked += 1
    total_verified = sum(1 for _, _, v in CRAWLERS if v)
    crawl_score = clamp(100 - (blocked / total_verified) * 100) if total_verified else 0
    # llms.txt 分档 0/30/50/70/90（references/scoring-spec.md §2.5）
    if llmstxt is None:
        lms = 0
        detail["llmstxt"] = {"present": False}
    else:
        t = llmstxt.strip()
        heads = len(re.findall(r"(?m)^#+\s", t))
        links = len(re.findall(r"(?m)^\s*[-*]\s*\[", t))
        if not t:
            lms = 0
        elif heads == 0 and links == 0:
            lms = 30
        elif heads >= 1 and links <= 2:
            lms = 50
        elif heads >= 2 and links >= 3:
            lms = 70
        else:
            lms = 70
        detail["llmstxt"] = {"present": True, "headings": heads, "links": links}
    detail["blocked_verified_crawlers"] = blocked
    detail["unverified_note"] = (
        "以下厂商未公开专用爬虫 UA，禁止参与评分，仅提示人工核查：" + "、".join(CRAWLERS_UNVERIFIED))
    return clamp(crawl_score * 0.7 + lms * 0.3), detail


def judge_ua(robots: str, ua: str) -> bool:
    """判定 robots.txt 是否允许指定 UA（未声明即视为允许）。"""
    lines = robots.splitlines()
    target = ua.lower()
    applicable: List[str] = []
    current_all = False
    current_match = False
    for raw in lines:
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if re.match(r"(?i)^user-agent\s*:", line):
            val = line.split(":", 1)[1].strip().lower()
            current_all = (val == "*")
            current_match = (val == target) or (target.startswith(val) and val != "*")
            continue
        if current_all or current_match:
            applicable.append(line)
    if not applicable:
        return True
    for line in applicable:
        if re.match(r"(?i)^disallow\s*:\s*/?\s*$", line):
            return True
        if re.match(r"(?i)^disallow\s*:", line):
            return False
    return True


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="「智引」站内信号确定性评分")
    ap.add_argument("--content", required=True, help="fetch_page.py 产出的内容 JSON")
    ap.add_argument("--robots", default=None, help="robots.txt 文本路径")
    ap.add_argument("--llmstxt", default=None, help="llms.txt 文本路径")
    ap.add_argument("--out", default=None, help="评分 JSON 落盘路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--stamp", action="store_true", help="注入时间戳（默认不注入）")
    args = ap.parse_args(argv)

    content = load_json(args.content)
    robots = read_text_maybe(args.robots)
    llmstxt = read_text_maybe(args.llmstxt)

    cit, cit_detail = score_citability(content)
    infra, infra_detail = score_infra(content, robots)
    schema, schema_detail = score_schema(content)
    auth, auth_detail = score_authority(content)
    crawl, crawl_detail = score_crawl_llms(robots, llmstxt)

    pillars = {"citability": cit, "infra": infra, "schema": schema,
               "authority": auth, "crawl_llms": crawl}
    total = clamp(sum(pillars[k] * w for k, w in COMPOSITE_WEIGHTS.items()))

    # ---- veto ----
    veto: List[Dict[str, Any]] = []
    if (content.get("stats", {}).get("body_text_chars", 0) or 0) < 100:
        veto.append({"code": "NO_CONTENT", "type": "block",
                     "message": "正文 <100 字（疑似 JS 渲染或反爬），无法评分"})
    if crawl_detail.get("blocked_verified_crawlers") == sum(1 for _, _, v in CRAWLERS if v):
        veto.append({"code": "CRAWLER_BLOCKED_ALL", "type": "cap60",
                     "message": "全部已核验 AI/搜索爬虫被 robots.txt 禁止，评分封顶 60"})
    cap = 60 if any(v["type"] == "cap60" for v in veto) else None
    if cap is not None:
        total = min(total, cap)

    result: Dict[str, Any] = {
        "tool": TOOL_NAME,
        "schema_version": SCHEMA_VERSION,
        "track": "onsite",
        "engine": None,
        "score": {"total": total, "cap": cap, "pillars": pillars,
                  "weights": COMPOSITE_WEIGHTS,
                  "rating": rating_of(total)},
        "detail": {"citability": cit_detail, "infra": infra_detail, "schema": schema_detail,
                   "authority": auth_detail, "crawl_llms": crawl_detail},
        "veto": veto,
        "evidence": content.get("evidence", {}),
        "sampling": None,
    }
    if args.stamp:
        import time
        result["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        try:
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(payload, encoding="utf-8")
        except OSError as e:
            print(f"[智引·站内评分] 落盘失败：{e}", file=sys.stderr)
            return 64
    if args.json or args.out:
        print(payload)
    else:
        p = pillars
        print(f"[智引·站内信号分] {total}/100（{rating_of(total)}）"
              + (f"，封顶 {cap}" if cap else ""))
        print(f"  可引用性 {p['citability']} | 技术基建 {p['infra']} | Schema {p['schema']} | "
              f"权威 {p['authority']} | 爬虫/llms.txt {p['crawl_llms']}")
        for v in veto:
            print(f"  ⚠ veto：{v['code']} — {v['message']}")

    if any(v["type"] == "block" for v in veto):
        return 2
    if cap is not None:
        return 1
    return 0


def rating_of(total: int) -> str:
    if total >= 90:
        return "优秀"
    if total >= 75:
        return "良好"
    if total >= 60:
        return "一般"
    if total >= 40:
        return "薄弱"
    return "近乎不可见"


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[智引·站内评分] 脚本异常：{type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(64)
