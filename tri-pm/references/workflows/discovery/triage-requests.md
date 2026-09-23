---
name: triage-requests
description: 功能请求分诊编排——把一堆客户/干系人请求解析归主题、评优先级，产出含四级优先分层的 Triage Report。
source: pm-skills-main/pm-product-discovery/commands/triage-requests.md
domain: 探索
---

# /triage-requests → 功能请求分诊

> 蒸馏自命令 `triage-requests`｜域：探索｜源词数：684
> **语法翻译**：源项目以 `/triage-requests` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

把一堆功能请求——来自支持工单、销售通话、问卷或 Slack——变成一份排好优先级、可执行的 backlog。

## 参数提示

`"<feature requests as text, file, or paste>"`

## 调用示例（翻译为对话形态）

- 源：`/triage-requests`（无输入时反问）→ 「帮我把这批功能请求做一次分诊。」
- 源：`/triage-requests [paste a list of requests]` → 「这是我们收到的功能请求清单（粘贴），帮我归类排序。」
- 源：`/triage-requests [upload a CSV/spreadsheet]` → 「我上传了一个功能请求 CSV，请分诊。」

## 工作流步骤

1. **Step 1: Accept Feature Requests**（接收请求）— 接受任意格式：
   - **Pasted text**：一行或一段一条
   - **Uploaded file**：CSV、Excel 或文本文件
   - **Structured data**：若输入带列（requester、request、date 等），**保留这些列**

   无输入时请用户粘贴或上传。逐条解析，提取（3 项）：
   - The core ask（核心诉求：用户想要什么）
   - Context（谁提的、何时、为什么——若有）
   - Frequency signals（频次信号：有多少人提了类似的）

2. **Step 2: Gather Prioritization Context**（收集优先级情境）— 对话式提问、不要一次全抛（4 问，照抄）：
   - What is the product? What stage is it in?（产品是什么？处于什么阶段？）
   - What are the current strategic goals or OKRs?（当前战略目标或 OKR 是什么？——用于评对齐度）
   - Any constraints to consider? (team size, technical debt, upcoming deadlines)（有什么约束：团队规模、技术债、临近的截止期）
   - Are there segments whose requests should carry more weight? (enterprise, churning users, power users)（是否有些细分群体的请求应加权：企业客户、流失中用户、重度用户）

3. **Step 3: Categorize and Analyze**（归类与分析）〔引用技能：`**analyze-feature-requests**`〕— **5 个**分析维度（照抄）：
   - **Theme clustering**：把相似请求聚成主题（源例：`"reporting & analytics"`、`"collaboration"`、`"mobile experience"`）
   - **Request count per theme**：每个主题下有多少条独立请求
   - **Strategic alignment**：按既定目标给每个主题评级 **High/Medium/Low/None**
   - **Segment analysis**：哪些用户群在推动哪些主题
   - **Sentiment signals**：请求是否伴随 frustration、churn threats 或 delight（挫败感、流失威胁、惊喜）

4. **Step 4: Prioritize**（排优先级）〔引用技能：`**prioritize-features**`〕— 对每个主题（及主题内 top 个别请求），填这张 **5 因子**表（照抄）：

   | Factor | Assessment |
   |--------|-----------|
   | **Impact** | How many users affected? How severely?（影响多少用户？多严重？） |
   | **Strategic alignment** | Does it serve current goals?（服务于当前目标吗？） |
   | **Effort estimate** | T-shirt size (S/M/L/XL)（T 恤尺码估算） |
   | **Risk** | What happens if we don't do this?（不做会怎样？） |
   | **Revenue signal** | Is this tied to deals, retention, or expansion?（是否与成单、留存或扩容挂钩？） |

   然后给主题排序，产出优先级清单。

5. **Step 5: Generate Triage Report**（生成分诊报告）— 模板见下。

6. **Step 6: Offer Next Steps**（提供下一步）— 见「下一步建议」。

## Checkpoint

（源未设 checkpoint）

## 输出模板

```markdown
## Feature Request Triage Report

**Date**: [today]
**Requests analyzed**: [count]
**Themes identified**: [count]

### Theme Summary
| # | Theme | Requests | Top Ask | Alignment | Impact | Effort | Priority |
|---|-------|----------|---------|-----------|--------|--------|----------|

### Priority 1: Act Now
[Themes/requests to include in near-term planning]
- **[Theme]**: [X] requests — [why it's urgent]
  - Top requests: [list]
  - Recommended action: [build / prototype / investigate]

### Priority 2: Plan Next
[Themes worth planning but not urgent]

### Priority 3: Collect More Signal
[Themes with potential but insufficient evidence]

### Priority 4: Decline or Defer
[Requests that don't align with strategy — with rationale]

### Notable Individual Requests
[High-value one-off requests that didn't cluster into themes]

### Patterns and Insights
- [Key insight about what users are telling you]
- [Segment-specific patterns]
- [Gaps between what users ask for and underlying needs]
```

## 保存指令

Save the report as a markdown file to the user's workspace（把报告存为 Markdown 文件到用户工作区）。源未规定文件名。若输入是结构化数据，另外输出一份**可下载的 CSV**（enriched data）。

## 下一步建议

Step 6 的 4 条邀约（自然语言，非可执行命令）：

- 「要我为最高优先项**写用户故事**吗？」
- 「要我为其中某些主题**头脑风暴解决方案**吗？」
- 「要我**设计实验**、在动工前先验证需求吗？」
- 「要我**起草一份干系人通报**来总结这次分析吗？」

## 关键规则（源 Notes 逐条）

- 用户提供带列的 CSV 时，**保留其数据结构并在其上做增强**。
- 找请求**背后的真实需求**——原句示例：「add dark mode」可能真正意味着「reduce eye strain during long sessions」（减轻长时间使用的眼睛疲劳）。
- 标出**互相冲突**的请求（源例：「simplify the UI」 vs 「add more configuration options」）。
- 请求量大（**50+**）时，先汇总主题，再按需邀请用户下钻到具体主题。
- 输入为结构化数据时，把增强后的数据输出为可下载 CSV。

## Further Reading

（源未提供 Further Reading）
