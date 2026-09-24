#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spec 拆分器：读 requirements.md 的功能需求表 → 按依赖关系拆成 N 份独立 spec。

用法：
    python scripts/split-specs.py --input <requirements.md> --team 4 [--output <specs目录>]
    python scripts/split-specs.py --input <requirements.md> --team 4 --assignees A,B,C,D
"""
import argparse
import json
import re
import sys
from pathlib import Path


def find_repo_root(start):
    for cand in (start, *start.parents):
        if (cand / ".git").exists():
            return cand
    return start


REPO = find_repo_root(Path(__file__).resolve().parent)


def parse_features(t: str) -> list[dict]:
    """从 requirements.md 的功能需求表提取功能点。"""
    features = []
    m = re.search(r"^##\s*二、功能需求\s*$", t, re.M)
    if not m:
        return features
    seg = t[m.end():]
    nxt = re.search(r"^##\s+", seg[1:], re.M)
    if nxt:
        seg = seg[:nxt.start() + 1]
    for line in seg.splitlines():
        mm = re.match(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|", line)
        if mm:
            num = int(mm.group(1))
            cells = [c.strip() for c in line.split("|")[2:-1]]
            if len(cells) >= 2:
                features.append({
                    "num": num,
                    "name": cells[0],
                    "desc": cells[1] if len(cells) > 1 else "",
                    "priority": cells[2] if len(cells) > 2 else "P1",
                    "source": cells[3] if len(cells) > 3 else "",
                    "acceptance": cells[4] if len(cells) > 4 else "",
                })
    return features


def detect_dependencies(features: list[dict]) -> dict[int, list[int]]:
    """基于功能名中的关键词检测依赖关系（简单启发式）。"""
    deps = {}
    for f in features:
        deps[f["num"]] = []
        name = f["name"]
        # 审核类依赖对应的提交类
        for trigger_word, review_word in [
            ("入库", "入库"), ("申领", "申领"), ("归还", "归还"), ("调拨", "调拨"),
        ]:
            if f"{trigger_word}审核" in name:
                for g in features:
                    if f"{trigger_word}" in g["name"] and "审核" not in g["name"]:
                        deps[f["num"]].append(g["num"])
        # 看板依赖台账
        if "看板" in name:
            for g in features:
                if "管理" in g["name"] or "台账" in g["name"]:
                    deps[f["num"]].append(g["num"])
    return deps


def group_specs(features, deps, team_size):
    """按依赖关系 + 模块边界分组。简单贪心：拓扑排序 + 均匀分配。"""
    # 计算入度
    in_degree = {f["num"]: 0 for f in features}
    for f in features:
        for dep in deps.get(f["num"], []):
            if dep in in_degree:
                in_degree[f["num"]] += 1

    # 拓扑排序分层
    waves = []
    remaining = set(in_degree.keys())
    while remaining:
        wave = [n for n in remaining if in_degree[n] == 0]
        if not wave:
            break  # 循环依赖
        waves.append(sorted(wave))
        remaining -= set(wave)
        for f in features:
            if f["num"] in remaining:
                for dep in deps.get(f["num"], []):
                    if dep in set(wave):
                        in_degree[f["num"]] -= 1
                        if in_degree[f["num"]] == 0:
                            break

    # 按模块名分组（同模块 → 同 spec）
    module_groups = {}
    for f in features:
        # 从名称提取模块关键词
        name = f["name"]
        module = None
        for kw in ["物资分类", "财务分类", "固资管理", "资产标签", "资产入库", "入库审核",
                    "资产申领", "申领审核", "资产归还", "归还审核", "资产调拨", "调拨审核",
                    "我的固资", "数据看板", "设备报修", "报修处理", "我的已办"]:
            if kw in name:
                module = kw
                break
        if module is None:
            module = name[:4]
        module_groups.setdefault(module, []).append(f["num"])

    # 合并相关模块 → spec
    # 简化：按依赖波次 + 模块名聚类
    spec_assign = {}  # feature_num -> spec_index
    spec_id = 0

    # Wave 1: 无依赖的基础配置类
    wave1 = [f["num"] for f in features if f["num"] in waves[0] if waves]
    # 按类型分组：分类配置 vs 其他
    config = [n for n in wave1 if any("分类" in f["name"] for f in features if f["num"] == n)]
    other_w1 = [n for n in wave1 if n not in config]

    groups = []
    if config:
        groups.append(config)
    if other_w1:
        groups.append(other_w1)

    # Wave 2+: 按模块聚类
    for wave in waves[1:]:
        # 贪心：按模块名前缀分组
        wave_groups = {}
        for n in wave:
            f = next((f for f in features if f["num"] == n), None)
            if not f:
                continue
            # 模块关键词
            mod = "other"
            for kw in ["入库", "申领", "归还", "调拨", "报修", "看板", "固资", "标签", "我的"]:
                if kw in f["name"]:
                    mod = kw
                    break
            wave_groups.setdefault(mod, []).append(n)

        # 合并小组直到数量 = team_size - len(groups)
        remaining_slots = max(0, team_size - len(groups))
        sorted_wg = sorted(wave_groups.items(), key=lambda x: -len(x[1]))
        if remaining_slots >= len(sorted_wg):
            for mod, nums in sorted_wg:
                groups.append(nums)
        else:
            # 均匀分配
            all_nums = [n for nums in wave_groups.values() for n in nums]
            chunk = max(1, len(all_nums) // max(1, remaining_slots))
            for i in range(0, len(all_nums), chunk):
                groups.append(all_nums[i:i + chunk])

    return groups, waves


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="requirements.md 或 task-checklist.md 路径")
    ap.add_argument("--team", type=int, default=4, help="团队人数")
    ap.add_argument("--output", default=None, help="输出目录（默认 .tribro/coding/ 下）")
    ap.add_argument("--assignees", default="", help="逗号分隔的负责人名（如 A,B,C,D）")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.is_file():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 2

    t = src.read_text(encoding="utf-8", errors="ignore")
    features = parse_features(t)
    if not features:
        print("未从文档中解析到功能需求表", file=sys.stderr)
        return 1

    deps = detect_dependencies(features)
    groups, waves = group_specs(features, deps, args.team)

    assignees = [s.strip() for s in args.assignees.split(",")] if args.assignees else \
                [f"人员{chr(65 + i)}" for i in range(len(groups))]

    # 确定输出目录
    if args.output:
        out = Path(args.output).resolve()
    else:
        now = src.stat().st_mtime
        out = REPO / ".tribro" / "coding" / f"orchestrate_{int(now)}"
    out.mkdir(parents=True, exist_ok=True)

    # 产出 spec 文件
    for i, nums in enumerate(groups, 1):
        spec_id = f"spec-{i:02d}"
        assignee = assignees[i] if i < len(assignees) else f"人员{chr(64 + i + 1)}"
        feat_list = [f for f in features if f["num"] in nums]
        spec_deps = set()
        for f in feat_list:
            for d in deps.get(f["num"], []):
                if d not in nums:
                    spec_deps.add(d)

        lines = [
            f"# {spec_id}: 功能规格",
            "",
            f"| 项 | 值 |",
            f"|---|---|",
            f"| Spec ID | {spec_id} |",
            f"| 负责人 | {assignee} |",
            f"| 功能点数 | {len(feat_list)} |",
            f"| 依赖 | {'Spec-' + str(next(j for j, g in enumerate(groups, 1) if spec_deps & set(g)), '无') if spec_deps else '无'} |",
            "",
            "## 功能点",
            "",
        ]
        for f in feat_list:
            lines.append(f"- **{f['name']}**（{f['priority']}）：{f['desc']}")
            if f["acceptance"]:
                lines.append(f"  - 验收标准：{f['acceptance']}")
            if f["source"]:
                lines.append(f"  - 出处：{f['source']}")

        if spec_deps:
            lines.append(f"\n## 依赖的其他 Spec\n")
            for d in sorted(spec_deps):
                dep_group = next((j for j, g in enumerate(groups, 1) if d in g), "?")
                lines.append(f"- 功能点 #{d}（属于 spec-{dep_group:02d}）")

        lines.append(f"\n## 回执格式\n")
        lines.append(f"完成后产出 `receipt-{spec_id}.json`（格式见 tri-orchestrate SKILL.md）。")

        (out / f"{spec_id}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 产出 dispatch-plan.md
    dp = [f"# 分配计划\n", f"\n## 分配矩阵\n", f"| Spec | 负责人 | 功能点数 | 功能点编号 |\n|---|---|---|---|"]
    for i, nums in enumerate(groups, 1):
        assignee = assignees[i] if i < len(assignees) else f"人员{chr(64 + i)}"
        dp.append(f"| spec-{i:02d} | {assignee} | {len(nums)} | {nums} |")
    (out / "dispatch-plan.md").write_text("\n".join(dp) + "\n", encoding="utf-8")

    print(f"✅ 拆分完成：{len(features)} 个功能点 → {len(groups)} 份 spec")
    print(f"   输出目录：{out}")
    for i, nums in enumerate(groups, 1):
        print(f"   spec-{i:02d}: {len(nums)} 个功能点")
    return 0


if __name__ == "__main__":
    sys.exit(main())
