---
name: north-star-metric
description: 定义 North Star Metric 及 3-5 个支撑输入指标（指标星座），区分业务游戏类型并用 7 条标准校验。用于选定 NSM、搭建指标体系或学习 North Star Framework。
source: pm-skills-main/pm-marketing-growth/skills/north-star-metric/SKILL.md
domain: 增长
---

# North Star 指标（north-star-metric）

> 蒸馏自 `north-star-metric`｜域：增长｜源词数：约 500

## 必含章节清单（MUST-SECTIONS）

- [ ] Domain Context — 概念边界（NSM 不是什么 / 是什么）
- [ ] When to Use — 何时使用
- [ ] The Three Business Games — 三类业务游戏（照抄层级）
- [ ] Prompt — 三步生成指令（Step 1/2/3，含指标树层次与选取口径）
- [ ] Tips for Best Results — 最佳实践提示

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Further Reading — 保留 4 条合规外链

## 逐段引导问题

- **Domain Context**：厘清 NSM 的边界——它不是多指标、不是营收/LTV 指标、不是 OKR、不是战略；它是单一、以客户为中心的先行指标。
- **The Three Business Games**：先对业务分类，再定 NSM。
- **Prompt**：三步——分类业务游戏 → 选定 NSM（过 7 条标准）→ 定 3-5 个输入指标。
- **Tips for Best Results**：用户提供商业模式、愿景使命、现有指标、客户分群、核心价值。

## 指标树构建层次（照抄源口径，不可改写）

```
业务游戏 (Business Game)
   └─ North Star Metric (单一、客户中心)
        └─ Input Metrics × 3–5（先行指标，驱动 NSM）
```

- **Step 1 — Classify the Business Game**：判定公司属于 Attention / Transaction / Productivity 哪一类（见下）。
- **Step 2 — Identify the North Star Metric**：给出单一指标，须满足全部 7 条标准（见下）。
- **Step 3 — Identify Input Metrics**：定义 3-5 个 Input Metrics，其选取口径（照抄 3 条）：
  - Be easier to move in the short term（短期更易推动）
  - Directly contribute to the North Star outcome（直接贡献于 NSM 结果）
  - Help identify where optimization efforts should focus（帮助定位优化发力点）

## 三类业务游戏（照抄）

- **Attention Game**：客户在产品中花费多少时间？（例：Facebook、Spotify、YouTube、TikTok）
- **Transaction Game**：客户与平台之间发生多少笔交易？（例：Amazon、Uber、Airbnb、PayPal）
- **Productivity Game**：用户多高效地完成工作或达成目标？（例：Canva、Dropbox、Loom、Notion）

## NSM 的 7 条有效标准（照抄）

1. **Easy to Understand**：定义清晰，组织内人人能懂
2. **Customer-Centric**：反映交付给客户的价值，而非仅营收或活跃
3. **Sustainable Value**：指示习惯与长期客户参与
4. **Vision Alignment**：代表朝公司愿景与使命的有意义进展
5. **Quantitative**：可用清晰数字衡量追踪
6. **Actionable**：团队可通过产品/营销/运营动作直接影响
7. **Leading Indicator**：预测未来业务成功与营收增长

## 输出模板

```markdown
## North Star Framework: [Product]
**Business Game**: [Attention / Transaction / Productivity]

### North Star Metric
- 单一指标：[名称]
- 是否满足 7 条标准：逐条标注 Y/N

### Input Metrics（3-5）
| Input Metric | 短期可推动? | 直接贡献 NSM? | 优化发力点 |
```

## 输出命名规则

源文件未规定（对话内输出即可）。

## 关键规则

- NSM **IS NOT**：multiple metrics；a revenue/LTV metric（须客户中心）；an OKR（那是目标设定技术）；a strategy（但选对 NSM 是战略选择）。
- NSM **IS**：单一、客户中心的 KPI，反映客户从产品中获得的价值，并作为长期业务成功的先行指标；可用 Key Results (OKRs) 表达对 NSM 的预期变化。
- 输入指标数量严格 3-5 个，选取 3 条口径照抄不得改写。
- 角色设定：专精 North Star 与增长度量框架的指标策略师。
- 输入原为源项目的占位参数（本环境不可用），改为「请根据以下业务背景：」的对话上下文。

## Checkpoint

> "A single, customer-centric KPI that reflects the value customers get from the product and serves as a leading indicator of long-term business success."
> 一个单一、以客户为中心的 KPI，反映客户从产品中获得的价值，并作为长期业务成功的先行指标。

## Further Reading

- [The North Star Framework 101](https://www.productcompass.pm/p/the-north-star-framework-101) — NSM 定义与 14 个公司示例（中立、可达、无付费墙）
- [AARRR (Pirate) Metrics: The 5-Stage Framework for Growth](https://www.productcompass.pm/p/aarrr-pirate-metrics) — 获客/激活/留存/营收/推荐五阶段（中立、可达、无付费墙）
- [The Google HEART Framework](https://www.productcompass.pm/p/the-google-heart-framework) — 幸福感/参与度/采纳/留存/任务成功（中立、可达、无付费墙）
- [The Ultimate List of Product Metrics](https://www.productcompass.pm/p/the-ultimate-list-of-product-metrics) — 分阶段的指标大全（中立、可达、无付费墙）

> 源正文另标注 Free resource：[The North Star Framework 101 (PDF)](https://learn.productcompass.pm/nsm101) — 源显式标注为免费资源，保留于 Domain Context 语境（抓取时返回 Loading…，未能完整确认可达性，但源声明为 Free resource，非 CTA/付费墙）。
