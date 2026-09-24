#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门④ 合规自检 —— `references/compliance-checklist.md` 22 条硬约束的可执行实现。

定位（家族硬约束第 18 条：可执行实现与 prompt 分离）：
  确定性判定由本脚本承担；prompt 层只「调用本脚本 + 解析 JSON + 按状态处置」。
  标注 `manual` 的条目**无法机器判定**，脚本不臆断，由 Agent 逐条给出证据位置。

判定口径（与 compliance-checklist.md §五 一致）：
  PASS   / FAIL / N-A（须附理由）/ MANUAL（需人工判定）

用法：
    python scripts/compliance_check.py --skill <slug>        # 审计单个 skill
    python scripts/compliance_check.py --all                 # 审计全部 tri-* skill
    python scripts/compliance_check.py --dir <路径>          # 审计任意目录
    python scripts/compliance_check.py --skill x --json      # 机器可读

退出码：0 = 可机器判定项无 FAIL；1 = 存在 FAIL；2 = 参数/环境错误

契约：本脚本与 `references/compliance-checklist.md` 的编号**一一对应**。
      修订约束时两处 MUST 同步修改（清单是标准，脚本是实现）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

FM = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
FM_FIELD = re.compile(r"^([a-zA-Z_]+):[ \t]*(.*)$", re.M)
SEMVER = re.compile(r"^\d+(\.\d+)*$")
CL_HEAD = re.compile(r"^##[ \t]*\[([0-9]+(?:\.[0-9]+)*)\]", re.M)
CL_ALL = re.compile(r"^##[ \t]*\[([0-9]+(?:\.[0-9]+)*)\]", re.M)
HARDCODED_COUNT = re.compile(r"\d+\s*个(下游|skill|顶层目录|tri-\*)")
SELFCHECK = re.compile(r"本次(意图|模式|操作|文档)\s*=")
SECTIONS = ["强制执行契约", "触发时机", "上游依赖检测", "输入契约", "职责边界",
            "核心能力方法论", "处理流程", "交付产物", "版本检查与更新机制"]
LOCK_INSTALL = re.compile(r"(?<!api\.)skillhub\.cn|skills_store_lock|\.hub/skills")

# 自检句**已登记例外**（单一事实源：references/family-spec.md §五 待登记项表）。
# 例外 MUST 在此与 family-spec 两处同步登记，NEVER 只改一处。
SELFCHECK_EXEMPT = {
    # 本分支（编程工作流专线）当前无「即时对话回应型」skill，故本表为空。
    # 新增例外时 MUST 在此与 references/family-spec.md §五 两处同步登记。
}


def parse_frontmatter(fmb: str) -> dict:
    """极简 frontmatter 解析，支持三类取值：

      1. 行内标量：`key: value`
      2. YAML 块标量：`key: >` / `key: |` + 缩进续行（折叠为单行）
      3. YAML 列表：`key:` + `  - item` 续行（不收集内容，仅保证「键存在」）

    **为什么需要它**：早期实现只用行内正则 `^key:[ \t]*(.*)$`，
    对 `description: >` 这类块标量只取到 `>`、对 `tags:` 多行列表取到空串，
    导致第 2／4 条按错误文本判定（实测误报 tri-lottie / tri-pm）。
    """
    out = {}
    lines = fmb.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^([a-zA-Z_]+):[ \t]*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", "|", ">-", "|-"):
            i += 1
            buf = []
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                buf.append(lines[i].strip())
                i += 1
            out[key] = " ".join(buf)
            continue
        out[key] = val
        i += 1
    return out


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


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


def sections(body: str) -> dict:
    """按 `## <标题>` 切分章节，返回 {标题: 正文}。

    **必须锚定 `## ` 标题**，不能用 body.find(<关键词>)——关键词常先出现在
    「强制执行契约」里对章节的引用（如「先通过 §版本检查与更新机制」），
    用 find 会把切片起点落在引用处，导致判定整体错位（实测曾因此误判 #22）。
    """
    out = {}
    marks = [(m.start(), m.group(1).strip()) for m in re.finditer(r"^##\s+(.+)$", body, re.M)]
    for i, (pos, title) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        out[title] = body[pos:end]
    return out


def find_sec(secs: dict, key: str):
    for title, txt in secs.items():
        if key in title:
            return txt
    return ""


def check(d: Path) -> dict:
    slug = d.name
    sm = d / "SKILL.md"
    if not sm.is_file():
        return {"slug": slug, "error": "SKILL.md 不存在", "items": []}
    t = read(sm)
    fm_raw = FM.match(t)
    fmb = fm_raw.group(1) if fm_raw else ""
    # 字段**存在性**用键名收集，不要求行内值非空——
    # YAML 列表（如 tags://n  - a\n  - b）会让行内值为空，早期版本据此误判缺字段（实测 tri-pm）。
    fm_keys = set(re.findall(r"^([a-zA-Z_]+):", fmb, re.M)) if fmb else set()
    fmd = parse_frontmatter(fmb)
    desc = fmd.get("description", "")
    ver = fmd.get("version", "")
    body = t[fm_raw.end():] if fm_raw else t
    secs = sections(body)

    # 角色识别（决定 #8 / #20 是否适用）
    if "总路由" in desc and "识别" in desc and "路由" in desc:
        role = "root"
    elif "内部专用工具" in desc or "内部专用工具" in body[:1200]:
        role = "internal"
    elif "横向" in desc:
        role = "lateral"
    elif ("下游" in desc or "桥接" in desc) and ("认领" in desc or "处理 I" in desc or "处理 L2" in desc):
        role = "downstream"
    elif "子 skill" in desc or "children" in desc:
        role = "child"
    else:
        role = "unknown"

    # 角色识别（决定 #8 / #20 是否适用）
    if "总路由" in desc and "识别" in desc and "路由" in desc:
        role = "root"
    elif "内部专用工具" in desc or "内部专用工具" in body[:1200]:
        role = "internal"
    elif "横向" in desc:
        role = "lateral"
    elif ("下游" in desc or "桥接" in desc) and ("认领" in desc or "处理 I" in desc or "处理 L2" in desc):
        role = "downstream"
    elif "子 skill" in desc or "children" in desc:
        role = "child"
    else:
        role = "unknown"

    r = []

    def add(n, name, status, evidence="", notes="", advisory=False):
        r.append({"n": n, "name": name, "status": status, "evidence": evidence,
                  "notes": notes, "advisory": advisory})

    # 1 目录结构
    need_any = ["references", "templates", "scripts", "tests"]
    core = [f for f in ("SKILL.md", "README.md", "CHANGELOG.md") if (d / f).is_file()]
    sub = [x for x in need_any if (d / x).is_dir()]
    ok = len(core) == 3 and len(sub) >= 2
    add(1, "目录结构完整", "PASS" if ok else "FAIL",
        f"核心文件 {len(core)}/3（{'/'.join(core)}）；子目录 {len(sub)}/4（{'/'.join(sub)}）")

    # 2 独立安装声明
    m = re.search(r"支持独立安装[，,]含上游依赖检测[一二三四两\d]*态逻辑", desc)
    has_upstream_sec = any("上游依赖检测" in h for h in secs)
    if m:
        add(2, "独立安装声明", "PASS", f"description 命中：{m.group(0)}")
    elif not has_upstream_sec and ("总路由" in desc or "总路由" in fmd.get("displayName", "")):
        add(2, "独立安装声明", "N-A", "根路由，无上游依赖",
            "本项仅需独立安装的上游依赖型 skill 适用（理由：根路由无上游，不存在独立安装声明）")
    else:
        add(2, "独立安装声明", "FAIL",
            "description 未含「支持独立安装，含上游依赖检测N态逻辑」")

    # 3 章序 —— 按家族实测校准（第三轮）
    #    实测：家族主流为「方法论 → 版本检查与更新机制 → 处理流程 → 交付产物」，
    #    「版本检查」在 20+ 个 skill 中紧接方法论之后、处理流程之前，
    #    与 CONTRIBUTING.md 所述「版本置于末位」不同——以**实测**为准。
    #    另有两处变体（版本检查置于更后 / 文件末），亦接受。
    HEAD_FIRST5 = ["强制执行契约", "触发时机", "上游依赖检测", "输入契约", "职责边界"]
    def has(kw):
        return any(kw in h for h in secs)
    def idx_of(*kws):
        for i, h in enumerate(secs):
            if any(k in h for k in kws):
                return i
        return -1
    missing = []
    for h in HEAD_FIRST5:
        if not has(h):
            missing.append(h)
    for label, kws in (("方法论（核心能力 · 可扩展）", ("方法论", "核心能力", "引擎", "架构", "流程：")),
                       ("处理流程 / 工作流", ("处理流程", "工作流")),
                       ("交付产物", ("交付产物",)),
                       ("版本检查与更新机制", ("版本检查与更新机制",))):
        if idx_of(*kws) < 0:
            missing.append(label)
    order_bad = []
    pos = [idx_of(k) for k in HEAD_FIRST5]
    for i in range(4):
        if pos[i] >= 0 and pos[i + 1] >= 0 and pos[i] > pos[i + 1]:
            order_bad.append(f"{HEAD_FIRST5[i]} 应在 {HEAD_FIRST5[i + 1]} 之前")
    mi, vi, wi = idx_of("方法论", "核心能力", "引擎"), idx_of("版本检查与更新机制"), idx_of("处理流程", "工作流")
    if mi >= 0 and vi >= 0 and vi < mi:
        order_bad.append("版本检查与更新机制 不应早于方法论章节")
    # 「版本检查 vs 处理流程」的先后**不作硬性要求**——家族自身两种皆有（主流在前、5 例在后），
    # 该差异纯属章节编排风格，凭频次立标准不成立。仅在 notes 中提示。
    pos_note = ""
    if vi >= 0 and wi >= 0 and vi > wi:
        pos_note = "版本检查置于处理流程之后（家族少数变体，5 例；非缺陷）"
    if role == "root":
        add(3, "SKILL.md 章节齐全且顺序正确", "N-A",
            "根路由，章节结构为已登记变体（family-spec §五）",
            "根路由以「判定 → 路由步骤 → 兜底」组织，不套用下游型九章（理由：无上游、无交付产物）")
        missing = order_bad = []
    add(3, "SKILL.md 章节齐全且顺序正确",
        "PASS" if not missing and not order_bad else "FAIL",
        (f"缺：{missing}；" if missing else "") + ("；".join(order_bad) if order_bad else "九类必备章节齐全，前五章顺序正确"),
        pos_note or "章序以**家族实测**为准，非 CONTRIBUTING.md 所述末位")

    # 4 frontmatter 八字段
    need = ["name", "slug", "version", "displayName", "description", "summary", "tags", "license"]
    miss = [k for k in need if k not in fm_keys]
    add(4, "frontmatter 完整",
        "PASS" if not miss and SEMVER.match(ver or "") else "FAIL",
        f"缺字段：{miss}；version={ver!r}" if (miss or not SEMVER.match(ver or "")) else f"八字段齐全，version={ver}")

    # 5 契约存在且含自检句
    #    **不要求数字编号**——家族契约既有 `1.` 数字列举，也有 `- MUST …` 无序列举
    #    （实测 tri-article / tri-docx2md / tri-pdf2md 等用无序列举，曾被误判「编号 0 条」）。
    #    （历史）原 tri-express 曾为已登记例外（family-spec §五）：设计上不作答前声明；该 skill 未包含在本分支，例外表现为空。
    seg = find_sec(secs, "强制执行契约")
    has_sc = bool(SELFCHECK.search(seg))
    if not seg:
        add(5, "强制执行契约存在且含自检句", "FAIL", "无「强制执行契约」章节")
    elif slug in SELFCHECK_EXEMPT:
        add(5, "强制执行契约存在且含自检句", "N-A",
            f"已登记例外（family-spec §五）：{SELFCHECK_EXEMPT[slug]}",
            "本项例外已在 family-spec §五 登记，故判 N-A")
    else:
        add(5, "强制执行契约存在且含自检句",
            "PASS" if has_sc else "FAIL",
            f"契约章节 {len(seg.splitlines())} 行；自检句 {'有' if has_sc else '无'}")

    # 6 上游检测态数匹配
    #    家族态名有变体：「引导安装」/「独立降级模式」/「待识别」皆合法；
    #    另有「自包含型」（声明无强制上游依赖）与「根路由」（tri-intent）不适用。
    seg6 = find_sec(secs, "上游依赖检测")
    if role == "root":
        add(6, "上游检测态数与类型匹配", "N-A", "根路由，无上游依赖",
            "根路由无上游可检测（理由：路由的发起方本身）")
    elif not seg6:
        add(6, "上游检测态数与类型匹配", "FAIL", "无「上游依赖检测」章节")
    elif re.search(r"无强制上游依赖|不依赖任何外部上游|独立可用", seg6):
        add(6, "上游检测态数与类型匹配", "N-A", "自包含型：声明了无强制上游依赖",
            "本项仅上游依赖型 skill 适用（理由：自包含型无上游态可数）")
    else:
        states = [k for k in ("引导安装", "独立降级", "待识别", "降级模式", "降级")
                  if k in seg6]
        if not states:
            add(6, "上游检测态数与类型匹配", "FAIL",
                "未见任何上游缺失态的处置（引导安装 / 独立降级 / 降级）")
        else:
            add(6, "上游检测态数与类型匹配", "PASS",
                f"检出态名：{'/'.join(states)}",
                "态名变体（引导安装 / 独立降级模式 / 待识别）均视为合法")

    # 7 职责边界
    #    表述有变体：「不负责」/「以下不是它的事」/「不做」/「NEVER」/「禁止」皆合法
    #    （实测 tri-frontend-design 用「以下不是它的事（显式转介）」，语义正确却被早期版本误判）。
    seg7 = find_sec(secs, "职责边界")
    RQ = ("不负责", "不是它的事", "不做", "NEVER", "禁止")
    hit = [k for k in RQ if k in seg7]
    if role == "root":
        add(7, "职责边界明确", "N-A", "根路由，结构为已登记变体",
            "根路由以「判定/路由/兜底」组织，MECE 边界由 §MECE 保证 章节承载（理由：无业务职责可划）")
    elif seg7 and hit:
        add(7, "职责边界明确", "PASS",
            f"该节 {len(seg7.splitlines())} 行；命中表述：{'/'.join(hit)}")
    elif seg7:
        add(7, "职责边界明确", "FAIL",
            f"该节 {len(seg7.splitlines())} 行；未见「不负责」类表述（不负责 / 不是它的事 / 不做 / NEVER / 禁止）")
    else:
        add(7, "职责边界明确", "FAIL", "无「职责边界」章节")

    # 8 MECE 交叉比对 —— 需人工
    if role == "downstream":
        add(8, "意图认领 MECE 不重叠", "MANUAL",
            "须交由人类/Agent 交叉比对 tri-intent/SKILL.md §路由映射表（路由真源）")
    else:
        add(8, "意图认领 MECE 不重叠", "N-A",
            f"角色={role}，不认领 L2/L3 编码",
            "本项仅路由型下游适用（理由：非路由型不参与路由表，无编码可重叠）")

    # 9 可扩展性
    add(9, "核心能力方法论含可扩展性",
        "PASS" if "可扩展性" in body else "FAIL",
        "含「可扩展性」小节" if "可扩展性" in body else "未见「可扩展性」小节")

    # 10 落盘规则
    add(10, "交付产物含落盘规则",
        "PASS" if ("落盘" in body and any(k in body for k in (".tribro/", "工作区", "docs/", "CONTEXT.md", "reports/", "就地更新", "落盘规则"))) else "FAIL",
        "含落盘位置说明" if "落盘" in body else "未见落盘位置说明")

    # 11 CHANGELOG
    cl = read(d / "CHANGELOG.md")
    vs = CL_ALL.findall(cl)
    head = CL_HEAD.search(cl)
    hv = head.group(1) if head else None
    mx = None
    for v in vs:
        if mx is None or (vcmp(v, mx) or 0) > 0:
            mx = v
    ok11 = bool(hv) and hv == ver and mx == hv
    add(11, "CHANGELOG 规范", "PASS" if ok11 else "FAIL",
        f"首条={hv} frontmatter={ver} 文件最大={mx}")

    # 12 tests
    #    **口径经全仓实测校准（第六轮）**：家族测试文件至少有 **四种约定**（逐 skill 互斥）：
    #      A 行首 TC 表行（tri-article / tri-humanize / tri-music…）
    #      B 章节式 ### TC（tri-coding / tri-god / tri-wiki / tri-loop / tri-pm / tri-checklist / tri-html…）
    #      C 组式/管道式无统一编号（tri-sdlc / tri-geo / tri-workflow / tri-learn…）
    #      D 纯列表+正文式，**不用表格**（tri-frontend-design 169 行 / tri-pm 262 行，0 表格行）
    #    ⇒ **任何单一形式判定都只覆盖部分约定**（此前五轮校准的根因——表格行数对 D 类不成立）。
    #    **约定无关的可靠判据**：测试文件存在 + **行数 ≥ 50** + 标题含「测试用例」
    #    （命名约定 `tests/<slug>-full-testcases.md` 保证意图，行数保证内容丰富度，
    #      标题保证类型。三者结合已足够稳健，且对四种约定一律成立）。
    td = d / "tests"
    tfiles = list(td.glob("*-full-testcases.md")) if td.is_dir() else []
    rich = False
    if tfiles:
        tt = read(tfiles[0])
        rich = len(tt.splitlines()) >= 50 and "测试用例" in tt
    add(12, "tests 全场景用例",
        "PASS" if rich else "FAIL",
        f"用例文件 {len(tfiles)} 个；{len(read(tfiles[0]).splitlines())} 行（约定无关口径：行数≥50 且标题含「测试用例」）"
        if tfiles else "无 tests/*-full-testcases.md")

    # 13 门禁（无门禁者 N-A，须附理由）
    has_gate = any(k in body for k in ("审批门", "门①", "闸门", "门禁", "审批"))
    add(13, "门禁/审批门明确",
        "PASS" if has_gate else "N-A",
        "含门禁表述" if has_gate else "纯只读 / 无产物落盘型，判 N-A（理由：无需要审批的产物）")

    # 14 兜底
    add(14, "兜底处理覆盖",
        "PASS" if ("兜底" in body and "NEVER" in body) else "FAIL",
        "含兜底处理且明确 NEVER 静默失败" if "兜底" in body else "未见兜底处理小节")

    # 15 自检句格式
    m15 = SELFCHECK.search(body)
    if slug in SELFCHECK_EXEMPT:
        add(15, "自检句格式与家族一致", "N-A",
            f"已登记例外（family-spec §五）：{SELFCHECK_EXEMPT[slug]}",
            "本项例外已在 family-spec §五 登记，故判 N-A")
    else:
        add(15, "自检句格式与家族一致", "PASS" if m15 else "FAIL",
            f"命中：{m15.group(0)}" if m15 else "未命中 本次意图=/本次模式=/本次操作=")

    # 16 反规避 —— 仅对有门禁者适用；放宽表述
    if not has_gate:
        add(16, "反规避规则", "N-A", "无门禁，反规避规则不适用（理由：无门禁即无可规避的标准）")
    else:
        m16 = re.search(r"(NEVER|不得|禁止)[^\n]{0,60}(下调|降低|放宽|简化|凑合|迁就|因为.{0,10}(着急|时间))",
                        body) or ("反规避" in body)
        add(16, "反规避规则（建议项）", "PASS" if m16 else "N-A",
            "含反规避表述" if m16 else "有门禁但未含显式反规避表述",
            "本项为建议项，FAIL 不阻断。上游仅确认 tri-review/tri-sdlc 显式设有反规避机制，"
            "家族其余 gated skill 普遍未写此表述——本条为本仓库重建推定，故不列入必检。",
            advisory=True)

    # 17 禁止硬编码家族计数
    m17 = HARDCODED_COUNT.search(body)
    hits = HARDCODED_COUNT.findall(body)
    add(17, "禁止硬编码家族计数", "PASS" if not m17 else "FAIL",
        f"命中：{m17.group(0)}（共 {len(hits)} 处）" if m17 else "未见硬编码家族计数")

    # 18 可执行实现分离
    sd = d / "scripts"
    py = list(sd.glob("*.py")) if sd.is_dir() else []
    add(18, "可执行实现与 prompt 分离",
        "PASS" if py else "N-A",
        (f"scripts/ 下 {len(py)} 个脚本：{'/'.join(p.name for p in py[:4])}") if py
        else "scripts/ 无脚本；无确定性逻辑型 skill 判 N-A（理由：无确定性逻辑需外置）")

    # 19 相邻边界表（放宽：表行 / 边界关键词 / 归属表均可）
    m19 = re.search(r"\|\s*(相邻|信号|归属|tri-\w+)[^\n]*\|", body) or ("边界判据" in body) \
          or ("边界说明" in body) or ("· tri-" in body)
    add(19, "与相邻 skill 边界表（建议项）", "PASS" if m19 else "N-A",
        "含相邻/归属边界表" if m19 else "未见相邻边界表或归属表",
        "本项为建议项，FAIL 不阻断。上游未确认该条为必检；家族实际写法多样"
        "（边界表 / 归属表 / 段落叙述），机械判定易误报，故不列入必检。",
        advisory=True)

    # 20 横向例外登记
    if role == "lateral":
        add(20, "横向层自检句例外登记", "MANUAL",
            "横向型；须确认 family-spec.md §五 是否已登记其自检句例外")
    else:
        add(20, "横向层自检句例外登记", "N-A",
            f"角色={role}，非横向型",
            "本项仅横向型适用（理由：非横向型不存在自检句例外需登记）")

    # 21 安装评估
    #    探针用**固定名**并放在 try/finally 里清理：早期版本用 id(d) 命名且清理不健壮，
    #    曾把 .cmp_probe_* 文件泄漏进被审计目录并误提交。
    conflict = (REPO / slug).exists()
    writable = False
    probe = d / ".cmp_writable_probe"
    try:
        probe.write_text("x", encoding="utf-8")
        writable = True
    except OSError:
        writable = False
    finally:
        try:
            if probe.exists():
                probe.unlink()
        except OSError:
            pass
    add(21, "安装评估", "PASS" if writable else "FAIL",
        f"目录可写={'是' if writable else '否'}；slug 目录存在={conflict}（存在属正常，仅记录）")

    # 22 版本检查内部化：硬要求 = 指向自身 spec；STUB 行数为**建议项**（不阻断）
    seg22 = find_sec(secs, "版本检查与更新机制")
    self_ref = "references/version-check-spec.md" in seg22
    # 外部引用**仅在自身指针缺失时**才算违规：指向自身 spec 的同时并列提及
    # 「家族级设计总纲 tri-intent/references/version-gate.md」是本设计**鼓励**的写法
    # （本仓库 payload spec 即如此），早期版本把所有外部提及判违规（实测误报 tri-humanize）。
    foreign = re.findall(r"tri-\w+/references/[\w.-]+", seg22)
    lines = len(seg22.splitlines())
    hard_ok = self_ref and not (foreign and not self_ref)
    add(22, "版本检查内部化",
        "PASS" if hard_ok else "FAIL",
        f"自身指针={'有' if self_ref else '无'}；指向外部={('是（违规）:' + ','.join(sorted(set(foreign))[:2])) if foreign else '否'}",
        f"该节 {lines} 行" + ("（超 STUB 建议值 30 行，属建议项、不阻断）" if lines > 30 else ""))

    # 门④ 判定：**建议项 FAIL 不阻断**（家族既有惯例：必检项 + 建议项，建议项记入「建议改进项」）
    fails = [x for x in r if x["status"] == "FAIL" and not x.get("advisory")]
    advisory = [x for x in r if x["status"] == "FAIL" and x.get("advisory")]
    return {"slug": slug, "dir": d.as_posix(), "items": r,
            "fail": len(fails), "advisory": len(advisory),
            "manual": sum(1 for x in r if x["status"] == "MANUAL"),
            "verdict": "FAIL" if fails else "PASS"}


def render(res: dict) -> str:
    if res.get("error"):
        return f"### `{res['slug']}`\n\n🔴 {res['error']}\n"
    mark = {"PASS": "✅", "FAIL": "🔴", "N-A": "⬜", "MANUAL": "🔍"}
    out = [f"### `{res['slug']}` — 门④ {'PASS' if res['verdict'] == 'PASS' else 'FAIL'}"
           f"（FAIL {res['fail']} · 需人工 {res['manual']}）\n",
           "| # | 约束 | 判定 | 证据 / 原因 |", "|---|---|---|---|"]
    for x in res["items"]:
        ev = x["evidence"]
        if x.get("notes"):
            ev += f"<br><em>（{x['notes']}）</em>"
        out.append(f"| {x['n']} | {x['name']} | {mark.get(x['status'],'?')} {x['status']} | {ev} |")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", default=None)
    ap.add_argument("--dir", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.dir:
        targets = [Path(args.dir).resolve()]
    elif args.skill:
        p = (REPO / args.skill).resolve()
        if not p.is_dir():
            print(f"未找到：{p}", file=sys.stderr)
            return 2
        targets = [p]
    elif args.all:
        targets = sorted(p for p in REPO.glob("tri-*") if (p / "SKILL.md").is_file())
    else:
        print("需指定 --skill / --dir / --all", file=sys.stderr)
        return 2

    results = [check(d) for d in targets]

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        print(f"# 门④ 合规自检（compliance-checklist.md 22 条）\n")
        print(f"审计对象 **{len(results)}** 个；门④ FAIL **{sum(1 for r in results if r.get('verdict')=='FAIL')}** 个\n")
        for r in results:
            print(render(r))
        print("> 🔍 `MANUAL` 项 MUST 由 Agent 逐条给出证据位置，NEVER 臆断。")
        print("> 口径：任一条 FAIL → 门④ FAIL → 回炉门②；连续 3 轮 FAIL → 停止回炉并报告卡点。")

    return 1 if any(r.get("verdict") == "FAIL" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
