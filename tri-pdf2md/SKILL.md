---
name: PDF 转 Markdown
slug: tri-pdf2md
version: 1.4.5
displayName: PDF 转 Markdown
description: 专门用于 PDF 高质量转 Markdown 的编排与质量保障 skill——预检分级（加密/扫描件/复杂版面判定）、多后端探测与编排（anydoc 文本层首选 + NeedsOcr 信号分流 + pymupdf4llm/docling/marker/MinerU/markitdown/pdfplumber 降级链）、版面分析转换（保留文档层级/坐标/标题树）、质量校验与保真度分级报告（保真率/丢失率/结构对比/置信度 A/B/C）、类 Obsidian 结构化输出（YAML frontmatter 强制元数据：文档名/版本/页码）+ Small-to-Big 父子分块 + 人工调优审阅页 + RAG 双路召回数据供给契约；定位是编排与质量保障层，不自研 OCR/版面模型，复用成熟后端；支持独立安装，含上游依赖检测三态逻辑（快照模式/引导安装/降级模式）。
summary: 五阶段管道（预检分级→后端探测→版面分析转换→质量校验→结构化交付）+ 四档降级链 + 可验证分级保真契约 + 「PDF 视为有时效、有坐标的数据源」硬编码锚点——把「无损」落为保真率/丢失率可计算、置信度可分级、块级页码坐标锚点可追溯的质量报告与 RAG 语料。
tags: [tri, pdf, markdown, conversion, fidelity, quality-report, ocr-orchestration, obsidian, chunking, rag-handoff]
license: MIT
---

# PDF 转 Markdown

> 本 skill 是 tri-intent 的**下游 skill（读取快照直接执行，绝不重识别意图）**，也可完全独立运行（直接给定 PDF 路径）。执行路径：门A 预检分级 → 门B 后端探测 → 门C 版面分析转换 → 门D 质量校验与报告 → 门E 结构化交付（类 Obsidian + 父子分块），交付 `<同名>.md + assets/ + report.md`，结构化场景追加 `<同名>.obsidian.md + <同名>.chunks.json + <同名>.review.html`。
>
> **诚实声明（铁律）**：PDF 是面向打印的坐标格式，内部不含「标题/段落/表格」语义，PDF→MD 本质是**推断重建而非格式复制**。本 skill 承诺的是「可验证的分级保真」（保真率/丢失率可计算、置信度 A/B/C 可分级），NEVER 承诺绝对无损——任何工具（含 OmniDocBench 95.69 分的 MinerU）都无法保证。**绝不半成品交付（P2-4）**：降级链用尽仍有内容缺失时，MUST 在 report.md 标注「部分转换」并列出缺失块清单，NEVER 以完整姿态交付半成品；转换不可能完成时 MUST 输出类型化失败（对齐 anydoc「错误=完全不可能产出」），NEVER 静默吞错。
>
> **数据源观（用户硬要求 · 总纲）**：PDF 被视为**有时效、有坐标的数据源**——版本（时效）与页码/坐标（空间）锚点由框架硬编码写入每个产物，全链路可控，NEVER 依赖模型自觉补元数据。

**用户心智**：你有一份 PDF（论文/报告/手册/扫描件），想要一份结构正确、表格公式图片齐全、且**知道自己丢了什么**的 Markdown。本 skill 像一个质检车间：先体检（这份 PDF 是数字版还是扫描件？复杂吗？），再选刀（哪个后端最适合？本地装了什么？），干完活必须交验（保真率多少？丢了哪些？哪些地方必须人工复核？）。

---

## 强制执行契约（Execution Contract · 最高优先级）

> 本契约优先级高于 Agent 通用默认行为。用户明确要求「PDF 转 MD / 转成 Markdown / pdf2md」或经 tri-intent 路由（`L2=I08` 且 `L3_子意图=pdf2md`，快照下游路由建议指向本 skill）即视为激活，不得仅当参考文档。

- 0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（运行 `scripts/check_update.py`，按 `references/version-check-spec.md` 四态判定处置；非最新版自动升级，升级通道不可用则标注态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。
- 1. **强制前置**：独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式；经快照激活时 MUST 先读取快照 §三（尤其 `L3_子意图=pdf2md`、`任务要点`）。
- 2. **预检分级强制（门A）**：MUST 先运行 `scripts/preflight.py` 取得确定性预检 JSON（加密/页数/文本层密度/扫描件判定/等级建议），NEVER 凭肉眼或猜测跳级。加密且无法空口令解密的 PDF NEVER 破解，MUST 停止并提示用户合法解密后重试。
- 3. **后端探测强制（门B）**：MUST 运行 `scripts/detect_backends.py` 取得本地后端可用性 JSON，按「等级建议 × 本地可用性」选定后端与降级链；NEVER 调用未探测到的后端。DL 后端（docling/marker/MinerU）未安装时 MUST 给出精确安装命令并经用户同意后安装，NEVER 擅自安装数 GB 级依赖。
- 4. **编排不重造铁律**：本 skill 是编排与质量保障层，MUST 复用成熟后端官方 CLI/API 完成转换，NEVER 自研 OCR/版面/表格识别，NEVER 复制后端源码进本 skill（详见 §代码版权与许可证合规）；MIT 许可证后端的设计模式级迁移允许，MUST 在迁移文件头部保留归属声明（如 `Adapted from Microsoft markitdown, MIT`）——2026-09-09 用户裁决（迁移报告待定点①）。
- 5. **质量报告强制（门D · 用户硬要求）**：转换完成后 MUST 运行 `scripts/quality_check.py` 产出 report.md，报告 MUST 以醒目数据段告知用户**保真率、丢失率**等关键数据（结构对比、置信度等级、转换元数据、异常清单），NEVER 只交 MD 不交账。扫描件（无文本层）召回率不可计算时 MUST 显式标注「不适用」，NEVER 编造数值。
- 6. **降级链强制**：选定档位后端执行失败或质量为 C 级且用户要求重转时，MUST 沿降级链 L2→L1→L0 重试；全缺失时 MUST 输出安装指引并停在预检报告态，NEVER 空手交付。
- 7. **L3 LLM 兜底须确认**：涉及付费 LLM 视觉 API 或商业 API（Doc2X/TextIn/LlamaParse 等）时，MUST 先向用户说明成本与数据外发风险并取得确认，NEVER 未经确认调用。
- 8. **图表处置**：图表 NEVER 试图转成 MD 正文，MUST 提取为 `assets/` 图片资产 + 保留题注引用；转换后 MUST 校验 MD 内图片引用与资产文件一一对应。
- 9. **复核项永不消失**：report.md MUST 固定列出复核项清单（跨页表格/图表题注/脚注归属/多栏阅读顺序/中文字体嵌入缺失），NEVER 因置信度为 A 而省略。
- 10. **自检句**：作答前 MUST 声明「本次意图=I08（L3=pdf2md），已读取快照=<是/否>，预检等级=<L0/L1/L2>，选定后端=<slug>，保真度=<A/B/C/待检>，结构化=<未启用/Obsidian+分块>」；与预检/探测结果冲突时 MUST 停止并纠正。
- 11. **结构化输出强制（门E）**：用户要求「知识库/RAG 语料/Obsidian 笔记/带元数据/父子分块」或显式 `--obsidian` 时 MUST 运行 `scripts/structure_pack.py` 产出三件套——类 Obsidian MD（YAML frontmatter 强制元数据：文档名/版本/页码）+ `<同名>.chunks.json`（Small-to-Big 父子分块）+ `<同名>.review.html`（人工调优审阅页）；NEVER 输出裸 MD 即宣称「结构化完成」。
- 12. **坐标与时效锚点铁律（用户硬要求）**：每个子块 MUST 带页码锚点与近似坐标（bbox），文档级 MUST 带版本元数据（缺省取 PDF 修改时间 + 页数指纹，可 `--doc-version` 覆盖）——PDF 是**有时效、有坐标的数据源**，锚点由框架硬编码写入，NEVER 依赖模型自觉补全。
- 13. **RAG 对接边界（MECE）**：本 skill 供给双路召回所需的全部数据结构（父子分块、BM25 文本、向量文本、权限/版本过滤字段、重排候选），但**检索执行（ES/向量库）、重排、生成归下游系统**——评测四指标中本 skill 负责**解析完整率**与**引用可追溯率**的数据供给，召回命中率与生成忠实度归下游（映射详见 `references/rag-handoff-spec.md`，grep 模式：`召回|评测`）。
- 14. **不支持格式优雅跳过（家族统一 · 用户指令 2026-09-08）**：输入为 .odt/.ods/.odp/.rtf/.epub（tri-xx2md 家族统一不支持格式，含内容为此类格式的误标 zip/RTF 文件）时，门A preflight MUST 输出 `status=SKIP`（reason_code=unsupported_format，退出码 0），本 skill MUST 明确告知用户「无法转换」并列出支持格式与替代建议后跳过结束，NEVER 尝试强行转换，NEVER 报错中断。

---

## 触发时机

- **主触发（独立运行）**：用户明确要求「把 xxx.pdf 转成 Markdown」「PDF 转 MD」「无损转 PDF」且对象是 PDF 文件；含「转成知识库/RAG 语料/Obsidian 笔记」语义时同时激活门E 结构化交付。
- **次触发（tri-intent 接入）**：上游 tri-intent 产出快照，`L2=I08 翻译转换` 且 `L3_子意图=pdf2md`，`下游路由建议=tri-pdf2md`——读取快照 §三 后按本契约执行。
- 任一触发成立即激活。PDF 的其它操作（合并/拆分/表单/水印/提取附件）不归本 skill，见 §职责边界。

---

## 上游依赖检测（独立使用时 · 三态）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟）且下游路由建议指向本 skill | 读取快照 §三（任务要点/输入文件/输出期望），按四阶段管道执行（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | MUST 提示用户「本次请求尚未经意图识别」，引导先经 tri-intent 产出快照；NEVER 按空上下文静默执行 |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户明确拒绝安装 | 从用户请求自构造等价输入（意图判定默认 I08/L3=pdf2md + PDF 路径 + 输出期望），声明降级模式后按四阶段管道执行，生成的报告标注「未经意图识别」 |

**模式 B 提示语**：

> 本 skill 依赖 tri-intent 进行意图识别与输入校验。当前未检测到 tri-intent。
> 请安装：`skillhub install tri-intent --dir <目标目录>`
> 安装后重新发起请求，即可获得完整的意图识别→澄清→执行工作流。

**模式 C 降级声明**：

> 用户明确拒绝安装后，从用户请求自构造等价输入（意图判定 I08/L3=pdf2md + PDF 路径 + 输出期望），声明「当前为降级模式，意图识别精度低于完整工作流，转换质量不受影响但路由归属需人工复核」。

> **对称双向检测**：本 skill 检上游 tri-intent；tri-intent 亦在路由映射表登记本 skill 为 I08·pdf2md 子类下游（一跳覆写），未安装时会提示安装。任一端缺失都被发现。

---

## 输入契约

| 来源 | 字段 | 用途 |
|------|------|------|
| 快照 §三（模式 A） | `任务要点` / `一句话复述` | 提取 PDF 路径、输出目录、质量期望（是否要求公式/表格精细/结构化知识库用途） |
| 用户直调（模式 C） | PDF 文件路径 | 转换对象；MUST 存在且可读 |
| 用户直调（可选） | 输出目录 | 默认 `.tribro/pdf2md/<命名>/`；assets/ 与 report.md 同级 |
| 用户直调（可选） | 档位偏好 `--grade` | 强制指定 L0/L1/L2；缺省由门A 自动建议 |
| 用户直调（可选） | 结构化开关 `--obsidian` | 启用门E（类 Obsidian + 父子分块 + 审阅页）；知识库/RAG 用途默认建议启用 |
| 用户直调（可选） | 文档版本标识 `--doc-version` | 时效元数据（缺省：PDF 修改时间 + 页数指纹自动生成） |
| 用户直调（可选） | 分块参数 `--parent-granularity` / `--child-max-chars` | 门E 分块粒度（缺省 section / 800） |
| `references/backends.md` | 后端矩阵 | 门B/门C 选择与命令参考（grep 模式：后端名） |
| `references/fidelity-spec.md` | 保真度阈值 | 门D 分级判定（grep 模式：置信度） |
| `references/obsidian-output-spec.md` | 类 Obsidian 输出规范 | 门E 输出格式（frontmatter schema/锚点语法，grep 模式：`frontmatter|锚点`） |
| `references/chunking-spec.md` | 父子分块规范 | 门E 分块策略与人工调优工作流（grep 模式：`父子|调优`） |
| `references/rag-handoff-spec.md` | RAG 对接契约 | 双路召回数据供给与评测四指标映射（grep 模式：`召回|评测`） |

> 输入 PDF 为目录时 NEVER 批量静默转换，MUST 先列清单与用户确认范围。

---

## 职责边界

- **本 skill 负责**：PDF→MD 的预检分级、后端探测与编排、版面分析转换指导（保留层级/坐标/标题树）、质量校验与保真度分级报告、图片资产提取与引用校验、类 Obsidian 结构化输出、Small-to-Big 父子分块与人工调优审阅页、RAG 双路召回数据供给（数据结构层）。
- **不负责**：PDF 合并/拆分/表单填写/水印/加密破解（归环境内置 pdf skill）；语言翻译（归 tri-content/tri-translate）；MD 之外的格式转换（归 tri-content）；意图识别（归 tri-intent）；**检索执行（ES/向量库建设、BM25/向量索引）、重排模型、答案生成、LLM-as-Judge 评测运行（归下游 RAG 系统——本 skill 只供给其所需数据结构与锚点）**。
- **与 tri-content（I08 默认下游）的边界**：I08 的语言翻译与其它格式转换仍路由 tri-content；仅「PDF→MD」语义命中 `L3_子意图=pdf2md` 时一跳覆写到本 skill。一个 L2（I08）对应一个一跳下游，仅由 L3 区分——与 I06 article→tri-article 同构。
- **与 tri-translate 的边界**：无重叠。tri-translate 是语言翻译方法论（横向）；本 skill 是格式转换（PDF→MD）。
- **与环境内置 pdf skill 的边界**：内置 pdf skill 做 PDF 文档操作；本 skill 只做「PDF→Markdown 格式转换 + 质量报告」这一件事。
- **不支持格式（家族统一）**：.odt/.ods/.odp/.rtf/.epub 五种格式为 tri-xx2md 家族统一不支持范围，preflight 命中即明确提示无法转换并跳过（status=SKIP），NEVER 强行处理，NEVER 报错中断。
- **不触发场景（Not-Trigger）**：本 skill 不接手「PDF 合并/拆分/表单填写/水印/加密破解」（归环境内置 pdf skill）；不接手「RAG 检索执行/嵌入/重排/答案生成/评测」（归下游 RAG 系统，本 skill 只供给数据结构与锚点）；不接手「语言翻译」（归 tri-content/tri-translate）；不接手「意图识别」（归 tri-intent）。

---

## 五阶段管道方法论（核心能力 · 可扩展）

> 「先体检、再选刀、干完活、必须交验、按用途打包」。五阶段中门A/门B/门D/门E 是确定性脚本（约束：算法下沉），门C 由本 skill 指导 Agent 调用后端官方命令。

### 门A · 预检分级（scripts/preflight.py）

```bash
python scripts/preflight.py --pdf <路径> [--sample-pages 12] --json
```

> **输入规模守卫（P2-2）**：preflight 内置 `scripts/scale_guard.py`（anydoc limits.rs 口径：条目数 100k / 总解压 512MiB / 单条目 128MiB，刻意不可配置）。硬上限超限 → BLOCK（ResourceLimit=完全不可能产出语义）。守卫明细见预检 JSON `scale_guard` 字段。

> **内容真身二次校验（M9）**：preflight 输出含 `content_check` 字段（`scripts/sniffer.py`：.pdf 验 `%PDF-` 头）。`match=false` → BLOCK「扩展名与内容不符」。

检测项：加密与空口令可解性 / 页数 / 抽样页文本层密度（平均字符/页）/ 扫描件判定 / 混合类型（部分页有文本层）/ 表格与图片信号（pdfplumber）。输出等级建议：

| 判定 | 等级建议 |
|---|---|
| 加密且空口令不可解 | BLOCK——提示合法解密后重试，NEVER 破解 |
| 全部/绝大多数抽样页无文本层（扫描件） | L2（需 OCR 精细档） |
| 有文本层 + 检出表格/多栏/大量图片（复杂版面） | L1（标准档） |
| 有文本层 + 版面简单（纯文字为主） | L0（快速档） |
| 部分页有文本层部分没有（混合） | L1 起步，报告标注混合风险 |

### 门B · 后端探测与选择（scripts/detect_backends.py）

```bash
python scripts/detect_backends.py --grade <L0|L1|L2> --json
```

探测七后端本地可用性（import 与 CLI 双探测，anydoc 为 dual 型双通道首选、仅入 L0）：`anydoc / pymupdf4llm / docling / marker / mineru / markitdown / pdfplumber`。决策规则：等级建议 × 本地可用性 → 选定后端 + 降级链（探测 JSON 决定，NEVER Agent 另选）；全缺失 → 输出安装指引并停在预检报告态。

**四档分级策略**（完整矩阵含安装命令/许可证/基准分见 `references/backends.md`，grep 模式：`L0|L1|L2|L3`）：

| 档位 | 适用 | 首选 | 降级 | 预期质量 |
|---|---|---|---|---|
| L0 快速 | 数字 PDF、简单版式、大批量 | pymupdf4llm | markitdown → pdfplumber | 文本优，表格/公式有限 |
| L1 标准 | 多栏、表格、少量公式 | docling | marker 2 → L0 链 | 表格 TEDS 80+ |
| L2 精细 | 扫描件、学术文献、复杂版面 | MinerU | docling → marker → L0 链 | 文本 98+/公式 CDM 97/表格 TEDS 93 |
| L3 兜底 | 后端全失败或用户极致要求 | LLM 视觉 API | 商业 API（Doc2X/TextIn/LlamaParse） | 不稳定且付费，须用户确认 |

### 门C · 版面分析转换（本 skill 指导，后端干活）

> 用户硬要求：使用 PyMuPDF/MinerU 等后端进行**版面分析**，保留文档层级、坐标、标题树——转换不是「抽文本」而是「重建结构」。

1. 按选定后端的官方命令执行（命令模板见 `references/backends.md` §各后端已验证命令，grep 模式：`命令`）；优先开启后端的版面分析能力（docling `--export-figures`、MinerU 输出 `*_content_list.json` 中间产物、pymupdf4llm `show_progress`）。**anydoc 主链（L0 文本层 PDF）**：MUST 先运行 `python scripts/needsocr_check.py --pdf <file> --json`（P0-2 信号门）——`needs_ocr=true` 时页码清单 MUST 写入报告风险项且等级建议自动置 L2（脚本逻辑），MUST 改走 L2 DL 链，NEVER 对扫描件强行走 anydoc；`needs_ocr=false` 时 anydoc 直转 GFM。
2. 产出 `<同名>.md` + `assets/` 图片资产；后端产出结构化中间产物（content_list/标题树）时 MUST 保留供门E 复用，NEVER 丢弃。
3. 后处理：清理页眉页脚重复、统一图片相对路径、校验 MD 语法（表格列对齐/代码块闭合）、保留标题层级树（NEVER 压平为纯段落）。
4. 失败或超时 → **MUST 调用 `python scripts/convert_pipeline.py --doc <路径> --md <同名>.md --chain "<selected>,<fallback_chain>" --json` 一次性代码化执行降级链（M1，NEVER Agent 手工逐后端重试）**；输出 JSON 的 `backend_used`/`attempts`（逐后端异常聚合）MUST 写入门D 报告「降级轨迹」字段；退出码 3（全后端失败）时向用户输出聚合诊断并停止。
5. **无边框表格提取（M6）**：pdfplumber runner 逐页先经 `scripts/pdf_form_extract.py` 词坐标聚类（70 分位 gap 容差 + 列密度上限 + 表行占比下限三重防误判，Adapted from Microsoft markitdown, MIT），判为表单页产出对齐 MD 表，否则回退普通文本；`meta.pages_with_form_tables` 计数 MUST 写入门D 报告，**form 路径产物置信度强制 ≤B**（启发式有误判可能，NEVER 直接给 A）；该脚本也可由 Agent 视 NeedsOcr/表格信号单独调用（`--pdf <路径> --md <输出> --json`）。

### 门D · 质量校验与报告（scripts/quality_check.py · 用户硬要求）

```bash
python scripts/quality_check.py --pdf <路径> --md <路径> [--report-dir <目录>] --json
```

**校验指标**（全部确定性计算，NEVER 目测）：

| 指标 | 定义 | 算法 |
|---|---|---|
| **保真率（文本召回率）** | PDF 文本层内容被 MD 覆盖的比例 | 归一化后字符 bigram 集合覆盖率（中文/英文自适应） |
| **丢失率** | 1 − 保真率；附分页丢失明细 | 同上，按页统计丢失集中页 |
| 噪声率 | MD 有而 PDF 无的比例（OCR 噪声/幻觉信号） | 反向 bigram 覆盖率 |
| 结构对比 | 标题/表格/图片：PDF 侧计数 vs MD 侧计数 | pdfplumber 计数 vs MD 语法计数 |
| 异常清单 | 乱码（U+FFFD）/空章节/MD 截断 | 正则 + 长度启发式 |

**质量四维 LLM 抽评（可选 · 默认关闭 · P2-1）**：completeness / structure / formatting / cleanliness 四维盲评（LLM-judge 双 swap），方法论唯一真源 `references/fidelity-spec.md` §质量四维抽评。启用属付费确认场景（总则②）：MUST 用户二次确认，NEVER 默认或自动调用；基准引用一律标注来源。默认仅交付确定性指标。

**置信度分级**（阈值唯一真源 `references/fidelity-spec.md`，grep 模式：`置信度`）：

| 置信度 | 判定 | 处置 |
|---|---|---|
| **A 直接可用** | 保真率 ≥95% 且结构计数吻合 | 交付，报告标注 |
| **B 抽查复核** | 保真率 85–95% 或结构部分缺失 | 交付 + 列出复核项 |
| **C 强制人工复核** | 保真率 <85%，或扫描件 OCR，或有乱码/截断 | 交付 + 醒目警示 + 建议升级档位重转 |

**report.md 关键数据段（固定结构，NEVER 省略）**：保真率、丢失率、分页丢失明细、结构对比表、置信度等级与原因、转换元数据（后端/档位/页数/耗时/资产数/降级轨迹）、异常清单、固定复核项清单。扫描件无文本层时保真率标注「不适用（无文本层）」并降为 C 级口径。

### 门E · 结构化交付（scripts/structure_pack.py · 类 Obsidian + 父子分块 · 用户硬要求）

```bash
python scripts/structure_pack.py --pdf <路径> --md <转换产物> [--out-dir <目录>]
       [--doc-version <版本标识>] [--parent-granularity section|page] [--child-max-chars 800] --json
```

**触发**：用户要求知识库/RAG 语料/Obsidian 笔记/带元数据/父子分块，或显式 `--obsidian`。产出三件套：

| 产物 | 内容 | 硬编码锚点 |
|---|---|---|
| `<同名>.obsidian.md` | YAML frontmatter（title/source/doc_version/pages/converted_at/backend/grade/confidence）+ 标题树 ToC + 正文 | 每节尾页码锚点（Obsidian 注释 `%% p.N %%`） |
| `<同名>.chunks.json` | Small-to-Big 父子分块：父块=章节/页，子块=段落/语义单元 | 每块 chunk_id/page/bbox/heading_path/doc_version |
| `<同名>.review.html` | 人工调优审阅页（自包含，浏览器打开） | 边界调整（合并/拆分）+ 元数据补全 + 导出修订版 |

**Small-to-Big 分块策略**（细则唯一真源 `references/chunking-spec.md`，grep 模式：`父子|调优`）：父块提供检索上下文（章节级 1500–3000 字符），子块提供匹配粒度（段落级 ≤800 字符）；检索命中子块、返回父块上下文。每个子块带**可人工补全的元数据槽位**（entity/entity_aliases/source_context）——如「同比增长 3%」补公司名后写入 chunk 元数据，NEVER 改写原文正文。

**人工调优工作流**：浏览器打开 `<同名>.review.html` → 调整分块边界（合并/拆分）→ 补全元数据槽位 → 导出修订版 `chunks.revised.json` → 回填入库。人工修订 NEVER 直接改正文（保真红线），只作用于分块层。

### RAG 对接与评测闭环（数据供给契约 · 用户硬要求）

> 关键结论（用户硬要求）：**PDF 是有时效、有坐标的数据源，全链路靠框架硬编码实现可控，而非依赖模型自觉。** 本 skill 是这条链路的「数据供给侧」，检索与生成是「消费侧」，边界如下：

| 环节 | 归属 | 本 skill 供给 |
|---|---|---|
| 权限与版本过滤 | 下游（关系库/ES） | 每块带 `doc_version` + 文档级 `doc_id` 字段，支持时效过滤（新版本 PDF 重新转换 → 新版本号 → 下游按版本淘汰旧块） |
| BM25 召回 | 下游 | 子块纯文本字段（已去 MD 语法噪声） |
| 向量召回 | 下游 | 子块文本 + 可选补全元数据（entity 等注入 embedding 文本） |
| 重排精选 | 下游（重排模型） | 父子块关联结构（子块命中 → 父块上下文入重排候选） |
| LLM-as-Judge 四指标 | 分工 | **解析完整率** = 门D 保真率（本 skill 计算）；**引用可追溯率** = 块级锚点覆盖率 anchor_coverage（门E 计算：带页码+bbox 的子块占比）；**召回命中率、生成忠实度** = 下游评测（本 skill 供给评测所需的 gold chunks 与锚点数据） |

细则唯一真源：`references/rag-handoff-spec.md`（grep 模式：`召回|评测|权限`）。

### 可扩展性

1. **新增后端**：在 `references/backends.md` 矩阵追加一行 + `detect_backends.py` 的 `BACKENDS` 表追加探测项，零改流程。
2. **调整档位阈值**：只改 `preflight.py` 顶部常量（扫描件字符阈值等）。
3. **调整保真度阈值**：只改 `references/fidelity-spec.md`（单一事实源）。
4. **新增质量指标**：在 `quality_check.py` 追加计算函数 + 报告模板加一行。
5. **调整分块策略**：只改 `references/chunking-spec.md`（单一事实源）与 `structure_pack.py` 顶部常量；人工调优产物（修订版 chunks.json）可回灌再入库，不触发重转换。

---

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：本 skill 内部 `references/version-check-spec.md`（不依赖任何外部上游 skill）。**可执行实现**：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

**执行方式（MUST）**：运行 `python scripts/check_update.py --slug tri-pdf2md --json`，解析 `state` 字段——`A`/`B`/`C`/`D` 一律放行并标注口径，`BLOCK`（退出码 ≥20）绝对禁止执行并按 `block_code` 输出恢复指引。退出码 `<20` 放行；脚本自身异常兜底降级放行，NEVER 因版本门故障阻断启动。四态判定、升级流程、节流缓存细则均在 `references/version-check-spec.md`，本章节 NEVER 内联。

---

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 门A → 门B → 门C → 门D → 门E（按需）→ 交付。版本检查未通过前 NEVER 进入以下任一步骤。

1. **入口分流**：声明自检句 → 模式 A 读快照 §三 / 模式 C 自构造输入；提取 PDF 路径、输出期望与结构化开关（知识库/RAG 用途 → 门E 启用）。
2. **门A 预检**：运行 `preflight.py`；BLOCK（加密）则停止并提示；取得等级建议与风险项。
3. **门B 探测**：运行 `detect_backends.py`；向用户报告「等级建议 + 本地可用后端 + 选定方案」；DL 后端缺失且需要 L1/L2 时给出安装命令，经同意后安装并复测。
4. **门C 版面分析转换**：按选定后端官方命令执行（开启版面分析能力）→ 产出 MD + assets + 结构化中间产物 → 后处理（页眉页脚/图片路径/MD 语法/保留标题树）→ 失败经 scripts/convert_pipeline.py 代码化执行降级链（M1）。
5. **门D 校验**：运行 `quality_check.py` → 产出 report.md（含保真率/丢失率等关键数据段）；C 级时向用户醒目警示并给出升级重转选项。
6. **门E 结构化交付（按需）**：知识库/RAG/Obsidian 用途时运行 `structure_pack.py` → 产出 `<同名>.obsidian.md + <同名>.chunks.json + <同名>.review.html`；向用户报告锚点覆盖率（anchor_coverage）与人工调优建议。
7. **交付**：`<同名>.md + assets/ + report.md`（+ 结构化三件套）落输出目录（默认 `.tribro/pdf2md/<命名>/`）；回显产物路径与置信度结论。
8. **链路落盘**：本次转换的过程数据（预检 JSON/探测 JSON/质量 JSON/结构化 JSON）落 `.tribro/pdf2md/<命名>/` 供追溯。

---

## 交付产物

| 产物 | 文件名 | 内容 | 审批门 |
|------|--------|------|--------|
| Markdown 正文 | `<同名>.md` | 转换结果（含图片相对引用、保留标题树） | 门D 校验后 |
| 图片资产 | `assets/` | 提取的图表图片 + 题注对应 | 与正文同步 |
| 质量报告 | `report.md` | 保真率/丢失率/结构对比/置信度/复核项/异常清单 | 门D（MUST，NEVER 省略） |
| 类 Obsidian 笔记 | `<同名>.obsidian.md` | YAML frontmatter 强制元数据（文档名/版本/页码）+ 标题树 ToC + 页码锚点正文 | 门E（结构化场景 MUST） |
| 父子分块语料 | `<同名>.chunks.json` | Small-to-Big 分块 + 块级锚点（page/bbox/heading_path/doc_version）+ 元数据槽位 | 门E（结构化场景 MUST） |
| 人工调优审阅页 | `<同名>.review.html` | 分块边界调整 + 元数据补全 + 修订导出 | 门E（结构化场景 MUST） |
| 过程数据 | `.tribro/pdf2md/<命名>/*.json` | 预检/探测/质量/结构化四份 JSON（追溯用） | 自动 |

---

## 质量标准

| 维度 | 标准 | 验证方式 |
|------|------|----------|
| 报告完整性 | report.md 含保真率/丢失率/结构对比/置信度/元数据/异常/复核项全段 | `quality_check.py` 输出核对 |
| 保真度诚实 | 召回率不可计算时显式「不适用」，NEVER 编造数值 | 报告字段校验 |
| 图片引用一致 | MD 图片引用与 assets/ 文件一一对应 | 计数比对 |
| 降级完整 | 后端失败必留降级轨迹，全缺失停在预检态 | 过程 JSON 核对 |
| 结构保留 | 标题层级非空、表格语法闭合、代码块闭合 | MD 语法检查 |
| 结构化锚点完整（门E） | frontmatter 含文档名/版本/页数；每个子块带 page/bbox/heading_path；anchor_coverage 如实报告 | `structure_pack.py` 输出核对 |
| 调优不改正文 | 人工修订只作用于分块层与元数据槽位，NEVER 改写正文文本 | 修订版与原版 diff 正文段 |
| 边界恪守 | 不破解加密、不擅自装重依赖、不擅自调付费 API | 流程审查 |
| 版本联动 | SKILL.md / CHANGELOG / tests 三处版本一致 | 发布前核对 |

---

## 落盘规则

- 本 skill 为 tri-forge 生成物，包落盘于 `.tribro/skills/tri-pdf2md/`（安装后经 junction 同步平台）。
- 用户成果物（`<同名>.md + assets/ + report.md`）落 `.tribro/pdf2md/<命名>/`——全部产物统一落盘至 `.tribro/`。
- 过程数据（预检/探测/质量 JSON）落 `.tribro/pdf2md/<命名>/`（命名沿用家族规范 `PDF2MD_<日期>_<时间>_<会话ID>`）。
- 全程不生成 LICENSE / .gitignore。

---

## 目录结构

```
tri-pdf2md/
├── SKILL.md                       主入口：契约 + 五阶段管道 + 保真度契约 + RAG 对接契约 + 代码版权合规
├── README.md                      特性/目录/安装/使用/测试/设计原则
├── CHANGELOG.md                   Keep a Changelog + SemVer
├── _meta.json                     平台元数据
├── references/
│   ├── backends.md                后端矩阵（能力/安装/许可证/基准分/已验证命令 · grep 索引）
│   ├── fidelity-spec.md           保真度分级规范（阈值唯一真源 + 复核项清单）
│   ├── obsidian-output-spec.md    类 Obsidian 输出规范（frontmatter schema + 锚点语法 · 唯一真源）
│   ├── chunking-spec.md           Small-to-Big 父子分块规范（策略 + 人工调优工作流 · 唯一真源）
│   ├── rag-handoff-spec.md        RAG 双路召回数据供给契约 + 评测四指标映射（唯一真源）
│   └── version-check-spec.md      版本检查与更新规范（内部唯一真源）
├── scripts/
│   ├── preflight.py               门A：预检分级（加密/文本层/扫描件/等级建议 + 输入规模守卫）
│   ├── detect_backends.py         门B：七后端探测与档位决策（anydoc L0 首选 + NeedsOcr 分流 + 降级链）
│   ├── postprocess.py             门C：转换后处理（两遍锚点保护/实体解码/围栏感知清理）
│   ├── convert_pipeline.py        门C：降级链执行器（M1：逐后端 attempts 异常聚合 + 聚合诊断 + meta 钩子，自包含副本）
│   ├── pdf_form_extract.py        M6：无边框表格/表单词坐标聚类提取（Adapted from Microsoft markitdown, MIT）
│   ├── md_table.py                M8：自产表转义（竖线转义/换行折空格/列对齐，家族同源副本）
│   ├── sniffer.py                 M9：内容真身二次校验 + charset 嗅探（家族同源副本）
│   ├── _io_safe.py                输出编码兜底（M2：GBK 控制台 safe_print，家族同源副本）
│   ├── needsocr_check.py          门C：NeedsOcr 信号解析 → 扫描页自动置 L2 DL 链
│   ├── quality_check.py           门D：保真率/丢失率/结构对比/异常/报告生成
│   ├── structure_pack.py          门E：类 Obsidian 输出 + 父子分块 + 审阅页 + 锚点覆盖率
│   ├── scale_guard.py             门A 输入规模守卫（anydoc limits.rs 口径 · P2-2）
│   └── check_update.py            版本检查与更新（家族同源）
└── tests/
    ├── tri-pdf2md-full-testcases.md  全场景全能力测试用例（审计版）
    ├── mutation_smoke.py          变异冒烟测试（确定性变异 × N 轮 · P2-3）
    └── samples/                   真实格式样本 ×2（anydoc fixture 固化）
```

### 运行时落盘结构（`.tribro/pdf2md/`）

```
.tribro/pdf2md/<命名>/
├── preflight.json     门A 预检输出（等级建议 + 风险项）
├── backends.json      门B 探测输出（可用后端 + 降级链）
├── quality.json       门D 质量输出（指标 + 置信度）
└── structure.json     门E 结构化输出（分块统计 + 锚点覆盖率 + 评测供给数据）
```

---

## 进化契约

> 本 skill 生成物自带进化契约（compliance #23）——如何接收反馈、沉淀经验、自我修订：

- **反馈接收点**：用户对 report.md 复核项的回填与投诉（「这页表格丢了」「这个公式错了」）写入 `.tribro/pdf2md/feedback/`；每次 C 级报告自动视为一条改进信号；review.html 导出的修订版 chunks.json（人工调优结果）亦为反馈输入。
- **经验沉淀位**：后端版本漂移（CLI 参数变更）、新后端出现、基准分显著变化（OmniDocBench 等）沉淀入 `.tribro/pdf2md/lessons.md`；规范修订回写 `references/backends.md` 与 `references/fidelity-spec.md`；分块调优经验（人工边界调整高频段落类型）回写 `references/chunking-spec.md`。
- **自我修订触发条件**：① 同类 PDF 连续 ≥3 次 C 级 → 修订档位判定阈值或首选后端；② 后端基准分排名显著变化 → 修订 `references/backends.md` 矩阵；③ 新高质量开源后端出现（社区 Stars/基准双高）→ 评估纳入矩阵并更新 `detect_backends.py` 的 `BACKENDS` 表；④ 人工调优对某类段落边界修订率 >30% → 修订 `chunking-spec.md` 分块参数缺省值。
- **质量闭环归属**：本 skill 负责「转换 + 度量 + 报告 + 结构化供给」，复核与采信由用户执行；report.md 的复核项回填与 chunks.json 的人工修订是下一次转换阈值/分块参数调优的输入。

---

## 代码版权与许可证合规（硬红线）

- 本 skill 只**编排调用**后端官方 CLI / Python API，NEVER 复制、改写或内嵌任何后端源码。
- 后端许可证口径（AGPL-3.0：pymupdf4llm、MinerU 3.3.0 前旧版；MIT：docling/pdfplumber；Apache-2.0：marker、MinerU 3.3.0+ OSL）见 `references/backends.md` §许可证——AGPL 后端以「外部依赖调用、不分发其代码」方式使用；用户对许可证敏感时引导改用 MIT/Apache 后端（markitdown/pdfplumber/docling/marker）。
- 报告与文档引用基准数据 MUST 标注来源与版本（如 OmniDocBench v1.5/v1.6），NEVER 混用口径。
