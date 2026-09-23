# Changelog

本文件记录 tri-docx2md 的版本演进，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.4.5] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手 Word 文档操作、语言翻译、MD 之外格式转换与 PDF→MD，只做 Word→Markdown 转换。

## [1.4.4] - 2026-09-09

### 修复

- convert_pipeline `_repair_first` 成功路径 mkdtemp 临时目录不回收（质量测试轮 §六-4）——改为 `@contextmanager` 确定性清理（成功/失败/异常都清，best-effort），实证 mammoth(+repair) 链转换后 `%TEMP%/tri_docx2md_repair_*` 零增量
### 变更

- README 测试节版本引用同步（v1.0.0 → v1.4.4）；版本联动四件套同步 1.4.4（依据 docs/quality-test-xx2md-20260909.md §九）

## [1.4.3] - 2026-09-09

### 变更

- 可用性：门D quality_check 必选参数补 help 文本（--doc/--md）
- 健壮性：dump_assets 缺 python:anydoc 绑定时报可操作安装指引（原裸 ModuleNotFoundError）
- 维护性：scripts/__pycache__ 清理（发布卫生）
- 依据：七维质量测试报告 docs/quality-test-xx2md-20260909.md；版本联动四件套同步 1.4.3

## [1.4.2] - 2026-09-09

### 变更

- 门A 接入 M9 内容真身二次校验：preflight 新增 content_check 字段（扩展名与内容不符 → BLOCK），sniffer.py 同源副本落盘
- 自产表工具 md_table.py 同源副本落盘（供未来自产表生成处取用）
- convert_pipeline 执行核心新增 meta 钩子（M4/M9：PipelineResult.meta + _runner_meta，本 skill 暂无附加项）
- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.4.2

## [1.4.1] - 2026-09-09

### 变更

- 强制执行契约铁律追加 MIT 归属条款：MIT 许可证后端的设计模式级迁移允许，MUST 在迁移文件头部保留归属声明（2026-09-09 用户裁决，迁移报告待定点①）
- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.4.1

## [1.4.0] - 2026-09-09

### 新增

- M1 降级链执行器 `scripts/convert_pipeline.py`（自包含副本，设计迁移自 markitdown _convert 循环 + FailedConversionAttempt，MIT 归属保留）：按 detect_backends 的 selected+fallback_chain 一次性代码化执行降级链，逐后端 attempts 异常聚合（类型/消息/耗时/栈尾）+ 全失败聚合诊断；空产物视为失败；单后端 300s 超时防挂死；契约升级——失败重试 MUST 调用本脚本，NEVER Agent 手工逐后端重试
- M2 输出编码兜底 `scripts/_io_safe.py`（家族同源副本，迁移自 markitdown __main__._handle_output 的 errors="replace" 模式）：全部输出脚本 print→safe_print 机械替换，Windows GBK 控制台输出含 GBK 外字符 NEVER 再崩溃；check_update.py 为家族同源文件刻意不动
- M3 docx 预处理修复器 `scripts/repair_docx.py`（自包含；逐公式 OMML→LaTeX 编排调用 markitdown oMath2Latex API + styles/dstrike/zip casing 兜底修复，MIT 归属保留）：mammoth/python-docx 降级路径公式不再丢失；单公式失败只跳过并诚实计数（实测 markitdown 整体 pre_process API 会在单个畸形公式上放弃全部数学转换，故按逐元素容错落地）；门D quality_check 新增源侧 OMML 计数（src_omml）+「公式」结构对比行 + 公式丢失异常信号
- 自包含分发（2026-09-09 用户指令）：上述迁移物均为本 skill 内部独立完整副本，零跨 skill 依赖，单 skill 单独安装即完整运行
- SKILL.md：门C 失败重试条款升级为 MUST 调用 convert_pipeline.py（M1）；目录结构补登记；backends.md markitdown 条目定位细化（兼作降级链 runner）

### 变更

- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.4.0

## [1.3.0] - 2026-09-08

### 新增

- 输入规模守卫 `scripts/scale_guard.py`（P2-2，anydoc limits.rs 口径）：preflight 统一集成——ZIP 容器族检查条目数（100k）/总解压量（512MiB）/单条目（128MiB）硬上限，超限 BLOCK（ResourceLimit=完全不可能产出语义）；表格类网格槽位估算（dimension+mergeCells）超预算 4M 固定走 L1 流式路径；守卫明细写入预检 JSON `scale_guard` 字段
- 变异冒烟测试 `tests/mutation_smoke.py`（P2-3，方法论蒸馏自 anydoc tests/robustness.rs）：真实样本确定性变异（xorshift64*，字节翻转/随机截断 ×25 轮），断言「门A JSON 必产出、引擎可失败但永不挂起/信号崩溃」；`--quick` 快速冒烟
- 真实格式样本固化 `tests/samples/`（×11，源：anydoc-main fixture）并在 full-testcases 新增 T7 用例组
- 质量四维 LLM 抽评方法论（P2-1）：`references/fidelity-spec.md` §质量四维抽评（completeness/structure/formatting/cleanliness，LLM-judge 双 swap）；门D 增加可选抽评条款——默认关闭，启用属付费确认场景（MUST 用户二次确认，NEVER 自动调用）
- 修复：preflight zip 探测 except 补 `zlib.error`（损坏 deflate 流此前逃逸导致编排层崩溃退出、无 JSON 产出——变异冒烟 P2-3 实测发现并复现）

### 变更

- SKILL.md：诚实声明追加「绝不半成品交付」MUST 条款（P2-4，对齐 anydoc「错误=完全不可能产出」）；门A 增加输入规模守卫说明；目录结构与磁盘同步（补登记 postprocess.py/dump_assets.py/needsocr_check.py 等存量脚本）

## [1.2.0] - 2026-09-08

### 新增

- anydoc（Firecrawl，MIT，v0.2.4）接入为一等后端并固定全链首选（anydoc-main 蒸馏报告 v1.3.0 P0-1）：`scripts/detect_backends.py` 新增 dual 型双探测（import anydoc 优先 / CLI 兜底）；L0/L1/DOC 档降级链固定为 anydoc → 既有链，探测 JSON 决定，NEVER Agent 另选
- `.doc` 旧格式路径定案修订：anydoc 可用时 MUST 直读（自研 MS-DOC 解析器，`doc_convert.mode=direct`），anydoc 缺失时才降级 LibreOffice 中转（冲突 4 裁定）；`backends.md` 同步为七后端矩阵
- 图片资产落盘适配层 `scripts/dump_assets.py`（P0-4 唯一路径）：anydoc 主链时 MUST 运行——to_document().assets 逐个落盘 `assets/asset_<id>.<ext>` + MD 末尾追加「图片资产清单」段保证引用一一对应；幂等（重跑不重复追加）
- `references/backends.md`：anydoc 行（能力/安装/许可证 MIT/已验证命令）+ .doc 直读路径 + 演进记录
- `scripts/postprocess.py` 升级（P1-2/P1-6）：锚点从无差别删除改为两遍式——先收集 `[](#...)` 引用集合，仅删未被引用锚点（交叉引用存活）；新增动态围栏修复与破表检测（检测型，修复职责归 anydoc 主链已转义输出）

### 变更

- 门B 措辞：六后端 → 七后端（anydoc dual 型双通道首选）；门C：anydoc 主链资产契约（dump_assets.py）写入；表格式 `.doc` 契约修订为「anydoc 直读首选、LibreOffice 降级」

## [1.1.1] - 2026-09-08

### 新增

- 家族统一五格式优雅跳过（用户指令 2026-09-08）：`scripts/preflight.py` 新增守卫——输入为 .odt/.ods/.odp/.rtf/.epub（tri-xx2md 家族统一不支持格式，含内容为此类格式的误标 zip/RTF 文件）时输出 `status=SKIP`（reason_code=unsupported_format，退出码 0，未做任何转换尝试）
- 强制执行契约新增「不支持格式优雅跳过」条目；职责边界明确五种格式为家族统一不支持范围——明确提示无法转换并跳过，NEVER 强行转换、NEVER 报错中断

## [1.1.0] - 2026-08-24

### 新增

- 门C 确定性后处理脚本 `scripts/postprocess.py`：去除后端输出中的 HTML 标签（Word 书签锚点 `<a id="…">`/`</a>`/`<span>`/`<div>`/`<o:p>` 等，保留 br/sub/sup/kbd/code/img/table 白名单）、HTML 实体解码（`&amp;`/`&lt;`/`&gt;`/`&quot;`/`&nbsp;`）、围栏感知合并连续空行与清理行尾空白；保留标题层级（#）、加粗/斜体、有序/无序列表序号、表格语法等 MD 格式化信息
- 质量标准新增「HTML 标签清理」维度（无残留非白名单标签、实体已解码，以 `postprocess.py` 统计核对）

### 变更

- 门C 后处理步骤：MUST 先运行 `scripts/postprocess.py --md <同名>.md` 做确定性标签清理，再执行页眉页脚/图片路径/MD 语法等后续处理；明确 NEVER 删除有序/无序列表序号

## [1.0.0] - 2026-08-24

### 新增

- 首发版：Word 转 Markdown 编排与质量保障 skill（tri-forge 门②生成，严格参照 tri-pdf2md 模式）
- 四阶段管道：门A 预检分级（`scripts/preflight.py`：文件类型魔数判定 docx=PK zip 头 / doc=OLE 复合文档头 D0CF11E0、OOXML 加密检测、段落/图片/表格计数、等级建议）→ 门B 后端探测（`scripts/detect_backends.py`：六后端 import/CLI 双探测 + 档位决策 + 降级链 + .doc 旧格式路径）→ 门C 结构降维转换（指导 Agent 调后端官方命令）→ 门D 质量校验（`scripts/quality_check.py`）
- 保真度契约（用户硬要求）：report.md MUST 含保真率、丢失率等关键数据——文本召回率（字符 bigram 覆盖）/ 丢失率 / 噪声率 / 结构对比（标题/表格/图片）/ 置信度 A/B/C / 异常清单 / 固定复核项；源文本不可提取时召回率显式「不适用」NEVER 编造
- 双档分级策略：L0 快速（mammoth/markitdown/python-docx）/ L1 标准（pandoc）；.doc 旧格式经 LibreOffice headless 转 docx 中间格式（antiword 纯文本兜底）
- 双格式兼容：.docx（OOXML）与 .doc（OLE 二进制）；WPS 生成的 .docx/.doc 同格式兼容
- 诚实边界契约：Word→MD 是「结构降维」（批注/修订/页眉页脚/嵌入对象必然丢失）；OOXML 加密 NEVER 破解（BLOCK）；图表提取为 assets/ 不转正文；GPL 后端只调用不分发（代码版权合规章节）
- references 三份唯一真源：`backends.md`（后端矩阵+已验证命令）、`fidelity-spec.md`（保真度阈值）、`version-check-spec.md`（版本检查）
- 上游依赖检测三态逻辑（快照模式/引导安装/降级模式）+ tri-intent I08·docx2md 子类一跳路由接入
- 全场景测试用例 `tests/tri-docx2md-full-testcases.md`（管道/降级/保真/边界/合规/版本六组）
