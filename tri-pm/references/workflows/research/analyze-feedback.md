---
name: analyze-feedback
description: 规模化分析用户反馈——情感分析、主题抽取与分群级洞察
source: pm-skills-main/pm-market-research/commands/analyze-feedback.md
domain: 研究
---

# /analyze-feedback → 用户反馈分析

> 蒸馏自命令 `analyze-feedback`｜域：研究｜源词数：~720
> **语法翻译**：源项目以 `/analyze-feedback` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

将海量用户反馈（评论、问卷、工单、NPS 答复）处理为带情感分析与分群级模式的结构化洞察。

## 参数提示

`<feedback data as CSV, text, or file>`（源 argument-hint）

## 调用示例（翻译为对话形态）

- 源：`/analyze-feedback [upload a CSV of NPS responses]`
- 本环境等价说法：「帮我分析这份 NPS 答复的 CSV」
- 源：`/analyze-feedback [paste app store reviews or survey responses]`
- 本环境等价说法：「这是我粘贴的应用商店评论/问卷答复，帮我分析」
- 源：`/analyze-feedback [upload support ticket export]`
- 本环境等价说法：「这是我上传的工单导出，帮我做反馈分析」

## 工作流步骤

1. **接受反馈数据** — 接受任意格式：〔引用技能：无〕
   - CSV/Excel（含反馈文本与可选元数据：日期、分群、评分）；粘贴文本（评论、问卷、Slack 消息）；上传文档或反馈工具导出。
   - 提问：这是什么反馈（NPS/评论/工单/问卷）？有要单独分析的分群吗（用户层级/套餐/地理）？想找什么（通用主题/具体问题/时间趋势）？

2. **分析** — 应用 **sentiment-analysis** 技能：〔引用技能：`**sentiment-analysis**`〕
   - **Sentiment scoring**：每条反馈分类（正面/中性/负面）
   - **Theme extraction**：识别重复主题并聚类相关反馈
   - **Frequency analysis**：统计各主题出现次数
   - **Segment analysis**：按用户分群拆解情感与主题（数据允许时）
   - **Trend detection**：有日期时识别情感随时间变化

3. **生成分析报告** — 按下列模板输出「Feedback Analysis Report」。

4. **提供下一步** — 见「下一步建议」。

## Checkpoint

> （源未设 checkpoint）

## 输出模板

```markdown
## Feedback Analysis Report

**Date**: [today]
**Feedback analyzed**: [count] responses
**Source**: [NPS survey / app reviews / support tickets / etc.]
**Period**: [date range if available]

### Overall Sentiment
- Positive: [X%] | Neutral: [Y%] | Negative: [Z%]
- Average sentiment score: [X/10]
- Trend: [improving / stable / declining]

### Top Themes
| # | Theme | Mentions | Sentiment | Segments Most Affected |
|---|-------|----------|-----------|----------------------|

### Theme Deep-Dive
#### Theme 1: [Name] — [X] mentions, [sentiment]
- **What users are saying**: [summary with representative quotes]
- **Root cause**: [what's driving this feedback]
- **Impact**: [how this affects retention, satisfaction, or revenue]
- **Recommendation**: [what to do about it]
[Repeat for top 5-8 themes]

### Segment Analysis
| Segment | Volume | Avg Sentiment | Top Theme | Key Difference |
|---------|--------|-------------|-----------|---------------|

### Notable Quotes
> "[quote]" — [segment, sentiment]

### Trends Over Time
[If date data available: chart-ready data showing sentiment shifts]

### Actionable Insights
1. [Insight + recommended action]

### Gaps
[What this feedback doesn't tell you — suggested follow-up research]
```

## 保存指令

源要求存为 markdown 文档。若输入为结构化数据（CSV），同时另存带情感评分的富化 CSV。

## 下一步建议

- 是否要基于这些反馈模式创建用户画像？
- 是否要将头部主题作为功能请求做 triage？
- 是否要设计访谈提纲深挖某个主题？

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
