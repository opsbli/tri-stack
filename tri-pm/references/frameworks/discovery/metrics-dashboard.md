---
name: metrics-dashboard
description: 产品指标看板框架——分 North Star / Input / Health / Business 四层定义指标，含 6 列指标定义表、看板布局、复盘节奏与告警设计；用于搭建 KPI 与产品分析监控。
source: pm-skills-main/pm-product-discovery/skills/metrics-dashboard/SKILL.md
domain: 探索
---

# 产品指标看板（metrics-dashboard）

> 蒸馏自 `metrics-dashboard`｜域：探索｜源词数：637

设计一套完整的产品指标看板：选对指标、定好可视化形式与告警阈值。

## 必含章节清单（MUST-SECTIONS）

执行 **6 步**：

- [ ] Identify the metrics framework — 确定指标框架（分 4 层）
- [ ] For each metric, define — 逐指标填 6 列定义表
- [ ] Design the dashboard layout — 设计看板布局
- [ ] Set review cadence — 设定复盘节奏（4 档）
- [ ] Define alerts — 定义告警（3 问）
- [ ] Recommend tools — 按用户技术栈推荐工具

指标分层固定 **4 层**：

- [ ] North Star Metric — 北极星指标（单一，最能刻画核心价值交付）
- [ ] Input Metrics (3-5) — 输入指标：驱动北极星的杠杆
- [ ] Health Metrics — 健康指标：保障产品整体健康的护栏
- [ ] Business Metrics — 业务指标：收入、成本、单位经济性

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Domain Context — 领域背景：Metrics/KPIs/NSM 之分、好指标 4 标准、8 种指标类型、5 步行动
- [ ] 前置读取：用户若提供文件（existing dashboards、analytics data、OKRs、strategy docs）先读

## 逐段引导问题

- **For each metric, define** — **6 列**定义表（照抄表头与填写口径）：

| Metric | Definition | Data Source | Visualization | Target | Alert Threshold |
|---|---|---|---|---|---|
| [Name] | [Exact calculation: numerator/denominator, time window] | [Where the data comes from] | [Line chart / Bar / Number / Funnel] | [Goal value] | [When to trigger an alert] |

- **Set review cadence** — **4 档**（照抄）：
  - **Daily**: Operational health (errors, latency, critical flows)（运营健康：报错、延迟、关键流程）
  - **Weekly**: Input metrics and engagement trends（输入指标与参与度趋势）
  - **Monthly**: North Star, business metrics, OKR progress（北极星、业务指标、OKR 进展）
  - **Quarterly**: Strategic review and metric recalibration（战略复盘与指标重新校准）
- **Define alerts** — **3 问**（照抄）：What thresholds trigger investigation?（什么阈值触发调查？）／ Who gets alerted and through what channel?（谁被告警、通过什么渠道？）／ What's the expected response time?（期望响应时间是多久？）
- **Recommend tools** — 按用户情境推荐（照抄分组）：
  - Amplitude、Mixpanel、PostHog — 产品分析（product analytics）
  - Looker、Metabase、Mode — 基于 SQL 的看板
  - Datadog、Grafana — 运营健康

## 输出模板

看板布局骨架（照抄）：

```
┌─────────────────────────────────────────────┐
│  NORTH STAR: [Metric] — [Current Value]     │
│  Trend: [↑/↓ X% vs last period]             │
├──────────────────┬──────────────────────────┤
│  Input Metric 1  │  Input Metric 2          │
│  [Sparkline]     │  [Sparkline]             │
├──────────────────┼──────────────────────────┤
│  Input Metric 3  │  Input Metric 4          │
│  [Sparkline]     │  [Sparkline]             │
├──────────────────┴──────────────────────────┤
│  HEALTH: [Latency] [Error Rate] [NPS]       │
├─────────────────────────────────────────────┤
│  BUSINESS: [MRR] [CAC] [LTV] [Churn]        │
└─────────────────────────────────────────────┘
```

## 输出命名规则

源文件未规定命名。要求：Save the dashboard specification as a markdown document（把看板规格存为 Markdown 文档）。

## 关键规则（Domain Context 原文照抄）

**Metrics vs KPIs vs NSM**：Metrics = 一切可度量的东西；KPIs = 少数长期跟踪的关键量化指标；North Star Metric = **单一**的、以客户为中心的 KPI，且是业务成功的**领先指标**。

**好指标的 4 条标准**（Ben Yoskovitz, *Lean Analytics*）：
1. **Understandable** — 建立共同语言
2. **Comparative** — 要能跨时间比较，而非快照
3. **Ratio or Rate** — 比率/速率比绝对数更有信息量
4. **Behavior-changing** — 黄金法则原句：「If a metric won't change how you behave, it's a bad metric.」（如果一个指标不会改变你的行为，它就是坏指标。）

**8 种指标类型**（4 对，照抄）：
- **Vanity vs Actionable** — 只有可行动指标才会改变行为
- **Qualitative vs Quantitative** — WHAT vs WHY，两者都需要；never stop talking to customers（永远不要停止与客户交谈）
- **Exploratory vs Reporting** — 探索型用于挖掘意料之外的洞察
- **Lagging vs Leading** — 领先指标带来更快的学习循环，例：客户投诉可预测流失

**5 步行动**（照抄）：
1. 用「好指标 4 标准」审计现有指标
2. 更新看板——确保所有关键指标都是好指标
3. 识别虚荣指标——使用时务必谨慎
4. 区分领先指标与滞后指标
5. 挑一个问题，深挖数据

案例与更多细节：[Are You Tracking the Right Metrics?](https://www.productcompass.pm/p/are-you-tracking-the-right-metrics)（Ben Yoskovitz）

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [The Ultimate List of Product Metrics](https://www.productcompass.pm/p/the-ultimate-list-of-product-metrics) — 产品指标总清单
- [The North Star Framework 101](https://www.productcompass.pm/p/the-north-star-framework-101) — 北极星框架入门
- [The Product Analytics Playbook: AARRR, HEART, Cohorts & Funnels for PMs](https://www.productcompass.pm/p/the-product-analytics-playbook-aarrr) — 产品分析手册
- [AARRR (Pirate) Metrics: The 5-Stage Framework for Growth](https://www.productcompass.pm/p/aarrr-pirate-metrics) — 海盗指标五阶段
- [The Google HEART Framework: Your Guide to Measuring User-Centric Success](https://www.productcompass.pm/p/the-google-heart-framework) — Google HEART 框架
- [Funnel Analysis 101: How to Track and Optimize Your User Journey](https://www.productcompass.pm/p/funnel-analysis) — 漏斗分析入门
- [Are You Tracking the Right Metrics?](https://www.productcompass.pm/p/are-you-tracking-the-right-metrics) — 你在跟踪正确的指标吗

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
