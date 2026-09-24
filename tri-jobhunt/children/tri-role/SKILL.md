---
name: tri-role
slug: tri-role
version: 1.0.1
displayName: 专项角色简历
description: tri-jobhunt 的 children 子 skill，由主 skill(R9)委派。叠加 技术/高管/学术/创意/转行 五角色的差异增量到通用求职方法论，产出角色专属简历与定位。
summary: 专项角色简历子 skill。
tags: [tech, executive, academic, creative, career-change]
license: MIT
---

# tri-role · 专项角色简历（children 子 skill）
> 产物落盘：本 children 不独立落盘——用户成果物由主 skill `tri-jobhunt` 统一落 `.tribro/jobhunt/`（`.tribro/` 不存在时由主 skill 先创建）；链路审计文档由主 skill 落 `.tribro/forge/jobhunt/`。本 children 随主 skill 包分发，遵循主 skill §落盘规则。


> 由主 skill `tri-jobhunt` 依 R9 委派激活，**不对外暴露**。五角色**不是独立方法论**，而是
> 「通用求职方法论 × 特定受众口味」——本子 skill 只叠加差异增量，通用规则从共享 references 取。

## 职责

识别用户角色（技术/高管/学术/创意/转行）→ 叠加 `references/role-branches.md` 差异 →
套用对应角色章节结构、公式与指标 → 产出角色专属简历 + 定位挂注。

## 决策要点（引用 role-branches.md）

| 角色 | 结构/公式/特殊点 |
|---|---|
| 技术 | 章节含 GitHub；`[Action Verb]+[Technical What]+[Scale/Impact]+[Technology Used]`；技术指标四类 |
| 高管 | 2-3 页；7 节含 P&L；`[Leadership]+[Strategic Initiative]+[Outcome at Scale]`；权力动词 |
| 学术 | CV 12 节；按职位调顺序；出版/资助/教学格式；阶段长度表 |
| 创意 | 两版本方法（ATS 版 + 设计版）；设计三原则 + 6 秒可扫描 |
| 转行 | 迁移技能框架 + 术语翻译 + Why 四段叙事 + Functional 格式 |

## 关键动作

- 角色分支**仅叠加角色差异**、不重写通用方法论（R2/R4 仍走 tri-resume-core 通用层）。
- 机密数据（高管 P&L 等）用百分比/范围/相对影响替代绝对数。
- 真实性边界（R11）：角色化时可加行业术语、可重排真实信息，NEVER 虚构职位/成果。

## 输出

按角色产出：`# TECH/EXECUTIVE RESUME` / `# ACADEMIC CV` / `# CREATIVE RESUME STRATEGY` /
`# CAREER CHANGE TRANSLATION`，含 Positioning Notes（叙事主题/差异化）。

## 边界

- 只服务求职/转行/学术求职场景；高管面向猎头/董事会/PE-VC 需调整受众口径。
- 转行理由须为兴趣进化，禁「burned out / hate job / more money」。