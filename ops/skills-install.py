#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 skillhub 平台补装/取包 tri-* skill。

用途：本仓库为自维护 fork。tri-intent 的路由表会引用一些本仓库未纳入的 skill，
本工具负责把它们从平台取回并落盘，随后应由补丁层统一加固。

用法：
    python ops/skills-install.py --detect              # 只报告缺失集（只读）
    python ops/skills-install.py --detect --install    # 检出缺失并全部补装
    python ops/skills-install.py --slugs tri-pm,tri-wiki --install
    python ops/skills-install.py --detect --dry-run    # 预演，不写盘

关键环境事实（实测，见 ops/patches/README.md 与本仓库 memory）：
  * 下载端点为 **query 形式**：GET /api/v1/download?slug=<slug>
    → 302 → https://skillhub-*.cos.accelerate.myqcloud.com/skills/<nsId>/<slug>/<ver>.zip
    注意：path 形式 /api/v1/download/<slug> 返回 405（形状错误）
  * 平台**不提供 sha256**（version.json 的 sha256 为空串）
  * 枚举某作者全部 skill：GET /api/v1/users/<handle>/skills?page=N
    （pageSize 固定 20，pageSize 参数不生效）
  * **Python 是原生 Windows 程序，读不到 Git Bash 的 /tmp** → 本脚本不做临时文件中转
  * 已知不可得：tri-forge（平台 skills/download 双 404，作者名下 92/92 全量枚举零命中；
    且上游 .gitignore 显式排除了 tri-forge/，属作者有意私有）
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    """向上找含 .git 的目录。不使用固定层级——本工具可能被移动。"""
    for cand in (start, *start.parents):
        if (cand / ".git").exists():
            return cand
    return start


REPO = find_repo_root(Path(__file__).resolve().parent)
DL = "https://api.skillhub.cn/api/v1/download?slug={slug}"
UA = {"User-Agent": "tri-skills-fork-installer/1.0"}
VERSION_RE = re.compile(r"^version:\s*([0-9]+(?:\.[0-9]+)*)", re.MULTILINE)

# 已确认在任何可达源都不存在的 slug（本地磁盘 / git 全历史 / 原作者仓库 / 平台 92/92 枚举）
UNAVAILABLE = {"tri-forge"}

# tri-intent 里出现的非 skill slug（子技能、文件名、版本标签等）
NOT_A_SKILL = {
    "tri-audio", "tri-image", "tri-video", "tri-ppt",          # tri-mm children
    "tri-charter", "tri-require", "tri-design", "tri-devenv",   # tri-sdlc children
    "tri-impl", "tri-cr", "tri-test", "tri-release", "tri-ops",
    "tri-xxx", "tri-x", "tri-skill",
}


def local_skills() -> set[str]:
    return {p.name for p in REPO.glob("tri-*") if (p / "SKILL.md").is_file()}


def mentioned_by_intent() -> dict[str, int]:
    """统计 tri-intent 全文提及的 tri-* slug 次数。"""
    rx = re.compile(r"\btri-[a-z0-9]+(?:-[a-z0-9]+)*\b")
    cnt: dict[str, int] = {}
    base = REPO / "tri-intent"
    if not base.is_dir():
        return cnt
    for p in base.rglob("*.md"):
        for m in rx.findall(p.read_text(encoding="utf-8", errors="ignore")):
            cnt[m] = cnt.get(m, 0) + 1
    return cnt


def detect() -> list[tuple[str, int]]:
    local, cnt = local_skills(), mentioned_by_intent()
    miss = []
    for slug, n in cnt.items():
        if slug in local or slug in UNAVAILABLE or slug in NOT_A_SKILL:
            continue
        if slug.startswith("tri-intent-") or re.search(r"-\d{6,}$", slug):
            continue                      # 文件名 / 日期标签
        miss.append((slug, n))
    return sorted(miss, key=lambda x: -x[1])


def fetch(slug: str, timeout: int = 90):
    req = urllib.request.Request(DL.format(slug=slug), headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(), r.geturl(), None
    except urllib.error.HTTPError as e:
        return None, None, f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001
        return None, None, f"{type(e).__name__}: {e}"


def install(slug: str, dry: bool) -> dict:
    target = REPO / slug
    if target.exists():
        return {"slug": slug, "status": "skip", "detail": "目录已存在"}

    data, final, err = fetch(slug)
    if err:
        return {"slug": slug, "status": "fail", "detail": err}

    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = [n for n in z.namelist() if not n.endswith("/")]
            if dry:
                return {"slug": slug, "status": "dry", "files": len(names),
                        "detail": final, "zipsize": len(data)}
            target.mkdir(parents=True, exist_ok=True)
            for n in names:
                src = z.read(n)
                dst = target / n
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src)      # 字节级写入，不做行尾翻译
    except zipfile.BadZipFile as e:
        return {"slug": slug, "status": "fail", "detail": f"非 zip 包：{e}"}

    ver = None
    sm = target / "SKILL.md"
    if sm.is_file():
        m = VERSION_RE.search(sm.read_text(encoding="utf-8", errors="ignore")[:4000])
        ver = m.group(1) if m else None
    return {"slug": slug, "status": "ok", "files": len(names), "version": ver, "detail": final}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detect", action="store_true", help="从 tri-intent 路由引用检出缺失集")
    ap.add_argument("--slugs", default="", help="逗号分隔的显式 slug 列表")
    ap.add_argument("--install", action="store_true", help="实际写入（默认只报告）")
    ap.add_argument("--dry-run", action="store_true", help="下载但只报告，不写盘")
    args = ap.parse_args()

    if args.slugs:
        slugs = [s.strip() for s in args.slugs.split(",") if s.strip()]
    elif args.detect:
        found = detect()
        print(f"# 检出的缺失 skill（{len(found)} 个，按被引用次数排序）\n")
        print("| slug | tri-intent 引用次数 |")
        print("|---|---|")
        for s, n in found:
            print(f"| `{s}` | {n} |")
        print()
        slugs = [s for s, _ in found]
    else:
        print("需指定 --detect 或 --slugs", file=sys.stderr)
        return 2

    if not slugs:
        print("无待补装的 skill。")
        return 0

    mode = "DRY-RUN" if args.dry_run else ("APPLY" if args.install else "REPORT-ONLY")
    print(f"# 补装 · {mode} · {len(slugs)} 个\n")
    print("| slug | 版本 | 文件数 | 包大小 | 结果 |")
    print("|---|---|---|---|---|")

    rows = []
    for s in slugs:
        if not args.install and not args.dry_run:
            # 只用 HEAD 式探测，不下载内容
            data, final, err = fetch(s)
            if err:
                print(f"| `{s}` | - | - | - | 🔴 {err} |")
                rows.append({"slug": s, "status": "fail"})
            else:
                print(f"| `{s}` | - | - | {len(data)//1024}KB | ⏸ 待安装 |")
                rows.append({"slug": s, "status": "dry"})
            continue
        r = install(s, dry=args.dry_run)
        rows.append(r)
        if r["status"] == "ok":
            print(f"| `{s}` | {r.get('version') or '?'} | {r['files']} | - | ✅ 已写入 |")
        elif r["status"] == "dry":
            print(f"| `{s}` | - | {r['files']} | {r['zipsize']//1024}KB | ⏸ 预演通过 |")
        elif r["status"] == "skip":
            print(f"| `{s}` | - | - | - | ⏭ {r['detail']} |")
        else:
            print(f"| `{s}` | - | - | - | 🔴 {r['detail']} |")

    ok = sum(1 for r in rows if r["status"] in ("ok", "dry"))
    fail = [r for r in rows if r["status"] == "fail"]
    print(f"\n成功/预演通过 **{ok}/{len(slugs)}**")
    if fail:
        print("失败：")
        for r in fail:
            print(f"- `{r['slug']}`：{r['detail']}")
    if args.install:
        print("\n**下一步（必做）**：运行补丁层加固新增 skill ——")
        print("    python ops/patches/apply.py")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
