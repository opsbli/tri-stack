---
name: plan-launch
description: 从第一性原理构建完整上市（GTM）计划——滩头细分、ICP、信息传达、渠道与发布计划
source: pm-skills-main/pm-go-to-market/commands/plan-launch.md
domain: 上市
---

# /plan-launch → 上市计划（Go-to-Market Strategy）

> 蒸馏自命令 `plan-launch`｜域：上市｜源词数：约 480
> **语法翻译**：源项目以 `/plan-launch` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

构建完整 GTM 计划：识别滩头市场、定义理想客户、打磨信息、选择渠道、制定发布时间线。

## 参数提示

（源 `argument-hint`：`<product or feature to launch>`——待发布的产品或功能）

## 调用示例（翻译为对话形态）

- 源：`/plan-launch AI-powered proposal writer for consulting firms`
- 本环境等价说法：「为咨询公司的 AI 提案写作工具做一份上市计划」
- 源：`/plan-launch New enterprise tier for our project management tool`
- 本环境等价说法：「给我们的项目管理工具做新企业版的发布计划」
- 源：`/plan-launch [upload a PRD, strategy doc, or pitch deck]`
- 本环境等价说法：「（上传 PRD / 战略文档 / 路演稿）帮我据此做上市计划」

## 工作流步骤

1. **Understand the Launch（理解发布）** — 提问〔引用技能：无，纯澄清〕
   - 发布什么？（新产品/功能/层级/市场扩张）
   - 阶段？（发布前规划 / 即将发布 / 发布后优化）
   - 已有客户还是从零开始？
   - 时间线？硬截止？
   - 预算约束？团队规模？
2. **Define Beachhead Segment（定义滩头细分）** — 〔引用技能：**beachhead-segment**〕
   - 按四标准评估潜在细分：痛点剧烈度、付费意愿、可赢份额、推荐潜力。
   - 推荐单一最佳首发细分并给理由；映射滩头后的相邻细分。
3. **Define Ideal Customer Profile（定义 ICP）** — 〔引用技能：**ideal-customer-profile**〕
   - 人口统计：公司规模、行业、地理、技术栈。
   - 行为：如何发现方案、采购流程、决策者。
   - JTBD：客户雇用产品去完成的特定任务。
   - 当前替代方案及其不足；如何快速识别的资格标准。
4. **Build GTM Strategy（构建 GTM 战略）** — 〔引用技能：**gtm-strategy**〕
   - Positioning（如何向该细分描述自己）、Messaging（不同干系人关键信息）、Channels（按预期 ROI 排序触达 ICP）、Launch tactics（发布前/发布日/发布后动作）、Pricing alignment、Success metrics。
5. **Generate GTM Plan（生成计划）** — 输出下方模板〔引用技能：无，落盘〕
   - 含 Beachhead Segment、ICP 表、Positioning & Messaging、Channel Strategy、Launch Timeline、Success Metrics、Risks & Mitigations、Expansion Plan。
6. **Offer Next Steps（建议下一步）** — 〔引用技能：无〕
   - 是否设计发布后增长闭环？是否做销售战斗卡？是否起草营销文案？是否建指标看板？

## Checkpoint

> （源未设 checkpoint；Step 2–4 后分别调用对应 skill 即隐含验收点）

## 输出模板

```markdown
## Go-to-Market Plan: [产品/功能]

**Launch date**: [目标]
**Type**: [新产品 / 功能 / 层级 / 市场扩张]

### Beachhead Segment
**Who**: [具体细分定义]
**Why them first**: [对照四标准的理由]
**Size**: [TAM/SAM/SOM 估算]

### Ideal Customer Profile
| Attribute | Definition |
|-----------|-----------|
| Company size | [范围] |
| Industry | [具体] |
| Decision maker | [职位] |
| Key JTBD | [任务] |
| Current solution | [当前方案] |
| Qualification signal | [识别信号] |

### Positioning & Messaging
**Positioning statement**: For [谁] who [需求], [产品] is [品类] that [收益]. Unlike [替代], we [差异化].

**Key messages by stakeholder**:
| Audience | Message | Proof Point |
|----------|---------|------------|

### Channel Strategy
| Channel | Tactic | Reach | Cost | Priority |
|---------|--------|-------|------|----------|

### Launch Timeline
| Phase | Timing | Actions | Owner |
|-------|--------|---------|-------|
| Pre-launch | [日期] | [列表] | [人] |
| Launch week | [日期] | [列表] | [人] |
| Post-launch | [日期] | [列表] | [人] |

### Success Metrics
| Metric | 30-day target | 90-day target |
|--------|-------------|-------------|

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|

### Expansion Plan
[滩头后：哪些相邻细分、顺序、适配]
```

## 保存指令

保存为 markdown（源要求 Save as markdown；未规定具体文件名）。

## 下一步建议

- 「要我为发布后牵引设计增长闭环吗？」
- 「要我为销售做竞争战斗卡吗？」
- 「要我起草发布的营销文案吗？」
- 「要我建发布追踪的指标看板吗？」

## Further Reading

（源命令未提供 Further Reading，已丢弃）
