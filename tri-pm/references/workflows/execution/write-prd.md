---
name: write-prd
description: 从功能想法或问题陈述创建结构化 PRD，对齐干系人并指导开发。
source: pm-skills-main/pm-execution/commands/write-prd.md
domain: 执行
---

# /write-prd → 产品需求文档（PRD）

> 蒸馏自命令 `write-prd`｜域：执行｜源词数：≈500
> **语法翻译**：源项目以 `/write-prd` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。
> **PRD 模板裁定**：依据 `distillation-baseline.md` §九 D-A，本命令的 MUST-SECTIONS 以 `/write-prd` 八段为命令态权威（与 `create-prd` 技能态模板不同，后者独有 Contacts/Market Segment(s)/Value Proposition(s)/Release 仅作可选补充，不进必含清单）。

## 用途

从模糊想法到详细 brief，创建结构化 PRD 以对齐干系人、指导开发。

## 参数提示

`<feature or problem statement>`（亦接受上传 brief/研究/战略文档）

## 调用示例（翻译为对话形态）

- 源：`/write-prd SSO support for enterprise customers`
- 本环境等价说法：「为企业客户做 SSO 支持的 PRD」
- 源：`/write-prd Users are dropping off during onboarding — fix step 3`
- 本环境等价说法：「用户 onboarding 流失，写 PRD 修复第 3 步」
- 源：`/write-prd [upload a brief]`
- 本环境等价说法：「我上传一份 brief，据此写 PRD」

## 必含章节清单（MUST-SECTIONS）

- [ ] Executive Summary — 执行摘要
- [ ] Background & Context — 背景与上下文
- [ ] Objectives & Success Metrics — 目标与成功指标（含 **Non-Goals** + Success Metrics 表）
- [ ] Target Users & Segments — 目标用户与细分
- [ ] User Stories & Requirements — 用户故事与需求（P0-P1-P2 表 + Acceptance Criteria）
- [ ] Solution Overview — 方案概述
- [ ] Open Questions — 待解决问题（表）
- [ ] Timeline & Phasing — 时间与分阶段

## 工作流步骤

1. **理解功能** — 接受任意形态输入：功能名、问题陈述、用户请求、模糊想法、上传文档。
2. **收集上下文**〔引用技能：`**create-prd**`〕— 按重要性优先提问：
   - 用户问题：解决什么、谁经历、多痛？
   - 目标用户：哪段、多少、当前 workaround？
   - 成功指标：怎么算成功、动了什么？
   - 约束：技术/时间/合规/跨团队依赖？
   - 先前尝试与市场现有方案？
   - 范围偏好：全量还是分阶段？
   （有文档则只问缺口）
3. **生成 PRD** — 应用 `create-prd` 技能产出 8 段文档（见输出模板）。
4. **评审迭代** — 生成后主动提议：收紧范围（质疑 P1 是否该降 P2）、跑事前复盘、拆为用户故事、写干系人更新。
   保存为 markdown 至工作区。

## Checkpoint

> **Step 3 后**："Apply the create-prd skill" — 应用 create-prd 技能产出 8 段文档（以本裁定八段为准）。

## 输出模板

```markdown
## Product Requirements Document: [Feature Name]
**Author**: [user] | **Date**: [today] | **Status**: Draft | **Stakeholders**: [if known]
### 1. Executive Summary
### 2. Background & Context
### 3. Objectives & Success Metrics
**Non-Goals**: 1. [...]  **Success Metrics**: | Metric | Current | Target | Measurement |
### 4. Target Users & Segments
### 5. User Stories & Requirements
**P0**/**P1**/**P2** 各表：| # | User Story | Acceptance Criteria |
### 6. Solution Overview
### 7. Open Questions | Question | Owner | Deadline |
### 8. Timeline & Phasing
```

## 保存指令

保存 PRD 为 markdown 文件至用户工作区（命名 `PRD-[product-name].md`）

## 下一步建议

- 「要我收紧范围吗？挑战哪些 P1 其实该是 P2。」
- 「要我对这份 PRD 跑事前复盘吗？」
- 「要把它拆成工程可用的用户故事吗？」
- 「要写一份干系人更新来同步吗？」

## Further Reading

- [How to Write a Product Requirements Document? The Best PRD Template.](https://www.productcompass.pm/p/prd-template)
- [A Proven AI PRD Template by Miqdad Jaffer (Product Lead @ OpenAI)](https://www.productcompass.pm/p/ai-prd-template)
