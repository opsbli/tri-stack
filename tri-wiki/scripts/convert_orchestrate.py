#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-wiki 门C：批量转换委派编排——计划生成（--plan）与产物汇总（--collect）。

仅用 Python 标准库。委派三态（installed/missing+同意/missing+拒绝）与执行层由
Agent 按本脚本输出的 convert-plan.json 推进；本脚本负责确定性检测与汇总。

用法：
    python convert_orchestrate.py --plan --manifest <sources-manifest.json> [--out <过程目录>] --json
    python convert_orchestrate.py --collect --converted-dir <目录> [--manifest <manifest>] [--out <过程目录>] --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

X2MD_SKILLS = ["tri-pdf2md", "tri-docx2md", "tri-pptx2md", "tri-xlsx2md", "tri-html2md"]

CANDIDATE_ROOTS = [
    Path(".tribro") / "skills",
    Path("skills"),
    Path.home() / ".workbuddy" / "skills",
    Path.home() / ".trae-cn" / "skills",
]

SCRIPT_HINT = {
    "tri-pdf2md": "preflight.py → detect_backends.py → 后端转换 → quality_check.py（详见其 SKILL.md 五阶段管道）",
    "tri-docx2md": "预检 → mammoth/markitdown 链转换 → postprocess.py（详见其 SKILL.md）",
    "tri-pptx2md": "预检 → python-pptx/markitdown 链转换（详见其 SKILL.md）",
    "tri-xlsx2md": "预检 → pandas→openpyxl 降级链转换（详见其 SKILL.md）",
    "tri-html2md": "html2text/BeautifulSoup 链转换（详见其 SKILL.md）",
}


def find_skill(skill: str) -> str | None:
    for root in CANDIDATE_ROOTS:
        d = root / skill
        if (d / "SKILL.md").is_file():
            return str(d.resolve())
    return None


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {}


def cmd_plan(args, out_dir: Path):
    manifest = load_json(Path(args.manifest))
    installed = {s: find_skill(s) for s in X2MD_SKILLS}
    plan, missing_skills = [], set()
    for f in manifest.get("files", []):
        if f["category"] != "convert":
            continue
        skill = f.get("suggested_skill")
        entry = {"path": f["path"], "format": f["format"], "skill": skill,
                 "skill_dir": installed.get(skill), "hint": SCRIPT_HINT.get(skill, ""),
                 "status": "planned" if installed.get(skill) else "blocked_missing_skill"}
        if not installed.get(skill):
            missing_skills.add(skill)
        plan.append(entry)

    direct_cnt = sum(1 for f in manifest.get("files", []) if f["category"] == "direct")
    blocked = bool(plan) and all(e["status"] == "blocked_missing_skill" for e in plan) and direct_cnt == 0
    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "plan", "installed": installed,
        "missing_skills": sorted(missing_skills),
        "install_hint": [f"skillhub install {s} --dir <目标目录>" for s in sorted(missing_skills)],
        "hard_block": blocked,
        "block_reason": "全部转换器缺失且无直通格式" if blocked else None,
        "plan": plan,
    }
    out = out_dir / "convert-plan.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


FIDELITY_RE = re.compile(r"保真率[^\d]*([0-9.]+)\s*%?")


def cmd_collect(args, out_dir: Path, manifest_path: Path | None):
    cdir = Path(args.converted_dir)
    mds = sorted(cdir.rglob("*.md")) if cdir.is_dir() else []
    manifest = load_json(manifest_path) if manifest_path else {}
    by_name = {}
    for f in manifest.get("files", []):
        by_name[Path(f["path"]).stem] = f

    converted, fid_scores = [], []
    for m in mds:
        stem = m.stem
        for suffix in ("_md", "-md"):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
        src = by_name.get(stem, {})
        fid = None
        rep = m.with_name("report.md")
        if rep.is_file():
            mm = FIDELITY_RE.search(rep.read_text(encoding="utf-8", errors="ignore")[:8000])
            if mm:
                v = float(mm.group(1))
                fid = v / 100 if v > 1 else v
                fid_scores.append(fid)
        converted.append({"md": str(m), "src": src.get("path"), "format": src.get("format"),
                          "fidelity": fid})

    total_convert = sum(1 for f in manifest.get("files", []) if f["category"] == "convert")
    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "collect", "converted_dir": str(cdir),
        "md_count": len(mds), "expected_convert": total_convert,
        "avg_fidelity": round(sum(fid_scores) / len(fid_scores), 4) if fid_scores else None,
        "converted": converted,
    }
    out = out_dir / "convert-summary.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--converted-dir", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not (args.plan or args.collect):
        ap.error("须指定 --plan 或 --collect")

    out_dir = Path(args.out) if args.out else Path(".tribro") / "wiki"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.plan:
        if not args.manifest:
            ap.error("--plan 需要 --manifest")
        result = cmd_plan(args, out_dir)
    else:
        if not args.converted_dir:
            ap.error("--collect 需要 --converted-dir")
        mp = Path(args.manifest) if args.manifest else None
        result = cmd_collect(args, out_dir, mp)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["mode"] == "plan":
            print(f"委派计划：{len(result['plan'])} 个转换任务；缺失 skill：{result['missing_skills'] or '无'}")
        else:
            print(f"汇总完成：{result['md_count']} 个 MD 产物；平均保真率：{result['avg_fidelity']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
