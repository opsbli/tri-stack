---
name: privacy-policy
description: 隐私政策生成命令——覆盖数据收集、使用、存储与合规（GDPR/CCPA），标注需法律审阅段
source: pm-skills-main/pm-toolkit/commands/privacy-policy.md
domain: 工具
---

# /privacy-policy → 隐私政策生成（命令态）

> 蒸馏自命令 `privacy-policy`｜域：工具｜源词数：约 550
> **语法翻译**：源项目以 `/privacy-policy` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。
> 能力内核引用技能态 `frameworks/toolkit/privacy-policy.md`。

## 用途

为产品起草全面的隐私政策，覆盖数据类型、管辖区、合规（GDPR/CCPA），并标注需法律审阅条款。

## 参数提示

`<product and data handling context>`（产品与数据处理背景）

## 调用示例（翻译为对话形态）

- 源：`/privacy-policy SaaS analytics tool that collects user behavior data — serving US and EU customers`
- 本环境等价说法：「我们有一个 SaaS 分析工具，收集用户行为数据，服务美欧客户，请起草隐私政策」
- 源：`/privacy-policy Mobile app with location data and third-party integrations`
- 本环境等价说法：「一款含位置数据与第三方集成的移动 App，请起草隐私政策」

## 工作流步骤

1. **Gather Context** — 追问：什么产品/服务？收集什么数据（个人/使用/cookie/位置/支付）？用户在哪里（决定 GDPR/CCPA 等）？第三方共享（分析/广告/集成）？存储地与时长？年龄限制（COPPA）？
2. **Draft the Policy** — 应用 **privacy-policy** 技能，生成段落覆盖：收集什么及如何收集、使用目的、处理法律依据（GDPR）、共享与第三方、留存与删除、用户权利（访问/删除/可携/退出）、Cookie、安全措施、儿童隐私（如适用）、跨境传输、联系信息、更新流程。〔引用技能：`**privacy-policy**`〕
3. **Deliver** — 输出完整政策、合规清单表、需法律审阅条款表、实施清单；提议 DOCX 导出。

## Checkpoint

（源未设 checkpoint 引句；以下为 Notes 提醒）
> "legal counsel should review before publishing"
> 发布前应由法律顾问审阅

## 输出模板

```markdown
## Privacy Policy: [Product]
[完整政策正文]

### Compliance Checklist
| Regulation | Status | Notes |
|-----------|--------|-------|

### Clauses Requiring Legal Review
| Clause | Why | Priority |
|--------|-----|----------|

### Implementation Checklist
- [ ] Cookie consent banner
- [ ] Data subject request process
- [ ] Data processing records
- [ ] DPA with processors
```

## 保存指令

源文件要求：保存为 markdown；可提议导出 DOCX。

## 下一步建议

- 将需法律审阅段交辖区数据隐私律师审阅（GDPR/CCPA 具体要求不可近似）
- 数据实践变化时即更新政策，而非仅年度更新

## Further Reading

（源未提供 Further Reading，已丢弃）
