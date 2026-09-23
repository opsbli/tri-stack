#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实测执行与流程控制（probe_runner.py）——「智引」(tri-geo) 确定性脚本 06/09

职责（对应设计指南 §3.1 / §4.2）：
    · prompt 集管理：按「品牌/对比/推荐/问题解决」四意图生成目标问题清单
    · 多轮采样调度（默认每引擎每问题 3 轮）+ 速率控制 + 执行日志
    · 原始回答逐轮落盘（证据链），manifest 记录每个任务的填充状态与数据来源类型

重要设计约束：
    · 本脚本是「执行控制器 + 证据落盘器」，NEVER 伪造引擎回答
    · 实际提问由 Agent（WebSearch / 官方接口 / 人工会话）执行，结果通过 ingest 回填
    · 若引擎不可达，source_type 标注 trace_search（留痕检索）或 unavailable，
      NEVER 用 LLM 自我推演（虚拟收录查询）冒充实测（P3 红线）

子命令：
    plan    生成执行计划与 manifest
    ingest  回填单条原始回答（校验非空 + 落盘 + 更新 manifest）
    status  查看完成度与待办任务

用法：
    python probe_runner.py plan --brand 格力 --product-type 空调 \
        --engines deepseek,doubao --rounds 3 --out-dir .geo-snapshots/格力 --json
    python probe_runner.py ingest --out-dir .geo-snapshots/格力 --engine deepseek \
        --prompt-id P01 --round 1 --file answers/deepseek-r1.txt --source-type session
    python probe_runner.py status --out-dir .geo-snapshots/格力 --json

退出码：
    0  成功
    2  校验失败（回答文本为空/过短、任务不存在、引擎越界）
    64 参数或环境错误
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = "1.0"
TOOL_NAME = "probe_runner.py"

ENGINE_CODES = ["deepseek", "doubao", "kimi", "zhipu", "wenxin", "yuanbao",
                "tongyi", "baidu_ai"]
SOURCE_TYPES = ["api", "session", "trace_search", "unavailable"]
MIN_ANSWER_CHARS = 20
DEFAULT_ROUNDS = 3

INTENTS = ["品牌", "对比", "推荐", "问题解决"]


def build_prompts(brand: str, product_type: str, competitors: List[str]) -> List[Dict[str, str]]:
    """确定性生成目标问题集（四意图）。"""
    b = (brand or "").strip()
    t = (product_type or "").strip()
    prompts: List[Dict[str, str]] = []
    seq = 1

    def add(intent: str, text: str) -> None:
        nonlocal seq
        prompts.append({"id": f"P{seq:02d}", "intent": intent, "prompt": text})
        seq += 1

    if b:
        add("品牌", f"{b}怎么样")
        add("品牌", f"{b}靠谱吗")
    if t:
        add("推荐", f"{t}推荐")
        add("推荐", f"国内{t}哪个牌子好")
        add("问题解决", f"{t}怎么选")
        add("问题解决", f"{t}一般多少钱")
    if b and t:
        add("品牌", f"{b}{t}值得买吗")
    for c in competitors[:3]:
        if b and c:
            add("对比", f"{b}和{c}哪个好")
    if not prompts:
        add("品牌", "（请提供品牌名以生成目标问题）")
    return prompts


def manifest_path(out_dir: Path) -> Path:
    return out_dir / "probe" / "manifest.json"


def load_manifest(out_dir: Path) -> Dict[str, Any]:
    p = manifest_path(out_dir)
    if not p.is_file():
        return {"schema_version": SCHEMA_VERSION, "tasks": [], "meta": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def save_manifest(out_dir: Path, data: Dict[str, Any]) -> None:
    p = manifest_path(out_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def task_file(out_dir: Path, engine: str, prompt_id: str, round_no: int) -> Path:
    return out_dir / "probe" / engine / f"{prompt_id}-r{round_no}.txt"


def cmd_plan(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    prompts = build_prompts(args.brand or "", args.product_type or "",
                            [c for c in (args.competitors or "").split(",") if c.strip()])
    if args.prompts_file:
        custom = json.loads(Path(args.prompts_file).read_text(encoding="utf-8"))
        prompts = custom if isinstance(custom, list) else custom.get("prompts", prompts)

    engines = [e for e in (args.engines.split(",") if args.engines else ENGINE_CODES)
               if e in ENGINE_CODES]
    tasks: List[Dict[str, Any]] = []
    for engine in engines:
        for pr in prompts:
            for r in range(1, args.rounds + 1):
                tasks.append({
                    "engine": engine,
                    "prompt_id": pr["id"],
                    "intent": pr.get("intent", ""),
                    "prompt": pr["prompt"],
                    "round": r,
                    "path": str(task_file(out_dir, engine, pr["id"], r)),
                    "status": "pending",
                    "source_type": None,
                    "sha256": None,
                })
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "brand": args.brand,
        "product_type": args.product_type,
        "rounds": args.rounds,
        "engines": engines,
        "prompts": prompts,
        "tasks": tasks,
    }
    save_manifest(out_dir, manifest)
    result = {"tool": TOOL_NAME, "action": "plan", "out_dir": str(out_dir),
              "engines": engines, "prompts": len(prompts), "rounds": args.rounds,
              "total_tasks": len(tasks),
              "manifest": str(manifest_path(out_dir)),
              "instruction": "由 Agent 按 tasks 逐条实际提问，回答文本用 ingest 回填；"
                             "NEVER 用 LLM 推演冒充实测"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    manifest = load_manifest(out_dir)
    if not manifest.get("tasks"):
        print("[智引·实测] manifest 为空，请先执行 plan", file=sys.stderr)
        return 2
    if args.engine not in ENGINE_CODES:
        print(f"[智引·实测] 未知引擎：{args.engine}", file=sys.stderr)
        return 2

    text = ""
    if args.text:
        text = args.text
    elif args.file:
        fp = Path(args.file)
        if not fp.is_file():
            print(f"[智引·实测] 文本文件不存在：{fp}", file=sys.stderr)
            return 2
        text = fp.read_text(encoding="utf-8", errors="replace")
    else:
        print("[智引·实测] 缺少 --file 或 --text", file=sys.stderr)
        return 64

    if len(re.sub(r"\s+", "", text)) < MIN_ANSWER_CHARS:
        print(f"[智引·实测] 回答过短（<{MIN_ANSWER_CHARS} 字），拒绝回填（防脏数据）",
              file=sys.stderr)
        return 2

    dest = task_file(out_dir, args.engine, args.prompt_id, args.round)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()

    hit = 0
    for t in manifest["tasks"]:
        if (t["engine"] == args.engine and t["prompt_id"] == args.prompt_id
                and t["round"] == args.round):
            t.update({"status": "filled", "source_type": args.source_type, "sha256": sha})
            hit += 1
    if hit == 0:  # 允许计划外回填（补采样），追加任务记录
        manifest["tasks"].append({
            "engine": args.engine, "prompt_id": args.prompt_id, "intent": "",
            "prompt": args.prompt or "", "round": args.round, "path": str(dest),
            "status": "filled", "source_type": args.source_type, "sha256": sha})
    save_manifest(out_dir, manifest)
    print(json.dumps({"tool": TOOL_NAME, "action": "ingest", "path": str(dest),
                      "engine": args.engine, "prompt_id": args.prompt_id,
                      "round": args.round, "source_type": args.source_type,
                      "chars": len(re.sub(r"\s+", "", text)), "sha256": sha,
                      "matched_existing_task": hit},
                     ensure_ascii=False, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    manifest = load_manifest(out_dir)
    tasks = manifest.get("tasks", [])
    filled = [t for t in tasks if t.get("status") == "filled"]
    pending = [t for t in tasks if t.get("status") != "filled"]
    by_engine: Dict[str, Dict[str, int]] = {}
    for t in tasks:
        e = by_engine.setdefault(t["engine"], {"total": 0, "filled": 0})
        e["total"] += 1
        if t.get("status") == "filled":
            e["filled"] += 1
    result = {"tool": TOOL_NAME, "action": "status", "out_dir": str(out_dir),
              "total": len(tasks), "filled": len(filled), "pending": len(pending),
              "by_engine": by_engine,
              "pending_tasks": [{"engine": t["engine"], "prompt_id": t["prompt_id"],
                                 "round": t["round"], "prompt": t.get("prompt", "")}
                                for t in pending[:20]],
              "source_types": sorted({t.get("source_type") for t in filled if t.get("source_type")})}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="「智引」实测执行与流程控制")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("plan", help="生成执行计划与 manifest")
    p1.add_argument("--brand", default=None)
    p1.add_argument("--product-type", default=None)
    p1.add_argument("--competitors", default=None, help="竞品名逗号分隔")
    p1.add_argument("--engines", default=None, help="引擎编码逗号分隔，默认全选")
    p1.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    p1.add_argument("--prompts-file", default=None, help="自定义 prompt 集 JSON")
    p1.add_argument("--out-dir", required=True, help="输出根目录（快照目录）")
    p1.set_defaults(func=cmd_plan)

    p2 = sub.add_parser("ingest", help="回填单条原始回答")
    p2.add_argument("--out-dir", required=True)
    p2.add_argument("--engine", required=True)
    p2.add_argument("--prompt-id", required=True)
    p2.add_argument("--round", type=int, required=True)
    p2.add_argument("--file", default=None, help="回答文本文件路径")
    p2.add_argument("--text", default=None, help="回答文本（与 --file 二选一）")
    p2.add_argument("--prompt", default=None, help="原始问题（计划外回填时必填）")
    p2.add_argument("--source-type", default="session", choices=SOURCE_TYPES)
    p2.set_defaults(func=cmd_ingest)

    p3 = sub.add_parser("status", help="查看完成度")
    p3.add_argument("--out-dir", required=True)
    p3.set_defaults(func=cmd_status)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except Exception as e:  # noqa: BLE001
        print(f"[智引·实测] 脚本异常：{type(e).__name__}: {e}", file=sys.stderr)
        return 64


if __name__ == "__main__":
    sys.exit(main())
