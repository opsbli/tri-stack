---
translation_id: <UUID，如 550e8400-e29b-41d4-a716-446655440000>
source_lang: <源语言，如 en>
target_lang: <目标语言，如 zh-CN>
doc_type: <technical_doc | marketing | ui | academic | chat | legal>
audience: <developer | general | academic | business>
register: <formal | informal>
strategy_used: <free | literal | mixed>
glossary_version: <术语表版本，如 1>
never_translate_version: <不译规则集版本，如 1>
upstream_mode: <A_snapshot | B_install_prompt | C_degraded>
session_id: <会话ID，如 6a5c037d>
created_at: <ISO8601，如 2026-08-01T14:30:22+08:00>
mqm_score: <0-100，如 92>
mqm_status: <pass | fail>
retry_count: <重译次数，0-2>
placeholder_residual_count: <占位符残留数，MUST=0>
schema_version: 1
---

# 译文交付物 · <translation_id 前 8 位>

> 本文件由 tri-translate 的 TRANSLATE_EXECUTE 模式产出，是最终译文交付物。
> 文件名示例：`TRANSLATE_20260801_143022_6a5c037d/deliverable.md`
> 存放路径：`.tribro/translate/<命名>/deliverable.md`

---

## 上下文摘要

<!-- 简述本次翻译的上下文，便于审计复现。三要素：文档类型、目标读者、风格 register。 -->

- **文档类型**：<doc_type>
- **目标读者**：<audience>
- **风格等级**：<register>
- **主策略**：<strategy_used>
- **上游模式**：<upstream_mode>（A=快照模式 / B=引导安装 / C=降级模式）

---

## 译文正文

<!-- 三策略分层产出的最终译文。占位符已 100% 还原为原文要素。
     翻译过程 NEVER 翻译占位符；译后 MUST 还原所有占位符，残留则 NEVER 交付。 -->

<这里放置三策略分层产出的最终译文，按原文段落结构组织。所有 __<TYPE>_<N>__ 占位符已还原为原文要素。>

---

## 不译要素清单（摘要）

<!-- 列出译文内保留原文的要素，便于人工复核。完整清单见同目录 preserved.md。 -->

| 类型 | 数量 | 示例 |
|------|------|------|
| 路径 | <N> | <示例> |
| 代码 | <N> | <示例> |
| URL | <N> | <示例> |
| 品牌名 | <N> | <示例> |

---

## 自检结论

- **占位符残留数**：`<placeholder_residual_count>`（MUST = 0）
- **MQM 综合得分**：`<mqm_score>` / 100
- **MQM 状态**：`<mqm_status>`（pass=通过 / fail=未通过门槛）
- **重译次数**：`<retry_count>`（0-2，超过则退守直译）

> 若 `placeholder_residual_count > 0` 或 `mqm_status = fail`，本译文 NEVER 应交付。须回到处理流程重译或退守直译。
