---
name: generate-data
description: 生成逼真虚拟数据集用于测试——CSV/JSON/SQL/Python 脚本。
source: pm-skills-main/pm-execution/commands/generate-data.md
domain: 执行
---

# /generate-data → 测试数据生成器

> 蒸馏自命令 `generate-data`｜域：执行｜源词数：≈480
> **语法翻译**：源项目以 `/generate-data` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

为开发、测试、演示或原型创建逼真虚拟数据集，以偏好格式输出即用文件。

## 参数提示

`<description of the data you need>`（亦接受粘贴表定义）

## 调用示例（翻译为对话形态）

- 源：`/generate-data 1000 users with names, emails, plan tier, signup date, activity score`
- 本环境等价说法：「生成 1000 用户，含姓名/邮箱/套餐/注册日/活跃分」
- 源：`/generate-data E-commerce orders dataset: products, customers, timestamps, amounts`
- 本环境等价说法：「生成电商订单数据集：产品/客户/时间戳/金额」

## 工作流步骤

1. **定义数据集** — 理解：实体？列（类型/约束）？行数？表间关系？分布（如「80% 免费套餐」）？真实约束（邮箱唯一、日期有序）？
2. **生成数据**〔引用技能：`**dummy-dataset**`〕— 建 Python 脚本生成；用逼真数据（真名/有效邮箱/真日期）；守约束（唯一 ID、外键、时序）；应用分布；执行产出文件。
3. **交付** — 按请求格式输出（或问）：CSV（通用）、JSON（API/前端）、SQL INSERT（填库）、Python 脚本（可重现）。保存数据文件与生成脚本至工作区。
4. **下一步** — 提议：加列/扩量、建关联表、写测这些数据的场景、建分析 SQL。

## Checkpoint

> **Step 2 后**："Never include real personal data — all names, emails, and identifiers must be fake" — 绝不含真实个人数据，姓名/邮箱/标识须全假。

## 输出模板

```markdown
## Generated Dataset: [Description]
**Rows** / **Columns** / **Format**
### Schema: | Column | Type | Constraints | Distribution |
### Sample (first 5 rows)
### Files: [data file] / [generator script]
```

## 保存指令

保存数据文件与生成脚本至用户工作区

## 下一步建议

- 「要加列或扩数据集吗？」
- 「要建关联表（如这些用户的订单）吗？」
- 「要写测这些数据的场景吗？」
- 「要建分析此数据集的 SQL 吗？」

## Further Reading

- （源未提供 Further Reading 或全部不合规，已丢弃）
