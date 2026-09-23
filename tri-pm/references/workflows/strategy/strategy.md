---
name: strategy
description: 用九段式战略画布构建完整产品战略文档——从愿景到防御性
source: pm-skills-main/pm-product-strategy/commands/strategy.md
domain: 战略
---

# /strategy → 产品战略画布

> 蒸馏自命令 `strategy`｜域：战略｜源词数：约 480
> **语法翻译**：源项目以 `/strategy` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

用九段式 Product Strategy Canvas 构建完整产品战略文档，覆盖愿景、细分、价值主张、取舍、指标、增长、能力、防御性。

## 参数提示

`<product or company>`（产品名或公司名；留空则 Agent 追问产品信息）

## 调用示例（翻译为对话形态）

- 源：`/strategy AI-powered design tool for non-designers`
- 本环境等价说法：「用九段式战略画布，为『面向非设计师的 AI 设计工具』构建产品战略」
- 源：`/strategy [upload existing strategy doc, pitch deck, or business plan]`
- 本环境等价说法：「我上传一份现有战略文档/商业计划书，请你提炼或挑战其中的战略」
- 源：`/strategy`（空）
- 本环境等价说法：「帮我做产品战略」（Agent 会追问产品信息）

## 工作流步骤

1. **理解产品** — 接受产品描述、上传文档（战略/Pitch/PRD/商业计划）、或现有战略来打磨。追问：产品做什么、服务谁？所处阶段（想法/MVP/增长/成熟）？商业模式？为何需要战略文档（新品/转型/年度规划/融资）？〔引用技能：`**product-strategy**`、`**product-vision**`〕
2. **构建战略画布** — 依次走完 9 段：①Vision 激励人心的北极星 ②Target Segments 服务谁（及不服务谁）③Pain Points & Value 解决的问题与创造的价值 ④Value Propositions 每细分的 JTBD 价值 ⑤Strategic Trade-offs 选择不做什么（与做什么同等重要）⑥Key Metrics 成功度量 ⑦Growth Engine 获客与扩展 ⑧Core Capabilities 自建/维持 ⑨Defensibility 难复制之处（网络效应/数据/品牌/转换成本）。每段给具体内容而非泛泛建议。
3. **生成战略文档** — 按下方输出模板产出 markdown，含 Strategic Risks（前 3 大可能证伪战略的因素）与 Next Steps。
4. **提供下一步** — 建议：是否要构建 Lean Canvas 或 Business Model Canvas？是否基于战略建路线图？是否做宏观环境扫描以压力测试假设？是否基于第 6 段定义 OKR？

## Checkpoint

> （源未设 checkpoint）

## 输出模板

```markdown
## Product Strategy: [Product Name]
**Date**: [today]  **Stage**: [idea/MVP/growth/mature]  **Author**: [user]

### 1. Vision
[激励、可达成、有情感——最多 2-3 句]
### 2. Target Segments
| Segment | Size | Pain Level | Current Alternative | Priority |
|---------|------|-----------|-------------------|----------|
**Primary segment**: [who and why]   **Explicitly not serving**: [who and why]
### 3. Pain Points & Value Created
[每细分：问题、当前成本、方案交付的价值]
### 4. Value Propositions
**For [Segment A]**: When [situation], they want [motivation], so they can [outcome]
### 5. Strategic Trade-offs
| We Choose | Over | Because |
|-----------|------|---------|
### 6. Key Metrics
- **North Star**: [metric]  - **Input Metrics**: [3-5 levers]  - **Health Metrics**: [guardrails]
### 7. Growth Engine
[获客/激活/扩展的具体机制]
### 8. Core Capabilities
| Capability | Build/Buy/Partner | Investment Level | Timeline |
### 9. Defensibility
[护城河类型：网络效应/数据/品牌/转换成本/规模经济]
### Strategic Risks
[前 3 大风险]
### Next Steps
[社交化/测试/构建]
```

## 保存指令

保存为 markdown（源未规定具体文件名，建议 `Product-Strategy-[product-name].md`）。

## 下一步建议

- 构建 Lean Canvas 或 Business Model Canvas 以补充商业模式视角
- 基于本战略创建产品路线图
- 运行宏观环境扫描（SWOT/PESTLE/波特五力）压力测试假设
- 基于第 6 段定义 OKR

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
