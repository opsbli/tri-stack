#!/usr/bin/env python3
"""笔记生命周期治理（tri-wiki 门G · 阶段三）。

补的缺口：v1 入库笔记的 status 恒为 seedling，没有演进路径、没有衰减机制、
没有复核提醒——知识库会随时间堆成「半读页面填埋场」。

状态机（两条轨道，与参考项目同构）：
    成长轨：seedling → budding → evergreen
    衰减轨：stale → deprecated → archive

推进判据全部确定性（不靠模型目测）：
  - evergreen：元数据完整 + 有反向链接 + 正文信息量达标（三条件全中）
  - budding ：元数据完整且（有链接或正文达标）
  - stale   ：evergreen/budding 超过 --stale-days 未复核
  - archive ：status=deprecated 且再次超过 --stale-days

用法：
    python lifecycle_govern.py --kb-root <知识库根> --plan  --json
    python lifecycle_govern.py --kb-root <知识库根> --apply
输出：`.wiki-meta/lifecycle-plan.json`。仅依赖标准库。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

GROWTH = ["seedling", "budding", "evergreen"]
DECAY = ["stale", "deprecated", "archive"]
ALL_STATES = GROWTH + DECAY

DEFAULT_STALE_DAYS = 180
DEFAULT_EVERGREEN_MIN_LINKS = 2
# 中文信息密度高，800 字符已是一篇成型的笔记；门槛按中文语料校准，见可信度常量表
DEFAULT_EVERGREEN_MIN_CHARS = 800
REQUIRED_FIELDS = ["title", "type", "source", "source_format", "created"]

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
WIKI_LINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:[#\|][^\]]*)?\]\]")
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
SKIP_DIRS = {".git", ".obsidian", ".wiki-meta", "90-attachments"}


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


def decide(fm: dict, body: str, inbound: int, stale_days: int,
           min_links: int, min_chars: int) -> tuple[str, str]:
    """返回 (suggested_status, reason)。只建议，不强制跃迁衰减轨。"""
    current = (fm.get("status") or "seedling").strip().lower()
    if current not in ALL_STATES:
        current = "seedling"

    complete = all(fm.get(f) for f in REQUIRED_FIELDS)
    chars = len(body.strip())
    rich = chars >= min_chars
    linked = inbound >= min_links
    days = age_days(fm.get("updated") or fm.get("created"))

    # 衰减轨：已在衰减轨上的按其自身规则推进
    if current in DECAY:
        if current == "stale" and days is not None and days > stale_days * 2:
            return "deprecated", f"stale 后再次超过 {stale_days * 2} 天未复核"
        if current == "deprecated" and days is not None and days > stale_days * 2:
            return "archive", f"deprecated 后超过 {stale_days * 2} 天未处置"
        return current, "衰减轨保持不变，等待人工仲裁"

    # 成长轨
    if complete and rich and linked:
        target = "evergreen"
        reason = f"元数据完整 + 正文 {chars} 字 + 反向链接 {inbound}"
    elif complete and (rich or linked):
        target = "budding"
        reason = f"元数据完整 +（正文 {chars} 字 / 反向链接 {inbound}）之一达标"
    else:
        return "seedling", "元数据或内容未达 budding 门槛"

    # 时效衰减：成长为 evergreen/budding 后长期未复核 → 建议转 stale
    if days is not None and days > stale_days:
        return "stale", f"{target} 已 {int(days)} 天未复核（>{stale_days} 天）"
    return target, reason


def main() -> int:
    ap = argparse.ArgumentParser(description="笔记生命周期治理")
    ap.add_argument("--kb-root", required=True)
    ap.add_argument("--plan", action="store_true", help="只出计划（默认）")
    ap.add_argument("--apply", action="store_true", help="写回 frontmatter status/reviewed")
    ap.add_argument("--stale-days", type=int, default=DEFAULT_STALE_DAYS)
    ap.add_argument("--min-links", type=int, default=DEFAULT_EVERGREEN_MIN_LINKS)
    ap.add_argument("--min-chars", type=int, default=DEFAULT_EVERGREEN_MIN_CHARS)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.apply and args.plan:
        print(json.dumps({"ok": False, "error": "--plan 与 --apply 互斥",
                          "error_code": "ARG_CONFLICT"}, ensure_ascii=False))
        return 2

    kb_root = Path(args.kb_root).resolve()
    if not kb_root.is_dir():
        print(json.dumps({"ok": False, "error": f"知识库根不存在: {kb_root}",
                          "error_code": "KB_ROOT_MISSING"}, ensure_ascii=False))
        return 2

    raws, fms, bodies = {}, {}, {}
    for path in iter_notes(kb_root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        key = path.relative_to(kb_root).as_posix()
        raws[key] = text
        fms[key] = parse_frontmatter(text)
        bodies[key] = body_of(text)

    inbound: dict[str, int] = {}
    for key, body in bodies.items():
        for t in WIKI_LINK_RE.findall(body):
            inbound[t.strip()] = inbound.get(t.strip(), 0) + 1

    today = datetime.now().strftime("%Y-%m-%d")  # 本地日期，与用户直觉一致
    entries, changed = [], 0
    for key in sorted(raws):
        fm = fms[key]
        title = fm.get("title") or key
        target, reason = decide(fm, bodies[key], inbound.get(title, 0),
                                args.stale_days, args.min_links, args.min_chars)
        current = (fm.get("status") or "seedling").strip().lower()
        entries.append({
            "path": key,
            "title": title,
            "current": current,
            "suggested": target,
            "changed": target != current,
            "reason": reason,
        })

    if args.apply:
        for e in entries:
            if not e["changed"]:
                continue
            path = kb_root / e["path"]
            text = raws[e["path"]]
            m = FRONTMATTER_RE.match(text)
            if not m:
                continue
            block = m.group(1)
            if re.search(r"^status:", block, re.MULTILINE):
                block = re.sub(r"^status:.*$", f"status: {e['suggested']}", block,
                               count=1, flags=re.MULTILINE)
            else:
                block = f"{block.rstrip()}\nstatus: {e['suggested']}\n"
            if re.search(r"^reviewed:", block, re.MULTILINE):
                block = re.sub(r"^reviewed:.*$", f"reviewed: {today}", block,
                               count=1, flags=re.MULTILINE)
            else:
                block = f"{block.rstrip()}\nreviewed: {today}\n"
            path.write_text(f"---\n{block.rstrip()}\n---\n{text[m.end():]}", encoding="utf-8")
            changed += 1

    out_dir = kb_root / ".wiki-meta"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "lifecycle-plan.json"
    dist: dict[str, int] = {}
    for e in entries:
        dist[e["suggested"]] = dist.get(e["suggested"], 0) + 1
    payload = {
        "ok": True,
        "kb_root": str(kb_root),
        "generated_at": today,
        "params": {"stale_days": args.stale_days, "min_links": args.min_links,
                   "min_chars": args.min_chars},
        "note_count": len(entries),
        "changes": sum(1 for e in entries if e["changed"]),
        "applied": changed,
        "distribution": dist,
        "entries": entries,
    }
    tmp = out_path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    tmp.replace(out_path)

    if args.json:
        print(json.dumps({"ok": True, "note_count": payload["note_count"],
                          "changes": payload["changes"], "applied": changed,
                          "distribution": dist, "output": str(out_path)},
                         ensure_ascii=False, indent=2))
    else:
        print(f"笔记 {payload['note_count']} 篇 | 建议变更 {payload['changes']} "
              f"| 已写入 {changed} | 分布 {dist}")
        print(f"报告：{out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
