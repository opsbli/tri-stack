---
name: prioritize-features
description: 功能待办优先级框架——按 Impact / Effort / Risk / Strategic alignment 四因子评估并给出前 5 推荐，配 Opportunity Score、ICE、RICE 公式；用于排期与范围决策。
source: pm-skills-main/pm-product-discovery/skills/prioritize-features/SKILL.md
domain: 探索
---

# 功能待办优先级（prioritize-features）

> 蒸馏自 `prioritize-features`｜域：探索｜源词数：325

评估并排序一批功能想法，选出**前 5 个**值得推进的。

## 必含章节清单（MUST-SECTIONS）

- [ ] Understand priorities — 理解优先级：确认产品目标与成功指标
- [ ] Evaluate each feature — 按 4 因子逐个评估
- [ ] Recommend the top 5 features — 给出前 5 推荐（含 4 项说明）
- [ ] Present as a prioritization table — 以优先级表呈现（if helpful）

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Domain Context — 领域背景：框架选型建议与 Opportunity Score / ICE / RICE 公式
- [ ] 前置读取：用户若提供文件（spreadsheets、backlogs、opportunity assessments）直接读并分析

## 逐段引导问题

- **Understand priorities**：确认 product objective（产品目标）与 success metrics（成功指标）。
- **Evaluate each feature**——**4 个**评估因子及其原始提问（照抄）：
  - **Impact**: How much does it move the needle on desired outcomes? Consider Opportunity Score if customer data is available.（对期望成果的推动有多大？若有客户数据，考虑用 Opportunity Score。）
  - **Effort**: How much development, design, and coordination is required?（需要多少开发、设计与协调投入？）
  - **Risk**: How much uncertainty exists? What assumptions need testing?（有多少不确定性？哪些假设需要验证？）
  - **Strategic alignment**: How well does it fit the product vision and current goals?（与产品愿景和当前目标的契合度如何？）
- **Recommend the top 5 features**——每项须含 **4 项**（照抄）：
  - Clear ranking (1-5)（明确排名 1–5）
  - Brief rationale for each selection（每项入选的简要理由）
  - Key trade-offs considered（考虑过的关键取舍）
  - What was deprioritized and why（哪些被降级、为什么）

## 领域公式（Domain Context 原文照抄）

- **Opportunity Score**（Dan Olsen, *The Lean Product Playbook*）——推荐用于评估**客户问题**：
  **Opportunity Score = Importance × (1 − Satisfaction)**，normalized to 0–1（Importance 与 Satisfaction 均归一化到 0–1）。
  判读规则：**High Importance + low Satisfaction = best opportunities**（高重要性 + 低满意度 = 最佳机会）。
- **ICE**——推荐用于对举措（initiatives）快速打分：
  **Impact (Opportunity Score × # Customers) × Confidence × Ease**
- **RICE**——为更大团队把 **Reach** 作为独立因子加入。
- 框架选型指引见工具箱域的 `prioritization-frameworks` 框架文件（源文件原为跨技能引用）。

## 输出模板

```markdown
（源文件未给出完整输出骨架，只规定呈现形式：
「Present as a prioritization table if helpful」——
即优先级表，每行含：排名(1-5) ｜ 功能 ｜ Impact ｜ Effort ｜ Risk ｜ Strategic alignment ｜ 入选理由；
表后附「关键取舍」与「被降级项及原因」两段。）
```

## 输出命名规则

源文件未规定命名。仅要求：Save as markdown if the output is substantial（内容较多时存为 Markdown）。

## 关键规则

- 输出数量固定 **前 5 个**，且必须给出**明确排名 1–5**（不是并列一堆）。
- 必须交代「被降级了什么、为什么」——只列入选项不算完成。
- 核心立场（源文件原句）：**Prioritize problems (opportunities), not solutions.**（优先排序**问题（机会）**，而不是解决方案。）
- 有客户数据时优先用 Opportunity Score 评 Impact；无数据时才退回定性判断。
- Opportunity Score 的两项输入（Importance、Satisfaction）必须归一化到 0–1，否则乘积不可比。
- 用户若上传了表格/待办清单，直接读取并在其数据结构上分析，不要另起一张表。

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [Kano Model: How to Delight Your Customers Without Becoming a Feature Factory](https://www.productcompass.pm/p/kano-model-how-to-delight-your-customers) — Kano 模型：如何取悦客户而不沦为功能工厂
- [The Product Management Frameworks Compendium + Templates](https://www.productcompass.pm/p/the-product-frameworks-compendium) — PM 框架汇编

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
