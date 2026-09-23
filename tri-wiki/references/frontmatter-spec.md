---
name: frontmatter-spec
description: tri-wiki 知识库笔记 YAML frontmatter 字段规范——必填/可选/类型/默认值的唯一事实源。
---

# 知识库笔记 Frontmatter 字段规范（frontmatter-spec）

> tri-wiki 门D（元数据注入）与门F（组织完整度校验）的唯一事实源。调整字段时只改本文件 + `organize.py` 的 `REQUIRED_FIELDS` 常量。
> grep 检索模式：`必填` / `可选` / `字段` / `生命周期` / `status` / `dup_group` / `untrusted`。

## 一、字段总表

| 字段 | 类型 | 必填 | 默认/生成规则 | 说明 |
|---|---|---|---|---|
| `title` | string | ✅ | 取 H1 或文件名（去扩展名） | 给人看的标题，非文件名 |
| `type` | string | ✅ | `doc` | `doc`（笔记）/ `moc`（索引页）/ `index`（首页） |
| `source` | string | ✅ | 源文件绝对路径 | 可追溯（直通类=原路径；转换类=原路径） |
| `source_format` | string | ✅ | 按扩展名 | `pdf`/`docx`/`pptx`/`xlsx`/`html`/`md`/`txt`/`csv` |
| `created` | date | ✅ | 构建日 `YYYY-MM-DD` | ISO 8601 |
| `tags` | list | ❌ | 空列表 | 主题词表 + 内容标签（≤5） |
| `status` | string | ❌ | `seedling` | 生命周期六态，唯一真源 `lifecycle-spec.md` §2：`seedling`/`budding`/`evergreen`/`stale`/`deprecated`/`archive` |
| `aliases` | list | ❌ | 空列表 | 别名，供链接匹配与检索 |
| `updated` | date | ❌ | 同 `created` | 最近更新 |
| `converter` | string | ❌ | 空 | 转换器与版本（如 `tri-pdf2md@1.1.0`；直通类留空） |
| `fidelity` | number | ❌ | 空 | 该文件转换保真率（convert 类从质量报告继承） |
| `split_from` | string | ❌ | 空 | 拆分子页指向父页文件名（原子化拆分时写入） |
| `kb` | string | ❌ | 库名 | 所属知识库（多库场景区分） |
| `reviewed` | date | ❌ | 空 | 最近一次复核日期（`lifecycle_govern.py --apply` 写入） |
| `dup_group` | string | ❌ | 空 | 近重复簇号（`dedup_content.py --apply` 写入；人工仲裁后按需删除） |
| `untrusted` | bool | ❌ | 空 | 正文疑似含指令注入文本时置 `true`，处置见 `lint-rules.md` §4 |

## 二、书写规范（YAML 硬约束）

1. frontmatter MUST 位于文档首行 `---` 开始，前后无空行，无 BOM 字符。
2. 字段名用合法标识符（小写英文+下划线），NEVER 中文/空格/特殊符号。
3. 布尔值写 `true`/`false`，NEVER 「是/否」。
4. 日期统一 ISO 8601（`YYYY-MM-DD`）。
5. 列表用块式写法（`- 项`）或流式（`[a, b]`），单文件内保持一致。
6. 字符串含 `:` 或 `#` 时 MUST 加引号。

## 三、生成模板

### 3.1 普通笔记（doc）

```yaml
---
title: Koa 中间件机制
type: doc
source: D:\docs\后端\koa指南.pdf
source_format: pdf
created: 2026-08-24
tags: [后端, Node.js, 中间件]
status: seedling
aliases: [洋葱模型]
converter: tri-pdf2md@1.1.0
fidelity: 0.95
---
```

### 3.2 MOC 索引页（moc）

```yaml
---
title: 后端 MOC
type: moc
source: tri-wiki generated
source_format: md
created: 2026-08-24
tags: [后端, MOC]
status: seedling
---
```

### 3.3 首页（index）

```yaml
---
title: <库名> 知识库
type: index
source: tri-wiki generated
source_format: md
created: 2026-08-24
tags: [MOC]
status: seedling
---
```

## 四、组织完整度校验（门F）

- 必填五字段（title/type/source/source_format/created）逐文件解析校验，覆盖率 MUST = 100%。
- 缺失字段由 `organize.py` 注入时自动补全（NEVER 留空交付）；`type: doc` 且 `source` 为占位值（`tri-wiki generated`）视为异常——doc 类 MUST 指向真实源。
- YAML 解析失败 → 该文件计为「组织失败」，进报告复核项。

## 五、治理字段的写入者（门G）

| 字段 | 初次注入 | 后续治理 |
|---|---|---|
| `status` | `organize.py`（默认 `seedling`） | `lifecycle_govern.py --apply`（显式要求，NEVER 静默跃迁） |
| `reviewed` | 不写 | `lifecycle_govern.py --apply` 写入当日日期 |
| `dup_group` | 不写 | `dedup_content.py --apply` 写入簇号 |
| `untrusted` | 不写 | 人工确认后写入（脚本只检测留痕，NEVER 自动改写） |

治理字段 NEVER 影响必填五字段的完整性判定；缺失治理字段不算组织失败。
