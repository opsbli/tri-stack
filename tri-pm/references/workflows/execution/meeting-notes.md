---
name: meeting-notes
description: 将会议转录整理为结构化纪要——含决策、行动项与跟进项。
source: pm-skills-main/pm-execution/commands/meeting-notes.md
domain: 执行
---

# /meeting-notes → 会议摘要

> 蒸馏自命令 `meeting-notes`｜域：执行｜源词数：≈480
> **语法翻译**：源项目以 `/meeting-notes` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

把原始会议转录或粗略笔记转为清晰结构化纪要，捕获决策并指派行动项。

## 参数提示

`<transcript or meeting notes>`（亦接受上传转录/音频摘要/笔记）

## 调用示例（翻译为对话形态）

- 源：`/meeting-notes [paste transcript]`
- 本环境等价说法：「把这份转录整理成会议纪要与决策」
- 源：`/meeting-notes [upload transcript file]`
- 本环境等价说法：「我上传转录文件，整理成会议摘要」

## 工作流步骤

1. **接受转录** — 任意形态：完整转录（Otter/Fireflies/Meet/Zoom）、粗略笔记、音频摘要、多输入。稀疏则据现有内容并标缺口。
2. **提取结构**〔引用技能：`**summarize-meeting**`〕— 识别：Participants、Topics、Decisions、Action Items（负责人+截止）、Open Questions、Key quotes、Context。
3. **生成摘要** — 输出 Meeting Summary（见模板）。保存 markdown。
4. **下一步** — 提议：邮件发参与者、从行动项建工单、据决策起草干系人更新。

## Checkpoint

> **Step 3 后**："Decisions are the most valuable output — make sure every decision is captured clearly" — 决策是最有价值产出，确保每条清晰捕获。

## 输出模板

```markdown
## Meeting Summary
**Date** / **Participants** / **Meeting type** / **Topic**
### Summary / Key Decisions / Action Items (table) / Discussion Highlights / Open Questions / Next Steps
```

## 保存指令

保存为 markdown

## 下一步建议

- 「要我把纪要邮件发参与者吗？」
- 「要从行动项建工单吗？」
- 「要据决策起草干系人更新吗？」

## Further Reading

- （源未提供 Further Reading 或全部不合规，已丢弃）
