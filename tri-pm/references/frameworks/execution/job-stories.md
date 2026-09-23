---
name: job-stories
description: 用「When [情境], I want [动机], so I can [结果]」格式写 Job Stories，含详细验收标准。
source: pm-skills-main/pm-execution/skills/job-stories/SKILL.md
domain: 执行
---

# Job Stories（job-stories）

> 蒸馏自 `job-stories`｜域：执行｜源词数：≈500

## 必含章节清单（MUST-SECTIONS）

- [ ] Title — 工作结果/产出标题
- [ ] Description — When [situation], I want [motivation], so I can [outcome]
- [ ] Design — 设计文件链接
- [ ] Acceptance Criteria — 6-8 条聚焦结果的标准

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] （无）

## 逐段引导问题

- **Identify situations**：触发需求的用户情境。
- **Define motivations**：行为背后的动机。
- **Clarify outcomes**：想达成的产出。
- **JTBD 焦点**：聚焦「工作」而非「角色」。
- **Acceptance**：验证结果达成；可观察、可量化语言；处理边界。

## 输出模板

```markdown
**Title:** [Job outcome or result]
**Description:** When [situation], I want to [motivation], so I can [outcome].
**Design:** [Link to design files]
**Acceptance Criteria:**
1. [Situation is properly recognized]
2. [System enables the desired motivation]
3. [Progress or feedback is visible]
4. [Outcome is achieved efficiently]
5. [Edge cases handled gracefully]
6. [Integration and notifications work]
```

## 输出命名规则

源文件未规定（输出为 Job Stories 集）

## 关键规则

- 每条遵循 When...I want...so I can 格式
- 6-8 条验收标准聚焦结果
- 强调用户情境与动机，附设计链接

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- [Jobs-to-be-Done Masterclass with Tony Ulwick and Sabeen Sattar](https://www.productcompass.pm/p/jobs-to-be-done-masterclass-with) (video course)
