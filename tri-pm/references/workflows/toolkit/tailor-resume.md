---
name: tailor-resume
description: 简历对 JD 定制命令——关键词对齐、经历重构与战略优化
source: pm-skills-main/pm-toolkit/commands/tailor-resume.md
domain: 工具
---

# /tailor-resume → 简历对 JD 定制（命令态）

> 蒸馏自命令 `tailor-resume`｜域：工具｜源词数：约 650
> **语法翻译**：源项目以 `/tailor-resume` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。
> 能力内核引用技能态 `frameworks/toolkit/review-resume.md`。

## 用途

拿简历与目标 JD，战略对齐经历以最大化面试机会：关键词优化、要点重写、差距分析。

## 参数提示

`<resume> + <job description>`（简历 + 岗位描述）

## 调用示例（翻译为对话形态）

- 源：`/tailor-resume [upload resume] Here's the JD: [paste job description]`
- 本环境等价说法：「这是我的简历 [上传]，目标 JD 如下：[粘贴 JD]，请帮我定制」
- 源：`/tailor-resume [upload both resume and JD as files]`
- 本环境等价说法：「上传我的简历和 JD 两个文件，请做简历对 JD 优化」

## 工作流步骤

1. **Accept Both Documents** — 需两份输入：简历（文本/PDF/DOCX）+ 目标 JD（文本/URL/文件）；只给一份则追问另一份。
2. **Analyze the Job Description** — 提取：必备资格与技能、优先资格、关键职责、行业与领域信号、资深级别信号、文化与团队信号。
3. **Tailor the Resume** — 应用 **review-resume** 技能：关键词对齐（JD 关键词自然补入）、要点重写（用 XYZ+S 重构 JD 相关成就）、段落重排（相关经历优先）、摘要/目标重写直击岗位、技能栏对齐 JD。〔引用技能：`**review-resume**`〕
4. **Generate Tailored Resume + Analysis** — 输出对齐分、关键词差距表、改动清单、完整重写简历、差距分析、求职信谈点。

## Checkpoint

（源未设 checkpoint 引句）
> （源未设 checkpoint）

## 输出模板

```markdown
## Resume Tailoring: [Job Title] at [Company]
### Alignment Score: [X/10]
### Keyword Gap Analysis
| JD Keyword | In Resume? | Recommendation |
|-----------|-----------|---------------|
### Changes Made
1. **[Section]**: [what changed and why]
### Tailored Resume
[完整重写简历文本]
### Gap Analysis
**Strong matches**: ... **Reframed matches**: ... **Gaps**: ...
### Cover Letter Talking Points
[3-4 点]
```

## 保存指令

源文件要求：将定制后简历保存为 markdown。

## 下一步建议

- 审视差距分析中 Gaps 项，补强或准备面试说辞
- 据此生成求职信

## Further Reading

（源未提供 Further Reading，已丢弃）
