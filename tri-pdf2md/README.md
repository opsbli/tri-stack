# tri-pdf2md · PDF 转 Markdown（编排与质量保障层）

> tri-xxx 家族路由型 skill，认领 **I08 翻译转换 · L3 子意图 `pdf2md`**（经 tri-intent 一跳覆写路由）。也可独立运行。
> 核心理念：**先体检、再选刀、干完活、必须交验、按用途打包**——把「无损」落为可验证的分级保真；**PDF 视为有时效、有坐标的数据源**，锚点框架硬编码，全链路可控不依赖模型自觉。

## 特性

- **五阶段管道**：门A 预检分级（`preflight.py`）→ 门B 后端探测（`detect_backends.py`）→ 门C 版面分析转换（保留层级/坐标/标题树）→ 门D 质量校验（`quality_check.py`）→ 门E 结构化交付（`structure_pack.py`）
- **anydoc 文本层首选（Firecrawl，MIT）**：L0 文本层 PDF 首选 anydoc，扫描页经 needsocr_check.py 信号自动置 L2；L1/L2 DL 链（docling/marker/MinerU）为扫描件主路径不变 → L3 LLM 兜底（须确认成本）
- **P2 方法论落地（anydoc 蒸馏）**：输入规模守卫 `scripts/scale_guard.py`（anydoc limits.rs 硬上限，表格类网格槽位超预算强制 L1）+ `tests/mutation_smoke.py` 变异冒烟（可失败但永不挂起）+ 「绝不半成品交付」条款 + 可选质量四维 LLM 抽评（默认关闭，用户二次确认后启用）
- **保真度契约**：报告 MUST 含**保真率、丢失率**等关键数据（分页明细/结构对比/置信度 A/B/C/异常清单/固定复核项）——用户硬要求
- **类 Obsidian 结构化输出**（门E）：YAML frontmatter 强制元数据（文档名/版本/页码）+ 标题树 ToC + 页码锚点 `%% p.N %%`（零侵入）——用户硬要求
- **Small-to-Big 父子分块 + 人工调优**（门E）：父块=章节上下文、子块=段落粒度；review.html 可视化调整边界、补全元数据（如「同比增长 3%」补公司名）、导出修订版；**保真红线：修订 NEVER 改写正文**
- **RAG 双路召回数据供给**（门E）：权限/版本过滤字段 + BM25 文本 + 向量文本 + 父子重排候选 + 引用溯源锚点（page/bbox）；检索/重排/生成/评测运行归下游（MECE）
- **诚实边界**：加密不破解；扫描件召回率显式「不适用」不编造；图表提资产不转正文；AGPL 后端只调用不分发

## 目录结构

```
tri-pdf2md/
├── SKILL.md                       主入口（契约 + 五阶段管道 + 保真度契约 + RAG 对接契约 + 代码版权合规）
├── README.md                      本文件
├── CHANGELOG.md                   Keep a Changelog + SemVer
├── _meta.json                     平台元数据 + 档位/阈值/结构化配置
├── references/
│   ├── backends.md                后端矩阵（能力/安装/许可证/基准分/已验证命令）
│   ├── fidelity-spec.md           保真度分级规范（阈值唯一真源 + 复核项清单）
│   ├── obsidian-output-spec.md    类 Obsidian 输出规范（frontmatter schema + 锚点语法）
│   ├── chunking-spec.md           Small-to-Big 父子分块规范（策略 + 人工调优工作流）
│   ├── rag-handoff-spec.md        RAG 双路召回数据供给契约 + 评测四指标映射
│   └── version-check-spec.md      版本检查与更新规范（内部唯一真源）
├── scripts/
│   ├── preflight.py               门A：预检分级
│   ├── detect_backends.py         门B：后端探测与档位决策
│   ├── quality_check.py           门D：质量校验与报告生成
│   ├── structure_pack.py          门E：类 Obsidian 输出 + 父子分块 + 审阅页 + 锚点覆盖率
│   └── check_update.py            版本检查与更新（家族同源）
└── tests/
    └── tri-pdf2md-full-testcases.md  全场景全能力测试用例
```

## 安装

```bash
skillhub install tri-pdf2md --dir <目标目录>
# 或本地源树直接复制 tri-pdf2md/ 到 skills 识别路径
```

上游（可选增强）：`skillhub install tri-intent`——安装后「把 xxx.pdf 转成 MD」会被自动识别为 I08·pdf2md 并路由到本 skill。

## 使用

```bash
# 门A 预检（等级建议 + 风险项）
python scripts/preflight.py --pdf doc.pdf --json

# 门B 探测（选定后端 + 降级链 + 缺失安装指引）
python scripts/detect_backends.py --grade L0 --json

# 门C 版面分析转换（按 references/backends.md §三 已验证命令执行所选后端）

# 门D 校验与报告（产出 report.md：保真率/丢失率/置信度等关键数据）
python scripts/quality_check.py --pdf doc.pdf --md doc.md --backend markitdown --grade L0 --json

# 门E 结构化交付（知识库/RAG/Obsidian 用途；产出 obsidian.md + chunks.json + review.html）
python scripts/structure_pack.py --pdf doc.pdf --md doc.md \
       --backend markitdown --grade L0 --confidence A --fidelity-rate 0.98 \
       --doc-version "v2026-08-24_r2" --json
```

交付：`<同名>.md` + `assets/` + `report.md`（结构化场景追加 `<同名>.obsidian.md` + `<同名>.chunks.json` + `<同名>.review.html`），落 PDF 同目录或用户指定目录。

**门E 之后的人工调优**：浏览器打开 `<同名>.review.html` → 合并/拆分子块、补全实体元数据（例：「同比增长 3%」补「腾讯控股」）→ 标记已核 → 导出 `chunks.revised.json` → 回填下游入库。

## 测试

见 `tests/tri-pdf2md-full-testcases.md`：能力清单扫描 + 分组用例（管道/降级/保真/结构化/边界/合规/版本），基于 tri-pdf2md v1.4.4。

## 设计原则

- **编排不重造**：复用成熟后端官方 CLI/API，不自研 OCR/版面模型
- **确定性下沉**：预检/探测/校验/结构化全部脚本化输出 JSON，prompt 层不做数值推断
- **可验证分级保真**：「无损」重定义为保真率可计算、置信度可分级、复核项可执行
- **有时效、有坐标的数据源**（用户硬要求）：版本（时效）与页码/bbox（空间）锚点框架硬编码写入每个产物，全链路可控，NEVER 依赖模型自觉
- **MECE 边界**：仅认领 I08·pdf2md；PDF 其它操作归内置 pdf skill，翻译归 tri-content/tri-translate；检索执行/重排/生成/评测运行归下游 RAG 系统（本 skill 只做数据供给侧）
