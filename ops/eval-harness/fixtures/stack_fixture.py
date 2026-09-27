#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-code-analyzer stack_detect 命中分支探针（eval fixture，%TEMP% 隔离）。

场景：
  flutter_hit —— 构造最小 Flutter 仓（pubspec.yaml 含 flutter 依赖 + lib/main.dart）
                ⇒ INDEX.md 主信号必中 ⇒ hit=true 且命中 Flutter / Dart 卡

输出 JSON：{"scenario": ..., "ok": bool, "detail": ...}
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "tri-code-analyzer" / "scripts" / "stack_detect.py"
PY = sys.executable


def scenario_flutter_hit(work: Path):
    (work / "pubspec.yaml").write_text(
        "name: demo_app\n"
        "dependencies:\n"
        "  flutter:\n"
        "    sdk: flutter\n", encoding="utf-8")
    (work / "lib").mkdir()
    (work / "lib" / "main.dart").write_text("void main() {}\n", encoding="utf-8")
    r = subprocess.run([PY, str(SCRIPT), str(work), "--json"], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=120)
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        return False, f"stdout 非合法 JSON rc={r.returncode}"
    ok = (r.returncode == 0 and d.get("hit") is True
          and "Flutter / Dart" in d.get("stacks", [])
          and "flutter.md" in d.get("cards", []))
    return ok, f"rc={r.returncode} hit={d.get('hit')} stacks={d.get('stacks')} cards={d.get('cards')}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", choices=["flutter_hit"], required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="eval-stack-fixture-") as td:
        ok, detail = scenario_flutter_hit(Path(td))
    print(json.dumps({"scenario": a.scenario, "ok": ok, "detail": detail},
                     ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
