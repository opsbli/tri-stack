---
name: plan-okrs
description: 构思与团队/公司战略对齐的团队级 OKR——定性目标 + 可量化关键结果。
source: pm-skills-main/pm-execution/commands/plan-okrs.md
domain: 执行
---

# /plan-okrs → 团队 OKR 规划

> 蒸馏自命令 `plan-okrs`｜域：执行｜源词数：≈530
> **语法翻译**：源项目以 `/plan-okrs` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

生成连接团队工作与公司战略的 OKR，产出 3 套含定性目标与定量关键结果的方案。

## 参数提示

`<team, product area, or company objective>`（亦接受上传公司 OKR/战略文档）

## 调用示例（翻译为对话形态）

- 源：`/plan-okrs Growth team Q2 — company goal is 50% ARR increase`
- 本环境等价说法：「增长团队 Q2 OKR，公司目标是 ARR 增 50%」
- 源：`/plan-okrs [upload company OKRs]`
- 本环境等价说法：「我上传公司 OKR，据此拟团队 OKR」

## 工作流步骤

1. **收集上下文** — 问：哪团队/产品域？周期？（季度标准，亦年/自定义）对齐的公司级目标？上季度得失？约束/已知优先级？接受上传文档。
2. **生成 OKR**〔引用技能：`**brainstorm-okrs**`〕— 3 套（Objective + 3-5 KR）：
   - Objective：定性、激励、有雄心但可达、行动导向
   - KR：定量、可测、时间限、有负责人
   - 可见 ladder 到公司目标；平衡先行（活动）与滞后（结果）指标
3. **校验质量** — 逐条查：Objective 激励？KR 可测？目标有雄心不泄气（70% 达成=校准良好）？每 Objective 3-5 KR？KR 防博弈（如「上线 5 功能」诱出 junk）？
4. **呈现迭代** — 输出团队 OKR 结构（见模板），含 Alignment Map、Scoring Guide、Check-in Cadence。主动提议：调雄心、建指标看板、写干系人更新。

## Checkpoint

> **Step 3 后**："Are targets ambitious but not demoralizing? (70% achievement = well-calibrated)" — 目标有雄心但不泄气（70% 达成=校准良好）。

## 输出模板

```markdown
## Team OKRs: [Team] — [Period]
**Aligned to**: [Company Objective(s)]
### Objective 1: [Inspiring statement]
| # | Key Result | Baseline | Target | Owner |
### Objective 2 / 3: [same]
### Alignment Map: Company → Team → KR → Impact
### Scoring Guide: 0.0-0.3 miss / 0.4-0.6 short / 0.7-0.9 calibrated / 1.0 nailed
### Check-in Cadence: Weekly / Mid-quarter / End-of-quarter
```

## 保存指令

源文件未规定（内容充实时保存 markdown）

## 下一步建议

- 「要我调整雄心级别——更激进或更温和？」
- 「要我为这些建指标看板？」
- 「要我起草一份干系人更新介绍这些 OKR？」

## Further Reading

- [Objectives and Key Results (OKRs) 101](https://www.productcompass.pm/p/okrs-101-advanced-techniques)
- [OKR vs KPI: What's the Difference?](https://www.productcompass.pm/p/okr-vs-kpi-whats-the-difference)
