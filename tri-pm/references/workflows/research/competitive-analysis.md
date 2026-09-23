---
name: competitive-analysis
description: 分析竞争版图——识别竞品、对比优劣势、发现差异化机会
source: pm-skills-main/pm-market-research/commands/competitive-analysis.md
domain: 研究
---

# /competitive-analysis → 竞争版图分析

> 蒸馏自命令 `competitive-analysis`｜域：研究｜源词数：~700
> **语法翻译**：源项目以 `/competitive-analysis` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

研究并分析你的竞争版图。识别直接与间接竞品，绘制定位图，并挖掘差异化机会。

## 参数提示

`<your product or market>`（源 argument-hint）

## 调用示例（翻译为对话形态）

- 源：`/competitive-analysis AI-powered project management tools`
- 本环境等价说法：「帮我分析 AI 驱动的项目管理工具的竞争格局」
- 源：`/competitive-analysis Our product vs Notion, Asana, and Monday.com`
- 本环境等价说法：「分析我们的产品对比 Notion、Asana、Monday.com」
- 源：`/competitive-analysis [upload a competitor list or market brief]`
- 本环境等价说法：「这是我上传的竞品清单/市场简报，帮我做竞争分析」

## 工作流步骤

1. **理解竞争上下文** — 〔引用技能：无〕
   - 提问：你的产品是什么？竞争品类？有指定要分析的竞品吗，还是由我识别？视角是什么（功能对比/定位/定价/ GTM）？用于什么（战略/销售赋能/投资人 pitch/路线图）？

2. **识别竞品** — 应用 **competitor-analysis** 技能：〔引用技能：`**competitor-analysis**`〕
   - 识别 5 个直接竞品（同品类、同买家）；识别 2–3 个间接竞品（不同路径、同 JTBD）；如相关标注新兴/颠覆性玩家；用联网检索收集当前信息。

3. **逐个分析竞品** — 对每竞品：〔引用技能：`**competitor-analysis**`〕
   - **Positioning**：如何自我描述、目标受众、关键讯息
   - **Strengths**：擅长处、取胜处
   - **Weaknesses**：不足处、常见抱怨
   - **Pricing**：模式与价位（若公开）
   - **Market traction**：融资、团队规模、客户基数信号
   - **Recent moves**：新功能、合作、转向

4. **生成竞争分析** — 按下列模板输出「Competitive Analysis」。

5. **提供下一步** — 见「下一步建议」。

## Checkpoint

> （源未设 checkpoint）

## 输出模板

```markdown
## Competitive Analysis: [Your Product/Market]

**Date**: [today]
**Analyzed**: [count] competitors

### Market Overview
[2-3 sentences on market dynamics, trends, and where it's heading]

### Competitive Landscape
| Competitor | Category | Target | Positioning | Strength | Weakness |
|-----------|----------|--------|------------|----------|----------|

### Feature Comparison Matrix
| Capability | Your Product | Competitor A | Competitor B | Competitor C |
|-----------|-------------|-------------|-------------|-------------|

### Positioning Map
[2x2 matrix showing competitive positioning on key dimensions]

### Differentiation Opportunities
1. **[Opportunity]** — [why it's defensible and valuable]

### Competitive Threats
1. **[Threat]** — [what to watch for, recommended response]

### Recommendations
- **Double down on**: [your unique advantages]
- **Close the gap on**: [table-stakes features you're missing]
- **Ignore**: [competitor moves that aren't worth responding to]
```

## 保存指令

源要求存为 markdown 文档。

## 下一步建议

- 是否要为针对某竞品创建销售 battlecard？
- 是否要开发与头部竞品差异化的定位？
- 是否要识别需补齐的功能缺口加入路线图？

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
