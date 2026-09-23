---
name: user-personas
description: 从研究数据提炼精致用户画像——3 个含 JTBD、痛点、收益与意外洞察的 persona
source: pm-skills-main/pm-market-research/skills/user-personas/SKILL.md
domain: 研究
---

# 用户画像（user-personas）

> 蒸馏自 `user-personas`｜域：研究｜源词数：~560

## 必含章节清单（MUST-SECTIONS）

- [ ] Purpose — 目的
- [ ] Input — 输入（用户提供的研究数据）
- [ ] Analysis Steps — 分析步骤（5 步）
- [ ] Output Structure — 输出结构（每 persona 6 块）
- [ ] Best Practices — 最佳实践

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Further Reading —（源外链全部不合规，已丢弃）

## 逐段引导问题

- **Input**：为「目标产品/主题」（即用户提供的目标产品/主题）创建 3 个精致用户画像。若用户提供 CSV、Excel、问卷答复、访谈转录或其他研究数据文件，直接读取并分析，提取关键模式、人口属性、动机与行为。
- **Analysis Steps**：数据收集 → 模式识别 → 分组（按共享动机与 JTBD 归入不同 persona）→ 充实（合成为连贯画像）→ 验证（交叉比对确保扎根真实发现）。
- **Output Structure**：每个 persona 须含 6 块（见下）。
- **Best Practices**：所有洞察须扎根真实数据、引用原话、识别行为模式而非仅人口类别、persona 尽量互斥、标注数据缺口。

## 输出模板

```markdown
### Persona 1：[名称]
**Persona Name & Demographics**：年龄区间、角色/职称、公司规模（B2B 时）、关键特征
**Primary Job-to-be-Done**：核心待达成结果；场景与频率
**Top 3 Pain Points**：阻碍达成的 3 个具体挑战；影响与严重度
**Top 3 Desired Gains**：寻求的收益/结果；成功衡量方式
**One Unexpected Insight**：数据中反直觉的行为模式/动机；对产品决策的意义
**Product Fit Assessment**：「目标产品」如何满足（或可满足）该 persona 的需求；摩擦点或未满足需求
（重复 Persona 2、3）
```

## 输出命名规则

源文件未规定具体落盘文件名。

## 与相近框架的差异与适用时机

本框架与 `market-segments`、`user-segmentation` 易混淆，三者区别如下（均来自源文件 description 与 Purpose）：

- **user-personas（本框架）**：从**已有研究数据**（问卷/访谈/CSV）合成 **3 个具体人物画像**，强调 JTBD、痛点、收益与「一个意外洞察」。适用于「我已有数据，帮我画出用户长什么样」。
- **market-segments**：识别 **3–5 个客户细分市场**，聚焦市场机会、TAM 评估、目标受众优先级。适用时机是「评估市场机会、探索新市场、决定先打哪类客户」。输出更偏市场层面（规模、增长、竞争格局）。
- **user-segmentation**：从**反馈数据**（评论/工单/使用日志）按**行为与需求**（非人口属性）聚类出 **≥3 个用户分群**，强调行为特征、当前产品契合度、分群优先级（投资/维持/降优先级）。适用时机是「手头是用户反馈，想挖出隐藏的行为族群并排优先级」。

一句话：有数据画**人**用 personas；想看**市场盘子与目标**用 market-segments；有反馈按**行为分群排优先级**用 user-segmentation。

## 关键规则

- 所有洞察须扎根实际数据，避免假设；可用研究中的直接引语。
- 识别行为模式，而非仅人口类别。
- persona 尽量区分且互斥。
- 标注任何数据缺口或需补充研究的区域。

## Checkpoint

> （源未设 checkpoint）

## Further Reading

（源未提供 Further Reading 或全部不合规，已丢弃）
