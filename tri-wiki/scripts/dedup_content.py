#!/usr/bin/env python3
"""内容级深度去重（tri-wiki 门B 增强 · 门G 复用）。

补的缺口：v1 的去重标记只覆盖「直通类」源（.md/.txt 等），转换产物（PDF/Word 转出的
markdown）明确「转换后不回溯去重」，导致同一份文档的不同格式副本会重复入库。
本脚本在**知识库产物侧**做内容级去重，与源格式无关，因此可以覆盖转换产物。

算法（分层，与参考项目同构）：
  - 小库（≤ lsh-threshold 篇）：shingle(n) + Jaccard 全对比，精确；
  - 大库（> lsh-threshold 篇）：minhash 签名 + LSH 分桶先筛候选，再对候选精确比对，
    把 O(n²) 压到近似线性。

用法：
    python dedup_content.py --kb-root <知识库根> [--threshold 0.7] [--shingle 3] --json
    python dedup_content.py --kb-root <知识库根> --apply     # 把簇标记写入 frontmatter
输出：`.wiki-meta/dedup-report.json`。仅依赖标准库。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

DEFAULT_THRESHOLD = 0.70
DEFAULT_SHINGLE_N = 3
DEFAULT_LSW_THRESHOLD = 200   # 超过此篇数启用 minhash+LSH
NUM_HASHES = 64
BAND_ROWS = 4                 # 64 / 4 = 16 个 band

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
SKIP_DIRS = {".git", ".obsidian", ".wiki-meta", "90-attachments"}


def iter_notes(kb_root: Path):
    import os
    for dirpath, dirnames, filenames in os.walk(kb_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            if name.lower().endswith((".md", ".markdown")):
                yield Path(dirpath) / name


def body_of(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return text[m.end():] if m else text


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("-"):
            k, _, v = line.partition(":")
            fields[k.strip()] = v.strip().strip("'\"")
    return fields


def tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def shingles(text: str, n: int) -> set[str]:
    tk = tokens(text)
    if len(tk) < n:
        return {" ".join(tk)} if tk else set()
    return {" ".join(tk[i:i + n]) for i in range(len(tk) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter)


def minhash_signature(sh: set[str], num_perm: int = NUM_HASHES) -> list[int]:
    """确定性 minhash：用 sha1(seed+shingle) 模拟哈希函数，保证跨运行可复现。"""
    sig = []
    for seed in range(num_perm):
        best = None
        for s in sh:
            h = int(hashlib.sha1(f"{seed}:{s}".encode("utf-8")).hexdigest()[:12], 16)
            if best is None or h < best:
                best = h
        sig.append(best if best is not None else 0)
    return sig


def lsh_candidates(sigs: dict[str, list[int]]) -> set[tuple[str, str]]:
    buckets: dict[tuple, list[str]] = {}
    for key, sig in sigs.items():
        for band in range(0, len(sig), BAND_ROWS):
            chunk = tuple(sig[band:band + BAND_ROWS])
            buckets.setdefault((band, chunk), []).append(key)
    pairs: set[tuple[str, str]] = set()
    for members in buckets.values():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                pairs.add(tuple(sorted((members[i], members[j]))))
    return pairs


def main() -> int:
    ap = argparse.ArgumentParser(description="知识库内容级深度去重")
    ap.add_argument("--kb-root", required=True)
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ap.add_argument("--shingle", type=int, default=DEFAULT_SHINGLE_N)
    ap.add_argument("--lsh-threshold", type=int, default=DEFAULT_LSW_THRESHOLD,
                    help=f"篇数超过此值启用 minhash+LSH（默认 {DEFAULT_LSW_THRESHOLD}）")
    ap.add_argument("--apply", action="store_true",
                    help="把 dup_group 写回 frontmatter（只作用于知识库产物，不触碰源数据）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    kb_root = Path(args.kb_root).resolve()
    if not kb_root.is_dir():
        print(json.dumps({"ok": False, "error": f"知识库根不存在: {kb_root}",
                          "error_code": "KB_ROOT_MISSING"}, ensure_ascii=False))
        return 2

    docs = {}
    raws = {}
    for path in iter_notes(kb_root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        key = path.relative_to(kb_root).as_posix()
        docs[key] = shingles(body_of(text), args.shingle)
        raws[key] = text

    keys = sorted(docs)
    use_lsh = len(keys) > args.lsh_threshold
    cand: list[tuple[str, str]]
    if use_lsh:
        sigs = {k: minhash_signature(docs[k]) for k in keys}
        cand = sorted(lsh_candidates(sigs))
    else:
        cand = [(keys[i], keys[j]) for i in range(len(keys)) for j in range(i + 1, len(keys))]

    pairs = []
    for a, b in cand:
        sim = jaccard(docs.get(a, set()), docs.get(b, set()))
        if sim >= args.threshold:
            pairs.append({"a": a, "b": b, "similarity": round(sim, 4)})

    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for p in pairs:
        union(p["a"], p["b"])

    groups: dict[str, list[str]] = {}
    for k in keys:
        groups.setdefault(find(k), []).append(k)
    clusters = []
    for idx, (root, members) in enumerate(sorted(groups.items())):
        if len(members) < 2:
            continue
        members = sorted(members)
        keep = members[0]  # 保留最早（按路径序，稳定）
        clusters.append({
            "cluster_id": f"dup-{idx + 1:03d}",
            "members": members,
            "suggested_keep": keep,
            "suggested_flag": [m for m in members if m != keep],
        })

    applied = 0
    if args.apply:
        for cl in clusters:
            for member in cl["members"]:
                path = kb_root / member
                text = raws.get(member, "")
                if not text:
                    continue
                m = FRONTMATTER_RE.match(text)
                if not m:
                    continue
                block = m.group(1)
                if re.search(r"^dup_group:", block, re.MULTILINE):
                    continue
                new_block = f"{block.rstrip()}\ndup_group: {cl['cluster_id']}\n"
                new_text = f"---\n{new_block}---\n{text[m.end():]}"
                path.write_text(new_text, encoding="utf-8")
                applied += 1

    out_dir = kb_root / ".wiki-meta"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "dedup-report.json"
    payload = {
        "ok": True,
        "kb_root": str(kb_root),
        "note_count": len(keys),
        "mode": "minhash+lsh" if use_lsh else "exact-jaccard",
        "threshold": args.threshold,
        "shingle_n": args.shingle,
        "pairs": pairs,
        "clusters": clusters,
        "cluster_count": len(clusters),
        "redundant_count": sum(len(c["members"]) - 1 for c in clusters),
        "applied_frontmatter": applied,
    }
    tmp = out_path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    tmp.replace(out_path)

    if args.json:
        print(json.dumps({"ok": True, "note_count": payload["note_count"],
                          "mode": payload["mode"], "cluster_count": payload["cluster_count"],
                          "redundant_count": payload["redundant_count"],
                          "applied_frontmatter": applied,
                          "output": str(out_path)}, ensure_ascii=False, indent=2))
    else:
        print(f"笔记 {payload['note_count']} 篇 | 模式 {payload['mode']} "
              f"| 近重复簇 {payload['cluster_count']} | 冗余 {payload['redundant_count']} 篇 "
              f"| 已标记 {applied}")
        print(f"报告：{out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
