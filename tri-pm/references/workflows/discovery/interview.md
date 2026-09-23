---
name: interview
description: 客户访谈双模编排——prep 模式在访谈前产出结构化脚本，summarize 模式在访谈后把逐字稿提炼成结构化洞察。
source: pm-skills-main/pm-product-discovery/commands/interview.md
domain: 探索
---

# /interview → 客户访谈准备与摘要

> 蒸馏自命令 `interview`｜域：探索｜源词数：771
> **语法翻译**：源项目以 `/interview` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

两种模式：**prep** 在你与客户交谈**之前**产出结构化访谈脚本；**summarize** 在访谈**之后**提取洞察。

## 参数提示

`"[prep|summarize] <topic or transcript>"`

## 调用示例（翻译为对话形态）

- 源：`/interview prep Onboarding experience for enterprise users` → 「帮我准备一份访谈脚本，主题是企业用户的上手体验。」
- 源：`/interview summarize [paste transcript or upload file]` → 「这是访谈逐字稿（粘贴/上传），帮我提炼成结构化摘要。」
- 源：`/interview`（反问模式）→ 「我要做客户访谈。」（Agent 须先反问 prep 还是 summarize）

## 工作流步骤

### 模式一：Prep Mode（访谈前）

按你的研究问题定制一份结构化访谈脚本。

1. **Step 1: Understand the Research Goal**（理解研究目标）— 4 问（照抄）：
   - What are you trying to learn? (specific research question)（你想学到什么：具体研究问题）
   - Who are you interviewing? (segment, role, relationship to product)（你要访谈谁：细分、角色、与产品的关系）
   - How much time do you have? (15 min, 30 min, 60 min)（你有多少时间）
   - What decisions will this research inform?（这项研究将支撑什么决策）

2. **Step 2: Generate Interview Script**（生成脚本）〔引用技能：`**interview-script**`〕
   - 遵循 "The Mom Test" 原则——**ask about their life, not your idea**
   - No leading questions, no pitching（不引导、不推销），聚焦 past behavior and real situations（过去行为与真实情境）
   - 按下方「输出模板 · Prep」的分节结构成文

3. **Step 3: Customize and Review**（定制与复核）— 4 项：
   - 按时长调整问题数量
   - 为用户想验证的特定假设补充追问
   - **标出可能引导证人的问题**（flag questions that might lead the witness）
   - 提供可打印版本（存为 Markdown 到工作区）

### 模式二：Summarize Mode（访谈后）

把逐字稿转成结构化、可行动的洞察。

1. **Step 1: Accept the Transcript**（接收逐字稿）— 接受任意格式：
   - **Pasted text**：原始逐字稿或笔记
   - **Uploaded file**：文档、文本文件或会议记录导出
   - **Audio summary**：用户口述所谈内容（非完整逐字稿）

   若输入只是粗略笔记而非完整逐字稿，就基于已有内容工作，并**注明局限**。

2. **Step 2: Extract and Structure**（提取与结构化）〔引用技能：`**summarize-interview**`〕— 解析出 **8 项**（照抄）：
   - **Participant profile**：Role, experience level, segment, context
   - **Jobs to Be Done**：参与者试图达成什么
   - **Current workflow**：他们今天怎么解决这个问题
   - **Pain points**：Frustrations, workarounds, time sinks
   - **Satisfaction signals**：什么用得好、哪些瞬间令人愉悦
   - **Quotes**：能承载关键洞察的原话（有时间戳就带上）
   - **Surprises**：任何意外的、或与假设相矛盾的东西
   - **Feature reactions**：若谈到具体功能/概念，记录反应

3. **Step 3: Generate Interview Summary**（生成摘要）— 模板见下。

4. **Step 4: Connect to Broader Research**（接入更大范围研究）— 见「下一步建议」。

## Checkpoint

（源未设 checkpoint）

## 输出模板

**Prep 模式脚本骨架**（照抄）：

```markdown
## Interview Script: [Research Topic]

**Research Question**: [what we're trying to learn]
**Target Participant**: [who]
**Duration**: [X] minutes

### Warm-up (3-5 min)
[Rapport-building questions, role/context understanding]

### Core Exploration (15-40 min)
[JTBD probing, past behavior, current workflow, pain points]
- For each question: the question + why you're asking it + follow-up prompts

### Specific Topics (5-10 min)
[Targeted questions about specific features or concepts — if needed]

### Wrap-up (3-5 min)
[Open-ended closing, referral ask, next steps]

### Note-Taking Template
[Pre-formatted template to capture insights during the interview]

### Red Flags to Watch For
[Signs the conversation is going off-track or the participant is being polite rather than honest]
```

**Summarize 模式摘要骨架**（照抄）：

```markdown
## Interview Summary

**Participant**: [anonymized profile — role, segment, experience]
**Date**: [if known]
**Duration**: [if known]
**Interviewer**: [if known]

### Key Insights
1. **[Insight]** — [supporting evidence/quote]
2. **[Insight]** — [supporting evidence/quote]
3. ...

### Jobs to Be Done
- **Primary JTBD**: [When I..., I want to..., so I can...]
- **Related JTBDs**: [additional jobs]

### Current Workflow
[How the participant currently solves the problem, step by step]

### Pain Points
| Pain Point | Severity | Quote |
|-----------|----------|-------|

### Satisfaction Signals
| What Works | Why | Quote |
|-----------|-----|-------|

### Notable Quotes
> "[quote]" — on [topic]

### Assumptions Validated / Invalidated
| Assumption | Status | Evidence |
|-----------|--------|----------|

### Action Items
- [ ] [Follow-up action from this interview]
- [ ] [Research question to explore further]

### Raw Notes
[If helpful, include annotated key sections]
```

## 保存指令

- Prep 模式：提供可打印版本，存为 Markdown 到用户工作区。
- Summarize 模式：Save the summary as a markdown file（把摘要存为 Markdown 文件）。

源均未规定具体文件名。

## 下一步建议

Summarize 模式 Step 4 的 3 条邀约（自然语言，非可执行命令）：

- 「要我**把这份与你做过的其他访谈摘要做对比**吗？」
- 「要我根据这位参与者所说的**更新假设**吗？」
- 「要我从多份访谈中**提炼用户画像**吗？」

## 关键规则（源 Notes 逐条）

- Prep 模式：**始终包含「为什么问这个」的注解**——它能帮访谈者不跑偏。
- Summarize 模式：区分参与者**说了什么**与**做了什么**——behavioral > stated（行为证据优先于口头陈述）。
- 标出同一次访谈内部的**自相矛盾**（说一套、描述的做法是另一套）。
- 逐字稿若提到竞品，**捕捉竞争情报**。
- Summarize 模式下若提供了多份逐字稿，要**跨稿综合**并给出跨参与者的共性模式。

## Further Reading

（源未提供 Further Reading）
