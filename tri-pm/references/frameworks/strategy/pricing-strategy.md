---
name: pricing-strategy
description: 设计定价策略——定价模型、竞争定价分析、支付意愿估算、价格弹性
source: pm-skills-main/pm-product-strategy/skills/pricing-strategy/SKILL.md
domain: 战略
---

# 定价策略（Pricing Strategy）

> 蒸馏自 `pricing-strategy`｜域：战略｜源词数：约 460

## 必含章节清单（MUST-SECTIONS）

- [ ] 1. Understand the value delivered — 理解交付价值
- [ ] 2. Evaluate pricing models — 评估定价模型
- [ ] 3. Analyze competitive pricing — 竞争定价分析
- [ ] 4. Design the pricing structure — 设计定价结构
- [ ] 5. Estimate price sensitivity — 估算价格敏感度
- [ ] 6. Plan pricing experiments — 规划定价实验
- [ ] 7. Output a pricing recommendation — 输出定价建议

### 可选补充段（OPTIONAL）

- [ ] Context — 角色与输入
- [ ] Pricing Models 表 — 7 种模型对照

## 逐段引导问题

- **1. 理解价值**：核心价值主张？客户替代方案及其成本？产品交付的可量化结果（省时/增收/降本）？基于此的支付意愿？
- **2. 评估模型**：从下表选最契合者。
- **3. 竞争分析**：映射竞品定价档位与包含项；定位（高端/中端/预算）；找定价空白；记录行业惯例。
- **4. 设计结构**：2-4 档清晰差异化；功能门槛按价值指标而非任意限制；价值指标（按用户/事件/存储/API 计费）；锚定定价（让最流行档成明显选择）；年付折扣通常 **15-20%**。
- **5. 价格敏感度**：如有调研数据用 **Van Westendorp 价格敏感度计**（太便宜→质量疑虑；便宜→好价值；贵→开始犹豫；太贵→不买）；否则基于竞品与价值估算。
- **6. 实验**：A/B 测试定价页；创始人直售测支付意愿；落地页不同锚点测试；按价格点做转化率队列分析。
- **7. 输出建议**：见下方模板。

## 定价模型对照表

| Model | Best For | Example |
|---|---|---|
| **Flat-rate** | 简单产品、可预测成本 | Basecamp ($99/mo) |
| **Per-seat** | 协作工具、团队产品 | Slack, Figma |
| **Usage-based** | 基础设施、API 产品 | AWS, Twilio |
| **Tiered** | 有明显用户细分 | 多数 SaaS (Free/Pro/Enterprise) |
| **Freemium** | 有病毒/网络效应 | Spotify, Notion |
| **Freemium + usage** | 平台产品 | Vercel, OpenAI API |
| **Value-based** | 高影响企业工具 | Salesforce, Palantir |

## 输出模板

```markdown
## Pricing Strategy: [Product]
Recommended Model: [模型类型]
Value Metric: [计费单位]

| Tier | Price | Target Segment | Key Features | Positioning |
|---|---|---|---|---|

Key Assumptions:
- [假设] → [如何测试]

Risks:
- [风险] → [缓解]
```

## 输出命名规则

源文件未规定（仅写「Save as markdown」）。

## 关键规则

- 从价值交付、竞争定位、支付意愿出发。
- 逐步思考，标记上线前需验证的假设。
- 若有竞品定价/调研/财务/用量文件先读；必要时用联网检索竞品定价。

## Checkpoint

> （源未设 checkpoint）

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
