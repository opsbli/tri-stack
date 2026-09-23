---
name: summarize-meeting
description: 将会议转录整理为结构化纪要——日期、参与者、主题、关键决策、要点与行动项。
source: pm-skills-main/pm-execution/skills/summarize-meeting/SKILL.md
domain: 执行
---

# 会议摘要（summarize-meeting）

> 蒸馏自 `summarize-meeting`｜域：执行｜源词数：≈620

## 必含章节清单（MUST-SECTIONS）

- [ ] Date & Time — 日期与起止时间
- [ ] Participants — 参与者姓名与角色
- [ ] Topic — 主题（短标题）
- [ ] Summary — 要点列表
- [ ] Action Items — 行动项表（Due Date/Owner/Action）
- [ ] Decisions Made — 已做决策
- [ ] Open Questions — 未决问题

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] （无）

## 逐段引导问题

- **Extract**：讨论主题、所做决策、分歧/顾虑、行动项（负责人+截止）。
- **Summary**：用「Point 1/2/3」列关键讨论点或决策。
- **Action Items**：表格式（Due Date | Owner | Action）。
- **Decisions**：明确列决策。
- **Open Questions**：未决问题。

## 输出模板

```markdown
## Meeting Summary
**Date & Time**: [Date and start/end time]
**Participants**: [Full names and roles]
**Topic**: [Short title]
**Summary**
- **Point 1**: [key discussion point or decision]
**Action Items**
| Due Date | Owner | Action |
|----------|-------|--------|
**Decisions Made**
- [Decision 1]
**Open Questions**
- [Unresolved question 1]
```

## 输出命名规则

`Meeting-Summary-[date]-[topic].md`

## 关键规则

- 客观——总结所讨论，非个人意见
- 突出行动项，防遗漏
- 大型/复杂会议按主题分节
- 用「we」保持团队包容感

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- （源未提供 Further Reading 或全部不合规，已丢弃）
