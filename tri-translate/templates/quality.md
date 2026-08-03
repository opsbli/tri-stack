---
quality_id: <UUID，与 translation_id 一致>
translation_id: <translation_id>
source_lang: <源语言>
target_lang: <目标语言>
mqm_framework: <MQM-Core-v1>
total_segments: <段落总数>
overall_score: <0-100，如 92>
overall_status: <pass | fail>
upstream_mode: <A_snapshot | B_install_prompt | C_degraded>
degraded_notice: <若有则填"降级模式：精度低于标准链路"，否则 null>
created_at: <ISO8601>
schema_version: 1
---

# MQM 质量自检报告 · <translation_id 前 8 位>

> 本文件由 tri-translate 的 TRANSLATE_EXECUTE 模式产出，记录 MQM Core 4 维 + Hallucination 子维的质量自检结果。
> 文件名示例：`TRANSLATE_20260801_143022_6a5c037d/quality.md`
> 存放路径：`.tribro/translate/<命名>/quality.md`
> 质量门槛：Accuracy / Design / Hallucination 的 Critical+Major 错误 MUST = 0；Fluency / Terminology 允许 Minor。

---

## 一、维度汇总

<!-- 五维度统计错误数与扣分。Critical=10 / Major=5 / Minor=1 / No-error=0。
     维度扣分 = Σ(错误权重)；维度得分 = max(0, 100 - 维度扣分)。
     总得分 = 五维度得分加权平均（Accuracy 30% / Fluency 20% / Terminology 20% / Design 20% / Hallucination 10%）。
     总状态 = pass 当且仅当 Accuracy+Design+Hallucination 的 Critical+Major 全 0，且总得分 ≥70。 -->

| 维度 | Critical | Major | Minor | No-error | 扣分 | 得分 | 权重 |
|------|----------|-------|-------|----------|------|------|------|
| **Accuracy**（语义等价性） | <N> | <N> | <N> | <N> | <扣分> | <0-100> | 30% |
| **Fluency**（中文通顺度） | <N> | <N> | <N> | <N> | <扣分> | <0-100> | 20% |
| **Terminology**（术语一致性） | <N> | <N> | <N> | <N> | <扣分> | <0-100> | 20% |
| **Design**（markup 保留度） | <N> | <N> | <N> | <N> | <扣分> | <0-100> | 20% |
| **Hallucination**（幻觉检测） | <N> | <N> | <N> | <N> | <扣分> | <0-100> | 10% |

**总得分**：`<overall_score>` / 100　**总状态**：`<overall_status>`

---

## 二、门槛检查

| 门槛 | 标准 | 实际 | 是否通过 |
|------|------|------|----------|
| Accuracy Critical+Major | = 0 | <N> | <pass\|fail> |
| Design Critical+Major | = 0 | <N> | <pass\|fail> |
| Hallucination Critical+Major | = 0 | <N> | <pass\|fail> |
| Fluency Major | ≤ 2 | <N> | <pass\|fail> |
| Terminology Major | ≤ 1 | <N> | <pass\|fail> |
| 总得分 | ≥ 70 | <N> | <pass\|fail> |

> 任一门槛 fail，则整体 fail，须重译（最多 2 次）或退守直译。

---

## 三、错误明细

<!-- 列出所有检测到的错误，按段落定位。Critical/Major MUST 列出，Minor 可选。
     错误类型示例：accuracy-omission / accuracy-addition / fluency-grammar / fluency-europeanized / terminology-inconsistent / design-broken-markup / hallucination-fabricated / hallucination-altered。 -->

| 段落 # | 维度 | 错误类型 | 严重度 | 原文片段 | 译文片段 | 问题描述 |
|--------|------|----------|--------|----------|----------|----------|
| <N> | <维度> | <类型> | <Critical\|Major\|Minor> | <片段> | <片段> | <描述> |

---

## 四、降级模式声明

<!-- 仅当 upstream_mode = C_degraded 时填写。 -->

> <degraded_notice>

---

## 五、自检结论

- **总得分**：`<overall_score>` / 100
- **总状态**：`<overall_status>`
- **门槛通过情况**：<通过 / 未通过，列出未通过项>
- **重译次数**：<0-2>
- **占位符残留数**：MUST = 0

> 若 overall_status = fail，本译文 NEVER 应交付。须回到处理流程重译或退守直译。
