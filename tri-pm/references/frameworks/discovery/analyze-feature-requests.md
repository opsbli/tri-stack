---
name: analyze-feature-requests
description: 客户功能请求分析框架——按主题归类、评战略对齐，再用 Impact/Effort/Risk/对齐度选出前 3 并给出替代方案与高风险假设的低成本验证法。
source: pm-skills-main/pm-product-discovery/skills/analyze-feature-requests/SKILL.md
domain: 探索
---

# 功能请求分析（analyze-feature-requests）

> 蒸馏自 `analyze-feature-requests`｜域：探索｜源词数：296

把客户功能请求归类、评估、并对照产品目标排优先级。

## 必含章节清单（MUST-SECTIONS）

- [ ] Understand the goal — 理解目标：确认产品目标与期望成果
- [ ] Categorize requests into themes — 归类为主题并命名
- [ ] Assess strategic alignment — 逐主题评估战略对齐度
- [ ] Prioritize the top 3 features — 按 4 因子选出前 **3** 个
- [ ] For each top feature — 每个入选功能给出 4 项

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Domain Context — 领域背景：Opportunity Score 公式与「不让客户设计方案」立场
- [ ] 前置读取：用户若提供文件（spreadsheets、CSVs、含请求的文档）直接读并分析；数据结构化时考虑做汇总表

## 逐段引导问题

- **Understand the goal**：确认将指导优先级判断的 product objective（产品目标）与 desired outcomes（期望成果）。
- **Categorize requests into themes**：把相关请求归到一起，并给每个主题**命名**。
- **Assess strategic alignment**：逐主题评估「与既定目标的对齐程度」。
- **Prioritize the top 3 features**——**4 个**因子（照抄）：
  - **Impact**: Customer value and number of users affected（客户价值与受影响用户数）
  - **Effort**: Development and design resources required（所需开发与设计资源）
  - **Risk**: Technical and market uncertainty（技术与市场不确定性）
  - **Strategic alignment**: Fit with product vision and goals（与产品愿景和目标的契合度）
- **For each top feature**——**4 项**（照抄）：
  - Rationale (customer needs, strategic alignment)（理由：客户需求、战略对齐）
  - Alternative solutions worth considering（值得考虑的替代方案）
  - High-risk assumptions（高风险假设）
  - How to test those assumptions with minimal effort（如何以最小投入验证这些假设）

## 领域公式（Domain Context 原文照抄）

- **Opportunity Score**（Dan Olsen）——用于评估客户报告的问题：
  **Opportunity Score = Importance × (1 − Satisfaction)**，normalized to 0–1（归一化到 0–1）。
- 完整细节与模板见工具箱域的 `prioritization-frameworks` 框架文件（源文件原为跨技能引用）。

## 输出模板

```markdown
（源文件未给出字面骨架。结构性要求为：
主题汇总（每主题：名称 ｜ 归入的请求 ｜ 战略对齐度）
+ 前 3 功能（每个：Impact ｜ Effort ｜ Risk ｜ 战略对齐 ｜ 理由 ｜ 替代方案 ｜ 高风险假设 ｜ 最小投入验证法）。
数据为结构化格式时，「consider creating a summary table」——考虑输出汇总表。）
```

## 输出命名规则

源文件未规定命名。仅要求：Save as markdown or create a structured output document（存为 Markdown 或生成结构化输出文档）。

## 关键规则

- 核心立场（源文件原句）：**Never allow customers to design solutions. Prioritize opportunities (problems), not features.**（绝不让客户来设计解决方案；优先排序机会（问题），而非功能。）——即：请求要还原成背后的问题再排序。
- 输出数量固定 **前 3 个**（注意与 `prioritize-features` 的「前 5 个」不同，不要混用）。
- 每个入选功能都必须附**替代方案**与**高风险假设的最小投入验证法**——本框架的产物要能直接喂给实验设计。
- 用户上传结构化数据（CSV/表格）时，直接在其数据上分析并考虑输出汇总表。

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [Kano Model: How to Delight Your Customers Without Becoming a Feature Factory](https://www.productcompass.pm/p/kano-model-how-to-delight-your-customers) — Kano 模型：如何取悦客户而不沦为功能工厂

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
