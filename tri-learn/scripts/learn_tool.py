#!/usr/bin/env python3
"""tri-learn 学习教练确定性工具。

将学习技能中的确定性算法下沉为可执行脚本（家族硬约束 18），
agent 层仅在 SKILL.md 保留算法摘要 + 指针 + 用法；本脚本内部不分发他人代码。

子命令：
  route         根据文本识别学习流程模式（学/复/全局复/错题/间隔）
  create-topic  初始化一个主题文件夹（三个固定记录文件 + 可选的课程骨架）
  interval      计算给定掌握日与复习次数的下次复习日期（1/3/7/14/30）
  days-since    计算某主题距最后学习日期的天数
  due           列出某主题到期的复习项（对比绝对日期）
  scan          扫描根目录下所有主题的复习计划，按已过期/今天/未来3天分组
  mastery       返回掌握程度对应的建议动作（决策矩阵辅助）
  audit         校验主题文件夹的三个固定文件存在且结构满足契约

跨平台：使用 pathlib 构造路径，不依赖特定操作系统。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- 常量
TOPIC_FILES = ("进度.md", "错题与遗漏.md", "复习计划.md")

# 间隔重复节奏（固定参数，与 SKILL.md / references 一致）
INTERVALS_DAYS = (1, 3, 7, 14, 30)

# 五入口 + 回答 模式关键词（用于 route）
# 顺序即优先级：特异性高的信号放在前面，避免被泛化的「复习」先命中
ROUTE_RULES = [
    ("全局复习", ("今天该复习", "本周该复习", "该复习什么", "到期复习", "要复习什么")),
    ("错题", ("错题", "遗漏", "没掌握", "看看我的错", "看看我")),
    ("间隔查询", ("多久没学", "最近一次学", "多长时间没学", "多少天没学")),
    ("学习", ("我想学", "想学习", "开始学", "教我", "带我", "想掌握", "系统学习")),
    ("复习", ("复习", "回顾", "重温")),
]

MASTERY_ACTIONS = {
    "完全掌握": ("标记掌握，写入复习计划，生成下一课", True),
    "基本掌握": ("简短纠正，记录小遗漏，写入复习计划，生成下一课", True),
    "部分理解": ("记录遗漏，生成补充课(NNb_)，暂不进入下一课", False),
    "尚未理解": ("记录卡点，苏格拉底追问，从更基础处重建", False),
    "待检查": ("等待学习者回答检查站问题", False),
}


# ---------------------------------------------------------------- 基础工具
def today() -> dt.date:
    return dt.date.today()


def parse_date(s: str) -> dt.date:
    """解析 YYYY-MM-DD，失败抛 ValueError。"""
    return dt.date.fromisoformat(strip_inline(s))


def strip_inline(text: str) -> str:
    """去掉 markdown 行内码/强调等杂质，取日期子串。"""
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    return m.group(0) if m else text.strip(" \t|`*")


def next_interval_date(mastery_date: dt.date, review_count: int) -> dt.date:
    """生成当前第 N 次复习的‘下次复习’日期（基于间隔表）。"""
    idx = min(review_count - 1, len(INTERVALS_DAYS) - 1)
    return mastery_date + dt.timedelta(days=INTERVALS_DAYS[idx])


# ---------------------------------------------------------------- 模式路由
def cmd_route(args: argparse.Namespace) -> int:
    text = args.text
    matched = []
    for mode, kws in ROUTE_RULES:
        if any(kw in text for kw in kws):
            matched.append(mode)
    result = {
        "matched_modes": matched,
        "recommended": matched[0] if matched else "unsure",
        "input": text,
    }
    # 回答检查站的易混：包含检查站/答案 → 归"回答判掌握"
    if args.answer or "答案" in text or "检查站" in text:
        result["recommended"] = "回答判掌握"
    _emit(result, args.json)
    return 0


# ---------------------------------------------------------------- 主题初始化
TEMPLATES = {
    "进度.md": """# [{topic}] 学习进度

## 基本信息
- 开始日期：{date}
- 学习目标：
- 目标程度：了解概念 / 能独立运用 / 深度精通
- 先验知识：
- 最后学习日期：{date}
- 最后复习日期：—

## 课程进度

| 课程 | 完成日期 | 掌握程度 | 下次复习 | 关键误区 |
| --- | --- | --- | --- | --- |

## 当前状态
- 正在学习：
- 最近卡点：
- 下一步建议：
""",
    "错题与遗漏.md": """# [{topic}] 错题与遗漏

## 活跃遗漏

| 日期 | 来源课程 | 遗漏点 | 原回答问题 | 正确理解 | 下次复习重点 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |

## 已解决遗漏

| 解决日期 | 来源课程 | 原遗漏点 | 解决证据 |
| --- | --- | --- | --- |
""",
    "复习计划.md": """# [{topic}] 复习计划

## 复习规则

| 复习次 | 间隔 |
| --- | --- |
| 第 1 次 | 掌握后 1 天 |
| 第 2 次 | 第 1 次后 3 天 |
| 第 3 次 | 第 2 次后 7 天 |
| 第 4 次 | 第 3 次后 14 天 |
| 第 5 次 | 第 4 次后 30 天 |

## 待复习队列

| 下次复习 | 主题 | 课程 | 复习次 | 复习重点 | 状态 |
| --- | --- | --- | --- | --- | --- |

## 复习记录

| 日期 | 课程 | 结果 | 新增遗漏 | 下次复习 |
| --- | --- | --- | --- | --- |
""",
}


def cmd_create_topic(args: argparse.Namespace) -> int:
    root = Path(args.dir)
    topic_dir = root / args.topic
    if topic_dir.exists():
        print(json.dumps({"ok": False, "reason": "主题文件夹已存在", "path": str(topic_dir)})
              if args.json else f"主题文件夹已存在：{topic_dir}")
        return 1
    topic_dir.mkdir(parents=True)
    for fname, body in TEMPLATES.items():
        (topic_dir / fname).write_text(
            body.format(topic=args.topic, date=today().isoformat()), encoding="utf-8"
        )
    # 可选课程骨架
    if args.lesson:
        lesson = args.lesson
        (topic_dir / lesson).write_text(
            LESSON_SKELETON.format(topic=args.topic, title=lesson.split("_", 1)[-1].replace(".md", "")),
            encoding="utf-8",
        )
    produced = sorted(p.name for p in topic_dir.iterdir())
    _emit({"ok": True, "topic_dir": str(topic_dir), "produced": produced}, args.json)
    return 0


LESSON_SKELETON = """# [{topic}] - {title}

## 学习目标

本节结束后，学习者应该能做到什么。

## 内容讲解

用简单语言解释核心概念。优先使用类比、现实例子和循序渐进的小问题。

## 知识锚点

只在有高质量来源或稳定常识时写；没有可靠来源就省略。

## 小结

1.

---

## 检查站

1. 概念确认类问题
2. 理解应用类问题
3. 可选：开放思考类问题

请把你的答案直接告诉我，我会根据你的回答决定下一步。
"""


# ---------------------------------------------------------------- 间隔计算
def cmd_interval(args: argparse.Namespace) -> int:
    mastery = parse_date(args.mastery_date)
    nxt = next_interval_date(mastery, args.review_count)
    _emit(
        {
            "mastery_date": mastery.isoformat(),
            "review_count": args.review_count,
            "interval_days": INTERVALS_DAYS[min(args.review_count - 1, len(INTERVALS_DAYS) - 1)],
            "next_review_date": nxt.isoformat(),
        },
        args.json,
    )
    return 0


# ---------------------------------------------------------------- 天数
def days_since_last(topic_dir: Path) -> tuple[dt.date, int] | None:
    prog = topic_dir / "进度.md"
    if not prog.exists():
        return None
    m = re.search(r"最后学习日期[:：]\s*(\d{4}-\d{2}-\d{2})", prog.read_text(encoding="utf-8"))
    if not m:
        return None
    last = dt.date.fromisoformat(m.group(1))
    return last, (today() - last).days


def cmd_days_since(args: argparse.Namespace) -> int:
    topic_dir = Path(args.dir) / args.topic
    res = days_since_last(topic_dir)
    if res is None:
        _emit({"ok": False, "reason": "未找到最后学习日期"}, args.json)
        return 1
    last, days = res
    _emit({"topic": args.topic, "last_learning_date": last.isoformat(), "days_since": days}, args.json)
    return 0


# ---------------------------------------------------------------- 到期判断
def _parse_review_rows(plan: Path) -> list[dict]:
    """从复习计划.md 提取待复习队列行（下次复习/主题/课程/复习次/复习重点/状态）。"""
    rows = []
    for line in plan.read_text(encoding="utf-8").splitlines():
        strip = line.strip()
        if not strip.startswith("|") or strip.startswith("| 下次复习") or strip.startswith("|---"):
            continue
        cells = [c.strip() for c in strip.strip("|").split("|")]
        if len(cells) < 6:
            continue
        try:
            due = parse_date(cells[0])
        except ValueError:
            continue
        if cells[0] and re.match(r"\d{4}-\d{2}-\d{2}", cells[0]):
            rows.append(
                {
                    "next_review": due.isoformat(),
                    "topic": cells[1],
                    "lesson": cells[2],
                    "review_no": cells[3],
                    "focus": cells[4],
                    "status": cells[5],
                }
            )
    return rows


def _urgency(due: dt.date):
    if due < today():
        return "已过期"
    if due == today():
        return "今天到期"
    if due <= today() + dt.timedelta(days=3):
        return "未来3天即将到期"
    return "未到期"


def cmd_due(args: argparse.Namespace) -> int:
    topic_dir = Path(args.dir) / args.topic
    plan = topic_dir / "复习计划.md"
    if not plan.exists():
        _emit({"ok": False, "reason": f"缺少 {plan}"}, args.json)
        return 1
    rows = _parse_review_rows(plan)
    on_or_before = today()
    due = [r for r in rows if dt.date.fromisoformat(r["next_review"]) <= on_or_before]
    _emit({"topic": args.topic, "due_items": due}, args.json)
    return 0


# ---------------------------------------------------------------- 全局扫描
def cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.dir)
    grouped = {"已过期": [], "今天到期": [], "未来3天即将到期": []}
    total_touched = 0
    for topic_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        plan = topic_dir / "复习计划.md"
        if not plan.exists():
            continue
        total_touched += 1
        for r in _parse_review_rows(plan):
            due = dt.date.fromisoformat(r["next_review"])
            ur = _urgency(due)
            if ur in grouped:
                grouped[ur].append(r)
    _emit(
        {
            "topics_touched": total_touched,
            "grouped": grouped,
            "has_due": bool(grouped["已过期"] or grouped["今天到期"] or grouped["未来3天即将到期"]),
        },
        args.json,
    )
    return 0


# ---------------------------------------------------------------- 掌握判断
def cmd_mastery(args: argparse.Namespace) -> int:
    action, may_advance = MASTERY_ACTIONS.get(args.degree, (None, None))
    if action is None:
        _emit({"ok": False, "reason": f"未知掌握程度：{args.degree}", "valid": sorted(MASTERY_ACTIONS)}, args.json)
        return 1
    _emit({"degree": args.degree, "action": action, "advance_next_lesson": may_advance}, args.json)
    return 0


# ---------------------------------------------------------------- 审计
def cmd_audit(args: argparse.Namespace) -> int:
    topic_dir = Path(args.dir) / args.topic
    if not topic_dir.exists():
        _emit({"ok": False, "reason": "主题文件夹不存在"}, args.json)
        return 1
    missing = [f for f in TOPIC_FILES if not (topic_dir / f).exists()]
    _emit(
        {
            "topic": args.topic,
            "ok": not missing,
            "missing": missing,
            "files": sorted(p.name for p in topic_dir.iterdir() if p.is_file()),
        },
        args.json,
    )
    return 0


# ---------------------------------------------------------------- 分发
def _emit(d: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
    else:
        # 人类可读概览
        for k, v in d.items():
            print(f"{k}: {v}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="tri-learn 学习教练确定性工具")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("route", help="识别文本对应学习流程模式")
    sp.add_argument("text", help="用户表达，如「我想学X」「今天该复习什么」")
    sp.add_argument("--answer", action="store_true", help="标记为检查站回答")
    sp.add_argument("--json", action="store_true", help="JSON 输出")
    sp.set_defaults(func=cmd_route)

    sp = sub.add_parser("create-topic", help="初始化主题文件夹")
    sp.add_argument("topic")
    sp.add_argument("--dir", default=".", help="学习仓库根目录")
    sp.add_argument("--lesson", default=None, help="可选的课程文件名，如 01_变量.md")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_create_topic)

    sp = sub.add_parser("interval", help="计算下次复习日期")
    sp.add_argument("mastery_date", help="掌握日期 YYYY-MM-DD")
    sp.add_argument("review_count", type=int, help="本次复习次（1-5）")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_interval)

    sp = sub.add_parser("days-since", help="距最后学习日期的天数")
    sp.add_argument("topic")
    sp.add_argument("--dir", default=".")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_days_since)

    sp = sub.add_parser("due", help="列出某主题到期复习项")
    sp.add_argument("topic")
    sp.add_argument("--dir", default=".")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_due)

    sp = sub.add_parser("scan", help="扫描所有主题复习计划并三档分组")
    sp.add_argument("--dir", default=".", help="学习仓库根目录")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_scan)

    sp = sub.add_parser("mastery", help="掌握程度 → 建议动作")
    sp.add_argument("degree", help="完全掌握/基本掌握/部分理解/尚未理解/待检查")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_mastery)

    sp = sub.add_parser("audit", help="校验主题文件夹契约")
    sp.add_argument("topic")
    sp.add_argument("--dir", default=".")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_audit)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, FileNotFoundError) as exc:
        print(json.dumps({"error": str(exc), "code": "invalid_input"}))
        sys.exit(2)