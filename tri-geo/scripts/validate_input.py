#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数校验（validate_input.py）——「智引」(tri-geo) 确定性脚本 01/09

职责（对应设计指南 §3.1）：
    · URL / 域名合法性校验与规范化（补 scheme、去空白、提取域名）
    · 品牌名 / 品类必填项检查（按模式差异化要求）
    · 目标引擎编码白名单校验（国内 8 引擎）
    · 输入规范化，产出下游脚本统一消费的 params JSON

设计约束：
    · 纯标准库，零第三方依赖
    · 同输入多次运行结果完全一致（默认不输出时间戳；--stamp 才注入）
    · 校验判定 MUST 由本脚本完成，NEVER 交给 prompt 自觉

用法：
    python validate_input.py --url example.com --brand 格力 --product-type 空调 \
        --mode audit --engines deepseek,doubao --json
    python validate_input.py --domain example.com --mode quick --json
    python validate_input.py --url https://x.cn --mode cn_fit --json

退出码：
    0  校验通过（放行）
    1  缺必填项（Agent MUST 用 AskUserQuestion 补齐后重入，NEVER 猜测填充）
    2  非法输入（URL 不合法 / 引擎编码越界 / 模式未知）——终止，不降级
    64 参数或环境错误
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

SCHEMA_VERSION = "1.0"
TOOL_NAME = "validate_input.py"

# 国内目标引擎白名单（设计指南 §2.4 参数契约，8 引擎）
ENGINES: List[Tuple[str, str]] = [
    ("deepseek", "DeepSeek"),
    ("doubao", "豆包"),
    ("kimi", "Kimi"),
    ("zhipu", "智谱清言"),
    ("wenxin", "文心一言"),
    ("yuanbao", "元宝"),
    ("tongyi", "通义千问"),
    ("baidu_ai", "百度AI搜索"),
]
ENGINE_CODES = [code for code, _ in ENGINES]

# M3+ 国内模型引用适配的默认重点引擎（报告 §五 验收门 T6 要求的四引擎）
CN_FIT_CORE = ["deepseek", "doubao", "kimi", "zhipu"]

MODES = ["quick", "audit", "optimize", "cn_fit", "infra", "channels", "monitor"]

# 各模式必填项（design guide §2.1 模块触达路径）
REQUIRED_BY_MODE: Dict[str, List[str]] = {
    "quick": ["target"],
    "audit": ["target", "brand"],
    "optimize": ["target", "brand"],
    "cn_fit": ["target", "brand", "product_type"],
    "infra": ["target"],
    "channels": ["brand"],
    "monitor": ["brand"],
}


def normalize_url(raw: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """规范化 URL。返回 (url, domain, error)。"""
    if raw is None:
        return None, None, "url 为空"
    text = str(raw).strip().strip("\"'")
    if not text:
        return None, None, "url 为空字符串"
    if "://" not in text:
        text = "https://" + text.lstrip("/")
    try:
        p = urlparse(text)
    except ValueError as e:
        return None, None, f"URL 解析失败：{e}"
    if p.scheme not in ("http", "https"):
        return None, None, f"不支持的 scheme：{p.scheme}（仅 http/https）"
    host = (p.hostname or "").strip().rstrip(".")
    if not host or "." not in host or " " in host:
        return None, None, f"域名不合法：{host or '(空)'}"
    try:
        host.encode("idna")
    except UnicodeError:
        return None, None, f"域名含非法字符：{host}"
    return text, host, None


def parse_engines(raw: Optional[str]) -> Tuple[List[str], List[Dict[str, str]]]:
    """解析引擎编码列表。空值 → 默认全选 8 引擎。"""
    issues: List[Dict[str, str]] = []
    if raw is None or not str(raw).strip():
        return list(ENGINE_CODES), issues
    picked: List[str] = []
    for token in str(raw).replace(" ", ",").split(","):
        if not token:
            continue
        if token in ENGINE_CODES:
            if token not in picked:
                picked.append(token)
        else:
            issues.append({
                "field": "engines",
                "code": "UNKNOWN_ENGINE",
                "message": f"未知引擎编码：{token}（白名单：{','.join(ENGINE_CODES)}）",
            })
    if not picked and not issues:
        issues.append({"field": "engines", "code": "EMPTY_ENGINES",
                       "message": "engines 解析后为空"})
    return picked, issues


def build_params(args: argparse.Namespace) -> Tuple[Dict[str, Any], List[Dict[str, str]], List[str]]:
    """产出规范化参数、问题清单与缺失必填项。"""
    issues: List[Dict[str, str]] = []
    params: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "mode": None, "target": None, "brand": None,
        "product_type": None, "engines": [], "target_query": None,
    }

    # ---- 模式 ----
    if args.mode not in MODES:
        issues.append({"field": "mode", "code": "UNKNOWN_MODE",
                       "message": f"未知模式：{args.mode}（可选：{','.join(MODES)}）"})
    else:
        params["mode"] = args.mode

    # ---- 目标站点 ----
    raw_target = args.url or args.domain or None
    target: Optional[Dict[str, str]] = None
    if raw_target:
        url, domain, err = normalize_url(raw_target)
        if err:
            issues.append({"field": "url" if args.url else "domain",
                           "code": "INVALID_URL", "message": err})
        else:
            target = {"url": url, "domain": domain}
    params["target"] = target

    # ---- 品牌 / 品类 ----
    brand = (args.brand or "").strip()
    product_type = (args.product_type or "").strip()
    target_query = (args.target_query or "").strip()
    params["brand"] = brand or None
    params["product_type"] = product_type or None
    params["target_query"] = target_query or None

    # ---- 引擎 ----
    engines, engine_issues = parse_engines(args.engines)
    issues.extend(engine_issues)
    params["engines"] = engines

    # ---- 必填项 ----
    missing: List[str] = []
    if params["mode"]:
        for field in REQUIRED_BY_MODE[params["mode"]]:
            if field == "target" and not params["target"]:
                if not any(i["field"] in ("url", "domain") for i in issues):
                    missing.append("target(url/domain)")
            elif field == "brand" and not params["brand"]:
                missing.append("brand")
            elif field == "product_type" and not params["product_type"]:
                missing.append("product_type")

    # ---- cn_fit 模式引擎收窄提示（非错误）----
    if params["mode"] == "cn_fit" and args.engines is None:
        params["engines"] = list(CN_FIT_CORE)

    return params, issues, missing


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="「智引」参数校验：URL/域名、品牌、品类、引擎白名单、模式必填项")
    ap.add_argument("--url", default=None, help="目标页面 URL（可不带 scheme）")
    ap.add_argument("--domain", default=None, help="目标域名（与 --url 二选一）")
    ap.add_argument("--brand", default=None, help="品牌名（MUST 与用户原话一致，禁改写）")
    ap.add_argument("--product-type", default=None, help="品类/产品类型")
    ap.add_argument("--target-query", default=None, help="目标问题（本页应被 AI 引用以回答的提问）")
    ap.add_argument("--engines", default=None,
                    help=f"引擎编码逗号分隔，默认全选 8 引擎：{','.join(ENGINE_CODES)}")
    ap.add_argument("--mode", default="audit", choices=MODES, help="运行模式")
    ap.add_argument("--json", action="store_true", help="输出 JSON（默认输出人类可读）")
    ap.add_argument("--stamp", action="store_true", help="注入时间戳（默认不注入，保证确定性）")
    args = ap.parse_args(argv)

    params, issues, missing = build_params(args)
    hard_error = any(i["code"] in ("UNKNOWN_MODE", "INVALID_URL", "UNKNOWN_ENGINE")
                     for i in issues)

    result: Dict[str, Any] = {
        "tool": TOOL_NAME,
        "schema_version": SCHEMA_VERSION,
        "ok": not issues and not missing,
        "params": params,
        "issues": issues,
        "missing_required": missing,
        "next_action": ("proceed" if not issues and not missing
                        else ("ask_user" if missing and not hard_error else "abort")),
    }
    if args.stamp:
        import time
        result["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        tag = {"proceed": "校验通过", "ask_user": "需补齐必填项", "abort": "非法输入"}[result["next_action"]]
        lines = [f"[智引·参数校验] {tag}  mode={params['mode']}"]
        if params["target"]:
            lines.append(f"  目标：{params['target']['url']}（域名 {params['target']['domain']}）")
        if params["brand"]:
            lines.append(f"  品牌：{params['brand']}")
        if params["engines"]:
            names = [n for c, n in ENGINES if c in params["engines"]]
            lines.append(f"  引擎：{','.join(names)}")
        for m in missing:
            lines.append(f"  ✗ 缺失必填：{m}")
        for i in issues:
            lines.append(f"  ⚠ {i['field']}：{i['message']}")
        print("\n".join(lines))

    if hard_error or (issues and not missing):
        return 2 if hard_error else 2
    if missing:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[智引·参数校验] 脚本异常：{type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(64)
