---
name: tri-learn-full-testcases
description: tri-learn（学习教练）v1.0.2 全场景测试用例——覆盖五入口路由、掌握判断矩阵、文件契约模板、可执行脚本（route/interval/days-since/due/scan/mastery/audit/create-topic）、反模式与升级路径。
based-on-version: 1.0.2
version: 1.0.2
---

# tri-learn 全场景测试用例

> 基于 `tri-learn` v1.0.2。版本号与 SKILL.md frontmatter `version` 严格一致。

## 一、路由识别（route 脚本）

| # | 输入 | 预期模式 | 依据 |
|---|---|---|---|
| 1 | 我想学 Python 基础 | 学习 | 命中「我想学」 |
| 2 | 教我销售技巧 | 学习 | 命中「教我」 |
| 3 | 我想复习销售技巧 | 复习 | 命中「复习」 |
| 4 | 今天该复习什么 | 全局复习 | 命中「今天该复习」 |
| 5 | 看看我的错题 | 错题 | 命中「错题」 |
| 6 | 我多久没学过这个主题了 | 间隔查询 | 命中「多久没」 |
| 7 | （提交检查站答案） | 回答判掌握 | --answer 或含「答案/检查站」 |

命令：`python scripts/learn_tool.py route "<文本>" --json`，断言 `recommended` 与预期一致。

## 二、间隔重复计算（interval 脚本）

| # | 掌握日 | 复习次 | 预期下次复习 | 依据 |
|---|---|---|---|---|
| 1 | 2026-08-30 | 1 | 2026-08-31 | +1 天 |
| 2 | 2026-08-30 | 2 | 2026-09-03 | +3 天 |
| 3 | 2026-08-30 | 3 | 2026-09-10 | +7 天 |
| 4 | 2026-08-30 | 4 | 2026-09-24 | +14 天 |
| 5 | 2026-08-30 | 5 | 2026-10-30 | +30 天 |

命令：`python scripts/learn_tool.py interval 2026-08-30 <N> --json`，断言 `next_review_date` 与预期一致。

## 三、主题初始化与契约审计（create-topic / audit）

```bash
python scripts/learn_tool.py create-topic "Python基础" --dir <tmp> --json
python scripts/learn_tool.py audit "Python基础" --dir <tmp> --json
```

断言：create-topic 返回 `ok=true` 且 produced 含 `进度.md`、`错题与遗漏.md`、`复习计划.md`；audit 返回 `ok=true` 且 `missing=[]`。

## 四、天数计算（days-since）

在临时主题的 `进度.md` 写入 `最后学习日期：<N天前的日期>` 后运行 `days-since`，断言返回天数≈N。

## 五、到期判断与全局扫描（due / scan）

构造含「已过期/今天到期/未来3天」复习条目的 `复习计划.md`：

```bash
python scripts/learn_tool.py due "销售技巧" --dir <tmp> --json   # due_items 仅含到期项
python scripts/learn_tool.py scan --dir <tmp> --json              # grouped 三档正确归组
```

## 六、掌握判断（mastery）

| 输入 | 预期建议动作 | 是否推进 |
|---|---|---|
| 完全掌握 | …生成下一课 | 是 |
| 基本掌握 | …纠正…生成下一课 | 是 |
| 部分理解 | 生成补充课 NNb，暂不推进 | 否 |
| 尚未理解 | 记录卡点，苏格拉底追问重建 | 否 |

## 七、反模式与守真（人工走查）

- 未掌握时不推进下一课（铁律）。
- 复习先主动回忆，不复读原文。
- 复习日期一律绝对日期。
- 知识锚点无可靠来源则省略。
- 固定文件名 `进度.md` 等不改名。
- 默认不 git commit/push。

## 八、版本检查升级路径

```bash
python scripts/check_update.py --slug tri-learn --json
```

断言：退出码 `<20` 且产出合法 JSON（`state` ∈ {A,B,C,D}）；`--simulate-*` 注入可验证四态。

## 九、能力覆盖回归（对照蒸馏报告 §六）

16 项能力逐项在 SKILL.md / scripts / references 中定位到承载点，任一项缺失即判不良。