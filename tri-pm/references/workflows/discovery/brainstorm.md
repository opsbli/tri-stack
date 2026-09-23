---
name: brainstorm
description: 多视角构思编排——按「构思想法 / 设计实验」×「既有产品 / 新产品」两维度分流到对应框架，产出想法清单或实验清单。
source: pm-skills-main/pm-product-discovery/commands/brainstorm.md
domain: 探索
---

# /brainstorm → 多视角构思

> 蒸馏自命令 `brainstorm`｜域：探索｜源词数：688
> **语法翻译**：源项目以 `/brainstorm` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

从 PM、Designer、Engineer 三个视角生成产品想法或实验设计，并按「你在做既有产品还是新东西」做适配。

## 参数提示

`"[ideas|experiments] [existing|new] <product or feature description>"`

## 调用示例（翻译为对话形态）

- 源：`/brainstorm ideas existing Mobile banking app engagement`
  → 「为手机银行 App 的用户参与度构思想法（既有产品）。」
- 源：`/brainstorm ideas new AI-powered meal planning for busy parents`
  → 「新产品构思：给忙碌父母的 AI 备餐规划。」
- 源：`/brainstorm experiments existing Onboarding flow redesign`
  → 「为上手流程改版设计验证实验（既有产品）。」
- 源：`/brainstorm experiments new Marketplace for freelance designers`
  → 「新产品：自由设计师交易市场，设计验证实验。」
- 源：`/brainstorm`（interactive mode）
  → 「带我做一次头脑风暴。」（Agent 须先反问两个维度）

## 工作流步骤

1. **Step 1: Determine Mode**（确定模式）— 从上下文识别**两个维度**：
   - **What to brainstorm**：`ideas`（功能概念）或 `experiments`（验证测试）
   - **Product stage**：`existing`（持续探索）或 `new`（初始探索）

   任一维度缺失就追问；两者都缺时问（照抄）：
   - "Are you brainstorming **ideas** for what to build, or **experiments** to validate assumptions?"
   - "Is this for an **existing** product or a **new** product concept?"

2. **Step 2: Gather Context**（收集情境）— 要对话式提问，**最关键的问题先问**：

   **既有产品（4 问）**：
   - What is the product? Who are current users?（产品是什么？现有用户是谁？）
   - What opportunity area or problem space are you exploring?（在探索哪个机会域/问题空间？）
   - Any constraints (technical debt, platform limitations, team capacity)?（有什么约束：技术债、平台限制、团队产能？）
   - What has been tried before?（此前试过什么？）

   **新产品（4 问）**：
   - What is the product concept? What problem does it solve?（产品概念是什么？解决什么问题？）
   - Who is the target user? What's their current alternative?（目标用户是谁？他们现在的替代方案是什么？）
   - What stage are you at? (napkin sketch, validated problem, early prototype)（处在哪个阶段：餐巾纸草图、已验证问题、早期原型）
   - What are the riskiest assumptions?（最高风险的假设是什么？）

   情境可来自上传文件（PRDs、research docs、strategy decks）、粘贴文本或对话。

3. **Step 3: Generate Output**（生成产出）— 按模式分流：

   **若构思想法**〔引用技能：`**brainstorm-ideas-existing**` 或 `**brainstorm-ideas-new**`〕
   - 三视角生成：Product Manager（user value, business impact）／ Designer（UX, delight, accessibility）／ Engineer（technical innovation, platform leverage, scalability）
   - 每个想法含：name、description、target user impact、feasibility assessment
   - 排出 **top 5** 并附理由
   - 标注哪些属 **quick wins**、哪些属 **strategic bets**

   **若设计实验**〔引用技能：`**brainstorm-experiments-existing**` 或 `**brainstorm-experiments-new**`〕
   - 既有产品：建议 A/B tests、prototypes、fake-door tests、wizard-of-oz、concierge experiments、spikes
   - 新产品：构造 **XYZ+S hypotheses**，并建议 pretotype 实验（landing pages、explainer videos、pre-orders、concierge MVPs）
   - 每个实验含：hypothesis、method、success criteria、effort estimate、expected timeline
   - 按 **learning-per-effort ratio**（单位投入的学习量）排序

4. **Step 4: Deepen and Iterate**（深化与迭代）— 见「下一步建议」。

## Checkpoint

（源未设 checkpoint）

## 输出模板

**想法模式**（照抄）：

```markdown
## Brainstorm: [Product/Feature Area]
**Mode**: Ideas for [existing/new] product
**Context**: [1-2 sentence summary]

### PM Perspective
1. **[Idea Name]** — [description] | Impact: [H/M/L] | Effort: [H/M/L]
2. ...

### Designer Perspective
1. **[Idea Name]** — [description] | Impact: [H/M/L] | Effort: [H/M/L]
2. ...

### Engineer Perspective
1. **[Idea Name]** — [description] | Impact: [H/M/L] | Effort: [H/M/L]
2. ...

### Top 5 Recommendations
| Rank | Idea | Why | Quick Win? |
|------|------|-----|------------|

### Next Steps
[What to do with these ideas]
```

**实验模式**（照抄）：

```markdown
## Experiment Design: [Product/Feature Area]
**Mode**: Experiments for [existing/new] product

### Hypotheses
1. **[Hypothesis]** — XYZ format: [X]% of [Y] will [Z] within [S timeframe]

### Recommended Experiments
| # | Experiment | Tests Hypothesis | Method | Effort | Timeline |
|---|-----------|-----------------|--------|--------|----------|

### Experiment Details
[For each experiment: setup, success criteria, risks, what you'll learn]
```

## 保存指令

源未规定落盘位置与命名（本命令只规定输出格式）。

## 下一步建议

Step 4 的 4 条邀约（自然语言，非可执行命令）：

- 「要我把其中某个想法**细化成更完整的 spec** 吗？」
- 「要我**识别**头部想法背后的**假设**吗？」（衔接 `identify-assumptions-existing` / `identify-assumptions-new`）
- 「要**设计实验**来验证头部想法吗？」（切到实验模式）
- 「要我把这些**与你当前 backlog 一起排优先级**吗？」（衔接 `prioritize-features`）

## 关键规则（源 Notes 逐条）

- 既有产品：想法要**扎根于当前用户行为与已验证的问题**。
- 新产品：**先聚焦 desirability 与 feasibility 风险**。
- 用户若上传研究文档或访谈稿，**先提取洞察再构思**。
- 先广后深（breadth first, then depth）——先大量产出，再做评估。

## Further Reading

（源未提供 Further Reading）
