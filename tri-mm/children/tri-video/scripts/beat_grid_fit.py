#!/usr/bin/env python3
"""beat_grid_fit.py — BGM 节拍网格拟合与歧义裁决（确定性算法，配合 beat-sync-sound.md §2-3）。

流程：
  1. librosa.beat.beat_track 检测 beat 时刻序列（tempo 标量不可信，只用序列）；
  2. 对 beat 序列做最小二乘等距网格拟合 t_i = t0 + i*T，得真实 BPM 与相位；
  3. 半倍/双倍歧义裁决：对 0.5x / 1x / 2x 三个候选网格计算鼓点覆盖率得分，取最高；
  4. 输出 JSON：bpm / t0 / period / residual_ms / verdict（网格可信判定）。

验收标准（与 beat-sync-sound.md 一致）：
  - 残差 <= ±15ms（半帧内 @30fps）→ 网格可信；残差大 → 曲子有变速段，需分段拟合（本脚本
    以 --segment 秒段长做分段拟合辅助定位变速区间）。

用法：
  python beat_grid_fit.py <audio.mp3> [--json out.json] [--segment 30]

依赖：librosa、numpy（首次运行 `pip install librosa numpy`）；Python >= 3.10。
仅做分析，不改任何音频文件。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def fit_grid(beats):
    """最小二乘等距网格拟合：t_i = t0 + i*T。返回 (T, t0, residual_abs_max_ms)。"""
    import numpy as np

    b = np.asarray(beats, dtype=float)
    if len(b) < 4:
        raise ValueError("beat 点太少（<4），无法拟合网格")
    i = np.arange(len(b))
    A = np.vstack([i, np.ones_like(i)]).T
    (T, t0), *_ = np.linalg.lstsq(A, b, rcond=None)
    residual = b - (t0 + i * T)
    return float(T), float(t0), float(np.abs(residual).max() * 1000.0)


def coverage_score(beats, T, t0, grid_div: float) -> float:
    """鼓点覆盖率：整数拍附近 ±25ms 窗口内命中的 beat 比例（半倍/双倍歧义裁决用）。"""
    import numpy as np

    b = np.asarray(beats, dtype=float)
    phase = (b - t0) / (T * grid_div)
    nearest = np.round(phase)
    err_ms = np.abs(phase - nearest) * T * grid_div * 1000.0
    hits = float(np.mean(err_ms <= 25.0))
    # 惩罚过快网格（整数拍上几乎无点）：命中率*0.7 + 非零整数拍占比*0.3
    on_beat = float(np.mean(nearest % 1 == 0)) if len(b) else 0.0
    return hits * 0.7 + on_beat * 0.3


def analyze(path: str, segment: float | None) -> dict:
    try:
        import librosa
        import numpy as np
    except ImportError:
        print("缺少依赖：请先 `pip install librosa numpy`", file=sys.stderr)
        raise SystemExit(2)

    y, sr = librosa.load(path, sr=None, mono=True)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, tightness=400, units="time")
    beats = np.asarray(beats, dtype=float)
    if len(beats) == 0:
        raise SystemExit("未检测到 beat 点，无法分析")

    T, t0, res_ms = fit_grid(beats)

    # 半倍/双倍歧义裁决：对 0.5x / 1x / 2x 候选网格算覆盖率，最高者胜出（判据是鼓点数据，不是听感）
    candidates = {str(div): coverage_score(beats, T, t0, div) for div in (0.5, 1.0, 2.0)}
    best_div = float(max(candidates, key=lambda k: candidates[k]))
    if best_div != 1.0:
        T = T / best_div  # 周期随网格倍率修正（div=0.5 → 半倍网格，周期减半）

    result = {
        "audio": str(Path(path).resolve()),
        "bpm": round(60.0 / T, 2),
        "period_s": round(T, 5),
        "t0_s": round(t0, 4),
        "residual_max_ms": round(res_ms, 1),
        "grid_divisor": best_div,
        "coverage_scores": {str(k): round(v, 3) for k, v in candidates.items()},
        "beat_count": int(len(beats)),
        "verdict": "PASS" if res_ms <= 15.0 else "FAIL(分段拟合或人工复核)",
        "threshold_residual_ms": 15.0,
    }

    if segment and res_ms > 15.0:
        seg = float(segment)
        duration = len(y) / sr
        segments = []
        start = 0.0
        while start < duration:
            end = min(start + seg, duration)
            seg_beats = beats[(beats >= start) & (beats < end)]
            if len(seg_beats) >= 4:
                sT, s0, sres = fit_grid(seg_beats)
                segments.append({
                    "from_s": round(start, 2), "to_s": round(end, 2),
                    "bpm": round(60.0 / sT, 2), "residual_max_ms": round(sres, 1),
                })
            start = end
        result["segments"] = segments
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="BGM 节拍网格拟合（卡点前置分析）")
    ap.add_argument("audio", help="音频文件路径（mp3/wav）")
    ap.add_argument("--json", dest="json_out", help="结果 JSON 输出路径（缺省打印 stdout）")
    ap.add_argument("--segment", type=float, default=0.0,
                    help="残差超限时按该秒段长做分段拟合（如 30）")
    args = ap.parse_args()

    result = analyze(args.audio, args.segment or None)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
        print(f"已写出 {args.json_out}")
    print(text)
    sys.exit(0 if result["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
