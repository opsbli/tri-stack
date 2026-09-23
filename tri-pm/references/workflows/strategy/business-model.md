---
name: business-model
description: 用 Lean Canvas、Business Model Canvas、Startup Canvas 或 Value Proposition 框架探索商业模式
source: pm-skills-main/pm-product-strategy/commands/business-model.md
domain: 战略
---

# /business-model → 商业模式探索

> 蒸馏自命令 `business-model`｜域：战略｜源词数：约 720
> **语法翻译**：源以 `/business-model` 斜杠调用；本环境以下「工作流步骤」即等价编排，由 Agent 按步执行。

## 用途

用四个互补框架构建并分析商业模式，可单选或全跑以获得完整图景。

## 参数提示

`[lean|full|startup|value-prop] <product or business>`（模式 + 产品/业务；留空则 Agent 询问需求）

## 调用示例（翻译为对话形态）

- 源：`/business-model lean Marketplace connecting freelance PMs with startups`
- 本环境等价说法：「用 Lean Canvas 为『连接自由 PM 与初创公司的交易平台』建模」
- 源：`/business-model all SaaS onboarding tool`
- 本环境等价说法：「对『SaaS 入职工具』跑全部四种商业模式框架并做综合」

## 工作流步骤

1. **收集上下文** — 追问：产品/商业点子？阶段（想法/已验证/规模化）？有无现有模式要打磨？目标客户是谁？
2. **生成所选框架**（按模式引用对应技能）：
   - **Lean 模式**（早期/初创）〔引用：`**lean-canvas**`〕：产出 9 格 Lean Canvas + Riskiest Assumptions + Experiments。
   - **Full BMC 模式**（成熟/战略/融资）〔引用：`**business-model**`〕：产出 9 构件 BMC + Analysis（强弱、如何互相强化、脆弱与依赖）。
   - **Startup 模式**（新产品，推荐）〔引用：`**startup-canvas**`〕：产出 9 段战略 + 成本结构/收入流 + Strategy Coherence Check + Riskiest Assumptions。
   - **Value-Prop 模式**（打磨文案/PMF）〔引用：`**value-proposition**`〕：产出 6 段 JTBD 价值主张 + Value Proposition Statement。
   - **All 模式**：跑全部四框架并加综合段，对比跨框架洞察。
3. **保存与迭代** — 存为 markdown，建议下一步：用 SWOT/PESTLE 压力测试？为收入流设计定价？据此建战略画布？识别滩头细分？

## Checkpoint

> （源未设 checkpoint）

## 输出模板

各模式模板见对应框架文件（`lean-canvas.md` / `business-model.md` / `startup-canvas.md` / `value-proposition.md`）。Startup 模式骨架：

```markdown
## Startup Canvas: [Product]
### Part 1: Product Strategy
| Vision | Market Segments | Relative Costs |
| [inspiring why] | [JTBD, first segment] | [low cost vs unique value] |
| Value Proposition | Trade-offs | Key Metrics |
| [What before→How→What after→Alternatives] | [what you won't do] | [North Star+OMTM] |
| Growth | Capabilities | Can't/Won't |
| [PLG vs Sales-Led, channels] | [build vs partner] | [why competitors can't copy] |
### Part 2: Business Model
| Cost Structure | Revenue Streams |
| [fixed+variable, how scale] | [pricing model, revenue/channel] |
### Strategy Coherence Check / Riskiest Assumptions
```

## 保存指令

保存为 markdown（建议 `Business-Model-[product].md`）。

## 下一步建议

- 用 SWOT 或 PESTLE 压力测试该模式
- 为收入流设计定价策略
- 围绕该模式构建战略画布
- 识别滩头（beachhead）细分

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
