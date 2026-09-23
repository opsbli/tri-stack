#!/usr/bin/env python3
"""门B · 后端探测与档位决策（tri-docx2md）

探测七后端本地可用性（Python import 与 CLI 双探测，anydoc 为 dual 型双通道首选），
按「等级建议 × 本地可用性」选定后端与降级链；.doc 旧格式在 anydoc 可用时直读
（自研 MS-DOC 解析器），anydoc 缺失时降级 LibreOffice 转 docx 中间格式（antiword
纯文本兜底）；全缺失时输出安装指引并停在预检报告态。

用法：
    python scripts/detect_backends.py --grade <L0|L1> [--doc-format] --json
    python scripts/detect_backends.py --grade L0 --pretty
"""
from _io_safe import safe_print
import argparse
import importlib.util
import json
import shutil
import sys

# 后端注册表：kind=python 用 importlib 探测；kind=cli 用 shutil.which 探测；
# kind=dual 先 import 再 CLI（anydoc：Python 绑定优先，npx CLI 兜底）
BACKENDS = {
    "anydoc": {"kind": "dual", "module": "anydoc", "cli": ["anydoc", "npx"], "grade": "L0", "license": "MIT",
               "install": "pip install firecrawl-anydoc 或 npm i -g @firecrawl/anydoc（见 references/backends.md §anydoc）"},
    "mammoth": {"kind": "python", "module": "mammoth", "grade": "L0", "license": "BSD-2-Clause",
                "install": "pip install mammoth"},
    "markitdown": {"kind": "python", "module": "markitdown", "grade": "L0", "license": "MIT",
                   "install": "pip install markitdown[all]"},
    "python-docx": {"kind": "python", "module": "docx", "grade": "L0", "license": "MIT",
                    "install": "pip install python-docx"},
    "pandoc": {"kind": "cli", "cli": ["pandoc"], "grade": "L1", "license": "GPL-2.0",
               "install": "见 references/backends.md §安装"},
    "libreoffice": {"kind": "cli", "cli": ["soffice", "libreoffice"], "grade": "DOC", "license": "MPL-2.0",
                    "install": "见 references/backends.md §安装"},
    "antiword": {"kind": "cli", "cli": ["antiword"], "grade": "DOC", "license": "GPL-2.0",
                 "install": "见 references/backends.md §安装"},
}

# 档位优先序（首选在前；anydoc 为全链一等首选，缺失时探测 JSON 自动下移，NEVER Agent 另选）
GRADE_ORDER = {
    "L0": ["anydoc", "mammoth", "markitdown", "python-docx"],
    "L1": ["anydoc", "pandoc", "mammoth", "markitdown", "python-docx"],
    "DOC": ["anydoc", "libreoffice", "antiword"],
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


def decide(grade: str, probes: dict, doc_format: bool) -> dict:
    """等级 × 可用性 → 选定后端 + 降级链（含不可用项的安装指引）。"""
    order = GRADE_ORDER.get(grade, GRADE_ORDER["L0"])
    available_chain = [b for b in order if probes[b]["available"]]
    missing = [b for b in order if not probes[b]["available"]]
    plan = {
        "grade": grade,
        "doc_format": doc_format,
        "selected": available_chain[0] if available_chain else None,
        "fallback_chain": available_chain[1:],
        "missing_with_install": [{"backend": b, "install": probes[b]["install"]} for b in missing],
        "halted": not available_chain,
    }
    if plan["halted"]:
        plan["halt_reason"] = (
            f"{grade} 档及全部降级后端均不可用——输出安装指引并停在预检报告态，NEVER 空手交付"
        )

    # .doc 旧格式：anydoc 可用 → 直读（自研 MS-DOC 解析器，冲突 4 裁定）；
    # 否则 LibreOffice 转 docx 中间格式 → antiword 纯文本兜底
    doc_convert = {"needed": doc_format, "mode": None, "selected": None, "fallback": None, "halted": False}
    if doc_format:
        if probes["anydoc"]["available"]:
            doc_convert["mode"] = "direct"
            doc_convert["selected"] = "anydoc"
            doc_convert["fallback"] = "libreoffice"
        else:
            doc_convert["mode"] = "convert"
            doc_order = GRADE_ORDER["DOC"][1:]  # 跳过 anydoc
            doc_avail = [b for b in doc_order if probes[b]["available"]]
            doc_convert["selected"] = doc_avail[0] if doc_avail else None
            doc_convert["fallback"] = doc_avail[1] if len(doc_avail) > 1 else None
            doc_convert["halted"] = not doc_avail
            if doc_convert["halted"]:
                doc_convert["halt_reason"] = (
                    "anydoc 缺失且无 LibreOffice/antiword——.doc 旧格式无法转换，输出安装指引并停在预检报告态"
                )
    plan["doc_convert"] = doc_convert
    return plan


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-docx2md 门B 后端探测与档位决策")
    ap.add_argument("--grade", default="L0", choices=["L0", "L1"], help="门A 给出的等级建议")
    ap.add_argument("--doc-format", action="store_true", help=".doc 旧格式（启用 LibreOffice/antiword 中间转换路径）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--pretty", action="store_true", help="输出人类可读摘要")
    args = ap.parse_args()

    probes = {name: probe_backend(name) for name in BACKENDS}
    plan = decide(args.grade, probes, args.doc_format)
    payload = {"backends": probes, "plan": plan}

    if args.json or not args.pretty:
        safe_print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        safe_print(f"档位：{plan['grade']} ｜ .doc 旧格式：{plan['doc_format']}")
        for name, p in probes.items():
            mark = "OK " if p["available"] else "-- "
            safe_print(f"  {mark}{name:<14}（{p['grade']} ｜ {p['license']}）via {p['via']}")
        safe_print(f"选定后端：{plan['selected']}")
        safe_print(f"降级链：{' → '.join(plan['fallback_chain']) or '（无）'}")
        if plan["doc_format"]:
            dc = plan["doc_convert"]
            mode_desc = "anydoc 直读" if dc["mode"] == "direct" else "中转转换"
            safe_print(f".doc 旧格式（{mode_desc}）：{dc['selected']}（兜底 {dc['fallback'] or '无'}）")
            if dc["halted"]:
                safe_print(f"  .doc 停机原因：{dc['halt_reason']}")
        if plan["halted"]:
            safe_print(f"停机原因：{plan['halt_reason']}")
            for m in plan["missing_with_install"]:
                safe_print(f"  安装指引：{m['backend']} → {m['install']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
