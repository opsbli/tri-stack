# Changelog

本文件记录 tri-pptx2md 的版本演进，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.4.5] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手 PPT 文档操作、语言翻译与 MD 之外格式转换，只做 PPT→Markdown 转换。

## [1.4.4] - 2026-09-16

### 修复

- 门D 召回率口径：源侧改为**逐页**切字符 bigram 再求并集（原为所有页拼成一个串再切）。跨页边界不是真实邻接，拼接会造出「源侧存在、MD 侧因 `## Slide N` 页序锚点而永远匹配不到」的伪 bigram——实测 3 页高重复度 PPT 的完美转换只有 92.86% 并被判 B，与 fidelity-spec §一「召回 ≥95% 可达」相悖。修复后完美转换恒为 100% / A，遵守契约 #12 锚点不再与召回率互斥
- 门D 归一化：normalize 先做 NFKC 折叠，全角字母数字（`２０２６`）与兼容字符归一到半角后参与统计。修复前全角内容不进分母，整段丢失而召回率恒为 1.0，看不出问题
- 门D 置信度：召回 <85% 优先判 **C**（原由「页覆盖 ≥90% 或 召回 ≥85%」的 or 分支先行命中 B，使 fidelity-spec §三 C 行该条件在页覆盖达标时恒不可达）。一份「页都在但正文大面积缺失」的 MD 不再被判成 B
- 门D 理由文案：改为按实际命中条件动态生成，NEVER 硬编码「（85–95%）」区间（修复前会出现「文本召回 45.8%（85–95%）」这种自相矛盾的表述）
- 门D 异常清单：新增 `md_extra_blocks` 指标，MD `## Slide` 块数超过源页数时进异常清单并判 C（原页覆盖用 min() 截断到 100%、零告警）

### 新增

- `scripts/verify_recall.py`：召回率口径回归自检（零第三方依赖，zipfile 现场拼最小 .pptx），覆盖跨页粘连/全角数字/低召回判 C/多写块四条，退出码 0/1

### 文档

- `references/fidelity-spec.md`：§二 补 NFKC 折叠与「逐页 bigram」口径；§三 补 B/C 判定顺序裁决与「结构丢失」口径澄清（图片/备注缺失只做 A→B）
- `SKILL.md`：门D 指标表与置信度表同步；目录结构补 `verify_recall.py`
- 依据：实践案例文章 `articles/developer-tools/20260916-tri-pptx2md-recall-number-trap.md` 的实测问题清单反向审计；版本联动四件套同步 1.4.4

## [1.4.3] - 2026-09-09

### 变更

- 文档同步：README 测试节版本引用（v1.0.0 → v1.4.3）；版本联动四件套同步 1.4.3（依据 docs/quality-test-xx2md-20260909.md §九）

## [1.4.2] - 2026-09-09

### 变更

- 可用性：门D quality_check 必选参数补 help 文本（--ppt/--md）
- 健壮性：dump_assets 缺 python:anydoc 绑定时报可操作安装指引（原裸 ModuleNotFoundError）
- 维护性：postprocess 模块 docstring 归属名修正（tri-docx2md → tri-pptx2md）；scripts/__pycache__ 清理
- 依据：七维质量测试报告 docs/quality-test-xx2md-20260909.md；版本联动四件套同步 1.4.2

## [1.4.1] - 2026-09-09

### 变更

- 门A 接入 M9 内容真身二次校验：preflight 新增 content_check 字段（.pptx 族 zip 校验 / .ppt/.pps/.pot OLE∪OPC 并集校验），sniffer.py 同源副本落盘
- 自产表工具 md_table.py 同源副本落盘
- convert_pipeline 执行核心新增 meta 钩子（M4/M9：本 skill 暂无附加项）
- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.4.1

## [1.4.0] - 2026-09-09

### 变更

- M7 路线裁决（选 A）：GRADE_ORDER 三档（L0/L1/PPT）降级链将 markitdown 提前至 python-pptx 之前——降级路径获得「图表→MD 表格/演讲者备注保留/SVG 无栅格兜底」能力（依赖 markitdown 已安装，缺失时自动下移 python-pptx，NEVER 崩溃）；references/backends.md 分级策略表与矩阵定位同步；SKILL.md 门C 表述更新
- 强制执行契约铁律追加 MIT 归属条款（2026-09-09 用户裁决，迁移报告待定点①）
- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.4.0

## [1.3.0] - 2026-09-09

### 新增

- M1 降级链执行器 `scripts/convert_pipeline.py`（自包含副本，设计迁移自 markitdown _convert 循环 + FailedConversionAttempt，MIT 归属保留）：按 detect_backends 的 selected+fallback_chain 一次性代码化执行降级链，逐后端 attempts 异常聚合（类型/消息/耗时/栈尾）+ 全失败聚合诊断；空产物视为失败；单后端 300s 超时防挂死；契约升级——失败重试 MUST 调用本脚本，NEVER Agent 手工逐后端重试
- M2 输出编码兜底 `scripts/_io_safe.py`（家族同源副本，迁移自 markitdown __main__._handle_output 的 errors="replace" 模式）：全部输出脚本 print→safe_print 机械替换，Windows GBK 控制台输出含 GBK 外字符 NEVER 再崩溃；check_update.py 为家族同源文件刻意不动
- 自包含分发（2026-09-09 用户指令）：上述迁移物均为本 skill 内部独立完整副本，零跨 skill 依赖，单 skill 单独安装即完整运行
- SKILL.md：门C 失败重试条款升级为 MUST 调用 convert_pipeline.py（M1）；目录结构补登记；backends.md markitdown 条目定位细化（兼作降级链 runner）

### 变更

- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.3.0

## [1.2.0] - 2026-09-08

### 新增

- 输入规模守卫 `scripts/scale_guard.py`（P2-2，anydoc limits.rs 口径）：preflight 统一集成——ZIP 容器族检查条目数（100k）/总解压量（512MiB）/单条目（128MiB）硬上限，超限 BLOCK（ResourceLimit=完全不可能产出语义）；表格类网格槽位估算（dimension+mergeCells）超预算 4M 固定走 L1 流式路径；守卫明细写入预检 JSON `scale_guard` 字段
- 变异冒烟测试 `tests/mutation_smoke.py`（P2-3，方法论蒸馏自 anydoc tests/robustness.rs）：真实样本确定性变异（xorshift64*，字节翻转/随机截断 ×25 轮），断言「门A JSON 必产出、引擎可失败但永不挂起/信号崩溃」；`--quick` 快速冒烟
- 真实格式样本固化 `tests/samples/`（×8，源：anydoc-main fixture；大体积 pres.ppt 留驻 .tribro 不入包）并在 full-testcases 新增 T7 用例组
- 质量四维 LLM 抽评方法论（P2-1）：`references/fidelity-spec.md` §质量四维抽评（completeness/structure/formatting/cleanliness，LLM-judge 双 swap）；门D 增加可选抽评条款——默认关闭，启用属付费确认场景（MUST 用户二次确认，NEVER 自动调用）
- 修复：preflight zip 探测 except 补 `zlib.error`（损坏 deflate 流此前逃逸导致编排层崩溃退出、无 JSON 产出——变异冒烟 P2-3 实测发现并复现）

### 变更

- SKILL.md：诚实声明追加「绝不半成品交付」MUST 条款（P2-4，对齐 anydoc「错误=完全不可能产出」）；门A 增加输入规模守卫说明；目录结构与磁盘同步（补登记 postprocess.py/dump_assets.py/needsocr_check.py 等存量脚本）

## [1.1.0] - 2026-09-08

### 新增

- anydoc（Firecrawl，MIT，v0.2.4）接入为一等后端并固定全链首选（anydoc-main 蒸馏报告 v1.3.0 P0-1）：`scripts/detect_backends.py` 新增 dual 型双探测（import anydoc 优先 / CLI 兜底）；L0/L1/PPT 档降级链固定，探测 JSON 决定，NEVER Agent 另选
- `.ppt/.pps/.pot` 旧格式路径定案修订：anydoc 可用时 MUST 直读（自研二进制记录流解析器，基准 .ppt 80），anydoc 缺失时才降级 LibreOffice 中转（冲突 4 裁定）；`backends.md` 同步为五后端矩阵
- 图片资产落盘适配层 `scripts/dump_assets.py`（P0-4 唯一路径）：anydoc 主链时 MUST 运行——assets 落盘 + MD 资产清单段，幂等
- `references/backends.md`：anydoc 行 + .ppt 直读路径 + 演进记录
- 门C 后处理脚本 `scripts/postprocess.py` 新增（P1-2/P1-6，docx2md 同源移植）：锚点两遍式（仅删未被引用锚点）、动态围栏、破表检测、实体解码、围栏感知清理

### 变更

- 契约 #11 修订：旧格式强制 LibreOffice 中转 → anydoc 直读首选、LibreOffice 降级；门A/门B/门C 同步

## [1.0.1] - 2026-09-08

### 新增

- 家族统一五格式优雅跳过（用户指令 2026-09-08）：`scripts/preflight.py` 新增守卫——输入为 .odt/.ods/.odp/.rtf/.epub（tri-xx2md 家族统一不支持格式，含内容为此类格式的误标 zip/RTF 文件）时输出 `status=SKIP`（reason_code=unsupported_format，退出码 0，未做任何转换尝试）
- 强制执行契约新增「不支持格式优雅跳过」条目；职责边界明确五种格式为家族统一不支持范围——明确提示无法转换并跳过，NEVER 强行转换、NEVER 报错中断
## [1.0.0] - 2026-08-24

### 新增

- 首发版：PPT 转 Markdown 编排与质量保障 skill（tri-forge 门②生成）
- 四门管道：门A 预检分级（`scripts/preflight.py`：文件类型魔数判定/页数/备注/图片计数/旧格式标记/等级建议）→ 门B 后端探测（`scripts/detect_backends.py`：四后端 import/CLI 双探测 + 档位决策 + 降级链）→ 门C 结构降维转换（指导 Agent 调后端官方命令）→ 门D 质量校验（`scripts/quality_check.py`）
- 双格式兼容：.pptx（OOXML）与 .ppt（旧二进制 OLE）；WPS 生成的 .pptx/.ppt 同格式兼容
- 保真度契约（用户硬要求）：report.md MUST 含页覆盖率、文本召回率、丢失率等关键数据——页覆盖率 / 文本召回率（字符 bigram 覆盖）/ 丢失率 / 缺页明细 / 结构对比（每页文本/图片/备注）/ 置信度 A/B/C / 异常清单 / 固定复核项
- 四档分级策略：L0 快速（python-pptx/markitdown）/ L1 标准（pandoc）/ PPT 旧格式（LibreOffice headless 转中间 .pptx）/ L3 LLM 兜底（付费须确认），全场景降级链
- 输出结构：每张 slide 一个 `## Slide N` 二级标题块（标题 + 正文要点 + 备注引用块 + 图片引用），图片提取为 assets/
- 诚实边界契约：非 PPT 文件 BLOCK；图表/SmartArt 提取为 assets/ 不转正文；GPL/MPL 后端只调用不分发（代码版权合规章节）
- references 三份唯一真源：`backends.md`（后端矩阵+已验证命令）、`fidelity-spec.md`（保真度阈值）、`version-check-spec.md`（版本检查）
- 上游依赖检测三态逻辑（快照模式/引导安装/降级模式）+ tri-intent I08·pptx2md 子类一跳路由接入
- 全场景测试用例 `tests/tri-pptx2md-full-testcases.md`（管道/降级/保真/边界/合规/版本六组）
- 全管道冒烟验证通过：.pptx（L0→python-pptx）、.ppt（LibreOffice 转换路径）、非 PPT（BLOCK）三路径
