---
name: summarize-interview
description: 访谈记录结构化框架——把逐字稿转成含 JTBD、满意度信号与行动项的固定模板摘要；用于处理访谈录音/文字稿、综合探索访谈。
source: pm-skills-main/pm-product-discovery/skills/summarize-interview/SKILL.md
domain: 探索
---

# 客户访谈摘要（summarize-interview）

> 蒸馏自 `summarize-interview`｜域：探索｜源词数：266

把访谈逐字稿转成结构化摘要，聚焦 **Jobs to Be Done、满意度、行动项**。

## 必含章节清单（MUST-SECTIONS）

执行 **3 步**：

- [ ] Read the full transcript — 先完整读完逐字稿再动手摘要
- [ ] Fill in the summary template — 填写下方输出模板
- [ ] Use clear, simple language — 用清晰简单的语言

输出模板固定 **8 个字段/小节**（顺序照抄）：

- [ ] Date — 访谈日期与时间
- [ ] Participants — 全名与角色
- [ ] Background — 客户背景信息
- [ ] Current Solution — 目前在用的方案
- [ ] What They Like About Current Solution — 现方案的可取之处
- [ ] Problems With Current Solution — 现方案的问题
- [ ] Key Insights — 关键洞察
- [ ] Action Items — 行动项

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] 前置读取：逐字稿可为附件（text、PDF、audio transcription）或直接粘贴；有附件先读

## 逐段引导问题

- **Read the full transcript**：Read the full transcript carefully before summarizing（摘要前先仔细通读全文）。
- **Fill in the summary template**：信息缺失处用 `"-"`；数值不可得时可用定性描述替代（源例：`"not satisfied"` ／不满意）。
- **Use clear, simple language**：原句标准——「a primary school graduate should be able to understand the summary」（小学毕业生应当能看懂这份摘要）。
- **What They Like / Problems 两节的填写维度**（同一组四要素，照抄）：Job to be done、desired outcome、importance、satisfaction level（待办任务、期望成果、重要性、满意度）。
- **Key Insights**：Unexpected findings or notable quotes（意外发现或值得记录的原话）。
- **Action Items**：Date, Owner, Action 三元组（日期、责任人、动作）。源示例：`"2025-01-15, Paweł Huryn, Follow up with customer about pricing"`。

## 输出模板

```markdown
**Date**: [Date and time of the interview]
**Participants**: [Full names and roles]
**Background**: [Background information about the customer]

**Current Solution**: [What solution they currently use]

**What They Like About Current Solution**:
- [Job to be done, desired outcome, importance, and satisfaction level]

**Problems With Current Solution**:
- [Job to be done, desired outcome, importance, and satisfaction level]

**Key Insights**:
- [Unexpected findings or notable quotes]

**Action Items**:
- [Date, Owner, Action — e.g., "2025-01-15, Paweł Huryn, Follow up with customer about pricing"]
```

## 输出命名规则

源文件未规定命名。要求：Save the summary as a markdown document in the user's workspace（把摘要存为 Markdown 文档到用户工作区）。

## 关键规则

- 模板是**固定字段**，不得增删或改序；缺信息填 `-`，不要留空、也不要臆测补全。
- 「喜欢什么」与「有什么问题」两节都要按 JTBD 四要素（任务/期望成果/重要性/满意度）写，不是自由散文。
- 满意度可用定性词代替分数。
- 语言难度上限：小学毕业生可读——避免行业术语堆砌。
- 行动项必须带日期与责任人，否则不算行动项。

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [User Interviews: The Ultimate Guide to Research Interviews](https://www.productcompass.pm/p/interviewing-customers-the-ultimate) — 用户访谈终极指南

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
