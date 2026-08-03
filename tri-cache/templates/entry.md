---
name: cache-entry-template
description: tri-cache 缓存原文 Markdown 模板。每条缓存条目的冷层原文格式，含 frontmatter 元数据 + 用户提问 + AI 回答 + 摘要四段。
---

# 缓存原文 · <问题类型>_<日期>_<时间>_<会话ID>_<hash8>

> 本文件是 tri-cache 的冷层存储单元，由 CACHE_WRITE 流程自动生成。
> 文件名示例：`I08_20260801_143022_6a5c037d_a1b2c3d4.md`
> 存放路径：`.tribro/cache/entries/<YYYY-MM>/`

---

## 元数据（frontmatter）

```yaml
---
cache_key: <SHA-256前16位，如 a1b2c3d4e5f6a7b8>
intent:
  l1: <A.Asking | B.Doing | C.Expressing | Meta>
  l2: <如 I08>
  aux: [<辅助意图>]
dimensions:
  d1: <办公|学习|编程|生活|创作|商业|情感|科研|未指定>
  d2: <文本|代码|图片|文档|表格|音视频|链接|无>
  d3: <单轮|多轮|长程Agent>
  d4: <简答|长文|结构化数据|可执行代码|文件产物|分步指引>
  d5: <明确|模糊|开放>
session_id: <会话ID，如 6a5c037d>
user_id: default
source_skill: <如 tri-ask|tri-content|tri-coding>
created_at: <ISO8601，如 2026-08-01T14:30:22+08:00>
ttl_seconds: <秒，如 2592000；null=永久>
expires_at: <ISO8601，如 2026-08-31T14:30:22+08:00>
tags: [<关键词，如 翻译, 中英>]
status: active
schema_version: 1
---
```

---

## 用户提问

<逐字粘贴用户的原始提问，保留原始措辞与格式。隐私过滤后敏感内容替换为 ***REDACTED***。>

```text
<原文>
```

---

## AI 回答

<逐字粘贴 AI 的完整回答，保留原始格式。隐私过滤后敏感内容替换为 ***REDACTED***。>

```text
<原文>
```

---

## 摘要

<≤200 字摘要，用于索引检索快速预览。由 CACHE_WRITE 流程生成（抽取式或 LLM 摘要）。>

---

## 复用建议

<由 CACHE_LOOKUP 流程在检索时追加，本模板不预填。按 L2 标注：
- I01-I02：直接复用（TTL 内有效）
- I03-I05/I06-I10/I13-I16：参考注入（请核实后使用）
- stale 状态：可能过时，强烈建议核实>
