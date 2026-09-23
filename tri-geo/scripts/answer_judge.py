#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实测结果规则判定（answer_judge.py）——「智引」(tri-geo) 确定性脚本 07/09

职责（对应设计指南 §3.1 / §4.2）：
    · 对 probe_runner.py 落盘的原始回答做规则判定：品牌提及、引用位次、情感倾向
    · 每条判定附命中位置原文摘录（证据），判定 JSON 与原文件一一对应
    · 规则无法确定时标记 needs_llm_review，NEVER 猜测判定（LLM 兜底占比 >30% 需补规则）
    · 多轮采样汇总：提及率、位次集合、情感分布；波动区间由实测统计得出，不预设数值

设计约束：
    · 纯标准库；同输入逐字节一致
    · 判定口径以 references/scoring-spec.md §3 为准

用法：
    python answer_judge.py --probe-dir .geo-snapshots/格力/probe --brand 格力 \
        --aliases 格力电器,GREE --domains gree.com --json
    python answer_judge.py --probe-dir ... --brand 格力 --out judge.json --json

退出码：
    0  判定完成
    2  无有效回答文件（样本为空，NEVER 以 0 分冒充实测结果）
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
TOOL_NAME = "answer_judge.py"

POS_WORDS = ["推荐", "值得", "领先", "优秀", "可靠", "建议选择", "首选", "不错", "好评", "稳定"]
NEG_WORDS = ["不推荐", "不建议", "差评", "投诉", "质量差", "翻车", "谨慎", "避坑", "缺陷", "问题多"]
CITE_MARK_RE = re.compile(r"[\[［]\s*\d+\s*[\]］]|\((?:https?://[^)]+)\)|来源[:：]")
DOMAIN_RE = re.compile(r"https?://([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")

EXCERPT_PAD = 30


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def find_mentions(text: str, names: List[str]) -> List[Dict[str, Any]]:
    """品牌/别名提及命中（大小写不敏感，中文无需分词）。"""
    hits: List[Dict[str, Any]] = []
    low = text.lower()
    for n in names:
        if not n:
            continue
        nl = n.lower()
        start = 0
        while True:
            i = low.find(nl, start)
            if i < 0:
                break
            hits.append({"alias": n, "index": i,
                         "excerpt": text[max(0, i - EXCERPT_PAD): i + len(n) + EXCERPT_PAD]})
            start = i + len(nl)
            if len(hits) > 50:
                break
    hits.sort(key=lambda x: x["index"])
    return hits


def cite_rank(text: str, domains: List[str]) -> Optional[int]:
    """引用位次：按文本中出现的域名顺序取品牌域名首次出现的序号（1 起）。"""
    if not domains:
        return None
    found: List[str] = []
    for m in DOMAIN_RE.finditer(text):
        host = m.group(1).lower()
        if host not in found:
            found.append(host)
    if not found:
        return None
    for idx, host in enumerate(found, start=1):
        for d in domains:
            if d.lower().strip() and d.lower().strip() in host:
                return idx
    return None


def sentiment(text: str, mentions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """情感判定：以提及位置附近的窗口为主，全兜底用全文。"""
    window = text
    if mentions:
        i = mentions[0]["index"]
        window = text[max(0, i - 120): i + 240]
    pos = [w for w in POS_WORDS if w in window]
    neg = [w for w in NEG_WORDS if w in window]
    if pos and not neg:
        label = "positive"
    elif neg and not pos:
        label = "negative"
    elif pos and neg:
        label = "conflict"
    else:
        label = "neutral"
    return {"label": label, "pos_hits": pos, "neg_hits": neg,
            "ambiguous": label == "conflict"}


def judge_one(path: Path, brand: str, aliases: List[str],
              domains: List[str], source_type: Optional[str]) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    names = [brand] + [a for a in aliases if a and a != brand]
    mentions = find_mentions(text, names)
    rank = cite_rank(text, domains)
    sent = sentiment(text, mentions)
    needs_review = bool(sent["ambiguous"]) or (bool(mentions) and rank is None)
    return {
        "file": str(path),
        "engine": path.parent.name,
        "prompt_id": re.sub(r"-r\d+\.txt$", "", path.name),
        "round": int((re.search(r"-r(\d+)\.txt$", path.name) or [None, 0])[1] or 0),
        "source_type": source_type,
        "mentioned": bool(mentions),
        "mention_count": len(mentions),
        "citation_rank": rank,
        "sentiment": sent["label"],
        "evidence": mentions[:3],
        "judge": "rule" if not needs_review else "needs_llm_review",
        "chars": len(norm(text)),
    }


def aggregate(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {"rounds": 0, "mention_rate": None, "ranks": [], "sentiments": {},
                "sampling": {"rounds": 0, "note": "无有效样本"}}
    rounds = len(rows)
    mentioned = [1 if r["mentioned"] else 0 for r in rows]
    ranks = [r["citation_rank"] for r in rows if r["citation_rank"] is not None]
    sents: Dict[str, int] = {}
    for r in rows:
        sents[r["sentiment"]] = sents.get(r["sentiment"], 0) + 1
    rate = sum(mentioned) / rounds
    sampling = {
        "rounds": rounds,
        "values": mentioned,
        # 波动区间由实测统计得出（min/max），NEVER 预设数值（设计指南 §4.2）
        "ci_low": round(min(mentioned) * 100.0, 1),
        "ci_high": round(max(mentioned) * 100.0, 1),
        "method": "多轮采样实测 min/max，样本量不足时结果仅供参考",
    }
    return {
        "rounds": rounds,
        "mention_rate": round(rate, 3),
        "mention_rate_pct": round(rate * 100, 1),
        "ranks": ranks,
        "avg_rank": round(sum(ranks) / len(ranks), 2) if ranks else None,
        "sentiments": sents,
        "sampling": sampling,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="「智引」实测结果规则判定")
    ap.add_argument("--probe-dir", required=True, help="probe 根目录（含 <engine>/*.txt）")
    ap.add_argument("--brand", required=True, help="品牌名")
    ap.add_argument("--aliases", default=None, help="别名/英文名，逗号分隔")
    ap.add_argument("--domains", default=None, help="品牌自有域名，逗号分隔")
    ap.add_argument("--manifest", default=None, help="manifest.json 路径（取 source_type）")
    ap.add_argument("--out", default=None, help="判定 JSON 落盘路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    root = Path(args.probe_dir)
    if not root.is_dir():
        print(f"[智引·判定] probe 目录不存在：{root}", file=sys.stderr)
        return 64

    aliases = [a.strip() for a in (args.aliases or "").split(",") if a.strip()]
    domains = [d.strip() for d in (args.domains or "").split(",") if d.strip()]

    source_map: Dict[str, str] = {}
    mpath = Path(args.manifest) if args.manifest else root / "manifest.json"
    if mpath.is_file():
        try:
            man = json.loads(mpath.read_text(encoding="utf-8"))
            for t in man.get("tasks", []):
                if t.get("status") == "filled" and t.get("source_type"):
                    key = f"{t['engine']}/{re.sub(r'-r\\d+\\.txt$', '', Path(t['path']).name)}/{t['round']}"
                    source_map[key] = t["source_type"]
        except (OSError, json.JSONDecodeError):
            pass

    files = sorted([p for p in root.rglob("*.txt") if p.is_file()])
    rows = [judge_one(p, args.brand, aliases, domains,
                      source_map.get(f"{p.parent.name}/{re.sub(r'-r\\d+\\.txt$', '', p.name)}/"
                                     f"{(re.search(r'-r(\\d+)\\.txt$', p.name) or [None, 0])[1]}"))
            for p in files]

    by_engine: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        by_engine.setdefault(r["engine"], {"rows": []})["rows"].append(r)
    engines = {e: aggregate(v["rows"]) for e, v in by_engine.items()}

    needs = [r for r in rows if r["judge"] == "needs_llm_review"]
    result: Dict[str, Any] = {
        "tool": TOOL_NAME,
        "schema_version": SCHEMA_VERSION,
        "track": "probe",
        "brand": args.brand,
        "rows": rows,
        "engines": engines,
        "overall": aggregate(rows),
        "needs_llm_review": {"count": len(needs),
                             "ratio": round(len(needs) / len(rows), 3) if rows else 0.0,
                             "files": [r["file"] for r in needs][:10]},
        "note": "LLM 兜底占比 >30% 时 MUST 回头补规则，而非扩大兜底（设计指南 §3.2）",
    }

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(payload, encoding="utf-8")
    if args.json or args.out:
        print(payload)
    else:
        o = result["overall"]
        print(f"[智引·实测判定] 样本 {len(rows)} 条 / 引擎 {len(engines)} 个")
        for e, agg in engines.items():
            print(f"  {e}：提及率 {agg['mention_rate_pct']}% "
                  f"（{agg['rounds']} 轮，区间 {agg['sampling']['ci_low']}-{agg['sampling']['ci_high']}%）"
                  f" 平均位次 {agg['avg_rank']}")
        print(f"  存疑样本 {len(needs)} 条（{result['needs_llm_review']['ratio'] * 100:.1f}%）")

    if not rows:
        print("[智引·判定] 无有效回答文件，NEVER 以 0 分冒充实测结果", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[智引·判定] 脚本异常：{type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(64)
