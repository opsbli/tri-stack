#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""gate_lint.py — tri-coding §质量标准 两条 prompt 层 MUST 的可执行载体（tt5 批）。

两条 MUST 此前**只写在条文里、无任何可执行载体**，所以 tri-stack-train 的
requirements.md 可以把 AC 期望结果写成「本机冒烟通过」、shell-probe.test.ts 可以把
`existsSync` 的实现缺陷固化成期望行为，而没有任何东西拦下。本脚本是它们的可执行实现。

子命令：
  ac      --file <requirements.md> [--json]   §6 验收标准：禁词 + 可观测断言
  mock    --file <test.ts> [--src <subject>] [--json]   反同源假设静态检查
  self-test                                    内置自检（含 M4a/M4b 实证夹具）

返回码：0 = 合规；1 = 命中违规；2 = 用法错误。

边界（诚实声明，非缺陷）：
- `ac` 的禁词扫描覆盖整节验收标准正文，但**跳过 blockquote 行与代码围栏**：
  模板自己用 blockquote 引用禁词清单，若一并扫描会对自己的模板误报；
  验收点写成正文就扫得到。可观测断言的判定则按**验收点块**逐块扫。
- `ac` 的「可观测断言」是**形态启发式**：只认 DOM 选择器 / IPC 事件 / 进程退出码 /
  文件哈希 / 可测阈值五类（判据原文列举的五类）。真实但非此五类的断言方式
  （如「日志包含 X」）不会被识别，属预期的召回下限。
- `mock` 用正则而非 TS 解析器，**不做类型推导、不解析作用域**：
  ① 只识别 `vi.fn()` / `vi.mocked()` / `jest.spyOn()` / `mock*.mockX()` 四种 stubbing 惯用法；
  ② 被测源码的「直接调用依赖」= 调用标识符 − 文件内声明 − JS 关键字，**不解析 import 来源**，
     因此跨文件 re-export 的间接依赖查不到；
  ③ 不做「是否已补走真实实现的对照用例」的判断——`vi.importActual` 在 M4a 实证文件里
     **恰好存在**（partial mock），若拿它当豁免会直接漏掉实证案例，故不作豁免。
  命中即报；是否补对照用例由人判。需要豁免时用行内标记登记理由，见 `--ack-reason`。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# ═══════════════════════ ac 判据（templates/requirements.md §6） ═══════════════════════

# 判据原文：「本节每条验收点 MUST 可机器判定，NEVER 出现「本机冒烟 / 用户冒烟 / 用户确认 /
# 手动通过 / 肉眼观察 / 看起来正常」等字样」。列表逐字取自条文，非本脚本自创。
AC_FORBIDDEN: tuple[str, ...] = (
    "本机冒烟", "用户冒烟", "用户确认", "手动通过", "肉眼观察", "看起来正常",
)

# 判据原文列举的五类可观测断言：DOM 选择器+断言 / IPC 事件名+期望 payload /
# 进程退出码 / 文件哈希 / 可测阈值。
ASSERT_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"querySelector|getElementById|getAttribute|innerHTML|innerText|textContent|DOM|选择器"),
    re.compile(r"IPC|ipcRenderer|webContents\s*\.\s*send|payload|事件名|onMessage"),
    re.compile(r"退出码|exitCode|exit[_ ]?code|process\s*\.\s*exit"),
    re.compile(r"哈希|\bhash\b|sha256|md5|checksum|digest", re.I),
    re.compile(r"[≥≤]\s*\d|\d+\s*%|\d+\s*(?:ms|s|MB|KB|GB)\b|阈值"),
)

ACCEPT_HEADING_RE = re.compile(r"^(#{2,4})\s*(?:\d+\s*[.)、]?\s*)?验收标准")
CHECKBOX_RE = re.compile(r"^\s*[-*+]\s*\[[ xX]\]")


def _find_acceptance_section(lines: list[str]) -> tuple[int, int] | None:
    """定位「## N. 验收标准」节，返回 0-based 行区间 [start, end)。找不到返回 None。"""
    start: int | None = None
    level = 0
    for i, ln in enumerate(lines):
        m = ACCEPT_HEADING_RE.match(ln)
        if m:
            start, level = i, len(m.group(1))
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^(#{1,%d})\s" % level, lines[j]):
            end = j
            break
    return start, end


def audit_ac_text(text: str) -> dict:
    """校验 requirements.md 文本的验收标准节。

    两条判据（逐条对应 templates/requirements.md §6 条文）：
      ① 禁词——节内正文出现 AC_FORBIDDEN 任一字样即违规（`ac-forbidden-word`）；
         扫描时跳过 blockquote 行与代码围栏——模板自己用 blockquote 引用禁词清单，
         一并扫会对自己的模板误报，而验收点写成正文就扫得到。
      ② 可观测断言——每个验收点块 MUST 命中 ASSERT_PATTERNS 至少一类
         （未命中报 `ac-missing-assertion`）。
    整份文件无验收标准节报 `ac-missing-section`。
    """
    lines = text.replace("\r\n", "\n").split("\n")
    span = _find_acceptance_section(lines)
    if span is None:
        return {"file": None, "check": "ac", "violations": 1,
                "violationDetails": [{"type": "ac-missing-section",
                                      "detail": "未找到「## N. 验收标准」节——验收标准即无载体"}],
                "acknowledged": [], "skipped": False,
                "stats": {"acceptancePoints": 0}}

    start, end = span
    body = lines[start:end]

    # 切验收点块：每个 checkbox 行起，到下一个 checkbox 或节末为止
    cb_idx = [i for i, ln in enumerate(body) if CHECKBOX_RE.match(ln)]
    blocks: list[tuple[int, int, str]] = []
    for k, i in enumerate(cb_idx):
        j = cb_idx[k + 1] if k + 1 < len(cb_idx) else len(body)
        blocks.append((start + i, start + j, body[i]))

    # 代码围栏开关（跨整节）；blockquote 行跳过——模板自己用 blockquote 引用禁词清单，
    # 若也扫会对自己的模板误报（验收点块内仍可命中，不放宽正文扫描范围）
    fence = False
    forbidden: list[dict] = []
    for ln in body:
        s = ln.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or s.startswith(">"):
            continue
        for w in AC_FORBIDDEN:
            if w in s:
                forbidden.append({"type": "ac-forbidden-word", "word": w,
                                  "line": ln.rstrip(),
                                  "detail": "「%s」把通过定义成用户说通过，等于无验收" % w})

    no_assert: list[dict] = []
    for b_start, b_end, head in blocks:
        blk = body[b_start - start:b_end - start]
        fence2 = False
        clean = []
        for ln in blk:
            if ln.strip().startswith("```"):
                fence2 = not fence2
                continue
            if not fence2:
                clean.append(ln)
        if not any(p.search("\n".join(clean)) for p in ASSERT_PATTERNS):
            no_assert.append({"type": "ac-missing-assertion", "blockStart": b_start + 1,
                              "blockEnd": b_end, "head": head.rstrip()[:80],
                              "detail": "验收点未附任何可观测断言（DOM / IPC / 退出码 / 哈希 / 阈值）"})

    return {"file": None, "check": "ac", "violations": len(forbidden) + len(no_assert),
            "violationDetails": forbidden + no_assert, "acknowledged": [],
            "skipped": False, "stats": {"acceptancePoints": len(blocks),
                                        "forbiddenHits": len(forbidden),
                                        "missingAssertion": len(no_assert)}}


def audit_ac(path: Path) -> dict:
    """校验单个 requirements.md 文件（`ac --file` 入口）。"""
    res = audit_ac_text(path.read_bytes().decode("utf-8", errors="replace"))
    res["file"] = str(path)
    return res


# ═══════════════════════ mock 判据（§质量标准 反同源假设 ②） ═══════════════════════

# 判据原文：「`vi.mock` / `mockReturnValue` / `mockResolvedValue` 的目标 MUST NOT 是
# 被测对象**直接调用**的那个依赖函数」。以下四种 stubbing 惯用法覆盖常见形态。
_STUB_PATTERNS: tuple[re.Pattern, ...] = (
    # factory 内：existsSync: vi.fn()   /   'existsSync': vi.fn()
    re.compile(r"['\"]?([A-Za-z_$][\w$]*)['\"]?\s*:\s*vi\s*\.\s*fn\s*\("),
    # const m = vi.mocked(existsSync)   /   vi.mocked<MockedFn>(existsSync)
    re.compile(r"vi\s*\.\s*mocked\s*(?:<[^<>]*)?>?\s*\(\s*([A-Za-z_$][\w$]*)"),
    # jest.spyOn(fs, 'existsSync')   /   jest.spyOn(globalThis, "existsSync")
    re.compile(r"jest\s*\.\s*spyOn\s*\([^,]*?['\"]([A-Za-z_$][\w$]*)['\"]"),
    # const m = jest.spyOn(fs, "existsSync").mockReturnValue(...)
    re.compile(r"spyOn\s*\([^,]*?,\s*['\"]([A-Za-z_$][\w$]*)['\"]\s*\)\s*\.\s*mock\w*"),
)
# mockExistsSync.mockReturnValue(...) → 候选符号 existsSync（去 mock 前缀）
_ALIAS_STUB_RE = re.compile(
    r"\b(m[A-Z][\w$]*)\s*\.\s*(?:mockReturnValue|mockReturnValueOnce|mockImplementation|"
    r"mockImplementationOnce|mockResolvedValue|mockRejectedValue)\s*\(")

TEST_SUFFIXES = (".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx",
                 ".test.js", ".test.jsx", ".spec.js", ".spec.jsx")
SOURCE_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")

# 行内豁免标记：登记技术理由后才生效，避免静默放过
ACK_RE = re.compile(r"(?://|#)\s*gate-lint:\s*same-origin-ok\b\s*(\S.{8,})")

JS_KEYWORDS = frozenset("""
await break case catch class const continue debugger default delete do else
export extends finally for function if import in instanceof new of return super
switch this throw try typeof var void while with yield as from satisfies any
number string boolean true false null undefined unknown symbol bigint object
never globalThis require process requireActual
""".split())

DECL_RE = re.compile(
    r"\bfunction\s+([A-Za-z_$][\w$]*)|\bclass\s+([A-Za-z_$][\w$]*)|"
    r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*[:=]|\binterface\s+([A-Za-z_$][\w$]*)|"
    r"\btype\s+([A-Za-z_$][\w$]*)")
CALL_RE = re.compile(r"(?<![A-Za-z0-9_$])\b([A-Za-z_$][\w$]*)\s*\(")


def _strip_comments(src: str) -> str:
    """用空格替换注释内容——保位置不移位，且注释内的 stubbing 惯用法不会被误识别。"""
    out = re.sub(r"//[^\n]*", " ", src)
    out = re.sub(r"/\*.*?\*/", " ", out, flags=re.S)
    return out


def _declared_names(src: str) -> set[str]:
    """文件内声明的标识符——它们是自有函数，不是「依赖」。"""
    clean = _strip_comments(src)
    names: set[str] = set()
    for m in DECL_RE.finditer(clean):
        for g in m.groups():
            if g:
                names.add(g)
    return names


def _called_symbols(src: str) -> set[str]:
    clean = _strip_comments(src)
    return {m.group(1) for m in CALL_RE.finditer(clean)}


def _stubbed_symbols(src: str) -> set[str]:
    """测试文件里被 stub 的符号集合（判据 ② 的左侧）。"""
    clean = _strip_comments(src)
    syms: set[str] = set()
    for p in _STUB_PATTERNS:
        for m in p.finditer(clean):
            syms.add(m.group(1))
    for m in _ALIAS_STUB_RE.finditer(clean):
        alias = m.group(1)
        rest = alias[1:]  # 去掉 m 前缀
        syms.add(rest[0].lower() + rest[1:] if rest else alias)
        syms.add(alias)
    return syms


def find_subject(test_path: Path, explicit: str | None = None) -> Path | None:
    """按 `<base>.test.ts → <base>.ts` 约定找被测源码；找不到返回 None。"""
    if explicit:
        p = Path(explicit)
        return p if p.is_file() else None
    name = test_path.name
    base = None
    for suf in TEST_SUFFIXES:
        if name.endswith(suf):
            base = name[: -len(suf)]
            break
    if base is None:
        base = test_path.stem
    for suf in SOURCE_SUFFIXES:
        c = test_path.with_name(base + suf)
        if c.is_file():
            return c
    idx = test_path.with_name(base + "/index.ts")
    if idx.is_file():
        return idx
    return None


def audit_mock_text(test_src: str, subject_src: str | None,
                    ack_reason: str | None = None) -> dict:
    """反同源静态检查。

    判据（对应 §质量标准「反同源假设」②）：被 stub 的符号 **MUST NOT** 是被测对象
    **直接调用**的那个依赖函数。命中 ⇒ 必须补一条走真实实现的对照用例。

    `subject_src is None` 时无法判定，返回 `skipped=True` 且不报违规——
    与家族的 MANUAL 约定一致：判不了必须显式可见，NEVER 静默计入通过。
    """
    stubbed = _stubbed_symbols(test_src)
    if subject_src is None:
        return {"file": None, "check": "mock", "violations": 0, "violationDetails": [],
                "acknowledged": [], "skipped": True,
                "skipReason": "未找到被测源码——反同源检查无法判定，须人工确认",
                "stats": {"stubbedSymbols": sorted(stubbed)}}

    declared = _declared_names(subject_src)
    direct_deps = {s for s in _called_symbols(subject_src)
                   if s not in declared and s not in JS_KEYWORDS}
    hits = sorted(stubbed & direct_deps)

    acknowledged = ack_reason if ack_reason else None
    if hits and not acknowledged:
        details = [{"type": "same-origin-mock", "symbol": h,
                    "detail": "「%s」既是测试 stub 的目标、又是被测对象直接调用的依赖——"
                              "夹具与被测实现同源，实现错了测试必绿；MUST 补一条走真实实现的对照用例" % h}
                   for h in hits]
        return {"file": None, "check": "mock", "violations": len(hits),
                "violationDetails": details, "acknowledged": [], "skipped": False,
                "stats": {"stubbedSymbols": sorted(stubbed),
                          "directDeps": len(direct_deps), "hits": len(hits)}}

    ack_list = ([{"type": "same-origin-mock", "symbol": h, "ackReason": acknowledged}
                 for h in hits] if hits else [])
    return {"file": None, "check": "mock", "violations": 0, "violationDetails": [],
            "acknowledged": ack_list, "skipped": False,
            "stats": {"stubbedSymbols": sorted(stubbed),
                      "directDeps": len(direct_deps), "hits": len(hits),
                      "acknowledged": len(ack_list)}}


def audit_mock(path: Path, src: str | None = None, ack_reason: str | None = None) -> dict:
    """校验单个测试文件（`mock --file` 入口）。"""
    test_src = path.read_bytes().decode("utf-8", errors="replace")
    subject = find_subject(path, src)
    reason = ack_reason
    if reason is None:
        m = ACK_RE.search(test_src)
        if m:
            reason = m.group(1).rstrip()
    subj_src = subject.read_bytes().decode("utf-8", errors="replace") if subject else None
    res = audit_mock_text(test_src, subj_src, reason)
    res["file"] = str(path)
    res["subject"] = str(subject) if subject else None
    return res


# ═══════════════════════ CLI ═══════════════════════

def _print(res: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return
    print("check: %s" % res.get("check"))
    print("file: %s" % res.get("file"))
    if res.get("subject") is not None:
        print("subject: %s" % res["subject"])
    print("stats: %s" % json.dumps(res.get("stats", {}), ensure_ascii=False))
    print("skipped: %s" % res.get("skipped", False), end="")
    if res.get("skipReason"):
        print("  ← %s" % res["skipReason"])
    else:
        print()
    print("violations: %d" % res.get("violations", 0))
    for d in res.get("violationDetails", []):
        print("  ✗ %s  %s" % (d.get("type", "?"), d.get("detail", "")))
        if d.get("symbol"):
            print("      符号: %s" % d["symbol"])
        if d.get("word"):
            print("      禁词: %s   |   %s" % (d["word"], d.get("line", "")))
        if d.get("head"):
            print("      验收点: %s" % d["head"])
    for d in res.get("acknowledged", []):
        print("  ⚠ %s  符号: %s" % (d.get("type", "?"), d.get("symbol")))
        print("      登记理由: %s" % d.get("ackReason", ""))


# ═══════════════════════ self-test ═══════════════════════

# 反同源实证夹具——取自 tri-stack-train M4a 真实文件的最小复现（shell-probe）
_M4A_SUBJECT = """\
import { existsSync } from 'node:fs'

function resolvePath(name: string): string | null {
  const full = name
  if (existsSync(full)) return full
  return null
}

async function probe(shell: string): Promise<boolean> {
  const p = resolvePath(shell)
  return p !== null
}

export { resolvePath, probe }
"""

# 实证形态：factory 里 stub existsSync，再用 mockExistsSync.mockReturnValue(false) 反复设假
_M4A_TEST_HIT = """\
import { existsSync } from 'node:fs'

vi.mock('node:fs', async () => {
  const actual = await vi.importActual('node:fs')
  return { ...actual, existsSync: vi.fn() }
})

const mockExistsSync = vi.mocked(existsSync)

describe('UT09（存在性检查分支）', () => {
  test('a', () => {
    mockExistsSync.mockReturnValue(false)
  })
  test('b', () => {
    mockExistsSync.mockReturnValue(false)
  })
})
"""

# 合规形态：stub 的被测对象根本不调用
_TEST_OK = """\
import { readText } from '../lib/safe-file'

vi.mock('../lib/safe-file', () => ({
  readText: vi.fn().mockResolvedValue('{}')
}))

const mockReadText = vi.mocked(readText)

test('cache miss', async () => {
  mockReadText.mockResolvedValue('{}')
})
"""

# 已登记技术理由的形态：命中但降为 acknowledged
_TEST_ACK = _M4A_TEST_HIT.replace(
    "describe('UT09（存在性检查分支）'",
    "// gate-lint: same-origin-ok existsSync 属进程原生 API，不可替换，对照用例见 test-report.md §降级证据\n"
    "describe('UT09（存在性检查分支）'")

# AC 合规形态
_AC_OK = """\
## 6. 验收标准（可验证）

- [ ] 终端面板可创建
      断言：`document.querySelector('.term-panel')` 非空且高度 >0
- [ ] 探测命令退出码正确
      断言：退出码 = 0，payload.shell === 'pwsh.exe'
"""

# AC 禁词形态——tri-stack-train M4b 实证：期望结果列直接写「本机冒烟通过」
_AC_FORBIDDEN = """\
## 6. 验收标准（可验证）

- [ ] 终端面板可创建
      期望结果：本机冒烟通过
- [ ] 会话切换正常
      期望结果：用户确认无异常
"""

# AC 缺断言形态
_AC_NO_ASSERT = """\
## 6. 验收标准（可验证）

- [ ] 终端面板可创建
- [ ] 会话切换正常
      期望结果：面板显示正常
"""

# 禁词只出现在说明性 blockquote——判据只约束验收点，故不算违规
_AC_BLOCKQUOTE_ONLY = """\
## 6. 验收标准（可验证）

> **禁词（硬红线）**：本节每条验收点 NEVER 出现「本机冒烟 / 用户冒烟 / 用户确认」等字样。

- [ ] 终端面板可创建
      断言：`document.querySelector('.term-panel')` 非空
"""


def _run_selftest() -> int:
    fails: list[str] = []

    def eq(a, b, msg: str) -> None:
        if a != b:
            fails.append("%s: 期望 %r，实际 %r" % (msg, b, a))

    # ---- ac ----
    eq(audit_ac_text(_AC_OK)["violations"], 0, "合规 AC 应零违规")
    eq(audit_ac_text(_AC_OK)["stats"]["acceptancePoints"], 2, "应识别 2 个验收点")

    r = audit_ac_text(_AC_FORBIDDEN)
    eq(r["violations"], 4, "两处禁词 + 两个验收点同时缺可观测断言 = 4 条违规")
    eq(r["stats"]["forbiddenHits"], 2, "两处禁词应各报一条")
    eq(r["stats"]["missingAssertion"], 2, "两个验收点均应报缺断言")
    eq(sorted(d["word"] for d in r["violationDetails"] if "word" in d),
       ["本机冒烟", "用户确认"], "禁词应原样回显")
    eq(sum(1 for d in r["violationDetails"] if d["type"] == "ac-forbidden-word"), 2,
       "ac-forbidden-word 应 2 条")
    eq(sum(1 for d in r["violationDetails"] if d["type"] == "ac-missing-assertion"), 2,
       "ac-missing-assertion 应 2 条")

    r2 = audit_ac_text(_AC_NO_ASSERT)
    eq(r2["violations"], 2, "两个验收点均缺可观测断言")
    eq(all(d["type"] == "ac-missing-assertion" for d in r2["violationDetails"]), True,
       "缺断言类型应为 ac-missing-assertion")

    r3 = audit_ac_text(_AC_BLOCKQUOTE_ONLY)
    eq(r3["violations"], 0, "禁词仅在说明性 blockquote 中不算违规（判据约束的是验收点）")

    eq(audit_ac_text("# 需求\n\n没有验收标准节。\n")["violations"], 1,
       "无验收标准节必须报 ac-missing-section")
    eq(audit_ac_text("# 需求\n\n没有验收标准节。\n")["violationDetails"][0]["type"],
       "ac-missing-section", "无节类型应为 ac-missing-section")

    # ---- mock ----
    eq(audit_mock_text("const x = 1", None)["skipped"], True, "无被测源码应 skipped")
    eq(audit_mock_text("const x = 1", None)["violations"], 0, "无法判定不报违规")

    eq(_stubbed_symbols(_M4A_TEST_HIT), {"existsSync"}, "M4a 夹具应识别出 stub 符号 existsSync")
    eq(_called_symbols(_M4A_SUBJECT) - _declared_names(_M4A_SUBJECT) - JS_KEYWORDS,
       {"existsSync"}, "被测源码的直接依赖应为 {existsSync}")

    r = audit_mock_text(_M4A_TEST_HIT, _M4A_SUBJECT)
    eq(r["violations"], 1, "M4a 实证形态必须被拦")
    eq(r["violationDetails"][0]["type"], "same-origin-mock", "违规类型应为 same-origin-mock")
    eq(r["violationDetails"][0]["symbol"], "existsSync", "违规符号应原样回显")
    # mutation：若交集逻辑被改成「空集」，上面这条必须变红
    eq(r["violations"] > 0, True, "mutation: 同源代码不得被判合规")

    r = audit_mock_text(_M4A_TEST_HIT, _M4A_SUBJECT, ack_reason="existsSync 不可替换，降级证据见 test-report.md")
    eq(r["violations"], 0, "登记技术理由后应降为 acknowledged")
    eq(len(r["acknowledged"]), 1, "acknowledged 应保留一条痕迹")
    eq(r["acknowledged"][0]["ackReason"].startswith("existsSync"), True,
       "acknowledged 应回显理由")

    eq(audit_mock_text(_TEST_OK, _M4A_SUBJECT)["violations"], 0,
       "stub 的被测对象不调用（readText）应合规")

    # 声明即自有函数，不应算依赖
    eq(audit_mock_text(_M4A_TEST_HIT, "function existsSync(p){return true}\nexport function probe(){existsSync('x')}\n")["violations"], 0,
       "被测源码自己声明的函数不算「依赖」")

    eq(_stubbed_symbols("const a = 1 // vi.mocked(fake)\n/* vi.fn() */"), set(),
       "注释内的 stubbing 惯用法不得被识别")
    eq(_called_symbols("probe() // existsSync('\"x'\")\n"), {"probe"},
       "注释内的调用不得被计入直接依赖")

    if fails:
        print("self-test FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print("self-test OK（ac 3 判据 · mock 反同源 + acknowledged 降级 · 注释剥离）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="tri-coding §质量标准 两条 prompt 层 MUST 的可执行载体（tt5 批）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("ac", help="§6 验收标准：禁词 + 可观测断言")
    p1.add_argument("--file", required=True)
    p1.add_argument("--json", action="store_true")

    p2 = sub.add_parser("mock", help="反同源假设静态检查：stub 目标 vs 被测对象直接调用依赖")
    p2.add_argument("--file", required=True)
    p2.add_argument("--src", help="被测源码路径（默认按 <base>.test.ts → <base>.ts 约定推导）")
    p2.add_argument("--ack-reason",
                    help="行内标记 gate-lint: same-origin-ok 未登记时，用此参数登记技术理由")
    p2.add_argument("--json", action="store_true")

    sub.add_parser("self-test", help="内置自检（含 M4a/M4b 实证夹具）")

    args = ap.parse_args()
    try:
        if args.cmd == "self-test":
            return _run_selftest()
        if args.cmd == "ac":
            res = audit_ac(Path(args.file))
        elif args.cmd == "mock":
            res = audit_mock(Path(args.file), src=args.src, ack_reason=args.ack_reason)
        else:
            ap.print_help()
            return 2
    except OSError as e:
        print("文件读取失败：%s" % e, file=sys.stderr)
        return 2

    _print(res, args.json)
    return 1 if res.get("violations") else 0


if __name__ == "__main__":
    sys.exit(main())
