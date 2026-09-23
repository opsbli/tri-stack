---
name: sprint-plan
description: 规划冲刺——估算团队产能、遴选与排序故事、绘制依赖、识别风险。
source: pm-skills-main/pm-execution/skills/sprint-plan/SKILL.md
domain: 执行
---

# 冲刺规划（sprint-plan）

> 蒸馏自 `sprint-plan`｜域：执行｜源词数：≈420

## 必含章节清单（MUST-SECTIONS）

- [ ] Sprint Goal — 一句话成功描述
- [ ] Duration — 周期（2 周 / 1 周）
- [ ] Team Capacity — 可用产能（故事点）
- [ ] Committed Stories — 承诺故事（Y 点 / Z 条）
- [ ] Buffer — 剩余缓冲产能
- [ ] Stories — 故事列表（标题/点/负责人/依赖）
- [ ] Risks — 风险与缓解

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] （无）

## 逐段引导问题

- **Capacity**：成员数与可用性（PTO/会议/值班）？历史速度（近 3 冲刺均值）？预留 15-20% 缓冲。
- **Select**：从高优先级 backlog 拉取；核验 Definition of Ready（清晰 AC、已估算、无阻塞）；到产能即停。
- **Dependencies**：识别依赖与关键路径；外部依赖标负责人。
- **Risks**：高不确定性/复杂度、可能滑点的外部依赖、知识集中（仅一人能做）。

## 输出模板

```markdown
Sprint Goal: [one sentence]
Duration: [2 weeks]
Team Capacity: [X story points]
Committed Stories: [Y pts across Z stories]
Buffer: [remaining]

Stories:
1. [Story] — [pts] — [owner] — [deps]
Risks:
- [Risk] → [Mitigation]
```

## 输出命名规则

源文件未规定（save as markdown）

## 关键规则

- 产能缓冲预留 15-20% 应对突发/bug/技术债
- 故事须达 Definition of Ready 方可承诺
- 冲刺目标为单一清晰句，概括主要价值交付

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- [Product Owner vs Product Manager: What's the difference?](https://www.productcompass.pm/p/product-manager-vs-product-owner)
