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
    - sync_script：同 sync_spec 同法，但目标由 glob 命中的 SKILL.md 推导父目录 + dest；
      文件不存在时创建目录并新增（用于给 skill 补带自有 scripts/）
    - replace_text：old 命中则替换；old 未命中但 already_marker 命中则判「已应用」；
      old 与 new 都未命中则判「未找到」并计入 warnings
    - replace_regex：同 replace_text，但 pattern 为正则（一行可多处）；
      另支持整行守卫 skip_line_containing 与文件跳过 skip_names / skip_prefixes
    - converge_version_section：already_marker 命中即跳过；无遗留标记的节一律不碰
    - sync_version_meta / sync_readme_version：语义值一致则跳过

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


def script_targets(repo: Path, skip: set[str], glob: str, dest: str):
    """按 glob 命中 SKILL.md，推导每个 skill 目录下的脚本落点。"""
    targets = []
    for sm in sorted(repo.glob(glob)):
        if under_skip(sm, skip) or not sm.is_file():
            continue
        targets.append(sm.parent / dest)
    return targets


def op_sync_script(op, repo, skip, dry):
    """部署自带脚本（如 scripts/check_update.py）到每个目标 skill 目录。

    与 `sync_spec` 同法：按**归一化文本**（LF）比对、**字节写入**，
    避免行尾风格差异造成无意义改写；目标不存在时创建父目录并新增。
    用途：给「STUB 里引用了 `scripts/check_update.py` 但自身不带 scripts/」的
    skill（如 tri-sdlc 的 9 个子 skill）补齐文件，使单 skill 独立安装成立。
    """
    payload = PATCH_DIR / op["payload"]
    if not payload.is_file():
        return {"status": "error", "detail": f"payload 缺失：{payload}", "written": 0, "skipped": 0}
    dest = op["dest"]
    pbytes = payload.read_bytes()
    ptext = pbytes.decode("utf-8").replace("\r\n", "\n")
    written = skipped = 0
    details = []
    for t in script_targets(repo, skip, op["glob"], dest):
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
        # 先判「已应用」：标记存在即跳过。
        # 关键：**锚点型注入**的 old 是「插入位置」，插入后锚点依然存在——
        # 若只在 old 缺失时才看标记，每次重放都会**重复注入**。
        # （曾因此把代码重复注入 43 份 ×3；幂等必须用内容指纹验证，不能只比输出。）
        if marker and marker in txt:
            already += 1
            continue
        n_old = txt.count(old_lf)
        if n_old:
            if not dry:
                write_keep(f, txt.replace(old_lf, new_lf), crlf)
            applied += n_old
            details.append(f"{f.relative_to(repo).as_posix()} ×{n_old}")
    if not applied and not already:
        missing = 1
    return {
        "status": "ok" if (applied or already) else "not_found",
        "applied": applied, "already": already, "not_found": missing,
        "details": details,
    }


def op_sync_version_meta(op, repo, skip, dry):
    """强制执行 §六 的 P1↔P3 一致性：_meta.json 的 version 同步为 SKILL.md frontmatter 的值。

    与原 tri-forge `sync_registry.py --apply` 的设计一致——它只回写 3 与 4，
    P2（CHANGELOG 首条）属人工内容，须人写条目，故本 op **不动 CHANGELOG**。

    本 op 是**规则化**而非字面量匹配：`old` 不适用，逐 skill 比对语义值。
    这样新增/同步 skill 后自动生效，且幂等（一致则跳过）。

    P4（`~/.workbuddy/skills/.skills_store_lock.json`）**不在本 op 范围内**——
    该文件在仓库外、属平台安装态，本补丁层的契约是「只作用于仓库内路径」。
    """
    import json as _json
    import re as _re

    fm = _re.compile(r"^version:[ \t]*([^\s#]+)", _re.M)
    written = skipped = missing = 0
    details = []
    for sm in collect(repo, op["glob"], skip):
        d = sm.parent
        mj = d / "_meta.json"
        if not mj.is_file():
            missing += 1
            continue
        try:
            t = sm.read_text(encoding="utf-8", errors="ignore")
            mv = fm.search(t[:4000])
            if not mv:
                details.append(f"跳过 {d.name}：SKILL.md 无 version")
                missing += 1
                continue
            want = mv.group(1).strip()
            meta = _json.loads(mj.read_text(encoding="utf-8"))
        except (OSError, _json.JSONDecodeError) as e:
            details.append(f"跳过 {d.name}：{type(e).__name__}")
            missing += 1
            continue
        cur = meta.get("version")
        if cur == want:
            skipped += 1
            continue
        if not dry:
            meta["version"] = want
            # 字节级写入，不做行尾翻译；保持 2 空格缩进与文件末换行
            mj.write_bytes((_json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        written += 1
        details.append(f"{d.name}：_meta.json {cur} → {want}")
    return {"status": "ok", "written": written, "skipped": skipped,
            "missing": missing, "details": details}


def op_sync_readme_version(op, repo, skip, dry):
    """强制执行 §六 的 P1↔P5 一致性：README 的**版本声明**同步为 SKILL.md 的值。

    P5 是 §六 原文未列、但实测存在的第 5 处同步点（本仓库补充）。只认两种声明形式：
      (a) shields.io 徽章：`![version](...badge/version-<v>-blue)`
      (b) README 顶部 frontmatter：`---\\nversion: <v>\\n---`
    **不碰**散文提及（如「基于 xxx v1.4.4」）与历史升级记录（如「当前版本：2.1.1」）——
    那些不是同步点，改动它们是篡改历史。

    规则化而非字面量匹配：逐 skill 比对语义值，幂等（一致则跳过）。
    """
    import re as _re

    fm = _re.compile(r"^version:[ \t]*([^\s#]+)", _re.M)
    rmfm = _re.compile(r"\A---\r?\n(.*?)\r?\n---", _re.S)
    rmfm_ver = _re.compile(r"^version:[ \t]*([^\s#]+)", _re.M)
    badge = _re.compile(r"(shields\.io/badge/version-)([0-9]+(?:\.[0-9]+)*)(-)")

    written = skipped = missing = 0
    details = []
    for sm in collect(repo, op["glob"], skip):
        d = sm.parent
        rm = d / "README.md"
        if not rm.is_file():
            missing += 1
            continue
        try:
            p1v = fm.search(sm.read_text(encoding="utf-8", errors="ignore")[:4000])
            if not p1v:
                missing += 1
                continue
            want = p1v.group(1).strip()
            raw = rm.read_bytes()
            t = raw.decode("utf-8")
        except OSError:
            missing += 1
            continue

        form, cur = None, None
        m = rmfm.match(t)
        if m:
            mv = rmfm_ver.search(m.group(1))
            if mv:
                form, cur = "frontmatter", mv.group(1).strip()
        if form is None:
            mb = badge.search(t)
            if mb:
                form, cur = "badge", mb.group(2)

        if form is None:
            missing += 1
            continue
        if cur == want:
            skipped += 1
            continue

        if not dry:
            if form == "frontmatter":
                new = rmfm.sub(lambda mm: rmfm_ver.sub(f"version: {want}", mm.group(0), count=1), t, count=1)
            else:
                new = badge.sub(lambda mm: f"{mm.group(1)}{want}{mm.group(3)}", t, count=1)
            rm.write_bytes(new.encode("utf-8"))
        written += 1
        details.append(f"{d.name}：README({form}) {cur} → {want}")
    return {"status": "ok", "written": written, "skipped": skipped,
            "missing": missing, "details": details}


def op_converge_version_section(op, repo, skip, dry):
    """规则化收敛「版本检查与更新机制」节为**瘦指针 STUB**。

    背景：家族规范 `references/version-check-spec.md` §六 要求该节为 ≤30 行 STUB
    （执行方式 + 真源指针），**禁止内联**四态判定细则 / 升级流程 / 版本比较算法。
    上游同步来的版本节是 35 行「远端 skillhub 口径」全量版，与本仓库已落地的
    自维护模式（`SELF_MAINTAINED = True`，完全跳过远端请求）**直接矛盾**。

    判据（只对**命中遗留标记**的节生效，不碰已合规的节）：
      - 节内含 `already_marker` → 已收敛，跳过（幂等靠内容标记，不靠输出比对）
      - 节内含 `legacy_markers` 任一 → 遗留节，收敛为 STUB
      - 两者皆无 → 跳过并留痕（如已合规的 9 行 STUB，或试算中含 skill 专属内容者）
      - `force_skills` 可显式追加待收敛 skill；`preserve` 可为其指定
        「从该标记起原样保留」，用于节内混有 skill 专属职能的情形。

    `{slug}` 占位由 skill 目录名填充 ⇒ 对新增 / 同步的 skill 自动生效。
    """
    import re as _re

    head = _re.compile(r"^## 版本检查与更新机制.*$", _re.M)
    nxt = _re.compile(r"^## ", _re.M)
    marker = op["already_marker"]
    legacy = op.get("legacy_markers") or []
    force = set(op.get("force_skills") or [])
    preserve = op.get("preserve") or {}
    template = op["template"]

    written = skipped = missing = 0
    details = []
    for sm in collect(repo, op["glob"], skip):
        try:
            txt, crlf = read_norm(sm)
        except OSError:
            continue
        slug = sm.parent.name
        m = head.search(txt)
        if not m:
            missing += 1
            continue
        m2 = nxt.search(txt, m.end())
        end = m2.start() if m2 else len(txt)
        sec = txt[m.start():end]

        if marker in sec:
            skipped += 1
            continue
        if not any(lm in sec for lm in legacy) and slug not in force:
            skipped += 1
            details.append(f"跳过 {slug}：版本节无遗留标记（保留原文）")
            continue

        keep_from = preserve.get(slug)
        tail = ""
        if keep_from and keep_from in sec:
            tail = sec[sec.index(keep_from):].strip("\n")

        new_sec = template.replace("{slug}", slug).rstrip("\n") + "\n\n"
        if tail:
            new_sec += tail + "\n\n"

        old_lines = sec.strip("\n").count("\n") + 1
        new_lines = new_sec.strip("\n").count("\n") + 1
        if not dry:
            write_keep(sm, txt[:m.start()] + new_sec + txt[end:], crlf)
        written += 1
        details.append(f"{slug}：{old_lines} 行 → {new_lines} 行" + ("（保留专属段）" if tail else ""))
    return {"status": "ok" if (written or skipped) else "not_found",
            "written": written, "skipped": skipped, "missing": missing,
            "details": details}


def op_replace_regex(op, repo, skip, dry):
    """按**正则**批量替换（行尾无关），并支持两种「不碰」的守卫。

    与 `replace_text` 同源（共用 read_norm / write_keep），差别有三：
      - `pattern` 是正则，用 `subn` 逐行全局替换（一行可命中多处）；
      - `skip_line_containing`：任一子串出现在该行 → **整行不动**。
        用于把历史记载排除在外：CHANGELOG 里的 `skillhub install <slug> --upgrade`
        与主路径安装提示共享 `skillhub install` 前缀，只有这个守卫能区分二者。
      - `skip_names` / `skip_prefixes`：按文件名 / 相对路径前缀整文件跳过。

    `already_marker` 命中即整文件判「已应用」——幂等必须靠**内容指纹**，
    不能只比输出文本（早期教训：锚点型注入会重复注入 43 份 ×3）。
    """
    import re as _re

    pat = _re.compile(op["pattern"])
    repl = op["replacement"].replace("\r\n", "\n")
    marker = op.get("already_marker")
    guards = op.get("skip_line_containing") or []
    names = set(op.get("skip_names") or ())
    prefixes = tuple(op.get("skip_prefixes") or ())
    applied = already = 0
    details = []
    for f in collect(repo, op["glob"], skip):
        rel = f.relative_to(repo).as_posix()
        if f.name in names or (prefixes and rel.startswith(prefixes)):
            continue
        try:
            txt, crlf = read_norm(f)
        except OSError:
            continue
        if marker and marker in txt:
            already += 1
            continue
        lines = txt.split("\n")
        n = 0
        for i, ln in enumerate(lines):
            if any(g in ln for g in guards):
                continue
            new_ln, k = pat.subn(repl, ln)
            if k:
                lines[i] = new_ln
                n += k
        if not n:
            continue
        if not dry:
            write_keep(f, "\n".join(lines), crlf)
        applied += n
        details.append(f"{rel} ×{n}")
    if not applied and not already:
        return {"status": "not_found", "applied": 0, "already": 0,
                "not_found": 1, "details": details}
    return {"status": "ok", "applied": applied, "already": already,
            "not_found": 0, "details": details}


DISPATCH = {"sync_spec": op_sync_spec, "replace_text": op_replace_text,
            "replace_regex": op_replace_regex,
            "sync_version_meta": op_sync_version_meta,
            "converge_version_section": op_converge_version_section,
            "sync_script": op_sync_script,
            "sync_readme_version": op_sync_readme_version}


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
            if r["type"] in ("sync_spec", "sync_script"):
                desc = f"写入 {r['written']}｜跳过 {r['skipped']}"
            elif r["type"] in ("sync_version_meta", "sync_readme_version",
                               "converge_version_section"):
                desc = f"写入 {r['written']}｜跳过 {r['skipped']}｜N/A {r['missing']}"
            elif r["type"] == "replace_text":
                desc = f"应用 {r['applied']}｜已应用 {r['already']}"
            elif r["type"] == "replace_regex":
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
