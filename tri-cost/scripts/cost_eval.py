#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tri-cost 成本审计确定性算法（cost_eval.py）

职责：把 tri-cost 的 token 聚合、成本估算、高消耗标记、ROI 评分落成确定性可执行逻辑。
prompt 层调用本脚本获取结构化结果，NEVER 在 prompt 内用散文复现这些计算。

功能：
  聚合   cost-index.jsonl -> 分节点 input/output/total/cost + 全链路合计
  估算   按 _meta.json price 表（input/output 单价可不同）计算成本
  标记   单节点 >= 全链路 high_cost_ratio 或 >= high_cost_tokens -> high_cost
  ROI    roi = value_injection / normalized_cost，按 ROI 升序给出优化优先级
  基线   --baseline 对比，输出 delta 百分比

用法：
  python cost_eval.py --index .tribro/cost/cost-index.jsonl --report .tribro/cost/audit
  python cost_eval.py --index x.jsonl --meta _meta.json --baseline .tribro/cost/base/baseline.json
  python cost_eval.py --runsyntax                          # 运行自检（合成数据冒烟）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


# 默认节点顺序（与 references/cost-model.md 一致）
DEFAULT_NODES = ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8"]
NODE_NAMES = {
    "N1": "用户提问输入", "N2": "意图识别", "N3": "快照落盘",
    "N4": "下游读取快照", "N5": "核心执行/工具调用", "N6": "推理思考",
    "N7": "最终答案生成", "N8": "输出",
}


def load_index(path: Path) -> List[Dict]:
    """读取 cost-index.jsonl（每行一条记录）。文件不存在返回空列表。"""
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def load_meta(path: Path) -> Dict:
    """读取 _meta.json；缺失时返回默认单价与阈值。"""
    defaults = {
        "price": {
            "default": {"input": 0.000003, "output": 0.000004},
            "models": {},
        },
        "high_cost_ratio": 0.20,
        "high_cost_tokens": 4000,
    }
    if not path.exists():
        return defaults
    try:
        meta = json.loads(path.read_text(encoding="utf-8"))
        for k, v in defaults.items():
            meta.setdefault(k, v)
        return meta
    except (json.JSONDecodeError, OSError):
        return defaults


def price_for(model: str, meta: Dict) -> Dict:
    """按模型取单价；未登记模型回退 default。"""
    models = meta.get("price", {}).get("models", {})
    if model and model in models:
        return models[model]
    return meta.get("price", {}).get("default", {"input": 0.000003, "output": 0.000004})


def aggregate(records: List[Dict], meta: Dict) -> Dict:
    """分节点聚合 token 与成本。"""
    nodes: Dict[str, Dict] = {
        n: {"node_id": n, "name": NODE_NAMES.get(n, n), "input": 0, "output": 0,
            "total": 0, "cost": 0.0, "records": 0}
        for n in DEFAULT_NODES
    }
    for r in records:
        nid = r.get("node_id", "")
        if nid not in nodes:
            nid = "N5"  # 未知节点归入核心执行
        it = int(r.get("input_tokens", 0) or 0)
        ot = int(r.get("output_tokens", 0) or 0)
        model = r.get("model", "")
        p = price_for(model, meta)
        nodes[nid]["input"] += it
        nodes[nid]["output"] += ot
        nodes[nid]["total"] += it + ot
        nodes[nid]["cost"] += it * p["input"] + ot * p["output"]
        nodes[nid]["records"] += 1

    total_tokens = sum(n["total"] for n in nodes.values())
    total_cost = sum(n["cost"] for n in nodes.values())
    ratio = meta.get("high_cost_ratio", 0.20)
    tokens_th = meta.get("high_cost_tokens", 4000)

    for n in nodes.values():
        n["ratio"] = (n["total"] / total_tokens) if total_tokens else 0.0
        n["high_cost"] = bool(
            total_tokens and (n["ratio"] >= ratio or n["total"] >= tokens_th)
        )

    return {
        "nodes": [nodes[n] for n in DEFAULT_NODES],
        "totals": {"input": sum(n["input"] for n in nodes.values()),
                   "output": sum(n["output"] for n in nodes.values()),
                   "tokens": total_tokens, "cost": total_cost},
    }


def roi_score(agg: Dict, value_injection: Dict[str, float]) -> List[Dict]:
    """按 ROI 升序给节点排优化优先级。value_injection ∈ [0,1] 由审计时按节点价值注入度打分。"""
    max_cost = max((n["cost"] for n in agg["nodes"]), default=0.0)
    rows = []
    for n in agg["nodes"]:
        norm_cost = (n["cost"] / max_cost) if max_cost else 0.0
        vi = value_injection.get(n["node_id"], 0.5)
        roi = (vi / norm_cost) if norm_cost else 0.0
        rows.append({**n, "roi": roi})
    rows.sort(key=lambda r: (r["roi"], -r["total"]))
    return rows


def baseline_delta(totals: Dict, baseline: Dict):
    """对比基线，返回全链路 token/cost 变化百分比。baseline 缺失返回 None。"""
    if not baseline:
        return None
    base_tokens = baseline.get("totals", {}).get("tokens")
    if base_tokens is None or base_tokens == 0:
        return None
    delta = (totals["tokens"] - base_tokens) / base_tokens * 100.0
    return round(delta, 2)


def build_report(agg: Dict, rows: List[Dict], delta, meta: Dict) -> Dict:
    """组装结构化报告（供落盘 cost-report.md 使用）。"""
    high = [n for n in rows if n["high_cost"]]
    optimizable = [n for n in rows if n["roi"] < 1.0]
    return {
        "total_tokens": agg["totals"]["tokens"],
        "total_input": agg["totals"]["input"],
        "total_output": agg["totals"]["output"],
        "estimated_cost": round(agg["totals"]["cost"], 6),
        "baseline_delta": delta,
        "high_cost_nodes": [n["node_id"] for n in high],
        "optimize_priority": [n["node_id"] for n in optimizable],
        "meta": {"high_cost_ratio": meta.get("high_cost_ratio"),
                 "high_cost_tokens": meta.get("high_cost_tokens")},
    }


def runsyntax() -> int:
    """合成数据冒烟自检：验证聚合/标记/ROI 基本正确。"""
    import tempfile, time
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        ip = d / "cost-index.jsonl"
        recs = []
        for nid, it, ot in [("N1", 100, 10), ("N2", 200, 50), ("N5", 3000, 200),
                            ("N7", 50, 600), ("N8", 0, 10)]:
            recs.append({"node_id": nid, "input_tokens": it, "output_tokens": ot,
                         "model": "", "session_id": "smoke", "ts": time.time()})
        ip.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in recs),
                      encoding="utf-8")
        meta = load_meta(Path(__file__).parent.parent / "_meta.json")
        agg = aggregate(load_index(ip), meta)
        t = agg["totals"]
        assert t["tokens"] == 4220, t
        rows = roi_score(agg, {"N1": 0.2, "N2": 0.3, "N5": 0.9, "N7": 1.0, "N8": 0.1})
        rep = build_report(agg, rows, None, meta)
        assert rep["estimated_cost"] > 0
        assert rep["high_cost_nodes"] == ["N5"], rep["high_cost_nodes"]
        print("runsyntax OK: tokens=%d high=%s" % (t["tokens"], rep["high_cost_nodes"]))
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-cost 成本审计确定性算法")
    ap.add_argument("--index", type=Path, default=None, help="cost-index.jsonl 路径")
    ap.add_argument("--meta", type=Path, default=None, help="_meta.json 路径")
    ap.add_argument("--baseline", type=Path, default=None, help="baseline.json 路径")
    ap.add_argument("--value-injection", type=str, default="",
                    help='JSON 字典，如 {"N5":0.9,"N7":1.0}')
    ap.add_argument("--report", type=Path, default=None, help="输出报告 JSON 路径")
    ap.add_argument("--runsyntax", action="store_true", help="合成数据冒烟自检")
    args = ap.parse_args()

    if args.runsyntax:
        return runsyntax()

    skill_dir = Path(__file__).resolve().parent.parent
    index = args.index or skill_dir / ".tribro" / "cost" / "cost-index.jsonl"
    meta = load_meta(args.meta or skill_dir / "_meta.json")
    records = load_index(index)
    agg = aggregate(records, meta)

    vi = {}
    if args.value_injection:
        try:
            vi = json.loads(args.value_injection)
        except json.JSONDecodeError:
            vi = {}
    rows = roi_score(agg, vi)

    baseline = None
    if args.baseline and args.baseline.exists():
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    delta = baseline_delta(agg["totals"], baseline)

    result = {
        "report": build_report(agg, rows, delta, meta),
        "nodes": rows,
        "baseline_delta": delta,
    }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                               encoding="utf-8")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())