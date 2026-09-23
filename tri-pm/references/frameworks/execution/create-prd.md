---
name: create-prd
description: 用 8 段 PRD 模板撰写产品需求文档——覆盖问题、目标、用户、方案与发布规划。
source: pm-skills-main/pm-execution/skills/create-prd/SKILL.md
domain: 执行
---

# PRD 撰写（create-prd）

> 蒸馏自 `create-prd`｜域：执行｜源词数：≈620

> ⚠️ **PRD 模板裁定声明（据 `distillation-baseline.md` §九 D-A）**
> 源项目存在两套互相冲突的 8 段 PRD：技能态 `create-prd`（Summary / Contacts / Background / Objective / Market Segment(s) / Value Proposition(s) / Solution / Release）与命令态 `/write-prd`（Executive Summary / Background & Context / Objectives & Success Metrics / Target Users & Segments / User Stories & Requirements / Solution Overview / Open Questions / Timeline & Phasing）。上游已裁定**以 `/write-prd` 为命令态权威**。
> 因此本文件的**必含章节按 `/write-prd` 八段填写**（见下）。技能态独有的 **Contacts / Market Segment(s) / Value Proposition(s) / Release** 仅在「可选补充段」列出，不进必含清单、不参与 BLOCK 判定。

## 必含章节清单（MUST-SECTIONS）

- [ ] Executive Summary — 执行摘要（2-3 句：是什么、为谁、为何现在做）
- [ ] Background & Context — 背景与上下文（问题空间、前期研究、市场背景）
- [ ] Objectives & Success Metrics — 目标与成功指标（含 **Non-Goals** + Success Metrics 表）
- [ ] Target Users & Segments — 目标用户与细分
- [ ] User Stories & Requirements — 用户故事与需求（P0-P1-P2 表 + Acceptance Criteria）
- [ ] Solution Overview — 方案概述
- [ ] Open Questions — 待解决问题（表：问题 / 负责人 / 截止）
- [ ] Timeline & Phasing — 时间与分阶段

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Contacts — 关键干系人姓名/角色/备注（来自技能态 create-prd）
- [ ] Market Segment(s) — 市场细分（按人群问题/任务定义，非人口统计）
- [ ] Value Proposition(s) — 价值主张（客户任务/收益/规避痛点/优于竞品处）
- [ ] Release — 发布规划（首版 vs 未来版；用相对时间，避免精确日期）

## 逐段引导问题

- **Executive Summary**：本文档讲什么？
- **Background & Context**：这是关于什么举措？为何是现在？有什么刚变为可能？
- **Objectives & Success Metrics**：目标是什么、为何重要？如何利好公司与客户？与愿景战略如何对齐？用 SMART OKR 格式写 Key Results；Non-Goals 显式列出不做的事。
- **Target Users & Segments**：为谁构建？有何约束？
- **User Stories & Requirements**：按 P0（必须有）/P1（应有）/P2（未来）分级，每条配 Acceptance Criteria。
- **Solution Overview**：关键特性、设计决策、技术方案（如相关）。
- **Open Questions**：仍悬而未决、无法从上下文回答的问题。
- **Timeline & Phasing**：里程碑、依赖、分阶段。

## 输出模板

```markdown
## Product Requirements Document: [Feature Name]
**Author**: [user] | **Date**: [today] | **Status**: Draft | **Stakeholders**: [if known]

### 1. Executive Summary
[2-3 sentences: what, for whom, why now]

### 2. Background & Context
[Problem space, prior research, market context, what prompted this]

### 3. Objectives & Success Metrics
**Goals**:
1. [Specific, measurable goal]
**Non-Goals**:
1. [What we're not doing, and why]
**Success Metrics**:
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|

### 4. Target Users & Segments
[Who this serves, user profiles, segment sizing]

### 5. User Stories & Requirements
**P0 — Must Have** | **P1 — Should Have** | **P2 — Nice to Have**
（每条：# | User Story | Acceptance Criteria）

### 6. Solution Overview
[High-level approach, key design decisions]

### 7. Open Questions
| Question | Owner | Deadline |
|----------|-------|----------|

### 8. Timeline & Phasing
[Milestones, dependencies, phasing]
```

## 输出命名规则

`PRD-[product-name].md`（源文件规定；内容充实时存为 markdown 文档）

## 关键规则

- 具体、以数据驱动；每段回链整体战略
- 显式标注假设，便于团队验证
- 用小学生能懂的语言，避免术语
- Non-Goals 与 Goals 同等重要，防范围蔓延
- 成功指标须具体：「提升 NPS」差，「90 天内 NPS 由 32 升至 45」好

## Checkpoint

> "Apply the create-prd skill" — 注：源项目此处调用 create-prd 却给出与技能态不同的模板（未收敛）；本环境以 `/write-prd` 八段为权威。

## Further Reading

- [How to Write a Product Requirements Document? The Best PRD Template.](https://www.productcompass.pm/p/prd-template)
- [A Proven AI PRD Template by Miqdad Jaffer (Product Lead @ OpenAI)](https://www.productcompass.pm/p/ai-prd-template)
