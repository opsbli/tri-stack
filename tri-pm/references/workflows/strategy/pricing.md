---
name: pricing
description: 设计定价策略——模型、竞争分析、支付意愿估算、定价实验
source: pm-skills-main/pm-product-strategy/commands/pricing.md
domain: 战略
---

# /pricing → 定价策略设计

> 蒸馏自命令 `pricing`｜域：战略｜源词数：约 520
> **语法翻译**：源以 `/pricing` 斜杠调用；本环境以下「工作流步骤」即等价编排，由 Agent 按步执行。

## 用途

从第一性原理构建定价策略：分析定价模型、估算支付意愿、对标竞品、设计定价实验。

## 参数提示

`<product or pricing question>`（产品或定价问题；可附竞品定价页或当前定价数据）

## 调用示例（翻译为对话形态）

- 源：`/pricing SaaS project management tool moving from free to paid`
- 本环境等价说法：「我们的 SaaS 项目管理工具要从免费转付费，请设计定价策略」
- 源：`/pricing Should we switch from per-seat to usage-based pricing?`
- 本环境等价说法：「我们是否该从按席位改为按用量计费？请分析」
- 源：`/pricing [upload competitor pricing pages or current pricing data]`
- 本环境等价说法：「我上传竞品定价页/当前定价数据，请据此设计定价」

## 工作流步骤

1. **理解定价上下文** — 追问：产品？交付什么价值？当前定价（模型/价位/打包）？触发点（新品/调价/竞争压力/增长停滞）？目标客户与预算？约束（合同/市场期待/定位）？
2. **分析定价模型** — 〔引用：`**pricing-strategy**`、`**monetization-strategy**`〕评估适用模型：Flat-rate（简单可预测）、Per-seat/user（随采纳扩展）、Usage-based（成本对齐价值）、Tiered（捕获不同支付意愿）、Freemium（驱动采纳）、Hybrid（复杂产品多杠杆）。每模型给优劣、契合度、收入预测法。
3. **竞争定价分析** — 用联网检索对标 3-5 竞品，识别品类定价模式与趋势（如 B2B SaaS 从 per-seat 转向 usage-based），收集定价页数据点。
4. **支付意愿估算** — 有调研/反馈则做 Van Westendorp 分析并按用户类型细分；无数据则基于价值交付、竞争锚定、市场常态估算，并设计可运行的支付意愿调研。
5. **生成定价建议** — 按下方案板产出 markdown（含 Free/Trial 策略、竞争基准、收入预测、迁移计划、实验、风险、关键指标）。
6. **提供下一步** — 建议：建含替代收入模型的变现策略？跑市场扫描验证定价假设？起草调价客户沟通？设计定价 A/B 测试？

## Checkpoint

> （源未设 checkpoint）

## 输出模板

```markdown
## Pricing Strategy: [Product]
**Date**: [today]  **Current pricing**: [if applicable]
### Recommended Model: [模型名]
**Why this model**: [基于价值交付的理由]
### Pricing Structure
| Tier | Price | Includes | Target Segment | Key Limit |
### Free / Trial Strategy
[免费什么、门槛什么、转化触发]
### Competitive Benchmark
| Competitor | Model | Price Range | Positioning |
### Revenue Projections
| Scenario | Assumptions | Year 1 ARR | Year 2 ARR |
| Conservative/Expected/Optimistic | | | |
### Migration Plan
[老客户过渡：祖父条款/沟通/时间线]
### Pricing Experiments
| Experiment | What We're Testing | Method | Duration |
### Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
### Key Metrics to Track
- 各档转化率 / ARPU / 升级降级率 / 按价格敏感度流失 / 价格弹性信号
```

## 保存指令

保存为 markdown（建议 `Pricing-Strategy-[product].md`）。

## 下一步建议

- 创建含替代收入模型的变现策略
- 跑市场扫描验证定价假设
- 起草调价客户沟通文案
- 设计定价 A/B 测试

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
