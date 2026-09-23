#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""家族版本一致性校验（tri-forge 承接职能）。

原由上游 tri-forge 的 `scripts/sync_registry.py` 提供。该 skill 被作者私有化
（上游 `.gitignore` 显式排除 `tri-forge/`），本仓库为自维护 fork，自行重建。

校验**五点**版本声明是否一致（规范见 `references/version-check-spec.md` §五）：

  P1  <skill>/SKILL.md  frontmatter `version:`        ← 唯一真源（基准）
  P2  <skill>/CHANGELOG.md 首个 `## [x.y.z]`          ← 须 = P1，且为全文件最大版本
  P3  <skill>/_meta.json `version`                   ← 须 = P1
  P4  ~/.workbuddy/skills/.skills_store_lock.json    ← 须 = P1（通常不存在，存在时才校验）
  P5  <skill>/README.md 的**版本声明**                ← 须 = P1

P5 只认两种**声明形式**：shields.io 徽章（`badge/version-<v>-`）或 README 顶部 frontmatter。
**不认**散文提及（如「基于 xxx v1.4.4」）与历史升级记录（如「当前版本：2.1.1」）——改动那些是篡改历史。

用法：
    python scripts/check_registry.py --check                 # 报告漂移（非零退出码）
    python scripts/check_registry.py --check --json
    python scripts/check_registry.py --apply                 # 规则化回写 P3/P5
    python scripts/check_registry.py --apply --dry-run       # 只报告将回写什么
    python scripts/check_registry.py --check --skill tri-coding

退出码：0 = 一致；1 = 存在漂移；2 = 参数/环境错误

**--apply 的边界（与上游原设计一致）**：
  - P3 / P5 可**规则化**回写（按语义值同步为 P1）
  - **P2 属人工内容**——CHANGELOG 条目需人写，本脚本**只报告、NEVER 代写**
  - P4 在仓库外（平台安装态），MUST 显式加 `--include-lock` 才会回写，默认只报告

> ⚠️ 实现说明：`ops/version-lint.py`（仓库运维侧）实现同一套规则。
> 两者是刻意的重复——tri-forge 需能**独立安装**，不得依赖仓库根的其他文件。
> 修订规则时 MUST 同步两处（且以 `references/version-check-spec.md` §五 为准）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
LOCK = Path.home() / ".workbuddy" / "skills" / ".skills_store_lock.json"

FM = re.compile(r"^version:[ \t]*([^\s#]+)", re.M)
CL_ALL = re.compile(r"^##[ \t]*\[([0-9]+(?:\.[0-9]+)*)\]", re.M)
SEMVER = re.compile(r"^\d+(\.\d+)*$")
BADGE = re.compile(r"(shields\.io/badge/version-)([0-9]+(?:\.[0-9]+)*)(-)")
RMFM = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)


def vcmp(a, b):
    if not a or not b or not SEMVER.match(a) or not SEMVER.match(b):
        return None
    sa, sb = a.split("."), b.split(".")
    for i in range(max(len(sa), len(sb))):
        x = int(sa[i]) if i < len(sa) else 0
        y = int(sb[i]) if i < len(sb) else 0
        if x != y:
            return 1 if x > y else -1
    return 0


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def readme_decl(t: str):
    m = RMFM.match(t)
    if m:
        mv = FM.search(m.group(1))
        if mv:
            return mv.group(1).strip(), "frontmatter"
    mb = BADGE.search(t)
    if mb:
        return mb.group(2), "badge"
    return None, None


def check_one(d: Path, lock: dict) -> dict:
    r = {"slug": d.name, "P1": None, "P2": None, "P3": None, "P4": None,
         "P5": None, "P5_form": None, "drift": []}

    t = read(d / "SKILL.md")
    m = FM.search(t[:4000])
    r["P1"] = m.group(1).strip() if m else None
    if not r["P1"]:
        r["drift"].append("P1 缺失：SKILL.md frontmatter 无 version")
    elif not SEMVER.match(r["P1"]):
        r["drift"].append(f"P1 格式非法：{r['P1']}")

    cl = read(d / "CHANGELOG.md")
    vs = CL_ALL.findall(cl)
    if vs:
        r["P2"] = vs[0]
        mx = vs[0]
        for v in vs:
            if (vcmp(v, mx) or 0) > 0:
                mx = v
        if r["P1"] and r["P2"] != r["P1"]:
            r["drift"].append(f"P2≠P1（CHANGELOG 首条 {r['P2']} ≠ {r['P1']}）")
        if mx != r["P2"]:
            r["drift"].append(f"P2 非最大（首条 {r['P2']} < {mx}）")

    mj = d / "_meta.json"
    if mj.is_file():
        try:
            r["P3"] = json.loads(read(mj)).get("version")
        except json.JSONDecodeError:
            r["drift"].append("P3 解析失败：_meta.json 非法 JSON")
        if r["P3"] and r["P1"] and r["P3"] != r["P1"]:
            r["drift"].append(f"P3≠P1（_meta.json {r['P3']} ≠ {r['P1']}）")

    ent = lock.get(d.name)
    if isinstance(ent, dict) and ent.get("version"):
        r["P4"] = ent["version"]
        if r["P1"] and r["P4"] != r["P1"]:
            r["drift"].append(f"P4≠P1（lock.json {r['P4']} ≠ {r['P1']}）")

    rt = read(d / "README.md")
    if rt:
        v5, form = readme_decl(rt)
        r["P5"], r["P5_form"] = v5, form
        if v5 and r["P1"] and v5 != r["P1"]:
            r["drift"].append(f"P5≠P1（README({form}) {v5} ≠ {r['P1']}）")

    return r


def apply_fixes(d: Path, r: dict, lock: dict, include_lock: bool, dry: bool) -> list:
    """规则化回写 P3 / P5（P2 人工、P4 默认只报告）。返回动作清单。"""
    acts = []
    if not r["P1"] or not SEMVER.match(r["P1"]):
        return acts
    want = r["P1"]

    # P3
    mj = d / "_meta.json"
    if mj.is_file() and r["P3"] and r["P3"] != want:
        if not dry:
            try:
                meta = json.loads(read(mj))
                meta["version"] = want
                mj.write_bytes((json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
            except (OSError, json.JSONDecodeError):
                return acts
        acts.append(f"{r['slug']}：_meta.json {r['P3']} → {want}")

    # P5
    rm = d / "README.md"
    if rm.is_file() and r["P5"] and r["P5"] != want:
        if not dry:
            raw = rm.read_bytes()
            t = raw.decode("utf-8")
            if r["P5_form"] == "frontmatter":
                m = RMFM.match(t)
                if m:
                    new = RMFM.sub(lambda mm: FM.sub(f"version: {want}", mm.group(0), count=1),
                                   t, count=1)
                else:
                    new = t
            else:
                new = BADGE.sub(lambda mm: f"{mm.group(1)}{want}{mm.group(3)}", t, count=1)
            rm.write_bytes(new.encode("utf-8"))
        acts.append(f"{r['slug']}：README({r['P5_form']}) {r['P5']} → {want}")

    # P4（仅显式 include_lock）
    if include_lock and r["P4"] and r["P4"] != want and LOCK.is_file():
        if not dry:
            try:
                data = json.loads(read(LOCK))
                data["skills"][r["slug"]]["version"] = want
                LOCK.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
            except (OSError, KeyError, json.JSONDecodeError):
                return acts
        acts.append(f"{r['slug']}：lock.json {r['P4']} → {want}")

    return acts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-lock", action="store_true")
    ap.add_argument("--skill", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not (args.check or args.apply):
        args.check = True

    targets = sorted(p for p in REPO.glob("tri-*") if (p / "SKILL.md").is_file())
    if args.skill:
        targets = [p for p in targets if p.name == args.skill]
    if not targets:
        print("未找到目标 skill", file=sys.stderr)
        return 2

    lock = {}
    if LOCK.is_file():
        try:
            lock = json.loads(read(LOCK)).get("skills") or {}
        except json.JSONDecodeError:
            lock = {}

    results = [check_one(d, lock) for d in targets]
    acts = []
    if args.apply:
        for d, r in zip(targets, results):
            acts += apply_fixes(d, r, lock, args.include_lock, args.dry_run)

    bad = [r for r in results if r["drift"]]
    if args.json:
        print(json.dumps({"results": results, "drift_count": len(bad),
                          "actions": acts, "dry_run": args.dry_run}, ensure_ascii=False, indent=2))
    else:
        mode = "APPLY" + ("（dry-run）" if args.dry_run else "") if args.apply else "CHECK"
        print(f"# 家族版本一致性校验 · {mode}\n")
        print(f"检查 **{len(results)}** 个 skill；**存在漂移 {len(bad)} 个**\n")
        if bad:
            print("| skill | P1 | P2 | P3 | P4 | P5 |")
            print("|---|---|---|---|---|---|")
            for r in bad:
                p5 = r["P5"] or "—"
                if r["P5_form"]:
                    p5 += f"({r['P5_form']})"
                print(f"| `{r['slug']}` | {r['P1'] or '—'} | {r['P2'] or '—'} "
                      f"| {r['P3'] or '—'} | {r['P4'] or '—'} | {p5} |")
            print("\n## 漂移明细\n")
            for r in bad:
                print(f"### `{r['slug']}`（基准 P1 = {r['P1'] or '?'}）\n")
                for x in r["drift"]:
                    print(f"- {x}")
                print()
        n2 = sum(1 for r in bad if any(x.startswith("P2") for x in r["drift"]))
        n3 = sum(1 for r in bad if any(x.startswith("P3") for x in r["drift"]))
        n5 = sum(1 for r in bad if any(x.startswith("P5") for x in r["drift"]))
        if n2:
            print(f"> **P2（{n2} 个）属人工内容**，需手写 CHANGELOG 条目，本脚本 NEVER 代写。")
        if n3 or n5:
            print(f"> **P3（{n3}）/ P5（{n5}）可规则化回写**：`python scripts/check_registry.py --apply`")
        if acts:
            print(f"\n## 已回写 {len(acts)} 处\n")
            for a in acts:
                print(f"- {a}")
        elif args.apply:
            print("\n无需回写。")

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
