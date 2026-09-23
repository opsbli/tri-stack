---
name: stakeholder-map
description: 用权力×利益矩阵绘制干系人地图并创建定制沟通计划。
source: pm-skills-main/pm-execution/commands/stakeholder-map.md
domain: 执行
---

# /stakeholder-map → 干系人地图与沟通计划

> 蒸馏自命令 `stakeholder-map`｜域：执行｜源词数：≈490
> **语法翻译**：源项目以 `/stakeholder-map` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

识别项目所有干系人，按影响力与利益映射，生成确保正确的人在正确时间获正确信息的沟通计划。

## 参数提示

`<project, initiative, or launch>`（亦接受上传项目 brief/组织图）

## 调用示例（翻译为对话形态）

- 源：`/stakeholder-map New analytics platform launch`
- 本环境等价说法：「为新分析平台上线做干系人地图」
- 源：`/stakeholder-map Pricing model change affecting all customers`
- 本环境等价说法：「定价模型变更影响所有客户，做干系人地图」

## 工作流步骤

1. **理解举措** — 问：项目是什么？阶段？（规划/构建/发布/后发布）已知干系人？政治敏感动态？
2. **识别干系人** — 头脑风暴易漏者：内部（工程/设计/QA/数据/法务/财务/市场/销售/支持/领导）、外部（客户/伙伴/供应商/监管/董事会）、常漏（相邻团队/值班工程/客户成功/文档）。
3. **映射矩阵**〔引用技能：`**stakeholder-map**`〕— 每干系人落象限：Manage Closely（高权高益）/ Keep Satisfied（高权低益）/ Keep Informed（低权高益）/ Monitor（低权低益）。
4. **生成计划** — 输出 Stakeholder Map（Grid、分象限 Communication Plan、Potential Conflicts、Escalation Path、RACI）。保存 markdown。
5. **下一步** — 提议：为 Manage Closely 起草首份更新、建会议准备简报、设沟通节奏。

## Checkpoint

> **Step 3 后**："The 'Manage Closely' quadrant is where PMs spend most political capital — get these relationships right" — Manage Closely 象限是 PM 政治资本主投处，关系须做对。

## 输出模板

```markdown
## Stakeholder Map: [Initiative]
### Stakeholder Grid | ### Communication Plan (4 quadrants) | ### Potential Conflicts | ### Escalation Path | ### RACI Matrix
```

## 保存指令

保存为 markdown

## 下一步建议

- 「要为 Manage Closely 组起草首份干系人更新吗？」
- 「要为关键干系人对话建会议准备简报吗？」
- 「要把沟通节奏设为周期清单吗？」

## Further Reading

- [The Product Management Frameworks Compendium + Templates](https://www.productcompass.pm/p/the-product-frameworks-compendium)
- [Team Topologies: A Handbook to Set and Scale Product Teams](https://www.productcompass.pm/p/team-topologies-a-handbook-to-set)
