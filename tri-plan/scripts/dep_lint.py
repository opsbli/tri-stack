#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-plan 依赖图无环校验（确定性算法下沉，见 family-spec 约束 18）

用途
----
解析 plan.md §6.1「依赖关系列表」表格，对任务依赖图做拓扑排序，检出三类缺陷：

  SELF_LOOP  任务依赖了自己（a -> a）
  CYCLE      依赖成环（输出一条完整环路径）
  DANGLING   引用了不在任务清单里的任务编号

用法
----
    python scripts/dep_lint.py <plan.md>            # 人类可读报告
    python scripts/dep_lint.py <plan.md> --json     # 结构化输出，供编排读取

退出码
------
    0  PASS 无环、无自环、无悬引用
    1  FAIL 检出任一缺陷，须重构拆解后重跑
    2  用法错误或文件不可读

依赖类型（→ FS / ⇒ SS / ⇐ FF / ⇢ 外部）在本脚本中一律按「前置必须先于后继」处理：
四类标记都表达“前序不达成，本任务无法推进”的约束，方向一致，故统一建边。
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict, deque

NO_PRE = {"", "-", "—", "–", "无", "none", "None", "/", "N/A"}
# 前置任务单元格里可能出现的分隔符
SPLIT = re.compile(r"[,，、;；/]| 和 | & ")


def _table_at(lines, start):
    """从 start 起连续取表格行，遇到非表格行即止。"""
    out = []
    for raw in lines[start:]:
        s = raw.strip()
        if not s.startswith("|"):
            break
        out.append(s)
    return out


def table_rows(text: str):
    """取表头同时含「任务编号」与「前置」的那张表（§6.1）的数据行。

    plan.md 里还有 SMART / 约束 / 任务清单 / 里程碑 / 风险等表格，
    全量扫会把占位符（<任务描述>、R1、M1）当成任务编号。
    """
    lines = text.splitlines()
    for i, raw in enumerate(lines):
        s = raw.strip()
        if s.startswith("|") and "任务编号" in s and "前置" in s:
            return _table_at(lines, i + 1)
    return []


def all_task_ids(text: str):
    """收集全文所有以「任务编号」为第一列的表格的第一列（§五 任务清单 + §6.1）。

    任务全集以 §五 任务清单为准；§6.1 只列有依赖的任务，两者取并集。
    """
    ids = []
    lines = text.splitlines()
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or cells[0] != "任务编号":
            continue
        for row in _table_at(lines, i + 1):
            cells = [c.strip() for c in row.strip("|").split("|")]
            if not cells or all(set(c) <= set("-: ") for c in cells):
                continue
            if cells[0]:
                ids.append(cells[0])
    return list(dict.fromkeys(ids))


def parse_deps(text: str):
    """从 plan.md 里抠出 §6.1 依赖关系列表，返回 (nodes, edges, rows)。

    表头形如：| 任务编号 | 前置任务 | 依赖类型 | 标记 | 说明 |
    前置单元格支持 `—`/`无` 表示无前置，多个前置用逗号或顿号分隔。
    """
    nodes, edges, rows = [], [], []
    for raw in table_rows(text):
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        head = cells[0]
        # 跳过纯分隔行
        if all(set(c) <= set("-: ") for c in cells):
            continue
        tid, pre = head, cells[1]
        nodes.append(tid)
        rows.append((tid, pre))
        if pre in NO_PRE:
            continue
        for p in SPLIT.split(pre):
            p = p.strip().strip("`")
            if not p or p in NO_PRE:
                continue
            # 去掉依附在前置编号上的依赖类型字眼，如 "1.1.1 →"
            p = re.split(r"[\s>]", p)[0].strip()
            if p:
                edges.append((p, tid))
    # 去重保序
    # 任务全集 = §五 任务清单 ∪ §6.1 第一列
    nodes = list(dict.fromkeys(list(nodes) + all_task_ids(text)))
    edges = list(dict.fromkeys(edges))
    return nodes, edges, rows


def find_cycles(adj, candidates):
    """在残留节点集合里 DFS，返回至多 3 条环路径。"""
    cand = set(candidates)
    out, seen, stack = [], set(), []

    def dfs(u):
        stack.append(u)
        seen.add(u)
        for v in adj.get(u, []):
            if v not in cand:
                continue
            if v in stack:
                out.append(stack[stack.index(v):] + [v])
            elif v not in seen:
                dfs(v)
        stack.pop()

    for n in sorted(cand):
        if n not in seen:
            dfs(n)
    return out[:3]


def lint(nodes, edges):
    known = set(nodes)
    self_loop, inner, bad_ref = [], [], defaultdict(list)
    for a, b in edges:
        if a == b:
            self_loop.append(b)
            continue
        if a in known and b in known:
            inner.append((a, b))
        else:
            if a not in known:
                bad_ref[b].append(a)  # b 依赖了不存在的 a
            if b not in known:
                bad_ref[a].append(b)

    # 悬引用的任务不参与排期，避免被当成“零依赖”混进可执行序列；
    # 自环任务留在图里（否则环路径会被切断），但永不入队
    self_loop_set = set(self_loop)
    sched = [n for n in nodes if n not in bad_ref]
    sched_set = set(sched)
    indeg = {n: 0 for n in nodes}
    adj = defaultdict(list)
    for a, b in inner:
        adj[a].append(b)
        indeg[b] = indeg.get(b, 0) + 1
    q = deque(sorted([n for n in sched
                      if indeg[n] == 0 and n not in self_loop_set]))
    order = []
    while q:
        n = q.popleft()
        order.append(n)
        for m in sorted(adj[n]):
            indeg[m] -= 1
            if (indeg[m] == 0 and m in sched_set
                    and m not in self_loop_set):
                q.append(m)
    left = [n for n in sched if n not in order]
    cycles = find_cycles(adj, left) if left else []
    in_cycle = set()
    for c in cycles:
        in_cycle.update(c)

    self_loop = sorted(set(self_loop))
    dangling = sorted(set(bad_ref) | (set(left) - in_cycle))
    return {
        "tasks": len(nodes),
        "edges": len(edges),
        "order": order,
        "self_loop": self_loop,
        "cycle_nodes": sorted(in_cycle),
        "cycles": [c for c in cycles],
        "dangling": dangling,
        "bad_ref": {k: sorted(set(v)) for k, v in bad_ref.items()},
        "pass": not left and not bad_ref and not self_loop,
    }


def render(r: dict) -> str:
    lines = [
        "任务总数   : %d" % r["tasks"],
        "依赖边数   : %d" % r["edges"],
        "可排出序列 : %s" % (r["order"] or "（空）"),
        "SELF_LOOP  : %s" % (r["self_loop"] or "无"),
        "CYCLE      : %s" % (r["cycles"] or "无"),
        "DANGLING   : %s %s" % (r["dangling"] or "无",
                                r["bad_ref"] if r["bad_ref"] else ""),
        "结论       : %s" % ("PASS 无环" if r["pass"] else "FAIL 需重构"),
    ]
    return "\n".join(lines)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    path = args[0]
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print("[ERROR] 读不到 %s: %s" % (path, e))
        return 2

    nodes, edges, _ = parse_deps(text)
    if not nodes:
        print("[ERROR] 没解析到任何任务行，确认 plan.md §6.1 依赖关系列表存在")
        return 2
    r = lint(nodes, edges)
    if "--json" in argv:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(render(r))
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
