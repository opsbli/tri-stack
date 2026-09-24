# 编码需求说明书（requirements.md）

> **本模板由 `tri-prototype` 产出，供 `tri-coding` 门② 直接消费。**
> 产出后**无缝衔接** tri-coding 的门②（设计审批）流程——tri-coding 读取本文件，按其九章流程产出 `design.md`。
> 用户也可以将本文件用于 tri-plan（产出 `plan-brief.md` → `plan.md`）。

---

## 一、项目概述

| 项 | 内容 |
|---|---|
| 项目名称 | {{project_name}} |
| 项目背景 | {{project_background}} |
| 目标用户 | {{target_users}} |
| 核心价值 | {{core_value}} |
| 原型来源 | {{prototype_source}}（{{prototype_platform}}） |
| PRD 来源 | {{prd_source}} |
| 解析保真度 | {{fidelity_level}} |

## 二、功能需求

> 从原型与 PRD 中提取的功能列表，每条 MUST 有出处（原型页面名 / PRD 章节号）与验收标准。

| # | 功能名称 | 功能描述 | 优先级 | 出处 | 验收标准 |
|---|---|---|---|---|---|
| 1 | {{feature_name}} | {{feature_desc}} | P0/P1/P2 | 原型:{{page_name}} / PRD:{{prd_section}} | {{acceptance_criteria}} |

## 三、页面清单与交互规则

> 从原型中提取的页面结构与交互规则。

### 页面清单

| # | 页面名称 | 路由 | 组件列表 | 交互规则 |
|---|---|---|---|---|
| 1 | {{page_name}} | {{route}} | {{components}} | {{interactions}} |

### 全局交互

- {{global_interaction}}

## 四、业务规则

> 从 PRD 中提取的业务规则。冲突项 MUST 标注「PRD 优先」。

| # | 规则描述 | 出处 | 备注 |
|---|---|---|---|
| 1 | {{business_rule}} | PRD:{{prd_section}} | {{note}} |

## 五、非功能需求

| 维度 | 要求 |
|---|---|
| 性能 | {{performance}} |
| 安全 | {{security}} |
| 兼容性 | {{compatibility}} |
| 可访问性 | {{a11y}} |

## 六、技术约束

| 维度 | 约束 |
|---|---|
| 前端框架 | {{tech_stack}} |
| 后端 | {{backend}} |
| 数据库 | {{database}} |
| 部署环境 | {{deploy_env}} |

## 七、数据需求

| 数据实体 | 字段 | 来源 |
|---|---|---|
| {{entity}} | {{fields}} | 原型/PRD:{{source}} |

## 八、验收标准

> 每个功能的验收标准 MUST 可判（有明确通过/不通过条件）。

| # | 功能 | 验收标准 | 判定方式 |
|---|---|---|---|
| 1 | {{feature}} | {{acceptance}} | {{verification_method}} |

## 九、待补充项（信息不足时标注）

> 保真度不足时，本节列出需要用户补充的信息。**NEVER 编造**。

| # | 缺失信息 | 建议补充方式 | 影响 |
|---|---|---|---|
| 1 | {{missing_info}} | {{how_to_supply}} | {{impact}} |

---

## 解析元数据

| 项 | 值 |
|---|---|
| 解析时间 | {{parsed_at}} |
| 原型平台 | {{prototype_platform}} |
| 解析保真度 | {{fidelity_level}}（高≥80% / 中50-80% / 低<50%） |
| PRD 是否提供 | {{has_prd}} |
| 冲突项数量 | {{conflict_count}} |
| 待补充项数量 | {{pending_count}} |
