#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
写作规范校验器（writing_rules.py）——「智引」(tri-geo) 确定性脚本 04/09

职责（对应设计指南 §3.1 / §4.1）：
    · 校验 LLM 重写稿是否达标：直答前置、直答段字数（120-200 字，初始工程值）、
      代词密度、统计密度配额、问句式标题、标题层级、列表/表格、来源声明
    · 反模式清除（空话套话词表）+ 广告法禁用语红线过滤
    · 产出 pass/fail + 打回原因清单，供「LLM 产出 → 脚本校验 → 打回/降级」闭环消费

设计约束：
    · 纯标准库；同输入逐字节一致
    · 红线命中（广告法禁用语）= 不通过且标记 redline，NEVER 降级放行
    · 字数按字符计（不含空白），设计指南 §6.1

用法：
    python writing_rules.py --file rewrite.md --target-query "GEO 是什么" --json
    python writing_rules.py --file rewrite.md --out rules.json --json

退出码：
    0  全部通过
    2  未通过（打回清单见 checks）→ LLM 最多重修 2 轮
    3  红线命中（广告法/合规）→ 打回，禁止发布
    64 参数或环境错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = "1.0"
TOOL_NAME = "writing_rules.py"

# 直答段字数区间（初始工程值，待 ai_probe 实测校准后于 geo-writing-zh.md 记录修订）
DIRECT_ANSWER_MIN = 120
DIRECT_ANSWER_MAX = 200
PRON_DENSITY_MAX = 0.02
STATS_PER_500_TARGET = 3.0

DEF_RE = re.compile(r"[^\s。！？；：，、]{2,24}(?:是|指的是|指|包括|定义为|即)\s")
Q_HEAD_RE = re.compile(r"(什么是|如何|怎么|哪些|为什么|多久|多少钱|哪个好|吗[？?]|？)")
PRON_RE = re.compile(r"[他她它其该此这那]")
PCT_RE = re.compile(r"\d+(?:\.\d+)?\s*%|百分之\s*\d+")
MONEY_RE = re.compile(r"[￥¥$]\s?\d+(?:\.\d+)?(?:万|亿|元)?|\d+(?:\.\d+)?\s?(?:万元|亿元|元|美元)")
YEAR_RE = re.compile(r"(?:19|20)\d{2}\s*年")
UNIT_RE = re.compile(r"\d+(?:\.\d+)?\s?(?:天|小时|分钟|秒|倍|人|家|款|台|件|次|万|亿|公斤|kg|ms|GB|MB)")
URL_RE = re.compile(r"https?://\S+")
SOURCE_HINT_RE = re.compile(r"(来源|资料来源|参考|据|报告显示|数据显示|研究表明|[（(]\s*https?://)")

# 空话套话（反模式）
FILLER_PATTERNS = [
    (r"随着[^，。]{0,12}的(?:发展|普及|到来)", "套话开头：随着…的发展"),
    (r"在当今[^，。]{0,12}", "套话开头：在当今…"),
    (r"在这个信息爆炸的时代", "套话：信息爆炸时代"),
    (r"众所周知|显而易见|不难看出|毋庸置疑", "无信息量过渡语"),
    (r"让我们一起|话不多说|直接进入正题", "口语化开场"),
    (r"总之|总而言之|综上所述", "空泛总结（应换为可引用结论）"),
    (r"需要注意的是|值得注意的是(?![:：])", "无信息量提示语"),
]

# 广告法禁用语（红线，命中即打回）
AD_LAW_PATTERNS = [
    (r"最好|最佳|最优|最强|最先进|最专业", "绝对化用语：最X"),
    (r"最高级|极品|极致|顶级|顶尖", "绝对化用语：极/顶级"),
    (r"第一品牌|全国第一|行业第一|排名第一|销量第一", "绝对化用语：第一"),
    (r"国家级|世界级|国际级", "权威化用语：国家级/世界级"),
    (r"首选|独一无二|绝无仅有|史无前例", "绝对化用语：首选/唯一"),
    (r"绝对|百分之百|100%有效|百分百", "绝对化承诺"),
    (r"永久|彻底治愈|根治|包治", "绝对化承诺：永久/根治"),
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def strip_code(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    return text


def split_blocks(md: str) -> List[Dict[str, Any]]:
    """按标题切块。返回 [{level, heading, text}]。"""
    blocks: List[Dict[str, Any]] = []
    cur = {"level": 0, "heading": "", "lines": []}
    for line in md.splitlines():
        m = HEADING_RE.match(line.strip())
        if m:
            if cur["lines"] or cur["heading"]:
                blocks.append({**cur, "text": "\n".join(cur["lines"]).strip()})
            cur = {"level": len(m.group(1)), "heading": m.group(2).strip(), "lines": []}
        else:
            cur["lines"].append(line)
    if cur["lines"] or cur["heading"]:
        blocks.append({**cur, "text": "\n".join(cur["lines"]).strip()})
    return blocks


def first_prose_paragraph(md: str) -> str:
    """首个实质段落（跳过标题与列表行）。"""
    for raw in md.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(("|", "-", "*", ">")):
            continue
        if len(re.sub(r"\s+", "", line)) < 20:
            continue
        return line
    return ""


def check_direct_answer(md: str, target_query: Optional[str]) -> Dict[str, Any]:
    para = first_prose_paragraph(md)
    head = re.sub(r"\s+", "", para)[:120]
    has_def = bool(DEF_RE.search(head))
    has_num = bool(re.search(r"\d", head))
    query_hit = True
    if target_query:
        keys = [k for k in re.split(r"[的\s是吗？?]", target_query) if len(k) >= 2]
        query_hit = bool(keys) and any(k in head for k in keys[:3])
    ok = (has_def or has_num) and query_hit
    return {"id": "R1", "name": "直答前置", "status": "pass" if ok else "fail",
            "detail": {"首段前120字": head[:120], "定义句式": has_def,
                       "含具体数字": has_num, "命中目标问题": query_hit}}


def check_answer_length(md: str) -> Dict[str, Any]:
    para = re.sub(r"\s+", "", first_prose_paragraph(md))
    n = len(para)
    if DIRECT_ANSWER_MIN <= n <= DIRECT_ANSWER_MAX:
        status, mark = "pass", 100
    elif 100 <= n < DIRECT_ANSWER_MIN or DIRECT_ANSWER_MAX < n <= 250:
        status, mark = "fail", 70
    else:
        status, mark = "fail", 30
    return {"id": "R2", "name": f"直答段字数 {DIRECT_ANSWER_MIN}-{DIRECT_ANSWER_MAX} 字",
            "status": status, "detail": {"字数": n, "得分": mark}}


def check_pronoun(md: str) -> Dict[str, Any]:
    body = strip_code(md)
    chars = len(re.sub(r"\s+", "", body))
    pron = len(PRON_RE.findall(body))
    density = (pron / chars) if chars else 0.0
    ok = density < PRON_DENSITY_MAX
    return {"id": "R3", "name": "代词密度 <2%", "status": "pass" if ok else "fail",
            "detail": {"代词数": pron, "字符数": chars, "密度": round(density, 4)}}


def check_stats(md: str) -> Dict[str, Any]:
    body = strip_code(md)
    chars = len(re.sub(r"\s+", "", body))
    count = (len(PCT_RE.findall(body)) + len(MONEY_RE.findall(body))
             + len(YEAR_RE.findall(body)) + len(UNIT_RE.findall(body)))
    per500 = (count / (chars / 500)) if chars >= 100 else float(count)
    ok = per500 >= STATS_PER_500_TARGET
    return {"id": "R4", "name": f"统计密度 ≥{STATS_PER_500_TARGET} 个/500字",
            "status": "pass" if ok else "fail",
            "detail": {"统计点": count, "每500字": round(per500, 2)}}


def check_question_heading(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    hit = [b["heading"] for b in blocks if Q_HEAD_RE.search(b.get("heading", ""))]
    return {"id": "R5", "name": "存在问句式小标题", "status": "pass" if hit else "fail",
            "detail": {"命中": hit[:5]}}


def check_heading_levels(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    levels = [b["level"] for b in blocks if b.get("level")]
    skip = [(a, b) for a, b in zip(levels, levels[1:]) if b - a > 1]
    return {"id": "R6", "name": "标题层级不跳级", "status": "pass" if not skip else "fail",
            "detail": {"跳级": skip[:5]}}


def check_structure_md(md: str) -> Dict[str, Any]:
    lists = len(re.findall(r"(?m)^\s*(?:[-*+]|\d+\.)\s+\S", md))
    tables = len(re.findall(r"(?m)^\s*\|.*\|\s*$", md))
    ok = (lists + tables) >= 2
    return {"id": "R7", "name": "列表/表格结构化", "status": "pass" if ok else "fail",
            "detail": {"列表": lists, "表格行": tables}}


def check_filler(md: str) -> Dict[str, Any]:
    body = strip_code(md)
    hits = []
    for pat, desc in FILLER_PATTERNS:
        m = re.search(pat, body)
        if m:
            hits.append({"pattern": desc, "sample": m.group(0)})
    return {"id": "R8", "name": "反模式（空话套话）", "status": "pass" if not hits else "fail",
            "detail": {"命中": hits}}


def check_ad_law(md: str) -> Dict[str, Any]:
    body = strip_code(md)
    hits = []
    for pat, desc in AD_LAW_PATTERNS:
        for m in re.finditer(pat, body):
            hits.append({"pattern": desc, "sample": m.group(0)})
    return {"id": "R9", "name": "广告法禁用语（红线）", "status": "pass" if not hits else "fail",
            "redline": bool(hits), "detail": {"命中": hits[:10], "命中数": len(hits)}}


def check_source_declaration(md: str) -> Dict[str, Any]:
    paras = [p for p in re.split(r"\n\s*\n", strip_code(md)) if p.strip()]
    risky = []
    for p in paras:
        has_num = bool(re.search(r"\d+(?:\.\d+)?\s*%|(?:19|20)\d{2}\s*年|研究表明|数据显示|统计显示", p))
        has_src = bool(URL_RE.search(p) or SOURCE_HINT_RE.search(p))
        if has_num and not has_src:
            risky.append(re.sub(r"\s+", " ", p)[:80])
    return {"id": "R10", "name": "数据句附来源声明", "status": "pass" if not risky else "fail",
            "detail": {"无来源数据段": risky[:5], "数量": len(risky)}}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="「智引」重写稿写作规范校验（打回器）")
    ap.add_argument("--file", required=True, help="重写稿 Markdown 路径")
    ap.add_argument("--target-query", default=None, help="目标问题（校验直答是否对应）")
    ap.add_argument("--out", default=None, help="校验 JSON 落盘路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    p = Path(args.file)
    if not p.is_file():
        print(f"[智引·写作校验] 文件不存在：{p}", file=sys.stderr)
        return 64
    md = p.read_text(encoding="utf-8", errors="replace")
    blocks = split_blocks(md)

    checks = [
        check_direct_answer(md, args.target_query),
        check_answer_length(md),
        check_pronoun(md),
        check_stats(md),
        check_question_heading(blocks),
        check_heading_levels(blocks),
        check_structure_md(md),
        check_filler(md),
        check_ad_law(md),
        check_source_declaration(md),
    ]
    failed = [c for c in checks if c["status"] == "fail"]
    redlines = [c for c in checks if c.get("redline")]
    ok = not failed

    result: Dict[str, Any] = {
        "tool": TOOL_NAME,
        "schema_version": SCHEMA_VERSION,
        "file": str(p),
        "pass": ok,
        "checks": checks,
        "redline_hit": bool(redlines),
        "fixes": [f"{c['id']} {c['name']}：{json.dumps(c['detail'], ensure_ascii=False)}"
                  for c in failed],
        "next_action": "proceed" if ok else ("reject_redline" if redlines else "revise"),
    }

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(payload, encoding="utf-8")
    if args.json or args.out:
        print(payload)
    else:
        tag = "通过" if ok else ("红线命中·打回" if redlines else "未通过·打回")
        print(f"[智引·写作校验] {tag}（{len(checks) - len(failed)}/{len(checks)} 项通过）")
        for c in failed:
            print(f"  ✗ {c['id']} {c['name']} — {json.dumps(c['detail'], ensure_ascii=False)[:160]}")
        if redlines:
            print("  红线：广告法禁用语命中，禁止发布，必须改写后重跑")

    if redlines:
        return 3
    return 0 if ok else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[智引·写作校验] 脚本异常：{type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(64)
