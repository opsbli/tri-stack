# tri-wiki · 知识库搭建 skill

> 从异构源数据（PDF/Word/PPT/Excel/HTML/MD/TXT/CSV）批量搭建本地 Markdown 知识库的编排与质量保障层——Obsidian 兼容 + RAG 就绪 + 建库后可治理。

## 特性

- **六阶段管道**：A 需求与信息架构（确认门①，不可跳过）→ B 收集预检（格式分级 + 去重标记）→ C 批量转换（委派 x2md 族，三态检测）→ D 组织元数据（frontmatter 注入 + 确认门②）→ E 链接索引（MOC/双向链接 + 确认门③）→ F 质量交付（指标报告）
- **治理层门G（可选）**：建库之后的持续保养——增量同步（mtime+hash 双判据，索引可重建）、内容可信度评分（五分量 + 缺失重归一化 + 硬地板）、转载/近重复聚类（Jaccard，大库自动切 minhash+LSH）、生命周期状态机（成长轨 + 衰减轨，写入须确认）、结构化体检（12 条规则，error/warning/info 分级）
- **委派不重造**：单文档转换全部委派 tri-pdf2md / tri-docx2md / tri-pptx2md / tri-xlsx2md / tri-html2md，本 skill 专注集合级组织、链接、索引、质量、治理
- **三道人工确认门**：信息架构（不可跳过）/ 分类归置 / MOC 链接（②③可 `--auto`）；源数据全程只读
- **主题树 + MOC 双层结构**（默认；可选 PARA / Johnny Decimal / MOC-only）
- **可验证质量契约**：覆盖率 / 组织完整度 / 断链率 / 链接密度 / 重复率 / 可信度 / 置信度 A/B/C 分级，不可计算项显式「不适用」
- **不可信输入隔离**：网页/第三方文档正文中的指令性文本一律视为数据，检测留痕、NEVER 静默清洗
- **完成判据外化**：六条可机械校验判据 + 停车态/结束态区分，NEVER 依赖模型自述完成
- **RAG 就绪出口**：`--rag` 输出 Small-to-Big 父子分块 JSONL（数据供给层，不越界建向量库）
- **全程可追溯**：八份过程数据落 `.tribro/wiki/WIKI_<日期>_<命名>/`；`.wiki-meta/build-manifest.json` 记录源→产物映射；经验教训累积于 `.tribro/wiki/lessons.md`

## 目录结构

```
tri-wiki/
├── SKILL.md                       主入口
├── README.md / CHANGELOG.md / _meta.json
├── references/
│   ├── kb-formats.md              源格式×skill 映射矩阵
│   ├── ia-methods.md              组织方法论（主题树/MOC/PARA/JD）
│   ├── frontmatter-spec.md        frontmatter 字段规范（含治理字段）
│   ├── output-structure-spec.md   知识库结构与模板
│   ├── credibility-spec.md        可信度评分与转载聚类规范（门G）
│   ├── lifecycle-spec.md          生命周期状态机与增量同步规范（门G）
│   ├── lint-rules.md              结构化体检 12 条规则（门F/门G）
│   └── version-check-spec.md      版本检查规范（家族同源）
├── scripts/
│   ├── scan_sources.py            门B 扫描预检
│   ├── convert_orchestrate.py     门C 委派计划与汇总
│   ├── organize.py                门D 归置与元数据
│   ├── index_build.py             门E 索引与断链
│   ├── quality_check.py           门F 质量报告
│   ├── sync_incremental.py        门G 增量同步（plan/apply/rebuild）
│   ├── credibility_score.py       门G 可信度评分 + 转载聚类
│   ├── dedup_content.py           门G 内容级近重复（--apply 写 dup_group）
│   ├── lifecycle_govern.py        门G 生命周期推进（plan/apply）
│   ├── lint_vault.py              门F/门G 结构化体检（--strict 退出码 3）
│   └── check_update.py            版本检查（家族同源）
└── tests/
    └── tri-wiki-full-testcases.md
```

> 全部脚本仅依赖 Python 标准库（无第三方运行时依赖）。

## 安装

```bash
skillhub install tri-wiki --dir <目标目录>
# 或 tri-forge 安装链：python install_skill.py --skill .tribro/skills/tri-wiki
```

## 使用

```bash
# 独立运行（经 Skill 激活）
Use Skill: tri-wiki 把 d:\docs\项目资料\ 搭建成知识库

# 阶段脚本（Agent 按管道调用）
python scripts/scan_sources.py --sources d:\docs\项目资料 --json
python scripts/convert_orchestrate.py --plan --manifest sources-manifest.json --json
python scripts/organize.py --kb-root <库名> --plan classify-plan.json
python scripts/index_build.py --kb-root <库名> --moc-plan moc-plan.json
python scripts/quality_check.py --kb-root <库名> --process-dir .tribro/wiki/WIKI_*/
python scripts/lint_vault.py --kb-root <库名> --strict --json

# 治理层（建库后可选；写入类动作先 plan 后确认）
python scripts/sync_incremental.py  --kb-root <库名> --mode plan
python scripts/credibility_score.py --kb-root <库名> --json
python scripts/dedup_content.py     --kb-root <库名> --json          # 先看建议，再 --apply
python scripts/lifecycle_govern.py  --kb-root <库名> --plan --json   # 再看建议，再 --apply
```

## 测试

见 `tests/tri-wiki-full-testcases.md`（能力清单全覆盖用例，含治理层门G 分组）。

## 设计原则

1. **规范是唯一事实源**：frontmatter/结构/格式矩阵/方法论/可信度/生命周期/规则集七份真源在 references/，正文仅指针 + grep 模式。
2. **确定性算法下沉**：分级/归置/索引/指标/治理全部脚本化，语义环节（分类/MOC 草稿）产草稿 + 确认门。
3. **源数据零触碰**：全程只读，产物独立目录；高风险操作（批量覆盖/删除）永不发生。
4. **MECE 边界**：单文档转换归 x2md 族，集合建库归本 skill；检索执行归下游 RAG；发布部署仅出指引；网页抓取与学术检索 NEVER 自建。
5. **索引是缓存**：`.wiki-meta/` 下派生数据可删除重建；治理结论（status/dup_group）写入笔记 frontmatter 随笔记走，不随索引走。
6. **治理非静默**：检测与建议自动化，取舍与废弃人工化——机器提示「这篇该退了」，NEVER 替用户决定「这篇废了」。
