---
name: pre-mortem
description: 对 PRD/发布计划做事前复盘风险分析——在失败前识别可能出错之处。
source: pm-skills-main/pm-execution/commands/pre-mortem.md
domain: 执行
---

# /pre-mortem → 发布前风险分析

> 蒸馏自命令 `pre-mortem`｜域：执行｜源词数：≈480
> **语法翻译**：源项目以 `/pre-mortem` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

想象发布已失败，倒推原因。用 Tigers/Paper Tigers/Elephants 框架浮现真实风险并制定缓解计划。

## 参数提示

`<PRD, plan, or feature description>`（亦接受上传文档）

## 调用示例（翻译为对话形态）

- 源：`/pre-mortem [paste a PRD]`
- 本环境等价说法：「我对这份 PRD 做事前复盘」
- 源：`/pre-mortem We're launching a self-serve billing portal next month`
- 本环境等价说法：「下月上线自助计费门户，做事前复盘」

## 工作流步骤

1. **接受计划** — 任意形态：PRD、功能 spec、发布计划、项目 brief、口头描述。越详细分析越锐。
2. **识别风险**〔引用技能：`**pre-mortem**`〕— 想象已发布且失败，跨类生成：Technical/User/Business/Operational/Dependencies。
3. **分类风险** — Tigers（真实，评 Launch-blocking/Fast-follow/Track）；Paper Tigers（吓人但夸大，说明可控）；Elephants（团队避谈的隐忧，建设性抛出）。
4. **生成报告** — 输出 Pre-Mortem（Risk Summary、Launch-Blocking/Fast-follow/Track 表、Paper Tigers、Elephants、Go/No-Go Checklist）。保存 markdown。
5. **下一步** — 提议：更新 PRD 加缓解、为最险处建测试场景、起草发布清单。

## Checkpoint

> **Step 3 后**："Elephants are the highest-value output — surfacing what the team avoids discussing" — 大象是最高价值产出，浮现团队避谈的真相。

## 输出模板

```markdown
## Pre-Mortem: [Feature/Launch]
**Risk Summary**: Tigers [n] / Paper Tigers [n] / Elephants [n]
### Launch-Blocking Tigers | Fast-Follow Tigers | Track Tigers
### Paper Tigers | Elephants in the Room
### Go/No-Go Checklist: [ ] all blocking mitigated / fast-follow assigned / monitoring / rollback / support briefed
```

## 保存指令

保存为 markdown

## 下一步建议

- 「要我把风险缓解更新进 PRD 吗？」
- 「要我为最危险处建测试场景吗？」
- 「要我据这些起草发布清单吗？」

## Further Reading

- [How Meta and Instagram Use Pre-Mortems to Avoid Post-Mortems](https://www.productcompass.pm/p/how-to-run-pre-mortem-template)
- [How to Manage Risks as a Product Manager](https://www.productcompass.pm/p/how-to-manage-risks-as-a-product-manager)
