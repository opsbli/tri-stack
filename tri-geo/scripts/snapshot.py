#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快照台账与 delta 计算（snapshot.py）——「智引」(tri-geo) 确定性脚本 08/09

职责（对应设计指南 §3.1 / §5.2）：
    · 标准化快照 JSON 追加写入（同名日期+模式已存在时拒绝覆盖，需 --revision）
    · 跨期 delta 计算（总分与五维逐项对比）
    · 历史只读保护：NEVER 覆盖或改写既有快照

目录约定（设计指南 §5.2）：
    .geo-snapshots/<品牌名>/<YYYY-MM-DD>-<mode>.json

用法：
    python snapshot.py append --brand 格力 --mode audit --scores scores.json \
        --evidence raw/site.html --top-fixes fixes.json --json
    python snapshot.py delta --brand 格力 --json
    python snapshot.py list --brand 格力 --json

退出码：
    0  成功
    2  无历史快照（delta）/ 无入参数据
    3  同名快照已存在且未指定 --revision（拒绝覆盖）
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
TOOL_NAME = "snapshot.py"

MODES = ["quick", "audit", "optimize", "cn_fit", "infra", "channels", "monitor"]


def safe_dir_name(brand: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", (brand or "").strip())
    return name or "unknown"


def snapshot_file(root: Path, brand: str, date: str, mode: str,
                  revision: Optional[int]) -> Path:
    base = root / safe_dir_name(brand) / f"{date}-{mode}"
    return Path(f"{base}.json") if not revision else Path(f"{base}-r{revision}.json")


def load_json_file(path: Optional[str]) -> Optional[Any]:
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def cmd_append(args: argparse.Namespace) -> int:
    root = Path(args.root)
    scores = load_json_file(args.scores)
    if scores is None:
        print("[智引·快照] 缺少有效 --scores（评分 JSON 不存在或不可解析）", file=sys.stderr)
        return 2

    date = args.date
    target = snapshot_file(root, args.brand, date, args.mode, args.revision)
    if target.exists() and not args.force:
        print(f"[智引·快照] 同名快照已存在：{target}；历史只读，请使用 --revision 2 或换日期",
              file=sys.stderr)
        return 3

    evidence: List[str] = [e for e in (args.evidence or "").split(",") if e.strip()]
    fixes = load_json_file(args.top_fixes)
    if isinstance(fixes, dict):
        fixes = fixes.get("fixes") or fixes.get("top_fixes")
    probe = load_json_file(args.probe)

    snapshot: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "date": date,
        "type": args.mode,
        "brand": args.brand,
        "scores": {
            "total": (scores.get("score") or {}).get("total"),
            "cap": (scores.get("score") or {}).get("cap"),
            "pillars": (scores.get("score") or {}).get("pillars", {}),
            "rating": (scores.get("score") or {}).get("rating"),
        },
        "probe": (probe or {}).get("overall") if isinstance(probe, dict) else None,
        "veto": scores.get("veto", []),
        "evidence_paths": evidence,
        "top_fixes": fixes if isinstance(fixes, list) else [],
        "note": args.note or "",
    }
    if args.force and target.exists():
        target.unlink()  # 仅 --force 时允许重写当日同模式快照（发布前调试用）

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"tool": TOOL_NAME, "action": "append", "path": str(target),
                      "brand": args.brand, "mode": args.mode,
                      "total": snapshot["scores"]["total"]},
                     ensure_ascii=False, indent=2))
    return 0


def cmd_delta(args: argparse.Namespace) -> int:
    root = Path(args.root) / safe_dir_name(args.brand)
    if not root.is_dir():
        print(f"[智引·快照] 品牌目录不存在：{root}", file=sys.stderr)
        return 2
    files = sorted([p for p in root.glob("*.json") if p.is_file()])
    if len(files) < 2:
        print(f"[智引·快照] 历史快照不足 2 条（当前 {len(files)} 条），无法计算 delta",
              file=sys.stderr)
        return 2
    first = json.loads(files[0].read_text(encoding="utf-8"))
    last = json.loads(files[-1].read_text(encoding="utf-8"))

    def num(x: Any) -> Optional[float]:
        return float(x) if isinstance(x, (int, float)) else None

    pillars_now = (last.get("scores") or {}).get("pillars") or {}
    pillars_old = (first.get("scores") or {}).get("pillars") or {}
    rows: List[Dict[str, Any]] = []
    for k in sorted(set(list(pillars_now) + list(pillars_old))):
        a, b = num(pillars_old.get(k)), num(pillars_now.get(k))
        rows.append({"item": k, "baseline": a, "latest": b,
                     "delta": (round(b - a, 1) if (a is not None and b is not None) else None)})
    t_old, t_new = num((first.get("scores") or {}).get("total")), num((last.get("scores") or {}).get("total"))
    result = {
        "tool": TOOL_NAME, "action": "delta", "brand": args.brand,
        "baseline_file": str(files[0]), "latest_file": str(files[-1]),
        "baseline_date": first.get("date"), "latest_date": last.get("date"),
        "total": {"baseline": t_old, "latest": t_new,
                  "delta": round(t_new - t_old, 1) if (t_old is not None and t_new is not None) else None},
        "pillars": rows,
        "snapshots": [str(p) for p in files],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root) / safe_dir_name(args.brand)
    files = sorted([p for p in root.glob("*.json") if p.is_file()]) if root.is_dir() else []
    rows = []
    for p in files:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            rows.append({"file": str(p), "date": d.get("date"), "type": d.get("type"),
                         "total": (d.get("scores") or {}).get("total")})
        except (OSError, json.JSONDecodeError):
            rows.append({"file": str(p), "date": None, "type": None, "total": None})
    print(json.dumps({"tool": TOOL_NAME, "action": "list", "brand": args.brand,
                      "count": len(rows), "snapshots": rows},
                     ensure_ascii=False, indent=2))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="「智引」快照台账与 delta 计算")
    sub = ap.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--brand", required=True)
    common.add_argument("--root", default=".geo-snapshots", help="快照根目录")

    a = sub.add_parser("append", parents=[common])
    a.add_argument("--mode", required=True, choices=MODES)
    a.add_argument("--scores", required=True, help="site_signal.py 评分 JSON")
    a.add_argument("--probe", default=None, help="answer_judge.py 判定 JSON（可选）")
    a.add_argument("--evidence", default="", help="证据路径，逗号分隔")
    a.add_argument("--top-fixes", default=None, help="Top 修复项 JSON（数组或 {fixes:[]}）")
    a.add_argument("--date", default=None, help="快照日期，默认今天")
    a.add_argument("--revision", type=int, default=None, help="当日内重复运行的版本号")
    a.add_argument("--force", action="store_true", help="允许覆盖当日同模式快照（默认拒绝）")
    a.add_argument("--note", default=None)
    a.set_defaults(func=cmd_append)

    d = sub.add_parser("delta", parents=[common])
    d.set_defaults(func=cmd_delta)

    l = sub.add_parser("list", parents=[common])
    l.set_defaults(func=cmd_list)

    args = ap.parse_args(argv)
    if getattr(args, "date", None) is None and args.cmd == "append":
        import time
        args.date = time.strftime("%Y-%m-%d")
    try:
        return args.func(args)
    except Exception as e:  # noqa: BLE001
        print(f"[智引·快照] 脚本异常：{type(e).__name__}: {e}", file=sys.stderr)
        return 64


if __name__ == "__main__":
    sys.exit(main())
