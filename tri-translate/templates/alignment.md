---
alignment_id: <UUID，与 translation_id 一致>
translation_id: <translation_id>
source_lang: <源语言>
target_lang: <目标语言>
total_segments: <段落总数>
free_count: <意译段数>
literal_count: <直译段数>
preserved_count: <不译段数>
created_at: <ISO8601>
schema_version: 1
---

# 原文-译文对照表 · <translation_id 前 8 位>

> 本文件由 tri-translate 的 TRANSLATE_EXECUTE 模式产出，提供段落级原文-译文对照。
> 文件名示例：`TRANSLATE_20260801_143022_6a5c037d/alignment.md`
> 存放路径：`.tribro/translate/<命名>/alignment.md`

---

## 策略分布

<!-- 统计三策略在本次翻译中的分布，便于人工评估策略选择是否合理。 -->

| 策略 | 段数 | 占比 |
|------|------|------|
| 意译（free） | <free_count> | <%> |
| 直译（literal） | <literal_count> | <%> |
| 不译（preserved） | <preserved_count> | <%> |
| **合计** | <total_segments> | 100% |

---

## 段落级对照

<!-- 每段落一行，逐段对齐原文与译文。占位符已还原，原文呈现真实不译要素。
     策略列取值：free / literal / preserved。
     备注：标注触发退守的原因（如"术语密集"/"含代码"/"路径保留"）。 -->

| 段落 # | 原文 | 译文 | 策略 | 备注 |
|--------|------|------|------|------|
| 1 | <原文段落 1> | <译文段落 1> | <free\|literal\|preserved> | <备注> |
| 2 | <原文段落 2> | <译文段落 2> | <free\|literal\|preserved> | <备注> |
| ... | ... | ... | ... | ... |

---

## 自检结论

- **段数一致性**：原文段数 = 译文段数（MUST 一致）
- **策略标注完整性**：每段 MUST 标注策略
- **占位符还原**：原文展示真实要素，无 `__<TYPE>_<N>__` 残留
