---
name: tri-jobhunt-full-testcases
description: tri-jobhunt v1.0.3 全量能力测试用例（基于 tri-jobhunt v1.0.3）
version: 1.0.3
---

# tri-jobhunt 全量测试用例

> 测试对象：`tri-jobhunt` 主 skill（单入口路由 + 6 children 子 skill + references 共享层）
> 版本联动：测试基于 **tri-jobhunt v1.0.3**（与 SKILL.md / CHANGELOG.md 版本一致，约束 14）。

## 零、能力清单（全量扫描结果）

分组约定：A 元数据 / B 强制执行契约 / C 输入契约 / D 核心方法论 / E 自检声明 / F 交付产物 / G 职责边界 / H 质量标准。

| 编号 | 分组 | 能力点 | 规范 |
|---|---|---|---|
| 1 | A | frontmatter 八字段齐全，version=1.0.3 | family-spec §二 |
| 2 | A | description 含「支持独立安装，含上游依赖检测2态逻辑」 | 约束 2 |
| 3 | B | 强制执行契约置顶 + 最高优先级 + 第零步版本门 | 约束 3/22 |
| 4 | B | 单入口强制（子 skill 不外暴露） | 方法论 |
| 5 | B | R1-R11 分发强制 + 共享 references 复用 | 约束 4 |
| 6 | B | 真实性把关 R11 + 量化诚实 | 方法论 |
| 7 | C | 输入契约：请求文本/简历/JD/角色 | family-spec §3.5 |
| 8 | D | 单入口分发范式 + 知识装配顺序 | 约束 25 |
| 9 | D | R1-R11 决策规则（映射到 6 子 skill） | jobhunt-routes §一 |
| 10 | D | references 五件套就位 + grep 模式 | 约束 19 |
| 11 | D | 六 children 子 skill 就位且 SKILL.md 非空 | family-spec §4.5 |
| 12 | E | 自检句资源锚定格式（触发源=用户显式调用，已读取 jobhunt-references） | 横向型例外 |
| 13 | F | 交付产物机制：求职物料/子skill产物/追踪表 | §交付产物 |
| 14 | G | 职责边界：与 tri-intent/content/coding/fix/review 不重叠 | 约束 8 |
| 15 | H | 质量标准：单入口/ATS/量化/真实性 | §质量标准 |
| 16 | H | 完成判据（结束态 vs 停车态） | 约束 24 |
| 17 | H | 进化契约三要素（反馈点/沉淀位/修订触发） | 约束 23 |
| 18 | H | 落盘规则：.tribro/skills/<slug>/，NEVER LICENSE/.gitignore | 约束 7/11 |

## 一、用例

| 用例# | 输入 | 预期 | 校验 |
|---|---|---|---|
| T01 | 用户显式 `/tri-jobhunt` 优化简历 ATS | 命中 R1 → 分发 tri-resume-core → 产出 ATS 报表 | grep `# ATS COMPATIBILITY REPORT` |
| T02 | 用户要求「改善 bullet / 加量化」 | 命中 R2 → STAR/XYZ + 指标 | grep `# RESUME QUANTIFICATION`；每 bullet ≥1 数字 |
| T03 | 用户给 JD 问「值不值得投」 | 命中 R3 → tri-jd → 匹配分 0.7R+0.3P + 红旗 + 投否建议 | grep `# JOB ANALYSIS REPORT` |
| T04 | 需定向定制 | 命中 R4 → Highlight 不 Fabricate + master 版本 | grep `# RESUME TAILORING PLAN` |
| T05 | 写求职信/冷邮件/LinkedIn | 命中 R5 → tri-docs 对应模板 | grep `# COVER LETTER` / `Subject: ` |
| T06 | 准备面试 | 命中 R6 → STAR 库五类 + 预测题 | grep `# INTERVIEW PREP` |
| T07 | 薪资谈判 | 命中 R7 → TotalComp + 反报价脚本 | grep `# SALARY NEGOTIATION STRATEGY` |
| T08 | 多 Offer 比较 | 命中 R8 → 加权矩阵 + 四提问 | grep `# JOB OFFER COMPARISON` |
| T09 | 技术/高管简历 | 命中 R9 → tri-role 叠加角色差异 | grep `# EXECUTIVE RESUME` / `# TECH RESUME` |
| T10 | 用户填了一版「编造业绩」 | R11 拦截 → 提示真实性边界 | 产出含「HIGHLIGHT 不 Fabricate」提示 |
| T11 | 子 skill 缺失 | 上游依赖检测 B 态 → 降级提示补齐 | 输出「子 skill 未就位」 |
| T12 | 版本门 | 运行 `scripts/check_update.py --slug tri-jobhunt --json` | 退出码 <20 且输出合法 JSON（state ∈ A/B/C/D） |

## 用例统计

- 用例总数注数：T01-T12 共 12 条，覆盖能力点 1-18 全部。
- 分布：B 契约 4 条 / C 输入 1 / D 方法论 5 / E 1 / G 1 / H 3 / 门禁自检 1。
- 审计方式：文本 grep + 脚本运行（T12）+ 目录存在性（T11/10）。

## 生成信息

- 生成时间：2026-08-30
- 生成方式：tri-forge 门②骨架生成，审计方式为逐能力点映射。