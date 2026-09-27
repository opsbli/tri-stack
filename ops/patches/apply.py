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
    - drop_block：按 begin/end 锚点整块删除。**纯删除型修正的幂等表达**——
      `begin` 命中即删，`begin` 已缺失即判「已应用」（块已不存在）；
      锚点不唯一时 **fail-closed**（不做动作并报 not_found），绝不「猜一个」删掉

绝不删除文件（`drop_block` 只删除**文件内文本块**，不做文件级删除）；绝不触碰 exclude_paths。
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
    ptext = norm_lf(pbytes.decode("utf-8"))
    written = skipped = 0
    details = []
    for t in spec_targets(repo, skip):
        if t.is_file():
            try:
                cur = norm_lf(t.read_bytes().decode("utf-8", errors="replace"))
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
    ptext = norm_lf(pbytes.decode("utf-8"))
    written = skipped = 0
    details = []
    for t in script_targets(repo, skip, op["glob"], dest):
        if t.is_file():
            try:
                cur = norm_lf(t.read_bytes().decode("utf-8", errors="replace"))
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


def norm_lf(s: str) -> str:
    """把任意行尾归一化为 LF —— **去掉全部 `\\r`**。

    教训（README 坑 5）：本仓库工作区存在 `\\r\\r\\n`（CRLF blob 又被检出/写入链补一个 CR）
    的文件。`.replace("\\r\\n", "\\n")` 只会吃掉后一个 `\\r`、**留下裸 `\\r`**，
    归一化后行尾变成 `\r\n` ⇒ **多行 `old`（LF 书写）永不命中**，op 静默报 `not_found`；
    用在 `sync_spec` / `sync_script` 的比对里则会**每次判「不一致」而反复重写**（幂等失效）。
    先替 `\\r\\n` 再替 `\\r` **同样是错的**（`\\r\\r\\n` 被拆成两次匹配 ⇒ 仍得 `\\n\\n`）。
    故一律 `replace("\\r", "")`。
    """
    return s.replace("\r", "")


def read_norm(f: Path):
    """读取并归一化为 LF，同时记录原文件是否用 CRLF。

    归一化走后述 `norm_lf`（去掉全部 `\\r`），不再只替 `\\r\\n`。
    副作用：`\\r\\r\\n` 文件一旦因命中而被写入，会经 `write_keep` 归一为纯 CRLF。
    这是有意的——`.gitattributes` 的 `eol=lf` 会在入库时再归一为 LF，
    故 index diff 只显示真实内容变更。
    """
    raw = f.read_bytes()
    crlf = b"\r\n" in raw
    return norm_lf(raw.decode("utf-8", errors="replace")), crlf


def write_keep(f: Path, txt: str, crlf: bool) -> None:
    """按原文件的行尾风格写回，避免因归一化而引入整文件 diff。

    `crlf=True` 的文件一律写成**纯 CRLF**—— `\\r\\r\\n` 输入经 `norm_lf` 后已是纯 `\\n`，
    这里补回一个 `\\r` 即归一为 CRLF（不会写成 `\\r\\r\\n`）。
    """
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


def op_drop_block(op, repo, skip, dry):
    """整块删除 —— 补 `replace_text` 表达不了 `delete` 动作的能力缺口。

    缺口（可证明，见 README 坑 4 / patch-batch-workflow `references/lessons.md` #2）：
    纯删除型修正的 `new` 若不引入新文本，则改后文本的每个连续子串都已在改前文本中
    （含跨删除边界的接缝）⇒ `already_marker` 要么**改前已存在**（永不生效）、要么
    **改后不存在**（永不幂等）。故 `delete` 在本补丁层无法用 `replace_text` 表达，
    此前只能绕道「在 `new` 里塞一段改前不存在的新文本充当标记」。

    本 op 的判据（三态，与 `replace_text` 同构，但把「内容指纹」换成「块存在性」）：
      - `begin` 命中 → 删除 [begin 所在行首, end 所在行末]，本文件计 applied
      - `begin` 未命中 且 `removed_witness` 亦未命中 → 判「已应用」（块已不存在）
      - `begin` 未命中 但 `removed_witness` 仍命中 → 判 not_found（**锚点漂移 / 半删除态**）
    `removed_witness` 缺省取 `begin`（begin 必随块一起消失）。此时后两态合并为
    「begin 缺失 ⇒ 已应用」——这是纯删除型的正确幂等语义，代价是 **begin 写错会
    被误判为已应用**；故锚点唯一性 MUST 由构建期断言保证（工作流 Step 2：改前
    `txt.count(begin) == 1`），本 op 只是最后一道闸。需要更强保护时显式给出一个
    与 begin 不同的 `removed_witness`，即可恢复三态判别。

    **fail-closed（比 `replace_text` 更严）**：任一匹配文件出现
      `begin` 出现次数 ≠ 1、`end` 出现次数 ≠ 1、或 `end` 位于 `begin` 之前，
    该文件**不动作**并计入 not_found；只要 not_found > 0，整 op 状态即 not_found
    （`replace_text` 在部分成功时仍报 ok，本 op 刻意不沿用 —— 静默降级是坑 1 的同类）。

    字段：`glob` / `begin` / `end` / `removed_witness`? / `swallow_trailing_blank`?（默认 True）
    """
    begin = op["begin"].replace("\r\n", "\n")
    end = op["end"].replace("\r\n", "\n")
    witness = (op.get("removed_witness") or begin).replace("\r\n", "\n")
    swallow = op.get("swallow_trailing_blank", True)
    applied = already = missing = 0
    details = []
    for f in collect(repo, op["glob"], skip):
        try:
            txt, crlf = read_norm(f)
        except OSError:
            continue
        rel = f.relative_to(repo).as_posix()
        n_begin, n_end = txt.count(begin), txt.count(end)
        if n_begin == 0:
            if witness in txt:
                missing += 1
                details.append(f"{rel}：锚点漂移（begin 缺失但 removed_witness 仍在）")
            else:
                already += 1
            continue
        if n_begin != 1 or n_end != 1:
            missing += 1
            details.append(f"{rel}：锚点不唯一 begin×{n_begin} / end×{n_end}（fail-closed，不动作）")
            continue
        lines = txt.split("\n")
        i = next(k for k, ln in enumerate(lines) if begin in ln)
        j = next(k for k, ln in enumerate(lines) if end in ln)
        if j < i:
            missing += 1
            details.append(f"{rel}：end 出现在 begin 之前（锚点顺序异常，fail-closed）")
            continue
        lo, hi = i, j + 1
        if swallow and hi < len(lines) and lines[hi].strip() == "":
            hi += 1
        if not dry:
            write_keep(f, "\n".join(lines[:lo] + lines[hi:]), crlf)
        applied += 1
        details.append(f"{rel}：删 {hi - lo} 行（L{lo + 1}–L{hi}）")
    ok = bool(missing == 0 and (applied or already))
    return {"status": "ok" if ok else "not_found",
            "applied": applied, "already": already, "not_found": missing, "details": details}


DISPATCH = {"sync_spec": op_sync_spec, "replace_text": op_replace_text,
            "replace_regex": op_replace_regex,
            "sync_version_meta": op_sync_version_meta,
            "converge_version_section": op_converge_version_section,
            "sync_script": op_sync_script,
            "sync_readme_version": op_sync_readme_version,
            "drop_block": op_drop_block}


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
            elif r["type"] == "drop_block":
                desc = (f"删除 {r['applied']}｜已应用 {r['already']}"
                        f"｜未找到 {r['not_found']}")
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
