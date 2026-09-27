#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-checklist build_checklist 组装器探针（eval fixture，%TEMP% 隔离）。

场景：
  dry_run_validate —— 构造最小 diff.json + template.json → --dry-run 校验 ⇒ 期望 rc=0
  build_dimensions —— 全量组装 --out ⇒ 期望产出 Markdown 含四维标题（改动点/审查点/测试点/测试步骤）

输出 JSON：{"scenario": ..., "ok": bool, "detail": ...}
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BUILD = Path(__file__).resolve().parents[3] / "tri-checklist" / "scripts" / "build_checklist.py"
PY = sys.executable

DIFF = {
    "mode": "staged",
    "files": [
        {"path": "src/api/user.py", "status": "modified", "insertions": 12, "deletions": 3},
        {"path": "src/api/__init__.py", "status": "added", "insertions": 2, "deletions": 0},
    ],
    "stats": {"files_changed": 2, "insertions": 14, "deletions": 3},
    "sensitive_files": [],
    "test_files": [],
}
TEMPLATE = {
    "dimensions": {
        "changes": {"items": ["改动是否最小化"]},
        "review": {"items": ["是否需要人工审查"]},
        "test": {"items": ["是否有对应测试"]},
        "test_steps": {"items": ["如何复现验证"]},
    }
}

DIM_TITLES = ["改动点", "审查点", "测试点", "测试步骤"]


def run(*argv):
    return subprocess.run([PY, str(BUILD), *argv], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=60)


def scenario_dry_run(work: Path):
    d = work / "diff.json"
    t = work / "template.json"
    d.write_text(json.dumps(DIFF, ensure_ascii=False), encoding="utf-8")
    t.write_text(json.dumps(TEMPLATE, ensure_ascii=False), encoding="utf-8")
    r = run("--diff", str(d), "--template", str(t), "--out", str(work / "x.md"), "--dry-run")
    return r.returncode == 0, f"--dry-run rc={r.returncode} {r.stderr.strip()[:120]}"


def scenario_build_dimensions(work: Path):
    d = work / "diff.json"
    t = work / "template.json"
    out = work / "checklist.md"
    d.write_text(json.dumps(DIFF, ensure_ascii=False), encoding="utf-8")
    t.write_text(json.dumps(TEMPLATE, ensure_ascii=False), encoding="utf-8")
    r = run("--diff", str(d), "--template", str(t), "--out", str(out))
    if r.returncode != 0 or not out.is_file():
        return False, f"rc={r.returncode} 产物存在={out.is_file()} {r.stderr.strip()[:120]}"
    text = out.read_text(encoding="utf-8", errors="replace")
    missing = [t2 for t2 in DIM_TITLES if t2 not in text]
    return not missing, f"四维标题缺失={missing or '无'}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", choices=["dry_run_validate", "build_dimensions"],
                    required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="eval-tri-checklist-") as td:
        ok, detail = (scenario_dry_run if a.scenario == "dry_run_validate"
                      else scenario_build_dimensions)(Path(td))
    print(json.dumps({"scenario": a.scenario, "ok": ok, "detail": detail},
                     ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
