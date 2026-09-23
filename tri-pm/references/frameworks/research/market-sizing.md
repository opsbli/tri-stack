---
name: market-sizing
description: 用 TAM/SAM/SOM 估算市场规模，含自顶向下与自底向上两套算法
source: pm-skills-main/pm-market-research/skills/market-sizing/SKILL.md
domain: 研究
---

# 市场规模估算（TAM / SAM / SOM）

> 蒸馏自 `market-sizing`｜域：研究｜源词数：~780

## 必含章节清单（MUST-SECTIONS）

- [ ] Purpose — 目的
- [ ] Input — 输入（含市场边界约束）
- [ ] Analysis Steps — 分析步骤（7 步，含两套算法）
- [ ] Output Structure — 输出结构（含 TAM/SAM/SOM 与汇总表）
- [ ] Best Practices — 最佳实践

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Further Reading —（源外链全部不合规，已丢弃）

## 逐段引导问题

- **Input**：在指定市场约束（地理、行业垂直、客户类型等）内估算「目标产品/主题」（即用户提供的目标产品/主题）的市场规模。若用户提供市场研究、行业报告、财务数据或竞品信息，直接读取分析；用联网检索找当前市场数据、行业报告与增长预测。
- **Analysis Steps**：市场定义 → 自顶向下估算 → 自底向上估算 → SAM 范围 → SOM 估算 → 增长预测 → 假设映射。
- **Output Structure**：须含市场定义、TAM、SAM、SOM、汇总表、增长驱动、关键假设与风险。
- **Best Practices**：始终同时给两套估算做三角验证；联网检索当前行业数据并标注来源；区分基于价值（营收）与基于体量（用户/单位）的估算。

## 两套算法步骤（原样保留源描述）

**Algorithm 1 — Top-Down Estimation（自顶向下）**
> Start from total industry size and narrow to the relevant slice.
> 从行业总体规模出发，逐步收窄到相关切片。

**Algorithm 2 — Bottom-Up Estimation（自底向上）**
> Build from unit economics (customers × price × frequency) to cross-validate.
> 从单位经济（客户数 × 单价 × 频率）出发搭建，用以交叉验证。

两步在 TAM 处交叉验证（reconciliation），输出须同时呈现两种方法并说明取舍。

## 输出模板

```markdown
**Market Definition**
- Problem space and customer need
- Geographic and segment boundaries
- Key constraints or scoping decisions

**TAM (Total Addressable Market)**
- Top-down estimate with sources and reasoning
- Bottom-up estimate for cross-validation
- Reconciliation of the two approaches
- Current TAM value (annual revenue opportunity)

**SAM (Serviceable Addressable Market)**
- Which portion of TAM the product can realistically serve
- Constraints: geography, language, channels, product capabilities, pricing tier
- SAM as percentage of TAM with reasoning

**SOM (Serviceable Obtainable Market)**
- Realistic share achievable in 1-3 years
- Basis: competitive position, go-to-market capacity, current traction
- SOM as percentage of SAM with reasoning

**Market Summary Table**
| Metric | Current Estimate | 2-3 Year Projection |
|--------|-----------------|---------------------|
| TAM    |                 |                     |
| SAM    |                 |                     |
| SOM    |                 |                     |

**Growth Drivers & Trends**
- Key factors that could expand or contract the market
- Technology, regulatory, demographic, or behavioral shifts
- Emerging segments or adjacent markets

**Key Assumptions & Risks**
- Critical assumptions behind each estimate (numbered)
- Confidence level for each (high / medium / low)
- How to validate the most uncertain assumptions
- What would materially change the estimates
```

## 输出命名规则

源文件未规定具体落盘文件名。

## 关键规则

- 始终同时提供自顶向下与自底向上估算以做三角验证（triangulate）。
- 用联网检索获取当前行业数据、分析师报告、市场基准。
- 为市场数据标注来源——避免无支撑数字。
- 明确假设；标注「估算」vs「数据」。
- 区分基于价值（营收）与基于体量（用户/单位）的估算。
- 国际市场考虑货币与购买力平价（PPP）。
- 标注置信区间宽的区域。
- 推荐具体数据源或研究以 sharpen 估算。

## Checkpoint

> （源未设 checkpoint）

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
