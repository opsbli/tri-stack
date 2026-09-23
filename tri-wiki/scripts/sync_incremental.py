#!/usr/bin/env python3
"""增量同步与索引状态管理（tri-wiki 门G · 阶段一）。

设计来源：参考项目「markdown 是真相、索引是缓存」的持久化哲学——
索引可以从 markdown 全量重建，因此源笔记永远不需要依赖索引存在。

双判据变更检测（与参考项目 sync 同构）：
  1) mtime 差值 > MTIME_EPSILON 秒才认为「可能变了」；
  2) 可能变了的文件再算 sha256 二次确认，避免时钟抖动/复制导致的假变更。

用法：
    python sync_incremental.py --kb-root <知识库根> --mode plan  --json
    python sync_incremental.py --kb-root <知识库根> --mode apply
    python sync_incremental.py --kb-root <知识库根> --mode rebuild

输出：`.wiki-meta/sync-state.json`（索引状态）+ stdout 摘要。
仅依赖 Python 标准库。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

STATE_VERSION = 1
STATE_NAME = "sync-state.json"
MTIME_EPSILON = 0.001  # 秒；小于此差值视为同一时刻，转 hash 二次确认
SCAN_SUFFIXES = {".md", ".markdown"}
SKIP_DIRS = {".git", ".obsidian", ".wiki-meta", "90-attachments"}


def iter_notes(kb_root: Path):
    """遍历知识库内所有笔记（跳过元数据/附件/版本目录）。"""
    for dirpath, dirnames, filenames in os.walk(kb_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            if Path(name).suffix.lower() in SCAN_SUFFIXES:
                yield Path(dirpath) / name


def rel_key(path: Path, kb_root: Path) -> str:
    return path.relative_to(kb_root).as_posix()


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"state_version": STATE_VERSION, "generated_at": None, "files": {}}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("files"), dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return {"state_version": STATE_VERSION, "generated_at": None, "files": {}}


def scan_current(kb_root: Path) -> dict:
    now = {}
    for path in iter_notes(kb_root):
        try:
            st = path.stat()
        except OSError:
            continue
        now[rel_key(path, kb_root)] = {
            "mtime": round(st.st_mtime, 6),
            "size": st.st_size,
        }
    return now


def compute_plan(kb_root: Path, previous: dict, current: dict, rebuild: bool) -> dict:
    """双判据比对：mtime 判疑似，hash 判确定。"""
    prev_files = previous.get("files", {})
    added, modified, unchanged, deleted = [], [], [], []

    for key in sorted(set(prev_files) - set(current)):
        deleted.append(key)

    for key, cur in sorted(current.items()):
        old = prev_files.get(key)
        if old is None:
            added.append(key)
            continue
        if rebuild:
            modified.append(key)
            continue
        if abs(cur["mtime"] - old.get("mtime", 0.0)) > MTIME_EPSILON:
            # 疑似变更 → hash 二次确认
            digest = sha256_of(kb_root / key)
            if digest != old.get("hash"):
                modified.append(key)
            else:
                unchanged.append(key)
        elif cur["size"] != old.get("size"):
            digest = sha256_of(kb_root / key)
            if digest != old.get("hash"):
                modified.append(key)
            else:
                unchanged.append(key)
        else:
            unchanged.append(key)

    return {
        "added": added,
        "modified": modified,
        "unchanged": unchanged,
        "deleted": deleted,
    }


def build_state(kb_root: Path, current: dict) -> dict:
    files = {}
    for key, meta in current.items():
        files[key] = {
            "mtime": meta["mtime"],
            "size": meta["size"],
            "hash": sha256_of(kb_root / key),
        }
    return {
        "state_version": STATE_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "kb_root": str(kb_root),
        "files": files,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="知识库增量同步与索引状态管理")
    ap.add_argument("--kb-root", required=True, help="知识库根目录")
    ap.add_argument(
        "--mode",
        choices=["plan", "apply", "rebuild"],
        default="plan",
        help="plan=只出计划不落盘；apply=执行并刷新状态；rebuild=忽略旧状态全量重建",
    )
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    kb_root = Path(args.kb_root).resolve()
    if not kb_root.is_dir():
        print(json.dumps({"ok": False, "error": f"知识库根不存在: {kb_root}",
                          "error_code": "KB_ROOT_MISSING"}, ensure_ascii=False))
        return 2

    meta_dir = kb_root / ".wiki-meta"
    state_path = meta_dir / STATE_NAME
    previous = {} if args.mode == "rebuild" else load_state(state_path)
    current = scan_current(kb_root)
    plan = compute_plan(kb_root, previous, current, rebuild=(args.mode == "rebuild"))

    result = {
        "ok": True,
        "mode": args.mode,
        "kb_root": str(kb_root),
        "counts": {
            "total": len(current),
            "added": len(plan["added"]),
            "modified": len(plan["modified"]),
            "unchanged": len(plan["unchanged"]),
            "deleted": len(plan["deleted"]),
        },
        "plan": plan,
        "state_path": str(state_path),
    }

    if args.mode in ("apply", "rebuild"):
        meta_dir.mkdir(parents=True, exist_ok=True)
        state = build_state(kb_root, current)
        tmp = state_path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
        tmp.replace(state_path)  # 原子替换
        result["state_written"] = True
        result["note"] = "索引是缓存：删除本文件后以 --mode rebuild 可从 markdown 全量重建。"
    else:
        result["state_written"] = False
        result["note"] = "plan 模式不落盘；确认无误后以 --mode apply 刷新状态。"

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        c = result["counts"]
        print(f"总计 {c['total']} 篇 | 新增 {c['added']} | 修改 {c['modified']} "
              f"| 未变 {c['unchanged']} | 删除 {c['deleted']}")
        print(f"状态文件：{result['state_path']}（写入={result['state_written']}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
