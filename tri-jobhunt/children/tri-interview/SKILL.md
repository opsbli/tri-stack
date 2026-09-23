---
name: tri-interview
slug: tri-interview
version: 1.0.1
displayName: 面试准备
description: tri-jobhunt 的 children 子 skill，由主 skill(R6)委派。以 STAR 故事库为核心，预测题目、准备难答、生成向面试官的问题。复用共享 references/star-framework。
summary: 面试准备子 skill。
tags: [interview, star, behavioral, storytelling]
license: MIT
---

# tri-interview · 面试准备（children 子 skill）
> 产物落盘：本 children 不独立落盘——用户成果物由主 skill `tri-jobhunt` 统一落 `.tribro/tri-jobhunt/`（`.tribro/` 不存在时由主 skill 先创建）；链路审计文档由主 skill 落 `.tribro/forge/tri-jobhunt/`。本 children 随主 skill 包分发，遵循主 skill §落盘规则。


> 由主 skill `tri-jobhunt` 依 R6 委派激活，**不对外暴露**。把简历要点转换成可讲的 STAR 故事，
> 并预测题目、准备难答，让面试有底气。复用共享 `references/star-framework.md`。

## 三阶段框架

1. **Phase 1 · 角色分析**：读 JD，识别岗位要的胜任力与可能的 Behavioral 题。
2. **Phase 2 · Story Banking**：从简历 bullet 造 STAR 故事，归档进故事库。
3. **Phase 3 · 模拟准备**：预测题 → 写 Script → 练多版本时长。

## 决策要点（引用 star-framework.md）

- 故事库五类：Leadership / Problem-Solving / Collaboration / Achievement / Failure-Growth，
  **目标 8-10 个 STAR**。
- 多版本：Full 2min / Short 60s / One-liner 15s。
- 难答公式：weakness = `Real+Self-awareness+Improvement`；离职 = 积极+向前+简短；
  失败 = 真实失败 + 学到了 + 如何应用。

## 关键动作

| 任务 | 动作 |
|---|---|
| 预测题 | 按角色归纳 Behavioral 5 类 + Role-Specific(PM/Eng/Marketing/Sales)×4 + Standard×3 组 |
| 「Tell Me About Yourself」 | 30-60s 脚本：现在→过去→为什么适合 |
| 薪资问题转移 | 提前把薪资引到谈判阶段，暂答「更看重匹配度，薪资可在 offer 阶段谈」 |
| 向面试官提问 | 分 Hiring Manager / Team / Exec 三组；避免 4 类高风险问题 |

## 输出

`# INTERVIEW PREP: [POSITION] AT [COMPANY]`：Role Analysis + Predicted Questions +
STAR Story Bank + "Tell Me About Yourself" Script + Questions to Ask + Red Flag Answers。

## 边界

- STAR 必须是**本人真实经历**，NEVER 虚构（R11）。可调长度与侧重，不造假。
- 高敏感（薪资）只给话术与框架，不替代专业薪酬意见。