---
name: north-star
description: 定义 North Star 指标及支撑输入指标——区分业务游戏并用最佳实践校验。
source: pm-skills-main/pm-marketing-growth/commands/north-star.md
domain: 增长
---

# /north-star → North Star 指标定义

> 蒸馏自命令 `north-star`｜域：增长｜源词数：约 500
> **语法翻译**：源项目以 `/north-star` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

找出最能捕捉产品交付价值的单一指标，以及驱动它的输入指标。对业务游戏分类，并用成熟标准校验。

## 参数提示

（源 `argument-hint`：`<product or business>`）即用户给出的产品或业务描述，例如「面向团队协同的 B2B SaaS」「订阅制变现的消费级健身 App」。

## 调用示例（翻译为对话形态）

- 源：`/north-star B2B SaaS for team collaboration`
- 本环境等价说法：「我们的产品是面向团队协同的 B2B SaaS，帮我定 North Star 指标」
- 源：`/north-star Consumer fitness app monetized through subscriptions`
- 本环境等价说法：「我们是个订阅变现的消费级健身 App，帮我定 North Star」
- 源：`/north-star Help me fix our North Star — we're tracking DAU but it doesn't feel right`
- 本环境等价说法：「我们的 North Star 定得不对——现在跟踪 DAU 但感觉不对，帮我修正」

## 工作流步骤

1. **理解产品** — 询问：产品是什么、给用户交付什么价值？商业模式（订阅/交易/广告/市场）？目前在跟踪哪些指标（如有）？为何现在需要（新品 / 现有指标不对 / 团队对齐）？〔引用技能：无，纯澄清〕
2. **分类业务游戏**〔引用技能：**north-star-metric**〕— 判定产品玩的是哪类游戏：
   - **Attention**：营收来自用户时间/互动（媒体、社交、广告型）
   - **Transaction**：营收来自购买（电商、市场）
   - **Productivity**：营收来自效率提升（SaaS、工具、B2B）
   - 游戏类型决定哪种 North Star 合理。
3. **定义 North Star** — 提出 2-3 个候选；逐条用 7 条标准校验（见下）；推荐最强候选并给依据。
4. **定义输入指标** — 为选定 NSM 识别 3-5 个输入指标：每个都是直接驱动 NSM 的杠杆；每个可由特定团队负责；合在一起对 NSM 变动的解释应 MECE。
5. **生成指标体系** — 按下方输出模板汇总为 markdown。
6. **给出下一步建议** — 见「下一步建议」。

## Checkpoint

> **Step 3 后**："Revenue is never a good North Star — it's a lagging indicator that doesn't capture user value." — 营收永远不是好 North Star——它是滞后指标，无法捕捉用户价值。

> **Step 4 后**："Input metrics are what make the framework actionable — without them, the North Star is just a vanity dashboard." — 输入指标才让框架可落地——没有它们，North Star 只是个虚荣仪表盘。

## 输出模板

```markdown
## North Star Framework: [Product]
**Business Game**: [Attention / Transaction / Productivity]

### North Star Metric
**Metric**: [precise name]
**Definition**: [formula or measurement method]
**Why this metric**: [explains value, leads revenue, is actionable]
**Current value**: [if known]
**Target**: [goal]

### Validation
| Criterion | Pass? | Notes |
|----------|-------|-------|
| Expresses value | [Y/N] | [explanation] |
| Leading indicator | [Y/N] | [explanation] |
| Measurable | [Y/N] | [explanation] |
| Understandable | [Y/N] | [explanation] |
| Actionable | [Y/N] | [explanation] |
| Not vanity | [Y/N] | [explanation] |
| Not gameable | [Y/N] | [explanation] |

### Input Metrics
| Input Metric | Drives North Star By | Owner | Current | Target |
|-------------|---------------------|-------|---------|--------|

### Metrics Constellation
[Visual tree showing North Star → Input Metrics → Team Actions]

### Counter-Metrics
| Metric | Protects Against |
|--------|-----------------|

### Anti-Patterns Avoided
[Why we didn't choose DAU, revenue, or other common but flawed metrics]
```

## 保存指令

源要求：Save as markdown（存为 markdown 文件）。本环境建议落盘路径：`tri-pm/references/workflows/growth/` 同级产物，或用户指定目录，文件名如 `north-star-framework-[product].md`。

## 下一步建议

- 「要我围绕这套指标搭一个完整仪表盘吗？」
- 「要我基于这些指标创建 OKR 吗？」
- 「要我写 SQL 查询来计算这些指标吗？」

## Notes（关键规则）

- North Star 应衡量*交付的价值*，而非仅*活跃*——「日活」只有在活跃使用=价值交付时才成立。
- 营收永远不是好 North Star——它是滞后指标，不捕捉用户价值。
- 输入指标才让框架可落地——没有它们，North Star 只是虚荣仪表盘。
- 每年或商业模式重大变化时重审 North Star。
- 反向指标（Counter-metrics）防范古德哈特定律——当指标成为目标，它就不再是好指标。

## Further Reading

- [The North Star Framework 101](https://www.productcompass.pm/p/the-north-star-framework-101) — NSM 定义与示例（中立、可达、无付费墙）
- [AARRR (Pirate) Metrics](https://www.productcompass.pm/p/aarrr-pirate-metrics) — 增长五阶段框架（中立、可达、无付费墙）
