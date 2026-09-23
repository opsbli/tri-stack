---
name: analyze-cohorts
description: 按队列分析用户留存与参与模式——留存曲线、功能采纳趋势与可执行洞察，可上传数据或描述需求。
source: pm-skills-main/pm-data-analytics/commands/analyze-cohorts.md
domain: 分析
---

# /analyze-cohorts → 队列分析

> 蒸馏自命令 `analyze-cohorts`｜域：分析｜源词数：~410
> **语法翻译**：源项目以 `/analyze-cohorts` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

按队列分析用户留存与参与模式。上传数据或描述需求，得到留存曲线、功能采纳趋势与可执行洞察。

## 参数提示

`<data file or description of what to analyze>`（数据文件，或想分析的内容描述）

## 调用示例（翻译为对话形态）

- 源：`/analyze-cohorts [upload a CSV of user activity data]`
- 本环境等价说法：「（上传一份用户活跃数据 CSV）帮我做队列分析」
- 源：`/analyze-cohorts Monthly retention for users who signed up in Jan-Jun, grouped by acquisition channel`
- 本环境等价说法：「按获客渠道分组，分析 1–6 月注册用户的月度留存」
- 源：`/analyze-cohorts Help me set up a cohort analysis for our onboarding redesign`
- 本环境等价说法：「帮我们为 onboarding 改版搭一套队列分析方案」

## 工作流步骤

1. **接收数据或定义分析** — 两条路径：有数据（用户上传含 user_id、signup_date、activity_date、event_type 等的用户级 CSV/表格）；无数据（用户描述需求 → 生成 SQL 查询与分析框架）〔引用技能：`**cohort-analysis**`〕
2. **定义队列** — 询问：队列由什么定义（注册周/月、获客渠道、套餐层级、首次使用的功能）？留存事件是什么（登录、核心动作、任意活跃、购买）？时间粒度（日/周/月）？时间范围？〔引用技能：`**cohort-analysis**`〕
3. **分析** — 应用 `**cohort-analysis**` 技能：有数据时用 Python(pandas) 建队列表、算各周期留存率、生成留存曲线、识别改善/衰退/季节性/异常模式、跨队列比较功能采纳；仅描述时则设计框架、生成 SQL、做分析模板表、定义指标与可视化方式。
4. **生成报告** — 按输出模板产出；若提供了数据，同时存为 markdown 报告与 CSV/表格。
5. **提议下一步** — 是否按另一维度进一步分群、是否基于留存阈值设指标告警、是否设计实验改善最弱队列的留存。

## Checkpoint

（源未设显式 checkpoint）

## 输出模板

```markdown
## Cohort Analysis: [Description]

**Date**: [today]
**Cohort definition**: [e.g., signup month]
**Retention event**: [e.g., completed a project]
**Granularity**: [weekly/monthly]

### Retention Table
| Cohort | Size | Week 1 | Week 2 | Week 3 | ... | Week 12 |
|--------|------|--------|--------|--------|-----|---------|

### Key Findings
1. **[Finding]** — [supporting data]
2. ...

### Cohort Comparison
- **Best-performing cohort**: [which, why]
- **Worst-performing cohort**: [which, why]
- **Trend**: [improving/declining/stable over time]

### Retention Benchmarks
| Period | Your Rate | Industry Benchmark | Gap |
|--------|----------|-------------------|-----|

### Recommendations
1. [What to investigate or change based on findings]
2. ...

### Follow-Up Queries
[SQL queries for deeper investigation]
```

## 保存指令

若用户提供数据：分析同时保存为 **markdown 报告**与 **CSV/表格**。

## 下一步建议

- 是否要按另一维度**进一步分群**
- 是否要基于留存阈值**设置指标告警**
- 是否要为最弱队列设计**改善留存的实验**

## Further Reading

（源未提供独立 Further Reading；源 README 中的斜杠调用已按规格翻译为对话形态，不作为可执行命令保留）

## 关键注意事项（Notes 照抄）

- 队列分析的质量取决于留存事件定义——要推动「有意义的行为」，而非仅「登录」。
- 早期队列常因种子用户偏差而不同——对比时注明。
- 若用 Python 脚本算留存，保存脚本以便用户用新数据复跑。
- 季节性效应会伪装成趋势——若队列差异可能由日历驱动，须标出。
