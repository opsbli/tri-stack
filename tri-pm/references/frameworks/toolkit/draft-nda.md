---
name: draft-nda
description: NDA（保密协议）起草框架——覆盖信息类型、司法管辖区与需法律审阅的条款，含标准 8 段结构
source: pm-skills-main/pm-toolkit/skills/draft-nda/SKILL.md
domain: 工具
---

# 保密协议起草（draft-nda · 技能态）

> 蒸馏自 `draft-nda`｜域：工具｜源词数：约 800
> 本文为**技能态**。同名命令态见 `workflows/toolkit/draft-nda.md`。

## 必含章节清单（MUST-SECTIONS）

- [ ] Purpose — 框架目的
- [ ] Important Disclaimer — 重要免责声明（原样保留）
- [ ] Input Arguments — 输入参数
- [ ] Process — 起草流程（5 步）
- [ ] NDA Template Structure — 模板三段结构
- [ ] Key Sections to Include — 8 大必备条款（逐条）

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Content Guidelines — 内容准则（见下方正文）
- [ ] Output Format — 输出三段式（见下方正文）
- [ ] Important Reminders — 重要提醒（见下方正文）

## 逐段引导问题

- **Purpose**：为两方起草一份全面、清晰、专业的 NDA，覆盖信息类型、管辖区，并明确标注需法律审阅的条款。
- **Disclaimer**：非法律意见，执行前须经执业律师审阅。
- **Input Arguments**：需双方名称/地址/代表、信息类型、管辖区。
- **Key Sections**：标准 8 段顺序是否齐备，每段的必备内容是否覆盖。

## 输出模板

```markdown
## Non-Disclosure Agreement
[完整 NDA 正文，标注需审阅段]

### Clauses Requiring Legal Review
| Clause | Why It Needs Review | Consideration |
|--------|---------------------|---------------|

### Plain-Language Summary
[非法律读者能懂的简释]
```

## 输出命名规则

源文件未规定（命令态默认保存为 markdown，可导出 DOCX）

## 重要免责声明（原样保留）

**This is for informational purposes only and does not constitute legal advice. Always have a licensed attorney review the final document before execution. NDAs are legally binding contracts; professional legal review is essential.**

## 输入参数（源变量翻译为对话上下文）

- 一方公司名 / 地址 / 代表（姓名+职务）
- 二方公司名 / 地址 / 代表
- 信息共享类型（如商业计划、客户名单、技术规格、定价、源码）
- 管辖司法辖区（如美国加州、英格兰与威尔士）

## 流程（5 步）

1. **Clarify Requirements**：双方均为公司还是含个人？信息类型？单向还是 mutual（双向）？地理管辖？拟定时长？
2. **Structure the NDA**：按标准 8 段组织（见下）。
3. **Use Plain Language**：清晰易懂，首次出现术语即定义。
4. **Highlight Clauses Needing Legal Review**：在需定制/法律专长的段标注 `[⚠️ LEGAL REVIEW REQUIRED]` 并说明。
5. **Provide Context**：简述每段重要性、双方需做的决策、常见坑。

## Key Sections to Include（8 大必备条款，逐条照抄）

**Preamble（序言）**：清楚列出双方法定全名与地址；说明目的（探索潜在商业关系/合作/并购等）；定义生效日（Effective Date）。

**Definitions（定义）**：
- Confidential Information：界定何为保密（商业计划、财务、技术规格、客户名单等），含范围。
- Excluded Information：明确非保密内容（公开信息、独立开发信息、从无保密义务第三方处获得的信息）。

**Obligations（义务）**：接收方保密义务；信息获批用途；许可披露（员工/顾问/按需知密）；`[⚠️]` 注意标准（"与自有保密信息同等谨慎，但不低于合理谨慎"）。

**Permitted Disclosures（许可披露）**：可向谁透露（员工/顾问/按需知密）；要求接收方也同意保密；为法律强制披露设例外（尽可能含通知义务）。

**Term and Duration（期限）**：信息分享期；关系结束后保密义务存续多久；`[⚠️]` 不同信息类型期限不同（商业秘密需更长保护）。

**Return or Destruction（归还或销毁）**：应请求/终止时归还或安全销毁；可书面证明销毁完成；考虑接收方是否留一份合规副本。

**Remedies（救济）**：`[⚠️]` 违约可能造成不可弥补损害、可用禁令救济；救济不影响其他法定救济。

**General Provisions（通用条款）**：
- Governing Law and Jurisdiction：指定适用法域（如加州或英格兰）。
- `[⚠️]` Dispute resolution：诉讼/仲裁/调解。
- Severability：某条无效不影响其余。
- Entire Agreement：取代此前讨论。
- Amendments：仅经双方书面签署可修改。
- Counterparts：可签独立副本。

## 内容准则（Content Guidelines）

- plain language：写给小学文化读者，避免拉丁语与多余法律术语。
- clarity over precision：先清晰，法律精度由律师打磨。
- 必要时举例说明何为/非保密信息。
- 用具体信息类型让协议不泛泛而谈。
- 若信息类型显示仅一方分享，标为单向 NDA；双方则用双向措辞。

## 输出三段式（Output Format）

1. **Summary**：要点概览——双方、信息类型、关键期限与条款、管辖区。
2. **Full NDA Document**：完整、可定制的 NDA 正文。
3. **Customization Notes**：需法律审阅段、双方待决事项、常见修改、下一步（法律审阅/签署）。

## 重要提醒（Important Reminders）

- 这只是起点，非最终法律意见。
- 各辖区差异大；请相关辖区执业律师审阅。
- 某些行业（科技、医药、金融）有特定 NDA 惯例。
- 考虑双向（mutual）还是单向（one-way）需求。
- 想清期限：信息应被保护多久。
- 任一方签署前务必经律师审阅。

## Checkpoint

（源未设显式 checkpoint 引句；以下为重要提醒）
> "Always have an attorney review before any party signs."
> 任一方签署前务必经律师审阅。
