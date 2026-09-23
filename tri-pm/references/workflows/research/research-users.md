---
name: research-users
description: 综合用户研究——从研究数据构建画像、用户分群并绘制客户旅程
source: pm-skills-main/pm-market-research/commands/research-users.md
domain: 研究
---

# /research-users → 用户研究综合

> 蒸馏自命令 `research-users`｜域：研究｜源词数：~880
> **语法翻译**：源项目以 `/research-users` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

将原始研究数据转化为可行动的用户画像、行为分群与客户旅程地图。接受问卷数据、访谈笔记、反馈、分析数据，或无数据时的产品描述做探索性研究。

## 参数提示

`<research data, survey results, or product description>`（源 argument-hint）

## 调用示例（翻译为对话形态）

- 源：`/research-users [upload survey results, interview notes, or feedback data]`
- 本环境等价说法：「帮我综合用户研究：[上传问卷结果/访谈笔记/反馈数据]」
- 源：`/research-users B2B project management tool for agencies — help me understand our users`
- 本环境等价说法：「我们是面向代理商的 B2B 项目管理工具，帮我理解我们的用户」
- 源：`/research-users [paste user feedback or support ticket data]`
- 本环境等价说法：「这是我们粘贴的用户反馈/工单数据，帮我做用户研究」

## 工作流步骤

1. **接受研究输入** — 接受任意组合：问卷答复（CSV/表格/粘贴）、访谈笔记或转录、工单或功能请求、产品分析/行为数据、NPS 或满意度数据、产品描述（无数据时的探索性研究）。〔引用技能：无〕
   - 提问：你有什么研究？什么格式？想理解什么（用户是谁/差异/摩擦在哪）？这会支撑什么决策（路线图/定位/定价/ onboarding）？

2. **构建画像** — 应用 **user-personas** 技能：〔引用技能：`**user-personas**`〕
   - 从数据识别 3–4 个区分性 persona；每 persona：名称、角色、目标（JTBD）、痛点、收益、行为模式；包含数据中让你意外的洞察；标注 persona 占比（数据允许时）。

3. **用户分群** — 应用 **user-segmentation** 与 **market-segments** 技能：〔引用技能：`**user-segmentation**`、`**market-segments**`〕
   - 创建行为分群（非仅人口）；每分群：规模、JTBD、产品契合、付费意愿、参与度；识别最高价值与最高增长分群；将分群映射到 persona（重叠关系）。

4. **绘制客户旅程** — 应用 **customer-journey-map** 技能：〔引用技能：`**customer-journey-map**`〕
   - 端到端旅程：Awareness → Consideration → Onboarding → Active Use → Expansion → Advocacy；每阶段：触点、情绪、痛点、aha 时刻；识别最大流失点；标注值得放大的愉悦时刻。

5. **生成研究报告** — 按下列模板输出「User Research Report」。

6. **提供下一步** — 见「下一步建议」。

## Checkpoint

> （源未设 checkpoint）

## 输出模板

```markdown
## User Research Report: [Product]

**Date**: [today]
**Data sources**: [what was analyzed]
**Sample size**: [if applicable]

### Executive Summary
[3-5 sentences: key findings and implications]

### Personas
#### Persona 1: [Name] — "[Quote that captures them]"
- **Who**: [role, context, experience level]
- **Primary JTBD**: [When..., I want to..., so I can...]
- **Key pains**: [top 3]
- **Key gains**: [what delights them]
- **Behavioral pattern**: [how they use the product]
- **Prevalence**: [X% of user base]
[Repeat for each persona]

### User Segments
| Segment | Size | Primary JTBD | Product Fit | Value | Growth |
|---------|------|-------------|-------------|-------|--------|

### Customer Journey Map
| Stage | Touchpoints | Emotion | Pain Points | Opportunities |
|-------|------------|---------|-------------|---------------|

### Key Insights
1. [Insight with supporting evidence]

### Recommendations
1. [Actionable recommendation tied to findings]

### Open Questions
[What the data didn't answer — suggested follow-up research]
```

## 保存指令

源要求存为 markdown 文档。

## 下一步建议

- 是否要为某个具体 persona 创建访谈提纲深挖？
- 是否要跨这些分群做情感分析？
- 是否要为头部 persona 构建价值主张？
- 是否要将旅程图痛点按优先级转成功能机会？

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
