#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-pm 产物与知识包校验器（差距 G6 + G10' + G13 的落地实现）。

用途
----
1. ``--check-refs``     命令范式中的 ``**<框架名>**`` 引用是否可解析（防悬空引用）
2. ``--check-sections`` 框架文件的 MUST-SECTIONS 块是否可解析（完成判据的事实源）
3. ``--check-size``     单文件词数是否超上限（分层加载体积守卫）
4. ``--check-syntax``   是否残留 Claude Code 专有语法
5. ``--check-assembly`` 单次装配体积是否超上限
6. ``--artifact``       产物是否含该框架的全部必含章节
   ``--framework``

退出码
------
0 = 全部通过；非 0 = 存在失败项（详见输出）。
``--artifact`` 模式下缺失章节逐条列出。

词数口径
--------
中文按**字**计、英文按**词**计（源项目为纯英文，用 ``wc -w`` 统计；tri-pm 产物为中英混排，
单纯 ``wc -w`` 会把整段中文算作 1 个词，故采用混合口径）。该口径仅用于体积守卫，
不用于与源项目的字数对比。

用法示例
--------
    python scripts/validate_pm_artifact.py --all
    python scripts/validate_pm_artifact.py --check-refs
    python scripts/validate_pm_artifact.py --artifact PRD-demo.md --framework create-prd
    python scripts/validate_pm_artifact.py --check-assembly create-prd write-prd
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
REFERENCES = SKILL_ROOT / "references"
FRAMEWORKS = REFERENCES / "frameworks"
WORKFLOWS = REFERENCES / "workflows"

# G13 裁定上限（依据 references/distillation-baseline.md §九 D-B）
# 2026-09-03 修订（D-B 修订记录）：按实测数据校准——
#   常驻层实测 4,569 词；框架最大 1,337 词（gtm-motions）；命令最大 1,416 词
#   （performance-audit-static）；最坏理论装配 7,322 词。
#   单文件 900→1,500（源项目自身渐进披露警告阈值为 3,000 词，取其一半；
#   结构红线优先于散文压缩）；装配 3,500→8,000（实测最坏 + ~9% 余量）。
MAX_FILE_WORDS = 1500
MAX_ASSEMBLY_WORDS = 8000
RESIDENT_FILES = ["distillation-baseline.md", "distilled-architecture.md"]

# 专有语法残留检测（差距报告 Part 6 同款）
SYNTAX_PATTERNS = [
    (re.compile(r"\$ARGUMENTS"), "$ARGUMENTS"),
    (re.compile(r"/pm-[a-z-]+:"), "/pm-*:command 硬引用"),
]

MUST_SECTIONS_RE = re.compile(
    r"##\s*必含章节清单[^\n]*\n(.*?)(?=\n##\s|\Z)", re.S
)
SECTION_ITEM_RE = re.compile(r"^-\s*\[\s*[ xX]\s*\]\s*(.+?)\s*$", re.M)
OPTIONAL_HEADER_RE = re.compile(r"^###\s*[^\n]*(?:可选|OPTIONAL)", re.M | re.I)
REF_RE = re.compile(r"\*\*([a-z0-9][a-z0-9-]*)\*\*")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.S)
# 引用协议锚点（D-C 约定）：命令文件中的框架引用 MUST 带「引用…：」标记，
# 形如 〔引用技能：`**create-prd**`〕；无标记的普通粗体（如 **unit**）NEVER 视为引用。
REF_MARKER_RE = re.compile(r"引用[技能命令流程工作流]*\s*[：:]")

CJK_RE = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
LATIN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'/\-]*")


def word_count(text: str) -> int:
    """中文按字、英文按词的混合口径。"""
    return len(CJK_RE.findall(text)) + len(LATIN_RE.findall(text))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def framework_index() -> dict[str, Path]:
    """{框架名: 文件路径}，不含 -part2 等拆分后缀。

    同名主干优先取**无 part 后缀**的文件（MUST-SECTIONS 块位于 part1；
    曾因排序使 `-part2` 抢占索引导致误报「缺块」，2026-09-03 修复）。
    """
    if not FRAMEWORKS.is_dir():
        return {}
    idx: dict[str, Path] = {}
    for p in sorted(FRAMEWORKS.rglob("*.md")):
        stem = re.sub(r"-part\d+$", "", p.stem)
        cur = idx.get(stem)
        if cur is None or (re.search(r"-part\d+$", cur.stem) and not re.search(r"-part\d+$", p.stem)):
            idx[stem] = p
    return idx


def workflow_files() -> list[Path]:
    if not WORKFLOWS.is_dir():
        return []
    return sorted(WORKFLOWS.rglob("*.md"))


def parse_must_sections(text: str) -> list[str] | None:
    """解析 MUST-SECTIONS 块。返回 None 表示该框架**没有**该块。

    块范围到下一个 H2（`## `）为止——中间的 H3 子标题（如画布类的
    `### Left Side: Creating Value` 分组）**不截断**块，其下条目照常收录；
    但标题含「可选 / OPTIONAL」的子块条目 NEVER 参与 MUST 判定（D-C 约定）。
    """
    m = MUST_SECTIONS_RE.search(text)
    if not m:
        return None
    items: list[str] = []
    in_optional = False
    for line in m.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            in_optional = bool(re.match(r"#+\s+[^\n]*(?:可选|OPTIONAL)", stripped, re.I))
            continue
        if in_optional:
            continue
        im = re.match(r"^-\s*\[\s*[ xX]\s*\]\s*(.+?)\s*$", stripped)
        if im:
            items.append(im.group(1).strip())
    return items


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


# ---------------------------------------------------------------- 校验项


def check_refs() -> int:
    idx = framework_index()
    files = workflow_files()
    if not files:
        print("[check-refs] 跳过：workflows/ 目录不存在或为空")
        return 0
    print(f"[check-refs] 扫描 {len(files)} 个命令文件，框架索引 {len(idx)} 条")
    dangling: list[tuple[str, str, str]] = []
    total = 0
    for wf in files:
        body = strip_frontmatter(read_text(wf))
        for i, line in enumerate(body.splitlines(), start=1):
            # 引用协议（D-C 约定）：引用 MUST 带「引用…：」标记；
            # 无标记的普通粗体强调（如 **unit**、**manual**）NEVER 视为引用。
            if not REF_MARKER_RE.search(line):
                continue
            for m in REF_RE.finditer(line):
                name = m.group(1)
                if len(name) < 3 or name.isdigit():
                    continue
                total += 1
                if name not in idx:
                    dangling.append((wf.relative_to(SKILL_ROOT).as_posix(), name, str(i)))
    print(f"[check-refs] 引用总数 {total}，悬空 {len(dangling)}")
    for path, name, line in dangling:
        print(f"  悬空引用  {path}:{line}  **{name}**")
    if dangling:
        print(f"[check-refs] ❌ 失败：{len(dangling)} 处悬空引用")
        return 1
    print("[check-refs] ✅ 通过：0 悬空引用")
    return 0


def check_sections() -> int:
    idx = framework_index()
    if not idx:
        print("[check-sections] 跳过：frameworks/ 目录不存在或为空")
        return 0
    print(f"[check-sections] 扫描 {len(idx)} 个框架文件")
    missing: list[str] = []
    empty: list[str] = []
    counts: list[tuple[str, int]] = []
    for name, path in sorted(idx.items()):
        items = parse_must_sections(read_text(path))
        if items is None:
            missing.append(path.relative_to(SKILL_ROOT).as_posix())
        elif not items:
            empty.append(path.relative_to(SKILL_ROOT).as_posix())
        else:
            counts.append((name, len(items)))
    for p in missing:
        print(f"  缺 MUST-SECTIONS 块  {p}")
    for p in empty:
        print(f"  MUST-SECTIONS 块为空  {p}")
    total_sections = sum(c for _, c in counts)
    print(
        f"[check-sections] 有清单 {len(counts)} 个，章节条目合计 {total_sections}；"
        f"缺块 {len(missing)}，空块 {len(empty)}"
    )
    if missing or empty:
        print("[check-sections] ❌ 失败")
        return 1
    print("[check-sections] ✅ 通过")
    return 0


def check_size() -> int:
    files = list(FRAMEWORKS.rglob("*.md")) + workflow_files() if FRAMEWORKS.is_dir() else workflow_files()
    if not files:
        print("[check-size] 跳过：无文件可检")
        return 0
    print(f"[check-size] 扫描 {len(files)} 个文件，上限 {MAX_FILE_WORDS} 词")
    over = []
    for p in files:
        n = word_count(read_text(p))
        if n > MAX_FILE_WORDS:
            over.append((p.relative_to(SKILL_ROOT).as_posix(), n))
    for p, n in sorted(over, key=lambda x: -x[1]):
        print(f"  超限  {p}  {n} 词（+{n - MAX_FILE_WORDS}）")
    print(f"[check-size] 超限 {len(over)} / {len(files)}")
    if over:
        print("[check-size] ❌ 失败")
        return 1
    print("[check-size] ✅ 通过")
    return 0


def check_syntax() -> int:
    files: list[Path] = []
    for d in (FRAMEWORKS, WORKFLOWS):
        if d.is_dir():
            files += sorted(d.rglob("*.md"))
    if not files:
        print("[check-syntax] 跳过：无文件可检")
        return 0
    print(f"[check-syntax] 扫描 {len(files)} 个文件")
    hits = []
    for p in files:
        text = read_text(p)
        for pat, label in SYNTAX_PATTERNS:
            for m in pat.finditer(text):
                line = text[: m.start()].count("\n") + 1
                hits.append((p.relative_to(SKILL_ROOT).as_posix(), line, label))
    for p, line, label in hits:
        print(f"  残留  {p}:{line}  {label}")
    print(f"[check-syntax] 残留 {len(hits)} 处")
    if hits:
        print("[check-syntax] ❌ 失败")
        return 1
    print("[check-syntax] ✅ 通过")
    return 0


def check_assembly(framework: str, workflow: str | None = None) -> int:
    idx = framework_index()
    if framework not in idx:
        print(f"[check-assembly] ❌ 找不到框架「{framework}」")
        return 1
    total = 0
    detail = []
    for name in RESIDENT_FILES:
        p = REFERENCES / name
        if p.is_file():
            n = word_count(read_text(p))
            total += n
            detail.append((f"常驻层/{name}", n))
    fw = idx[framework]
    n = word_count(read_text(fw))
    total += n
    detail.append((f"框架/{fw.name}", n))
    if workflow:
        wf = None
        for p in workflow_files():
            if p.stem == workflow:
                wf = p
                break
        if wf is None:
            print(f"[check-assembly] ❌ 找不到命令「{workflow}」")
            return 1
        n = word_count(read_text(wf))
        total += n
        detail.append((f"命令/{wf.name}", n))
    for label, n in detail:
        print(f"  {label:<45} {n:>6} 词")
    print(f"  {'合计':<45} {total:>6} 词 / 上限 {MAX_ASSEMBLY_WORDS}")
    if total > MAX_ASSEMBLY_WORDS:
        print("[check-assembly] ❌ 失败：超出单次装配上限")
        return 1
    print("[check-assembly] ✅ 通过")
    return 0


def check_artifact(artifact: str, framework: str) -> int:
    idx = framework_index()
    if framework not in idx:
        print(f"[artifact] ❌ 找不到框架「{framework}」（可用：{len(idx)} 个）")
        return 1
    apath = Path(artifact)
    if not apath.is_file():
        print(f"[artifact] ❌ 产物不存在：{artifact}")
        return 1
    sections = parse_must_sections(read_text(idx[framework]))
    if not sections:
        print(
            f"[artifact] ⚠️ 框架「{framework}」无 MUST-SECTIONS 清单，"
            f"按 tri-pm 纪律**显式降级为无章节门**，不静默放行通过"
        )
        return 0
    text = read_text(apath)
    miss = []
    hit = []
    for s in sections:
        # 章节名形如「Executive Summary — 执行摘要」或纯中文/纯英文
        candidates = [c.strip() for c in re.split(r"[—–|/]", s) if c.strip()]
        if any(c and c in text for c in candidates):
            hit.append(s)
        else:
            miss.append(s)
    print(f"[artifact] 产物 {apath.name} ／ 框架 {framework} ／ 必含章节 {len(sections)}")
    for s in hit:
        print(f"  ✅ {s}")
    for s in miss:
        print(f"  ❌ 缺失  {s}")
    if miss:
        print(f"[artifact] ❌ 失败：缺失 {len(miss)} / {len(sections)} 个必含章节")
        return 1
    print("[artifact] ✅ 通过：必含章节齐全")
    return 0


# ---------------------------------------------------------------- 入口


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="tri-pm 产物与知识包校验器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--check-refs", action="store_true", help="校验命令中的框架引用可解析")
    ap.add_argument("--check-sections", action="store_true", help="校验框架文件的 MUST-SECTIONS 块")
    ap.add_argument("--check-size", action="store_true", help="校验单文件词数上限")
    ap.add_argument("--check-syntax", action="store_true", help="校验专有语法残留")
    ap.add_argument("--check-assembly", nargs="+", metavar=("FRAMEWORK", "WORKFLOW"),
                    help="校验单次装配体积（常驻层 + 框架 [+ 命令]）")
    ap.add_argument("--artifact", metavar="PATH", help="待校验产物路径")
    ap.add_argument("--framework", metavar="NAME", help="--artifact 对应的框架名")
    ap.add_argument("--all", action="store_true", help="跑 refs + sections + size + syntax")
    args = ap.parse_args(argv)

    if args.artifact:
        if not args.framework:
            ap.error("--artifact 必须同时指定 --framework")
        return check_artifact(args.artifact, args.framework)

    codes: list[int] = []
    ran = False

    if args.all or args.check_refs:
        codes.append(check_refs()); ran = True; print()
    if args.all or args.check_sections:
        codes.append(check_sections()); ran = True; print()
    if args.all or args.check_size:
        codes.append(check_size()); ran = True; print()
    if args.all or args.check_syntax:
        codes.append(check_syntax()); ran = True; print()
    if args.check_assembly:
        fw = args.check_assembly[0]
        wf = args.check_assembly[1] if len(args.check_assembly) > 1 else None
        codes.append(check_assembly(fw, wf)); ran = True; print()

    if not ran:
        ap.print_help()
        return 0

    failed = sum(1 for c in codes if c != 0)
    print("=" * 60)
    if failed:
        print(f"❌ {failed} / {len(codes)} 项校验未通过")
        return 1
    print(f"✅ 全部 {len(codes)} 项校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
