#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""四处版本一致性校验（`tri-intent/references/version-gate.md` §六 的可执行实现）。

§六 定义版本号在 4 处重复存在，任一处漏改都会造成运行态与源码态不一致：

  P1  <skill>/SKILL.md  frontmatter `version:`        ← 唯一真源（基准）
  P2  <skill>/CHANGELOG.md 首个 `## [x.y.z]`          ← 须与 P1 相等，且为全文件最大版本
  P3  <skill>/_meta.json `version`                   ← 平台识别可斜杠激活所需
  P4  ~/.workbuddy/skills/.skills_store_lock.json    ← 平台注册表（自维护环境通常不存在）
  P5  <skill>/README.md 的**版本声明**                ← §六 未列，但实测存在的第 5 处

关于 P5（本仓库补充，§六 原文只列 4 处）：
  实测 40 个 skill 中有 12 个在 README 里声明版本，且存在两种形式：
    (a) shields.io 徽章：`![version](https://img.shields.io/badge/version-1.1.0-blue)`
    (b) README 顶部 frontmatter：`---\nversion: 1.2.2\n---`
  **只认这两种声明形式**。README 中的散文提及（如「基于 tri-docx2md v1.4.4」）
  与历史升级记录（如「当前版本：2.1.1／上一版本：2.1.0」）**不是同步点**，不计入。
  依据：`tri-humanize/CHANGELOG.md` 记载过一次五处联动修复
  （「README 徽章 1.0.0 → 1.1.0，与 SKILL.md / CHANGELOG / _meta.json / tests 五处一致」），
  说明作者自己也把 README 版本声明当作同步点。

原实现为 tri-forge 的 `scripts/sync_registry.py`。tri-forge 未随任何可达源分发
（本地磁盘 / git 全历史 / 原作者仓库 / 平台 92 个 skill 全量枚举均无命中；且上游
`.gitignore` 显式排除了 `tri-forge/`，属作者有意私有），故本仓库自行实现等效校验。

§六 的历史教训（保留）：tri-intent v1.9.0 发布时 CHANGELOG 写了 1.9.0 而 frontmatter
仍是 1.8.0，漂移被打包进发布产物，导致任何人全新安装后自检都显示 1.8.0。
同批次 tri-music 2.2.0/2.1.1 同样中招。**这类漂移无法靠人工纪律避免。**

用法：
    python ops/version-lint.py                   # 人类可读报告
    python ops/version-lint.py --json            # 机器可读
    python ops/version-lint.py --emit-baseline   # 输出 ops/versions.json（自主版本线基线）
    python ops/version-lint.py --skill tri-coding  # 只查一个

退出码：0 = 无漂移 / 1 = 存在漂移 / 2 = 参数或环境错误

修复方式：
    P3/P4 可由补丁层规则化修正（op `sync_version_meta`，幂等）：
        python ops/patches/apply.py
    P2 属**人工内容**——CHANGELOG 条目需人写，本工具只报告不代写
    （与原 sync_registry.py 的 --apply 设计一致：它只回写 3 与 4）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for cand in (start, *start.parents):
        if (cand / ".git").exists():
            return cand
    return start


REPO = find_repo_root(Path(__file__).resolve().parent)
LOCK = Path.home() / ".workbuddy" / "skills" / ".skills_store_lock.json"
BASELINE = Path(__file__).resolve().parent / "versions.json"

FM_VERSION = re.compile(r"^version:\s*([^\s#]+)", re.MULTILINE)
CL_HEAD = re.compile(r"^##\s*\[([0-9]+(?:\.[0-9]+)*)\]", re.MULTILINE)
CL_ALL = re.compile(r"^##\s*\[([0-9]+(?:\.[0-9]+)*)\]", re.MULTILINE)
SEMVER = re.compile(r"^\d+(\.\d+)*$")
# P5：只认「版本声明」两种形式，见文件头说明
BADGE = re.compile(r"shields\.io/badge/version-([0-9]+(?:\.[0-9]+)*)-")
RMFM = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
RMFM_VER = re.compile(r"^version:[ \t]*([^\s#]+)", re.MULTILINE)


def readme_decl(t: str):
    """返回 (版本, 形式) 或 (None, None)。只认声明形式，不认散文/历史记录。"""
    m = RMFM.match(t)
    if m:
        mv = RMFM_VER.search(m.group(1))
        if mv:
            return mv.group(1).strip(), "frontmatter"
    mb = BADGE.search(t)
    if mb:
        return mb.group(1), "badge"
    return None, None


def vcmp(a: str, b: str):
    """逐段整数比较。任一不合格式返回 None。"""
    if not a or not b or not SEMVER.match(a) or not SEMVER.match(b):
        return None
    sa, sb = a.split("."), b.split(".")
    for i in range(max(len(sa), len(sb))):
        x = int(sa[i]) if i < len(sa) else 0
        y = int(sb[i]) if i < len(sb) else 0
        if x < y:
            return -1
        if y < x:
            return 1
    return 0


def read_text(p: Path):
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def load_lock() -> dict:
    if not LOCK.is_file():
        return {}
    try:
        d = json.loads(LOCK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    s = d.get("skills")
    return s if isinstance(s, dict) else {}


def check_skill(d: Path, lock: dict):
    slug = d.name
    r = {"slug": slug, "P1": None, "P2": None, "P2_is_max": None,
         "P3": None, "P4": None, "P5": None, "P5_form": None,
         "drift": [], "notes": []}

    # P1
    sm = d / "SKILL.md"
    t = read_text(sm)
    if t is None:
        r["drift"].append("P1 缺失：SKILL.md 不存在")
        return r
    m = FM_VERSION.search(t[:4000])
    r["P1"] = m.group(1).strip() if m else None
    if not r["P1"]:
        r["drift"].append("P1 缺失：frontmatter 无 version")
    elif not SEMVER.match(r["P1"]):
        r["drift"].append(f"P1 格式非法（应形如 1.2.3）：{r['P1']}")

    # P2
    cl = d / "CHANGELOG.md"
    tc = read_text(cl)
    if tc is None:
        r["notes"].append("P2 N/A：无 CHANGELOG.md")
    else:
        versions = CL_ALL.findall(tc)
        head = CL_HEAD.search(tc)
        r["P2"] = head.group(1) if head else None
        if not r["P2"]:
            r["notes"].append("P2 N/A：CHANGELOG 无 `## [x.y.z]` 条目")
        else:
            top = versions[0] if versions else None
            mx = None
            for v in versions:
                if mx is None or (vcmp(v, mx) or 0) > 0:
                    mx = v
            r["P2_is_max"] = (mx == r["P2"])
            if not r["P2_is_max"]:
                r["drift"].append(f"P2 非最大值：首个 {r['P2']}，文件最大 {mx}")
            if r["P1"] and r["P2"] != r["P1"]:
                r["drift"].append(f"P2≠P1：CHANGELOG 首条 {r['P2']} ≠ SKILL.md {r['P1']}")

    # P3
    mj = d / "_meta.json"
    tm = read_text(mj)
    if tm is None:
        r["notes"].append("P3 N/A：无 _meta.json")
    else:
        try:
            r["P3"] = json.loads(tm).get("version")
        except json.JSONDecodeError:
            r["drift"].append("P3 解析失败：_meta.json 非法 JSON")
        if r["P3"] is None:
            r["notes"].append("P3 N/A：_meta.json 无 version 字段")
        elif r["P1"] and r["P3"] != r["P1"]:
            r["drift"].append(f"P3≠P1：_meta.json {r['P3']} ≠ SKILL.md {r['P1']}")

    # P4
    ent = lock.get(slug)
    if ent is None:
        r["notes"].append("P4 N/A：lock.json 无该条目（自维护环境常见）")
    else:
        r["P4"] = ent.get("version")
        if r["P4"] and r["P1"] and r["P4"] != r["P1"]:
            r["drift"].append(f"P4≠P1：lock.json {r['P4']} ≠ SKILL.md {r['P1']}")

    # P5（README 版本声明）
    t5 = read_text(d / "README.md")
    if t5 is None:
        r["notes"].append("P5 N/A：无 README.md")
    else:
        v5, form = readme_decl(t5)
        r["P5"], r["P5_form"] = v5, form
        if v5 is None:
            r["notes"].append("P5 N/A：README 无版本声明（徽章/frontmatter）")
        elif r["P1"] and v5 != r["P1"]:
            r["drift"].append(f"P5≠P1：README({form}) {v5} ≠ SKILL.md {r['P1']}")

    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--skill", default=None)
    ap.add_argument("--emit-baseline", action="store_true",
                    help="把当前 SKILL.md 版本写为 ops/versions.json（自主版本线基线）")
    args = ap.parse_args()

    dirs = sorted(p for p in REPO.glob("tri-*") if (p / "SKILL.md").is_file())
    if args.skill:
        dirs = [p for p in dirs if p.name == args.skill]
    if not dirs:
        print("未找到任何 tri-* skill（或 --skill 未命中）", file=sys.stderr)
        return 2

    lock = load_lock()
    results = [check_skill(d, lock) for d in dirs]

    if args.emit_baseline:
        base = {
            "generated": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
            "purpose": "自维护 fork 的版本线基线。本仓库不再跟随上游版本号，此文件记录当前各 skill 版本，作为自主版本线的 v1 起点与一致性校验的参照。",
            "source_note": "版本取自各 tri-*/SKILL.md 的 frontmatter（§六 定义的唯一真源）。",
            "skills": {r["slug"]: r["P1"] for r in sorted(results, key=lambda x: x["slug"])},
        }
        BASELINE.write_bytes((json.dumps(base, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"已写入 {BASELINE.relative_to(REPO).as_posix()}（{len(base['skills'])} 个 skill）")

    if args.json:
        print(json.dumps({"results": results,
                          "drift_count": sum(1 for r in results if r["drift"])},
                         ensure_ascii=False, indent=2))
    else:
        bad = [r for r in results if r["drift"]]
        print("# 四处版本一致性校验（version-gate.md §六）\n")
        print(f"检查 {len(results)} 个 skill；**存在漂移 {len(bad)} 个**\n")
        print("| skill | P1 SKILL.md | P2 CHANGELOG | P2 是最大 | P3 _meta | P4 lock | P5 README | 判定 |")
        print("|---|---|---|---|---|---|---|---|")
        for r in sorted(results, key=lambda x: x["slug"]):
            mark = "🔴 漂移" if r["drift"] else "✅"
            p2max = "—" if r["P2_is_max"] is None else ("是" if r["P2_is_max"] else "**否**")
            p5 = r["P5"] or "—"
            if r["P5_form"]:
                p5 += f"({r['P5_form']})"
            print(f"| `{r['slug']}` | {r['P1'] or '—'} | {r['P2'] or '—'} | {p2max} "
                  f"| {r['P3'] or '—'} | {r['P4'] or '—'} | {p5} | {mark} |")
        if bad:
            print("\n## 漂移明细\n")
            for r in bad:
                print(f"### `{r['slug']}`（基准 P1 = {r['P1'] or '?'}）\n")
                for x in r["drift"]:
                    print(f"- {x}")
                print()
        n2 = sum(1 for r in bad if any(x.startswith("P2") for x in r["drift"]))
        n3 = sum(1 for r in bad if any(x.startswith("P3") for x in r["drift"]))
        if n2:
            print(f"> **P2（{n2} 个）属人工内容**，需手写 CHANGELOG 条目，本工具不代写。")
        if n3:
            print(f"> **P3（{n3} 个）可规则化修正**：`python ops/patches/apply.py`（op `sync_version_meta`）。")

    return 1 if any(r["drift"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
