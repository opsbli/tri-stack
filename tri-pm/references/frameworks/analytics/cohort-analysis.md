---
name: cohort-analysis
description: 对用户参与度数据做队列分析——留存曲线、功能采纳趋势与分群洞察，结合定量结果给出定性研究建议。
source: pm-skills-main/pm-data-analytics/skills/cohort-analysis/SKILL.md
domain: 分析
---

# 队列分析与留存探索器（cohort-analysis）

> 蒸馏自 `cohort-analysis`｜域：分析｜源词数：~620

## 必含章节清单（MUST-SECTIONS）

- [ ] Purpose — 用途
- [ ] How It Works — 工作机制（Step 1–5）
- [ ] Usage Examples — 使用示例（Example 1–3）
- [ ] Key Capabilities — 关键能力
- [ ] Tips for Best Results — 最佳实践提示
- [ ] Output Format — 输出格式

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Further Reading — 延伸阅读（见下方：已按规格丢弃）

## 逐段引导问题

- **Purpose**：按队列分析用户参与度与留存模式，识别行为、功能采纳与长期参与趋势，并把定量洞察与定性研究建议结合。
- **How It Works / Step 1（读取并校验数据）**：数据是否含 cohort 标识、时间周期、参与度指标？是否检查缺失值与数据质量问题？是否汇总关键统计（队列规模、日期范围、可用指标）？
- **How It Works / Step 2（生成定量分析）**：是否计算留存率与参与度趋势？是否识别留存曲线、流失模式、异常？是否计算各队列功能采纳率？是否计算逐月/逐周期变化？是否按需用 pandas/numpy 生成 Python 脚本？
- **How It Works / Step 3（创建可视化）**：图表结构照抄——留存热力图（cohorts vs. time periods）、展示队列进程的折线图、功能采纳对比图、标出流失点与参与度趋势；输出为交互图或静态图。
- **How It Works / Step 4（识别洞察与模式）**：是否发现以下一种或多种显著模式——特定队列的早期流失、后期参与度变化、功能采纳聚类、季节性或时间趋势？是否对比队列表现以建立基线？
- **How It Works / Step 5（建议后续研究）**：是否推荐定性研究（流失用户定向访谈、高参与队列功能使用调查、关键交互会话回放、高低留存队列的赢/输分析）？是否设计后续定量研究、建议 A/B 或功能实验？
- **Tips for Best Results**：是否含时间维度、是否明确定义队列（注册月/功能上线日等）、是否提供上下文（期间的产品变化/发布/事件）、是否含多指标、是否有足够数据（≥3–4 个队列）、是否要求特定输出？

## 队列划分口径（照抄源文件口径）

- **队列标识（cohort identifier）**：按注册月、功能上线日、获客渠道、套餐层级、首次使用的功能等显式分组。
- **时间维度**：多时间周期（日/周/月），至少 3–4 个队列才有意义。
- **参与度指标**：留存、参与度、功能使用、营收等可多指标并行。
- **留存事件**：强调「有意义的行为」而非仅「登录」。早期队列因种子用户偏差常与后期不同，对比时需注明。

## 输出模板

```markdown
**Data Summary**：队列概览与数据质量评估
**Quantitative Findings**：关键指标、留存率、趋势分析
**Visualizations**：展示留存曲线、采纳模式的图表
**Pattern Identification**：数据中 2–3 条显著洞察
**Research Recommendations**：具体的定性与定量后续动作
**Analysis Scripts**（按需）：可复现分析的 Python 代码
**Next Steps**：基于发现的优先级行动
```

## 输出命名规则

源文件未规定

## 关键规则

- **数据读取**：导入 CSV、Excel、JSON、SQL 查询结果。
- **留存分析**：计算并可视化随时间的留存率。
- **队列对比**：跨队列组比较指标。
- **异常检测**：标记异常模式或流失。
- **Python 脚本**：生成可复用分析代码。
- **可视化**：热力图、图表、交互看板。
- **研究设计**：建议定向后续研究与访谈方法。
- **统计摘要**：提供量化指标与相关性分析。
- **最佳实践（Tips，6 条照抄）**：① 包含时间维度；② 明确定义队列分组；③ 提供上下文（期间产品变化/发布/事件）；④ 多指标（留存、参与、功能使用、营收）；⑤ 充足数据（≥3–4 队列）；⑥ 要求具体输出（图表/Python 脚本/研究建议）。

## Checkpoint

（源未设 checkpoint）

## Further Reading

（源提供的 Further Reading 全部指向 productcompass.pm newsletter，含订阅 CTA 与付费墙提示，违反规格纪律 #7，已全部丢弃）
