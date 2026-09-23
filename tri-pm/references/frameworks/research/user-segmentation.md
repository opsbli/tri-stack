---
name: user-segmentation
description: 基于行为、JTBD 与需求从反馈数据中分群，识别至少 3 个差异化用户分群
source: pm-skills-main/pm-market-research/skills/user-segmentation/SKILL.md
domain: 研究
---

# 用户分群（user-segmentation）

> 蒸馏自 `user-segmentation`｜域：研究｜源词数：~750

## 必含章节清单（MUST-SECTIONS）

- [ ] Purpose — 目的
- [ ] Input — 输入
- [ ] Analysis Steps — 分析步骤（6 步）
- [ ] Output Structure — 输出结构（每分群 7 块）
- [ ] Best Practices — 最佳实践

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Further Reading —（源外链全部不合规，已丢弃）

## 逐段引导问题

- **Input**：基于行为、JTBD 与未满足需求，为「目标产品/主题」（即用户提供的目标产品/主题）做用户分群。若用户提供反馈、访谈、工单、使用日志、问卷等用户数据，直接读取分析，提取行为模式、动机与需求。
- **Analysis Steps**：数据准备 → 行为提取（使用模式、旅程、触点）→ 需求分析（JTBD、期望结果、痛点）→ 聚类（按行为与需求相似度分组）→ 验证（连贯、互斥、可行动）→ 刻画（含代表性引语）。
- **Output Structure**：每个分群（至少 3 个）须含 7 块。
- **Best Practices**：分群须扎根行为与动机数据而非仅人口；用真实引语；分群须服务不同核心需求；考虑分群间依赖与权衡；标注反馈中代表性不足的群体。

## 输出模板

```markdown
### Segment 1：[名称与概览]
**Segment Name & Overview**：清晰可描述标识；规模（数量或占比估计）；一句话特征
**Behavioral Characteristics**：如何使用「目标产品」（主场景、频率、深度）；典型旅程与关键触点；技术熟练度；与其他工具的整合
**Jobs-to-be-Done & Motivations**：核心 job；底层动机与期望结果；场景与频率；成功定义
**Key Needs & Pain Points**：该行为专属的未满足需求；阻碍；当前变通方案；痛点严重度与频率
**Current Product Fit**：当前契合度；最看重的特性；最沮丧的缺口；续用意愿 vs 流失风险
**Differentiated Value Proposition**：可解锁的独特价值；最大化契合的改进；最共鸣的传达与定位
**Segment Prioritization**：战略重要性（增长/营收/愿景契合）；实施难度；建议（投资/维持/降优先级）
（重复至至少 3 个分群）
```

## 输出命名规则

源文件未规定具体落盘文件名。

## 与相近框架的差异与适用时机

本框架与 `user-personas`、`market-segments` 易混淆，区别见下方（均来自源文件 description 与 Purpose）：

- **user-segmentation（本框架）**：从**反馈数据**按**行为与需求**（非人口属性）聚类出 **≥3 个用户分群**，强调行为特征、当前产品契合度、分群优先级（投资/维持/降优先级）。适用时机：「有用户反馈，想挖出隐藏行为族群并排优先级」。
- **user-personas**：从**研究数据**合成 **3 个具体人物画像**（JTBD + 痛点 + 收益 + 意外洞察），更偏具象「人」。
- **market-segments**：识别 **3–5 个客户细分市场**，聚焦**市场机会、规模、TAM、竞争格局**，更偏市场层面。

一句话：有反馈要**行为分群并排优先级**用本框架；画**具体人物**用 user-personas；看**市场盘子与目标**用 market-segments。

## 关键规则

- 分群扎根行为与动机数据，而非仅人口属性。
- 使用真实用户反馈中的代表性引语与例子。
- 分群须区分且服务不同核心需求。
- 考虑分群间依赖与优先级权衡。
- 标注反馈中代表性可能不足的群体。
- 可得时用产品使用或客户数据验证新兴分群。
- 考虑相邻行为与跨分群模式。

## Checkpoint

> （源未设 checkpoint）

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
