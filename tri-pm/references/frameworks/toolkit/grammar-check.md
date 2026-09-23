---
name: grammar-check
description: 语法/逻辑/行文检查框架——识别错误并给出定点修复建议，不整篇重写；覆盖语法、逻辑、行文三类
source: pm-skills-main/pm-toolkit/skills/grammar-check/SKILL.md
domain: 工具
---

# 语法与行文检查（grammar-check · 技能态）

> 蒸馏自 `grammar-check`｜域：工具｜源词数：1459
> 本文为**技能态**。命令态 `proofread` 引用本框架，见 `workflows/toolkit/proofread.md`。

## 必含章节清单（MUST-SECTIONS）

- [x] Purpose — 框架目的
- [x] Input Arguments — 输入参数
- [x] Process — 检查流程（5 步）
- [x] Error Categories — 检查项分类清单（3 类 + 17 子类，逐类）

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Output Format — 输出格式（见正文）
- [ ] Important Guidelines — 重要准则（见正文）
- [ ] Checklist for Review — 审阅清单（见 part2）
- [ ] Examples of Effective Feedback — 反馈示例（见 part2）
- [ ] When to Suggest No Change — 不改的情形（见 part2）

## 逐段引导问题

- **Purpose**：分析文本的语法、逻辑、行文错误，给出具体定点修复建议，重清晰、正确、可读。
- **Input Arguments**：需文本目标（OBJECTIVE）与待审文本（TEXT）。
- **Error Categories**：三类错误是否都扫描——语法/逻辑/行文各自子类是否覆盖。

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

## 输出命名规则

源文件未规定（以对话返回检查报告，不强制落盘文件名）

## 输入参数（源变量翻译为对话上下文）

- OBJECTIVE（文本意图/目标）：如"说服投资人投 A 轮""向新用户讲清功能""向员工传达公司价值观"
- TEXT（待审文本）

## 流程（5 步）

1. **Understand Context**：目标（营销稿/技术文档/演示/邮件/社媒）、受众（专家/大众/干系人/客户）、语气（正式/随意/权威/友好）。
2. **Scan for Errors**：通读一遍，标注语法/逻辑/行文错误。
3. **Categorize Errors**：按类型归组（语法/逻辑/行文）。
4. **Create Fix Suggestions**：每条含 Location / Error identified / Fix suggested / Rationale。
5. **Prioritize**：先标最高影响——Critical（混淆读者的语法或逻辑错）、Important（伤可读/说服力的行文问题）、Minor（润色）。

## 检查项分类清单（Error Categories，逐类照抄）

### Grammar Errors（语法）

- **Spelling**：拼写错误。
- **Punctuation**：标点（缺失撇号、逗号、句号；run-on 长句）。
- **Subject-Verb Agreement**：主谓一致（集体名词如 team 在美式英语作单数）。
- **Tense Consistency**：时态一致（过去/现在按时间框架统一）。
- **Pronoun Clarity**：代词清晰（"she"指经理还是设计师须明确）。
- **Modifier Placement**：修饰语位置（悬垂修饰语，谁执行动作须明确）。

### Logical Errors（逻辑）

- **Unsupported Claims**：无支撑主张（须补证据）。
- **Contradictions**：自相矛盾（两段陈述冲突须澄清）。
- **Incomplete Logic**：逻辑不完整（断言因果却无证明）。
- **Vague Claims**：含糊主张（须具体量化）。

### Flow Errors（行文）

- **Weak Transitions**：过渡弱（段间跳跃，缺连接词）。
- **Choppy Sentences**：句子破碎（可合并相关意群）。
- **Passive Voice Overuse**：被动语态过度（改主动更清晰）。
- **Unclear Pronoun Reference**：代词指代不清（"it"指什么须明确）。
- **Redundancy**：冗余（删同义重复）。
- **Tone Inconsistency**：语气不一致（正式与随意混用须统一）。

## 输出格式要点（Output Format）

不整篇重写，仅给：ERROR SUMMARY（分类计数）/ FIXES BY CATEGORY（每条 Location·Error·Fix·Why）/ PRIORITY FIXES（3–5 项最高影响）/ TONE AND OBJECTIVE ALIGNMENT（是否达成目标、语气是否对齐）。

## 关键规则

- 语气直白专业，对写作给予鼓励。
- 清晰优先：语法正确也可能令人困惑，清晰度至上。
- 用小学水平语言解释修复，不假设读者懂语法术语。
- 不重写：给具体修复建议而非整段代写，保留作者声音。
- 含理由：解释为何改，助作者理解原则。
- 具体："更清晰"无用，须点明具体错处与改法。

## Checkpoint

（源未设显式 checkpoint 引句）
> （源未设 checkpoint）

（详细示例、审阅清单、反馈示例与"不改情形"见 `grammar-check-part2.md`）
