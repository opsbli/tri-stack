---
name: red-team-prd
description: 对 PRD/路线图/战略做红队对抗——攻击其承重假设，给出每个最便宜测试。
source: pm-skills-main/pm-execution/commands/red-team-prd.md
domain: 执行
---

# /red-team-prd → 在现实之前攻击计划

> 蒸馏自命令 `red-team-prd`｜域：执行｜源词数：≈480
> **语法翻译**：源项目以 `/red-team-prd` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

找出会让计划失败的假设，诚实攻击，并给出每个最便宜测试——让你本周就能毙掉坏注，而非等到发布。

## 参数提示

`<PRD, roadmap, strategy, or the current doc>`

## 调用示例（翻译为对话形态）

- 源：`/red-team-prd [paste a PRD]`
- 本环境等价说法：「对我这份 PRD 做红队对抗」
- 源：`/red-team-prd Prioritize AI onboarding — activation is our bottleneck`
- 本环境等价说法：「红队对抗：优先级 AI onboarding，激活是瓶颈」
- 源：`/red-team-prd the current doc`
- 本环境等价说法：「对当前文档做红队对抗」

## 工作流步骤

1. **接受计划** — 任意形态：PRD、路线图、战略 memo、一句话赌注、上传文档。说「当前文档」则用上下文中的文档。
2. **红队攻击**〔引用技能：`**strategy-red-team**`〕— 提取每断言，仅留承重（假→计划死）；钢化每个再攻钢人；写「Fails if ___」；按 (impact×likelihood×cheapness) 排序；默认风险真实除非计划已引反驳证据，但显式说严谨处，绝不编造弱点。
3. **返回输出** — 见模板（Top Kill-Assumptions 3-5、What's Well-Reasoned、What I Couldn't Assess）。
4. **下一步** — 提议：把顶部假设变成本周实验、补跑事前复盘、重写最险段。

## Checkpoint

> **Step 2 后**："Five real kill-assumptions with tests beat twenty generic risks. Cut ruthlessly." — 5 个带测试的真实击杀假设胜过 20 个泛化风险，无情删减。

## 输出模板

```markdown
## Red-Team: [plan in one line]
### Top Kill-Assumptions (ranked)
- **Claim:** [load-bearing]  **Fails if:** [falsifiable]  **Evidence to get this week:** [specific]  **Kill criterion:** [threshold]  **Cheapest test:** [smallest]
### What's Well-Reasoned: [explicit, no manufactured doubt]
### What I Couldn't Assess: [gaps]
```

## 保存指令

源文件未规定（输出为红队报告）

## 下一步建议

- 「要把顶部击杀假设变成本周可跑实验吗？」
- 「要补跑事前复盘互补吗？」
- 「要重写计划中存活下来的最险段吗？」

## Further Reading

- [Assumption Prioritization Canvas: How to Identify And Test The Right Assumptions](https://www.productcompass.pm/p/assumption-prioritization-canvas)
- [How to Manage Risks as a Product Manager](https://www.productcompass.pm/p/how-to-manage-risks-as-a-product-manager)
