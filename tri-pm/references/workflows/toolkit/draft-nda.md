---
name: draft-nda
description: NDA 起草命令——按情境生成含司法辖区条款的保密协议，并标注需法律审阅段
source: pm-skills-main/pm-toolkit/commands/draft-nda.md
domain: 工具
---

# /draft-nda → 保密协议起草（命令态）

> 蒸馏自命令 `draft-nda`｜域：工具｜源词数：约 450
> **语法翻译**：源项目以 `/draft-nda` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。
> 能力内核引用技能态 `frameworks/toolkit/draft-nda.md`。

## 用途

为你的情境起草专业 NDA，覆盖信息类型、管辖区、期限，并明确标注需法律审阅的条款。

## 参数提示

`<parties and context>`（双方与背景）

## 调用示例（翻译为对话形态）

- 源：`/draft-nda Mutual NDA between our startup and a potential enterprise customer`
- 本环境等价说法：「帮我和一家潜在企业客户起草一份双向 NDA」
- 源：`/draft-nda One-way NDA for a freelance contractor accessing our codebase`
- 本环境等价说法：「一位自由承包商要访问我们的代码库，起草一份单向 NDA」

## 工作流步骤

1. **Gather Context** — 追问：双方是谁（公司名与角色）？双向还是单向？保护什么信息（商业秘密/代码/商业/客户数据）？管辖区（州/国）？期限？特殊关切（非竞争/非招揽/IP 归属）？
2. **Draft the NDA** — 应用 **draft-nda** 技能，生成完整 NDA：双方与序言、保密信息定义（含具体示例）、接收方义务、除外情形、期限与存续、归还/销毁、救济、准据法与管辖、标准 boilerplate（可分割/整体协议/修订）。〔引用技能：`**draft-nda**`〕
3. **Deliver** — 输出完整 NDA（标注段）、需法律审阅条款表、平实语言摘要；提议导出 DOCX 供签署。

## Checkpoint

（源未设 checkpoint 引句；以下为 Notes 提醒）
> "always recommend review by qualified legal counsel"
> 始终建议由合格律师审阅

## 输出模板

```markdown
## Non-Disclosure Agreement
[完整 NDA 正文，含标注段]

### Clauses Requiring Legal Review
| Clause | Why It Needs Review | Consideration |
|--------|---------------------|--------------|

### Plain-Language Summary
[非法律读者能懂的简释]
```

## 保存指令

源文件要求：保存为 markdown；可提议导出 DOCX 供签署。

## 下一步建议

- 将需法律审阅段交辖区律师审阅
- 视谈判情况调整为双向（mutual 通常更公平、更快）

## Further Reading

（源未提供 Further Reading，已丢弃）
