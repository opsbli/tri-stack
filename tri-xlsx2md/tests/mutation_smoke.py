#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""变异冒烟测试（P2-3）——方法论蒸馏自 anydoc tests/robustness.rs（25 轮确定性变异）。

对 tests/samples/ 真实格式样本做确定性字节变异（xorshift64* PRNG，种子=文件内容哈希），
每轮随机选「字节翻转（1–8 处）」或「随机截断（保留 1%–99%）」，然后：

  1. 门A preflight MUST 产出可解析 JSON（「报告必产出」——编排层永不失语）；
  2. 解析引擎（anydoc）可失败（类型化错误 / 非零退出）但 NEVER 挂起（超时即 FAIL）、
     NEVER 信号崩溃（rc<0 即 FAIL）——「可失败，但永不 panic/挂起」。

运行：
    python tests/mutation_smoke.py                # 全量 25 轮 × 全样本
    python tests/mutation_smoke.py --quick        # 3 轮快速冒烟
    python tests/mutation_smoke.py --rounds 10
退出码：0 全过 / 1 存在 FAIL。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG = {
    "arg_name": "--xlsx",                   # preflight 输入参数名（各 skill 输入契约不同）
    "exts": [".xlsx", ".xlsm", ".xls", ".xlsb", ".csv"],  # 参与变异的样本扩展名
    "engine": "anydoc",                     # 解析引擎模块名；None=仅跑门A（无 Rust 引擎的 skill）
}
TIMEOUT_PREFLIGHT = 30
TIMEOUT_ENGINE = 30
_MASK = (1 << 64) - 1


def _xs64(state: int) -> tuple[int, int]:
    """xorshift64* —— 与 anydoc robustness.rs 同族确定性 PRNG。"""
    state ^= state >> 12
    state ^= (state << 25) & _MASK
    state ^= state >> 27
    return state, (state * 2685821657736338717) & _MASK


def _mutate(data: bytearray, rng: int) -> tuple[bytes, int, int]:
    rng, r = _xs64(rng)
    if r % 4 == 3 and len(data) > 100:  # 1/4 概率随机截断
        rng, r = _xs64(rng)
        keep = max(1, int(len(data) * (r % 99 + 1) / 100))
        return bytes(data[:keep]), len(data) - keep, -1
    flips = r % 8 + 1
    for _ in range(flips):
        rng, r = _xs64(rng)
        pos = r % len(data)
        rng, r = _xs64(rng)
        data[pos] ^= (r % 255) + 1
    return bytes(data), flips, 1


def _run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=25)
    ap.add_argument("--quick", action="store_true", help="3 轮快速冒烟")
    args = ap.parse_args()
    rounds = 3 if args.quick else args.rounds

    samples_dir = SKILL_DIR / "tests" / "samples"
    samples = sorted(s for s in samples_dir.glob("*")
                     if s.is_file() and s.suffix.lower() in CONFIG["exts"])
    if not samples:
        print(f"[SKIP] tests/samples/ 无匹配样本（{', '.join(CONFIG['exts'])}）")
        return 0

    stats = {"runs": 0, "engine_ok": 0, "engine_typed_error": 0, "preflight_json": 0}
    failures: list[str] = []
    t0 = time.time()
    with tempfile.TemporaryDirectory() as td:
        for sample in samples:
            data = sample.read_bytes()
            seed = int.from_bytes(hashlib.sha1(sample.stem.encode()).digest()[:8], "big") or 1
            for rnd in range(1, rounds + 1):
                tag = f"{sample.name}#r{rnd}"
                mutant = Path(td) / f"{sample.stem}.m{rnd}{sample.suffix}"
                mutated, a, b = _mutate(bytearray(data), seed * 100003 + rnd)
                mutant.write_bytes(mutated)

                # ① 门A：报告必产出（JSON 必须可解析）
                pr = _run([sys.executable, str(SKILL_DIR / "scripts" / "preflight.py"),
                           CONFIG["arg_name"], str(mutant), "--json"], TIMEOUT_PREFLIGHT)
                stats["runs"] += 1
                if pr is None:
                    failures.append(f"{tag}: preflight 挂起（>{TIMEOUT_PREFLIGHT}s）")
                    continue
                try:
                    json.loads(pr.stdout)
                    stats["preflight_json"] += 1
                except Exception:
                    failures.append(f"{tag}: preflight JSON 不可解析（rc={pr.returncode}）")

                # ② 引擎：可失败但永不挂起/信号崩溃
                if CONFIG["engine"]:
                    er = _run([sys.executable, "-c",
                               f"import sys, {CONFIG['engine']}; "
                               f"{CONFIG['engine']}.to_markdown(sys.argv[1])",
                               str(mutant)], TIMEOUT_ENGINE)
                    if er is None:
                        failures.append(f"{tag}: 引擎挂起（>{TIMEOUT_ENGINE}s）")
                    elif er.returncode < 0:
                        failures.append(f"{tag}: 引擎信号崩溃 rc={er.returncode}")
                    elif er.returncode == 0:
                        stats["engine_ok"] += 1
                    else:
                        stats["engine_typed_error"] += 1  # 类型化失败 = 预期行为
                mutant.unlink(missing_ok=True)

    verdict = "PASS" if not failures else "FAIL"
    print(f"[{verdict}] 变异冒烟：{stats['runs']} 轮运行 / 引擎 ok={stats['engine_ok']} "
          f"类型化失败={stats['engine_typed_error']} / 门A JSON 产出={stats['preflight_json']} "
          f"/ 失败={len(failures)} / 耗时 {time.time() - t0:.1f}s")
    for f in failures[:20]:
        print(f"  - {f}")
    (SKILL_DIR / "tests" / "mutation-smoke-results.json").write_text(
        json.dumps({"verdict": verdict, "rounds": rounds, "stats": stats,
                    "failures": failures}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
