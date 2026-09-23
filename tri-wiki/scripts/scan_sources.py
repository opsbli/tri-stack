#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-wiki 门B：源数据扫描、格式识别、分级、去重标记（sources-manifest.json 产出）。

仅用 Python 标准库。确定性算法，prompt 层只调用并解析 JSON。

用法：
    python scan_sources.py --sources <目录或文件> [--only pdf,docx] [--out <过程目录>] --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

FORMAT_MAP = {
    ".pdf": ("convert", "tri-pdf2md"),
    ".docx": ("convert", "tri-docx2md"),
    ".doc": ("convert", "tri-docx2md"),
    ".pptx": ("convert", "tri-pptx2md"),
    ".ppt": ("convert", "tri-pptx2md"),
    ".xlsx": ("convert", "tri-xlsx2md"),
    ".xls": ("convert", "tri-xlsx2md"),
    ".html": ("convert", "tri-html2md"),
    ".htm": ("convert", "tri-html2md"),
    ".md": ("direct", None),
    ".markdown": ("direct", None),
    ".txt": ("direct", None),
    ".csv": ("direct", None),
}

MAGIC_CHECKS = [
    (b"%PDF", ".pdf"),
    (b"PK\x03\x04", "ooxml"),  # docx/pptx/xlsx 均为 zip 容器，扩展名细分
]

DIRECT_EXTS = {".md", ".markdown", ".txt", ".csv"}
SIMHASH_BITS = 64


def md5_of(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _tokenize(text: str):
    tokens = []
    buf = ""
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            if buf:
                tokens.append(buf.lower())
                buf = ""
            tokens.append(ch)
        elif ch.isalnum():
            buf += ch
        else:
            if buf:
                tokens.append(buf.lower())
                buf = ""
    if buf:
        tokens.append(buf.lower())
    return tokens


def simhash(text: str) -> int:
    feats = _tokenize(text)
    if not feats:
        return 0
    grams = feats + [feats[i] + feats[i + 1] for i in range(len(feats) - 1)]
    weights = [0] * SIMHASH_BITS
    for g in grams:
        hv = int(hashlib.md5(g.encode("utf-8")).hexdigest()[:16], 16)
        for i in range(SIMHASH_BITS):
            weights[i] += 1 if (hv >> i) & 1 else -1
    return sum(1 << i for i in range(SIMHASH_BITS) if weights[i] > 0)


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def detect_format(path: Path):
    ext = path.suffix.lower()
    if ext not in FORMAT_MAP:
        return None, "unsupported_extension"
    if path.stat().st_size == 0:
        return None, "empty_file"
    try:
        with open(path, "rb") as f:
            head = f.read(8)
    except OSError:
        return None, "unreadable"
    if ext == ".pdf" and not head.startswith(b"%PDF"):
        return None, "magic_mismatch"
    if ext in {".docx", ".pptx", ".xlsx"} and not head.startswith(b"PK"):
        return None, "magic_mismatch"
    return ext, None


def scan(sources, only, out_dir: Path):
    files = []
    for src in sources:
        p = Path(src)
        if p.is_dir():
            files.extend(sorted(x for x in p.rglob("*") if x.is_file()))
        elif p.is_file():
            files.append(p)
        else:
            print(f"[WARN] 路径不存在，跳过：{p}", file=sys.stderr)
    # 排除过程目录自身
    try:
        out_res = out_dir.resolve()
        files = [f for f in files if out_res not in f.resolve().parents]
    except OSError:
        pass

    manifest, seen_md5, direct_sims = [], {}, []
    for f in files:
        ext, err = detect_format(f)
        if err:
            manifest.append({"path": str(f), "format": f.suffix.lower().lstrip("."),
                             "size": f.stat().st_size, "category": "skip",
                             "skip_reason": err, "suggested_skill": None,
                             "md5": None, "dup_flag": None})
            continue
        only_ok = not only or ext.lstrip(".") in only
        cat, skill = FORMAT_MAP[ext]
        entry = {"path": str(f), "format": ext.lstrip("."), "size": f.stat().st_size,
                 "category": cat if only_ok else "skip",
                 "skip_reason": None if only_ok else "filtered_by_only",
                 "suggested_skill": skill, "md5": None, "dup_flag": None}
        digest = md5_of(f)
        entry["md5"] = digest
        if digest in seen_md5:
            entry["category"], entry["dup_flag"] = "duplicate", seen_md5[digest]
        else:
            seen_md5[digest] = str(f)
        if entry["category"] == "direct":
            try:
                text = f.read_text(encoding="utf-8-sig", errors="ignore")[:20000]
                sh = simhash(text)
                near = next((d["path"] for d, s in direct_sims if hamming(s, sh) <= 3), None)
                if near:
                    entry["dup_flag"] = f"near_dup:{near}"
                else:
                    direct_sims.append((entry, sh))
            except OSError:
                pass
        manifest.append(entry)

    summary = {
        "total": len(manifest),
        "direct": sum(1 for e in manifest if e["category"] == "direct"),
        "convert": sum(1 for e in manifest if e["category"] == "convert"),
        "skip": sum(1 for e in manifest if e["category"] == "skip"),
        "duplicate": sum(1 for e in manifest if e["category"] == "duplicate"),
        "by_skill": {},
    }
    for e in manifest:
        s = e.get("suggested_skill")
        if s:
            summary["by_skill"][s] = summary["by_skill"].get(s, 0) + 1

    return manifest, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="+", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out) if args.out else Path(".tribro") / "wiki"
    out_dir.mkdir(parents=True, exist_ok=True)
    only = {x.strip().lower().lstrip(".") for x in args.only.split(",") if x.strip()} or None

    manifest, summary = scan(args.sources, only, out_dir)
    result = {"generated_at": datetime.now().isoformat(timespec="seconds"),
              "sources": args.sources, "only": sorted(only) if only else [],
              "summary": summary, "files": manifest}
    out_file = out_dir / "sources-manifest.json"
    out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"扫描完成：共 {summary['total']} 文件（直通 {summary['direct']} / "
              f"转换 {summary['convert']} / 跳过 {summary['skip']} / 重复 {summary['duplicate']}）")
        print(f"清单已写入 {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
