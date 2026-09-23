# Changelog

本文件记录 tri-xlsx2md 的版本演进，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.3.5] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手 Excel 文档操作、语言翻译与 MD 之外格式转换，只做 Excel→Markdown 转换。

## [1.3.4] - 2026-09-09

### 变更

- 文档同步：README 测试节版本引用（v1.0.0 → v1.3.4）；版本联动四件套同步 1.3.4（依据 docs/quality-test-xx2md-20260909.md §九）

## [1.3.3] - 2026-09-09

### 变更

- 可用性：门D quality_check 必选参数补 help 文本（--xlsx/--md）
- 修复（质量测试发现）：门D 工作表数探测原只识别 `## Sheet` 前缀（任意命名表如纯数字/中文表名被计 0 → 覆盖率 100% 也被误降 C）；改为计数任意 `## <工作表名>` 块并剔除资产清单段——sheet_match 恢复正确，覆盖率 100% 时置信度回 A
- 维护性：postprocess 模块 docstring 归属名修正（tri-docx2md → tri-xlsx2md）；scripts/__pycache__ 清理
- 依据：七维质量测试报告 docs/quality-test-xx2md-20260909.md；版本联动四件套同步 1.3.3

## [1.3.2] - 2026-09-09

### 新增

- M5：repair_xlsx.py showZeroes 非规范属性二进制级修复（迁移自 markitdown _xlsx_converter，MIT）；openpyxl/pandas runner TypeError 含 showZeroes → 修复字节流后重读一次，meta.show_zeroes_repaired 标注
### 变更

- M8：_sheet_to_md_table 改经 md_table.build_md_table（自产表生成即合规转义）
- M9：preflight 新增 content_check 字段（.xlsx/.xlsm zip 校验 / .doc/.xls/.xlsb OLE CFB 签名 / .ppt 旧格式并集校验）
- 修复（批次二发现）：①_run_pandas 迭代 dict 只出 key 的 M1 遗留 bug（MUST .items()）；②preflight 探测截断 .xls 时 xlrd compdoc 裸 print WARNING 污染 --json（显式传 logfile=StringIO 吞掉）
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
- 变异冒烟测试 `tests/mutation_smoke.py`（P2-3，方法论蒸馏自 anydoc tests/robustness.rs）：真实样本确定性变异（xorshift64*，字节翻转/随机截断 ×25 轮），断言「门A JSON 必产出、引擎可失败但永不挂起/信号崩溃」；`--quick` 快速冒烟
- 真实格式样本固化 `tests/samples/`（×8，源：anydoc-main fixture）并在 full-testcases 新增 T7 用例组
- 质量四维 LLM 抽评方法论（P2-1）：`references/fidelity-spec.md` §质量四维抽评（completeness/structure/formatting/cleanliness，LLM-judge 双 swap）；门D 增加可选抽评条款——默认关闭，启用属付费确认场景（MUST 用户二次确认，NEVER 自动调用）
- 修复：preflight zip 探测 except 补 `zlib.error`（损坏 deflate 流此前逃逸导致编排层崩溃退出、无 JSON 产出——变异冒烟 P2-3 实测发现并复现）

### 变更

- SKILL.md：诚实声明追加「绝不半成品交付」MUST 条款（P2-4，对齐 anydoc「错误=完全不可能产出」）；门A 增加输入规模守卫说明；目录结构与磁盘同步（补登记 postprocess.py/dump_assets.py/needsocr_check.py 等存量脚本）

## [1.1.0] - 2026-09-08

### 新增

- anydoc（Firecrawl，MIT，v0.2.4）接入为一等后端并固定全链首选（anydoc-main 蒸馏报告 v1.3.0 P0-1）：`scripts/detect_backends.py` 新增 dual 型双探测；L0/L1 档降级链固定，探测 JSON 决定，NEVER Agent 另选
- `.xlsb/.csv` 直读通道：anydoc 自研 BIFF/xlsb 解析器与 RFC 4180 CSV（多分隔符/多编码），.xlsb 不再依赖 LibreOffice 中转
- `references/backends.md`：anydoc 行 + 已验证命令 + 演进记录；资产契约 `assets: N/A`（P0-4 表格类写死判定）

### 变更

- 门B 措辞：五后端 → 六后端；门A/门C 分级表同步 anydoc 首选
### 新增

- 门C 后处理脚本 `scripts/postprocess.py` 新增（P1-2/P1-6，docx2md 同源移植）：锚点两遍式、动态围栏、破表检测、实体解码、围栏感知清理

## [1.0.2] - 2026-09-08

### 新增

- 家族统一五格式优雅跳过（用户指令 2026-09-08）：`scripts/preflight.py` 新增守卫——输入为 .odt/.ods/.odp/.rtf/.epub（tri-xx2md 家族统一不支持格式，含内容为此类格式的误标 zip/RTF 文件）时输出 `status=SKIP`（reason_code=unsupported_format，退出码 0，未做任何转换尝试）
- 强制执行契约新增「不支持格式优雅跳过」条目；职责边界明确五种格式为家族统一不支持范围——明确提示无法转换并跳过，NEVER 强行转换、NEVER 报错中断
## [1.0.1] - 2026-08-29

### 变更（毕业）

- 毕业发布至源码树 `tri-xlsx2md/`（原 `.tribro/skills/tri-xlsx2md/`），接通 tri-intent 路由 `L2=I08` + `L3_子意图=xlsx2md` 一跳下游
- 移除 skill 内 `references/version-check-spec.md` fork，§版本检查与更新机制 瘦指针改指向家族唯一真源 `tri-forge/references/version-check-spec.md`（约束 #22）
- 落盘规则更新：不再声明落盘于 `.tribro/skills/`
- 版本一致性：SKILL.md / CHANGELOG / tests / _meta.json 同步至 1.0.1

## [1.0.0] - 2026-08-24

### 新增

- 首发版：Excel 转 Markdown 编排与质量保障 skill（tri-forge 门②生成，方案审计通过）
- 四阶段管道：门A 预检分级（`scripts/preflight.py`：文件类型魔数判定/工作表数/单元格规模/加密检测/旧格式标记/超大警告/等级建议）→ 门B 后端探测（`scripts/detect_backends.py`：五后端 import/CLI 双探测 + 档位决策 + 降级链）→ 门C 结构降维转换（指导 Agent 调后端官方命令）→ 门D 质量校验（`scripts/quality_check.py`）
- 双格式兼容：.xlsx（OOXML，PK zip 魔数）与 .xls（旧二进制 BIFF，OLE 复合文档魔数 D0CF11E0）；WPS 生成的 .xlsx/.xls 同格式兼容
- 三档降级链：L0 快速（openpyxl/markitdown/xlrd）→ L1 标准（pandas/LibreOffice headless），全场景降级链
- 保真度契约（用户硬要求）：report.md MUST 含单元格覆盖率、工作表数对比等关键数据——单元格覆盖率（源非空单元格 vs MD 表格单元格）/ 工作表数对比（源 vs MD `## Sheet` 块）/ 行数对比 / 置信度 A/B/C / 异常清单 / 固定复核项
- 结构降维诚实边界：公式默认取缓存值（公式语义丢失）、格式/图表/数据透视不转正文、合并单元格展开为左上角值 + 其余空、空工作表标注「（空工作表）」——NEVER 声称无损
- 加密不破解：xlsx OOXML 加密 / xls BIFF FILEPASS 无法解密时 BLOCK 停止，提示合法解密后重试
- references 两份唯一真源：`backends.md`（后端矩阵+已验证命令）、`fidelity-spec.md`（保真度阈值）；版本检查统一指向家族 `tri-forge/references/version-check-spec.md`（不自带 fork）
- 上游依赖检测三态逻辑（快照模式/引导安装/降级模式）+ tri-intent I08·xlsx2md 子类一跳路由接入
- 全场景测试用例 `tests/tri-xlsx2md-full-testcases.md`（管道/降级/保真/边界/合规/版本六组）
- 全管道冒烟验证通过：.xlsx 简单表（L0→openpyxl→单元格覆盖 100%/置信度 A）、.xls 旧格式（L1→xlrd）、加密件（BLOCK）三路径
