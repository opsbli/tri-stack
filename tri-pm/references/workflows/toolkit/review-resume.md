---
name: review-resume
description: PM 简历审阅命令——对照 10 条最佳实践与 XYZ+S 公式，输出评分卡与 Top3 改进
source: pm-skills-main/pm-toolkit/commands/review-resume.md
domain: 工具
---

# /review-resume → PM 简历审阅（命令态）

> 蒸馏自命令 `review-resume`｜域：工具｜源词数：约 700
> **语法翻译**：源项目以 `/review-resume` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。
> 本文为**命令态**，能力内核引用技能态 `frameworks/toolkit/review-resume.md`。

## 用途

对 PM 简历做全面审阅，评估结构、影响指标、关键词优化，并给出带示例的具体改进建议。

## 参数提示

`<resume as text or file>`（简历文本或上传的 PDF/DOCX 文件）

## 调用示例（翻译为对话形态）

- 源：`/review-resume [paste resume text]`
- 本环境等价说法：「帮我审阅这份简历：[粘贴简历文本]」
- 源：`/review-resume [upload resume PDF or DOCX]`
- 本环境等价说法：「上传我的简历文件，请按 PM 最佳实践审阅」

## 工作流步骤

1. **Accept the Resume** — 接受粘贴文本、上传 PDF 或 DOCX，解析完整内容。
2. **Evaluate Against 10 Best Practices** — 应用 **review-resume** 技能，逐条核对：影响指标是否量化、XYZ+S 公式、PM 专属语言、结构与可读性、关键词优化、故事弧、简洁度、相关性、技术可信度、领导力信号。〔引用技能：`**review-resume**`〕
3. **Generate Review** — 输出评分卡（见下模板）、Top3 改进（Current/Suggested/Why）、逐段反馈、缺失项、待加关键词。
4. **Offer Next Steps** — 询问是否：按具体 JD 定制该简历 / 用 XYZ+S 重写特定要点 / 据此生成求职信。

## Checkpoint

（源未设 checkpoint 引句）
> （源未设 checkpoint）

## 输出模板

```markdown
## Resume Review
**Overall Score**: [X/10]
**Strongest area**: [某条最佳实践]
**Biggest opportunity**: [某条最佳实践]

### Scorecard
| # | Best Practice | Score | Assessment |
|---|-------------|-------|-----------|
| 1 | Impact Metrics | [/10] | ... |
| 2 | XYZ+S Formula | [/10] | ... |
| ... | ... | ... | ... |

### Top 3 Improvements
**1. [最高影响改动]**
- Current: "[简历原文]"
- Suggested: "[改进版]"
- Why: [理由]
**2. ...** **3. ...**

### Section-by-Section Feedback
[摘要/经历/教育/技能 逐段]

### Missing Elements
[PM 简历应有却缺失的]

### Keywords to Add
[典型 JD 中缺失的 PM 关键词]
```

## 保存指令

源文件未规定落盘位置（命令态默认以对话返回；如需留存可存为 markdown）

## 下一步建议

- 按具体 JD 定制该简历（参见 tailor-resume 工作流）
- 用 XYZ+S 公式重写特定要点
- 据此生成求职信

## Further Reading

（源未提供 Further Reading，已丢弃）
