---
name: sentiment-analysis
description: 分析用户反馈数据，按分群给出情感评分、JTBD 与产品满意度洞察
source: pm-skills-main/pm-market-research/skills/sentiment-analysis/SKILL.md
domain: 研究
---

# 情感分析（sentiment-analysis）

> 蒸馏自 `sentiment-analysis`｜域：研究｜源词数：~750

## 必含章节清单（MUST-SECTIONS）

- [ ] Purpose — 目的
- [ ] Input — 输入
- [ ] Analysis Steps — 分析步骤（6 步）
- [ ] Output Structure — 输出结构（含逐分群维度，照抄）
- [ ] Best Practices — 最佳实践

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Further Reading —（源外链全部不合规，已丢弃）

## 逐段引导问题

- **Input**：分析「目标产品/主题」（即用户提供的目标产品/主题）的用户反馈数据并识别带有情感洞察的市场分群。若用户提供 CSV、PDF、问卷、评论数据、社媒聆听报告等反馈源，直接读取分析，提取模式、主题与情感信号。
- **Analysis Steps**：数据摄入 → 分群识别（≥3）→ 主题分析 → 情感评分（每段整体满意度 -1 到 +1）→ 影响评估 → 综合。
- **Output Structure**：每个分群 7 块。
- **Best Practices**：扎根真实反馈并标注来源；识别分群内多数与少数视角；区分功能请求与根本痛点；考虑用户情境；标注小样本分群；寻找跨分群模式；平衡呈现强弱。

## 输出结构维度（逐条照抄源条目）

对识别出的每个分群：

**Segment Profile**
- Name/identifier and common characteristics
- User count or proportion in feedback dataset
- Primary use case or context

**Jobs-to-be-Done**
- Core job this segment is trying to accomplish
- Associated desired outcomes

**Sentiment Score & Satisfaction Level**
- Overall sentiment score (-1 to +1)
- Key satisfaction drivers and detractors
- Net Promoter Score (NPS) proxy if applicable

**Top Positive Feedback Themes**
- What this segment loves about 「目标产品」
- Key strengths from user perspective
- Examples of successful use cases

**Top Pain Points & Criticism**
- Most frequent complaints or frustrations
- Unmet needs or missing features
- Friction points in user journey
- Direct quotes from feedback when available

**Product-Segment Fit Assessment**
- How well 「目标产品」 serves this segment's needs
- Potential to improve fit through product changes
- Risk of churn or dissatisfaction

**Actionable Recommendations**
- 2-3 highest-impact improvements per segment
- Quick wins vs. strategic initiatives
- Segments to prioritize or de-prioritize

## 输出模板

```markdown
### Segment：[名称]
**Segment Profile**：标识与共性；反馈数据中的数量/占比；主场景
**Jobs-to-be-Done**：核心 job；期望结果
**Sentiment Score & Satisfaction Level**：整体情感分（-1 到 +1）；满意驱动与减分项；NPS 代理（如适用）
**Top Positive Feedback Themes**：喜爱点；用户视角强项；成功用例
**Top Pain Points & Criticism**：高频抱怨；未满足需求；旅程摩擦；直接引语
**Product-Segment Fit Assessment**：契合度；改进潜力；流失/不满风险
**Actionable Recommendations**：每段 2–3 个高影响改进；速赢 vs 战略；优先级
```

## 输出命名规则

源文件未规定具体落盘文件名。

## 关键规则

- 所有发现扎根实际用户反馈并标注来源。
- 识别分群内多数与少数视角。
- 区分功能请求与根本痛点。
- 考虑用户面临的情境与约束。
- 标注小样本或情感不确定的分群。
- 寻找跨分群模式与普遍痛点。
- 平衡呈现产品强项与弱项。

## Checkpoint

> （源未设 checkpoint）

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
