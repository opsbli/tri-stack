#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门② 前置三重校验 —— tri-req-audit 的可执行实现。

定位（家族硬约束第 18 条：可执行实现与 prompt 分离）：
  确定性判定（章节齐备性 / 占位符残留 / 出处标记 / 验收标准可判定性形态 / 待补充项定级）
  由本脚本承担；prompt 层只「调用本脚本 + 解析 JSON + 按 result 归类」。
  **语义判断**（如「这条断言是否真的可判」「这条规则是否真的矛盾」）**不由本脚本臆断**，
  由 Agent 复核并给出证据位置。

判据真源：`references/audit-dimensions.md`（§一 结构基线 / §二 八维 / §三 三重校验 / §四 分级）。

用法：
    python scripts/audit_precheck.py --file <.tribro/coding/<命名>/requirements.md> --json
    python scripts/audit_precheck.py --dir <项目根> --json      # 自动探测 requirements.md
    python scripts/audit_precheck.py --file <...>               # 人类可读

退出码：0 = 无 P0；1 = 存在 P0（判定「阻断开工」）；2 = 参数 / 环境错误
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 结构基线（唯一真源：references/audit-dimensions.md §一）
STRUCT = [
    ("一", "项目概述", ["项目名称", "项目背景", "目标用户", "核心价值"]),
    ("二", "功能需求", ["功能名称", "出处", "验收标准"]),
    ("三", "页面清单与交互规则", ["页面名称", "路由", "组件列表", "交互规则"]),
    ("四", "业务规则", ["规则描述", "出处"]),
    ("五", "非功能需求", ["性能", "安全", "兼容性"]),
    ("六", "技术约束", ["前端框架", "后端", "数据库", "部署环境"]),
    ("七", "数据需求", ["字段", "来源"]),
    ("八", "验收标准", ["功能", "验收标准", "判定方式"]),
    ("九", "待补充项", ["缺失信息", "建议补充方式", "影响"]),
]

PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")
H2 = re.compile(r"^##\s+(.+?)\s*$", re.M)
TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$", re.M)

# 不可判定信号（形容词 / 程度词，无客观通过条件）
UNTESTABLE = ["友好", "良好", "流畅", "合理", "快速", "美观", "易用", "稳定",
              "高效", "灵活", "完善", "舒适", "优秀", "较强", "较好"]
# 可观测信号（动词 / 阈值，存在即可判定）
OBSERVABLE = ["显示", "跳转", "返回", "写入", "保存", "拦截", "提示", "报错", "抛出",
              "可见", "不可见", "置灰", "禁用", "启用", "等于", "大于", "小于",
              "不超过", "不少于", "至少", "最多", "成功", "失败", "秒", "毫秒",
              "ms", "%", "条", "次", "字段", "接口", "状态"]
# 出处标记形态：`PRD:<章节号>` / `原型:<页面名>`（见 audit-dimensions.md §二 D8）
SOURCE_MARK = ("PRD", "原型", "prd")


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def cells(row: str) -> list:
    """拆一行 Markdown 表格的单元格。

    **为什么不 strip('|')**：`TABLE_ROW` 已用 `\\|(.+)\\|` 吃掉**外层**分隔管道，
    遗留的 group(1) 里首尾管道属**单元格边界**。再 strip('|') 会把末尾**空单元格**
    一并吃掉（`| a | b |  |` → 3 格而非 4 格），实测曾因此漏检「影响列为空」（mutation 逃逸）。
    """
    return [c.strip() for c in row.strip().split("|")]


def is_sep(row: str) -> bool:
    return bool(re.fullmatch(r"[\s|:\-]+", row.strip()))


def col_index(header: list, *names: str) -> int:
    """按表头名定位列号（表头驱动，替代 `c[-2]` 这类硬编码下标）。"""
    for i, h in enumerate(header):
        if any(n in h for n in names):
            return i
    return -1


def split_sections(text: str) -> dict:
    """按 `## ` 标题切片，返回 {标题: 正文}。"""
    out = {}
    marks = [(m.start(), m.group(1).strip()) for m in H2.finditer(text)]
    for i, (pos, title) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        out[title] = text[pos:end]
    return out


def find_sec(secs: dict, key: str) -> str:
    for t, t2 in secs.items():
        if key in t:
            return t2
    return ""


def table(seg: str):
    """返回 (表头单元格列表, [数据行单元格列表])；无表返回 ([], [])。"""
    rows = [r for r in TABLE_ROW.findall(seg) if not is_sep(r)]
    if not rows:
        return [], []
    return cells(rows[0]), [cells(r) for r in rows[1:]]


def check(text: str) -> dict:
    secs = split_sections(text)
    items = []

    def add(dim, level, title, evidence, suggestion=""):
        items.append({"dim": dim, "level": level, "title": title,
                      "evidence": evidence, "suggestion": suggestion})

    # ---- 结构识别：是否 tri-prototype 的九章形态 ----
    hit_ch = []
    for num, name, _ in STRUCT:
        if any((num + "、") in t and name in t for t in secs):
            hit_ch.append(name)
    standard = len(hit_ch) >= 7
    structure = {"standard": standard, "present": hit_ch,
                 "missing": [n for _, n, _ in STRUCT if n not in hit_ch]}
    if not standard:
        structure["note"] = "非九章形态；D1 判 N-A（附理由），其余维度照常"

    # ---- D1 章节与字段 ----
    for num, name, fields in STRUCT:
        if name in structure["missing"]:
            if standard:
                add("D1", "P0", f"整章缺失：{name}",
                    f"未命中 `## {name}` 标题", "回炉 tri-prototype 补齐该章")
            continue
        seg = find_sec(secs, name)
        for f in fields:
            if f not in seg:
                add("D1", "P1", f"{name} 缺字段「{f}」",
                    f"`{name}` 章节内未见「{f}」", "按模板补该列 / 该行")
        head, body = table(seg)
        if head and not body:
            add("D1", "P0", f"{name} 表体为空",
                "仅见表头，无数据行", "回炉补数据行")

    # ---- 占位符残留 ----
    ph = PLACEHOLDER.findall(text)
    if ph:
        add("D1", "P0", f"模板占位符未替换（{len(ph)} 处）",
            "、".join(sorted(set(ph))[:6]), "替换或删除全部 {{...}} 占位")

    # ---- D8 证据溯源：出处列 ----
    no_src = []
    for name, colnames in (("功能需求", ("出处",)), ("业务规则", ("出处",)),
                           ("数据需求", ("来源",))):
        seg = find_sec(secs, name)
        if not seg:
            continue
        head, body = table(seg)
        idx = col_index(head, *colnames)
        if idx < 0:
            continue
        for i, c in enumerate(body, start=2):
            if idx >= len(c):
                continue
            cell = c[idx]
            if not cell or not any(m in cell for m in SOURCE_MARK):
                label = c[1][:28] if len(c) > 1 else (c[0][:28] if c else "?")
                no_src.append(f"{name} 表第 {i} 行：{label}")
    if no_src:
        add("D8", "P0", f"条目缺出处（{len(no_src)} 条）",
            "；".join(no_src[:6]), "回炉补 `PRD:<章节号>` / `原型:<页面名>` 出处")

    # ---- 冲突项标注 ----
    #   扫描范围**限定在规则/功能/页面三章**：解析元数据的「冲突项数量｜0」等统计字段
    #   会引入假阳性（实测首版在完全无冲突的文档上误报 P1），故不纳入扫描。
    scan = "".join(find_sec(secs, k) for k in ("业务规则", "功能需求", "页面清单与交互规则"))
    if "冲突" in scan and "PRD 优先" not in text and "PRD优先" not in text:
        add("D8", "P1", "提到冲突但未标注「PRD 优先」",
            "业务规则/功能需求/页面章节含「冲突」字样，但全文未见「PRD 优先」标注",
            "按 tri-prototype §PRD 优先铁律补标注")

    # ---- D3 可测性（表头驱动定位「验收标准」列） ----
    bad_acc = []
    for name in ("功能需求", "验收标准"):
        seg = find_sec(secs, name)
        if not seg:
            continue
        head, body = table(seg)
        idx = col_index(head, "验收标准")
        if idx < 0:
            continue
        for i, c in enumerate(body, start=2):
            if idx >= len(c):
                continue
            cand = c[idx]
            if len(cand) < 4:
                continue
            if any(w in cand for w in UNTESTABLE) and not any(w in cand for w in OBSERVABLE):
                bad_acc.append(f"{name} 表第 {i} 行：{cand[:28]}")
    if bad_acc:
        add("D3", "P0", f"验收标准不可判定（{len(bad_acc)} 条）",
            "；".join(bad_acc[:6]), "改写为可观测条件（界面元素 / 数据 / 接口返回 + 阈值）")

    # ---- 门② 可消费性 ③：待补充项定级（影响列非空） ----
    seg9 = find_sec(secs, "待补充项")
    if seg9:
        head, body = table(seg9)
        idx = col_index(head, "影响")
        if idx >= 0:
            for i, c in enumerate(body, start=2):
                if idx >= len(c):
                    continue
                if not c[idx]:
                    add("D1", "P1", f"待补充项第 {i} 行未说明影响",
                        "「影响」列为空", "补「影响」列（是否阻塞门②）")

    # ---- 兜底：全维通过时要留结论 ----
    if not items:
        add("D1", "INFO", "八维预检未发现机器可判缺陷",
            "结构 / 溯源 / 可测性形态 / 待补充项定级均通过", "语义维（D2/D4/D5/D6）仍须 Agent 人工复核")

    counts = {lv: sum(1 for x in items if x["level"] == lv) for lv in ("P0", "P1", "P2")}
    verdict = "blocked" if counts["P0"] else ("conditional" if counts["P1"] else "ok")
    return {"structure": structure, "items": items, "counts": counts, "verdict": verdict}


def locate(root: Path):
    cand = sorted(root.glob(".tribro/coding/*/requirements.md"))
    return cand[-1] if cand else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=None)
    ap.add_argument("--dir", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.file:
        target = Path(a.file)
    elif a.dir:
        target = locate(Path(a.dir))
        if target is None:
            print("未在 .tribro/coding/*/ 下探测到 requirements.md", file=sys.stderr)
            return 2
    else:
        print("需指定 --file 或 --dir", file=sys.stderr)
        return 2

    if not target.is_file():
        print(f"文件不存在：{target}", file=sys.stderr)
        return 2

    res = check(read(target))
    res["file"] = target.as_posix()
    res["structure_mode"] = "standard" if res["structure"]["standard"] else "non-standard"

    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"# 前置三重校验 · {res['file']}\n")
        print(f"结构形态：**{res['structure_mode']}**；判定：**{res['verdict']}**"
              f"（P0 {res['counts']['P0']} / P1 {res['counts']['P1']}）\n")
        print("| 维度 | 级别 | 问题 | 证据 |")
        print("|---|---|---|---|")
        for x in res["items"]:
            print(f"| {x['dim']} | {x['level']} | {x['title']} | {x['evidence']} |")
        print("\n> 语义维（D2 无歧义 / D4 边界 / D5 状态 / D6 权限）MUST 由 Agent 逐条复核，本脚本不臆断。")

    return 1 if res["counts"]["P0"] else 0


if __name__ == "__main__":
    sys.exit(main())
