---
name: proofread
description: 校对命令——检查任意文本的语法/逻辑/行文，给出定点修复（不整篇重写）
source: pm-skills-main/pm-toolkit/commands/proofread.md
domain: 工具
---

# /proofread → 语法与行文校对（命令态）

> 蒸馏自命令 `proofread`｜域：工具｜源词数：约 450
> **语法翻译**：源项目以 `/proofread` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。
> 能力内核引用技能态 `frameworks/toolkit/grammar-check.md`。

## 用途

识别文本中的语法、逻辑、行文错误，给出具体、定点的修复建议，不整篇重写。

## 参数提示

`<text to check>`（待检查文本）

## 调用示例（翻译为对话形态）

- 源：`/proofread [paste text]`
- 本环境等价说法：「请校对下面这段：[粘贴文本]」
- 源：`/proofread [upload a document]`
- 本环境等价说法：「上传这份文档，请做语法与行文校对」

## 工作流步骤

1. **Accept Text** — 接受任意形态文本：粘贴、上传文档（DOCX/PDF/markdown）、或邮件草稿。
2. **Analyze** — 应用 **grammar-check** 技能，扫描三类问题：Grammar（拼写/标点/主谓一致/时态/冠词用法）、Logic（矛盾/无支撑主张/循环论证/指代不清）、Flow（过渡弱/句子节奏/段落结构/冗余/可读）。〔引用技能：`**grammar-check**`〕
3. **Report Issues** — 按类别列出每条错误的位置、问题、修复（见模板）。
4. **Offer** — 询问是否：应用全部修复返回清理后文本 / 聚焦某一段深入。

## Checkpoint

（源未设 checkpoint 引句）
> （源未设 checkpoint）

## 输出模板

```markdown
## Proofread Report
**Text length**: [word count]
**Issues found**: [count by category]

### Issues
#### 1. [Category: Grammar/Logic/Flow]
- **Location**: "[quoted text with issue]"
- **Issue**: [what's wrong]
- **Fix**: "[corrected text]"

### Summary
- Grammar: [X] / Logic: [X] / Flow: [X]
- Overall quality: [assessment]
```

## 保存指令

源文件未规定落盘位置（命令态默认以对话返回报告）

## 下一步建议

- 应用全部修复并返回清理后文本
- 对特定段落做更深入校对

## 与 grammar-check 的差异（本环境说明）

- **grammar-check** 是**技能态**（能力内核，见 `frameworks/toolkit/grammar-check.md`），定义完整的检查分类清单（语法 6 子类 / 逻辑 4 子类 / 行文 6 子类）与流程。
- **proofread** 是**命令态**（对话入口），调用该技能并面向最终用户交付报告；其三类子项略有增补：Grammar 增「冠词用法 article usage」、Logic 增「循环论证 circular reasoning」、Flow 增「句子节奏 sentence rhythm / 段落结构 paragraph structure」。
- 二者共用同一修复哲学：最小改动、保留作者声音、讲清理由。

## Further Reading

（源未提供 Further Reading，已丢弃）
