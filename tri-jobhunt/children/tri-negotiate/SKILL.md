---
name: tri-negotiate
slug: tri-negotiate
version: 1.0.1
displayName: 薪资谈判与 Offer 比较
description: tri-jobhunt 的 children 子 skill，由主 skill(R7/R8)委派。研究市场薪酬、算总薪酬、建反报价脚本，及跨 Offer 总薪酬与加权矩阵决策。
summary: 薪资谈判与 Offer 比较子 skill。
tags: [salary, negotiation, offer, compensation]
license: MIT
---

# tri-negotiate · 薪资谈判与 Offer 比较（children 子 skill）
> 产物落盘：本 children 不独立落盘——用户成果物由主 skill `tri-jobhunt` 统一落 `.tribro/tri-jobhunt/`（`.tribro/` 不存在时由主 skill 先创建）；链路审计文档由主 skill 落 `.tribro/forge/tri-jobhunt/`。本 children 随主 skill 包分发，遵循主 skill §落盘规则。


> 由主 skill `tri-jobhunt` 依 R7/R8 委派激活，**不对外暴露**。先算清总薪酬，再定谈判与决策。
> 高敏感内容只提供方法与框架，不替代专业薪酬/法律顾问意见。

## 职责

- **薪资谈判（R7）**：市场四分位 → TotalComp → 反报价脚本 → 5 场景话术。
- **Offer 比较（R8）**：总薪酬四分类 → 加权决策矩阵 → 四自我提问。

## 关键公式

| 公式 | 内容 |
|---|---|
| 总薪酬 | `Total Comp = Base + Bonus + Equity + Benefits`；区分 Year 1(含 sign-on) vs Ongoing |
| 八谈判维度 | Base / Signing / Annual Bonus / Equity / Benefits / Perks / Start date / Title |
| 市场四分位 | 25th / 50th / 75th / 90th |
| 股权 | RSUs = 现价×股数；Options = 现价-行权价；Vesting 4 年 1 cliff / Refresh |
| 加权矩阵 | `Weighted = Σ(score_i × weight_i)`；非货币四因素 Career Growth / Work-Life / Team-Culture / Risk |
| 四自我提问 | Gut Check / Monday Morning / Learning / Risk Test |

## 关键动作

- 谈判时间线：24-48h 研究 → 反报价 → 谈判 → 书面确认。
- 反报价框架：热情 → 重申价值 → 明确要价 → 给理由 → 开放式讨论。
- 5 场景脚本：报价偏低 / 先被问期望 / 基本工资不让 / 有竞争 offer / 被问现薪。
- 心态数据：多数雇主预期谈判；不谈判有长期机会成本。
- Offer 比较：将年假/远程折成 $ 值（如 10 days×$575/day）；期权可归零风险须明示。

## 输出

- `# SALARY NEGOTIATION STRATEGY`：Market Research + Their Offer + Your Counter + Script + Pushback Plan。
- `# JOB OFFER COMPARISON`：Offers + Total Comp 表 + Non-Monetary 表 + Weighted Analysis + Recommendation + Clarify Questions + Negotiation Op。

## 边界

Do's/Don'ts 各 9 条；总薪酬对比分 A/B 公司与 Year1 vs Ongoing；**NEVER 只看 base 做决定**。
外语版本按当地劳动法调整（「被问现薪」合法性随国家不同）。