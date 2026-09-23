---
name: write-query
description: 用自然语言生成 SQL 查询——支持 BigQuery、PostgreSQL、MySQL 等多方言，可读取上传的 schema。
source: pm-skills-main/pm-data-analytics/commands/write-query.md
domain: 分析
---

# /write-query → SQL 查询生成

> 蒸馏自命令 `write-query`｜域：分析｜源词数：~330
> **语法翻译**：源项目以 `/write-query` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

用平实语言描述所需数据，获取优化后的 SQL 查询。支持多方言，可从上传文件读取 schema。

## 参数提示

`<what you want to know, in plain English>`（你想知道的、用平实英语描述的请求）

## 调用示例（翻译为对话形态）

- 源：`/write-query Show me daily active users for the last 30 days, broken down by plan tier`
- 本环境等价说法：「帮我写查询：最近 30 天的日活用户，按套餐层级拆分」
- 源：`/write-query Find users who signed up last month but never completed onboarding`
- 本环境等价说法：「查一下上月注册但从未完成 onboarding 的用户」
- 源：`/write-query [upload a schema diagram] What's the conversion rate from trial to paid by cohort?`
- 本环境等价说法：「（上传一张 schema 图）按队列算 trial 到 paid 的转化率」

## 工作流步骤

1. **理解问题** — 解析用户的自然语言请求，识别：所请求的数据（指标、维度、过滤）、时间范围与粒度、分组与排序偏好、输出期望（原始/聚合/排名）〔引用技能：`**sql-queries**`〕
2. **确定 schema** — 若有 schema（上传的图、DDL 或描述）：映射到具体表与列、识别必要 join。若无 schema：询问数据库类型（BigQuery/PostgreSQL/MySQL 等）；从问题中推断合理 schema 并请用户确认；以常见 SaaS 数据模型约定为默认。
3. **生成查询** — 应用 `**sql-queries**` 技能：用正确方言写 SQL、优化可读性与性能、加注释解释关键逻辑、复杂查询用 CTE 提升可读性、处理边界情况（NULL、时区、去重）〔引用技能：`**sql-queries**`〕
4. **呈现与迭代** — 按输出模板输出，并主动提议：修改（加过滤/改分组/延长时间范围）、生成相关指标的配套查询、围绕该查询搭建看板、生成 cohort 分析版本。

## Checkpoint

（源未设显式 checkpoint）

## 输出模板

```markdown
## SQL Query: [What It Does]

**Dialect**: [BigQuery / PostgreSQL / MySQL / etc.]
**Tables used**: [list]

### Query
[SQL code block with comments]

### What This Returns
[Description of the output: columns, rows, expected result shape]

### Assumptions
- [Schema assumptions made]
- [Business logic assumptions]

### Notes
- [Performance considerations for large datasets]
- [Edge cases handled or flagged]
```

## 保存指令

源文件未规定落盘位置与命名（查询文本直接在对话中交付；可应要求写出可执行脚本）。

## 下一步建议

- 询问用户是否要**修改**（加过滤、改分组、延长时间范围）
- 是否要生成相关指标的**配套查询**
- 是否要围绕该查询**搭建看板**
- 是否需要该查询的 **cohort 分析版本**

## Further Reading

（源未提供独立 Further Reading；源 README 中的斜杠调用已按规格翻译为对话形态，不作为可执行命令保留）
