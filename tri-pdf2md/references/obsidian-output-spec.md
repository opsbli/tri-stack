---
name: obsidian-output-spec
description: tri-pdf2md 门E 类 Obsidian 结构化输出规范——frontmatter schema、页码锚点语法、标题树 ToC、坐标字段定义。本文件是该输出格式的唯一事实源。
version: 1.1.0
---

# 类 Obsidian 结构化输出规范（唯一真源）

> 适用门：门E（`scripts/structure_pack.py`）。设计动机（用户硬要求）：PDF 是**有时效、有坐标的数据源**——输出 MUST 强制携带文档名/版本/页码元数据，锚点由框架硬编码写入，NEVER 依赖模型自觉。

## 一、设计目标

1. **可放进 Obsidian 库直接用**：YAML frontmatter + 标准 Markdown + Obsidian 注释锚点（`%% ... %%`，渲染时不可见）。
2. **元数据强制不可缺**：文档名（时效入口）、版本（时效判定）、页码（空间锚点）三大字段缺失任一即视为不合格输出。
3. **可回溯**：任一段落可经锚点定位回原 PDF 页面（配合 chunks.json 的 bbox 坐标进一步定位到页面区域）。

## 二、frontmatter schema（强制字段表）

```yaml
---
title: "2026年Q2财务报告"            # 文档名：--doc-name 覆盖或缺省取 PDF 文件名（去扩展名）
source_file: "report_q2.pdf"          # 源 PDF 文件名（含扩展名）
source_path: "d:/docs/report_q2.pdf"  # 源 PDF 绝对路径（转换时刻快照）
doc_version: "v2026-08-24_a3f2"       # 时效标识：--doc-version 覆盖；缺省=PDF修改日期_页数指纹(短哈希)
pages: 42                             # 总页数
page_range: "1-42"                    # 转换覆盖页范围（全量即 1-pages）
converted_at: "2026-08-24T15:30:00"   # 转换时刻（ISO 8601 本地时区）
backend: "mineru"                     # 门C 实际执行后端 slug
grade: "L2"                           # 转换档位
confidence: "A"                       # 门D 置信度等级（A/B/C）
fidelity_rate: 0.971                  # 门D 保真率（扫描件为 null + confidence_note）
toc:                                  # 标题树（层级数组，供 Obsidian 大纲与下游结构消费）
  - "1 总体业绩"
  - "1.1 营收构成"
tags: [pdf2md, <用户附加标签>]
---
```

**强制校验**（structure_pack.py 内置）：title/source_file/doc_version/pages 四字段任一缺失 → 输出 `invalid=true` 并退出码 3；fidelity_rate 扫描件场景 MUST 为 `null`（NEVER 编造）。

## 三、正文页码锚点语法

- **节级锚点**：每个标题块（heading）末尾追加 Obsidian 注释 `%% p.N %%`（N 为该节起始页，1-based）。
- **跨页节**：`%% p.12-14 %%` 表示该节跨 12–14 页。
- **锚点对正文零侵入**：`%% %%` 在 Obsidian 阅读视图/预览中不渲染；纯文本场景可整行正则 `%%\s*p\.\d+(-\d+)?\s*%%` 一键剥离。
- **图片**：`![题注](assets/xxx.png) %% p.13 %%`——资产引用与页锚同点。

## 四、页码锚点判定算法（确定性，脚本内实现）

1. PDF 侧：pdfplumber 抽取每页文本，归一化（去空白/统一全半角）为页文本序列。
2. MD 侧：按标题切块，取每节归一化文本的**首 40 字符**作为指纹。
3. 匹配：指纹在页文本序列中 `find` 命中 → 该页即锚点页；未命中 → 退化为取该节前序最近命中节的页码并标记 `anchor_source="inherited"`；全无命中（扫描件无文本层）→ `anchor_source="unavailable"`，锚点输出 `%% p.? %%` 并在 chunks.json 标记。
4. NEVER 用模型猜页码；匹配失败必须显式标记。

## 五、坐标字段定义（写入 chunks.json，正文不携带）

| 字段 | 类型 | 含义 | 单位 |
|---|---|---|---|
| `page` | int | 1-based 页码 | 页 |
| `bbox` | [x0,y0,x1,y1] | 块文本在页面上的近似外接矩形 | pt（PDF 点，左上原点，pdfplumber 口径） |
| `bbox_confidence` | "exact"\|"approx" | exact=指纹精确命中该页字符区间；approx=仅页级命中，bbox 取页面正文区 | — |

## 六、与 Obsidian 特性的配合建议（非强制）

- frontmatter 的 `tags`/`toc` 可直接被 Obsidian Properties 与 Dataview 消费。
- 双链：`[[文档名#节标题]]` 可指向本笔记节；跨文档引用建议走 chunks.json 的 `doc_id + chunk_id`（机器侧稳定标识，标题改名不漂移）。

## 七、修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.1.0 | 2026-08-24 | 新增（用户补充要求回写：版面结构化 + 强制元数据 + 坐标锚点） |
