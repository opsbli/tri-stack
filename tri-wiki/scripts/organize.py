#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-wiki 门D：frontmatter 注入、命名规范重写、目录归置、大文档原子化拆分。

仅用 Python 标准库。输入 classify-plan.json（Agent 生成、确认门② 批复后的归置清单），
确定性执行落盘。字段规范唯一真源：references/frontmatter-spec.md。

用法：
    python organize.py --kb-root <知识库根> --plan <classify-plan.json> [--split-chars 8000] --json
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_FIELDS = ["title", "type", "source", "source_format", "created"]
ATTACH_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}
INVALID_FS = r'[\\/:*?"<>|]'


def parse_frontmatter(text: str):
    fm, body = {}, text
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            mm = re.match(r"^([A-Za-z_][\w]*)\s*:\s*(.*)$", line.strip())
            if mm:
                val = mm.group(2).strip()
                if val.startswith("[") and val.endswith("]"):
                    val = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
                fm[mm.group(1)] = val
    return fm, body


def dump_frontmatter(fm: dict) -> str:
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            if v:
                lines.append(f"{k}:")
                lines.extend(f"  - {x}" for x in v)
            else:
                lines.append(f"{k}: []")
        else:
            v = str(v)
            if ":" in v or "#" in v or v.startswith(("'", '"')):
                v = v.replace('"', "'")
                v = f'"{v}"'
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def sanitize(name: str, maxlen: int = 80) -> str:
    name = re.sub(INVALID_FS, "-", name).strip().strip(".")
    return name[:maxlen].rstrip() or "untitled"


def split_large(body: str, threshold: int):
    if len(body) <= threshold:
        return None
    parts = re.split(r"(?m)^(?=## )", body)
    if len(parts) <= 1:
        return None
    chunks, cur, cur_len = [], [], 0
    for p in parts:
        if cur and cur_len + len(p) > threshold:
            chunks.append("".join(cur))
            cur, cur_len = [], 0
        cur.append(p)
        cur_len += len(p)
    if cur:
        chunks.append("".join(cur))
    return [c for c in chunks if c.strip()]


def organize(kb_root: Path, plan: dict, split_chars: int):
    inbox = kb_root / "00-Inbox"
    att = kb_root / "90-attachments"
    meta = kb_root / ".wiki-meta"
    for d in (inbox, att, meta):
        d.mkdir(parents=True, exist_ok=True)

    kb_name = plan.get("kb_name", kb_root.name)
    results, manifest = [], []
    for item in plan.get("files", []):
        src = Path(item["src"])
        topic = item.get("dest_topic") or "00-Inbox"
        title = sanitize(item.get("title") or src.stem)
        tags = item.get("tags") or []
        src_fmt = item.get("source_format") or src.suffix.lower().lstrip(".")
        rec = {"src": str(src), "dest": None, "split_children": [], "status": "ok", "error": None}

        if not src.is_file():
            rec["status"], rec["error"] = "failed", "source_missing"
            results.append(rec)
            continue
        try:
            text = src.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            rec["status"], rec["error"] = "failed", f"read_error:{e}"
            results.append(rec)
            continue

        fm, body = parse_frontmatter(text)
        fm.setdefault("title", title)
        fm["type"] = "doc"
        fm["source"] = str(src.resolve())
        fm["source_format"] = src_fmt
        fm.setdefault("created", datetime.now().strftime("%Y-%m-%d"))
        if tags:
            fm["tags"] = tags
        fm.setdefault("status", "seedling")
        fm.setdefault("kb", kb_name)

        topic_dir = kb_root / topic if topic != "00-Inbox" else inbox
        topic_dir.mkdir(parents=True, exist_ok=True)

        chunks = split_large(body, split_chars)
        if chunks:
            parent = topic_dir / f"{title}.md"
            toc_lines = [f"# {title}\n"]
            for i, ch in enumerate(chunks, 1):
                hm = re.match(r"^##\s+(.+)$", ch.strip().splitlines()[0]) if ch.strip() else None
                sub_title = sanitize(hm.group(1)) if hm else f"part{i:02d}"
                sub_name = f"{title}-{i:02d}-{sub_title}"
                sub_fm = dict(fm)
                sub_fm["title"] = f"{title} · {sub_title}"
                sub_fm["split_from"] = f"{title}.md"
                sub_path = topic_dir / f"{sub_name}.md"
                sub_path.write_text(dump_frontmatter(sub_fm) + "\n" + ch, encoding="utf-8")
                rec["split_children"].append(sub_path.name)
                manifest.append({"src": str(src), "dest": str(sub_path)})
                toc_lines.append(f"- [[{sub_name}|{sub_title}]]")
            parent.write_text(dump_frontmatter(fm) + "\n" + "\n".join(toc_lines) + "\n", encoding="utf-8")
            rec["dest"] = str(parent)
            manifest.append({"src": str(src), "dest": str(parent)})
        else:
            dest = topic_dir / f"{title}.md"
            n = 1
            while dest.exists():
                dest = topic_dir / f"{title}-{n}.md"
                n += 1
            dest.write_text(dump_frontmatter(fm) + "\n" + body, encoding="utf-8")
            rec["dest"] = str(dest)
            manifest.append({"src": str(src), "dest": str(dest)})

        # 附件归置：与源 md 同级的 assets 图片复制到 90-attachments 并重写引用
        src_assets = src.parent / "assets"
        if src_assets.is_dir():
            for img in src_assets.iterdir():
                if img.suffix.lower() in ATTACH_EXTS:
                    target = att / img.name
                    if not target.exists():
                        shutil.copy2(img, target)
            if rec["dest"]:
                p = Path(rec["dest"])
                txt = p.read_text(encoding="utf-8")
                txt2 = re.sub(r"(\]\()[^)]*?assets/([^)/]+\))", rf"\1../90-attachments/\2", txt)
                if txt2 != txt:
                    p.write_text(txt2, encoding="utf-8")
        results.append(rec)

    (meta / "build-manifest.json").write_text(
        json.dumps({"generated_at": datetime.now().isoformat(timespec="seconds"),
                    "entries": manifest}, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = sum(1 for r in results if r["status"] == "ok")
    return {"kb_root": str(kb_root), "total": len(results), "ok": ok,
            "failed": len(results) - ok, "split_docs": sum(1 for r in results if r["split_children"]),
            "results": results}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb-root", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--split-chars", type=int, default=8000)
    ap.add_argument("--out", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    kb_root = Path(args.kb_root)
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8-sig"))
    result = organize(kb_root, plan, args.split_chars)

    out_dir = Path(args.out) if args.out else Path(".tribro") / "wiki"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "organize.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"归置完成：{result['ok']}/{result['total']} 成功，拆分 {result['split_docs']} 篇大文档")
    return 0


if __name__ == "__main__":
    sys.exit(main())
