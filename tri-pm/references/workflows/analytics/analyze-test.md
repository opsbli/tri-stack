---
name: analyze-test
description: 分析 A/B 测试结果——统计显著性、样本量校验与上线/延长/停止建议。
source: pm-skills-main/pm-data-analytics/commands/analyze-test.md
domain: 分析
---

# /analyze-test → A/B 测试分析

> 蒸馏自命令 `analyze-test`｜域：分析｜源词数：~470
> **语法翻译**：源项目以 `/analyze-test` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

用统计严谨性评估实验结果，并转化为清晰的产品决策：上线、延长或停止。

## 参数提示

`<test results as data, screenshot, or description>`（以数据、截图或描述形式给出的测试结果）

## 调用示例（翻译为对话形态）

- 源：`/analyze-test Control: 4.2% conversion (n=5000), Variant: 4.8% conversion (n=5100)`
- 本环境等价说法：「对照：转化率 4.2%（n=5000），变体：4.8%（n=5100），帮我判定」
- 源：`/analyze-test [upload a CSV of test results]`
- 本环境等价说法：「（上传一份测试结果 CSV）分析这个 A/B 实验」
- 源：`/analyze-test [screenshot from your experimentation platform]`
- 本环境等价说法：「（贴一张实验平台截图）解读这张 A/B 结果」

## 工作流步骤

1. **接收测试数据** — 任意格式：汇总统计（转化率、各变体样本量）、原始事件数据（CSV：user_id、variant、converted、timestamp）、实验平台截图（Optimizely、LaunchDarkly 等）、实验与结果描述。〔引用技能：`**ab-test-analysis**`〕
2. **校验实验设计** — 分析前检查：样本量是否足够（做功效分析）？测试是否够长（覆盖周周期，最少 1–2 个业务周期）？随机化是否干净（查样本比失衡 SRM）？测试期间有无外部因素？发现问题须标出——有缺陷测试的结果可能误导。〔引用技能：`**ab-test-analysis**`〕
3. **分析结果** — 应用 `**ab-test-analysis**` 技能：统计显著性（p 值与置信区间）、效应量（变体间绝对与相对差）、实际意义（效应是否大到对业务重要）、置信区间（真实效应的合理范围）、分群分析（数据允许时检查用户分群的差异效应）。〔引用技能：`**ab-test-analysis**`〕
4. **生成分析** — 按输出模板产出。
5. **提议下一步** — 是否基于发现设计后续实验、是否对特定分群跑分析、是否生成上线后监控该指标的 SQL。

## Checkpoint

（源未设显式 checkpoint；判定须与 `ab-test-analysis` 框架的 5 行判定表一致）

## 判定阈值（与框架精确一致，不模糊化）

- 显著正提升且无护栏问题 → **SHIP**；显著正提升但护栏堪忧 → **Investigate**；不显著但正向趋势 → **EXTEND**；不显著且持平 → **STOP**；显著负提升 → **Don't ship**（回退对照）。
- 显著性阈值 p < 0.05，置信区间 95% CI；样本量公式 n = (Z²α/2 × 2 × p × (1−p)) / MDE²，效能 < 80% 标红。

## 输出模板

```markdown
## A/B Test Analysis: [Test Name]

**Date**: [today]
**Test duration**: [X days/weeks]
**Total sample**: [N users]

### Results Summary
| Variant | Sample | Metric | Rate | 95% CI |
|---------|--------|--------|------|--------|
| Control | [n] | [metric] | [X%] | [X% - Y%] |
| Variant | [n] | [metric] | [X%] | [X% - Y%] |

### Statistical Analysis
- **Relative lift**: [+X%] ([CI range])
- **P-value**: [X]
- **Statistically significant**: [Yes/No] at 95% confidence
- **Minimum detectable effect**: [X%] (what the test was powered to detect)

### Sample Size Check
- **Required sample**: [N] per variant (for [X%] MDE at 80% power)
- **Actual sample**: [N] per variant
- **Verdict**: [Sufficiently powered / Underpowered / Overpowered]

### Decision
**Recommendation: [SHIP / EXTEND / STOP]**
[Clear explanation of why, considering both statistical and practical significance]

### Business Impact Estimate
If shipped to 100% of users:
- **Expected impact**: [metric change per month/quarter]
- **Revenue impact**: [if applicable]
- **Confidence**: [How certain we are about this estimate]

### Caveats
- [Any concerns about the test validity]
- [Segments where results differ]
- [Novelty effects or other biases to consider]

### Follow-Up
- [What to test next based on learnings]
- [Monitoring plan if shipping the variant]
```

## 保存指令

源文件未规定落盘位置与命名（分析在对话中交付；可应要求存为 markdown）。

## 下一步建议

- 是否要基于发现**设计后续实验**
- 是否要**对特定分群跑分析**
- 是否要生成**上线后监控该指标的 SQL**

## Further Reading

（源未提供独立 Further Reading；源 README 中的斜杠调用已按规格翻译为对话形态，不作为可执行命令保留）

## 关键注意事项（Notes 照抄）

- 统计显著 ≠ 实际显著——0.1% 提升在大样本下可显著但不值得上线。
- 信任结果前务必查样本比失衡（SRM）。
- 新奇效应会抬高短期结果——建议上线后监控 2–4 周。
- 检验效力不足时，正确答案通常是「extend」而非「无效应」。
- 营收类指标用置信区间估计最好/最坏业务影响。
- 若以 CSV 提供数据，用 Python（scipy.stats）生成完整分析。
