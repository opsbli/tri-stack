---
verify_id: <UUID>
created_at: <ISO8601>
schema_version: 1
---

# 段落级原文-验证对照

> 本表列出每个段落的原文、验证状态、引用与防线触发情况，供溯源核对。

| 段落 | 原文 | 幻觉类型 | 知识类型 | 防线触发 | 验证状态 | 引用 | 最终置信 |
|------|------|----------|----------|----------|----------|------|----------|
| [P0] | <原文段> | factuality | known | 1 | verified | — | 0.92 |
| [P1] | <原文段> | factuality | known | 2 | verified | [1][2] | 0.88 |
| [P2] | <原文段> | faithfulness | inferred | 3 | verified | [3] | 0.75 |
| [P3] | <原文段> | factuality | computed | 4 | verified | [4] | 0.70 |
| [P4] | <原文段> | mixed | guess | 兜底 | rejected | — | 0.35 |

## 字段说明

- **幻觉类型**：factuality（事实性）/ faithfulness（自洽性）/ mixed（混合）
- **知识类型**：known（事实）/ computed（计算）/ inferred（推断）/ iframe（框架）/ common（常识）/ guess（猜测）——与置信度同层级并行属性，决定验证路由
- **防线触发**：1（置信度+知识类型放行）/ 2（事实源验证）/ 3（多模型交叉验证）/ 4（自我反思修正）/ 兜底
- **验证状态**：verified / rejected / uncertain / human_review
- **引用**：该段落引用的信源标记（如 [1][2]），无则填 —
- **最终置信**：该段落经防线处理后的最终置信度

## 段落级验证状态汇总

| 状态 | 段落数 | 占比 |
|------|--------|------|
| verified | <N> | <N%> |
| rejected | <N> | <N%> |
| uncertain | <N> | <N%> |
| human_review | <N> | <N%> |
