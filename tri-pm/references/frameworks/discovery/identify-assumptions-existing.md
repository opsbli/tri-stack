---
name: identify-assumptions-existing
description: 既有产品功能想法的「魔鬼代言人」风险识别框架——从三视角追问为何会失败，在 Value / Usability / Viability / Feasibility 四类风险下列出假设。
source: pm-skills-main/pm-product-discovery/skills/identify-assumptions-existing/SKILL.md
domain: 探索
---

# 既有产品假设识别（identify-assumptions-existing）

> 蒸馏自 `identify-assumptions-existing`｜域：探索｜源词数：267

**Devil's advocate（魔鬼代言人）**式分析，在**四大风险域**下暴露高风险假设，用于压力测试一个既有产品的功能想法。

与 `identify-assumptions-new` 的差异：本技能只用 **4 类**核心产品风险；新产品版扩到 **8 类**（多出 Ethics、Go-to-Market、Strategy & Objectives、Team）。

## 必含章节清单（MUST-SECTIONS）

- [ ] Think from three perspectives — 三视角设想失败原因
- [ ] Identify assumptions across four risk areas — 在 4 类风险域下识别假设
- [ ] For each assumption, note — 每条假设记录 3 项

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] 前置读取：用户若提供文件（designs、PRDs、research）先读
- [ ] 输入前提：用户会描述 product、objective、market segment、feature idea 四项

## 逐段引导问题

- **Think from three perspectives**——追问「这个功能为什么可能失败」（why this feature might fail）：
  - **Product Manager perspective**: Business viability, market fit, strategic alignment（商业可行性、市场契合、战略对齐）
  - **Designer perspective**: Usability, user experience, adoption barriers（易用性、用户体验、采纳障碍）
  - **Engineer perspective**: Technical feasibility, performance, integration challenges（技术可行性、性能、集成挑战）
- **Identify assumptions across four risk areas**——**4 类**风险域及其原始引导问题（照抄）：
  - **Value**: Will it create value for customers? Does it solve a real problem?（会为客户创造价值吗？它解决的是真问题吗？）
  - **Usability**: Will users figure out how to use it? Is the learning curve acceptable?（用户能弄明白怎么用吗？学习曲线可接受吗？）
  - **Viability**: Can marketing, sales, finance, and legal support it?（市场、销售、财务、法务能支撑它吗？）
  - **Feasibility**: Can it be built with existing technology? Are there integration risks?（能用现有技术造出来吗？有集成风险吗？）
- **For each assumption, note**——**3 项**（照抄）：
  - What specifically could go wrong（具体可能出什么错）
  - How confident you are (High/Medium/Low)（你的信心度：高/中/低）
  - Suggested way to test it（建议的验证方式）

## 输出模板

```markdown
（源文件未给出显式输出骨架。结构性要求为：
按 Value / Usability / Viability / Feasibility 四域分组列出假设，
每条含：具体可能出错之处 ｜ 信心度（High/Medium/Low）｜ 建议验证方式。）
```

## 输出命名规则

源文件未规定命名，也未要求落盘（本技能无 save 指令）。

## 关键规则

- 视角数固定 **3 个**、风险域固定 **4 类**——既有产品版不引入 Go-to-Market 等新产品专属风险域。
- 信心度只用 **High/Medium/Low** 三档，不用数字打分（数字打分属 `prioritize-assumptions`）。
- 每条假设都必须配「建议的验证方式」，否则无法进入下游的实验设计。
- 立场纪律（源文件原句）：「Be thorough but constructive — the goal is to strengthen the idea, not kill it.」（要彻底但要有建设性——目标是**强化**这个想法，不是**杀掉**它。）
- 先读设计稿 / PRD / 研究材料，再做压力测试。

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [Assumption Prioritization Canvas: How to Identify And Test The Right Assumptions](https://www.productcompass.pm/p/assumption-prioritization-canvas) — 假设优先级画布
- [How to Manage Risks as a Product Manager](https://www.productcompass.pm/p/how-to-manage-risks-as-a-product-manager) — 产品经理如何管理风险

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
