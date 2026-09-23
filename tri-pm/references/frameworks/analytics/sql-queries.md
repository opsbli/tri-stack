---
name: sql-queries
description: 将自然语言需求转换为跨数据库平台的优化 SQL 查询——支持 BigQuery、PostgreSQL、MySQL 等多方言，可读取上传的 schema 文件。
source: pm-skills-main/pm-data-analytics/skills/sql-queries/SKILL.md
domain: 分析
---

# SQL 查询生成器（sql-queries）

> 蒸馏自 `sql-queries`｜域：分析｜源词数：~470

## 必含章节清单（MUST-SECTIONS）

- [ ] Purpose — 用途
- [ ] How It Works — 工作机制（Step 1–4）
- [ ] Usage Examples — 使用示例（Example 1–3）
- [ ] Key Capabilities — 关键能力
- [ ] Tips for Best Results — 最佳实践提示
- [ ] Output Format — 输出格式

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Further Reading — 延伸阅读（见下方：已按规格丢弃）

## 逐段引导问题

- **Purpose**：把自然语言需求转成跨平台 SQL，帮助 PM / 分析师 / 工程师免于手工写语法。
- **How It Works / Step 1（理解数据库 schema）**：是否提供了 schema 文件（SQL、文档或图表描述）？需提取表名、列定义、数据类型、关系，并识别主键、外键、索引策略。
- **How It Works / Step 2（处理请求）**：要检索或分析的确切数据是什么？确认 SQL 方言（BigQuery、PostgreSQL、MySQL、Snowflake 等）；是否还有补充要求（过滤、聚合、排序）？
- **How It Works / Step 3（生成优化查询）**：是否写出利用库结构的 SQL？是否加注释解释复杂逻辑？是否给出大数据集的性能考量与替代方案？
- **How It Works / Step 4（解释与测试）**：是否用平实语言解释逻辑？是否给出验证方法？是否提供性能优化建议？是否按需生成测试脚本或样本数据？
- **Usage Examples**：是否基于 schema 文件 / 图表描述 / 复杂分析（如按区域与客户层级分析营收并含同比）来生成查询？
- **Tips for Best Results**：是否提供上下文、是否明确数据、是否说明所用数据库方言、是否包含约束（数据量/时间范围/性能）、是否要求了输出格式？

## 输出模板

```markdown
**SQL Query**：生产可用的带注释 SQL 代码
**Explanation**：查询做什么、如何工作
**Performance Notes**：优化提示与注意事项
**Test Script**（按需）：样本数据与验证查询
```

## 输出命名规则

源文件未规定

## 关键规则

- **多方言支持**：源 Key Capabilities 原文列明支持 BigQuery、PostgreSQL、MySQL、Snowflake、SQL Server；Step 2 明确要求先确认所用方言（BigQuery、PostgreSQL、MySQL、Snowflake 等）。
- **文件读取**：可读取 schema 文件、SQL dump、数据文档。
- **查询优化**：建议索引、分区、性能改进。
- **解释**：拆解查询以便学习与归档。
- **测试**：可按需生成测试查询与样本数据脚本。
- **脚本执行**：为数据库创建可执行 SQL 脚本。
- **最佳实践（Tips，5 条，照抄）**：① 提供上下文——分享 schema 或结构；② 具体——清晰描述所需数据与任何过滤；③ 提及数据库——说明所用 SQL 方言；④ 包含约束——提及数据量、时间范围、性能需求；⑤ 要求格式——若需特定输出，请求查询结果的格式。

## Checkpoint

（源未设 checkpoint）

## Further Reading

（源提供的 Further Reading 全部指向 productcompass.pm newsletter，含订阅 CTA 与「upgrade for full access」付费墙提示，违反规格纪律 #7「无 CTA、非付费墙」，已全部丢弃，宁缺毋滥）
