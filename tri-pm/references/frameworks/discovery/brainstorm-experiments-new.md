---
name: brainstorm-experiments-new
description: 面向「新产品」的精益创业实验框架——构造 XYZ 假设并设计 2-3 个 pretotype（落地页/解说视频/预售/人工 MVP），遵循 Skin-in-the-Game 与 YODA 原则。
source: pm-skills-main/pm-product-discovery/skills/brainstorm-experiments-new/SKILL.md
domain: 探索
---

# 新产品精益实验（brainstorm-experiments-new）

> 蒸馏自 `brainstorm-experiments-new`｜域：探索｜源词数：341

用精益创业方法（lean startup）构造 **XYZ 假设**，并设计 **pretotype** 实验，以最小投入验证一个新产品概念。

**与同族三个技能的差异**：本技能 = 新产品 × 实验设计。与 `brainstorm-experiments-existing` 的根本分野：既有产品可在真实产品/真实流量上测（A/B、原型、spike），新产品**还没有产品**，所以先用 XYZ 假设把「谁、多少比例、做什么」量化，再用 pretotype 制造出「像有产品」的最小信号源。理论底座是 Alberto Savoia《The Right It》。

## 必含章节清单（MUST-SECTIONS）

- [ ] Create an XYZ Hypothesis — 构造 XYZ 假设（3 个变量）
- [ ] Suggest 2-3 pretotype experiments — 建议 2-3 个 pretotype 实验（5 类候选）
- [ ] Key principles (Alberto Savoia, *The Right It*) — 3 条关键原则
- [ ] For each experiment, specify — 每个实验的 4 项必填字段

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] 前置读取：用户若提供文件（market research、landing page mockups）先读

## 逐段引导问题

- **Create an XYZ Hypothesis**——固定句式：**"At least X% of Y will do Z"**（至少 X% 的 Y 会做 Z）。三变量定义照抄：
  - **X%**: The percentage of the target market expected to engage（预期参与的目标市场百分比）
  - **Y**: The specific target market（具体目标市场，源例：`"mid-size luxury sedan buyers"`）
  - **Z**: How they will engage with the product（他们将如何与产品互动）
- **Suggest 2-3 pretotype experiments**——源文件给出的 **5 类**候选（照抄，不增不减）：
  - **Landing Page**: Test interest by measuring sign-ups or clicks（落地页：以注册数或点击量测兴趣）
  - **Explainer Video**: Test understanding and appeal through engagement metrics（解说视频：以互动指标测理解度与吸引力）
  - **Email Campaign**: Test demand through response and click-through rates（邮件活动：以回复率与点击率测需求）
  - **Pre-Order / Waitlist**: Test willingness to pay through skin-in-the-game commitment（预售/等候名单：以有代价的承诺测付费意愿）
  - **Concierge / Manual MVP**: Deliver the service manually to test value（管家式/人工 MVP：人工交付服务以测价值）
- **Key principles**（Alberto Savoia, *The Right It*）——**3 条**（照抄）：
  - **Skin-in-the-Game**：测的是**付费意愿**，不只是兴趣。只有真实代价（time, money, reputation ／时间、金钱、声誉）才是可靠信号。
  - **Your Own Data (YODA)**：通过自己的实验收集**自己的数据**，而不是依赖 **Others' Data (ODP)** ——如市场报告或类比。原句：「The market for your idea does not care about the market for someone else's idea.」（你点子的市场，并不在乎别人点子的市场。）
  - Measure actual behavior, not users' opinions（测真实行为，不测用户观点）
- **For each experiment, specify**：the hypothesis being tested（所测假设）、the method（方法）、the metric（指标）、the success threshold（成功阈值）。

## 输出模板

```markdown
（源文件未给出完整输出骨架。结构性要求为：
1 条 XYZ 假设（At least X% of Y will do Z）
+ 2-3 个 pretotype 实验，每个含：所测假设 ｜ 方法 ｜ 指标 ｜ 成功阈值。）
```

## 输出命名规则

源文件未规定命名。仅要求：Save as markdown if substantial（内容较多时存为 Markdown）。

## 关键规则

- XYZ 假设必须**可量化**：X 是百分比、Y 是具体可触达的细分市场（不能是「所有人」）、Z 是可观测动作。
- pretotype 数量**限定 2-3 个**，不是越多越好——精益的重点是快。
- **Skin-in-the-Game 优先**：只测「兴趣」（点赞、问卷说会买）的实验信号弱；应尽量设计要求用户付出时间/金钱/声誉代价的实验。
- **拒绝 ODP**：市场报告、竞品类比不能替代自己的实验数据（YODA > ODP）。
- 与既有产品实验一致的底线：测行为，不测观点；每个实验必须有成功阈值。

## Checkpoint

（源未设 checkpoint）

## Further Reading

- [How to Build the Right Product with Alberto Savoia (ex-Innovator at Google)](https://www.productcompass.pm/p/how-to-build-the-right-product-with) — Alberto Savoia 谈如何造对的产品
- [Testing Product Ideas: The Ultimate Validation Experiments Library](https://www.productcompass.pm/p/the-ultimate-experiments-library) — 验证实验方法库

（已丢弃 1 条：`Continuous Product Discovery Masterclass (CPDM)`，源标 `(video course)` 付费课程。）
