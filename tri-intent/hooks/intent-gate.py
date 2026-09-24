#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""intent-gate: 意图识别结果呈现器（可选轻量复述工具）。

定位：意图识别产出快照后的**可选**复述工具。位于「产出快照」之后、
「交接下游 skill」之前。核心职责：
  1. 依据 L2 意图编码，按 SKILL.md §四 落盘规则计算「落盘去向」(Flow 三态)；
  2. 依据置信度分档（高/中/低）决定是否强制复述或强制回退 clarify-gate；
  3. 读取快照的结构化字段，渲染轻量复述文案供用户发现明显误识别；
  4. 输出下游 skill 路由建议 + 机器可用 slug，供上层 Agent 据此交接与依赖检测。

注意：本脚本不再是「执行前闸门」，不编排下游执行链路，不审批执行计划。
复述在高置信且无竞争意图时可跳过；中/低置信时由本脚本强制要求。

用法：
  # 仅按意图编码计算落盘去向与路由建议（快速判定）
  python3 intent-gate.py --intent I13
  # 中文别名同样可用
  python3 intent-gate.py --intent 代码审查
  # 子类覆写路由（workflow | loop | music）
  python3 intent-gate.py --intent I15 --subtype music --json
  # 带置信度判定（<0.60 强制澄清，<0.85 强制复述）
  python3 intent-gate.py --intent I11 --confidence 0.72 --margin 0.10 --json
  # 结合快照渲染完整复述文案 + 路由 JSON
  python3 intent-gate.py --snapshot .tribro/snapshots/I13_xxx.md
  # 输出纯 JSON（供程序消费）
  python3 intent-gate.py --intent I11 --json

退出码：0=正常；2=输入错误/意图无法识别/置信度非法。
"""

import argparse
import json
import re
import sys

# ---- 落盘规则表：与 SKILL.md §四 保持单一事实源 ----------------------------

# 不落盘（免打断/即时响应）
NO_PERSIST_INTENTS = {"I17", "I18", "I19", "I20", "M05"}

FLOW_PERSIST = "落盘快照"
FLOW_NO_PERSIST = "不落盘"
FLOW_CLARIFY = "先澄清"

INTENT_NAMES = {
    "I01": "信息查询", "I02": "概念解释", "I03": "建议咨询", "I04": "决策辅助",
    "I05": "推理计算", "I06": "内容生成", "I07": "内容改写", "I08": "翻译转换",
    "I09": "总结提炼", "I10": "分析处理", "I11": "编码开发", "I12": "调试修复",
    "I13": "规划拆解", "I14": "操作执行", "I15": "多媒体生成", "I16": "头脑风暴",
    "I17": "角色扮演", "I18": "情感陪伴", "I19": "闲聊娱乐", "I20": "观点表达",
    "I21": "蒸馏造物",
    "CR": "代码审查",
    "M01": "澄清追问", "M02": "纠错反馈", "M03": "追加细化", "M04": "能力询问",
    "M05": "中止确认",
}

# 「代码审查」的中文别名 → 规范编码 CR（历史上以字符串「代码审查」作为路由键）
INTENT_ALIASES = {
    "代码审查": "CR", "CODE-REVIEW": "CR", "CODE REVIEW": "CR", "REVIEW": "CR",
    "I21.DISTILL": "I21",
}

# 下游 skill 路由建议表（人类可读名 + 机器可用 slug 双轨）
ROUTE_SUGGESTIONS = {
    "I01": "咨询作答 skill", "I02": "咨询作答 skill", "I03": "咨询作答 skill",
    "I04": "咨询作答 skill", "I05": "咨询作答 skill",
    "I06": "内容处理 skill", "I07": "内容处理 skill", "I08": "内容处理 skill",
    "I09": "内容处理 skill", "I10": "内容处理 skill",
    "I11": "编码开发 skill",
    "I12": "调试修复 skill",
    "CR": "代码审查 skill",
    "I13": "规划拆解 skill",
    "I14": "操作执行 skill",
    "I15": "多媒体生成 skill",
    "I16": "头脑风暴 skill",
    "I21": "蒸馏造物 skill",
    "I17": "表达陪伴 skill（直接自然回应）", "I18": "表达陪伴 skill（直接自然回应）",
    "I19": "表达陪伴 skill（直接自然回应）", "I20": "表达陪伴 skill（直接自然回应）",
    "M01": "元操作处理 skill", "M02": "元操作处理 skill",
    "M03": "元操作处理 skill", "M04": "元操作处理 skill",
    "M05": "即时叫停/放行（不交接）",
}

# L2 意图 → 下游 skill slug（供「下游依赖检测」直接消费，避免中文泛称无法映射目录）
# 本分支为**编程工作流专线**：未包含的落点映射为空串，表示「无下游、跳过依赖检测」（与 M05 同处置）。
ROUTE_SLUGS = {
    # —— 本分支有下游的落点 ——
    "I11": "tri-coding",
    "I12": "tri-fix",
    "CR": "tri-review",
    "I13": "tri-plan",
    "I14": "tri-action",
    "I21": "tri-god",
    "M01": "tri-meta", "M02": "tri-meta", "M03": "tri-meta", "M04": "tri-meta",
    # —— 本分支未包含（分类保留、无下游）——
    "I01": "", "I02": "", "I03": "", "I04": "", "I05": "",
    "I06": "", "I07": "", "I08": "", "I09": "",
    "I10": "",   # I10 默认无下游；三个子类见下方 SUBTYPE_SLUGS
    "I15": "", "I16": "",
    "I17": "", "I18": "", "I19": "", "I20": "",
    "M05": "",
}

# 子类覆写：(意图, 子类键) → slug。子类由 tri-intent 依任务要点语义判定后传入
SUBTYPE_SLUGS = {
    ("I13", "workflow"): "tri-workflow",
    ("I14", "workflow"): "tri-workflow",
    ("I14", "loop"): "tri-loop",
    # 全生命周期（SDLC）子类：三个 L2 共用同一子类键，优先级高于 workflow / loop 子类
    ("I11", "sdlc"): "tri-sdlc",
    ("I13", "sdlc"): "tri-sdlc",
    ("I14", "sdlc"): "tri-sdlc",
    # I11 编码开发子类
    ("I11", "frontend-design"): "tri-frontend-design",
    ("I11", "motion"): "tri-lottie",
    ("I11", "pm-prototype"): "tri-prototype",
    # I10 分析处理子类（本分支全部保留）
    ("I10", "arch-viz"): "tri-html",
    ("I10", "audit-checklist"): "tri-checklist",
    ("I10", "code-analyzer"): "tri-code-analyzer",
}

# ---- 置信度阈值（单一事实源，与 SKILL.md §置信度机制 对齐）------------------

CONF_HIGH = 0.85      # ≥ 高置信：直接落盘交接，可跳过复述
CONF_LOW = 0.60       # < 低置信：不直接交接，强制走 clarify-gate
CONF_MARGIN = 0.15    # 主次意图分差 < 该值 → 竞争意图，强制复述并列候选


def normalize_intent(intent):
    """将输入的意图标识归一化为规范编码（支持中文别名，如「代码审查」→ CR）。"""
    raw = (intent or "").strip()
    code = raw.upper()
    code = INTENT_ALIASES.get(code, INTENT_ALIASES.get(raw, code))
    if code not in INTENT_NAMES:
        raise ValueError(f"无法识别的意图编码: {intent!r}")
    return code


def resolve_slug(code, subtype=None):
    """解析下游 skill slug，子类命中时覆写默认 slug。"""
    if subtype:
        key = (code, subtype.strip().lower())
        if key in SUBTYPE_SLUGS:
            return SUBTYPE_SLUGS[key]
    return ROUTE_SLUGS.get(code, "")


def grade_confidence(confidence, margin=None):
    """将置信度数值分档，返回 (档位, 是否需强制澄清, 是否需强制复述, 说明)。

    档位：高(≥0.85) / 中(0.60–0.85) / 低(<0.60)；
    margin 为主次意图分差，< CONF_MARGIN 视为竞争意图，强制复述。
    confidence 为 None 时视为未评估，按「中」保守处理。
    """
    if confidence is None:
        return "未评估", False, True, "未提供置信度，按中档保守处理：强制轻量复述一次"

    try:
        c = float(confidence)
    except (TypeError, ValueError):
        raise ValueError(f"置信度必须为 0–1 之间的数值: {confidence!r}")
    if not 0.0 <= c <= 1.0:
        raise ValueError(f"置信度超出 [0,1] 区间: {c}")

    competing = margin is not None and float(margin) < CONF_MARGIN

    if c < CONF_LOW:
        return "低", True, True, (
            f"置信度 {c:.2f} < {CONF_LOW}，识别不可靠，强制走 clarify-gate 澄清后重路由"
        )
    if c < CONF_HIGH:
        note = f"置信度 {c:.2f} 处于 [{CONF_LOW}, {CONF_HIGH})，强制轻量复述一次以便用户纠偏"
        if competing:
            note += f"；且主次意图分差 {float(margin):.2f} < {CONF_MARGIN}，存在竞争意图"
        return "中", False, True, note
    if competing:
        return "高", False, True, (
            f"置信度 {c:.2f} 达高档，但主次意图分差 {float(margin):.2f} < {CONF_MARGIN}，"
            "存在竞争意图，仍强制复述并列出候选"
        )
    return "高", False, False, f"置信度 {c:.2f} ≥ {CONF_HIGH}，识别可靠，可跳过复述直接交接"


def decide_flow(intent, gate_clarify=False, confidence=None, margin=None):
    """根据 L2 意图编码与置信度计算落盘去向。

    参数:
        intent: L2 意图编码，如 "I13"（支持中文别名「代码审查」）
        gate_clarify: clarify-gate 是否命中（需先澄清）
        confidence: 意图识别置信度 0–1，None 表示未评估
        margin: 主次意图分差，用于竞争意图检测
    返回:
        (flow, reason, conf_info) 三元组
    """
    code = normalize_intent(intent)
    grade, force_clarify, need_recap, conf_note = grade_confidence(confidence, margin)
    conf_info = {
        "grade": grade, "note": conf_note,
        "need_recap": need_recap, "force_clarify": force_clarify,
    }

    # Expressing/M05 免打断：即使低置信也不走落盘澄清，仅在对话内即时对齐
    if code in NO_PERSIST_INTENTS:
        conf_info["force_clarify"] = False
        return FLOW_NO_PERSIST, "表达陪伴/中止确认，免打断即时响应，不落盘", conf_info

    # 先澄清优先级最高：显式命中 clarify-gate，或置信度低于下限
    if gate_clarify:
        return FLOW_CLARIFY, "需求模糊/矛盾/缺关键信息，clarify-gate 命中", conf_info
    if force_clarify:
        return FLOW_CLARIFY, conf_note, conf_info

    return FLOW_PERSIST, f"{code} {INTENT_NAMES[code]}，产出快照并交接下游 skill", conf_info


# ---- 快照解析（只读结构化字段，不重新做意图判定）----------------

def parse_snapshot(text):
    """从快照文本中抽取渲染复述所需的结构化字段。"""
    data = {
        "intent_l1": "", "intent_l2": "", "summary": "",
        "task_points": [], "route_suggestion": "",
        "confidence": None, "margin": None,
    }
    # §三 结构化结论 yaml 字段
    m = re.search(r"L1_交互类型:\s*(.+)", text)
    if m:
        data["intent_l1"] = m.group(1).strip()
    m = re.search(r"L2_核心意图:\s*(.+)", text)
    if m:
        data["intent_l2"] = m.group(1).strip()
    m = re.search(r"一句话复述:\s*(.+)", text)
    if m:
        data["summary"] = m.group(1).strip()
    m = re.search(r"下游路由建议:\s*(.+)", text)
    if m:
        data["route_suggestion"] = m.group(1).strip()
    # 置信度（可选字段，快照 §三 intent 区）
    m = re.search(r"置信度:\s*([0-9.]+)", text)
    if m:
        try:
            data["confidence"] = float(m.group(1))
        except ValueError:
            pass
    m = re.search(r"主次分差:\s*([0-9.]+)", text)
    if m:
        try:
            data["margin"] = float(m.group(1))
        except ValueError:
            pass

    # 任务要点
    m = re.search(r"任务要点:\s*\n(.*?)(?=\n\S|\Z)", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"\s*-\s*(.+)", line)
            if mm:
                v = mm.group(1).strip()
                if v and not v.startswith("<"):
                    data["task_points"].append(v)
    return data


# ---- 轻量复述文案渲染 ------------------------------------------------------

def render_recap(intent_code, flow, data=None, conf_info=None, slug=""):
    data = data or {}
    conf_info = conf_info or {}
    l2 = data.get("intent_l2") or f"{intent_code} {INTENT_NAMES.get(intent_code, '')}"
    l1 = data.get("intent_l1") or "-"
    summary = data.get("summary") or "<见快照 §三 一句话复述>"
    points = data.get("task_points") or ["<见快照 §三 任务要点>"]
    route = data.get("route_suggestion") or ROUTE_SUGGESTIONS.get(intent_code, "<待定>")

    lines = []
    lines.append("# ===== 意图识别结果（可选轻量复述）=====")
    lines.append(f"【我理解你要】：{summary}")
    lines.append(f"【意图类型】：{l1} / {l2}")
    lines.append("【任务要点】：")
    for i, p in enumerate(points, 1):
        lines.append(f"  {i}. {p}")
    lines.append(f"【下游路由】：{route}" + (f"（{slug}）" if slug else ""))
    if conf_info:
        lines.append(f"【识别置信度】：{conf_info.get('grade', '未评估')} — {conf_info.get('note', '')}")
    if flow == FLOW_NO_PERSIST:
        lines.append(f"【落盘去向】：{flow}（直接自然回应，不生成快照）")
    elif flow == FLOW_CLARIFY:
        lines.append(f"【落盘去向】：{flow}（先走 clarify-gate 补齐后再识别）")
    else:
        lines.append(f"【落盘去向】：{flow}（已产出快照，交接下游 skill）")
    lines.append("")
    lines.append("如发现明显误识别，请指出，我将更新快照。")
    lines.append("如理解正确，无需回复——快照已交接下游 skill 处理。")
    lines.append("# ======================================")
    return "\n".join(lines)


# ---- CLI --------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="intent-gate 意图识别结果呈现器（可选轻量复述）")
    ap.add_argument("--intent", help="L2 意图编码，如 I13")
    ap.add_argument("--snapshot", help="快照 snapshot.md 路径（解析并渲染复述）")
    ap.add_argument("--clarify", action="store_true", help="clarify-gate 命中（先澄清）")
    ap.add_argument("--confidence", type=float, default=None,
                    help="意图识别置信度 0–1，<0.60 强制澄清，<0.85 强制复述")
    ap.add_argument("--margin", type=float, default=None,
                    help="主次意图分差，<0.15 视为竞争意图强制复述")
    ap.add_argument("--subtype", default=None,
                    help="子类覆写键：workflow | loop | music")
    ap.add_argument("--json", action="store_true", help="仅输出落盘决策与路由 JSON")
    args = ap.parse_args(argv)

    data = None
    intent_code = (args.intent or "").strip()

    if args.snapshot:
        try:
            with open(args.snapshot, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"[intent-gate] 读取快照失败: {e}", file=sys.stderr)
            return 2
        data = parse_snapshot(text)
        if not intent_code:
            l2 = data.get("intent_l2", "")
            m = re.match(r"(I\d{2}|M\d{2})", l2)
            if m:
                intent_code = m.group(1)
            elif "代码审查" in l2 or "code review" in l2.lower():
                intent_code = "CR"

    if not intent_code:
        print("[intent-gate] 缺少意图编码：请用 --intent 或提供含 L2_核心意图 的快照",
              file=sys.stderr)
        return 2

    # CLI 参数优先于快照内字段
    confidence = args.confidence
    margin = args.margin
    if data:
        if confidence is None:
            confidence = data.get("confidence")
        if margin is None:
            margin = data.get("margin")

    try:
        code = normalize_intent(intent_code)
        flow, reason, conf_info = decide_flow(
            code, gate_clarify=args.clarify, confidence=confidence, margin=margin
        )
    except ValueError as e:
        print(f"[intent-gate] {e}", file=sys.stderr)
        return 2

    slug = resolve_slug(code, args.subtype)
    decision = {
        "intent": code,
        "intent_name": INTENT_NAMES.get(code, ""),
        "flow": flow,
        "route_suggestion": ROUTE_SUGGESTIONS.get(code, ""),
        "route_slug": slug,
        "confidence": confidence,
        "confidence_grade": conf_info["grade"],
        "need_recap": conf_info["need_recap"],
        "force_clarify": conf_info["force_clarify"],
        "reason": reason,
    }

    if args.json:
        print(json.dumps(decision, ensure_ascii=False, indent=2))
        return 0

    print(render_recap(code, flow, data, conf_info, slug))
    print()
    print("---- 机器可读决策 ----")
    print(json.dumps(decision, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
