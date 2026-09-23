#!/usr/bin/env python3
"""内容可信度评分与转载独立性聚类（tri-wiki 门G · 阶段二）。

设计来源：参考项目的「质量分是持久属性而非临时判断」原则，落到知识库场景：
  - 多分量加权合成，权重集中于文件头常量，便于校准；
  - 缺失分量做重归一化（不因缺字段就把整篇判死）；
  - 硬地板：损坏/不可读/显式废弃的笔记直接压到地板值，不参与排序竞争；
  - 独立性聚类：转载/衍生稿聚成一簇，簇内只让最早者拿满分，其余按 1/size 计权。

分量（默认权重，可在文件头调整）：
  provenance 0.30  —— 来源可追溯性（有 source / 有原始格式 / 转换可溯源）
  integrity   0.20  —— 元数据完整性（frontmatter 必填字段覆盖率）
  substance   0.20  —— 正文信息量（有效字符数 + 结构度）
  linkage     0.15  —— 链接连通性（反向链接数）
  freshness   0.15  —— 时效（距 updated/created 的衰减）

用法：
    python credibility_score.py --kb-root <知识库根> --json
输出：`.wiki-meta/credibility.json` + stdout 摘要。仅依赖标准库。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---- 可调常量（校准入口）----
WEIGHTS = {
    "provenance": 0.30,
    "integrity": 0.20,
    "substance": 0.20,
    "linkage": 0.15,
    "freshness": 0.15,
}
REQUIRED_FIELDS = ["title", "type", "source", "source_format", "created"]
CREDIBILITY_FLOOR = 0.05      # 硬地板：损坏 / 显式废弃
SUBSTANCE_FULL_CHARS = 4000   # 达到即视为信息量满分
MIN_BODY_CHARS = 10           # 低于此值视为近乎空，压地板
INDEX_TYPES = {"index", "moc", "tags"}  # 导航页天然短，不参与「信息量」分量
FRESHNESS_HALF_LIFE_DAYS = 540  # 时效半衰期（约 18 个月）
DEFAULT_INDEPENDENCE_THRESHOLD = 0.70  # 转载判定 Jaccard 阈值
SHINGLE_N = 3
MIN_CLUSTER_CHARS = 200

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
WIKI_LINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:[#\|][^\]]*)?\]\]")
HEADING_RE = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("-"):
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip().strip("'\"")
    return fields


def body_of(text: str) -> str:
    return text[FRONTMATTER_RE.match(text).end():] if FRONTMATTER_RE.match(text) else text


def iter_notes(kb_root: Path):
    skip = {".git", ".obsidian", ".wiki-meta", "90-attachments"}
    for dirpath, dirnames, filenames in __import__("os").walk(kb_root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in sorted(filenames):
            if name.lower().endswith((".md", ".markdown")):
                yield Path(dirpath) / name


def age_days(date_str: str | None) -> float | None:
    if not date_str:
        return None
    m = DATE_RE.search(date_str)
    if not m:
        return None
    try:
        dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
    except ValueError:
        return None
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0)


def score_provenance(fm: dict) -> float | None:
    parts = []
    if fm.get("source"):
        parts.append(0.5)
    if fm.get("source_format"):
        parts.append(0.25)
    if fm.get("converter") or fm.get("split_from"):
        parts.append(0.25)
    if not parts:
        return None
    return min(1.0, sum(parts))


def score_integrity(fm: dict) -> float | None:
    if not fm:
        return None
    hit = sum(1 for f in REQUIRED_FIELDS if fm.get(f))
    return hit / len(REQUIRED_FIELDS)


def score_substance(body: str, note_type: str | None = None) -> float | None:
    """导航页（index/MOC/tags）天然短小 → 返回 None 走重归一化，NEVER 因此触地板。"""
    if note_type and note_type.strip().lower() in INDEX_TYPES:
        return None
    text = body.strip()
    if not text:
        return None
    length = len(text)
    if length < MIN_CLUSTER_CHARS:
        return None if length < MIN_BODY_CHARS else round(length / MIN_CLUSTER_CHARS * 0.3, 4)
    structure = min(1.0, len(HEADING_RE.findall(text)) / 5.0)
    length_score = min(1.0, math.log1p(length) / math.log1p(SUBSTANCE_FULL_CHARS))
    return round(0.7 * length_score + 0.3 * structure, 4)


def score_freshness(fm: dict) -> float | None:
    days = age_days(fm.get("updated") or fm.get("created"))
    if days is None:
        return None
    return round(0.5 ** (days / FRESHNESS_HALF_LIFE_DAYS), 4)


def shingle(text: str, n: int = SHINGLE_N) -> set:
    tokens = re.findall(r"\w+", text.lower())
    if len(tokens) < n:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cluster_derivatives(docs: list[dict], threshold: float) -> list[list[str]]:
    """转载/衍生稿聚类：并查集 + Jaccard 近重复。"""
    parent = {d["key"]: d["key"] for d in docs}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    sigs = {d["key"]: d["shingles"] for d in docs}
    keys = [d["key"] for d in docs]
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            if jaccard(sigs[keys[i]], sigs[keys[j]]) >= threshold:
                union(keys[i], keys[j])

    groups: dict[str, list[str]] = {}
    for k in keys:
        groups.setdefault(find(k), []).append(k)
    return [sorted(v) for v in groups.values() if len(v) > 1]


def main() -> int:
    ap = argparse.ArgumentParser(description="知识库内容可信度评分与转载聚类")
    ap.add_argument("--kb-root", required=True)
    ap.add_argument("--threshold", type=float, default=DEFAULT_INDEPENDENCE_THRESHOLD,
                    help=f"转载判定 Jaccard 阈值（默认 {DEFAULT_INDEPENDENCE_THRESHOLD}）")
    ap.add_argument("--no-cluster", action="store_true", help="跳过转载聚类（大库加速）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    kb_root = Path(args.kb_root).resolve()
    if not kb_root.is_dir():
        print(json.dumps({"ok": False, "error": f"知识库根不存在: {kb_root}",
                          "error_code": "KB_ROOT_MISSING"}, ensure_ascii=False))
        return 2

    docs, records = [], []
    for path in iter_notes(kb_root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        key = path.relative_to(kb_root).as_posix()
        fm = parse_frontmatter(text)
        body = body_of(text)
        docs.append({"key": key, "shingles": shingle(body)})
        records.append({"path": key, "fm": fm, "body": body})

    # 反向链接统计（链接连通性分量）
    inbound: dict[str, int] = {}
    for r in records:
        for target in WIKI_LINK_RE.findall(r["body"]):
            t = target.strip()
            inbound[t] = inbound.get(t, 0) + 1
    max_inbound = max(inbound.values()) if inbound else 1

    clusters = [] if args.no_cluster else cluster_derivatives(docs, args.threshold)
    cluster_of = {}
    for idx, group in enumerate(clusters):
        for member in group:
            cluster_of[member] = {"cluster_id": f"dup-{idx + 1:03d}", "size": len(group)}

    scored = []
    for r in records:
        key = r["path"]
        fm = r["fm"]
        title = fm.get("title") or key
        # 地板只给「彻底空」或「已显式废弃」两类，短小的导航页 NEVER 触地板
        broken = (fm.get("status") in ("deprecated", "archive")) or \
            len(r["body"].strip()) < MIN_BODY_CHARS
        raw = {
            "provenance": score_provenance(fm),
            "integrity": score_integrity(fm),
            "substance": score_substance(r["body"], fm.get("type")),
            "linkage": round(min(1.0, inbound.get(title, 0) / max_inbound), 4) if inbound else None,
            "freshness": score_freshness(fm),
        }
        present = {k: v for k, v in raw.items() if v is not None}
        if broken or not present:
            score = CREDIBILITY_FLOOR
            basis = "floor"
        else:
            wsum = sum(WEIGHTS[k] for k in present)
            score = sum(WEIGHTS[k] * v for k, v in present.items()) / wsum
            basis = "renormalized" if wsum < sum(WEIGHTS.values()) else "full"
        cl = cluster_of.get(key)
        if cl:
            score = round(score / cl["size"], 4)
        scored.append({
            "path": key,
            "title": title,
            "credibility": round(score, 4),
            "basis": basis,
            "components": {k: v for k, v in raw.items()},
            "missing_components": [k for k, v in raw.items() if v is None],
            "derivative_cluster": cl,
        })

    scored.sort(key=lambda x: (-x["credibility"], x["path"]))
    values = [s["credibility"] for s in scored]
    summary = {
        "note_count": len(scored),
        "mean": round(sum(values) / len(values), 4) if values else 0.0,
        "median": round(sorted(values)[len(values) // 2], 4) if values else 0.0,
        "floor_hits": sum(1 for s in scored if s["basis"] == "floor"),
        "derivative_clusters": len(clusters),
        "derivative_notes": sum(len(c) for c in clusters),
        "weights": WEIGHTS,
        "floor": CREDIBILITY_FLOOR,
    }

    out_dir = kb_root / ".wiki-meta"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "credibility.json"
    payload = {
        "ok": True,
        "generated_at": f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}",
        "threshold": args.threshold,
        "summary": summary,
        "notes": scored,
        "clusters": [{"cluster_id": f"dup-{i + 1:03d}", "members": g} for i, g in enumerate(clusters)],
    }
    tmp = out_path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    tmp.replace(out_path)

    if args.json:
        print(json.dumps({"ok": True, "summary": summary, "output": str(out_path)},
                         ensure_ascii=False, indent=2))
    else:
        s = summary
        print(f"笔记 {s['note_count']} 篇 | 均值 {s['mean']} | 中位 {s['median']} "
              f"| 触地板 {s['floor_hits']} | 转载簇 {s['derivative_clusters']}（{s['derivative_notes']} 篇）")
        print(f"报告：{out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
