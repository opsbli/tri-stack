#!/usr/bin/env python3
"""把 SVG 转成 @Nx PNG（结构图轨的 PNG 导出）。

设计要点：自己做 rendering 不现实，改为「按顺序探测本机已有的渲染器并调用」。
用 shutil.which 而非 `which` 命令 —— 后者在 Windows 上不存在，原实现因此完全不可用。

用法：
    python svg_to_png.py input.svg
    python svg_to_png.py input.svg -s 3 -o out.png
    python svg_to_png.py input.svg --json
退出码：0 成功；2 输入/参数问题；3 本机无任何可用渲染器（属环境降级，非脚本缺陷）。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

RENDERERS = [
    ("resvg", ["resvg", "-z", "{scale}", "{src}", "{out}"]),
    ("rsvg-convert", ["rsvg-convert", "-z", "{scale}", "-o", "{out}", "{src}"]),
    ("inkscape", ["inkscape", "--export-type=png", "--export-dpi={dpi}", "-o", "{out}", "{src}"]),
    ("magick", ["magick", "-density", "{dpi}", "-background", "none", "{src}", "{out}"]),
    ("convert", ["convert", "-density", "{dpi}", "-background", "none", "{src}", "{out}"]),
    ("cairosvg", [sys.executable, "-c", "import sys,cairosvg;"
                  " cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2],"
                  " scale=float(sys.argv[3]))", "{src}", "{out}", "{scale}"]),
]

# ImageMagick 家族必须做身份校验：Windows 的 C:\Windows\system32\convert.exe
# 是磁盘格式转换工具，与 ImageMagick 同名。未经校验直接调用后果不可逆。
IMAGE_MAGICK_NAMES = ("magick", "convert")


def is_real_imagemagick(name):
    """返回 True 才允许调用；同名但非 ImageMagick 返回 False。"""
    path = shutil.which(name)
    if not path:
        return False
    # 先按绝对路径排除 Windows 系统目录
    system_roots = (os.environ.get("SystemRoot", r"C:\Windows"), os.environ.get("SystemDrive", "C:") + r"\Windows")
    abspath = os.path.abspath(path).lower()
    for root in system_roots:
        if root and abspath.startswith(os.path.abspath(root).lower() + os.sep):
            return False
    try:
        proc = subprocess.run([path, "-version"], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=10)
    except Exception:
        return False
    text = (proc.stdout + proc.stderr).decode("utf-8", "replace").lower()
    return "imagemagick" in text


def parse_dimensions(svg_text):
    """从 viewBox 或 width/height 取 SVG 逻辑尺寸。"""
    vb = re.search(r'viewBox\s*=\s*"([^"]+)"', svg_text)
    if vb:
        parts = [p for p in re.split(r"[\s,]+", vb.group(1).strip()) if p]
        if len(parts) >= 4:
            try:
                w, h = float(parts[2]), float(parts[3])
                if w > 0 and h > 0:
                    return w, h
            except ValueError:
                pass
    w = re.search(r'\bwidth\s*=\s*"(\d+(?:\.\d+)?)"', svg_text)
    h = re.search(r'\bheight\s*=\s*"(\d+(?:\.\d+)?)"', svg_text)
    if w and h:
        return float(w.group(1)), float(h.group(1))
    return None, None


def find_renderer():
    for name, _ in RENDERERS:
        if name == "cairosvg":
            probe = subprocess.run(
                [sys.executable, "-c", "import cairosvg"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if probe.returncode == 0:
                return name
            continue
        if not shutil.which(name):
            continue
        if name in IMAGE_MAGICK_NAMES and not is_real_imagemagick(name):
            continue
        return name
    return None


def build_command(name, template, src, out, scale):
    dpi = str(int(72 * scale))
    argv = []
    for token in template:
        if token == "{dpi}":
            argv.append(dpi)
        elif token == "{scale}":
            argv.append(str(scale))
        elif token == "{src}":
            argv.append(src)
        elif token == "{out}":
            argv.append(out)
        else:
            argv.append(token)
    return argv


def main():
    ap = argparse.ArgumentParser(description="SVG -> @Nx PNG")
    ap.add_argument("input", help="输入 .svg 路径")
    ap.add_argument("-s", "--scale", type=float, default=2.0, help="缩放倍数，默认 2")
    ap.add_argument("-o", "--output", help="输出路径，默认 <输入名>@Nx.png")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    src = os.path.abspath(args.input)
    if not os.path.isfile(src):
        sys.stderr.write("Error: %s 不存在\n" % args.input)
        return 2
    if not src.lower().endswith(".svg"):
        sys.stderr.write("Error: 输入必须是 .svg 文件\n")
        return 2
    if args.scale <= 0:
        sys.stderr.write("Error: --scale 必须为正数\n")
        return 2

    if args.output:
        out = os.path.abspath(args.output)
    else:
        base = os.path.splitext(src)[0]
        suffix = "" if args.scale == 1 else "@%gx" % args.scale
        out = base + suffix + ".png"

    with open(src, "r", encoding="utf-8") as fh:
        svg_text = fh.read()
    lw, lh = parse_dimensions(svg_text)
    if lw is None:
        sys.stderr.write("Error: 无法从 viewBox/width/height 推断尺寸\n")
        return 2

    name = find_renderer()
    if name is None:
        sys.stderr.write(
            "Error: 本机未找到任何 SVG 渲染器。"
            "可用其一：resvg / rsvg-convert / inkscape / ImageMagick(magick|convert) / python cairosvg\n"
            "降级建议：直接交付 SVG 本体（Track-V 的主要产物），PNG 导出为可选增强。\n")
        return 3

    template = dict(RENDERERS)[name]
    argv = build_command(name, template, src, out, args.scale)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        sys.stderr.write("Error: %s 渲染失败：%s\n" % (name, proc.stderr.decode("utf-8", "replace").strip()))
        return 3

    payload = {
        "renderer": name,
        "input": src,
        "output": out,
        "scale": args.scale,
        "logical_size": "%gx%g" % (lw, lh),
        "pixel_size": "%dx%d" % (round(lw * args.scale), round(lh * args.scale)),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print("%s -> %s (%s, 渲染器=%s)" % (src, out, payload["pixel_size"], name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
