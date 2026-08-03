---
verify_id: <UUID>
created_at: <ISO8601>
schema_version: 1
---

# 修订记录

> 本报告记录防线四（自我反思修正）的各轮修订过程。仅触发防线四时生成。

## 修订轮次总览

| 轮次 | 方法 | 段落 | 原始置信 | 修订后置信 | 判定 |
|------|------|------|----------|------------|------|
| 1 | CoVe | [P1] | 0.55 | 0.72 | fail → 轮次 2 |
| 2 | Reflexion | [P1] | 0.72 | 0.81 | fail → 轮次 3 |
| 3 | Critique-Refine | [P1] | 0.81 | 0.88 | pass |

## 轮次 1 · CoVe（Chain-of-Verification）

**段落**：[P1]

**步骤 1·主张提取**：
- 主张 1：<extracted claim 1>
- 主张 2：<extracted claim 2>

**步骤 2·验证查询生成**：
- 查询 1：<verification query 1>
- 查询 2：<verification query 2>

**步骤 3·证据检索**：
- 证据 1（来自 [3] T2）：<evidence excerpt>
- 证据 2（来自 [4] T3）：<evidence excerpt>

**步骤 4·修订**：
- 原回答：<original answer>
- 修订后回答：<revised answer>
- 修订原因：<基于证据 1/2 修正了主张 1>

**置信度变化**：0.55 → 0.72（提升 0.17，仍未达阈值 0.85）

## 轮次 2 · Reflexion

**段落**：[P1]

**反思结构**：
```
<thought>
  上一轮修订后置信 0.72，仍未达标。反思：
  - 主张 1 已修正，但主张 2 仍缺乏证据
  - 需进一步检索证据或调整表述
</thought>
<answer>
  <refined answer>
</answer>
<confidence>
  0.81
</confidence>
```

**置信度变化**：0.72 → 0.81（提升 0.09，仍未达阈值 0.85）

## 轮次 3 · Critique-Refine

**段落**：[P1]

**核查员评语**：
- 核查员发现：<critique notes>
- 建议修改：<suggested changes>

**修订员修订**：
- 修订前：<answer before>
- 修订后：<answer after>

**置信度变化**：0.81 → 0.88（提升 0.07，达阈值 0.85，pass）

## 修订前后对照

| 段落 | 修订前回答 | 修订后回答 | 关键变化 |
|------|-----------|-----------|----------|
| [P1] | <original> | <final> | <changes summary> |

## 修订效果评估

- **总修订轮次**：3
- **置信度提升**：0.55 → 0.88（+0.33）
- **是否达阈值**：是（0.88 ≥ 0.85）
- **最终判定**：verified（标注"3 轮修订"）

## 未达阈值的兜底

> 若 3 轮修订后仍未达阈值，进入兜底：
> - 综合置信 < 0.5 且无 T1/T2 → 拒答或列多答案
> - critical 风险 + 置信 < 0.8 → 强制人审
> - 高风险操作 → 双人审
