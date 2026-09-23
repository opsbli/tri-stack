---
name: output-structure-spec
description: tri-wiki 知识库标准输出结构与 index/MOC/tags 模板——门D 门E 生成的唯一事实源。
---

# 知识库标准输出结构与模板（output-structure-spec）

> tri-wiki 门D（归置）与门E（索引生成）的唯一事实源。新增页面类型时在 `index_build.py` 追加生成函数 + 本文件追加模板。
> grep 检索模式：`MOC` / `index` / `模板` / `tags`。

## 一、标准结构（topic-moc 默认；其它方法论骨架见 ia-methods.md §二）

```
<库名>/
├── index.md                 # 首页：库说明 + 统计 + 各 MOC 入口
├── tags.md                  # 标签聚合页
├── 00-Inbox/                # 未分类/低置信度/近重复待仲裁
├── <主题1>/
│   ├── <主题1>-MOC.md       # 主题内容地图
│   └── <标题>.md
├── 90-attachments/          # 图片等附件（assets）
└── .wiki-meta/
    ├── build-manifest.json  # 构建清单（源→产物映射）
    ├── sync-state.json      # 增量同步状态（mtime+hash，可删除后 rebuild）
    ├── credibility.json     # 内容可信度评分与转载簇
    ├── dedup-report.json    # 内容级近重复簇与仲裁建议
    ├── lifecycle-plan.json  # 生命周期推进计划（plan/apply）
    └── lint-report.json     # 结构化体检规则命中清单
```

> `.wiki-meta/` 内除 `build-manifest.json` 外**全部为派生缓存**，可删除后由对应脚本重建；唯一例外是治理标记（`status`/`reviewed`/`dup_group`），它们写入笔记 frontmatter 而非本目录——治理结论随笔记走，不随索引走。

## 二、index.md 模板（首页）

```markdown
---
title: <库名> 知识库
type: index
source: tri-wiki generated
source_format: md
created: <日期>
tags: [MOC]
status: seedling
---

# <库名> 知识库

> 由 tri-wiki 于 <日期> 构建 · 共 <N> 篇笔记 · <M> 个主题 · 置信度 <A/B/C>

## 主题导航

- [[<主题1>-MOC|<主题1>]]（<n1> 篇）
- [[<主题2>-MOC|<主题2>]]（<n2> 篇）

## 使用指引

- 用 Obsidian 打开本目录即可获得图谱/反向链接/全文搜索
- 发布为站点：Quartz / MkDocs Material（命令见 build-report.md）
- RAG 接入：chunks.jsonl 语料（若启用 --rag）
```

## 三、MOC 模板（主题内容地图）

```markdown
---
title: <主题> MOC
type: moc
source: tri-wiki generated
source_format: md
created: <日期>
tags: [<主题>, MOC]
status: seedling
---

# <主题> · 内容地图

> <一句话主题范围说明（来自 build-plan 主题词表）>

## 条目

- [[<笔记1>]] — <一句话简介>
- [[<笔记2>]] — <一句话简介>

## 相关主题

- [[<相邻主题>-MOC]]：<关系说明>
```

## 四、tags.md 模板（标签聚合）

```markdown
---
title: 标签索引
type: moc
source: tri-wiki generated
source_format: md
created: <日期>
tags: [MOC]
---

# 标签索引

## <主题标签1>（<n> 篇）

- [[<笔记A>]] / [[<笔记B>]] …

## <标签2>（<n> 篇）

- …
```

## 五、原子化拆分规范（门D）

- 触发：正文（去 frontmatter）字符数 > `--split-chars`（缺省 8000）。
- 切分：按 H2（`##`）标题切分为子页；无 H2 的超长文档按空段落块切分并标注 `part`。
- 命名：`<标题>-<两位序号>-<H2标题>.md`；父页 `<标题>.md` 保留 frontmatter + ToC（各子页链接 + 一句话简介）。
- 子页 frontmatter：继承父页字段 + `split_from: <父页文件名>`；正文各子页 `type: doc`。
- 附件：子页引用的图片路径统一重指 `90-attachments/`。

## 六、链接生成规则（门E）

| 链接类型 | 匹配依据 | 语法 |
|---|---|---|
| MOC→笔记 | 归属主题目录内全部 doc | `[[<文件名去扩展名>\|<标题>]]` |
| 笔记→笔记（语义建议） | aliases/标题精确匹配正文出现 + LLM 语义建议（确认门③） | `[[<目标>\|<原文>]]` |
| MOC→MOC | 主题词表相邻关系 + 共享标签 | `[[<主题>-MOC]]` |

- 断链判定：`[[]]` 内目标在库内无同名文件（去扩展名比对，含 aliases 解析）。
- 链接密度 = 总链接数 / doc 笔记数；<1 时在报告提示（不阻断）。
