#!/usr/bin/env python3
"""tri-cache 项目初始化：为目标项目建立四层缓存架构。

四层架构落盘：
    L1 滑动窗口  window_state.json + window_state 表（最近 N 轮全文）
    L2 结构化    index.db cache_entries 表（元数据 + 摘要 + 标签）
    L3 轻量摘要  cache_entries.summary + summaries/<YYYY-MM>.jsonl
    L4 向量检索  index.db embeddings 表（确定性字符 n-gram 哈希嵌入）

用法：
    python scripts/cache_init.py --root <项目根目录> [--force] [--dry-run]
    python scripts/cache_init.py --root <项目根目录> --json
    python scripts/cache_init.py --root .                      # 默认当前项目

退出码：0=成功；1=参数/环境错误；2=目标已存在且未 --force。
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 2

# 与 schemas/cache-entry.schema.md 对齐的建表 DDL（schema v2）
DDL = """
CREATE TABLE IF NOT EXISTS cache_entries (
  cache_key      TEXT PRIMARY KEY,
  question       TEXT NOT NULL,
  answer         TEXT NOT NULL,
  summary        TEXT NOT NULL,
  intent_l1      TEXT,
  intent_l2      TEXT,
  aux_intents    TEXT,
  d1_domain      TEXT,
  d2_input_form  TEXT,
  d3_rounds      TEXT,
  d4_output      TEXT,
  d5_certainty   TEXT,
  session_id     TEXT NOT NULL,
  user_id        TEXT DEFAULT 'default',
  source_skill   TEXT,
  created_at     INTEGER NOT NULL,
  last_accessed  INTEGER NOT NULL,
  hit_count      INTEGER DEFAULT 0,
  ttl_seconds    INTEGER,
  expires_at     INTEGER,
  content_size   INTEGER,
  tags           TEXT,
  status         TEXT DEFAULT 'active',
  entry_path     TEXT,
  schema_version INTEGER DEFAULT 2
);
CREATE INDEX IF NOT EXISTS idx_intent_l2   ON cache_entries(intent_l2);
CREATE INDEX IF NOT EXISTS idx_session     ON cache_entries(session_id);
CREATE INDEX IF NOT EXISTS idx_user        ON cache_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_created     ON cache_entries(created_at);
CREATE INDEX IF NOT EXISTS idx_last_access ON cache_entries(last_accessed);
CREATE INDEX IF NOT EXISTS idx_expires     ON cache_entries(expires_at);
CREATE INDEX IF NOT EXISTS idx_status      ON cache_entries(status);

CREATE TABLE IF NOT EXISTS embeddings (
  cache_key   TEXT PRIMARY KEY REFERENCES cache_entries(cache_key) ON DELETE CASCADE,
  dim         INTEGER NOT NULL,
  ngram_min   INTEGER NOT NULL,
  ngram_max   INTEGER NOT NULL,
  vector      TEXT NOT NULL,
  created_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS window_state (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id  TEXT NOT NULL,
  seq         INTEGER NOT NULL,
  cache_key   TEXT NOT NULL REFERENCES cache_entries(cache_key),
  question    TEXT NOT NULL,
  answer      TEXT NOT NULL,
  summary     TEXT,
  created_at  INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_window_session ON window_state(session_id, seq);

CREATE TABLE IF NOT EXISTS cache_meta (
  key   TEXT PRIMARY KEY,
  value TEXT
);
"""

# cache_meta 预置统计键
PRESET_STATS = {
    "total_entries": "0",
    "total_size_bytes": "0",
    "total_hits": "0",
    "total_misses": "0",
    "total_evictions": "0",
    "last_cleanup_at": "null",
}


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA cache_size=-20000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _load_template_meta() -> dict:
    template = Path(__file__).resolve().parent.parent / "templates" / "meta.json"
    if not template.is_file():
        return {}
    try:
        return json.loads(template.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def init_project(root: str, force: bool = False,
                 dry_run: bool = False) -> dict:
    """初始化目标项目的四层缓存架构。返回结构化结果。"""
    root_path = Path(root).resolve()
    cache_dir = root_path / ".tribro" / "cache"
    result: dict = {
        "root": str(root_path),
        "cache_dir": str(cache_dir),
        "schema_version": SCHEMA_VERSION,
        "created": [],
        "skipped": [],
        "errors": [],
    }

    if cache_dir.exists() and any(cache_dir.iterdir()) and not force:
        result["errors"].append(
            f"缓存目录已存在且非空：{cache_dir}（使用 --force 覆盖重建）")
        return result

    if dry_run:
        result["created"] = [
            "entries/", "summaries/", "index.db", "meta.json", "window_state.json",
        ]
        return result

    # 1. 目录骨架
    (cache_dir / "entries").mkdir(parents=True, exist_ok=True)
    (cache_dir / "summaries").mkdir(parents=True, exist_ok=True)
    result["created"].extend(["entries/", "summaries/"])

    # 2. index.db（四表 + 索引 + 预置统计）
    db_path = cache_dir / "index.db"
    conn = _connect(db_path)
    conn.executescript(DDL)
    for key, value in PRESET_STATS.items():
        conn.execute(
            "INSERT OR IGNORE INTO cache_meta(key, value) VALUES(?, ?)",
            (key, value))
    conn.commit()
    conn.close()
    result["created"].append("index.db")

    # 3. meta.json（模板拷贝，可覆盖更新）
    meta = _load_template_meta()
    meta_path = cache_dir / "meta.json"
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    result["created"].append("meta.json")

    # 4. window_state.json（滑动窗口持久化）
    window_path = cache_dir / "window_state.json"
    window_path.write_text(
        json.dumps({"windows": {}, "schema_version": SCHEMA_VERSION},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    result["created"].append("window_state.json")

    return result


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="tri-cache 项目初始化：为目标项目建立四层缓存架构")
    ap.add_argument("--root", default=".", help="目标项目根目录（默认当前目录）")
    ap.add_argument("--force", action="store_true", help="覆盖重建已存在的缓存目录")
    ap.add_argument("--dry-run", action="store_true", help="只报告将创建的结构，不落盘")
    ap.add_argument("--json", action="store_true", help="输出 JSON 供 Agent 解析")
    args = ap.parse_args(argv)

    result = init_project(args.root, force=args.force, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[tri-cache init] 目标项目：{result['root']}")
        print(f"  缓存目录：{result['cache_dir']}")
        print(f"  schema 版本：v{result['schema_version']}")
        for item in result["created"]:
            print(f"  ✓ 创建 {item}")
        for item in result["skipped"]:
            print(f"  · 跳过 {item}")
        for err in result["errors"]:
            print(f"  ✗ {err}")
        if result["errors"]:
            return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[tri-cache init] 脚本自身异常：{type(e).__name__}: {e}",
              file=sys.stderr)
        sys.exit(1)
