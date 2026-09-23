#!/usr/bin/env python3
"""知识库结构化体检（tri-wiki 门F 增强 · 门G 复用）。

补的缺口：v1 只有「断链检测」一条规则。本脚本把体检扩展为可分级、可机检的规则集，
规则定义集中在 RULES 表（新增规则 = 追加一条字典，不改流程）。

严重度：
  error   —— 阻断交付（--strict 时退出码 3）
  warning —— 记入报告，由人工仲裁
  info    —— 仅提示

用法：
    python lint_vault.py --kb-root <知识库根> --json
    python lint_vault.py --kb-root <知识库根> --strict     # 有 error 则退出码 3
输出：`.wiki-meta/lint-report.json`。仅依赖标准库。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = ["title", "type", "source", "source_format", "created"]
MAX_NOTE_CHARS = 60000
MIN_SINGLETON_TAG_NOTES = 1
INJECTION_PATTERNS = [
    r"忽略(上述|以上|之前)(的)?(所有)?指令",
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s*prompt",
    r"you\s+are\s+now\s+",
]
SENSITIVE_PATTERNS = [r"api[_-]?key\s*[:=]", r"password\s*[:=]", r"token\s*[:=]\s*['\"][A-Za-z0-9]{16,}"]

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
WIKI_LINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:[#\|][^\]]*)?\]\]")
TAG_RE = re.compile(r"^\s*-\s+([A-Za-z0-9_\-\u4e00-\u9fff]+)\s*$", re.MULTILINE)
SKIP_DIRS = {".git", ".obsidian", ".wiki-meta", "90-attachments"}
INDEX_TYPES = {"index", "moc", "tags"}  # 导航页天然短小，豁免 empty-notes 规则

RULES = [
    {"id": "missing-frontmatter", "severity": "error",
     "desc": "笔记缺少 YAML frontmatter 块"},
    {"id": "missing-required-fields", "severity": "error",
     "desc": f"frontmatter 必填字段缺失（{', '.join(REQUIRED_FIELDS)}）"},
    {"id": "duplicate-titles", "severity": "error",
     "desc": "同一 title 被多篇笔记占用（链接解析歧义）"},
    {"id": "broken-links", "severity": "error",
     "desc": "wiki 链接指向不存在的笔记"},
    {"id": "orphan-notes", "severity": "warning",
     "desc": "无任何入链也无出链的孤立笔记"},
    {"id": "empty-notes", "severity": "warning",
     "desc": "正文有效字符 < 40"},
    {"id": "oversized-notes", "severity": "warning",
     "desc": f"单篇正文 > {MAX_NOTE_CHARS} 字符（建议原子化拆分）"},
    {"id": "singleton-tags", "severity": "info",
     "desc": "只被一篇笔记使用的标签（标签体系噪声）"},
    {"id": "unresolved-duplicates", "severity": "warning",
     "desc": "被 dedup_content.py 标记 dup_group 但未被仲裁"},
    {"id": "credibility-floor", "severity": "warning",
     "desc": "可信度评分落到地板值（损坏或已废弃）"},
    {"id": "prompt-injection-risk", "severity": "error",
     "desc": "正文疑似含指令注入文本（视为数据，需围栏标注）"},
    {"id": "sensitive-literal", "severity": "warning",
     "desc": "正文疑似含密钥/口令字面量"},
]


def iter_notes(kb_root: Path):
    import os
    for dirpath, dirnames, filenames in os.walk(kb_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            if name.lower().endswith((".md", ".markdown")):
                yield Path(dirpath) / name


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


def body_of(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return text[m.end():] if m else text


def main() -> int:
    ap = argparse.ArgumentParser(description="知识库结构化体检")
    ap.add_argument("--kb-root", required=True)
    ap.add_argument("--strict", action="store_true",
                    help="存在 error 级问题时以退出码 3 结束（供交付门禁使用）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    kb_root = Path(args.kb_root).resolve()
    if not kb_root.is_dir():
        print(json.dumps({"ok": False, "error": f"知识库根不存在: {kb_root}",
                          "error_code": "KB_ROOT_MISSING"}, ensure_ascii=False))
        return 2

    notes: dict[str, dict] = {}
    for path in iter_notes(kb_root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        key = path.relative_to(kb_root).as_posix()
        fm = parse_frontmatter(text)
        body = body_of(text)
        notes[key] = {
            "has_fm": bool(FRONTMATTER_RE.match(text)),
            "fm": fm,
            "body": body,
            "title": fm.get("title") or "",
            "outbound": [t.strip() for t in WIKI_LINK_RE.findall(body)],
        }

    # 名称索引（与 index_build 同口径：title + 文件名主干 + aliases）
    index: dict[str, str] = {}
    for key, n in notes.items():
        stem = Path(key).stem
        for alias in filter(None, [n["title"], stem]):
            index.setdefault(alias.lower(), key)

    inbound: dict[str, int] = {}
    for n in notes.values():
        for t in n["outbound"]:
            inbound[t.lower()] = inbound.get(t.lower(), 0) + 1

    tag_count: dict[str, int] = {}
    title_count: dict[str, list[str]] = {}
    for key, n in notes.items():
        if n["title"]:
            title_count.setdefault(n["title"].lower(), []).append(key)
        raw_fm = n["fm"]
        tags_raw = raw_fm.get("tags", "")
        for t in re.findall(r"[A-Za-z0-9_\-\u4e00-\u9fff]+", tags_raw):
            if t and t not in ("", "[]"):
                tag_count[t] = tag_count.get(t, 0) + 1

    findings: dict[str, list] = {r["id"]: [] for r in RULES}

    for key, n in sorted(notes.items()):
        if not n["has_fm"]:
            findings["missing-frontmatter"].append(key)
        else:
            miss = [f for f in REQUIRED_FIELDS if not n["fm"].get(f)]
            if miss:
                findings["missing-required-fields"].append(
                    {"path": key, "missing": miss})
        for t in n["outbound"]:
            if t.lower() not in index:
                findings["broken-links"].append({"path": key, "target": t})
        if not n["outbound"] and inbound.get((n["title"] or Path(key).stem).lower(), 0) == 0:
            findings["orphan-notes"].append(key)
        if len(n["body"].strip()) < 40 and n["fm"].get("type") not in INDEX_TYPES:
            findings["empty-notes"].append(key)
        if len(n["body"]) > MAX_NOTE_CHARS:
            findings["oversized-notes"].append({"path": key, "chars": len(n["body"])})
        if n["fm"].get("dup_group"):
            findings["unresolved-duplicates"].append({"path": key, "group": n["fm"]["dup_group"]})
        blob = n["body"].lower()
        for pat in INJECTION_PATTERNS:
            if re.search(pat, blob, re.IGNORECASE):
                findings["prompt-injection-risk"].append({"path": key, "pattern": pat})
                break
        for pat in SENSITIVE_PATTERNS:
            if re.search(pat, n["body"], re.IGNORECASE):
                findings["sensitive-literal"].append({"path": key, "pattern": pat})
                break

    for title, paths in title_count.items():
        if len(paths) > 1:
            findings["duplicate-titles"].append({"title": title, "paths": paths})
    for tag, cnt in tag_count.items():
        if cnt <= MIN_SINGLETON_TAG_NOTES:
            findings["singleton-tags"].append({"tag": tag, "count": cnt})

    cred_path = kb_root / ".wiki-meta" / "credibility.json"
    if cred_path.exists():
        try:
            data = json.loads(cred_path.read_text(encoding="utf-8"))
            for item in data.get("notes", []):
                if item.get("basis") == "floor":
                    findings["credibility-floor"].append(
                        {"path": item.get("path"), "credibility": item.get("credibility")})
        except (json.JSONDecodeError, OSError):
            pass

    sev_of = {r["id"]: r["severity"] for r in RULES}
    report = []
    for r in RULES:
        items = findings[r["id"]]
        report.append({
            "rule": r["id"],
            "severity": r["severity"],
            "desc": r["desc"],
            "count": len(items),
            "items": items[:200],
        })
    errors = sum(x["count"] for x in report if x["severity"] == "error")
    warnings = sum(x["count"] for x in report if x["severity"] == "warning")
    infos = sum(x["count"] for x in report if x["severity"] == "info")

    out_dir = kb_root / ".wiki-meta"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "lint-report.json"
    payload = {
        "ok": True,
        "kb_root": str(kb_root),
        "note_count": len(notes),
        "totals": {"error": errors, "warning": warnings, "info": infos},
        "rules": report,
    }
    tmp = out_path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    tmp.replace(out_path)

    if args.json:
        print(json.dumps({"ok": True, "note_count": payload["note_count"],
                          "totals": payload["totals"], "output": str(out_path)},
                         ensure_ascii=False, indent=2))
    else:
        t = payload["totals"]
        print(f"笔记 {payload['note_count']} 篇 | error {t['error']} "
              f"| warning {t['warning']} | info {t['info']}")
        for r in report:
            if r["count"]:
                print(f"  [{r['severity']:7}] {r['rule']}: {r['count']}")
        print(f"报告：{out_path}")

    if args.strict and errors:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
