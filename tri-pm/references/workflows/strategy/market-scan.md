---
name: market-scan
description: 一次性宏观环境扫描——SWOT、PESTLE、波特五力、安索夫矩阵综合
source: pm-skills-main/pm-product-strategy/commands/market-scan.md
domain: 战略
---

# /market-scan → 宏观环境分析

> 蒸馏自命令 `market-scan`｜域：战略｜源词数：约 560
> **语法翻译**：源以 `/market-scan` 斜杠调用；本环境以下「工作流步骤」即等价编排，由 Agent 按步执行。

## 用途

运行多个战略分析框架以理解竞争与宏观环境，将 SWOT、PESTLE、波特五力、安索夫矩阵整合为单一战略概览。

## 参数提示

`<product, market, or industry>`（产品/市场/行业；可附市场简报或战略文档）

## 调用示例（翻译为对话形态）

- 源：`/market-scan EdTech market for corporate learning`
- 本环境等价说法：「对企业学习的 EdTech 市场做宏观环境扫描」
- 源：`/market-scan Our fintech product — preparing for board strategy review`
- 本环境等价说法：「我们的金融科技产品正准备董事会战略评审，请做市场扫描」

## 工作流步骤

1. **理解上下文** — 追问：分析什么产品/公司/市场？目的（战略规划/市场进入/融资准备/年度评审）？聚焦哪些框架还是全跑？当前市场地位？
2. **运行分析**（顺次引用，后一框架承接前一洞察）：
   - **SWOT**〔引用：`**swot-analysis**`〕：内部优/劣，外部机/威，每象限可行动建议。
   - **PESTLE**〔引用：`**pestle-analysis**`〕：政治/经济/社会/技术/法律/环境，每因素评估影响与周期。
   - **Porter's Five Forces**〔引用：`**porters-five-forces**`〕：竞争对抗/供应商/买家/替代品/新进入者，给行业吸引力评级。
   - **Ansoff Matrix**〔引用：`**ansoff-matrix**`〕：市场渗透/市场开发/产品开发/多元化，风险调整后的增长机会。
3. **综合（Synthesize）** — 跨框架交叉：Converging signals（多框架共识）、Strategic imperatives（跨分析关键行动）、Key risks（需缓解的威胁）、Growth opportunities（最佳风险调整机会）。
4. **生成报告** — 按下方案板产出 markdown。
5. **提供下一步** — 建议：基于发现建产品战略？分析波特识别的具体竞品？为市场渗透机会设计定价策略？

## Checkpoint

> （源未设 checkpoint）

## 输出模板

```markdown
## Strategic Market Scan: [Market/Product]
**Date**: [today]  **Purpose**: [战略规划/市场进入/...]

### Executive Summary
[5-7 句覆盖战略态势与关键建议]

### SWOT Analysis
| Strengths | Weaknesses |   | Opportunities | Threats |
| [内部正面] | [内部负面] |   | [外部正面] | [外部负面] |
**SWOT Actions**: [杠杆 S+O，缓解 W+T]

### PESTLE Analysis
| Factor | Current State | Impact | Trend | Timeframe |
| Political/Economic/Social/Technological/Legal/Environmental | | H/M/L | | |

### Porter's Five Forces
| Force | Intensity | Key Drivers | Implications |
| Rivalry/Supplier/Buyer/Substitutes/NewEntrants | | | |
**Industry Attractiveness**: [High/Medium/Low]

### Ansoff Growth Matrix
| Strategy | Opportunity | Risk Level | Investment | Priority |
| Penetration/Development/Product/Diversification | | Low/Med/High | | H/M/L |

### Cross-Framework Synthesis
**Converging signals**: ...  **Strategic imperatives**: ...  **Key risks**: ...  **Best opportunities**: ...

### Strategic Recommendations
1. [有多框架证据支撑的建议] ...
### Monitoring Plan
| Signal | What to Watch | Source | Check Frequency |
```

## 保存指令

保存为 markdown（建议 `Market-Scan-[market].md`）。

## 下一步建议

- 基于发现构建产品战略
- 深入分析波特识别出的具体竞品
- 为市场渗透机会设计定价策略

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
