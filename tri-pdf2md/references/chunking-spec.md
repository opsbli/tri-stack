---
name: chunking-spec
description: tri-pdf2md 门E Small-to-Big 父子分块规范——分块策略、块 schema、元数据槽位、人工调优工作流与 review.html 交互契约。本文件是分块策略的唯一事实源。
version: 1.1.0
---

# Small-to-Big 父子分块规范（唯一真源）

> 适用门：门E（`scripts/structure_pack.py`）。设计动机（用户硬要求）：检索命中要精准（小块），上下文要完整（大块）——Small-to-Big 解耦两者；边界与元数据补全提供**可视化人工调优界面**，框架硬编码锚点，不依赖模型自觉。

## 一、Small-to-Big 核心机制

```
父块（Parent · 检索上下文层）          子块（Child · 匹配粒度层）
┌──────────────────────────┐      ┌─────────────┐ ┌─────────────┐
│ 3.1 营收构成（章节全文）    │ ◄──  │ c01 段落/表格 │ │ c02 段落/公式 │ ...
│ 1500–3000 字符            │      │ ≤800 字符    │ │ ≤800 字符   │
└──────────────────────────┘      └─────────────┘ └─────────────┘
检索：子块参与 BM25/向量召回 → 命中子块 → 返回其父块（+兄弟块摘要）入重排与生成上下文
```

- **父块**：章节级（`--parent-granularity section` 缺省）或页级（`page`，无清晰标题的 PDF 用）。容量上限 3000 字符，超限按下一级标题再切。
- **子块**：段落级（MD 空行分界）；超 `--child-max-chars`（缺省 800）按句末标点（。！？；.!?）二次切分；表格整体为一个子块 NEVER 从中切断；代码块/公式块整体为一个子块。
- **块间关系**：子块 MUST 记录 `parent_id`；父块 MUST 记录 `children` 列表——双向可遍历。

## 二、chunk schema（`<同名>.chunks.json`）

```json
{
  "doc_id": "report_q2_pdf_1a2b3c",           // 文档稳定标识（文件名+页数+大小短哈希）
  "doc_version": "v2026-08-24_a3f2",           // 时效标识（同 frontmatter）
  "generated_at": "2026-08-24T15:31:00",
  "parent_granularity": "section",
  "child_max_chars": 800,
  "chunks": [
    {
      "chunk_id": "p001",                      // 父块 pNNN
      "type": "parent",
      "level": 2,                              // 标题层级（页级父块为 null）
      "heading_path": ["3 分部业绩", "3.1 营收构成"],   // 标题树路径
      "text": "…章节全文…",
      "page_start": 12, "page_end": 14,
      "children": ["p001-c01", "p001-c02"],
      "char_count": 1820
    },
    {
      "chunk_id": "p001-c01",                  // 子块 pNNN-cMM
      "type": "child",
      "parent_id": "p001",
      "heading_path": ["3 分部业绩", "3.1 营收构成"],
      "text": "…段落原文（NEVER 改写）…",
      "page": 12,
      "bbox": [72.0, 120.5, 523.0, 340.2],     // pt，pdfplumber 口径
      "bbox_confidence": "exact",
      "char_count": 316,
      "metadata": {                            // 人工补全槽位（可空）
        "entity": "",                          // 例：「腾讯控股」
        "entity_aliases": [],                  // 例：["0700.HK", "Tencent"]
        "source_context": "",                  // 例：「2026Q2 财报」——补全「同比增长3%」的主语场景
        "reviewed": false                      // 人工已核= true
      }
    }
  ]
}
```

**保真红线**：`text` 字段是转换产物原文；人工调优 NEVER 改写 `text`——补全信息只进 `metadata`（召回时拼接进 embedding 文本，不改证据原文）。

## 三、锚点覆盖率（anchor_coverage）

- 定义：`带 page+bbox 的子块数 / 子块总数`（`anchor_source != "unavailable"`）。
- 口径：exact + approx 都计入覆盖；扫描件全量 unavailable → coverage 如实为 0.0 并注明「无文本层，坐标不可计算」。
- 用途：LLM-as-Judge「引用可追溯率」的数据源（见 rag-handoff-spec.md §四）。

## 四、人工调优工作流（review.html 交互契约）

review.html 是**自包含静态页**（无服务器、无外部依赖、数据内嵌），浏览器直接打开：

| 操作 | 交互 | 落点 |
|---|---|---|
| 调整边界·合并 | 选中相邻子块 → 「合并」按钮 | 合并为一个子块（text 以 `\n\n` 连接，锚点取并集，chunk_id 重编） |
| 调整边界·拆分 | 选中子块 → 光标定位切点 → 「在此拆分」 | 一拆二，锚点按指纹就近归属 |
| 补全元数据 | 子块编辑面板：entity / entity_aliases / source_context 输入框 | 写入 metadata 槽位；示例引导文案：「同比增长 3%」→ 补「腾讯控股」入 entity |
| 标记已核 | 「已核」开关 | metadata.reviewed = true |
| 导出 | 「导出修订版」按钮 | 浏览器下载修订版 `chunks.revised.json`（含 `revised_at` 时间戳）；原 chunks.json NEVER 被覆盖 |

**回灌约定**：修订版文件与原版同 schema（仅多 `revised_at` 顶层字段）；入库时以下游摄取器消费 `chunks.revised.json` 为准；修订统计（合并/拆分/补全次数）可反馈进化契约触发条件④。

## 五、参数缺省与调整入口

| 参数 | 缺省 | 调整方式 |
|---|---|---|
| parent_granularity | section | CLI `--parent-granularity page`（标题树缺失/混乱时） |
| child_max_chars | 800 | CLI `--child-max-chars`；>1200 或 <300 需在 chunks.json 记录非缺省告警 |
| 父块容量上限 | 3000 | 常量（structure_pack.py 顶部），修订须同步本文件 |

## 六、修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.1.0 | 2026-08-24 | 新增（用户补充要求回写：Small-to-Big 父子分块 + 可视化人工调优） |
