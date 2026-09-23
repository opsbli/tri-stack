---
name: prioritize-assumptions
description: 用 Impact × Risk 矩阵给假设做分诊并为每格指定动作（延后/直接实现/否决/设计实验），配 ICE 与 RICE 公式；用于决定先测哪条假设。
source: pm-skills-main/pm-product-discovery/skills/prioritize-assumptions/SKILL.md
domain: 探索
---

# 假设优先级（prioritize-assumptions）

> 蒸馏自 `prioritize-assumptions`｜域：探索｜源词数：324

用 **Impact × Risk 矩阵**给假设分诊（triage），并为需要验证的假设建议有针对性的实验。

## 必含章节清单（MUST-SECTIONS）

- [ ] For each assumption, evaluate two dimensions — 逐条评估 Impact 与 Risk 两个维度
- [ ] Categorize each assumption using the Impact × Risk matrix — 用 2×2 矩阵归类（4 格各有指定动作）
- [ ] For each assumption requiring testing, suggest an experiment — 为需测假设建议实验（3 项要求）
- [ ] Present results — 以优先级矩阵或表格呈现结果

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Domain Context — 领域背景：ICE / RICE / Opportunity Score 公式
- [ ] 前置读取：用户若提供含假设或研究数据的文件先读

## 逐段引导问题

- **两个评估维度**（公式照抄，不得简化）：
  - **Impact**：验证这条假设所创造的价值 **AND** 受影响的客户数量。在 ICE 中：**Impact = Opportunity Score × # Customers**
  - **Risk**：定义为 **Risk = (1 − Confidence) × Effort**
- **Impact × Risk 矩阵——4 格与各自动作**（照抄，动作不得对调或合并）：

| 象限 | 英文原文 | 指定动作 |
|---|---|---|
| 低影响 · 低风险 | **Low Impact, Low Risk** | → Defer testing until higher-priority assumptions are addressed（延后验证，先处理更高优先级的假设） |
| 高影响 · 低风险 | **High Impact, Low Risk** | → Proceed to implementation (low risk, high reward)（直接进入实现：低风险高回报） |
| 低影响 · 高风险 | **Low Impact, High Risk** | → Reject the idea (not worth the investment)（否决该想法：不值得投入） |
| 高影响 · 高风险 | **High Impact, High Risk** | → Design an experiment to test it（设计实验来验证——这一格才是「leap of faith」所在） |

- **为需测假设建议实验**的 **3 项**要求（照抄）：
  - Maximizes validated learning with minimal effort（以最小投入最大化已验证学习）
  - Measures actual behavior, not opinions（测真实行为，不测观点）
  - Has a clear success metric and threshold（有清晰的成功指标与阈值）

## 领域公式（Domain Context 原文照抄）

- **ICE**（适合假设优先级）：**Impact (Opportunity Score × # Customers) × Confidence (1–10) × Ease (1–10)**
- **Opportunity Score**（Dan Olsen）：**Opportunity Score = Importance × (1 − Satisfaction)**，normalized to 0–1（归一化到 0–1）
- **RICE**：把 Impact 拆成 Reach × Impact 两个独立因子：**(R × I × C) / E**
- 完整公式与模板见工具箱域的 `prioritization-frameworks` 框架文件（源文件原为跨技能引用）。

## 输出模板

```markdown
（源文件未给出完整输出骨架，只规定呈现形式：
「Present results as a prioritized matrix or table」——
即优先级矩阵或表格，每行含：假设 ｜ Impact ｜ Risk ｜ 所属象限 ｜ 指定动作 ｜（若需测）实验+指标+阈值。）
```

## 输出命名规则

源文件未规定命名。仅要求：Save as markdown if the output is substantial（内容较多时存为 Markdown）。

## 关键规则

- **Risk 不是「出错概率」**，而是 `(1 − Confidence) × Effort`——投入越大、信心越低，风险越高。照此计算，不得替换为其他风险定义。
- Impact 必须同时含「价值」与「受影响客户数」两个乘数因子，不能只填价值。
- 四格动作是**硬映射**：低影响高风险 → **否决想法**（不是「延后」），低影响低风险 → **延后**（不是「否决」）。
- 只有 **High Impact + High Risk** 才值得花实验预算。
- 每个建议的实验都必须自带成功指标与阈值。

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [Assumption Prioritization Canvas: How to Identify And Test The Right Assumptions](https://www.productcompass.pm/p/assumption-prioritization-canvas) — 假设优先级画布原文

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
