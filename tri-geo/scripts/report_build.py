#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告渲染（report_build.py）——「智引」(tri-geo) 确定性脚本 09/09

职责（对应设计指南 §3.1 / §4.4）：
    · 把评分/判定/快照 JSON 渲染为 HTML 或 Markdown 报告
    · 每个分数 MUST 附带「产出脚本 + 证据路径 + 采样信息」（P3 评分来源规范落地）
    · 模板语法为 stdlib 子集（零第三方依赖）：
          {{KEY}}                    单值替换
          {{#LIST}} … {{/LIST}}      列表循环，块内 {{field}} 取当前项字段
      模板扩展名由 .j2 改为 .html（skillhub 平台拒绝 .j2 上传）；渲染仍由本脚本用标准库实现（NEVER 引入 Jinja2）

用法：
    python report_build.py --scores scores.json --brand 格力 --out 智引-格力-audit.html
    python report_build.py --scores scores.json --probe judge.json --format md --out report.md
    python report_build.py --scores scores.json --mode quick --out card.html

退出码：
    0  成功
    2  缺少必需入参数据
    64 参数或环境错误（模板缺失时自动降级 Markdown，不阻断）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = "1.0"
TOOL_NAME = "report_build.py"

PILLAR_NAMES = {
    "citability": "可引用性",
    "infra": "技术基建",
    "schema": "结构化数据",
    "authority": "权威信号",
    "crawl_llms": "爬虫与 llms.txt",
}
PILLAR_TOOL = {
    "citability": "site_signal.py",
    "infra": "site_signal.py",
    "schema": "site_signal.py",
    "authority": "site_signal.py",
    "crawl_llms": "site_signal.py",
}

BLOCK_RE = re.compile(r"\{\{#(\w+)\}\}\r?\n?(.*?)\{\{/\1\}\}\r?\n?", re.S)
VAR_RE = re.compile(r"\{\{(\w+)\}\}")


def render(tpl: str, ctx: Dict[str, Any]) -> str:
    """stdlib 子集渲染：先展开循环块，再替换单值。"""

    def repl_block(m: "re.Match[str]") -> str:
        name = m.group(1)
        body = m.group(2)
        items = ctx.get(name) or []
        parts = []
        for it in items:
            if isinstance(it, dict):
                merged = {**ctx, **it}
            else:
                merged = {**ctx, "item": it}
            parts.append(VAR_RE.sub(
                lambda mm: "" if merged.get(mm.group(1)) is None else str(merged.get(mm.group(1))),
                body))
        return "".join(parts)

    text = BLOCK_RE.sub(repl_block, tpl)
    return VAR_RE.sub(
        lambda mm: "" if ctx.get(mm.group(1)) is None else str(ctx.get(mm.group(1))),
        text)


def load_json_maybe(path: Optional[str]) -> Optional[Dict[str, Any]]:
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def build_context(args: argparse.Namespace, scores: Dict[str, Any],
                  probe: Optional[Dict[str, Any]],
                  delta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    score = scores.get("score") or {}
    pillars = score.get("pillars") or {}
    evidence = scores.get("evidence") or {}
    detail = scores.get("detail") or {}

    pillar_rows: List[Dict[str, Any]] = []
    for k, v in pillars.items():
        w = (score.get("weights") or {}).get(k)
        pillar_rows.append({
            "name": PILLAR_NAMES.get(k, k),
            "key": k,
            "score": v,
            "weight": f"{round((w or 0) * 100)}%",
            "tool": PILLAR_TOOL.get(k, "site_signal.py"),
        })

    # Top 修复项：按维度分从低到高（弱项优先）
    fixes: List[Dict[str, Any]] = []
    for row in sorted(pillar_rows, key=lambda r: (r["score"] if isinstance(r["score"], (int, float)) else 0)):
        if isinstance(row["score"], (int, float)) and row["score"] < 75:
            fixes.append({
                "item": f"提升「{row['name']}」（当前 {row['score']}/100）",
                "priority": "P0" if row["score"] < 50 else "P1",
                "basis": f"由 {row['tool']} 确定性计算，证据：{evidence.get('raw_path') or evidence.get('html_sha256') or '见快照'}",
            })

    probe_rows: List[Dict[str, Any]] = []
    if probe:
        for engine, agg in (probe.get("engines") or {}).items():
            probe_rows.append({
                "engine": engine,
                "rate": agg.get("mention_rate_pct"),
                "rounds": agg.get("rounds"),
                "interval": f"{agg.get('sampling', {}).get('ci_low')}-{agg.get('sampling', {}).get('ci_high')}%",
                "avg_rank": agg.get("avg_rank") or "-",
                "tool": "answer_judge.py",
            })

    veto_rows = [{"code": v.get("code"), "message": v.get("message")}
                 for v in (scores.get("veto") or [])]

    return {
        "brand": args.brand or "-",
        "date": args.date,
        "mode": args.mode,
        "total": score.get("total"),
        "rating": score.get("rating") or "-",
        "cap": score.get("cap") or "",
        "pillars": pillar_rows,
        "fixes": fixes,
        "probe_rows": probe_rows,
        "veto_rows": veto_rows,
        "evidence_path": evidence.get("raw_path") or "-",
        "html_sha256": evidence.get("html_sha256") or "-",
        "toolchain": "site_signal.py / answer_judge.py / snapshot.py",
        "delta_total": (delta or {}).get("total", {}).get("delta"),
        "delta_baseline": (delta or {}).get("baseline_date"),
        "delta_latest": (delta or {}).get("latest_date"),
        "coverage_above70": (detail.get("citability") or {}).get("coverage_above70"),
    }


def render_markdown(ctx: Dict[str, Any]) -> str:
    lines = [f"# 智引（tri-geo）GEO 诊断报告 — {ctx['brand']}", "",
             f"- 日期：{ctx['date']}", f"- 模式：{ctx['mode']}",
             f"- 站内信号分：**{ctx['total']}/100**（{ctx['rating']}）"
             + (f"，封顶 {ctx['cap']}" if ctx["cap"] else ""),
             f"- 评分来源：{ctx['toolchain']}；证据：{ctx['evidence_path']}",
             f"- 输入指纹：{ctx['html_sha256']}", ""]
    lines += ["## 维度得分", "", "| 维度 | 得分 | 权重 | 产出脚本 |", "|---|---|---|---|"]
    for r in ctx["pillars"]:
        lines.append(f"| {r['name']} | {r['score']} | {r['weight']} | {r['tool']} |")
    if ctx["probe_rows"]:
        lines += ["", "## 引擎实测（采样实测，非推演）", "",
                  "| 引擎 | 提及率 | 轮数 | 波动区间 | 平均位次 | 判定脚本 |", "|---|---|---|---|---|---|"]
        for r in ctx["probe_rows"]:
            lines.append(f"| {r['engine']} | {r['rate']}% | {r['rounds']} | {r['interval']} | "
                         f"{r['avg_rank']} | {r['tool']} |")
    if ctx["veto_rows"]:
        lines += ["", "## 一票否决", ""]
        for v in ctx["veto_rows"]:
            lines.append(f"- {v['code']}：{v['message']}")
    if ctx["fixes"]:
        lines += ["", "## 优先修复项", ""]
        for i, f in enumerate(ctx["fixes"][:5], 1):
            lines.append(f"{i}. [{f['priority']}] {f['item']}  ")
            lines.append(f"   依据：{f['basis']}")
    lines += ["", "> 本报告所有分数由确定性脚本计算产生，可经证据路径复核；"
                   "引用文献数字均标注测试环境与来源。"]
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="「智引」报告渲染（stdlib 子集模板）")
    ap.add_argument("--scores", required=True, help="site_signal.py 评分 JSON")
    ap.add_argument("--probe", default=None, help="answer_judge.py 判定 JSON")
    ap.add_argument("--delta", default=None, help="snapshot.py delta JSON")
    ap.add_argument("--brand", default=None)
    ap.add_argument("--mode", default="audit")
    ap.add_argument("--template", default=None, help="模板路径，默认按 mode 选取")
    ap.add_argument("--format", default="html", choices=["html", "md"])
    ap.add_argument("--date", default=None)
    ap.add_argument("--out", default=None, help="输出文件路径（默认 stdout）")
    args = ap.parse_args(argv)

    scores: Optional[Dict[str, Any]] = load_json_maybe(args.scores)
    if scores is None:
        print("[智引·报告] 缺少有效 --scores", file=sys.stderr)
        return 2
    probe = load_json_maybe(args.probe)
    delta = load_json_maybe(args.delta)

    if args.date is None:
        import time
        args.date = time.strftime("%Y-%m-%d")

    ctx = build_context(args, scores, probe, delta)

    text: str
    if args.format == "md":
        text = render_markdown(ctx)
    else:
        tpl_path = Path(args.template) if args.template else Path(
            __file__).resolve().parent.parent / "templates" / (
            "quick-card.html.j2" if args.mode == "quick" else "report.html.j2")
        if not tpl_path.is_file():
            print(f"[智引·报告] 模板缺失：{tpl_path}，降级 Markdown", file=sys.stderr)
            text = render_markdown(ctx)
        else:
            text = render(tpl_path.read_text(encoding="utf-8"), ctx)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(json.dumps({"tool": TOOL_NAME, "out": str(out), "format": args.format,
                          "brand": ctx["brand"], "total": ctx["total"]},
                         ensure_ascii=False, indent=2))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[智引·报告] 脚本异常：{type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(64)
