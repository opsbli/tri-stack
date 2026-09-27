#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-action hash_confirm 行为探针（eval fixture，%TEMP% 隔离，不触仓库文件）。

场景：
  write_verify —— 空白确认日志 --write 写哈希行 → --verify 与记录行比对 ⇒ 期望 rc=0
  tamper       —— 写入后篡改文件内容 → --verify ⇒ 期望 rc!=0（防篡改必须检出）

输出 JSON：{"scenario": ..., "ok": bool, "detail": ...}
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HASH_CONFIRM = Path(__file__).resolve().parents[3] / "tri-action" / "scripts" / "hash_confirm.py"
PY = sys.executable

SAMPLE = """# 确认日志

- 2026-09-27 用户确认删除 output/report_final.pdf
"""


def run(*argv):
    return subprocess.run([PY, str(HASH_CONFIRM), *argv], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=60)


def scenario_write_verify(work: Path):
    log = work / "confirm-log.md"
    log.write_text(SAMPLE, encoding="utf-8")
    r1 = run(str(log), "--write")
    if r1.returncode != 0:
        return False, f"--write rc={r1.returncode} {r1.stderr.strip()[:120]}"
    r2 = run(str(log), "--verify")
    return r2.returncode == 0, f"--verify rc={r2.returncode}（期望 0）"


def scenario_tamper(work: Path):
    log = work / "confirm-log.md"
    log.write_text(SAMPLE, encoding="utf-8")
    r1 = run(str(log), "--write")
    if r1.returncode != 0:
        return False, f"--write rc={r1.returncode}"
    log.write_text(SAMPLE + "- 2026-09-27 用户确认删除 secrets.key\n", encoding="utf-8")
    r2 = run(str(log), "--verify")
    return r2.returncode != 0, f"--verify rc={r2.returncode}（期望非 0：篡改必须检出）"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", choices=["write_verify", "tamper"], required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="eval-tri-action-") as td:
        ok, detail = (scenario_write_verify if a.scenario == "write_verify"
                      else scenario_tamper)(Path(td))
    print(json.dumps({"scenario": a.scenario, "ok": ok, "detail": detail},
                     ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
