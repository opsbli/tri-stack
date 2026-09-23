---
name: user-stories
description: 用 3C（卡片/对话/确认）与 INVEST 准则写用户故事，含描述、设计链接与验收标准。
source: pm-skills-main/pm-execution/skills/user-stories/SKILL.md
domain: 执行
---

# 用户故事（user-stories）

> 蒸馏自 `user-stories`｜域：执行｜源词数：≈500

## 必含章节清单（MUST-SECTIONS）

- [ ] Title — 故事标题（Card：简短标题 + 一句话）
- [ ] Description — As a [role], I want [action], so that [benefit]
- [ ] Design — 设计文件链接（Figma/Miro 等）
- [ ] Acceptance Criteria — 4-6 条可测标准

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] （无）

## 逐段引导问题

- **3 C's**：Card（标题+一句话）/ Conversation（意图详谈）/ Confirmation（清晰验收标准）。
- **INVEST 六项（逐条判定）**：
  1. **Independent** — 独立，可任意顺序开发
  2. **Negotiable** — 可协商，非约束合同
  3. **Valuable** — 有价值，交付用户/业务价值
  4. **Estimable** — 可估算
  5. **Small** — 小，适合一个冲刺
  6. **Testable** — 可测，结果可观察验证
- **Plain language**：小学生能懂。
- **Link design**：附设计链接供视觉参考。

## 输出模板

```markdown
**Title:** [Feature name]
**Description:** As a [user role], I want to [action], so that [benefit].
**Design:** [Link to design files]
**Acceptance Criteria:**
1. [Clear, testable criterion]
2. [Observable behavior]
3. [System validates correctly]
4. [Edge case handling]
5. [Performance or accessibility consideration]
6. [Integration point]
```

## 输出命名规则

源文件未规定（输出为结构化用户故事集）

## 关键规则

- 每故事含标题/描述/设计链接/4-6 验收标准
- 故事独立、可任意顺序开发、规模为一个冲刺
- 引用相关设计文档

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- [How to Write User Stories: The Ultimate Guide](https://www.productcompass.pm/p/how-to-write-user-stories)
