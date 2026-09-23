---
name: setup-metrics
description: 指标体系搭建编排——定义 North Star、Input、Health、Counter 四类指标并设计红黄绿告警阈值，产出 Dashboard Spec。
source: pm-skills-main/pm-product-discovery/commands/setup-metrics.md
domain: 探索
---

# /setup-metrics → 产品指标看板设计

> 蒸馏自命令 `setup-metrics`｜域：探索｜源词数：668
> **语法翻译**：源项目以 `/setup-metrics` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

为你的产品或功能设计一套完整的指标框架——从选对 North Star，到定义能及早发现问题的告警阈值。

## 参数提示

`"<product or feature area>"`

## 调用示例（翻译为对话形态）

- 源：`/setup-metrics SaaS project management tool` → 「帮我为这个 SaaS 项目管理工具搭一套指标体系。」
- 源：`/setup-metrics New checkout flow we just launched` → 「我们刚上线了新结账流程，帮我设计指标与告警阈值。」
- 源：`/setup-metrics`（反问模式）→ 「我要搭一套产品指标。」（Agent 须先反问度量对象）

## 工作流步骤

1. **Step 1: Understand What to Measure**（明确度量对象）— 5 问（照抄）：
   - What product or feature area are you setting up metrics for?（为哪个产品/功能域搭指标？）
   - What stage is it in? (pre-launch, recently launched, mature)（处于什么阶段：未发布、刚上线、成熟）
   - What are the current business goals or OKRs?（当前业务目标或 OKR 是什么？）
   - Do you have existing metrics? What's missing or broken?（已有指标吗？缺什么、坏在哪？）
   - What analytics tools are you using?（在用什么分析工具？——用于定制实施建议）

2. **Step 2: Define the Metrics Framework**（定义指标框架）〔引用技能：`**metrics-dashboard**`〕— **4 类**指标（照抄各自要求）：

   **North Star Metric**
   - 找出最能刻画产品向用户交付的价值的**单一指标**
   - 按 3 条标准校验：measures value delivery、is a leading indicator、is actionable（度量价值交付、是领先指标、可行动）
   - 精确定义该指标：formula、data source、time window（公式、数据源、时间窗）

   **Input Metrics（3-5 个）**
   - 找出驱动 North Star 的杠杆
   - 每个输入指标都应能被某个团队**直接行动**
   - 画出因果链：**Input → North Star → Business Outcome**

   **Health Metrics（3-5 个）**
   - 应保持稳定的指标；一旦劣化说明出了问题
   - 示例：error rates、latency、support ticket volume、NPS、churn rate
   - 定义「健康」区间与劣化阈值

   **Counter-Metrics（1-2 个）**
   - 可能提示「你在朝错误方向优化」的指标
   - 源例：若 North Star 是 `"daily active users"`，counter-metric 用 `"session quality"` 防止空洞的参与度

3. **Step 3: Design Alert Thresholds**（设计告警阈值）— 逐指标填这张表（照抄）：

   | Metric | Green | Yellow | Red | Check Frequency |
   |--------|-------|--------|-----|----------------|
   | [metric] | [healthy range] | [warning] | [critical] | [daily/weekly] |

   两档语义（照抄）：
   - **Yellow**: Investigate — something may be off（去排查，可能有问题）
   - **Red**: Act immediately — page someone or escalate（立即行动，呼人或升级）

4. **Step 4: Create Dashboard Spec**（产出看板规格）— 模板见下。

5. **Step 5: Offer Next Steps**（提供下一步）— 见「下一步建议」。

## Checkpoint

（源未设 checkpoint）

## 输出模板

```markdown
## Metrics Dashboard: [Product/Feature]

**North Star**: [metric name]
**Definition**: [precise formula]
**Current value**: [if known]
**Target**: [goal]

### Input Metrics
| Metric | Definition | Owner | Target | Current |
|--------|-----------|-------|--------|---------|

### Health Metrics
| Metric | Healthy Range | Yellow Threshold | Red Threshold |
|--------|-------------|-----------------|---------------|

### Counter-Metrics
| Metric | Why It Matters | Watch For |
|--------|---------------|-----------|

### Metrics Tree
North Star: [metric]
├── Input: [metric 1] → driven by [team/action]
├── Input: [metric 2] → driven by [team/action]
├── Input: [metric 3] → driven by [team/action]
└── Counter: [metric] → watch for [degradation signal]

### Implementation Notes
- Data sources: [where each metric comes from]
- Refresh frequency: [real-time / hourly / daily]
- Tool recommendations: [based on user's stack]

### Review Cadence
- **Daily**: Glance at North Star and health metrics
- **Weekly**: Review input metrics trends, discuss in team standup
- **Monthly**: Deep dive — are inputs driving the North Star as expected?
- **Quarterly**: Reassess the metrics framework itself
```

## 保存指令

Save as a markdown file to the user's workspace（存为 Markdown 文件到用户工作区）。源未规定文件名。

## 下一步建议

Step 5 的 4 条邀约（自然语言，非可执行命令）：

- 「要我**写 SQL 查询**来计算这些指标吗？」
- 「要我基于这套指标框架**制定 OKR** 吗？」
- 「要我**做一次同期群分析**来设定现实的基线吗？」
- 「要我**建一个每周指标复盘模板**吗？」

## 关键规则（源 Notes 逐条）

- 好的 North Star 很稀有——多数团队挑的是虚荣指标。要坚持推向能刻画 **user value delivered**（已交付的用户价值）的指标，而不只是参与度。
- Input metrics 在解释 North Star 时应满足 **MECE**（mutually exclusive, collectively exhaustive ／互斥且穷尽）。
- 产品若未发布，现在就定义指标，但要注明**基线需在上线后校准**。
- Counter-metrics 用于对抗 **Goodhart's Law**——原句：「when a metric becomes a target, it ceases to be a good metric」（当一个指标变成目标，它就不再是好指标）。
- 建议**从少而精、埋点扎实的指标起步**，而不是做一个没人看的庞大看板。

## Further Reading

（源未提供 Further Reading）
