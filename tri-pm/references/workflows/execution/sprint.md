---
name: sprint
description: 冲刺生命周期——规划冲刺、跑回顾、或生成发布说明（三模式）。
source: pm-skills-main/pm-execution/commands/sprint.md
domain: 执行
---

# /sprint → 冲刺生命周期

> 蒸馏自命令 `sprint`｜域：执行｜源词数：≈870
> **语法翻译**：源项目以 `/sprint` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

覆盖冲刺生命周期三模式：**plan** 规划、**retro** 回顾、**release-notes** 发布沟通。

## 参数提示

`[plan|retro|release-notes] <context>`（无参则问所处阶段）

## 调用示例（翻译为对话形态）

- 源：`/sprint plan 2-week sprint, 4 engineers, focus on checkout`
- 本环境等价说法：「规划一个 2 周冲刺，4 名工程师，聚焦结账」
- 源：`/sprint retro [paste feedback]`
- 本环境等价说法：「把团队反馈整理成冲刺回顾」
- 源：`/sprint release-notes [paste tickets]`
- 本环境等价说法：「根据这些工单写发布说明」

## 工作流步骤

**Plan 模式**
1. **收集上下文** — 周期、团队组成与可用性、目标、backlog、遗留项、已知中断。
2. **估算产能**〔引用技能：`**sprint-plan**`〕— 会议/值班/PTO 后可用点；按历史或行业 70% 理论产能调整；展示每人拆分。
3. **遴选排序** — 推荐合产能故事；标依赖链；识别风险（未细化/外部依赖/需设计）；平衡快赢与大项；每故事须有 AC。
4. **生成计划** — 输出 Sprint Plan（见模板，含 Capacity 表、Selected Stories、Risks、Definition of Done）。

**Retro 模式**
1. **收集反馈** — 粘贴反馈/指标/观察；问偏好格式：Start/Stop/Continue、4Ls、Sailboat。
2. **分析结构**〔引用技能：`**retro**`〕— 归类、找主题、分症状与根因、标亮点。
3. **生成回顾** — 输出 Sprint Retrospective（What Went Well/Didn't、Key Insights、Action Items 表、Metrics）。

**Release Notes 模式**
1. **接受内容** — Jira/Linear 工单、PRD、Git 提交、内部总结。
2. **转化**〔引用技能：`**release-notes**`〕— 技术→用户收益；分类 New/Improvements/Fixes；用产品语气。
3. **生成说明** — 输出 What's New（Highlights、New Features、Improvements、Bug Fixes、Coming Soon）。保存 markdown，可转多渠道。

## Checkpoint

> **Plan 后**："Protect 20% buffer for unplanned work — teams that plan at 100% capacity always miss" — 留 20% 缓冲，100% 排产必失败。
> **Retro 后**："Focus on 2-3 high-impact action items, not 10" — 聚焦 2-3 高影响行动项。

## 输出模板

```markdown
## Sprint Plan: [Name]
**Duration** / **Sprint Goal** / **Team**
### Capacity | Selected Stories | Sprint Risks | Definition of Done
## Sprint Retrospective: [Name] — [Format]
### What Went Well / Didn't / Key Insights / Action Items / Metrics
## What's New — [Version]
### Highlights / New Features / Improvements / Bug Fixes / Coming Soon
```

## 保存指令

保存为 markdown（各模式均可）

## 下一步建议

- 模式可串联：plan →（执行）→ retro → release-notes
- 「要把风险最高处拆成测试场景吗？」「要写发布清单吗？」

## Further Reading

- [Product Owner vs Product Manager: What's the difference?](https://www.productcompass.pm/p/product-manager-vs-product-owner)
