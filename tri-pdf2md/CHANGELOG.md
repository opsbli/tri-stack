# Changelog

本文件记录 tri-pdf2md 的版本演进，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.4.5] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手 PDF 文档操作、RAG 检索执行、语言翻译，只做 PDF→Markdown 转换与数据供给。

## [1.4.4] - 2026-09-09

### 变更

- 文档同步：README 测试节版本引用（v1.1.0 → v1.4.4）；核实 scale_guard 已实现 zip 解压量三硬上限（总 512MB/单条目 128MB/条目 100k，anydoc limits.rs 口径），质量测试报告 §六-3 无需代码变更；版本联动四件套同步 1.4.4（依据 docs/quality-test-xx2md-20260909.md §九）

## [1.4.3] - 2026-09-09

### 变更

- 可用性：门D quality_check 必选参数补 help 文本（--pdf/--md）
- 健壮性：needsocr_check 缺 python:anydoc 绑定时报可操作安装指引（原裸 ModuleNotFoundError，识别扫描件信号的前置依赖说明）
- 维护性：postprocess 模块 docstring 归属名修正（tri-docx2md → tri-pdf2md）；scripts/__pycache__ 清理
- 依据：七维质量测试报告 docs/quality-test-xx2md-20260909.md；版本联动四件套同步 1.4.3

## [1.4.2] - 2026-09-09

### 新增

- M6：pdf_form_extract.py 无边框表格/表单词坐标聚类提取（迁移自 markitdown _pdf_converter，MIT；70 分位容差/列密度上限/表行占比下限三重防误判常量化）
  pdfplumber runner 逐页先试表单聚类，失败回退普通文本；meta.pages_with_form_tables 计数；form 路径产物门D 置信度 MUST ≤B
### 变更

- M9：preflight 新增 content_check 字段（含 .pdf %PDF- 头校验）
- 自产表经 md_table.build_md_table（M8）保证生成即合规
- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.4.2

## [1.4.1] - 2026-09-09

### 变更

- 强制执行契约铁律追加 MIT 归属条款：MIT 许可证后端的设计模式级迁移允许，MUST 在迁移文件头部保留归属声明（2026-09-09 用户裁决，迁移报告待定点①）
- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.4.1

## [1.4.0] - 2026-09-09

### 新增

- M1 降级链执行器 `scripts/convert_pipeline.py`（自包含副本，设计迁移自 markitdown _convert 循环 + FailedConversionAttempt，MIT 归属保留）：按 detect_backends 的 selected+fallback_chain 一次性代码化执行降级链，逐后端 attempts 异常聚合（类型/消息/耗时/栈尾）+ 全失败聚合诊断；空产物视为失败；单后端 300s 超时防挂死；契约升级——失败重试 MUST 调用本脚本，NEVER Agent 手工逐后端重试
- M2 输出编码兜底 `scripts/_io_safe.py`（家族同源副本，迁移自 markitdown __main__._handle_output 的 errors="replace" 模式）：全部输出脚本 print→safe_print 机械替换，Windows GBK 控制台输出含 GBK 外字符 NEVER 再崩溃；check_update.py 为家族同源文件刻意不动
- 自包含分发（2026-09-09 用户指令）：上述迁移物均为本 skill 内部独立完整副本，零跨 skill 依赖，单 skill 单独安装即完整运行
- SKILL.md：门C 失败重试条款升级为 MUST 调用 convert_pipeline.py（M1）；目录结构补登记；backends.md markitdown 条目定位细化（兼作降级链 runner）

### 变更

- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.4.0

## [1.3.0] - 2026-09-08

### 新增

- 输入规模守卫 `scripts/scale_guard.py`（P2-2，anydoc limits.rs 口径）：preflight 统一集成——ZIP 容器族检查条目数（100k）/总解压量（512MiB）/单条目（128MiB）硬上限，超限 BLOCK（ResourceLimit=完全不可能产出语义）；表格类网格槽位估算（dimension+mergeCells）超预算 4M 固定走 L1 流式路径；守卫明细写入预检 JSON `scale_guard` 字段
- 变异冒烟测试 `tests/mutation_smoke.py`（P2-3，方法论蒸馏自 anydoc tests/robustness.rs）：真实样本确定性变异（xorshift64*，字节翻转/随机截断 ×25 轮），断言「门A JSON 必产出、引擎可失败但永不挂起/信号崩溃」；`--quick` 快速冒烟
- 真实格式样本固化 `tests/samples/`（×2，源：anydoc-main fixture）并在 full-testcases 新增 T8 用例组
- 质量四维 LLM 抽评方法论（P2-1）：`references/fidelity-spec.md` §质量四维抽评（completeness/structure/formatting/cleanliness，LLM-judge 双 swap）；门D 增加可选抽评条款——默认关闭，启用属付费确认场景（MUST 用户二次确认，NEVER 自动调用）

### 变更

- SKILL.md：诚实声明追加「绝不半成品交付」MUST 条款（P2-4，对齐 anydoc「错误=完全不可能产出」）；门A 增加输入规模守卫说明；目录结构与磁盘同步（补登记 postprocess.py/dump_assets.py/needsocr_check.py 等存量脚本）

## [1.2.0] - 2026-09-08

### 新增

- anydoc（Firecrawl，MIT，v0.2.4）接入为 L0 档首选（仅文本层 PDF；anydoc-main 蒸馏报告 v1.3.0 P0-1/P0-2）：`scripts/detect_backends.py` 新增 dual 型双探测；L1/L2 DL 链不动（扫描件主路径）
- NeedsOcr 信号门 `scripts/needsocr_check.py`（P0-2）：anydoc 主链 MUST 先运行——扫描页捕获 NeedsOcrError 输出精确页码清单并自动置等级建议 L2（脚本逻辑），页码清单写入门A 风险项/report.md
- `references/backends.md`：anydoc 行（隔离边界：不做 OCR）+ 已验证命令 + 演进记录

### 变更

- 门B 措辞：六后端 → 七后端；门C 新增 anydoc 主链与 NeedsOcr 分流规则
### 新增

- 门C 后处理脚本 `scripts/postprocess.py` 新增（P1-2/P1-6，docx2md 同源移植）：锚点两遍式、动态围栏、破表检测、实体解码、围栏感知清理

## [1.1.1] - 2026-09-08

### 新增

- 家族统一五格式优雅跳过（用户指令 2026-09-08）：`scripts/preflight.py` 新增守卫——输入为 .odt/.ods/.odp/.rtf/.epub（tri-xx2md 家族统一不支持格式，含内容为此类格式的误标 zip/RTF 文件）时输出 `status=SKIP`（reason_code=unsupported_format，退出码 0，未做任何转换尝试）
- 强制执行契约新增「不支持格式优雅跳过」条目；职责边界明确五种格式为家族统一不支持范围——明确提示无法转换并跳过，NEVER 强行转换、NEVER 报错中断
## [1.1.0] - 2026-08-24

### 新增

- **门E 结构化交付**（`scripts/structure_pack.py`，用户补充要求回写）：管道由四阶段升级为**五阶段**（预检分级→后端探测→版面分析转换→质量校验→结构化交付），产出三件套——`<同名>.obsidian.md` + `<同名>.chunks.json` + `<同名>.review.html`（带文档名前缀，同目录多文档互不覆盖）
- **类 Obsidian 结构化输出**（`references/obsidian-output-spec.md` 唯一真源）：YAML frontmatter 强制元数据（文档名/版本/页码，缺一即校验失败）+ 标题树 ToC + 节级页码锚点（Obsidian 注释 `%% p.N %%`，零侵入可剥离）；页码锚点由指纹匹配算法硬编码判定，匹配失败显式标记 NEVER 模型猜页
- **Small-to-Big 父子分块**（`references/chunking-spec.md` 唯一真源）：父块=章节级（≤3000 字符）提供检索上下文，子块=段落级（≤800 字符）提供匹配粒度；表格/代码块/公式块整体 NEVER 从中切断；每块硬编码锚点（chunk_id/page/bbox/heading_path/doc_version）
- **人工调优审阅页**（review.html，自包含零依赖）：可视化调整分块边界（合并/拆分）+ 补全元数据槽位（entity/entity_aliases/source_context，如「同比增长 3%」补公司名）+ 标记已核 + 导出修订版 chunks.json；**保真红线：人工修订 NEVER 改写正文原文**，只作用于分块层
- **RAG 双路召回数据供给契约**（`references/rag-handoff-spec.md` 唯一真源）：权限与版本过滤字段（doc_id + doc_version，版本更新整体替换 NEVER 增量 patch）、BM25 路（子块纯文本）、向量路（文本 + 补全元数据拼接）、重排候选（父子关联）；**MECE 边界：检索执行/重排/生成/评测运行归下游**，本 skill 只做数据供给侧
- **LLM-as-Judge 评测四指标分工**：解析完整率（=门D 保真率）与引用可追溯率（=门E 锚点覆盖率 anchor_coverage）由本 skill 计算；召回命中率与生成忠实度归下游评测（本 skill 供给 gold chunks 与锚点数据）
- **「有时效、有坐标的数据源」总纲**（用户硬要求）：版本与页码/坐标锚点全部由框架硬编码写入产物，全链路可控，NEVER 依赖模型自觉补元数据
- 契约新增第 11/12/13 条（结构化输出强制/坐标时效锚点铁律/RAG 对接边界）；自检句增加「结构化=」字段
- 门C 升级为「版面分析转换」：开启后端版面分析能力（docling/MinerU content_list 中间产物保留复用），保留文档层级/坐标/标题树 NEVER 压平

## [1.0.0] - 2026-08-24

### 新增

- 首发版：PDF 转 Markdown 编排与质量保障 skill（tri-forge 门②生成，方案 `solution-design.md` 审计通过）
- 四阶段管道：门A 预检分级（`scripts/preflight.py`：加密/页数/文本层密度/扫描件/混合类型/等级建议）→ 门B 后端探测（`scripts/detect_backends.py`：六后端 import/CLI 双探测 + 档位决策 + 降级链）→ 门C 转换执行（指导 Agent 调后端官方命令）→ 门D 质量校验（`scripts/quality_check.py`）
- 保真度契约（用户硬要求）：report.md MUST 含保真率、丢失率等关键数据——文本召回率（字符 bigram 覆盖）/ 丢失率 / 噪声率 / 分页丢失明细 / 结构对比（标题/表格/图片）/ 置信度 A/B/C / 异常清单 / 固定复核项；扫描件召回率显式「不适用」NEVER 编造
- 四档分级策略：L0 快速（pymupdf4llm/markitdown/pdfplumber）/ L1 标准（docling/marker）/ L2 精细（MinerU）/ L3 LLM 兜底（付费须确认），全场景降级链
- 诚实边界契约：加密 PDF NEVER 破解（BLOCK）；图表提取为 assets/ 不转正文；AGPL 后端只调用不分发（代码版权合规章节）
- references 三份唯一真源：`backends.md`（后端矩阵+已验证命令）、`fidelity-spec.md`（保真度阈值）、`version-check-spec.md`（版本检查）
- 上游依赖检测三态逻辑（快照模式/引导安装/降级模式）+ tri-intent I08·pdf2md 子类一跳路由接入
- 全场景测试用例 `tests/tri-pdf2md-full-testcases.md`（管道/降级/保真/边界/合规/版本六组）
- 全管道冒烟验证通过：数字 PDF（L0→markitdown→保真率 100%/置信度 A）、扫描件（不适用/C）、加密件（BLOCK）三路径
