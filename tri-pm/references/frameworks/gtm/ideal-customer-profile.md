---
name: ideal-customer-profile
description: 从研究数据中识别理想客户画像（ICP）——含人口统计、行为、JTBD 与需求；用于定义 ICP、分析 PMF 调研数据或理解最佳客户是谁
source: pm-skills-main/pm-go-to-market/skills/ideal-customer-profile/SKILL.md
domain: 上市
---

# 理想客户画像（Ideal Customer Profile）

> 蒸馏自 `ideal-customer-profile`｜域：上市｜源词数：约 560

## 必含章节清单（MUST-SECTIONS）

- [ ] Overview — 概述
- [ ] When to Use — 何时使用
- [ ] ICP Framework Components — ICP 四大组成维度（含子项，见下）
- [ ] How It Works — 六步流程
- [ ] Output — 输出物结构
- [ ] Tips — 提示

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Framework — 方法论出处（Clayton Christensen JTBD 理论 + 客户画像方法）
- [ ] Further Reading（见文末，已合规保留）

## 逐段引导问题

**ICP Framework Components（维度清单——逐条照抄）**

- **Demographics（人口/企业统计）**：谁（企业/个人视角）？
  - 公司规模（员工数、营收）
  - 行业或垂直领域
  - 地理位置
  - 职位与部门
  - 岗位年限
  - 教育与背景
  - 组织结构与汇报关系
- **Behaviors（行为）**：如何工作与决策？
  - 如何发现并评估方案
  - 采购流程与决策时间线
  - 技术素养与产品采用速度
  - 协作风格（个人决策 vs 委员会）
  - 变更管理与采用风格
  - 工具切换频率
  - 社群参与与同侪影响
- **Jobs to Be Done (JTBD)（待办任务）**：想达成什么？
  - 主任务/目标
  - 支撑主任务的次要任务
  - 情感任务（想感受如何）
  - 社交任务（身份与认知）
  - 想回避或消除的任务
  - 各任务频率与重要性
  - 完成任务的成功度量
- **Needs and Pain Points（需求与痛点）**：产品解决什么问题？
  - 具体痛点
  - 现有变通方案与局限
  - 对生产力/结果的影响
  - 问题的成本或时间负担
  - 情感挫败程度
  - 解决障碍
  - 可用预算
  - 竞争优先级

**How It Works（六步）**
- Step 1 Gather Customer Data：PMF 调研、访谈转录、试用/免费用户行为、反馈与支持工单、流失分析、赢单输单分析、竞品客户分析。
- Step 2 Segment by Value：最高 LTV、最快到价值、最低流失、最高扩张/增购、最热情、最佳案例潜力、最契合产品愿景。
- Step 3 Profile Demographics：公司规模、垂直与子垂直、地理集中、部门与汇报结构、预算方、公司阶段、文化指标。
- Step 4 Identify Behaviors：如何发现产品、评估流程与时间线、关键干系人、销售障碍、采用速度与广度、团队参与、功能使用频率、支持需求。
- Step 5 Define JTBD：主任务（功能）、情感维度、社交维度、成功度量、情境与约束、竞争任务与优先级、重要性排序。
- Step 6 Document Pain Points and Needs：前状态、理想后状态、差距规模与量化、情感维度、资源约束、疑虑、成功标准。

## 输出模板

```markdown
# Ideal Customer Profile: [产品名]

## 企业统计画像
[公司规模 / 行业 / 位置]

## 行为画像
[采购模式 / 采用风格]

## 完整 JTBD 映射
[功能 / 情感 / 社交任务]

## Top 5-7 痛点与具体需求
[痛点 + 量化影响]

## 量化影响指标
[问题成本 / 方案价值]

## 决策流程与关键干系人
[流程 + 角色]

## 典型客户旅程与时间线
[阶段 + 时长]

## GTM 含义与信息传达
[含义]

## 不契合排除标准（谁不是好客户）
[disqualification]

## ICP 内高价值细分（ideal-of-the-ideal）
[最理想子集]
```

## 输出命名规则

源文件未规定 markdown 落盘命名。

## 关键规则

- 定量与定性数据结合使用。
- 访谈 10+ 高价值客户以识别模式。
- 寻找非显见的人口模式（异常值可能高价值）。
- 同时定义理想 ICP 与可接受的次级细分。
- 随客户数据积累每季度复盘 ICP。
- 用 ICP 评估所有新销售机会。
- 在整个组织（市场/销售/产品）共享 ICP。
- ICP 应驱动聚焦，而非排除所有人。

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- [5 GTM Principles You Should Know as a PM](https://www.productcompass.pm/p/5-gtm-principles-with-frameworks-templates) — 5 条 GTM 原则
- [How to Design a Value Proposition Customers Can't Resist?](https://www.productcompass.pm/p/how-to-design-value-proposition-template) — 价值主张设计
