---
name: transform-roadmap
description: 将功能导向路线图转换为结果导向路线图，传达战略意图。
source: pm-skills-main/pm-execution/commands/transform-roadmap.md
domain: 执行
---

# /transform-roadmap → 结果导向路线图

> 蒸馏自命令 `transform-roadmap`｜域：执行｜源词数：≈480
> **语法翻译**：源项目以 `/transform-roadmap` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

把功能清单或输出导向路线图改写为结果导向路线图，传达「为什么」而非「做什么」。

## 参数提示

`<roadmap as text, file, or list of planned features>`

## 调用示例（翻译为对话形态）

- 源：`/transform-roadmap [paste your feature list]`
- 本环境等价说法：「把我这份功能清单改写成结果导向路线图」
- 源：`/transform-roadmap [upload roadmap doc]`
- 本环境等价说法：「我上传路线图文档，帮我转写」

## 工作流步骤

1. **接受当前路线图** — 任意形态：功能清单/backlog、路线图文档（Now/Next/Later、季度、时间线）、表格/Gantt 导出、截图。解析每项：功能名、描述、目标时间、上下文。
2. **理解战略上下文** — 问：本期产品目标/OKR？受众（高管/工程/客户/董事会）？偏好格式（Now/Next/Later、季度、时间线）？
3. **改写每项**〔引用技能：`**outcome-roadmap**`〕— 对每功能：识别用户/业务结果；改写为「[Verb] [metric/experience] for [segment]」；同结果功能归一组；加成功指标。
   - 例：「Build SSO」→「Reduce enterprise onboarding friction — 50% faster time-to-first-value」
4. **生成路线图** — 按 Now/Next/Later 输出（含 Strategic themes、Transformation Notes、What Changed）。保存 markdown。
5. **评审** — 主动提议：加 OKR 对齐、写干系人演示、识别 Now 项风险。

## Checkpoint

> **Step 3 后**："If an output doesn't clearly serve an outcome, flag it for the user to justify or deprioritize" — 输出不清晰服务某结果则标记用户论证或降优先级。

## 输出模板

```markdown
## Outcome-Focused Roadmap: [Product] — [Period]
**Strategic themes**: [2-3]
### Now / Next / Later
| Outcome | Success Metric | Key Initiatives | Status/Confidence/Dependencies |
### Transformation Notes: | Original Feature | Transformed Outcome | Why |
### What Changed: [narrative shift summary]
```

## 保存指令

保存为 markdown 文件

## 下一步建议

- 「要我为每个结果加 OKR 对齐吗？」
- 「要我起草一份干系人路线图演示？」
- 「要我为 Now 项识别风险吗？」

## Further Reading

- [Product Vision vs Strategy vs Objectives vs Roadmap: The Advanced Edition](https://www.productcompass.pm/p/product-vision-strategy-goals-and)
