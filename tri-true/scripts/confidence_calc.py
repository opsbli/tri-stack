#!/usr/bin/env python3
"""tri-true 置信度计算与 ECE 校准（确定性逻辑脚本）.

实现防线一的三层置信度综合公式与 ECE/Brier 校准估计器。
SKILL.md 仅保留公式摘要与本脚本指针，正则/算法全集在此。

用法:
    python scripts/confidence_calc.py --vc 0.8 --sc 0.7 --cc 0.75
    python scripts/confidence_calc.py --vc 0.8 --sc 0.7 --cc 0.75 --ece 0.12

公式: Confidence = 0.4*VC + 0.3*SC + 0.3*CC
"""
from __future__ import annotations
import argparse
import json
import sys


def compute_confidence(vc: float, sc: float, cc: float) -> float:
    """三层置信度加权综合。VC/SC/CC 均 0-1。"""
    for name, v in (("VC", vc), ("SC", sc), ("CC", cc)):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"{name} 必须在 [0,1] 区间，收到 {v}")
    return round(0.4 * vc + 0.3 * sc + 0.3 * cc, 4)


def expected_calibration_error(
    bins_conf: list[float], bins_acc: list[float], bins_n: list[int]
) -> float:
    """ECE：分桶置信度与实际准确率的加权绝对差。

    bins_conf / bins_acc / bins_n 等长，每桶一个值。
    """
    total = sum(bins_n)
    if total == 0:
        raise ValueError("样本总数为 0")
    ece = 0.0
    for conf, acc, n in zip(bins_conf, bins_acc, bins_n):
        ece += (n / total) * abs(conf - acc)
    return round(ece, 4)


def brier_score(preds: list[float], actuals: list[int]) -> float:
    """Brier 分数：预测概率与 0/1 实际的均方误差。"""
    if len(preds) != len(actuals):
        raise ValueError("preds 与 actuals 长度不一致")
    if not preds:
        raise ValueError("空输入")
    return round(sum((p - a) ** 2 for p, a in zip(preds, actuals)) / len(preds), 4)


def calibrate_k(ece: float) -> float:
    """由 ECE 反推校准系数 k（过度自信修正）。ECE 越大 k 越小。"""
    if not 0.0 <= ece <= 1.0:
        raise ValueError(f"ECE 必须在 [0,1]，收到 {ece}")
    return round(max(0.0, 1.0 - ece), 4)


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-true 三层置信度计算 + ECE/Brier 校准")
    ap.add_argument("--vc", type=float, required=True, help="Verbalized Confidence 0-1")
    ap.add_argument("--sc", type=float, required=True, help="Self-Consistency 0-1")
    ap.add_argument("--cc", type=float, required=True, help="Calibrated Confidence 0-1")
    ap.add_argument("--ece", type=float, help="历史 ECE（可选，用于反推校准系数 k）")
    args = ap.parse_args()

    result = {"confidence": compute_confidence(args.vc, args.sc, args.cc)}
    if args.ece is not None:
        result["ece"] = args.ece
        result["k"] = calibrate_k(args.ece)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
