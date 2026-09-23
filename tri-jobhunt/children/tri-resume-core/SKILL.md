---
name: tri-resume-core
slug: tri-resume-core
version: 1.0.1
displayName: 简历优化核心
description: tri-jobhunt 的 children 子 skill，由主 skill(R1/R2/R4/R10/R11)委派。ATS 兼容、要点量化、排版格式、分区构建、定向定制、版本管理。复用共享 references/ats-compliance / quantification / star-framework。
summary: 简历优化核心子 skill。
tags: [resume, ats, quantify, tailorm format, versions]
license: MIT
---

# tri-resume-core · 简历优化核心（children 子 skill）
> 产物落盘：本 children 不独立落盘——用户成果物由主 skill `tri-jobhunt` 统一落 `.tribro/tri-jobhunt/`（`.tribro/` 不存在时由主 skill 先创建）；链路审计文档由主 skill 落 `.tribro/forge/tri-jobhunt/`。本 children 随主 skill 包分发，遵循主 skill §落盘规则。


> 由主 skill `tri-jobhunt` 依 R1/R2/R4/R10/R11 委派激活，**不对外暴露**。这是求职材料的心脏：
> 把简历从「duty 罗列」改成「可过 ATS、可打动 HR」的成就式文档。复用共享 references。

## 职责

- **ATS 兼容 + 关键词优化（R1）**：解析 → 提词 → 算分 → 摆放 → 报表。
- **要点量化（R2）**：弱要点 → STAR/XYZ → 加指标 → 压缩（`star-framework.md` + `quantification.md`）。
- **排版格式（R1）**：页长/边距/字号/行距按 `ats-compliance.md` §二默认值。
- **分区构建**：Summary/技能/经历/教育/补充按章节顺序。
- **定向定制（R4）**：HIGHLIGHT 不 FABRICATE，按 JD 重排与改措辞。
- **版本管理（R10）**：master 单源 + `[Last]_[Role]_[Company]_[Date]` 命名 + 追踪表。

## 决策要点（引用共享层）

- ATS 铁律/格式参数/章节顺序/真实性边界 → `references/ats-compliance.md`。
- 六类指标/五估算/四模板/动词库 → `references/quantification.md`。
- STAR/XYZ/CAR 与 bullet 复核 → `references/star-framework.md`。

## 关键动作（R1/R2/R4）

| 子任务 | 动作 | 分配 |
|---|---|---|
| ATS 分析 | 算 Match Score（目标 ≥80%），列格式化问题（✅❌⚠️），给关键词摆放 | 关键词优先级 Summary(5-8)>Skills>Bullets |
| 要点量化 | 每条改写成 achievement + ≥1 数字 + ≤2 行；无精确数用保守/区间/最小边界 | 每 bullet ≤2-3 数字 |
| 定向定制 | 重排经历顺序、调 Summary、加 JD 关键词、改 bullet 语言 | **NEVER 编造技能/数字/经历** |

## 输出

- ATS 报表：`# ATS COMPATIBILITY REPORT`（Overall Score + Formatting Issues + Keyword Analysis + Recommended Changes + Estimated New Match）。
- 量化报表：`# RESUME QUANTIFICATION`（Analysis Summary + Quantified Bullets + Estimation Notes）。
- 定制计划：`# RESUME TAILORING PLAN`（Before/After + Keywords Added + Estimated Match）。
- 版本管理：`# RESUME VERSION MANAGEMENT`（Master Status + Active Versions + Update Queue）。

## 边界

- 真实性是铁律：HIGHLIGHT 不 Fabricate，NEVER 加假技能/假数字/编造荣誉（R11）。
- 双受众（ATS + HR）：在线投 .docx/.pdf，直发可用 .pdf。
- 高敏感（机密数据）用百分比/相对影响替代绝对数。