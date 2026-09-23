#!/usr/bin/env python3
"""门B · 后端探测与档位决策（tri-xlsx2md）

探测五后端本地可用性（Python import 与 CLI 双探测），按「等级建议 × 文件类型 × 本地可用性」
选定后端与降级链；全缺失时输出安装指引并停在预检报告态。

用法：
    python scripts/detect_backends.py --grade <L0|L1> [--type <xlsx|xls>] --json
    python scripts/detect_backends.py --grade L0 --type xlsx --pretty
"""
from _io_safe import safe_print
import argparse
import importlib.util
import json
import shutil
import sys

# 后端注册表：kind=python 用 importlib 探测；kind=cli 用 shutil.which 探测
BACKENDS = {
    "anydoc": {"kind": "dual", "module": "anydoc", "cli": ["anydoc", "npx"], "grade": "L0", "license": "MIT",
               "install": "pip install firecrawl-anydoc 或 npm i -g @firecrawl/anydoc（见 references/backends.md §anydoc）"},
    "openpyxl": {"kind": "python", "module": "openpyxl", "grade": "L0", "license": "MIT",
                 "install": "pip install openpyxl"},
    "markitdown": {"kind": "python", "module": "markitdown", "grade": "L0", "license": "MIT",
                   "install": "pip install markitdown[all]"},
    "xlrd": {"kind": "python", "module": "xlrd", "grade": "L0", "license": "BSD-3",
             "install": "pip install xlrd"},
    "pandas": {"kind": "python", "module": "pandas", "grade": "L1", "license": "BSD-3",
               "install": "pip install pandas"},
    "libreoffice": {"kind": "cli", "module": None, "cli": ["soffice", "libreoffice"], "grade": "L1",
                    "license": "MPL-2.0", "install": "系统包：apt install libreoffice / winget install TheDocumentFoundation.LibreOffice"},
}

# 档位优先序（首选在前）；降级链按 L1→L0 逐级展开
# anydoc 全族直读首选（.xlsx/.xlsm/.xls/.xlsb/.csv）；缺失时探测 JSON 自动下移，NEVER Agent 另选
GRADE_ORDER = {
    "L1": ["anydoc", "pandas", "libreoffice", "openpyxl", "markitdown", "xlrd"],
    "L0": ["anydoc", "openpyxl", "markitdown", "xlrd"],
}


def probe_backend(name: str) -> dict:
    spec = BACKENDS[name]
    info = {"available": False, "kind": spec["kind"], "grade": spec["grade"],
            "license": spec["license"], "install": spec["install"], "via": None}
    if spec["kind"] in ("python", "dual"):
        if importlib.util.find_spec(spec["module"]) is not None:
            info["available"] = True
            info["via"] = f"import {spec['module']}"
    if not info["available"] and spec["kind"] in ("cli", "dual"):
        for cli in spec["cli"]:
            path = shutil.which(cli)
            if path:
                info["available"] = True
                info["via"] = f"cli:{path}"
                break
    return info


def decide(grade: str, file_type: str, probes: dict) -> dict:
    """等级 × 文件类型 × 可用性 → 选定后端 + 降级链（含不可用项的安装指引）。"""
    order = list(GRADE_ORDER.get(grade, GRADE_ORDER["L0"]))
    if file_type == "xls":
        # .xls 旧格式：xlrd 为 L0 首选（openpyxl 不支持 .xls）
        order = ["xlrd"] + [b for b in order if b != "xlrd"]
    available_chain = [b for b in order if probes[b]["available"]]
    missing = [b for b in order if not probes[b]["available"]]
    plan = {
        "grade": grade,
        "file_type": file_type,
        "selected": available_chain[0] if available_chain else None,
        "fallback_chain": available_chain[1:],
        "missing_with_install": [{"backend": b, "install": probes[b]["install"]} for b in missing],
        "halted": not available_chain,
    }
    if plan["halted"]:
        plan["halt_reason"] = (
            f"{grade} 档及全部降级后端均不可用——输出安装指引并停在预检报告态，NEVER 空手交付"
        )
    return plan


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-xlsx2md 门B 后端探测与档位决策")
    ap.add_argument("--grade", default="L0", choices=["L0", "L1"], help="门A 给出的等级建议")
    ap.add_argument("--type", default="xlsx", choices=["xlsx", "xls"], help="文件类型（门A 判定）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--pretty", action="store_true", help="输出人类可读摘要")
    args = ap.parse_args()

    probes = {name: probe_backend(name) for name in BACKENDS}
    plan = decide(args.grade, args.type, probes)
    payload = {"backends": probes, "plan": plan}

    if args.json or not args.pretty:
        safe_print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        safe_print(f"档位：{plan['grade']} ｜ 类型：{plan['file_type']}")
        for name, p in probes.items():
            mark = "OK " if p["available"] else "-- "
            safe_print(f"  {mark}{name:<14}（{p['grade']} ｜ {p['license']}）via {p['via']}")
        safe_print(f"选定后端：{plan['selected']}")
        safe_print(f"降级链：{' → '.join(plan['fallback_chain']) or '（无）'}")
        if plan["halted"]:
            safe_print(f"停机原因：{plan['halt_reason']}")
            for m in plan["missing_with_install"]:
                safe_print(f"  安装指引：{m['backend']} → {m['install']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
