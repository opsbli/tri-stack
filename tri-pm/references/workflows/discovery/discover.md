---
name: discover
description: 完整的产品探索周期——从构思发散经假设映射到实验设计，7 步串联多个探索框架产出 Discovery Plan。
source: pm-skills-main/pm-product-discovery/commands/discover.md
domain: 探索
---

# /discover → 完整探索周期

> 蒸馏自命令 `discover`｜域：探索｜源词数：705
> **语法翻译**：源项目以 `/discover` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

运行一套结构化的产品探索流程，从发散思维推进到聚焦验证。本流程把多个探索框架串成一条端到端工作流。

## 参数提示

`"<product or feature idea>"`（产品或功能想法）

## 调用示例（翻译为对话形态）

- 源：`/discover Smart notification system for our project management tool`
  → 本环境等价说法：「帮我为我们项目管理工具的智能通知系统跑一遍完整探索周期。」
- 源：`/discover New product: AI writing assistant for non-native speakers`
  → 本环境等价说法：「新产品：面向非母语者的 AI 写作助手，做一次初始探索。」
- 源：`/discover`（无参数时会反问你在探索什么）
  → 本环境等价说法：「带我做一次产品探索。」（Agent 应先反问探索对象）

## 工作流步骤

1. **Step 1: Understand the Discovery Context**（理解探索情境）— 先判定属于哪一类：
   - **Existing product** — 在已有真实用户的成熟产品上做持续探索
   - **New product** — 为尚未验证需求的概念做初始探索

   向用户提问（3 问，照抄）：
   - What are you exploring? (product idea, feature area, opportunity space)（你在探索什么：产品想法、功能域、机会空间）
   - What do you already know? (prior research, customer feedback, data)（你已经知道什么：既有研究、客户反馈、数据）
   - What decisions will this discovery inform? (build/kill, prioritize, pivot)（这次探索将支撑什么决策：做/砍、排优先级、转向）

   情境输入可来自上传文件（research、PRDs、transcripts、data）、链接或对话。

2. **Step 2: Brainstorm Ideas (Divergent Phase)**（构思，发散阶段）〔引用技能：`**brainstorm-ideas-existing**` 或 `**brainstorm-ideas-new**`〕
   - 从 PM、Designer、Engineer 三视角生成想法
   - 呈现 **top 10 ideas** 并附简要理由
   - 请用户挑 **3-5 个**带入下一步，或接受全部

3. **Step 3: Identify Assumptions (Critical Thinking Phase)**（识别假设，批判思维阶段）〔引用技能：`**identify-assumptions-existing**` 或 `**identify-assumptions-new**`〕
   - 对每个入选想法，在各风险类别下暴露假设：
     - **Value**: Will users want this?（用户想要吗？）
     - **Usability**: Can users figure it out?（用户搞得懂吗？）
     - **Feasibility**: Can we build it?（我们造得出吗？）
     - **Viability**: Does the business case work?（商业上算得过来吗？）
     - **Go-to-Market**（**仅新产品**）: Can we reach and convert users?（我们能触达并转化用户吗？）
   - 使用 devil's advocate 多视角分析
   - 汇编一份跨所有想法的**假设总清单**（master list）

4. **Step 4: Prioritize Assumptions (Focus Phase)**（假设优先级，聚焦阶段）〔引用技能：`**prioritize-assumptions**`〕
   - 在 **Impact × Risk** 矩阵上定位假设
   - 识别 **"leap of faith" assumptions** —— high impact, high uncertainty（高影响、高不确定性的信念飞跃假设）
   - 按测试优先级排序假设
   - 把可以一起测的相关假设**归组**

5. **Step 5: Design Experiments (Validation Phase)**（设计实验，验证阶段）〔引用技能：`**brainstorm-experiments-existing**` 或 `**brainstorm-experiments-new**`〕
   - 为每条关键假设设计 **1-2 个**实验
   - 既有产品：A/B tests、fake doors、prototypes、user tests、data analysis
   - 新产品：XYZ hypotheses、pretotypes、landing pages、concierge MVPs
   - 每个实验含 success criteria、timeline、effort
   - 按依赖关系与投入量给实验排序

6. **Step 6: Create Discovery Plan**（产出探索计划）— 把以上全部汇编成一份探索计划文档（模板见下）。

7. **Step 7: Offer Next Steps**（提供下一步选项）— 见「下一步建议」。

## Checkpoint

源共设 **2 处** checkpoint，位置照抄：

> **Step 2 后**："Here are 10 ideas. Which ones should we stress-test? Pick 3-5, or I can carry all forward." — 「这是 10 个想法。我们该压力测试哪些？挑 3-5 个，或者我可以把全部带入下一步。」

> **Step 4 后**："Here are your riskiest assumptions. Which ones feel most critical to validate first?" — 「这些是你风险最高的假设。你觉得哪几条最该先验证？」

## 输出模板

Discovery Plan 全量骨架（6 组分节 + 2 张表，一字不删）：

```markdown
## Discovery Plan: [Topic]

**Date**: [today]
**Product Stage**: [existing/new]
**Discovery Question**: [what we're trying to learn]

### Ideas Explored
[Summary of brainstormed ideas with brief descriptions]

### Selected Ideas for Validation
[3-5 ideas carried forward with rationale]

### Critical Assumptions
| # | Assumption | Category | Impact | Uncertainty | Priority |
|---|-----------|----------|--------|-------------|----------|

### Validation Experiments
| # | Tests Assumption | Method | Success Criteria | Effort | Timeline |
|---|-----------------|--------|-----------------|--------|----------|

### Experiment Details
[For each experiment: hypothesis, setup, measurement, decision criteria]

### Discovery Timeline
Week 1: [experiments]
Week 2: [experiments]
Week 3: [analysis and decision]

### Decision Framework
- If [experiment] succeeds → proceed to [next step]
- If [experiment] fails → [pivot/kill/investigate further]
```

## 保存指令

Save the plan as a markdown file to the user's workspace（把探索计划存为 Markdown 文件到用户工作区）。源未规定文件名。

## 下一步建议

Step 7 的 4 条邀约（照抄原意，均为自然语言，不是可执行命令）：

- 「要我为最优想法**写一份 PRD** 吗？」（create a PRD for the top idea）
- 「要我**设计一份访谈脚本**来补充这些实验吗？」（design an interview script to supplement these experiments）
- 「要我**搭一套指标**来跟踪这些实验吗？」（set up metrics to track the experiments）
- 「要我**估算投入**并为 MVP 写用户故事吗？」（estimate effort and create user stories for the MVP）

## 关键规则（源 Notes 逐条）

- 这是一条 **15-30 分钟**的结构化工作流——开始前先告知用户。
- 每个 checkpoint 处，用户都可以改方向、跳过或深入。
- 用户若有研究数据，**先从中提取洞察再构思**。
- 探索计划应当是**活文档**——主动提出随实验进展更新它。
- 新产品：**先验证 desirability（可取性），再谈 feasibility**。
- 既有产品：检查是否存在可用于支撑假设判断的**使用数据**。

## Further Reading

（源未提供 Further Reading）
