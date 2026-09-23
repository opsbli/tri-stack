---
name: brainstorm-experiments-existing
description: 面向「既有产品」的实验设计框架——用原型、A/B 测试、fake door、技术 spike 等低成本方法验证假设；用于在全量实现前廉价验证功能想法。
source: pm-skills-main/pm-product-discovery/skills/brainstorm-experiments-existing/SKILL.md
domain: 探索
---

# 既有产品实验设计（brainstorm-experiments-existing）

> 蒸馏自 `brainstorm-experiments-existing`｜域：探索｜源词数：309

设计**低成本实验（low-effort experiments）**，在承诺全量实现之前先验证产品假设。

**与同族三个技能的差异**：本技能 = 既有产品 × 实验设计。它假定团队**已经有了功能想法和一批待验证假设**（The team has a feature idea and assumptions that need validation），因此起点是「澄清想法与假设」而非产生想法；对照 `brainstorm-experiments-new` 用的是 XYZ 假设 + pretotype（新产品尚无产品可测），本技能可以在**生产环境**上做真实流量实验。

## 必含章节清单（MUST-SECTIONS）

- [ ] Clarify the idea and assumptions — 澄清想法与假设：确认团队想建什么、要验证什么
- [ ] Suggest experiments — 为每条假设建议实验（6 类候选方法）
- [ ] Key principles to follow — 必须遵循的 4 条关键原则
- [ ] For each experiment, specify — 每个实验的 4 项必填字段

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] 前置读取：用户若提供文件（PRDs、assumption lists、designs）先读

## 逐段引导问题

- **Clarify the idea and assumptions**：确认 what the team wants to build（团队想建什么）与 what they need to validate（需要验证什么）。
- **Suggest experiments**——源文件给出的 **6 类**候选方法（照抄，不增不减）：
  - First-click testing or task completion with a prototype（原型上的首点击测试或任务完成率测试）
  - Feature stubs or fake door tests（功能桩 / 假门测试）
  - Technical spikes（技术 spike）
  - A/B tests on production (with risk mitigation)（生产环境 A/B 测试，需配风险缓解）
  - Wizard of Oz approaches（绿野仙踪法，人工冒充自动化）
  - Survey-based validation (behavioral, not opinion-based)（基于问卷的验证——问行为，不问观点）
- **Key principles to follow**——**4 条**（照抄）：
  - Measure actual behavior, not users' opinions（测真实行为，不测用户观点）
  - Test responsibly — don't put users or the business at risk（负责任地测试，勿让用户或业务承担风险）
  - For production tests (e.g., A/B tests), explain risk mitigation strategies（生产环境测试须说明风险缓解策略）
  - Aim for maximum validated learning with minimal effort（以最小投入换取最大的已验证学习）
- **For each experiment, specify**——**4 项**必填字段（照抄）：
  - **Assumption**: What do we believe?（假设：我们相信什么？）
  - **Experiment**: What exactly will we do to validate it?（实验：具体做什么来验证？）
  - **Metric**: What will be measured?（指标：测什么？）
  - **Success threshold**: The expected value if we are right（成功阈值：若我们判断正确，该指标的预期值）

## 输出模板

```markdown
（源文件未给出完整输出骨架，只规定呈现形式与字段：
「Present experiments in a clear table or structured format」——
即以清晰表格或结构化格式呈现，每行/每块含
Assumption ｜ Experiment ｜ Metric ｜ Success threshold 四列。）
```

## 输出命名规则

源文件未规定命名。仅要求：Save as markdown if substantial（内容较多时存为 Markdown）。

## 关键规则

- 起点是**已有的假设清单**；一条假设对应一个（或多个）实验，不要笼统地为「整个想法」设计一个实验。
- 生产环境实验（A/B 等）**必须**附风险缓解策略，这是硬性要求而非可选项。
- 问卷只能问**已发生的行为**，不能问观点或意愿（behavioral, not opinion-based）。
- 每个实验必须有可判定的 **success threshold**——没有阈值的实验不构成验证。
- 优化目标是「最大已验证学习 / 最小投入」的比值，而非实验的完备性。

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [Testing Product Ideas: The Ultimate Validation Experiments Library](https://www.productcompass.pm/p/the-ultimate-experiments-library) — 验证实验方法库
- [Assumption Prioritization Canvas: How to Identify And Test The Right Assumptions](https://www.productcompass.pm/p/assumption-prioritization-canvas) — 假设优先级画布
- [What Is Product Discovery? The Ultimate Guide Step-by-Step](https://www.productcompass.pm/p/what-exactly-is-product-discovery) — 产品探索全流程指南

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
