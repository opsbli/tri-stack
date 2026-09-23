---
name: value-proposition
description: 用六段式 JTBD 模板设计清晰有力的价值主张
source: pm-skills-main/pm-product-strategy/commands/value-proposition.md
domain: 战略
---

# /value-proposition → 价值主张设计

> 蒸馏自命令 `value-proposition`｜域：战略｜源词数：约 360
> **语法翻译**：源以 `/value-proposition` 斜杠调用；本环境以下「工作流步骤」即等价编排，由 Agent 按步执行。

## 用途

用六段式 JTBD 模板为产品或功能设计清晰、有说服力的价值主张（替代 Strategyzer 画布，从客户出发、聚焦实际结果）。

## 参数提示

`<product or feature>`（产品名或功能；留空则 Agent 追问产品信息）

## 调用示例（翻译为对话形态）

- 源：`/value-proposition AI writing tool for non-native English speakers`
- 本环境等价说法：「为非英语母语者的 AI 写作工具设计价值主张」
- 源：`/value-proposition [upload pitch deck, PRD, or competitive analysis]`
- 本环境等价说法：「我上传 Pitch/PRD/竞品分析，请据此提炼价值主张」

## 工作流步骤

1. **理解产品与市场** — 接受产品描述、上传文档、或现有价值主张。追问：做什么、服务谁？现有替代/绕过方案？有哪些客户洞察/研究？
2. **构建价值主张** — 〔引用技能：`**value-proposition**`〕产出 6 段模板：①Who 目标用户 ②Why JTBD ③What Before 现状痛点 ④How 方案 ⑤What After 改善结果 ⑥Alternatives 替代方案与优势。多细分则各写一份。附 Value Proposition Statement（一句式）及可复用文案（营销/销售/入职）。
3. **保存与下一步** — 存为 markdown，建议：用 Value Curve 对比竞品？围绕此价值主张建完整战略？据此建 Lean/Startup Canvas？据此生成营销文案？

## Checkpoint

> （源未设 checkpoint）

## 输出模板

```markdown
## Value Proposition: [Product]
### For [Segment]:
1. **Who**: [用户画像]
2. **Why**: [JTBD, 期望结果]
3. **What Before**: [现状痛点——现有工具/摩擦/绕过]
4. **How**: [方案——具体功能与能力]
5. **What After**: [改善结果——变得可能的事]
6. **Alternatives**: [无你时的替代方案，及你更优之处]

### Value Proposition Statement
[一句：For [who] who [need], [product] is a [category] that [benefit]. Unlike [alternative], we [differentiator].]

### Value Proposition Statements (Reusable)
- Marketing: [...]  - Sales: [...]  - Onboarding: [...]
```

## 保存指令

保存为 markdown（建议 `Value-Proposition-[product].md`）。

## 下一步建议

- 用 Value Curve（蓝海战略）与竞品可视化对比
- 围绕该价值主张构建完整战略（见 strategy 工作流步骤）
- 据此创建 Lean Canvas 或 Startup Canvas
- 从这些价值主张陈述生成营销文案

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
