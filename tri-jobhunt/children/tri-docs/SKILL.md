---
name: tri-docs
slug: tri-docs
version: 1.0.1
displayName: 求职产出文档
description: tri-jobhunt 的 children 子 skill，由主 skill(R5)委派。产出求职信、申请表答案、自荐冷邮件、LinkedIn 优化、作品集案例研究、推荐人清单。复用共享 references/quantification / star-framework。
summary: 求职辅助文档产出子 skill。
tags: [cover-letter, cold-email, linkedin, case-study, reference, application-form]
license: MIT
---

# tri-docs · 求职产出文档（children 子 skill）
> 产物落盘：本 children 不独立落盘——用户成果物由主 skill `tri-jobhunt` 统一落 `.tribro/jobhunt/`（`.tribro/` 不存在时由主 skill 先创建）；链路审计文档由主 skill 落 `.tribro/forge/jobhunt/`。本 children 随主 skill 包分发，遵循主 skill §落盘规则。


> 由主 skill `tri-jobhunt` 依 R5 委派激活，**不对外暴露**。按用户要的产出类型选对应模板。
> 复用共享 references（量化/STAR），遵循真实性边界。

## 职责（六类产出 + 模板）

| 产出 | 关键模板 |
|---|---|
| **求职信** | 250-400 word/3-4 段；五开头钩子（Specific Company Knowledge / Mutual Connection / Problem-Solver / Impressive Achievement / Industry Insight）；Body1 公式 `[Their Need]+[Your Exact Experience]+[Specific Result]`；开头禁「I am writing to apply」 |
| **申请表答案** | 7 类型（Experience/Why Company/Portfolio/Technical Skills/About You/情境行为/观点愿景）；长度校准（单行 1 句 / 短答 2-4 句 / 长答 100-250 词）；纯代码块输出；「When in doubt, shorter is better」 |
| **冷邮件** | 结构链 Subject→Hook(2-3 句具体)→Location→Experience Gap→Body→Connection→Portfolio→Closing；200-300 词；五类错误对照 |
| **LinkedIn** | Headline 220 字符(`[Role]|[Expertise]|[Value]`)；About 1500-2000/2600 上限；All-Star 门槛（照片/headline/现职/2 段过往/教育/≥5 技能/邮编/50+ 连接） |
| **案例研究** | 6 节（Overview/Problem/Process/Solution/Results/Learnings）；Results 量化表 `Metric|Before|After|Change` + 时间框架；Learnings 三段式 |
| **推荐人清单** | 五层优先级（现任上级>高级领导>同级/跨职能>客户/教授>朋友/家人）；三步法（Ask→Brief→Follow Up）；标准格式 |

## 关键动作

- 写前必读：JD（镜像语言）+ 简历（取真实项目）+ 问题本身；缺材料先索取。
- 求职信/申请表标题下一定给出「可对接下一步」：如求职信由 R3 的谈点生成。
- 量化与真实：任何数字用 `quantification.md` 的估算技巧；案例结果带时间框架。
- **NEVER 编造**任职经历、数据、荣誉（R11 边界）。

## 输出

按类型产出：`# COVER LETTER FOR [POSITION] AT [COMPANY]` / `Subject: …`（冷邮件）/
`# LINKEDIN PROFILE OPTIMIZATION` / `# CASE STUDY: [PROJECT]` / 推荐人清单。

## 边界

- 冷邮件个性化目标 = 「同事随口提及有趣的事」，不是 pitch deck；切掉「放哪家公司都行」的句子。
- LinkedIn 无照片提示「21× 更多浏览」；resume↔LinkedIn 三层同步（一致/扩展/调整）。
- 局限：外语版本按当地劳动法规调整（如「被问现薪」合法性随国家不同）。