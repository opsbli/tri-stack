---
name: strategy-red-team
description: 对 PRD/路线图/战略做红队对抗——攻击其承重假设，按 影响×可能×测试成本 排序，给出最便宜测试与终止标准。
source: pm-skills-main/pm-execution/skills/strategy-red-team/SKILL.md
domain: 执行
---

# 战略红队对抗（strategy-red-team）

> 蒸馏自 `strategy-red-team`｜域：执行｜源词数：≈600

## 必含章节清单（MUST-SECTIONS）

- [ ] Top Kill-Assumptions — 排名后的承重假设（3-5 个）
- [ ] What's Well-Reasoned — 经得起推敲的部分（显式说明）
- [ ] What I Couldn't Assess — 计划未给足信息无法判断的缺口

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] （无）

## 逐段引导问题 / 对抗步骤（照抄口径）

1. **Extract every claim**：列出计划断言为真者（用户/市场/约束/机制/时间）；区分承重 claims（假→计划死）与装饰性。
2. **Steelman, then attack**：先写最强成立理由，再攻击该强理由——非稻草人。
3. **Write "Fails if ___"**：具体可证伪。「Fails if 激活并非真正约束」优于「执行风险」。
4. **Rank by (impact if wrong) × (likelihood wrong) × (cheapness to test)**：本周该测的排最前。
5. **Self-refute, don't fabricate**：默认「风险真实」除非计划已引证据反驳；但真严谨就说清楚，绝不编造弱点。
6. **For each surviving kill-assumption 给可执行项**：Fails if / Evidence to get this week / Kill criterion / Cheapest test。
7. **可选跨模型**：用户要求且另一模型可达才做，默认单模型。
8. **Structure output**（见模板）。

## 输出模板

```markdown
## Red-Team: [plan in one line]
### Top Kill-Assumptions (ranked)
For each (3–5 max):
- **Claim:** [load-bearing assertion]
- **Fails if:** [concrete, falsifiable condition]
- **Evidence to get this week:** [specific]
- **Kill criterion:** [threshold]
- **Cheapest test:** [smallest experiment]
### What's Well-Reasoned
[State explicitly what holds up — don't manufacture doubt.]
### What I Couldn't Assess
[Gaps where the plan didn't give enough to judge.]
```

## 输出命名规则

源文件未规定（输出为红队报告，截图友好）

## 关键规则

- 无稻草人——攻击强理由或别攻击
- 无泛化风险清单——每条须针对本计划
- 无编造——严谨就说严谨
- 排序无情——最便宜高影响测试是重点
- 情绪价值是缓解「怕发错注」的恐惧，结尾给「做什么」

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- [Assumption Prioritization Canvas: How to Identify And Test The Right Assumptions](https://www.productcompass.pm/p/assumption-prioritization-canvas)
- [How to Manage Risks as a Product Manager](https://www.productcompass.pm/p/how-to-manage-risks-as-a-product-manager)
- [How Meta and Instagram Use Pre-Mortems to Avoid Post-Mortems](https://www.productcompass.pm/p/how-to-run-pre-mortem-template)
