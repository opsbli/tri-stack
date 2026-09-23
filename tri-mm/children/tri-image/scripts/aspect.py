#!/usr/bin/env python3
"""把宽高比换算成像素尺寸。

为什么需要它：原生生图后端（Tier-1）只接受像素尺寸，不接受 "16:9" 这样的宽高比
参数。换算必须由脚本完成，NEVER 由模型心算——边长还要满足部分模型"必须是 16 的倍数"
的约束，那是确定性问题，不下沉就会出错。

用法：
    python aspect.py 16:9
    python aspect.py 16:9 --quality 2k --json
    python aspect.py 2.35:1 --multiple 16 --json
退出码：0 成功；2 输入不合法。
"""
import argparse
import json
import sys

# 质量档 -> 目标长边像素
PRESETS = {
    "1k": 1024,
    "normal": 1024,
    "2k": 2048,
    "4k": 3840,
}

# 近似比 -> 规范比（把 3:2、21:9 等折算到最接近的受support比）
ALIASES = {
    (3, 2): (16, 9),
    (2, 3): (9, 16),
    (21, 9): (235, 100),
    (32, 9): (32, 9),
}

MAX_EDGE = 3840


def parse_ratio(text):
    if ":" not in text:
        raise ValueError("比例必须形如 W:H，例如 16:9")
    left, _, right = text.partition(":")
    try:
        w = float(left)
        h = float(right)
    except ValueError:
        raise ValueError("比例的宽高必须是数字")
    if w <= 0 or h <= 0:
        raise ValueError("宽高必须为正数")
    return w, h


def normalize(w, h):
    """把任意浮点比折算到最接近的受support比，返回 (pw, ph, 是否被折算)。"""
    target = w / h
    best = None
    for cw, ch in [(1, 1), (16, 9), (9, 16), (4, 3), (3, 4), (235, 100), (32, 9)]:
        diff = abs((cw / ch) - target)
        if best is None or diff < best[2]:
            best = (cw, ch, diff)
    pw, ph, diff = best
    aliased = diff > 0.01
    return pw, ph, aliased


def compute(ratio, quality="2k", multiple=16):
    w, h = parse_ratio(ratio)
    pw, ph, aliased = normalize(w, h)
    long_edge = PRESETS.get(quality.lower())
    if long_edge is None:
        raise ValueError("未知质量档：%s（可选 %s）" % (quality, "/".join(sorted(set(PRESETS)))))

    if pw >= ph:
        width_px, height_px = long_edge, max(1, round(long_edge * ph / pw))
    else:
        height_px, width_px = long_edge, max(1, round(long_edge * pw / ph))

    if multiple > 1:
        width_px = round(width_px / multiple) * multiple
        height_px = round(height_px / multiple) * multiple
        width_px = max(multiple, width_px)
        height_px = max(multiple, height_px)

    scaled = False
    if max(width_px, height_px) > MAX_EDGE:
        factor = MAX_EDGE / max(width_px, height_px)
        width_px = int(width_px * factor)
        height_px = int(height_px * factor)
        scaled = True
        if multiple > 1:
            width_px = round(width_px / multiple) * multiple
            height_px = round(height_px / multiple) * multiple

    return {
        "ratio": ratio,
        "canonical_ratio": "%d:%d" % (pw, ph),
        "aliased": aliased,
        "quality": quality,
        "width": width_px,
        "height": height_px,
        "size": "%dx%d" % (width_px, height_px),
        "multiple": multiple,
        "clamped_to_max_edge": scaled,
    }


def main():
    ap = argparse.ArgumentParser(description="宽高比 -> 像素尺寸换算")
    ap.add_argument("ratio", help="形如 16:9 / 1:1 / 2.35:1")
    ap.add_argument("--quality", default="2k", help="1k/normal/2k/4k，默认 2k")
    ap.add_argument("--multiple", type=int, default=16, help="边长对齐倍数，默认 16（0/1 表示不对齐）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    try:
        result = compute(args.ratio, args.quality, args.multiple)
    except ValueError as exc:
        sys.stderr.write("Error: %s\n" % exc)
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("%s -> %s (%dx%d)%s" % (
            args.ratio, result["size"], result["width"], result["height"],
            "  [已折算到 %s]" % result["canonical_ratio"] if result["aliased"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
