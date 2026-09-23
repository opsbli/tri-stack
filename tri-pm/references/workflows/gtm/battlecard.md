---
name: battlecard
description: 创建销售可用的竞争战斗卡——定位、功能比较、异议处理与取胜策略
source: pm-skills-main/pm-go-to-market/commands/battlecard.md
domain: 上市
---

# /battlecard → 竞争战斗卡（Competitive Battlecard）

> 蒸馏自命令 `battlecard`｜域：上市｜源词数：约 420
> **语法翻译**：源项目以 `/battlecard` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

创建简洁、销售可用的战斗卡，帮助团队在针对特定竞品的交易中取胜。含定位、功能比较、异议处理与对话策略。

## 参数提示

（源 `argument-hint`：`<your product> vs <competitor>`——我方产品 vs 竞品）

## 调用示例（翻译为对话形态）

- 源：`/battlecard Our CRM vs Salesforce`
- 本环境等价说法：「做一张我们的 CRM 对 Salesforce 的战斗卡」
- 源：`/battlecard ProjectFlow vs Monday.com for mid-market teams`
- 本环境等价说法：「做一张 ProjectFlow 对 Monday.com（中端团队）的战斗卡」
- 源：`/battlecard [upload competitor materials or win/loss data]`
- 本环境等价说法：「（上传竞品材料或赢单输单数据）据此做战斗卡」

## 工作流步骤

1. **Identify the Matchup（确认对阵）** — 〔引用技能：无，纯澄清〕
   - 你的产品与具体竞品；典型买家是谁在二者间选择？
   - 是否有赢单输单数据或销售反馈？通常出现在哪个交易阶段（早期评估/最终决策/替换）？
2. **Research the Competitor（研究竞品）** — 〔引用技能：**competitive-battlecard**，配合联网搜索〕
   - 当前产品能力与近期发布；定价模式与公开定价；目标市场与定位；已知弱点（评论/论坛/反馈）；近期公司动态（融资/领导层/战略转变）。
3. **Generate Battlecard（生成战斗卡）** — 输出下方模板〔引用技能：无，落盘〕
   - 含 Quick Summary、Positioning、Feature Comparison、Pricing Comparison、Objection Handling、Landmines to Plant、Trap Questions to Expect、Win/Loss Patterns、Conversation Starters、Resources。
4. **Offer Next Steps（建议下一步）** — 〔引用技能：无〕
   - 是否为其他竞品做战斗卡？是否做全市场竞争分析？是否基于本卡起草面向客户的对比内容？是否据竞争洞察更新定位？

## Checkpoint

> （源未设 checkpoint；Step 2 后调用 competitive-battlecard skill 即隐含验收点）

## 输出模板

```markdown
## Competitive Battlecard: [我方产品] vs [竞品]

**Last updated**: [今天]
**Use when**: [该竞品出现的情境]

### Quick Summary
**We win when**: [我方有优势时的买家画像与情境]
**We lose when**: [竞品有优势时的买家画像与情境]
**Key differentiator**: [一句话]

### Positioning
**How they position**: [其信息]
**How we position against them**: [我方反定位]

### Feature Comparison
| Capability | Us | Them | Verdict |
|-----------|-----|------|---------|
| [能力] | [状态] | [状态] | [优势方] |

### Pricing Comparison
| Dimension | Us | Them | Notes |
|----------|-----|------|-------|

### Objection Handling
| Objection | Response | Proof Point |
|----------|---------|------------|
| "他们有 [功能]" | [回应] | [证据] |
| "他们更便宜" | [回应] | [TCO 分析] |
| "他们更成熟" | [回应] | [反制] |

### Landmines to Plant
[向客户提问以暴露竞品弱点]
1. "问他们关于 [话题]——其回答会暴露 [弱点]"

### Trap Questions to Expect
[竞品会鼓励客户问你的问题]
1. "[问题]" —— 如何回应：[回应]

### Win/Loss Patterns
**We typically win because**: [Top 3 原因]
**We typically lose because**: [Top 3 原因]

### Conversation Starters
**If they're already using [竞品]**: [替换交易打法]
**If they're evaluating both**: [竞争评估打法]

### Resources
- [反击该竞品的客户故事/案例]
- [第三方对比或评论]
- [针对该竞争情境优化的演示脚本]
```

## 保存指令

保存为 markdown（源要求 Save as markdown；未规定具体文件名）。

## 下一步建议

- 「要我为其他竞品做战斗卡吗？」
- 「要我做市场的完整竞争分析吗？」
- 「要我基于本卡起草面向客户的对比内容吗？」
- 「要我据竞争洞察更新定位吗？」

## Further Reading

（源命令未提供 Further Reading，已丢弃）
