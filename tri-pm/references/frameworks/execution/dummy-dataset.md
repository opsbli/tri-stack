---
name: dummy-dataset
description: 生成逼真虚拟数据集用于测试——可定制列、约束与输出格式（CSV/JSON/SQL/Python 脚本）。
source: pm-skills-main/pm-execution/skills/dummy-dataset/SKILL.md
domain: 执行
---

# 虚拟数据集生成（dummy-dataset）

> 蒸馏自 `dummy-dataset`｜域：执行｜源词数：≈620

## 必含章节清单（MUST-SECTIONS）

- [ ] Dataset Specification — 类型、列（名/类型/值域）、行数、约束
- [ ] Output Format — CSV / JSON / SQL INSERT / Python 脚本（四选输出）
- [ ] Generated Data — 可执行脚本或直接数据文件
- [ ] Validation — 数据质量与约束合规
- [ ] Documentation — 生成逻辑说明与快速上手

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] （无）

## 逐段引导问题

- **Type**：数据域（客户反馈/交易/用户档案等）。
- **Columns**：列名、数据类型、值范围。
- **Rows**：样本量（默认 100）。
- **Format**：CSV/JSON/SQL/Python。
- **Constraints**：业务逻辑与关系（唯一 ID、外键、时间有序、分布）。
- **Realistic**：数据像真而非随机串；执行并产出文件。

## 输出模板

```markdown
## Generated Dataset: [Description]
**Rows**: [count] | **Columns**: [list] | **Format**: [CSV/JSON/SQL/Python]
### Schema
| Column | Type | Constraints | Distribution |
### Sample (first 5 rows)
[preview]
### Files
- [data file] / [generator script]
```

## 输出命名规则

源文件未规定（保存数据文件与生成脚本至工作区）

## 关键规则

- 始终提供生成脚本以便不同参数重现
- demo 数据要讲故事（季节趋势、留存问题、高价值用户段）
- 真实基数：1000 用户不会对应 1000 个独立城市
- 财务数据用真实价格分布，非均匀随机
- 绝不含真实个人数据——姓名/邮箱/标识须全假

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- （源未提供 Further Reading 或全部不合规，已丢弃）
