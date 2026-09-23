---
name: growth-strategy
description: 设计可持续增长机制——增长闭环与 GTM 动议，用于产品驱动与销售驱动策略
source: pm-skills-main/pm-go-to-market/commands/growth-strategy.md
domain: 上市
---

# /growth-strategy → 增长战略（Growth Loops & GTM Motions）

> 蒸馏自命令 `growth-strategy`｜域：上市｜源词数：约 480
> **语法翻译**：源项目以 `/growth-strategy` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

识别并设计驱动可持续牵引的增长机制。评估 5 类增长闭环与 7 类 GTM 动议，构建平衡的获客与扩张战略。

## 参数提示

（源 `argument-hint`：`<product or growth challenge>`——产品或增长挑战）

## 调用示例（翻译为对话形态）

- 源：`/growth-strategy B2B collaboration tool — growth has stalled at 5K users`
- 本环境等价说法：「B2B 协作工具卡在 5K 用户了，帮我做增长战略」
- 源：`/growth-strategy Consumer fitness app looking for viral growth`
- 本环境等价说法：「消费级健身 App 想做病毒增长，帮我设计」
- 源：`/growth-strategy [upload product metrics or growth data]`
- 本环境等价说法：「（上传产品指标或增长数据）据此设计增长战略」

## 工作流步骤

1. **Understand Growth Context（理解增长背景）** — 〔引用技能：无，纯澄清〕
   - 产品是什么？谁用？当前增长指标：用户数、增速、获客渠道。
   - 什么有效？什么无效？商业模式：营收如何与用户增长挂钩？团队与预算？
2. **Evaluate Growth Loops（评估增长闭环）** — 〔引用技能：**growth-loops**〕
   - 分析 5 类：Viral（自然使用中邀请）、Usage（更多使用创造更多价值并回流）、Collaboration（与他人的协作让产品更有价值）、User-Generated Content（创作内容吸引新用户）、Referral（满意用户主动推荐）。
   - 每类适用闭环：机制、要求、预期影响、实施 effort。
3. **Evaluate GTM Motions（评估 GTM 动议）** — 〔引用技能：**gtm-motions**〕
   - 评估 7 类：Inbound（内容/SEO/思想领导）、Outbound（销售/冷触达/ABM）、Paid Digital（SEM/社媒/展示/再营销）、Community（论坛/活动/用户组/开发者关系）、Partners（集成/经销商/联合营销）、ABM（定向企业获客）、PLG（免费层/自助/产品病毒）。
   - 每类：产品契合度、预期 CAC、见效时间线、所需工具。
4. **Design Growth Strategy（设计增长战略）** — 输出下方模板〔引用技能：无，落盘〕
   - 含推荐闭环表、主/次闭环详述、GTM 动议组合、增长实验、指标框架、90 天计划。
5. **Offer Next Steps（建议下一步）** — 〔引用技能：无〕
   - 是否规划具体发布战役？是否为入站动议创作营销内容？是否建指标追踪闭环健康？是否基于推荐闭环设计推荐计划？

## Checkpoint

> （源未设 checkpoint；Step 2–3 后分别调用对应 skill 即隐含验收点）

## 输出模板

```markdown
## Growth Strategy: [产品]

**Date**: [今天]
**Current state**: [用户数、增速、关键渠道]
**Growth goal**: [目标]

### Recommended Growth Loops
| Loop Type | Mechanism | Fit | Impact | Effort | Priority |
|----------|-----------|-----|--------|--------|----------|

### Primary Growth Loop: [类型]
**How it works**: [逐步机制]
**Requirements**: [需成立/需构建]
**Key metrics**: [度量闭环健康]
**Implementation plan**: [具体下一步]

### Secondary Growth Loop: [类型]
[同上]

### GTM Motion Mix
| Motion | Investment | Expected ROI | Timeline | Tools |
|--------|-----------|-------------|----------|-------|

### Growth Experiments
| # | Experiment | Tests What | Effort | Expected Learning |
|---|-----------|-----------|--------|------------------|

### Growth Metrics Framework
- **North Star**: [增长指标]
- **Loop health**: [每闭环指标]
- **CAC by channel**: [追踪方式]
- **Payback period**: [目标]

### 90-Day Growth Plan
**Month 1**: [重点与实验]
**Month 2**: [扩量有效、砍掉无效]
**Month 3**: [优化与系统化]
```

## 保存指令

保存为 markdown（源要求 Save as markdown；未规定具体文件名）。

## 下一步建议

- 「要我规划具体发布战役吗？」
- 「要我为入站动议创作营销内容吗？」
- 「要我建指标追踪增长闭环健康吗？」
- 「要我基于推荐闭环设计推荐计划吗？」

## Further Reading

（源命令未提供 Further Reading，已丢弃）
