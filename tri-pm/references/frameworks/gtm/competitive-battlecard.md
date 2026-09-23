---
name: competitive-battlecard
description: 创建销售可用的竞争战斗卡——针对特定竞品对比定位、功能比较、异议处理与输赢规律；用于备战销售团队、制作竞争物料或回应「为何不选竞品 X」
source: pm-skills-main/pm-go-to-market/skills/competitive-battlecard/SKILL.md
domain: 上市
---

# 竞争战斗卡（Competitive Battlecard）

> 蒸馏自 `competitive-battlecard`｜域：上市｜源词数：约 320

## 必含章节清单（MUST-SECTIONS）

- [ ] Context — 任务上下文
- [ ] Instructions: Research the competitor — 研究竞品
- [ ] Battlecard Sections — 战斗卡字段结构（逐字段，见下）
- [ ] Keep it scannable — 保持可扫读
- [ ] Output — 落盘要求

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Further Reading（见文末，已合规保留）

## 逐段引导问题

**Context**：为所指定的竞品（源中以参数占位，本环境译为「对话中给定的竞品名」）创建竞争战斗卡。用联网搜索研究竞品当前产品、定价、定位与近期变化；若用户提供文件（功能清单、赢单输单数据、销售通话笔记），先读。

**Instructions — Step 1 Research the competitor（联网搜索）**：
- 当前产品与功能
- 定价层级与模式
- 目标市场与定位
- 近期产品发布或变化
- 已知优势与弱点
- 客户评价与情绪（G2、Capterra、Reddit）

**Step 2 Create the battlecard — 字段构成（逐字段照抄）**：

- **Company Overview**：成立时间、总部、融资/营收（若上市）；目标市场与 ICP；一句话定位。
- **Quick Comparison**（表格）：

  | Capability | Us | Them | Winner |
  |---|---|---|---|
  | [功能领域 1] | [我方做法] | [对方做法] | [Us/Them/Tie] |
  | [功能领域 2] | ... | ... | ... |
  | Pricing | ... | ... | ... |
  | Support | ... | ... | ... |

- **Where We Win**：[优势 1]：[证据点或客户原话]；[优势 2]：[对方缺失的具体能力]；[优势 3]：[更好做法及理由]。
- **Where They Win**：[对方优势 1]：[我方反定位]；[对方优势 2]：[如何弥补差距]。
- **Common Objections & Responses**（表格）：

  | Prospect Says | Respond With |
  |---|---|
  | "Competitor X 有 [功能]" | "[我方替代做法及为何更好]" |
  | "他们更便宜" | "[价值框架：TCO、ROI、隐性成本]" |
  | "他们更成熟" | "[我方优势：速度、创新、聚焦、支持]" |

- **Landmines to Plant**（向客户提问以暴露竞品弱点）："在 [我方擅长领域] 对贵团队有多重要？"；"你们评估过 [对方缺失的具体能力] 吗？"
- **Win/Loss Patterns**：我们常赢当：[规律]；我们常输当：[规律]；竞争交易关键差异化：[决定性因素]。

**Step 3 Keep it scannable**：销售代表需在通话中参考——用表格、粗体、短 bullet。保存为 markdown，便于打印或在 Notion/Confluence 分享。

## 输出模板

```markdown
## Competitive Battlecard: [我方产品] vs [竞品]

### Company Overview
[成立/总部/融资 · 目标市场与 ICP · 一句话定位]

### Quick Comparison
| Capability | Us | Them | Winner |
|---|---|---|---|

### Where We Win
- [优势]：[证据]

### Where They Win
- [优势]：[反定位]

### Common Objections & Responses
| Prospect Says | Respond With |
|---|---|

### Landmines to Plant
- [暴露弱点的提问]

### Win/Loss Patterns
- 常赢当：[…] 常输当：[…] 关键差异化：[…]
```

## 输出命名规则

源文件未规定固定文件名，仅要求「保存为 markdown」。

## 关键规则

- 销售一线实用件；保持可扫读（表格/粗体/短句）。
- 用联网搜索补齐竞品当前信息；用户文件优先于搜索。
- 字段须齐全：Company Overview / Quick Comparison / Where We Win / Where They Win / Objections / Landmines / Win-Loss。

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- [How to Design a Value Proposition Customers Can't Resist?](https://www.productcompass.pm/p/how-to-design-value-proposition-template) — 价值主张设计
