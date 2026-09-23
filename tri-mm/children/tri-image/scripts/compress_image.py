#!/usr/bin/env python3
"""图片压缩 / 格式转换（后处理）。

原实现用 `spawn("which", ...)` 探测命令 —— POSIX 专用，Windows 上直接失效，
因此改为 shutil.which（跨平台）+ 可选 Pillow 兜底。这是本次修复的核心缺陷之一。

用法：
    python compress_image.py input.png
    python compress_image.py dir/ -r
    python compress_image.py a.png -f webp -q 80 -k
    python compress_image.py a.png -o out.webp --json
退出码：0 成功；2 输入/参数问题；3 本机无可用压缩后端。
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

SUPPORTED_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".tiff")

# (名称, 模板)。{q} 质量，{src} 输入，{out} 输出
FORMATS = ("webp", "png", "jpeg")

BACKENDS = {
    "webp": [
        ("cwebp", ["cwebp", "-q", "{q}", "{src}", "-o", "{out}"]),
        ("magick", ["magick", "{src}", "-quality", "{q}", "{out}"]),
        ("convert", ["convert", "{src}", "-quality", "{q}", "{out}"]),
    ],
    "png": [
        ("magick", ["magick", "{src}", "-quality", "{q}", "{out}"]),
        ("convert", ["convert", "{src}", "-quality", "{q}", "{out}"]),
    ],
    "jpeg": [
        ("magick", ["magick", "{src}", "-quality", "{q}", "{out}"]),
        ("convert", ["convert", "{src}", "-quality", "{q}", "{out}"]),
    ],
}


def is_real_imagemagick(name):
    """Windows 的 C:\\Windows\\system32\\convert.exe 是磁盘格式转换工具，
    与 ImageMagick 的 convert 同名。直接用它会造成不可逆后果，故必须做身份校验。"""
    path = shutil.which(name)
    if not path:
        return False
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    if system_root and os.path.abspath(path).lower().startswith(
            os.path.abspath(system_root).lower() + os.sep):
        return False
    try:
        proc = subprocess.run([path, "-version"], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=10)
    except Exception:
        return False
    text = (proc.stdout + proc.stderr).decode("utf-8", "replace").lower()
    return "imagemagick" in text


def detect_backend(fmt):
    for name, _ in BACKENDS.get(fmt, []):
        if not shutil.which(name):
            continue
        if name in ("magick", "convert") and not is_real_imagemagick(name):
            continue
        return name
    return None


def compress_with_pillow(src, out, fmt, quality):
    """零外部依赖降级路径：仅在系统无命令行工具时使用。"""
    try:
        from PIL import Image
    except ImportError:
        return False
    img = Image.open(src)
    save_kwargs = {"quality": quality}
    if fmt == "webp":
        img.save(out, "WEBP", **save_kwargs)
    elif fmt == "png":
        img.convert("RGBA" if img.mode in ("RGBA", "LA") else "RGB").save(out, "PNG")
    else:
        img.convert("RGB").save(out, "JPEG", quality=quality)
    return True


def run_backend(name, template, src, out, quality):
    argv = []
    for token in template:
        if token == "{q}":
            argv.append(str(quality))
        elif token == "{src}":
            argv.append(src)
        elif token == "{out}":
            argv.append(out)
        else:
            argv.append(token)
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode == 0, proc.stderr.decode("utf-8", "replace").strip()


def output_path(src, fmt, keep, custom):
    if custom:
        return os.path.abspath(custom)
    ext = ".jpg" if fmt == "jpeg" else "." + fmt
    base, old = os.path.splitext(src)
    if old.lower() == ext or keep:
        # 同扩展名或显式要求保留原文件 -> 另存为带后缀的新文件，NEVER 覆盖源
        return base + "-compressed" + ext
    return base + ext


def dedupe(out, used):
    """同一批内输出路径冲突时自动加序号，NEVER 让两个输入写到同一个输出。"""
    if out not in used:
        used.add(out)
        return out
    base, ext = os.path.splitext(out)
    i = 2
    while True:
        candidate = "%s-%d%s" % (base, i, ext)
        if candidate not in used:
            used.add(candidate)
            return candidate
        i += 1


def collect(dirpath, recursive):
    found = []
    for entry in sorted(os.listdir(dirpath)):
        full = os.path.join(dirpath, entry)
        if os.path.isdir(full):
            if recursive:
                found.extend(collect(full, recursive))
        elif os.path.isfile(full) and entry.lower().endswith(SUPPORTED_EXTS):
            found.append(full)
    return found


def process(src, fmt, quality, keep, custom_out, backend, used=None):
    """返回 (dict|None, error)。写盘一律走 tmp -> rename，NEVER 中途破坏源文件。"""
    src = os.path.abspath(src)
    used = used if used is not None else set()
    out = output_path(src, fmt, keep, custom_out)
    if os.path.abspath(out) == src:
        # 兜底：任何情况下都不允许输出路径等于输入路径
        base, ext = os.path.splitext(src)
        out = base + "-compressed" + ext
    out = dedupe(os.path.abspath(out), used)

    before = os.path.getsize(src)
    tmp = out + ".tmp"
    ok, err = True, ""

    if backend == "pillow":
        ok = compress_with_pillow(src, tmp, fmt, quality)
        err = "" if ok else "Pillow 转换失败"
    else:
        template = dict((n, t) for n, t in BACKENDS[fmt])[backend]
        ok, err = run_backend(backend, template, src, tmp, quality)

    if not ok or not os.path.isfile(tmp):
        if os.path.exists(tmp):
            os.remove(tmp)
        return None, err or "压缩失败"

    os.replace(tmp, out)
    after = os.path.getsize(out)
    return {
        "input": src,
        "output": out,
        "input_size": before,
        "output_size": after,
        "ratio": round(after / before, 4) if before else 0.0,
        "backend": backend,
    }, ""


def main():
    ap = argparse.ArgumentParser(description="图片压缩 / 格式转换")
    ap.add_argument("input", help="文件或目录")
    ap.add_argument("-f", "--format", default="webp", choices=list(FORMATS), help="默认 webp")
    ap.add_argument("-q", "--quality", type=int, default=80)
    ap.add_argument("-k", "--keep", action="store_true", help="保留原文件")
    ap.add_argument("-r", "--recursive", action="store_true")
    ap.add_argument("-o", "--output", help="单文件模式的输出路径")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    target = os.path.abspath(args.input)
    if not os.path.exists(target):
        sys.stderr.write("Error: %s 不存在\n" % args.input)
        return 2
    if not 0 <= args.quality <= 100:
        sys.stderr.write("Error: 质量必须在 0-100\n")
        return 2

    backend = detect_backend(args.format)
    if backend is None:
        backend = "pillow"
        probe = subprocess.run([sys.executable, "-c", "import PIL"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if probe.returncode != 0:
            sys.stderr.write(
                "Error: 本机无可用压缩后端。可安装其一：cwebp / ImageMagick / python Pillow\n")
            return 3

    if os.path.isdir(target):
        files = collect(target, args.recursive)
        if not files:
            sys.stderr.write("Error: 目录下无受支持图片\n")
            return 2
        results, failures, used = [], [], set()
        for f in files:
            res, err = process(f, args.format, args.quality, args.keep, None, backend, used)
            if res:
                results.append(res)
            else:
                failures.append({"file": f, "error": err})
        tin = sum(r["input_size"] for r in results)
        tout = sum(r["output_size"] for r in results)
        if args.json:
            print(json.dumps({"backend": backend, "files": results, "failures": failures,
                              "summary": {"count": len(results), "input": tin, "output": tout,
                                          "saving_pct": round((1 - tout / tin) * 100, 1) if tin else 0}},
                             ensure_ascii=False))
        else:
            for r in results:
                print("%s -> %s (%d%% reduction)" % (r["input"], r["output"],
                                                     round((1 - r["ratio"]) * 100)))
            for f in failures:
                print("FAIL %s: %s" % (f["file"], f["error"]))
            print("\n共 %d 个：%s -> %s（节省 %s%%）" % (
                len(results),
                fmt_size(tin), fmt_size(tout),
                round((1 - tout / tin) * 100, 1) if tin else 0))
        return 0

    res, err = process(target, args.format, args.quality, args.keep, args.output, backend)
    if not res:
        sys.stderr.write("Error: %s\n" % err)
        return 3
    if args.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print("%s -> %s（节省 %d%%）" % (res["input"], res["output"], round((1 - res["ratio"]) * 100)))
    return 0


def fmt_size(n):
    if n < 1024:
        return "%dB" % n
    if n < 1024 * 1024:
        return "%dKB" % round(n / 1024)
    return "%.1fMB" % (n / 1024 / 1024)


if __name__ == "__main__":
    sys.exit(main())
