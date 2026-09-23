---
name: ab-test-analysis
description: 用统计显著性、样本量校验、置信区间评估 A/B 测试结果，并给出上线/延长/停止建议。
source: pm-skills-main/pm-data-analytics/skills/ab-test-analysis/SKILL.md
domain: 分析
---

# A/B 测试分析（ab-test-analysis）

> 蒸馏自 `ab-test-analysis`｜域：分析｜源词数：~520

## 必含章节清单（MUST-SECTIONS）

- [ ] Context — 上下文（含测试标的，译自源模板占位符）
- [ ] Instructions — 分析步骤（Step 1–6）
- [ ] Outcome→Recommendation — 判定表（5 行，阈值精确照抄）
- [ ] Output Template — 输出骨架

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Further Reading — 延伸阅读（见下方：已按规格丢弃）

## 上下文（语法翻译）

源原文中有一处「测试标的占位符」（Claude Code 插件注入的变量，本环境不可用），译为：你正在分析**对话上下文中用户提供的测试名称或描述**的 A/B 测试结果。若用户提供数据文件（CSV / Excel / 分析导出），直接读取分析；需要时生成 Python 脚本做统计计算。

## 逐段引导问题

- **Step 1（理解实验）**：假设是什么？改了什么（变体）？主指标是什么、有无护栏指标？测试跑了多久？流量拆分比例？
- **Step 2（校验实验设置）**：样本量是否足以支撑预期效应量（公式见下）？是否至少跑满 1–2 个完整业务周期？有无样本比失衡（SRM）证据？是否有足够时间洗掉新奇/首因效应？
- **Step 3（计算统计显著性）**：对照/变体转化率、相对提升（(variant−control)/control×100）、p 值（双尾 z 检验或卡方）、95% 置信区间、是否 p<0.05、业务上是否具实际意义？
- **Step 4（检查护栏指标）**：营收/参与/页面加载等护栏指标是否劣化？主指标胜出但护栏劣化可能不是真赢。
- **Step 5（解读结果）**：按下方判定表给出建议。
- **Step 6（输出摘要）**：按输出模板产出，存为 markdown；若提供原始数据则生成 Python 脚本计算。

## 判定阈值与三类建议触发条件（精确照抄，不得模糊化）

| Outcome（触发条件） | Recommendation（建议） |
|---|---|
| Significant positive lift, no guardrail issues | **Ship it** — roll out to 100% |
| Significant positive lift, guardrail concerns | **Investigate** — understand trade-offs before shipping |
| Not significant, positive trend | **Extend the test** — need more data or larger effect |
| Not significant, flat | **Stop the test** — no meaningful difference detected |
| Significant negative lift | **Don't ship** — revert to control, analyze why |

- **显著性阈值**：p < 0.05（双尾 z 检验或卡方检验）；置信区间取 95% CI。
- **样本量公式**：n = (Z²α/2 × 2 × p × (1−p)) / MDE²；当检验效能 < 80% 时标红（underpowered）。
- **时长下限**：至少 1–2 个完整业务周期。
- **实际意义**：提升对业务是否足够大，统计显著 ≠ 实际显著（0.1% 提升在大样本下可显著但不值得上线）。

## 输出模板

```markdown
## A/B Test Results: [Test Name]

**Hypothesis**: [What we expected]
**Duration**: [X days] | **Sample**: [N control / M variant]

| Metric | Control | Variant | Lift | p-value | Significant? |
|---|---|---|---|---|---|
| [Primary] | X% | Y% | +Z% | 0.0X | Yes/No |
| [Guardrail] | ... | ... | ... | ... | ... |

**Recommendation**: [Ship / Extend / Stop / Investigate]
**Reasoning**: [Why]
**Next steps**: [What to do]
```

## 输出命名规则

源文件未规定（仅要求「Save as markdown」）

## 关键规则

- 逐项逐步推理（Think step by step）。
- 校验样本量 / 时长 / 随机化 / 新奇效应后再下结论；设计有缺陷的结果可能误导。
- 护栏指标与主指标冲突时须「Investigate」而非直接「Ship」。
- 检验效力不足时，通常正确回答是「Extend」而非「无效应」。
- 营收类指标用置信区间估计最好/最坏业务影响。
- 若以 CSV 提供原始数据，用 Python（scipy.stats）生成完整分析。

## Checkpoint

（源未设独立 checkpoint，但 Step 6 要求「Think step by step. Save as markdown.」——分析须逐步推理并存盘）

## Further Reading

（源提供的 Further Reading 全部指向 productcompass.pm newsletter，含订阅 CTA 与付费墙提示，违反规格纪律 #7，已全部丢弃）
