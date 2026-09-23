---
name: write-stories
description: 把功能拆为 backlog 项——用户故事/Job Stories/WWA 三格式，含验收标准。
source: pm-skills-main/pm-execution/commands/write-stories.md
domain: 执行
---

# /write-stories → Backlog 项生成器

> 蒸馏自命令 `write-stories`｜域：执行｜源词数：≈520
> **语法翻译**：源项目以 `/write-stories` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

把功能拆为结构良好的 backlog 项。按团队偏好选三格式之一，各含完整验收标准。

## 参数提示

`[user|job|wwa] <feature description or PRD>`（无参则问功能与格式）

## 调用示例（翻译为对话形态）

- 源：`/write-stories user Allow users to export reports as PDF and CSV`
- 本环境等价说法：「用用户故事格式，把『导出报告为 PDF/CSV』拆成 backlog 项」
- 源：`/write-stories job Notification system for task deadlines`
- 本环境等价说法：「用 Job Stories 格式，拆『任务截止通知系统』」
- 源：`/write-stories wwa Dark mode for the mobile app`
- 本环境等价说法：「用 WWA 格式，拆『移动端深色模式』」

## 工作流步骤

1. **接受功能** — 任意形态：PRD、功能描述、用户研究发现、口头想法。有 PRD 则提取需求分解。
2. **确定格式** — 未指定则问：User Stories / Job Stories / WWA？不确定推荐用户故事默认。
3. **分解功能** — 拆 5-15 个独立故事（小到一冲刺）；每故事独立有价值；按依赖与优先级排序；每故事 3-5 验收标准；标需设计/技术 spike 的故事。
4. **生成故事**〔引用技能：`**user-stories**`/`**job-stories**`/`**wwas**`〕— 输出 Backlog（见模板，含 Story Map、Technical Notes、Open Questions）。保存 markdown。
5. **下一步** — 提议：为故事建测试场景、建虚拟数据、估冲刺产能、转格式。

## Checkpoint

> **Step 3 后**："One story = one deployable unit of value — if it needs another story to be useful, combine them" — 一个故事=一个可部署价值单元，需依赖他故事才有用则应合并。

## 输出模板

```markdown
## Backlog: [Feature]
**Format** / **Total stories** / **Estimated effort**
### Stories: [Title] + [story in format] + Acceptance Criteria + Priority/Effort/Dependencies
### Story Map / Technical Notes / Open Questions
```

## 保存指令

保存为 markdown

## 下一步建议

- 「要为这些故事生成测试场景吗？」
- 「要建虚拟数据供开发测试吗？」
- 「要估这些故事的冲刺产能吗？」
- 「要转成其他格式（用户故事↔Job Stories↔WWA）吗？」

## Further Reading

- [How to Write User Stories: The Ultimate Guide](https://www.productcompass.pm/p/how-to-write-user-stories)
- [Jobs-to-be-Done Masterclass with Tony Ulwick and Sabeen Sattar](https://www.productcompass.pm/p/jobs-to-be-done-masterclass-with) (video course)
