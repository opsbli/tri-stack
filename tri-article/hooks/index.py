#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tri-article 文章索引与去重辅助脚本（纯标准库，无第三方依赖）。

职责：维护 {{ARTICLES_ROOT}}/index.json 单一事实源，支撑「便于搜索去重」的存储结构：
  .tribro/article/articles/
    ├── index.json
    └── <domain-slug>/<YYYYMMDD>-<slug>.md

子命令：
  dedup   --title "..." --domain "..."           检查是否重复（硬/软）
  add    --title "..." --domain "..." --slug "..." --tags "a/b" --path "..."
  search [--domain X] [--tag Y] [--keyword Z]    过滤检索
  list                                             列出全量

用法示例：
  python index.py dedup --title "Electron 桌面开发的 3 个坑" --domain "electron-desktop"
  python index.py add --title "..." --domain "electron-desktop" --slug "electron-3-pits" \
        --tags "Electron/性能优化" --path "articles/electron-desktop/20260801-electron-3-pits.md"
"""
import argparse
import hashlib
import json
import os
import re
import sys

DEFAULT_ROOT = os.path.join(".tribro", "article", "articles")
INDEX_FILE = "index.json"
SOFT_DISTANCE = 2  # 同领域 slug 编辑距离阈值，≤2 视为软重复


def load_index(root):
    path = os.path.join(root, INDEX_FILE)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (ValueError, OSError):
        return []


def save_index(root, records):
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, INDEX_FILE)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)


def normalize_title(title):
    t = (title or "").lower()
    t = re.sub(r"[^\w\u4e00-\u9fff]+", " ", t, flags=re.UNICODE)
    return re.sub(r"\s+", " ", t).strip()


def title_hash(title):
    return hashlib.sha256(normalize_title(title).encode("utf-8")).hexdigest()


def slugify(text):
    t = (text or "").lower().strip()
    t = re.sub(r"[^\w\u4e00-\u9fff]+", "-", t, flags=re.UNICODE)
    return re.sub(r"-+", "-", t).strip("-")


def edit_distance(a, b):
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[lb]


def cmd_dedup(args):
    root = args.root
    th = title_hash(args.title)
    domain = slugify(args.domain) if args.domain else ""
    records = load_index(root)
    hard = [r for r in records if r.get("title_hash") == th]
    soft = []
    if domain:
        for r in records:
            if r.get("domain") == domain and r.get("slug"):
                if edit_distance(r["slug"], slugify(args.slug or "")) <= SOFT_DISTANCE:
                    soft.append(r)
    level = "hard" if hard else ("soft" if soft else "none")
    result = {
        "duplicate": bool(hard or soft),
        "level": level,
        "hard": [{"title": r.get("title"), "path": r.get("path")} for r in hard],
        "soft": [{"title": r.get("title"), "path": r.get("path")} for r in soft],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if hard else 0


def cmd_add(args):
    root = args.root
    records = load_index(root)
    domain = slugify(args.domain) if args.domain else ""
    slug = args.slug or slugify(args.title)
    rec = {
        "id": slug,
        "title": args.title,
        "slug": slug,
        "domain": domain,
        "tags": [t for t in (args.tags or "").split("/") if t],
        "created_at": args.created_at or "",
        "title_norm": normalize_title(args.title),
        "title_hash": title_hash(args.title),
        "content_hash": args.content_hash or "",
        "path": args.path or "",
        "status": args.status or "done",
    }
    # 同 (slug, domain) 视为同一篇文章的覆盖更新，原地替换而非追加，避免索引随覆盖重复增长
    replaced = False
    for i, r in enumerate(records):
        if r.get("slug") == slug and r.get("domain") == domain:
            records[i] = rec
            replaced = True
            break
    if not replaced:
        records.append(rec)
    save_index_file = os.path.join(root, INDEX_FILE)
    os.makedirs(root, exist_ok=True)
    with open(save_index_file, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0


def cmd_search(args):
    root = args.root
    records = load_index(root)
    kw = (args.keyword or "").lower()
    out = []
    for r in records:
        if args.domain and r.get("domain") != slugify(args.domain):
            continue
        if args.tag:
            tags = [t.lower() for t in r.get("tags", [])]
            if args.tag.lower() not in tags:
                continue
        if kw and kw not in (r.get("title") or "").lower():
            continue
        out.append(r)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args):
    records = load_index(args.root)
    print(json.dumps(records, ensure_ascii=False, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser(description="tri-article 文章索引与去重辅助")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="ARTICLES_ROOT，默认 .tribro/article/articles")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_d = sub.add_parser("dedup", help="检查标题/领域是否重复")
    p_d.add_argument("--title", required=True)
    p_d.add_argument("--domain", default="")
    p_d.add_argument("--slug", default="")
    p_d.set_defaults(func=cmd_dedup)

    p_a = sub.add_parser("add", help="追加一条索引记录")
    p_a.add_argument("--title", required=True)
    p_a.add_argument("--domain", default="")
    p_a.add_argument("--slug", default="")
    p_a.add_argument("--tags", default="")
    p_a.add_argument("--path", default="")
    p_a.add_argument("--created_at", default="")
    p_a.add_argument("--content_hash", default="")
    p_a.add_argument("--status", default="done")
    p_a.set_defaults(func=cmd_add)

    p_s = sub.add_parser("search", help="过滤检索")
    p_s.add_argument("--domain", default="")
    p_s.add_argument("--tag", default="")
    p_s.add_argument("--keyword", default="")
    p_s.set_defaults(func=cmd_search)

    p_l = sub.add_parser("list", help="列出全量")
    p_l.set_defaults(func=cmd_list)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
