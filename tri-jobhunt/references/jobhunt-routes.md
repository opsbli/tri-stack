# 求职全流程路由表（jobhunt-routes）· 主 skill 分发真源

> 主 skill `tri-jobhunt` 的唯一分发依据。识别用户请求类型 → 命中 R1-R11 → 分发到对应 children
> 子 skill。主 skill 只做**路由与把关**，不重复内联子 skill 方法；子 skill 复用共享 references。
> grep 模式：`R1`-`R11` / `路由` / `分发` / `前置产出`

## 一、决策规则 R1-R11（IF-THEN + 分发目标）

| # | 触发（IF） | 动作（THEN） | 分发子 skill | 依赖共享层 |
|---|---|---|---|---|
| R1 | 用户要「ATS 兼容 / 关键词优化简历 / not getting interviews」 | ATS 解析→提词→算分→摆放→报表 | tri-resume-core | ats-compliance |
| R2 | 用户要「改善 bullet / 加量化数据」 | 弱要点→套 STAR/XYZ→加指标→压缩 | tri-resume-core | star-framework + quantification |
| R3 | 用户给 JD 问「值不值得投 / 匹配多少」 | 先算匹配分(0.7R+0.3P)→红旗否决→给投否建议→再 Tailor | tri-jd | ats-compliance |
| R4 | 需针对 JD 定制简历 | Highlight 非 Fabricate + master 版本 | tri-resume-core | ats-compliance |
| R5 | 要写求职信/申请表/冷邮件/LinkedIn/案例研究/推荐人 | 按产出类型选对应模板 | tri-docs | quantification + star-framework |
| R6 | 需面试准备 | STAR 故事库(五类)→预测题→问面试官 | tri-interview | star-framework |
| R7 | 需薪资谈判 | 市场四分位→TotalComp→反报价脚本→5 场景 | tri-negotiate | — |
| R8 | 多 Offer 需决策 | 总薪酬表→加权矩阵→四自我提问 | tri-negotiate | — |
| R9 | 用户角色为 技术/高管/学术/创意/转行 | 叠加 role-branches 差异增量到通用方法论 | tri-role | role-branches |
| R10 | 需多版本文档管理 | master 单源 + 命名约定 + 追踪表 | tri-resume-core | ats-compliance |
| R11 | 产出涉及「用户伪造数据」可能 | 严守真实性边界：Highlight 不 Fabricate | 主 skill 把关 | ats-compliance |

## 二、联合路由（多能力串行的前置产出衔接）

```
R3(J D 决策) ──投→ R4(Tailor) ──→ R5(求职信/冷邮件)      # JD 分析→定制→信件
R2(要点量化) ──→ R6(面试 STAR 库)                       # 简历要点→面试故事
R9(角色定制) ──叠加─→ R1/R2/R4                          # 角色增量叠加通用方法论
R7(谈判) 与 R8(Offer 比较) 常并行，先算清 TotalComp 再定反报价
```

> 路由副规则：请求可能同时命中多规则（如「投这家公司，帮我写简历+求职信」）→ 按生命周期串行依次分发，
> 一次一环节推进，NEVER 一次性交付「全套」。

## 三、产出模板（各子 skill 交付形状）

| 子 skill | 产物文件头 | 必含 |
|---|---|---|
| tri-jd | `# JOB ANALYSIS REPORT` | OVERALL MATCH SCORE / Requirements / Strengths / Gaps / Red Flags / Decision Factors |
| tri-resume-core | `# ATS COMPATIBILITY REPORT` / `# RESUME QUANTIFICATION` / 定制计划 | 评分 / 格式问题 ✅❌⚠️ / 关键词 / Before-After |
| tri-docs | `# COVER LETTER` / `# CASE STUDY` / `Subject: …` | 钩子 / 6 节 / 结构链 |
| tri-interview | `# INTERVIEW PREP` | Role Analysis / 预测题 / STAR 库 / 问面试官 / 难答公式 |
| tri-negotiate | `# SALARY NEGOTIATION STRATEGY` / `# JOB OFFER COMPARISON` | Market / Counter / TotalComp 表 / 加权矩阵 |
| tri-role | `# EXECUTIVE RESUME` / `# ACADEMIC CV`… | 角色专属结构 + 定位挂注 |

## 四、完成后通用收尾（主 skill 把关）

- 涉及版本/追踪 → 写回 master 与追踪表。
- 涉及数字 → 标注估算方式；营销/未证实数据 → 标注「未证实」。
- 高敏感（薪资/法规/背调）→ 只给方法与框架，NEVER 替代专业法律/薪酬意见。