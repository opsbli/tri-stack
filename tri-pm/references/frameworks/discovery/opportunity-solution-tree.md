---
name: opportunity-solution-tree
description: 机会解决方案树（OST）——把「期望成果 → 机会 → 解决方案 → 实验」四层结构化，源自 Teresa Torres《Continuous Discovery Habits》；用于组织探索工作、防止直接跳到方案。
source: pm-skills-main/pm-product-discovery/skills/opportunity-solution-tree/SKILL.md
domain: 探索
---

# 机会解决方案树（opportunity-solution-tree）

> 蒸馏自 `opportunity-solution-tree`｜域：探索｜源词数：562

用于组织持续产品探索的可视化框架。把一个期望**成果（outcome）**连到客户**机会（opportunities）**、可能的**解决方案（solutions）**、以及用于验证的**实验（experiments）**。

**Opportunity Solution Tree**（Teresa Torres，《Continuous Discovery Habits》）是现代产品探索的骨干。它通过强制团队先绘制机会空间，来防止团队直接跳到解决方案。

## 必含章节清单（MUST-SECTIONS）

树结构固定 **4 层**（Structure: 4 levels）：

- [ ] Desired Outcome — 期望成果（顶层）
- [ ] Opportunities — 机会（第二层）
- [ ] Solutions — 解决方案（第三层）
- [ ] Experiments — 实验（底层）

流程固定 **6 步**（Process）：

- [ ] Define the desired outcome — 定义期望成果
- [ ] Map opportunities — 映射机会（3-7 个）
- [ ] Prioritize opportunities — 机会优先级（聚焦前 2-3）
- [ ] Generate solutions — 生成解决方案（每机会 3+ 个）
- [ ] Design experiments — 设计实验（每方案 1-2 个）
- [ ] Visualize the tree — 可视化整棵树

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Input Requirements — 输入要求（3 项）
- [ ] Key principles — 5 条关键原则

## 四层结构定义（照抄）

1. **Desired Outcome（顶层）** — 团队追求的可度量业务/产品成果。应当是**单一、清晰的指标**（源例：`"increase 7-day retention to 40%"` ／把 7 日留存提到 40%）。来自你的 OKRs 或产品战略。
2. **Opportunities（第二层）** — 通过研究发现的客户需求、痛点或愿望。它们是**值得解决的问题，而不是功能**。用客户视角措辞：`"I struggle to..."`（我很难……）或 `"I wish I could..."`（我希望我能……）。
   优先级用 **Opportunity Score：Importance × (1 − Satisfaction)**（Dan Olsen，《The Lean Product Playbook》）。**Importance 与 Satisfaction 归一化到 0–1。**
3. **Solutions（第三层）** — 应对每个机会的可能方式。**每个机会生成多个方案**——不要认定第一个想法。应由 **Product Trio**（PM + Designer + Engineer）共同构思。原句：「Best ideas often come from engineers.」（最好的想法常常来自工程师。）
4. **Experiments（底层）** — 快速、廉价的测试，验证某个方案是否真的解决了那个机会。使用假设验证（**Value、Usability、Viability、Feasibility** 四类风险）。优先选带 **"skin-in-the-game"**（有真实代价，Alberto Savoia）的实验，而非基于观点的验证。

## 输入要求（Input Requirements，照抄）

- A desired outcome or business metric to improve（一个期望成果或待改善的业务指标）
- Customer research data (interviews, surveys, analytics, feedback)（客户研究数据：访谈、问卷、分析、反馈）
- Optionally: existing opportunities or solution ideas to organize（可选：已有的机会或方案想法，待整理）

## 逐段引导问题

- **Define the desired outcome**：确认或帮助表述**一个**位于树顶的、单一且可度量的成果。
- **Map opportunities**：从所提供的研究中识别 **3-7 个**客户机会（需求/痛点）。归并相关机会。每条都用客户视角措辞。
- **Prioritize opportunities**：用 Opportunity Score 或定性评估排序。**聚焦前 2-3 个**。
- **Generate solutions**：为每个入选机会，从 PM、Designer、Engineer 三视角头脑风暴 **3+ 个**方案。
- **Design experiments**：为最有希望的方案建议 **1-2 个**快速实验，须明确：hypothesis（假设）、method（方法）、metric（指标）、success threshold（成功阈值）。
- **Visualize the tree**：以清晰的层级格式呈现完整 OST。

## 输出模板

```markdown
（源文件未给出字面骨架，其结构性要求即上述 4 层层级树：

Desired Outcome: [单一可度量指标]
├── Opportunity 1（客户视角措辞）｜Opportunity Score = Importance × (1 − Satisfaction)
│   ├── Solution 1.1
│   │   ├── Experiment: 假设 / 方法 / 指标 / 成功阈值
│   │   └── Experiment: ...
│   ├── Solution 1.2
│   └── Solution 1.3        ← 每机会至少 3 个方案
├── Opportunity 2
└── ...                     ← 机会总数 3-7，聚焦前 2-3
）
```

## 输出命名规则

源文件未规定命名。仅要求：Save as markdown if substantial（内容较多时存为 Markdown）。

## 关键规则（Key principles，5 条照抄）

- **One outcome at a time.**（一次只处理一个成果。）Don't try to solve everything. 把树聚焦在单一期望成果上。
- **Opportunities, not features.**（要机会，不要功能。）原句：「Never allow customers to design solutions. Prioritize opportunities (problems), not features.」（绝不让客户来设计解决方案。优先排序机会（问题），而非功能。）
- **Compare and contrast.**（对比择优。）选定前**至少生成 3 个**方案，避开「第一个想法」陷阱。
- **Discovery is not linear.**（探索不是线性的。）实验失败就回环；验证不通过的方案就砍掉；去探索新分支。
- **Continuous, not periodic.**（是持续的，不是周期性的。）每周根据访谈、分析和实验的所学**更新这棵树**。

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [The Extended Opportunity Solution Tree](https://www.productcompass.pm/p/the-extended-opportunity-solution-tree) — 扩展版机会解决方案树
- [What Is Product Discovery? The Ultimate Guide Step-by-Step](https://www.productcompass.pm/p/what-exactly-is-product-discovery) — 产品探索全流程指南
- [Product Trio: Beyond the Obvious](https://www.productcompass.pm/p/product-trio) — Product Trio 协作模式详解

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
