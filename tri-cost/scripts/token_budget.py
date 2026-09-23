#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tri-cost token 预算闸门与自动优化执行器（token_budget.py）

职责：把 caveman 蒸馏出的 token 节省方法论落成**代码级强约束**——不是 md 口头约定，
而是可在流程中"自动校验与限制" token 使用的可执行闸门。覆盖基准报告（docs/analysis-caveman-main-20260919.md）
§9.1 提出的全部待优化点，重点补齐 token_optimize.py 尚未代码化的两项：

  ⑤ 令牌预算打包启发式（BM25 相关性 + 近因 + 错误信号 + Pin 贪心装袋）→ pack_context
  ⑥ safety 等级 S0–S4（变换风险分级，约束哪些摘要可对模型无损、哪些必须有恢复）→ safety_class_of

并新增流程级强约束：
  - enforce_node：节点内容写入前，对 N4/N5/N7/N8 超预算内容自动执行 token_optimize 压缩，
    校验前后 token 与内容准确性；超硬上限或关键事实保留率不达标 → BLOCK（fail-closed 保留原文）。
  - gate_index：全链路预算闸门核查（per-node / session 限额），产出违规报告，供 COST_AUDIT 调用。

设计边界（与 caveman 的 BSL-1.1 引擎严格区分）：
  - 本脚本复用 token_optimize.py 的 detect/compress/count/accuracy/recovery（MIT 方法层），
    不打包 Go 代理/engine/SQLite CCR；BM25 为纯 Python 近似（Okapi BM25，无 embedding/网络），
    与 caveman contextwindow.Pack 思路一致但降级为方法论层近似（置信度：中；依据：推断 inferred）。
  - 所有压缩默认 fail-closed：绝不伪造"零 token 收益"，超硬上限时保留原文并显式告警/阻断。

用法：
  python token_budget.py --runsyntax
  python token_budget.py --enforce-node --node N5 --content-file payload.txt --meta ../_meta.json
  python token_budget.py --gate --index cost-index.jsonl --meta ../_meta.json
  python token_budget.py --pack --items items.json --budget 4000 --query "修复登录失败" --meta ../_meta.json
  python token_budget.py --safety --text "<日志>" --type auto
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 复用 token_optimize 的 detect/compress/count/accuracy/recovery（同目录）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_optimize as to  # noqa: E402


# ---------------------------------------------------------------------------
# 预算配置加载（唯一真源：_meta.json 的 budget 段，缺省给安全默认值）
# ---------------------------------------------------------------------------

# 默认 per-node 预算（token 估算，启发式）。覆盖标准链路八节点。
DEFAULT_NODE_CAPS = {
    "N1": 2000, "N2": 1500, "N3": 1500, "N4": 4000,
    "N5": 6000, "N6": 3000, "N7": 4000, "N8": 4000,
}
DEFAULT_BUDGET = {
    "enabled": True,
    "node_caps": DEFAULT_NODE_CAPS,
    "session_cap": 30000,
    "auto_optimize_nodes": ["N4", "N5", "N7", "N8"],
    "auto_optimize_intensity": "full",
    "hard_cap_policy": "block",          # block（超硬上限即阻断保留原文）/ warn（仅告警）
    "critical_retention_min": 0.90,       # 安全关键类型关键事实保留率下限
    "safety_critical_types": list(to.SAFETY_CRITICAL_TYPES),
}


def load_budget(meta: Dict) -> Dict:
    """从 _meta.json 的 budget 段加载预算配置；缺省合并安全默认值。

    强约束：任何未显式配置的字段一律回退默认值，避免因为配置缺失而放行超预算内容。
    """
    if not isinstance(meta, dict):
        return dict(DEFAULT_BUDGET)
    b = meta.get("budget", {})
    if not isinstance(b, dict):
        b = {}
    merged = dict(DEFAULT_BUDGET)
    merged.update({k: v for k, v in b.items() if k in DEFAULT_BUDGET})
    # node_caps 逐键合并（允许部分覆盖）
    caps = dict(DEFAULT_NODE_CAPS)
    caps.update(b.get("node_caps", {}) or {})
    merged["node_caps"] = caps
    # 列表/标量再归一
    merged["auto_optimize_nodes"] = list(b.get("auto_optimize_nodes", DEFAULT_BUDGET["auto_optimize_nodes"]))
    merged["safety_critical_types"] = list(b.get("safety_critical_types", DEFAULT_BUDGET["safety_critical_types"]))
    if merged["hard_cap_policy"] not in ("block", "warn"):
        merged["hard_cap_policy"] = "block"
    return merged


def load_meta(meta_path: Path) -> Dict:
    if meta_path and meta_path.exists():
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


# ---------------------------------------------------------------------------
# ⑥ safety 等级 S0–S4（蒸馏自 caveman engine/safety/safety.go:14-48）
# ---------------------------------------------------------------------------
# S0 字节安全（元数据/记账）：无载荷风险，可自由摘要。
# S1 提供商原生提示（缓存/路由）：config/tabular 类，低风险。
# S2 结构化（需 SDK 协作）：json 类，结构压缩安全。
# S3 行为级（eval-gated）：code/diff 类，压缩可能改变理解，需评估门控。
# S4 有损结构化（改模型可见字节，必须 CCR）：log / 含错误信号的载荷，压缩会丢行，
#      MUST 保留 recovery_handle（原文）方可压缩。
_SAFETY_BY_TYPE = {
    "config": "S1",
    "tabular": "S1",
    "json": "S2",
    "code": "S3",
    "diff": "S3",
    "html": "S3",
    "text": "S3",
    "search-result": "S3",
    "terminal": "S3",
    "toon": "S3",
    "a11y": "S3",
}
_S4_SIGNALS = re.compile(
    r"(ERROR|WARN|WARNING|FATAL|TRACE|Exception|Traceback|Error:|"
    r"failed|拒绝|失败|错误|不可逆|drop\s+table|truncate|rm\s+-rf)",
    re.I,
)


def safety_class_of(text: str, ptype: str = "auto") -> str:
    """对一段内容给出 S0–S4 风险分级（确定性，fail-closed 友好）。

    规则（蒸馏自 caveman engine/safety safety.go:14-48）：
      - log → S4（有损且常含错误行，压缩必丢行，MUST 保留 recovery_handle）
      - json/config/tabular → S2/S1（结构化，类型级摘要保错误键，风险低）
      - code/diff → S3（行为级，压缩可能改变理解，eval-gated）
      - 散文型（text/html/search-result/terminal/toon/a11y）：
          极小内容（≤120 token 估算）→ S0（无实质载荷风险）
          含错误/不可逆/失败信号 → S4（风格压缩可能丢关键行，必须有 recovery）
          其余 → S3
    注意：结构化类型按类型分级、不受尺寸影响——即便小 json 也按 S2 计，因为
    压缩是有损结构变换，需保留 recovery 方可。
    """
    if ptype == "auto":
        ptype = to.detect_type(text)
    if ptype == "log":
        return "S4"
    if ptype in ("json", "config", "tabular"):
        return _SAFETY_BY_TYPE.get(ptype, "S2")
    if ptype in ("code", "diff"):
        return "S3"
    # 散文型
    if to.estimate_tokens(text) <= 120:
        return "S0"
    if _S4_SIGNALS.search(text or ""):
        return "S4"
    return "S3"


_SAFETY_ORDER = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4}


# ---------------------------------------------------------------------------
# ⑤ BM25 式上下文裁剪（蒸馏自 caveman engine/contextwindow/contextwindow.go）
# ---------------------------------------------------------------------------

_CJK = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]")


def _tokenize(text: str) -> List[str]:
    """轻量分词：CJK 单字成词 + 英文/数字连续串。无外部依赖。"""
    text = (text or "").lower()
    tokens: List[str] = _CJK.findall(text)
    tokens += re.findall(r"[a-z0-9]+", text)
    return tokens


class _BM25:
    """Okapi BM25（k1=1.5, b=0.75，与 caveman 一致），纯 Python 近似。"""

    def __init__(self, docs: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs = [_tokenize(d) for d in docs]
        self.N = len(self.docs)
        self.avgdl = (sum(len(d) for d in self.docs) / self.N) if self.N else 0.0
        df: Dict[str, int] = {}
        for d in self.docs:
            for t in set(d):
                df[t] = df.get(t, 0) + 1
        self.df = df

    def _idf(self, t: str) -> float:
        n = self.N
        df = self.df.get(t, 0)
        return math.log(1.0 + (n - df + 0.5) / (df + 0.5))

    def score(self, idx: int, query_tokens: List[str]) -> float:
        d = self.docs[idx]
        dl = len(d)
        if dl == 0:
            return 0.0
        freq: Dict[str, int] = {}
        for t in d:
            freq[t] = freq.get(t, 0) + 1
        s = 0.0
        for t in query_tokens:
            if t not in freq:
                continue
            idf = self._idf(t)
            f = freq[t]
            s += idf * (f * (self.k1 + 1)) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        return s


def pack_context(items: List[Dict], budget_tokens: int, query: str = "",
                 reserve_tokens: int = 200, half_life_hours: float = 6.0,
                 error_boost: float = 0.8, pin_bonus: float = 1e6) -> Dict:
    """BM25 式上下文装袋（报告⑤）：按 score 降序贪心装袋至 budget-reserve；
    含 error_signal / pinned 的 item 强制保留（fail-closed：错误信号与钉住项不丢）；
    输出按原始时序重排以保持对话 chronology（与 caveman Pack 一致）。

    items: [{"id":, "text":, "priority":(0), "age_hours":(0), "error_signal":(False), "pinned":(False)}]
    返回 {"selected_ids","dropped_ids","packed_tokens","budget_tokens","score_map"}。
    """
    if not items:
        return {"selected_ids": [], "dropped_ids": [], "packed_tokens": 0,
                "budget_tokens": budget_tokens, "score_map": {}}
    bm25 = _BM25([it.get("text", "") for it in items])
    q_tokens = _tokenize(query)
    score_of: Dict[int, float] = {}
    for i, it in enumerate(items):
        s = bm25.score(i, q_tokens)
        s += float(it.get("priority", 0) or 0)
        age = float(it.get("age_hours", 0) or 0)
        s += math.exp(-age / half_life_hours)          # 近因权重（age=0 时≈1）
        if it.get("error_signal"):
            s += error_boost
        if it.get("pinned"):
            s += pin_bonus
        score_of[i] = s

    order = sorted(score_of, key=lambda i: -score_of[i])
    selected: List[int] = []
    packed = 0
    for i in order:
        it = items[i]
        tcost = to.estimate_tokens(it.get("text", ""))
        # 强制保留项：即便超预算也不丢（fail-closed）
        if it.get("pinned") or it.get("error_signal"):
            if i not in selected:
                selected.append(i)
                packed += tcost
            continue
        if packed + tcost <= max(budget_tokens - reserve_tokens, 0):
            selected.append(i)
            packed += tcost

    selected_sorted = sorted(selected)
    dropped = [i for i in range(len(items)) if i not in selected]
    return {
        "selected_ids": [items[i].get("id") for i in selected_sorted],
        "dropped_ids": [items[i].get("id") for i in dropped],
        "packed_tokens": packed,
        "budget_tokens": budget_tokens,
        "score_map": {items[i].get("id"): round(score_of[i], 3) for i in range(len(items))},
    }


# ---------------------------------------------------------------------------
# 流程级强约束：enforce_node（写入前预算闸门 + 自动优化）
# ---------------------------------------------------------------------------

def enforce_node(record: Dict, meta: Dict, content: str = None) -> Dict:
    """节点内容写入前预算闸门（强约束）：

    1. 取节点预算 cap；无 cap 定义 → PASS（不强制）。
    2. content 估算 token ≤ cap → PASS。
    3. 超 cap 且节点在 auto_optimize_nodes → 调 token_optimize 自动压缩；
       压缩后 ≤ cap 且关键事实保留率达标 → OPTIMIZED（用压缩文本 + 保留原文作 recovery）；
       否则（仍超硬上限或保留率不达标）→ 按 hard_cap_policy 处置：
         block → BLOCKED（fail-closed 保留原文，阻断"无损放行"）；
         warn  → WARN（保留原文并告警）。
    4. 超 cap 但节点未配自动优化 → 按 policy 处置（block/warn）。

    返回结构同时记录 safety_class（S0–S4）、before/after tokens、accuracy、warnings，
    供 COST_TRACK 落盘与 COST_AUDIT 汇总。
    """
    budget = load_budget(meta)
    node_id = record.get("node_id")
    if content is None:
        content = record.get("content", "")
    before = to.estimate_tokens(content)
    cap = budget["node_caps"].get(node_id)

    result: Dict = {
        "node_id": node_id,
        "before_tokens": before,
        "cap": cap,
        "status": "PASS",            # PASS / OPTIMIZED / BLOCKED / WARN
        "safety_class": None,
        "compressed_text": None,
        "original_text": content,    # fail-closed：原文始终保留
        "after_tokens": before,
        "saved_tokens": 0,
        "saved_pct": 0.0,
        "accuracy": None,
        "warnings": [],
    }

    if cap is None:
        # 未配置该节点预算 → 不强制（但记录）
        result["warnings"].append("节点 %s 未配置预算上限，跳过强约束" % node_id)
        return result

    if before <= cap:
        result["status"] = "PASS"
        return result

    # 超预算
    ptype = to.detect_type(content)
    sc = safety_class_of(content, ptype)
    result["safety_class"] = sc

    if node_id in budget["auto_optimize_nodes"] and content:
        opt = to.run_optimize(content, "auto", budget["auto_optimize_intensity"])
        after = opt["after_tokens"]
        acc = opt["accuracy"]
        crit_ok = (acc["critical_fact_retention_pct"] / 100.0) >= budget["critical_retention_min"]
        result["after_tokens"] = after
        result["saved_tokens"] = before - after
        result["saved_pct"] = opt["saved_pct"]
        result["accuracy"] = acc
        result["compressed_text"] = opt["compressed_text"]
        if after <= cap and crit_ok:
            result["status"] = "OPTIMIZED"
        else:
            # 仍超硬上限或关键事实保留率不达标 → fail-closed 不无损放行
            if budget["hard_cap_policy"] == "block":
                result["status"] = "BLOCKED"
                result["warnings"].append(
                    "节点 %s 超硬上限（%d>%d）且自动优化后仍超限或关键事实保留率<%.0f%%，"
                    "已阻断（fail-closed 保留原文，交由人工/下游处置）"
                    % (node_id, after, cap, budget["critical_retention_min"] * 100))
            else:
                result["status"] = "WARN"
                result["warnings"].append(
                    "节点 %s 超预算且自动优化后仍超限或保留率不达标，已保留原文并告警" % node_id)
    else:
        # 超预算但节点未配自动优化（N1/N2/N3/N6 等）→ 按 policy 处置
        if budget["hard_cap_policy"] == "block":
            result["status"] = "BLOCKED"
            result["warnings"].append(
                "节点 %s 超预算硬上限（%d>%d）且未配置自动优化，阻断写入" % (node_id, before, cap))
        else:
            result["status"] = "WARN"
            result["warnings"].append("节点 %s 超预算（%d>%d）且未配置自动优化，告警" % (node_id, before, cap))
    return result


# ---------------------------------------------------------------------------
# 流程级强约束：gate_index（全链路预算闸门核查 + 违规报告）
# ---------------------------------------------------------------------------

def gate_index(records: List[Dict], meta: Dict) -> Dict:
    """全链路预算闸门：逐节点合计 vs node_caps + 逐会话合计 vs session_cap，
    产出违规报告（level/node/session + over 量）。供 COST_AUDIT 在审计流程中调用。
    """
    budget = load_budget(meta)
    violations: List[Dict] = []
    node_totals: Dict[str, int] = {}
    session_totals: Dict[str, int] = {}

    for r in records:
        nid = r.get("node_id")
        toks = int(r.get("total_tokens",
                          (int(r.get("input_tokens", 0) or 0) + int(r.get("output_tokens", 0) or 0))))
        node_totals[nid] = node_totals.get(nid, 0) + toks
        sid = r.get("session_id", "_default")
        session_totals[sid] = session_totals.get(sid, 0) + toks

    for nid, tot in node_totals.items():
        cap = budget["node_caps"].get(nid)
        if cap and tot > cap:
            violations.append({"level": "node", "node_id": nid,
                               "total_tokens": tot, "cap": cap, "over": tot - cap})
    cap_s = budget["session_cap"]
    if cap_s:
        for sid, tot in session_totals.items():
            if tot > cap_s:
                violations.append({"level": "session", "session_id": sid,
                                   "total_tokens": tot, "cap": cap_s, "over": tot - cap_s})

    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "node_totals": node_totals,
        "session_totals": session_totals,
    }


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def runsyntax() -> int:
    # ⑤ pack_context：错误信号项强制保留，普通项按预算裁剪
    items = [
        {"id": "a", "text": "普通上下文：今天天气不错，我们讨论了项目进度。", "priority": 0, "age_hours": 2},
        {"id": "b", "text": "ERROR connection refused: db unreachable at 10:00:03", "error_signal": True},
        {"id": "c", "text": "用户询问如何配置 OAuth 回调地址，涉及 redirect_uri 参数。", "priority": 1, "age_hours": 1},
        {"id": "d", "text": "这是一段很长的无关闲聊内容，" * 20, "priority": 0, "age_hours": 10},
    ]
    pk = pack_context(items, budget_tokens=400, query="配置 OAuth 回调", reserve_tokens=50)
    assert pk["selected_ids"], "pack_context 返回空"
    assert "b" in pk["selected_ids"], "错误信号项 MUST 强制保留"
    assert "d" not in pk["selected_ids"], "低分长闲聊项应被裁剪"
    assert pk["packed_tokens"] <= 400, pk["packed_tokens"]

    # ⑥ safety_class_of（用足量内容越过 de minimis 阈值以触达类型级分级）
    big_cfg = "\n".join("key_%d = value_%d" % (i, i) for i in range(30))
    assert safety_class_of(big_cfg, "config") == "S1"
    big_json = json.dumps({"user": "alice", "role": "admin",
                           "perms": ["read", "write", "exec"], "note": "long configuration payload "
                           + "x" * 200})
    assert safety_class_of(big_json, "json") == "S2"
    big_code = "\n".join("def handler_%d(req):\n    return process(req, %d)\n" % (i, i) for i in range(8))
    assert safety_class_of(big_code, "code") == "S3"
    assert safety_class_of("2026-09-19 10:00 ERROR db unreachable", "log") == "S4"
    assert safety_class_of("hi", "text") == "S0"

    # enforce_node：大 log 内容超 N5 预算 → 自动优化至下限内，100% 关键事实
    big_log = "".join("2026-09-19 10:00:%02d INFO  worker tick\n" % i for i in range(60))
    big_log += "2026-09-19 10:05:00 ERROR db unreachable\n"
    meta = {"budget": {"node_caps": {"N5": 200}, "auto_optimize_nodes": ["N5"], "hard_cap_policy": "block"}}
    res = enforce_node({"node_id": "N5"}, meta, content=big_log)
    assert res["status"] == "OPTIMIZED", res
    assert res["after_tokens"] <= 200, res["after_tokens"]
    assert res["accuracy"]["critical_fact_retention_pct"] >= 100.0, res["accuracy"]

    # enforce_node：超极小硬上限 → 压缩后仍超限，BLOCKED（fail-closed 保留原文）
    dense = "value=" + " ".join(str(i) for i in range(2000)) + "\n"
    meta2 = {"budget": {"node_caps": {"N5": 10}, "auto_optimize_nodes": ["N5"], "hard_cap_policy": "block"}}
    res2 = enforce_node({"node_id": "N5"}, meta2, content=dense)
    # 极小 cap=10，压缩后通常仍超 → BLOCKED（fail-closed）
    assert res2["status"] in ("BLOCKED", "OPTIMIZED"), res2["status"]
    assert res2["original_text"] == dense, "fail-closed：原文必须保留"
    if res2["status"] == "BLOCKED":
        assert any("阻断" in w for w in res2["warnings"]), res2["warnings"]

    # gate_index：会话超 session_cap → 违规
    recs = [
        {"node_id": "N5", "total_tokens": 20000, "session_id": "s1"},
        {"node_id": "N7", "total_tokens": 15000, "session_id": "s1"},
    ]
    g = gate_index(recs, {"budget": {"session_cap": 30000}})
    assert g["passed"] is False
    assert any(v["level"] == "session" for v in g["violations"])

    print(
        "runsyntax OK: pack forced_keep_error=%s dropped_lowscore=%s | safety S0/S1/S2/S3/S4 graded | "
        "enforce OPTIMIZED after=%d crit=%.1f%% | gate violated=%s"
        % ("b" in pk["selected_ids"], "d" not in pk["selected_ids"],
           res["after_tokens"], res["accuracy"]["critical_fact_retention_pct"],
           not g["passed"])
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    here = Path(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description="tri-cost token 预算闸门与自动优化执行器")
    ap.add_argument("--runsyntax", action="store_true", help="合成数据冒烟自检")
    ap.add_argument("--meta", type=Path, default=here.parent / "_meta.json", help="_meta.json 路径")
    ap.add_argument("--enforce-node", action="store_true", help="对单节点执行预算闸门")
    ap.add_argument("--node", type=str, default=None, help="节点 id（N1–N8）")
    ap.add_argument("--content", type=str, default=None, help="节点内容文本")
    ap.add_argument("--content-file", type=Path, default=None, help="节点内容文件")
    ap.add_argument("--gate", action="store_true", help="全链路预算闸门核查")
    ap.add_argument("--index", type=Path, default=None, help="cost-index.jsonl 路径")
    ap.add_argument("--pack", action="store_true", help="BM25 式上下文裁剪")
    ap.add_argument("--items", type=str, default=None, help="items JSON 字符串")
    ap.add_argument("--items-file", type=Path, default=None, help="items JSON 文件")
    ap.add_argument("--budget", type=int, default=4000, help="pack 预算 token")
    ap.add_argument("--query", type=str, default="", help="pack 任务上下文 query")
    ap.add_argument("--safety", action="store_true", help="对文本做 S0–S4 风险分级")
    ap.add_argument("--text", type=str, default=None, help="safety 文本")
    ap.add_argument("--type", type=str, default="auto", help="safety 载荷类型")
    args = ap.parse_args()

    if args.runsyntax:
        return runsyntax()

    meta = load_meta(args.meta)

    if args.enforce_node:
        if not args.node:
            print("ERROR: --enforce-node 需 --node", file=sys.stderr)
            return 2
        content = args.content
        if args.content_file:
            content = args.content_file.read_text(encoding="utf-8")
        if content is None:
            content = ""
        print(json.dumps(enforce_node({"node_id": args.node}, meta, content=content),
                        ensure_ascii=False, indent=2))
        return 0

    if args.gate:
        if not args.index or not args.index.exists():
            print("ERROR: --gate 需 --index 文件", file=sys.stderr)
            return 2
        recs = []
        for line in args.index.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        print(json.dumps(gate_index(recs, meta), ensure_ascii=False, indent=2))
        return 0

    if args.pack:
        raw = args.items
        if args.items_file:
            raw = args.items_file.read_text(encoding="utf-8")
        if not raw:
            print("ERROR: --pack 需 --items 或 --items-file", file=sys.stderr)
            return 2
        items = json.loads(raw)
        print(json.dumps(pack_context(items, args.budget, query=args.query),
                        ensure_ascii=False, indent=2))
        return 0

    if args.safety:
        text = args.text or ""
        print(json.dumps({"detected_type": to.detect_type(text) if args.type == "auto" else args.type,
                          "safety_class": safety_class_of(text, args.type)},
                        ensure_ascii=False, indent=2))
        return 0

    print("ERROR: 需指定 --runsyntax / --enforce-node / --gate / --pack / --safety", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
