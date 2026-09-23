---
name: market-product
description: 一站式营销创意工具箱——生成营销点子、定位陈述、价值主张文案与产品命名，或任选模块。
source: pm-skills-main/pm-marketing-growth/commands/market-product.md
domain: 增长
---

# /market-product → 营销创意工具箱

> 蒸馏自命令 `market-product`｜域：增长｜源词数：约 400
> **语法翻译**：源项目以 `/market-product` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

一次性产出创意营销资产：活动点子、定位陈述、价值主张文案、产品命名方案。可走完整工作流，也可只挑特定模块。

## 参数提示

（源 `argument-hint`：`<product or marketing challenge>`）即用户给出的产品描述或营销挑战，例如「面向远程团队的 AI 排程工具——需要发布营销」。

## 调用示例（翻译为对话形态）

- 源：`/market-product AI scheduling tool for remote teams — need launch marketing`
- 本环境等价说法：「帮我的面向远程团队的 AI 排程工具做发布营销，给我一套营销工具箱」
- 源：`/market-product Help me position our analytics product against enterprise competitors`
- 本环境等价说法：「帮我们的分析产品做针对企业竞品的定位」
- 源：`/market-product We need a name for our new developer productivity feature`
- 本环境等价说法：「给我们的新开发者效率功能起个名」

## 工作流步骤

1. **理解营销需求** — 询问：产品是什么、目标受众？需要什么（整套工具箱，还是只要点子/定位/命名/文案）？背景是发布、重塑还是活动或竞争重定位？有无品牌规范或语气指南？〔引用技能：无，纯澄清〕
2. **按需求生成** — 依据所选模块分别调用对应技能：
   - **Marketing Ideas**〔引用技能：**marketing-ideas**〕：5 个创意、低成本的营销活动点子，每个含渠道、信息角度、互动逻辑、预估投入；混合速赢与大胆押注。
   - **Positioning**〔引用技能：**positioning-ideas**〕：识别前 5 名竞品作定位语境；生成 3-5 条与各自差异化的定位陈述；每条含策略依据。
   - **Value Proposition Statements**〔引用技能：**value-prop-statements**〕：生成营销/销售/上手三类语境文案；分群变体；短（标语）、中（电梯演讲）、长（落地页）三版本。
   - **Product Naming**〔引用技能：**product-name**〕：头脑风暴 5 个独特易记之名；每个含依据、品牌契合、域名可用性说明；检查无意歧义或冲突。
3. **生成输出** — 按下方输出模板汇总为 markdown。
4. **给出下一步建议** — 见「下一步建议」。

## Checkpoint

> **Step 3 后**："Recommended positioning: [which and why]" — 推荐定位：[选哪条、为何]

## 输出模板

```markdown
## Marketing Toolkit: [Product]
**Date**: [today]
**Context**: [launch / rebrand / campaign / etc.]

### Marketing Campaign Ideas
| # | Idea | Channel | Effort | Expected Impact |
|---|------|---------|--------|----------------|

### Positioning Options
| # | Positioning | vs Competitor | Strength | Risk |
|---|-----------|--------------|----------|------|
**Recommended positioning**: [which and why]

### Value Prop Copy
**Tagline**: [one line]
**Elevator pitch**: [2-3 sentences]
**Landing page hero**: [headline + subheading]
**Sales one-liner**: [for sales conversations]

### Product Name Options (if requested)
| # | Name | Rationale | Domain | Risk |
|---|------|----------|--------|------|

### Messaging Matrix
| Audience | Key Message | Proof Point | CTA |
|----------|-----------|------------|-----|
```

## 保存指令

源要求：Save as markdown（存为 markdown 文件）。本环境建议落盘路径：`tri-pm/references/workflows/growth/` 同级产物，或用户指定目录，文件名如 `marketing-toolkit-[product].md`。

## 下一步建议

- 「要我起草完整的营销内容吗（博客、邮件、社媒）？」
- 「要我为这次活动定义 North Star 指标吗？」
- 「要我做一张竞争 battlecard 来支撑定位吗？」
- 「要我规划完整的发布计划吗？」

## Notes（关键规则）

- 定位应被验证而非假设——建议对标题做 A/B 测试。
- 价值主张文案应用客户的语言，而非内部行话。
- 营销点子应具体可落地，而非泛泛（避免「用社交媒体」这类空话）。
- 产品名在确定前应查商标冲突。
- 始终把营销拉回客户的 JTBD（Jobs To Be Done），而非产品功能。

## Further Reading

- [Product Management vs. Product Marketing vs. Product Growth 101](https://www.productcompass.pm/p/product-management-vs-product-marketing) — 角色区分入门（中立、可达、无付费墙）
