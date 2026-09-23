---
name: tri-jd
slug: tri-jd
version: 1.0.1
displayName: JD 匹配分析
description: tri-jobhunt 的 children 子 skill，由主 skill(D R3)委派。分析职位描述、算人岗匹配分、识别红旗与非之项、给出投否决策，并产出求职信谈点。复用共享 references/ats-compliance。
summary: JD 分析与投否决策子 skill。
tags: [job-description, match-score, ats, applicant]
license: MIT
---

# tri-jd · JD 匹配分析（children 子 skill）
> 产物落盘：本 children 不独立落盘——用户成果物由主 skill `tri-jobhunt` 统一落 `.tribro/tri-jobhunt/`（`.tribro/` 不存在时由主 skill 先创建）；链路审计文档由主 skill 落 `.tribro/forge/tri-jobhunt/`。本 children 随主 skill 包分发，遵循主 skill §落盘规则。


> 由主 skill `tri-jobhunt` 依 R3 委派激活（用户给 JD 问「值不值得投 / 匹配多少」），**不对外暴露**。
> 遵循父 skill 的量化诚实与真实性边界。复用 `references/ats-compliance.md` 匹配分公式。

## 职责

- 解析 JD，提取 Required 与 Preferred 需求。
- 计算综合匹配分，给出投否建议与投递策略。
- 识别红旗（工作负荷 / 文化 / 薪酬）与否决项。
- 输出求职信谈点（供 tri-docs 使用）。

## 决策方法

| 步骤 | 动作 |
|---|---|
| 1 提需求 | 分 Required（硬性）与 Preferred（加分） |
| 2 算分 | `Overall = (Required%×0.7) + (Preferred%×0.3)` |
| 3 分级 | 90-100 过度合格 / 75-89 优秀立即投 / 60-74 良好配强求职信 / 50-59 stretch / <50 除非 dream job |
| 4 否决 | 执照/清评缺失、经验 <要求 50%+、「required」学位缺、地点不符 → 除非 dream job 否则否决 |
| 5 红旗 | "wear many hats" / "fast-paced" / "Rockstar" / "competitive salary" / "equity-heavy" 等 |
| 6 策略 | 投 10-15 个精准（70-90% 匹配）而非 50+ 广撒网 |

## 输出

`# JOB ANALYSIS REPORT`：含 OVERALL MATCH SCORE、Requirements Breakdown、Strengths、
Gaps、Customization Strategy、Cover Letter Talking Points、Red Flags、Decision Factors。

## 边界

- 模糊 JD（缺职责/级别）标注不确；一个 JD 多角色、内部职位、重贴职位单独提示。
- 高敏感（薪资）只提供方法与框架，不替代专业薪酬意见。
- 量化诚实：匹配分基于可辩护的需求数字，NEVER 虚报匹配率。