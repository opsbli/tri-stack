---
name: rag-handoff-spec
description: tri-pdf2md 门E RAG 双路召回数据供给契约——权限/版本过滤字段、BM25/向量双路数据、重排候选结构、LLM-as-Judge 四指标职责分工。本文件是 RAG 对接的唯一事实源。
version: 1.1.0
---

# RAG 双路召回数据供给契约（唯一真源）

> 适用门：门E。总纲（用户硬要求）：**PDF 是有时效、有坐标的数据源，通过框架硬编码实现全链路可控，而非依赖模型自觉。**
> **MECE 职责边界**：本 skill 是数据供给侧；检索执行（关系库/ES/向量库）、重排、生成、评测运行归下游 RAG 系统。本 skill NEVER 建索引、NEVER 跑检索、NEVER 跑重排——只保证供出去的数据结构完整、锚点齐全。

## 一、供给总览（下游链路 × 本 skill 产物）

```
tri-pdf2md 供给                          下游 RAG 系统（消费侧）
─────────────────                        ─────────────────────────
chunks.json ─┬─ 权限/版本过滤字段 ──────► 关系库/ES：doc_id + doc_version + 权限标签过滤
             ├─ 子块纯文本 ────────────► BM25 索引（关键词路）
             ├─ 子块文本(+metadata) ───► Embedding（向量路）
             ├─ 父子关联结构 ──────────► 重排模型：子块命中→父块入精选候选
             └─ page/bbox/heading_path ► 引用溯源：答案句 → 原PDF页/区域定位
report.md ──── 保真率/异常 ────────────► 评测体系：解析完整率数据源
structure.json ─ anchor_coverage ──────► 评测体系：引用可追溯率数据源
```

## 二、双路召回数据契约

### 2.1 先过滤：权限与版本（硬编码字段，下游消费）

| 字段 | 载体 | 用途 |
|---|---|---|
| `doc_id` | chunks.json 顶层 | 文档稳定标识（文件名+页数+大小短哈希）；权限标签由下游关系库按 doc_id 挂接 |
| `doc_version` | 顶层 + 每块 | 时效过滤主键：同 doc_id 新版本转换 → 新 doc_version → 下游按「doc_id + 最新 doc_version」淘汰旧块（旧版本可归档供审计） |
| `page` / `page_range` | 每块 / 父块 | 版本内空间定位 + 增量更新时按页 diff |

**更新流约定**：PDF 修订 → 重新经本 skill 全管道 → 产出新 doc_version 的 chunks.json → 下游整体替换该 doc_id 的块集——**NEVER 增量 patch 旧块**（页码坐标会整体漂移，patch 会造成锚点错位）。

### 2.2 BM25 路（关键词召回）

- 数据：子块 `text` 原文（后端已去页眉页脚；MD 语法噪声由 structure_pack 在导出时保留原样，下游按需再清洗）。
- 建议：BM25 索引粒度 = 子块；`heading_path` 可作为字段加权（标题词命中权重↑）。

### 2.3 向量路（语义召回）

- 数据：子块 `text`；**若 metadata 已补全**（entity/entity_aliases/source_context），建议拼接进 embedding 文本——「同比增长 3%」单句无主语，补「腾讯控股/2026Q2财报」后向量才可被「腾讯 Q2 增长」类查询命中。
- 双路融合（RRF 等）归下游。

### 2.4 重排精选

- 数据：父子关联（子块 `parent_id` / 父块 `children`）。
- 约定：粗排取 Top-K 子块 → 取其父块（去重）入重排 → 重排模型精选证据 → 生成上下文 = 精选父块（必要时附兄弟块标题）。父块即 Small-to-Big 的「Big」。

## 三、引用溯源契约

- 每个子块带 `page` + `bbox`（+ `heading_path` 人读定位）。
- 下游答案句标注 `chunk_id` → 反查 `doc_id + doc_version + page + bbox` → 定位原 PDF 页面区域（PDF 查看器 `#page=N` + 高亮 bbox）。
- `anchor_source="unavailable"`（扫描件等）的块 MUST 在引用 UI 标注「坐标不可追溯」——NEVER 静默降级。

## 四、LLM-as-Judge 评测四指标分工（用户硬要求）

| 指标 | 归属 | 数据源/算法 | 说明 |
|---|---|---|---|
| **解析完整率** | 本 skill 计算 | 门D `quality_check.py` 保真率（PDF 文本层 → MD 召回率） | 供给评测体系直接采用；扫描件为 null + 显式标注 |
| **引用可追溯率** | 本 skill 计算数据，下游运行 | 门E `anchor_coverage`（带 page+bbox 子块占比）× 答案实际引用块的可追溯比例 | 分两段：语料侧覆盖率（本 skill）+ 问答侧引用率（下游 Judge 按答案标注统计） |
| **召回命中率** | 下游 | Judge 生成问题集 → 双路召回 gold chunk 命中率 | 本 skill 供给 gold chunk 语料（chunks.json + 人工 reviewed 标记可作 gold 池） |
| **生成忠实度** | 下游 | Judge 对比答案与证据块（忠实度/幻觉判定） | 证据块原文即 `text` 字段——保真红线保证证据未被调优改写 |

**口径提醒**：四指标中本 skill 只「算得了的」（前两项的数据）才承诺计算；召回/生成指标 NEVER 在本 skill 报告中编造。

## 五、不做清单（防职责膨胀）

- NEVER 建 ES/向量索引，NEVER 写检索 DSL
- NEVER 集成/调用重排模型
- NEVER 运行 LLM-as-Judge（只供给 Judge 所需数据）
- NEVER 生成答案或引用 UI（只供给 chunk_id→page/bbox 映射）

## 六、修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.1.0 | 2026-08-24 | 新增（用户补充要求回写：双路召回数据供给 + 评测四指标分工） |
