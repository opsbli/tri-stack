---
name: identify-assumptions-new
description: 新产品的 8 类风险假设识别框架——在 Teresa Torres 的 4 类核心产品风险之上扩展 Ethics / Go-to-Market / Strategy & Objectives / Team，用于评估创业风险与新产品概念。
source: pm-skills-main/pm-product-discovery/skills/identify-assumptions-new/SKILL.md
domain: 探索
---

# 新产品假设识别（identify-assumptions-new）

> 蒸馏自 `identify-assumptions-new`｜域：探索｜源词数：458

在 **8 类风险**下做全面风险识别——把 Teresa Torres《Continuous Discovery Habits》的 **4 类核心产品风险**扩展为 8 类，新增 **Ethics、Go-to-Market、Strategy & Objectives、Team**，这四类对新产品尤其关键。

与 `identify-assumptions-existing` 的差异：既有产品只用前 4 类；本技能用全部 8 类，且每类的引导问题更多、更偏「产品是否该存在」。

## 必含章节清单（MUST-SECTIONS）

- [ ] Think from three perspectives — 三视角设想产品失败原因
- [ ] Identify assumptions across 8 risk categories — 在 8 类风险下识别假设
- [ ] For each assumption — 每条假设评信心度并建议验证方式

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Domain Context — 领域背景：4 类核心风险的出处，以及「扩展为 8 类」的理由
- [ ] 前置读取：用户若提供文件（business plans、research）先读

## 逐段引导问题

- **Think from three perspectives**——追问「这个产品为什么可能失败」（why this product might fail）：
  - **Product Manager**: Market demand, willingness to pay, competitive landscape（市场需求、付费意愿、竞争格局）
  - **Designer**: First-time user experience, onboarding, engagement（首次使用体验、上手引导、参与度）
  - **Engineer**: Build vs. buy decisions, scalability, technical debt（自建还是采购、可扩展性、技术债）
- **8 类风险及其全部引导问题**（照抄，一句不删）：
  - **Value**: Will it create value for customers? Will they keep using it?（会创造客户价值吗？他们会持续用吗？）
  - **Usability**: Will people figure out how to use it? Can we onboard them fast enough? Will it increase cognitive load?（用户能弄明白吗？我们能足够快地引导上手吗？它会增加认知负荷吗？）
  - **Viability**: Can we sell/monetize/finance it? Is it worth the cost? Can we support customers and help them succeed? Can we scale? Will it be compliant?（能卖/变现/融资吗？值这个成本吗？能支持客户并帮他们成功吗？能规模化吗？能合规吗？）
  - **Feasibility**: Can we do it with the current technology? Is this integration possible? Can it be efficient? Can we scale it?（现有技术能做吗？这个集成可行吗？能做到高效吗？能扩展吗？）
  - **Ethics**: Should we do it at all? Are there any ethical considerations? Will it pose a risk for our customers?（我们究竟该不该做？有伦理考量吗？会给客户带来风险吗？）
  - **Go-to-Market**（对新产品尤为关键）: Can we market it? Do we have the required channels? Can we convince customers to try it? Is this the right messaging for this channel? Is this the right time? Is this the right way to launch it?（能做市场推广吗？有需要的渠道吗？能说服客户试用吗？这是该渠道对的信息吗？时机对吗？这是对的上市方式吗？）
  - **Strategy & Objectives**: What are our assumptions? Can others copy our strategy? Have we considered political, economic, legal, technological, and environmental factors? Are those the best problems to solve?（我们的假设是什么？别人能抄我们的战略吗？政治、经济、法律、技术、环境因素都考虑了吗？这些是最值得解决的问题吗？）
  - **Team**: How well will the team work together? Do we have the right people? Do we have the right tools? Will the entire team stay with us long enough?（团队协作会如何？人对吗？工具对吗？整个团队会留够久吗？）
- **For each assumption**：rate confidence（评信心度）并 suggest a test（建议一个验证方式）。

## 输出模板

```markdown
（源文件未给出显式输出骨架。结构性要求为：
按 8 类风险分组列出假设，每条含：信心度 ｜ 建议的验证方式。）
```

## 输出命名规则

源文件未规定命名。仅要求：Save as markdown（存为 Markdown）。

## 关键规则

- 风险类别固定 **8 类**，顺序照上表；不得为省事只写 4 类。
- 期望值校准（源文件原句）：「Good teams assume at least three-quarters of their ideas won't perform as they hope.」（好团队会假设自己至少四分之三的想法达不到预期。）
- **Ethics** 是独立一类，问的是「should we do it at all」——不可并入 Viability 的合规问题。
- **Go-to-Market** 对新产品是关键风险域（especially critical for new products），不能省略。
- 每条假设都要有信心度评级与验证方式，为下游 `prioritize-assumptions` 的 Impact × Risk 矩阵提供输入。

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [Assumption Prioritization Canvas: How to Identify And Test The Right Assumptions](https://www.productcompass.pm/p/assumption-prioritization-canvas) — 假设优先级画布
- [What Is Product Discovery? The Ultimate Guide Step-by-Step](https://www.productcompass.pm/p/what-exactly-is-product-discovery) — 产品探索全流程指南

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
