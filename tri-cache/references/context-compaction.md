---
name: context-compaction
description: tri-cache CONTEXT_COMPACT 模式完整参考——模型感知 token 预算（scripts/token_budget.py）、溢出信号识别（先排除 429/限流）、压缩纪律六条、压缩后产物与检查点五段结构、执行流程七步。SKILL.md 仅留概览表与指针，执行细节查本文件。
---

# 上下文压缩与预算（L5 · 溢出治理）

> 蒸馏自 strix `llm/compaction.py` + `llm/context_budget.py`（Apache-2.0），去产品化改写。
> **解决的问题**：长会话/长审查迟早会撞上下文上限。撞上之后再处理，代价是丢信息（或整轮崩溃）；提前治理，代价只是多一次摘要。

## 一、模型感知预算（确定性 → 脚本）（确定性 → 脚本）

`scripts/token_budget.py` 提供：`context_window` / `output_limit` / `count_tokens` / `usable = window - buffer - output`。

```bash
python scripts/token_budget.py --model <model> --window --json         # 预算事实
python scripts/token_budget.py --model <model> --file <path> --json    # 文本是否装得下
python scripts/token_budget.py --self-test                             # 内置断言
```

**零新增依赖**：`litellm` 可导入且认识该模型时用它；否则回退 **UTF-8 字节上界**（`bytes/2.5 + 1`，对 UTF-8 分词器是保守上界）。**上界意味着宁可早点压缩，也不会静默溢出**。

## 二、溢出信号识别（先排除限流，别把 429 当溢出）（先排除限流，别把 429 当溢出）

命中下列任一即判溢出：① 异常类型为上下文溢出类；② 报文中含 `context length` / `context window` / `prompt is too long` / `input is too long` / `maximum prompt length` / `reduce the length of the messages` / `too many tokens` / `token limit exceeded` / `request entity too large`。

**排除项优先**：报文先命中 `rate limit` / `too many requests` / `throttling` / `service unavailable` / `quota` → 判为限流，**不得进压缩**（把 429 当溢出会平白丢信息）。

## 三、压缩纪律（摘要是状态的载体，不是文风练习）（摘要是状态的载体，不是文风练习）

1. **保留工具调用/结果配对**：截断后的历史必须仍是合法输入，不能留下悬空的调用或结果。
2. **逐项枚举，禁止合并去重**：清单类信息（发现、凭据位置、路径、参数、错误原文）逐条保留，不概括、不合并、不「等 N 项」。
3. **逐字保留不可再生的值**：URL / 端点 / 文件路径 / 参数 / payload / token / 版本 / 错误信息——原文照抄，不改写不占位。
4. **凭据类特殊处理**：命中隐私模式的 token/密钥以「占位标记 + 取值位置指针」保留形态，不把明文写进摘要（与 §隐私过滤 一致）。
5. **头部截断须显式标注**：摘要请求本身若也超长，被截掉的部分 MUST 写 `[... 较早对话已省略 ...]`，让模型知道它看到的是不完整的。
6. **不可发明**：摘要只重述已有内容，禁止补写摘要过程本身或推测缺失信息。

## 四、压缩后产物

| 产物 | 位置 | 说明 |
|---|---|---|
| 压缩检查点 | `.tribro/cache/compaction/<会话ID>_<序号>.md` | 含「目标 / 已确认项 / 未决项 / 关键值原文 / 已尝试路径」五段固定结构 |
| 完成度标记 | 同一文件 frontmatter `complete: true\|false` | 被预算截断时 MUST 为 `false` |

---

## grep 检索模式

`上下文压缩` / `CONTEXT_COMPACT` / `token_budget` / `溢出信号` / `rate limit` / `压缩纪律` / `检查点` / `complete`

## 五、CONTEXT_COMPACT 执行流程（与 SKILL.md §处理流程 同源）

1. **算预算** → `scripts/token_budget.py` 取 `usable`（无 litellm 时自动走字节上界）
2. **判信号** → 按 §二 判定真溢出；命中限流排除项 → 转退避重试，**不压缩**
3. **定保留** → 最近 N 轮保持原文，使剩余内容落在 `usable` 内
4. **写检查点** → 按 §三 六条纪律生成五段式检查点，落盘 `.tribro/cache/compaction/<会话ID>_<序号>.md`
5. **换出历史** → 用检查点替换被压缩部分，保留工具调用/结果配对完整性
6. **标注完成度** → 截断时 `complete: false` + 原因；正常压缩 `complete: true`
7. **兜底分支** → 换出后仍超 `usable`：① 对上一检查点再压缩一轮（**最多 2 轮**）；② 仍超则停止并报错、建议缩小任务范围或提升模型窗口，**NEVER 静默截断**
