#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tri-cost 主动 token 节省方法论执行器（token_optimize.py）

职责：把 caveman 蒸馏出的 token 节省方法论（见 references/caveman-distill.md 七/八）
落成确定性、纯 Python、零外部运行时的可执行逻辑，使 tri-cost 从"只观测建议"
升级为"主动执行方法论 + 量化前后对比"：

  1. detect   启发式识别载荷类型（13 类，严格遵循 caveman detect 顺序，fail-open 归 text）
  2. compress 按类型/强度做规则级摘要 + 输出风格压缩（fail-closed：不确定即多保留）
  3. count    前后 token 估算（启发式，相对比可信；绝对值为近似）
  4. accuracy 关键事实保留率（内容准确性）—— 内容准确性对比的核心度量
  5. recovery 产出 recovery_handle（原文始终可从报告 original_text 找回，fail-closed）
  6. report   结构化前后对比（token 消耗对比 + 内容准确性对比）

设计边界（与 caveman 的 BSL-1.1 引擎严格区分）：
  - 本脚本是 caveman 方法论层的纯 Python 近似执行（prompt 级规则摘要 + 风格压缩），
    不打包、不调用 Go 代理/engine/SQLite CCR；方法源自 MIT 的 skills/caveman/SKILL.md，
    详见 references/caveman-distill.md 顶部许可边界声明。
  - 所有压缩默认 fail-closed：关键事实保留率低于阈值或命中安全信号时，保留原文或显式告警，
    绝不伪造"零 token 收益"。

用法：
  python token_optimize.py --input payload.txt --type auto --intensity full --report out.json
  python token_optimize.py --text "raw log..." --type log --intensity full
  python token_optimize.py --runsyntax
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# caveman detect 13 类（含 engine 内部类 toon/a11y 归并到 text/html 处理）
PAYLOAD_TYPES = [
    "json", "terminal", "diff", "html", "tabular",
    "code", "log", "search-result", "config", "text",
    "toon", "a11y",
]
DEFAULT_INTENSITY = "full"
INTENSITIES = ["lite", "full", "ultra"]

# Auto-Clarity 回退：命中这些信号时不压缩风格（保留常规表达，避免技术歧义/不可逆风险）
SAFETY_PATTERNS = [
    r"警告", r"危险", r"不可逆", r"谨慎", r"注意[:：]", r"务必",
    r"warning", r"danger", r"irreversible", r"caution", r"never", r"do not",
    r"rm\s+-rf", r"\bformat\b", r"password", r"secret", r"密钥", r"私钥",
    r"删除.*数据", r"drop\s+table", r"truncate",
]

# 风格压缩：安全可剥离的口语/填充前缀（中英文，语言无关、低风险）
FILLER_PREFIXES = [
    "okay, ", "ok, ", "sure, ", "certainly, ", "of course, ", "alright, ",
    "当然，", "好的，", "好的。", "嗯，", "让我", "我们来", "首先，", "首先。",
    "总的来说，", "综上所述，", "最后，", "接下来，", "简单来说，",
]
# ultra 额外剥离的话语标记（保守，仅去括号外连接语）
DISCOURSE_MARKERS = [
    "此外，", "另外，", "需要注意的是，", "值得注意的是，", "总而言之，",
    "综上所述，", "换言之，", "换句话说，", "其实，", "实际上，",
]

# 安全关键载荷类型：关键事实保留率阈值收紧（低于即告警）
SAFETY_CRITICAL_TYPES = {"log", "diff", "code", "json"}
LOW_RETENTION_THRESHOLD = 0.90

# 风格压缩仅适用于"散文型"载荷；结构化载荷（json/diff/log/code/tabular/config）
# 的压缩由类型级摘要完成，风格压缩会破坏其显著空白（缩进/对齐），故跳过。
PROSE_TYPES = {"text", "html", "search-result", "terminal", "toon", "a11y"}


# ---------------------------------------------------------------------------
# 1. token 估算（启发式）
# ---------------------------------------------------------------------------

_CJK_RE = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]")


def estimate_tokens(text: str) -> int:
    """启发式 token 估算：CJK 约 1.5 token/字，非 CJK 约 4 字符/token。

    绝对值为近似（置信度：低；依据：常识 common）；但同一文本前后用同一函数计数，
    相对比值（saved_pct）稳健，足以支撑前后对比决策。
    """
    if not text:
        return 0
    cjk = len(_CJK_RE.findall(text))
    non_cjk = len(text) - cjk
    return math.ceil(cjk * 1.5 + non_cjk / 4.0)


# ---------------------------------------------------------------------------
# 2. detect（载荷类型识别，fail-open）
# ---------------------------------------------------------------------------

def detect_type(text: str) -> str:
    """启发式识别载荷类型，严格遵循 caveman detect 顺序：
    json → terminal → diff → html → tabular → code → log → search-result → config → text。
    """
    t = text.strip()
    if not t:
        return "text"

    # json（先判定，结论性强）
    if t[0] in "{[":
        try:
            json.loads(t)
            return "json"
        except (json.JSONDecodeError, ValueError):
            pass

    # terminal（ANSI 转义是结论性信号）
    if "\x1b[" in text or re.search(r"\$\s*$|#\s*$|[A-Za-z_\\/]+>\s*$", text.rstrip()):
        return "terminal"

    # diff
    if re.search(r"^(diff --git|Index: |\+\+\+|--- )", text, re.MULTILINE) or "@@" in text:
        return "diff"

    # html（JSX 防误判：需有常见标签且标签数多于花括号）
    if re.search(r"<(!DOCTYPE|html|head|body|div|span|table|pre|code|h[1-6])", text, re.I):
        if text.count("<") >= text.count("{"):
            return "html"

    # tabular（多行同分隔符）
    lines = [ln for ln in t.splitlines() if ln.strip()]
    if len(lines) >= 3:
        delims = set()
        for ln in lines[:6]:
            for d in ("|", "\t", ","):
                if d in ln:
                    delims.add(d)
        if delims and all(any(d in ln for d in delims) for ln in lines[:6]):
            return "tabular"

    # code
    if re.search(r"\b(def |class |import |from \S+ import|function |public |private |void |const |let |var )", text):
        return "code"

    # log（时间戳 + 级别）
    if re.search(r"\b(INFO|WARN|WARNING|ERROR|FATAL|DEBUG|TRACE)\b.*\d{1,2}[:.]\d{2}", text) or \
       re.search(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}", text, re.MULTILINE):
        return "log"

    # search-result（大量 URL 命中）
    if len(re.findall(r"https?://", text)) >= 3:
        return "search-result"

    # config（key=value / ini / yaml 缩进键）
    if re.search(r"^[A-Za-z0-9_.\-]+ *= *\S", text, re.MULTILINE) or \
       re.search(r"^\s{2,}[A-Za-z0-9_.\-]+:", text, re.MULTILINE):
        return "config"

    return "text"


# ---------------------------------------------------------------------------
# 3. 各类型规则级压缩（返回 compressed, critical_units）
#    critical_units：用于内容准确性度量的"关键事实"字符串列表
# ---------------------------------------------------------------------------

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def compress_json(text: str) -> Tuple[str, List[str]]:
    try:
        obj = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return text, [text[:80]]
    crit: List[str] = []
    lines: List[str] = []

    def walk(o, prefix=""):
        if isinstance(o, dict):
            crit.extend(str(k) for k in o.keys())
            for k, v in o.items():
                keyl = f"{prefix}{k}"
                if isinstance(v, (dict, list)):
                    lines.append(f"{keyl}: <{type(v).__name__}>")
                    walk(v, keyl + ".")
                else:
                    sval = str(v)
                    if re.search(r"error|fail|exception|拒绝|失败|错误", keyl, re.I) or \
                       isinstance(v, str) and len(sval) > 60:
                        lines.append(f"{keyl}: {sval}")  # 错误/长值原样保留
                        crit.append(sval[:60])
                    else:
                        lines.append(f"{keyl}: {sval[:40]}")
        elif isinstance(o, list):
            if o:
                crit.append(f"{prefix}[0]")
                lines.append(f"array[{len(o)}] -> sample:")
                walk(o[0], prefix + "[0].")
            else:
                lines.append("[]")

    walk(obj)
    compressed = "JSON keys/structure (errors kept verbatim):\n" + "\n".join(lines[:200])
    return compressed, crit


def compress_diff(text: str) -> Tuple[str, List[str]]:
    crit: List[str] = []
    out: List[str] = []
    for ln in text.splitlines():
        if ln.startswith(("diff --git", "+++", "---", "@@")) or ln[:1] in "+-":
            out.append(ln)
            if ln[:1] in "+-":
                crit.append(ln)
        # 丢弃上下文行（以空格开头）
    compressed = "\n".join(out)
    return compressed, crit


def compress_log(text: str) -> Tuple[str, List[str]]:
    crit: List[str] = []
    out: List[str] = []
    lines = text.splitlines()
    for ln in lines:
        if re.search(r"\b(ERROR|WARN|WARNING|FATAL|TRACE)\b", ln, re.I) or \
           re.search(r"(Exception|Traceback|Error:|failed|拒绝|失败|错误)", ln) or \
           re.match(r"\s+at |^\s+File \"", ln):
            out.append(ln)
            crit.append(ln)
    # 保留首末行作锚点
    if lines:
        if lines[0] not in out:
            out.insert(0, lines[0])
        if lines[-1] not in out:
            out.append(lines[-1])
    compressed = "\n".join(out) if out else text[:200]
    return compressed, crit


def compress_code(text: str) -> Tuple[str, List[str]]:
    crit: List[str] = []
    out: List[str] = []
    buf_body = False
    for ln in text.splitlines():
        s = ln.strip()
        if re.match(r"(import |from \S+ import|#|def |class |public |private |protected |func |function |void |const |let |var |interface |type |struct |enum )", s):
            out.append(ln)
            crit.append(ln)
            if s.startswith(("def ", "class ", "func ", "function ", "public ", "private ", "protected ")):
                buf_body = True
            else:
                buf_body = False
        elif buf_body and s == "":
            out.append("    ...")
            buf_body = False
        elif buf_body:
            # 吸收函数体，不输出（已用 ... 占位）
            if s.startswith(("def ", "class ", "func ", "}", "public ", "private ")):
                out.append("    ...")
                out.append(ln)
                crit.append(ln)
                buf_body = True
        # 其余函数体行丢弃
    compressed = "\n".join(out) if out else text[:200]
    return compressed, crit


def compress_html(text: str) -> Tuple[str, List[str]]:
    crit: List[str] = []
    # 去 script/style
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.S | re.I)
    # 抽取标题 / 代码 / 链接文本
    headings = re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", t, re.S | re.I)
    codes = re.findall(r"<(pre|code)[^>]*>(.*?)</\1>", t, re.S | re.I)
    for h in headings:
        clean = re.sub(r"<[^>]+>", "", h).strip()
        if clean:
            crit.append(clean)
    for _, c in codes:
        crit.append(re.sub(r"<[^>]+>", "", c).strip()[:60])
    # 去所有标签转纯文本
    plain = re.sub(r"<[^>]+>", " ", t)
    plain = re.sub(r"\s+", " ", plain).strip()
    compressed = "HTML headings/code (tags stripped):\n" + "\n".join(
        ["# " + h for h in headings if h.strip()]
    )
    if codes:
        compressed += "\n```\n" + "\n".join(c[:120] for _, c in codes[:20]) + "\n```"
    return (compressed if compressed.strip() else plain[:200]), crit


def compress_terminal(text: str) -> Tuple[str, List[str]]:
    crit: List[str] = []
    lines = [ln for ln in text.splitlines() if ln.strip()]
    # 去 ANSI 噪声
    clean = re.sub(r"\x1b\[[0-9;]*m", "", text)
    out: List[str] = []
    for ln in clean.splitlines():
        if re.search(r"(error|fail|exception|denied|拒绝|失败|错误|exit code|returned)", ln, re.I):
            out.append(ln.strip())
            crit.append(ln.strip())
    if lines:
        out.append(lines[-1].strip())  # 末行结论
        crit.append(lines[-1].strip())
    compressed = "\n".join(out) if out else clean.strip()[:200]
    return compressed, crit


def compress_tabular(text: str) -> Tuple[str, List[str]]:
    crit: List[str] = []
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return text[:200], [text[:80]]
    header = lines[0]
    crit.append(header)
    out = [header]
    for ln in lines[1:]:
        if re.search(r"(error|fail|change|diff|变动|异常|不一致|ERROR)", ln, re.I):
            out.append(ln)
            crit.append(ln)
    # 保留首末数据行
    if len(lines) > 1:
        if lines[-1] not in out:
            out.append(lines[-1])
            crit.append(lines[-1])
    compressed = "\n".join(out) if len(out) > 1 else text[:200]
    return compressed, crit


def compress_config(text: str) -> Tuple[str, List[str]]:
    crit: List[str] = []
    out: List[str] = []
    for ln in text.splitlines():
        if re.search(r"(error|fail|secret|password|key|token|异常|失败|错误)", ln, re.I):
            out.append(ln)
            crit.append(ln)
        elif "=" in ln or ":" in ln:
            out.append(ln)
            crit.append(ln.split("=")[0].split(":")[0].strip())
    compressed = "\n".join(out) if out else text[:200]
    return compressed, crit


def compress_search_result(text: str) -> Tuple[str, List[str]]:
    crit: List[str] = []
    lines = [ln for ln in text.splitlines() if ln.strip()]
    out: List[str] = []
    urls = re.findall(r"https?://\S+", text)
    crit.extend(urls[:10])
    # 保留首末命中 + 含诊断的行
    for i, ln in enumerate(lines):
        if i in (0, len(lines) - 1) or re.search(r"(error|not found|诊断|诊断结果|score|相关)", ln, re.I):
            out.append(ln)
            crit.append(ln[:60])
    compressed = "\n".join(out) if out else text[:200]
    return compressed, crit


def compress_text(text: str) -> Tuple[str, List[str]]:
    """通用文本：保留含代码/数字/技术关键词的实质句，丢弃纯口语/过渡句。"""
    crit: List[str] = []
    out: List[str] = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if re.search(r"(`{1,3}|def |class |\d{2,}|http|错误|失败|异常|必须|应该|步骤|参数|返回)", s) or \
           len(s) < 40:
            out.append(s)
            crit.append(s)
    compressed = "\n".join(out) if out else text[:200]
    return compressed, crit


# toon / a11y 归并：toon 当 text，a11y 当 html 的辅助树，简化处理
_TYPE_HANDLERS = {
    "json": compress_json,
    "diff": compress_diff,
    "log": compress_log,
    "code": compress_code,
    "html": compress_html,
    "terminal": compress_terminal,
    "tabular": compress_tabular,
    "config": compress_config,
    "search-result": compress_search_result,
    "text": compress_text,
    "toon": compress_text,
    "a11y": compress_html,
}


# ---------------------------------------------------------------------------
# 4. 输出风格压缩（N7/N8，强度档位）
# ---------------------------------------------------------------------------

def compress_style(text: str, intensity: str) -> Tuple[str, List[str]]:
    """风格压缩：删填充/客套/emoji/装饰表，保代码与错误串。fail-closed 友好。"""
    crit: List[str] = []
    # 关键事实：代码块与含数字/技术词的片段，须保留
    code_blocks = re.findall(r"```.*?```", text, re.S)
    crit.extend([c[:80] for c in code_blocks])
    for m in re.findall(r"(`[^`]+`|\b\w*\d\w*\b)", text):
        crit.append(m)

    s = text
    # 去掉 emoji
    s = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\ufe0f]", "", s)
    # 去填充前缀
    for p in FILLER_PREFIXES:
        if s.lower().startswith(p.lower()):
            s = s[len(p):]
            break
    if intensity in ("full", "ultra"):
        # 仅合并多余空行（绝不合并行内多空格，避免破坏代码/表格/缩进）
        s = re.sub(r"\n{3,}", "\n\n", s)
        # 删纯装饰性 markdown 表格分隔行
        s = re.sub(r"^\s*\|[\s:|-]+\|\s*$", "", s, flags=re.M)
    if intensity == "ultra":
        for m in DISCOURSE_MARKERS:
            s = s.replace(m, "")
    compressed = s.strip()
    return compressed, crit


# ---------------------------------------------------------------------------
# 5. 内容准确性度量（原子事实保留率 + 关键事实保障）
# ---------------------------------------------------------------------------

def _extract_facts(text: str) -> List[str]:
    """抽取原子事实：反引号代码、数字、CJK 双字以上词、英文词（>=3）。
    用于内容准确性度量——原子级、对前缀/空白裁剪不敏感。"""
    facts: List[str] = []
    facts += re.findall(r"`[^`]+`", text)
    facts += re.findall(r"\d+(?:\.\d+)?", text)
    facts += re.findall(r"[\u3400-\u9fff]{2,}", text)
    facts += re.findall(r"[A-Za-z]{3,}", text)
    # 去重保序
    seen = set()
    out = []
    for f in facts:
        if f.lower() not in seen:
            seen.add(f.lower())
            out.append(f)
    return out


def measure_accuracy(original: str, compressed: str, ptype: str) -> Dict:
    """内容准确性对比：
    - retention_pct：原子事实（代码/数字/中英关键词）子串保留率（表面保真度）
    - critical_fact_retention_pct：类型级关键事实（错误行/变更行/签名等）保留率（重要事实零丢失保障）
    """
    ofacts = _extract_facts(original)
    comp_norm = _norm(compressed)
    kept = []
    dropped = []
    for f in ofacts:
        if _norm(f) in comp_norm:
            kept.append(f[:60])
        else:
            dropped.append(f[:60])
    total = len(ofacts)
    ret = round(len(kept) / total * 100, 2) if total else 100.0

    # 类型级关键事实（重要事实）保障
    # 结构化类型（log/diff/code/json）用类型处理器抽取的重要行（错误行/变更行/签名/错误键）；
    # 散文型用原子事实，避免整行作为单位被前缀裁剪破坏。
    if ptype in ("log", "diff", "code", "json"):
        handler = _TYPE_HANDLERS.get(ptype, compress_text)
        _, crit = handler(original)
    else:
        crit = _extract_facts(original)
    if not crit:
        crit = [original[:80]]
    crit_kept = sum(1 for c in crit if c and _norm(c) in comp_norm)
    crit_total = len(crit)
    crit_ret = round(crit_kept / crit_total * 100, 2) if crit_total else 100.0

    return {
        "method": "原子事实（代码/数字/中英关键词）子串保留率 + 类型级关键事实保障",
        "retention_pct": ret,
        "critical_fact_retention_pct": crit_ret,
        "fact_total": total,
        "dropped_facts_sample": dropped[:10],
    }


# ---------------------------------------------------------------------------
# 6. 主执行
# ---------------------------------------------------------------------------

def run_optimize(text: str, ptype: str, intensity: str) -> Dict:
    if ptype == "auto":
        ptype = detect_type(text)

    # 安全信号 → Auto-Clarity 回退（不压风格，保留常规表达）
    safety_hit = any(re.search(p, text, re.I) for p in SAFETY_PATTERNS)
    # 风格压缩仅对散文型载荷生效（结构化载荷由类型级摘要处理，避免破坏空白）
    style_applied = (intensity != "off") and (not safety_hit) and (ptype in PROSE_TYPES)

    # 类型级摘要
    handler = _TYPE_HANDLERS.get(ptype, compress_text)
    summarized, _ = handler(text)

    # 风格压缩（仅对文本类/已摘要结果做）
    if style_applied:
        final_text, _ = compress_style(summarized if ptype != "text" else text, intensity)
    else:
        final_text = summarized if ptype != "text" else text

    before = estimate_tokens(text)
    after = estimate_tokens(final_text)
    saved = before - after
    saved_pct = round(saved / before * 100, 2) if before else 0.0

    acc = measure_accuracy(text, final_text, ptype)

    warnings = []
    if safety_hit:
        warnings.append("命中安全/不可逆信号，已按 Auto-Clarity 回退保留常规表达（未压风格）")
    if ptype in SAFETY_CRITICAL_TYPES and acc["critical_fact_retention_pct"] / 100 < LOW_RETENTION_THRESHOLD:
        warnings.append(
            f"安全关键类型({ptype})关键事实保留率 {acc['retention_pct']}% < "
            f"{int(LOW_RETENTION_THRESHOLD*100)}%，建议人工核对或 fail-closed 保留原文"
        )

    return {
        "methodology_source": "蒸馏自 caveman (JuliusBrussee/caveman v2.7.0) MIT 方法层；不含 BSL-1.1 引擎",
        "detected_type": ptype,
        "intensity": intensity,
        "style_applied": style_applied,
        "before_tokens": before,
        "after_tokens": after,
        "saved_tokens": saved,
        "saved_pct": saved_pct,
        "accuracy": acc,
        "recovery_handle": "原文见本报告 original_text 字段（fail-closed 可找回）",
        "compressed_text": final_text,
        "original_text": text,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# 7. 自检
# ---------------------------------------------------------------------------

def runsyntax() -> int:
    sample_log = (
        "2026-09-19 10:00:01 INFO  starting worker pool\n"
        "2026-09-19 10:00:02 INFO  loaded 120 tasks\n"
        "2026-09-19 10:00:03 ERROR connection refused: db unreachable\n"
        "2026-09-19 10:00:03 TRACE  retry 1/3\n"
        "2026-09-19 10:00:09 INFO  worker finished\n"
    )
    r = run_optimize(sample_log, "auto", "full")
    assert r["detected_type"] == "log", r["detected_type"]
    assert r["after_tokens"] < r["before_tokens"], (r["after_tokens"], r["before_tokens"])
    assert r["saved_tokens"] > 0
    assert r["accuracy"]["critical_fact_retention_pct"] >= 100.0, r["accuracy"]

    sample_diff = (
        "diff --git a/foo.py b/foo.py\n--- a/foo.py\n+++ b/foo.py\n"
        "@@ -1,3 +1,3 @@\n def a():\n-    return 1\n+    return 2\n context line\n"
    )
    r2 = run_optimize(sample_diff, "auto", "full")
    assert r2["detected_type"] == "diff"
    assert "+    return 2" in r2["compressed_text"]
    assert r2["accuracy"]["critical_fact_retention_pct"] >= 100.0

    # 安全回退：含不可逆信号时不压风格
    danger = "警告：此操作不可逆，将删除全部数据。请谨慎确认。"
    r3 = run_optimize(danger, "text", "full")
    assert r3["style_applied"] is False, "safety fallback failed"
    assert r3["warnings"]

    print(
        "runsyntax OK: log saved_pct=%.1f%% crit_acc=%.1f%% | diff crit_acc=%.1f%% | safety_fallback=%s"
        % (r["saved_pct"], r["accuracy"]["critical_fact_retention_pct"],
           r2["accuracy"]["critical_fact_retention_pct"], not r3["style_applied"])
    )
    return 0


# ---------------------------------------------------------------------------
# 8. CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="tri-cost 主动 token 节省方法论执行器")
    ap.add_argument("--input", type=Path, default=None, help="原始文本文件（载荷/输出草稿）")
    ap.add_argument("--text", type=str, default=None, help="直接传入原始文本")
    ap.add_argument("--type", type=str, default="auto",
                    help="载荷类型: auto/" + "/".join(PAYLOAD_TYPES))
    ap.add_argument("--intensity", type=str, default=DEFAULT_INTENSITY,
                    help="风格压缩强度: " + "/".join(INTENSITIES) + "/off")
    ap.add_argument("--report", type=Path, default=None, help="输出 JSON 报告路径")
    ap.add_argument("--runsyntax", action="store_true", help="合成数据冒烟自检")
    args = ap.parse_args()

    if args.runsyntax:
        return runsyntax()

    if args.input:
        text = args.input.read_text(encoding="utf-8")
    elif args.text is not None:
        text = args.text
    else:
        print("ERROR: 需提供 --input 或 --text", file=sys.stderr)
        return 2

    if args.intensity not in INTENSITIES + ["off"]:
        print("ERROR: --intensity 须为 " + "/".join(INTENSITIES) + "/off", file=sys.stderr)
        return 2

    result = run_optimize(text, args.type, args.intensity)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        print("report -> %s" % args.report)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
