#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地补丁层重放器（tri-skills）。

用途：把本仓库对上游 skill 的本地修正，表达为可**幂等重放**的操作。
每次 `skillhub upgrade` 整树替换 skill 目录后，重跑本脚本即可恢复修复。

用法：
    python ops/patches/apply.py             # 应用（幂等）
    python ops/patches/apply.py --dry-run   # 只报告将发生什么
    python ops/patches/apply.py --json      # 机器可读输出

幂等性：
    - sync_spec：按内容比对，已一致则跳过
    - replace_text：old 命中则替换；old 未命中但 already_marker 命中则判「已应用」；
      old 与 new 都未命中则判「未找到」并计入 warnings

绝不删除文件；绝不触碰 exclude_paths。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PATCH_DIR = Path(__file__).resolve().parent


def find_repo_root(start: Path) -> Path:
    """向上找含 .git 的目录。

    不使用固定层级（如 parent.parent）——本工具会被移动（曾位于 ops/patches/），
    固定层级会在迁移后静默指向错误的根，导致「静默不作用于任何文件」。
    """
    for cand in (start, *start.parents):
        if (cand / ".git").exists():
            return cand
    return start


REPO = find_repo_root(PATCH_DIR)
MANIFEST = PATCH_DIR / "manifest.json"

SKIP_PARTS_DEFAULT = {".workbuddy", ".git"}


def sha12(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def under_skip(p: Path, skip: set[str]) -> bool:
    return any(part in skip for part in p.parts)


def collect(repo: Path, glob: str, skip: set[str]):
    out = []
    for p in repo.glob(glob):
        if p.is_file() and not under_skip(p, skip):
            out.append(p)
    return sorted(out)


def spec_targets(repo: Path, skip: set[str]):
    """所有「SKILL.md 引用了 version-check-spec.md」的目录。"""
    targets = []
    for sm in sorted(repo.glob("**/SKILL.md")):
        if under_skip(sm, skip):
            continue
        try:
            txt = sm.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "version-check-spec.md" in txt:
            targets.append(sm.parent / "references" / "version-check-spec.md")
    return targets


def op_sync_spec(op, repo, skip, dry):
    """部署自带 spec。

    比对用**归一化文本**（LF）而非字节哈希：本仓库行尾本就混用
    （多数 .md 为 CRLF，新写入的 spec 为 LF），按字节比会误判为「不一致」
    并在每次运行时产生无意义的改写。
    """
    payload = PATCH_DIR / op["payload"]
    if not payload.is_file():
        return {"status": "error", "detail": f"payload 缺失：{payload}", "written": 0, "skipped": 0}
    pbytes = payload.read_bytes()
    ptext = pbytes.decode("utf-8").replace("\r\n", "\n")
    written = skipped = 0
    details = []
    for t in spec_targets(repo, skip):
        if t.is_file():
            try:
                cur = t.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")
            except OSError:
                cur = None
            if cur == ptext:
                skipped += 1
                continue
            details.append(f"覆盖 {t.relative_to(repo).as_posix()}")
        else:
            details.append(f"新增 {t.relative_to(repo).as_posix()}")
        if not dry:
            t.parent.mkdir(parents=True, exist_ok=True)
            t.write_bytes(pbytes)          # 字节级写入：不做行尾翻译，内容可复现
        written += 1
    return {"status": "ok", "written": written, "skipped": skipped, "details": details}


def read_norm(f: Path):
    """读取并归一化为 LF，同时记录原文件是否用 CRLF。"""
    raw = f.read_bytes()
    crlf = b"\r\n" in raw
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n"), crlf


def write_keep(f: Path, txt: str, crlf: bool) -> None:
    """按原文件的行尾风格写回，避免因归一化而引入整文件 diff。"""
    data = txt.replace("\n", "\r\n") if crlf else txt
    f.write_bytes(data.encode("utf-8"))


def op_replace_text(op, repo, skip, dry):
    """行尾无关的文本替换。

    匹配前统一归一化为 LF，写回时恢复原行尾风格。这样
    `old` / `already_marker` 用 LF 书写即可同时命中 LF 与 CRLF 文件——
    早期版本直接按字节匹配，遇到 CRLF 文件会静默不命中（表现为「应用 0」）。
    """
    old_lf = op["old"].replace("\r\n", "\n")
    new_lf = op["new"].replace("\r\n", "\n")
    marker = op.get("already_marker")
    if marker is None and len(op["new"]) >= 5:
        marker = op["new"]
    applied = already = missing = 0
    details = []
    for f in collect(repo, op["glob"], skip):
        try:
            txt, crlf = read_norm(f)
        except OSError:
            continue
        n_old = txt.count(old_lf)
        if n_old:
            if not dry:
                write_keep(f, txt.replace(old_lf, new_lf), crlf)
            applied += n_old
            details.append(f"{f.relative_to(repo).as_posix()} ×{n_old}")
        elif marker and marker in txt:
            already += 1
    if not applied and not already:
        missing = 1
    return {
        "status": "ok" if (applied or already) else "not_found",
        "applied": applied, "already": already, "not_found": missing,
        "details": details,
    }


DISPATCH = {"sync_spec": op_sync_spec, "replace_text": op_replace_text}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    skip = set(man.get("exclude_paths") or SKIP_PARTS_DEFAULT)

    results = []
    for op in man["ops"]:
        fn = DISPATCH.get(op["type"])
        if fn is None:
            results.append({"id": op["id"], "label": op["label"],
                            "status": "error", "detail": f"未知 op 类型 {op['type']}"})
            continue
        r = fn(op, REPO, skip, args.dry_run)
        r["id"] = op["id"]
        r["label"] = op["label"]
        r["type"] = op["type"]
        results.append(r)

    if args.json:
        print(json.dumps({"dry_run": args.dry_run, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        mode = "DRY-RUN" if args.dry_run else "APPLY"
        print(f"# 本地补丁层 · {mode}\n")
        print("| op | 说明 | 结果 |")
        print("|---|---|---|")
        for r in results:
            if r["type"] == "sync_spec":
                desc = f"写入 {r['written']}｜跳过 {r['skipped']}"
            elif r["type"] == "replace_text":
                desc = f"应用 {r['applied']}｜已应用 {r['already']}"
            else:
                desc = r.get("detail", "")
            mark = {"ok": "✅", "not_found": "⬜", "error": "🔴"}.get(r["status"], "?")
            print(f"| `{r['id']}` | {r['label']} | {mark} {desc} |")

        warn = [r for r in results if r["status"] not in ("ok",)]
        if warn:
            print("\n## 需注意\n")
            for r in warn:
                print(f"- `{r['id']}`：status={r['status']}（{r.get('detail','')}）")

        verbose = [r for r in results if r.get("details")]
        if verbose:
            print("\n## 明细\n")
            for r in verbose:
                print(f"### {r['id']} — {r['label']}\n")
                for d in r["details"][:60]:
                    print(f"- {d}")
                if len(r["details"]) > 60:
                    print(f"- …另有 {len(r['details']) - 60} 条")
                print()

    bad = [r for r in results if r["status"] == "error"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
