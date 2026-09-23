# Changelog

本文件记录 tri-html2md 的版本演进，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.3.5] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手 HTML 抓取/渲染/爬虫、语言翻译与 MD 之外格式转换，只做 HTML→Markdown 转换。

## [1.3.4] - 2026-09-09

### 修复

- 门D 脚本/样式泄漏判定改两段式（质量测试轮 §六-1 降噪）：anomaly（强制 C）= 80 字符连续窗口逐字出现在 MD（结构证据，真实整块泄漏）；bigram 覆盖率 >30% 但无逐字命中降为 warning（不降级）——消除 Docusaurus 类站点导航/JSON-LD 文案与正文词汇重叠的误报（test_blog 实测置信度 C→A，覆盖率 98.6%/窗口 0）
- 修复纯脚本页 `md_bg` 未定义的 NameError 隐患（泄漏检测块改独立计算 bigram）
### 变更

- README 测试节版本引用同步（v1.0.0 → v1.3.4）；版本联动四件套同步 1.3.4（依据 docs/quality-test-xx2md-20260909.md §九）

## [1.3.3] - 2026-09-09

### 变更

- 可用性：门D quality_check 必选参数补 help 文本（--html/--md）
- 维护性：postprocess 模块 docstring 归属名修正（tri-docx2md → tri-html2md）；scripts/__pycache__ 清理
- 依据：七维质量测试报告 docs/quality-test-xx2md-20260909.md；版本联动四件套同步 1.3.3

## [1.3.2] - 2026-09-09

### 变更

- M4：markitdown/html2text/bs4 runner 统一包裹 RecursionError 降级（弃结构保内容，meta.fallback=get_text_plain；降级产物门D 置信度 MUST ≤B）
- M9：preflight 新增 content_check 字段（防「扩展名对、内容不对」走错路径）；_read_text_auto/trafilatura runner 统一经 sniffer.detect_charset，报告记录探测编码
- 新增 sniffer.py / md_table.py 同源副本
- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.3.2

## [1.3.1] - 2026-09-09

### 变更

- 强制执行契约铁律追加 MIT 归属条款：MIT 许可证后端的设计模式级迁移允许，MUST 在迁移文件头部保留归属声明（2026-09-09 用户裁决，迁移报告待定点①）
- 版本联动：SKILL/CHANGELOG/tests/_meta.json 四件套同步 1.3.1

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
- 变异冒烟测试 `tests/mutation_smoke.py`（P2-3，方法论蒸馏自 anydoc tests/robustness.rs）：真实样本确定性变异（xorshift64*，字节翻转/随机截断 ×25 轮）（无 Rust 引擎 skill：仅门A 冒烟），断言「门A JSON 必产出、引擎可失败但永不挂起/信号崩溃」；`--quick` 快速冒烟
- 真实格式样本固化 `tests/samples/real-sample.html`（综合真实格式样本：CJK/实体/表格/锚点/嵌套列表/代码块）并在 full-testcases 新增 T7 用例组
- 质量四维 LLM 抽评方法论（P2-1）：`references/fidelity-spec.md` §质量四维抽评（completeness/structure/formatting/cleanliness，LLM-judge 双 swap）；门D 增加可选抽评条款——默认关闭，启用属付费确认场景（MUST 用户二次确认，NEVER 自动调用）

### 变更

- SKILL.md：诚实声明追加「绝不半成品交付」MUST 条款（P2-4，对齐 anydoc「错误=完全不可能产出」）；门A 增加输入规模守卫说明；目录结构与磁盘同步（补登记 postprocess.py/dump_assets.py/needsocr_check.py 等存量脚本）

## [1.1.0] - 2026-09-08

### 新增

- 门C 后处理脚本 `scripts/postprocess.py` 新增（P1-2/P1-6，docx2md 同源移植）：锚点两遍式（仅删未被 `[](#...)` 引用的锚点）、动态围栏、破表检测、实体解码、围栏感知清理
- 本 skill 后端链不变（anydoc 不做 HTML，蒸馏报告 v1.3.0 P0-1 隔离边界）

## [1.0.1] - 2026-09-08

### 新增

- 家族统一五格式优雅跳过（用户指令 2026-09-08）：`scripts/preflight.py` 新增守卫——输入为 .odt/.ods/.odp/.rtf/.epub（tri-xx2md 家族统一不支持格式，含内容为此类格式的误标 zip/RTF 文件）时输出 `status=SKIP`（reason_code=unsupported_format，退出码 0，未做任何转换尝试）
- 强制执行契约新增「不支持格式优雅跳过」条目；职责边界明确五种格式为家族统一不支持范围——明确提示无法转换并跳过，NEVER 强行转换、NEVER 报错中断
## [1.0.0] - 2026-08-24

### 新增

- 首发版：HTML 转 Markdown 编排与质量保障 skill（tri-forge 门②生成，方案 `solution-design.md` 审计通过）
- 四阶段管道：门A 预检分级（`scripts/preflight.py`：文件类型/编码检测/HTML 合法性/大小/内嵌资源计数/表格表单计数/等级建议）→ 门B 后端探测（`scripts/detect_backends.py`：五后端 import/CLI 双探测 + 档位决策 + 降级链）→ 门C 转换执行（指导 Agent 调后端官方命令）→ 门D 质量校验（`scripts/quality_check.py`）
- 保真度契约（用户硬要求）：report.md MUST 含文本召回率、丢失率等关键数据——文本召回率（字符 bigram 覆盖）/ 丢失率 / 噪声率 / 结构对比（标题 h1-h6/表格/图片/链接）/ 置信度 A/B/C / 异常清单 / 固定复核项；HTML 无可见文本召回率显式「不适用」NEVER 编造
- 两档分级策略：L0 快速（markitdown/html2text/beautifulsoup4）/ L1 标准（pandoc/trafilatura）；**无 L2/L3**（HTML 已有语义结构，不需要 OCR 档——与 tri-pdf2md 的关键差异）
- 诚实边界契约：编码不可解不猜测（BLOCK）；图片提取为 assets/ 不转正文；GPL 后端（pandoc）只调用不分发（代码版权合规章节）
- references 三份唯一真源：`backends.md`（后端矩阵+已验证命令）、`fidelity-spec.md`（保真度阈值+固定复核项）、`version-check-spec.md`（版本检查）
- 上游依赖检测三态逻辑（快照模式/引导安装/降级模式）+ tri-intent I08·html2md 子类一跳路由接入
- 全场景测试用例 `tests/tri-html2md-full-testcases.md`（管道/降级/保真/边界/合规/版本六组）
- 全管道冒烟验证通过：简单 HTML（L0→markitdown→文本召回率 100%/置信度 A）、复杂 HTML（L1 建议）、无可见文本页（不适用/C）、编码不可解（BLOCK）四路径
