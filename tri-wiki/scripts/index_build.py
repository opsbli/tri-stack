#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-wiki 门E：index/MOC/tags 生成与断链检测。

仅用 Python 标准库。输入 moc-plan.json（Agent 生成、确认门③ 批复后的 MOC 与链接建议），
确定性执行生成。模板唯一真源：references/output-structure-spec.md。

用法：
    python index_build.py --kb-root <知识库根> [--moc-plan <moc-plan.json>] --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def parse_frontmatter(text: str):
    fm = {}
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if m:
        cur_key = None
        for line in m.group(1).splitlines():
            mm = re.match(r"^([A-Za-z_][\w]*)\s*:\s*(.*)$", line.strip())
            li = re.match(r"^-\s+(.*)$", line.strip())
            if mm:
                cur_key = mm.group(1)
                fm[cur_key] = mm.group(2).strip()
            elif li and cur_key:
                if not isinstance(fm[cur_key], list):
                    fm[cur_key] = [] if not fm[cur_key] else [fm[cur_key]]
                fm[cur_key].append(li.group(1).strip())
    return fm


def list_docs(kb_root: Path):
    docs = []
    for md in sorted(kb_root.rglob("*.md")):
        rel = md.relative_to(kb_root)
        if rel.parts[0] in {".wiki-meta",}:
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        docs.append({"path": md, "rel": str(rel), "fm": fm, "text": text,
                     "links": LINK_RE.findall(text)})
    return docs


def as_list(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip().strip("'\"") for x in str(v or "").strip("[]").split(",") if x.strip()]


def build_name_index(docs):
    idx = {}
    for d in docs:
        idx[d["path"].stem] = str(d["rel"])
        for a in as_list(d["fm"].get("aliases")):
            if a:
                idx.setdefault(a, str(d["rel"]))
    return idx


def gen_index(kb_root: Path, docs, mocs):
    lines = ["---", "title: %s 知识库" % kb_root.name, "type: index",
             "source: tri-wiki generated", "source_format: md",
             "created: %s" % datetime.now().strftime("%Y-%m-%d"),
             "tags: [MOC]", "status: seedling", "---", "",
             "# %s 知识库" % kb_root.name, "",
             "> 由 tri-wiki 于 %s 构建 · 共 %d 篇笔记 · %d 个主题" % (
                 datetime.now().strftime("%Y-%m-%d"), len(docs), len(mocs)), "",
             "## 主题导航", ""]
    for m in mocs:
        cnt = sum(1 for d in docs if d["rel"].startswith(m["topic"] + "/") and d["fm"].get("type") == "doc")
        lines.append("- [[%s-MOC|%s]]（%d 篇）" % (m["topic"], m["topic"], cnt))
    lines += ["", "## 使用指引", "",
              "- 用 Obsidian 打开本目录即可获得图谱/反向链接/全文搜索",
              "- 发布为站点：Quartz / MkDocs Material（命令见 build-report.md）",
              "- RAG 接入：chunks.jsonl 语料（若启用 --rag）", ""]
    (kb_root / "index.md").write_text("\n".join(lines), encoding="utf-8")


def gen_mocs(kb_root: Path, docs, moc_plan):
    mocs = moc_plan.get("mocs", [])
    for m in mocs:
        topic = m["topic"]
        topic_dir = kb_root / topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        entries = []
        for d in docs:
            if d["rel"].startswith(topic + "/") and d["fm"].get("type") == "doc":
                desc = m.get("descriptions", {}).get(d["path"].stem, d["fm"].get("title", d["path"].stem))
                entries.append("- [[%s]] — %s" % (d["path"].stem, desc))
        lines = ["---", "title: %s MOC" % topic, "type: moc",
                 "source: tri-wiki generated", "source_format: md",
                 "created: %s" % datetime.now().strftime("%Y-%m-%d"),
                 "tags: [%s, MOC]" % topic, "status: seedling", "---", "",
                 "# %s · 内容地图" % topic, "",
                 "> %s" % m.get("description", ""), "", "## 条目", ""]
        lines.extend(entries or ["-（暂无条目）"])
        if m.get("related"):
            lines += ["", "## 相关主题", ""]
            lines.extend("- [[%s-MOC]]：%s" % (r["topic"], r.get("note", "")) for r in m["related"])
        lines.append("")
        (kb_root / topic / f"{topic}-MOC.md").write_text("\n".join(lines), encoding="utf-8")
    return mocs


def gen_tags(kb_root: Path, docs):
    tag_map = defaultdict(list)
    for d in docs:
        for t in as_list(d["fm"].get("tags")):
            if t:
                tag_map[t].append(d["path"].stem)
    lines = ["---", "title: 标签索引", "type: moc", "source: tri-wiki generated",
             "source_format: md", "created: %s" % datetime.now().strftime("%Y-%m-%d"),
             "tags: [MOC]", "---", "", "# 标签索引", ""]
    for t in sorted(tag_map):
        lines.append("## %s（%d 篇）" % (t, len(tag_map[t])))
        lines.append("")
        lines.append("- " + " / ".join("[[%s]]" % n for n in sorted(tag_map[t])))
        lines.append("")
    (kb_root / "tags.md").write_text("\n".join(lines), encoding="utf-8")
    return tag_map


def check_links(kb_root: Path):
    docs = list_docs(kb_root)
    name_idx = build_name_index(docs)
    total, broken = 0, []
    for d in docs:
        for target in d["links"]:
            total += 1
            t = target.strip()
            if t and t not in name_idx and not (kb_root / (t + ".md")).is_file():
                broken.append({"from": str(d["rel"]), "target": t})
    density = round(total / max(1, sum(1 for d in docs if d["fm"].get("type") == "doc")), 3)
    return {"total_links": total, "broken": broken, "broken_rate": round(len(broken) / total, 4) if total else 0.0,
            "link_density": density, "doc_count": len(docs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb-root", required=True)
    ap.add_argument("--moc-plan", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    kb_root = Path(args.kb_root)
    moc_plan = {}
    if args.moc_plan and Path(args.moc_plan).is_file():
        moc_plan = json.loads(Path(args.moc_plan).read_text(encoding="utf-8-sig"))

    docs = list_docs(kb_root)
    mocs = gen_mocs(kb_root, docs, moc_plan)
    gen_index(kb_root, docs, mocs)
    tag_map = gen_tags(kb_root, docs)
    links = check_links(kb_root)

    result = {"generated_at": datetime.now().isoformat(timespec="seconds"),
              "kb_root": str(kb_root), "doc_count": len(docs),
              "moc_count": len(mocs), "topics": [m["topic"] for m in mocs],
              "tag_count": len(tag_map), "links": links}
    out_dir = Path(args.out) if args.out else Path(".tribro") / "wiki"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"索引完成：{len(docs)} 篇笔记 / {len(mocs)} 个 MOC / {len(tag_map)} 个标签；"
              f"链接 {links['total_links']} 条（断链 {len(links['broken'])}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
