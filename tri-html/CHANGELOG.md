# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

## [1.3.5] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.3.4] - 2026-09-25

### 变更

- **新增「兜底处理（NEVER 静默失败）」章节**：补齐家族合规判据第 14 条要求的五类异常显式降级路径（版本检查异常 / 门禁不过 / 上游缺失 / hook 缺失 / 异常场景），并按本 skill 的触发源与既有机制定制。属文档补全，无行为变更（无代码改动）。

## [1.3.3] - 2026-09-24

### 变更

- **版本门节收敛为瘦指针 STUB**：`## 版本检查与更新机制` 由 35 行全量版收敛为 14 行（执行方式 + 真源指针），移除已失效的**远端 skillhub 内联细则**（端点解析 / 四态判定 / 升级流程 / SemVer 比较算法）。依据 `references/version-check-spec.md` §六（该节须 ≤30 行、禁内联细则）；本仓库已转自维护 fork（`scripts/check_update.py` 内置 `SELF_MAINTAINED = True`，完全跳过远端请求），原节描述的行为**永不执行**。
- **强制执行契约 §0 同步修正**：版本门措辞由「连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级」改为「运行 `scripts/check_update.py` 做本地版本一致性校验，本仓库为自维护 fork、不做远端比对」，消除 prompt 层与脚本实际行为的直接矛盾。
- 非功能性变更（文档口径），无行为变更。

## [1.3.2] - 2026-09-24

### 变更

- **分支收窄为编程工作流专线（22 skill）**：清理对已移除 skill 的交叉引用——职责边界表 / 不由本 skill 处理表的对应行改为「本分支未包含（原 tri-xxx）」或删除；已删的委派关系与相邻边界说明同步失效。非功能性变更（文档）。

## [1.3.1] - 2026-09-24

### 变更

- **落盘目录改名 `arch-viz/` → `html/`**：链路文档默认落 `.tribro/html/<命名>/`（原 `.tribro/arch-viz/<命名>/`）。命名判据见 `tri-forge/references/family-spec.md` §1.4 — 目录名 MUST 可从 skill slug 机械推导（`tri-html` → `html/`），原 L3 子意图名 `arch-viz` 不可推导。**旧目录不自动迁移**：已存在 `.tribro/arch-viz/` 的项目请手工改名，否则新产物会另起 `.tribro/html/`。

## [1.3.0] - 2026-09-22

### 新增

- **外部引擎演进对照登记**：新增 `references/engine-evolution-notes.md`——登记 vendored 引擎基线与外部演进的能力差（工作流约束驱动编译器 / v1→v2 迁移通道 / 内置品牌标记目录 / 机器可读参数回执 / 产物字体自包含 / 输出类型白名单 / 包内更新探测共 7 项），含现状基线清单、同步前置条件、同步评估要点与触发时机建议；登记项在引擎补齐前不进入创作路径。
- **SKILL.md 能力边界铁律**：§渲染引擎双模 新增「能力边界铁律」——作者契约只承诺 vendored 引擎真实具备的能力，引擎不具备的外部演进能力 MUST NOT 进入创作路径或对用户承诺。
- **交付诊断纪律补全**（`references/viewer-authoring.md` §五）：① 失败交付禁跑 `visual-check`（会检查到过期的最后好图而非失败候选）；② 三声明分离（deliver 确定性检查 / visual-check 浏览器证据 / 感知性视觉审查独立汇报）；③ compare 失败恢复处置（恢复目录保留并报告备份→目标路径）。
- **品牌能力现状标注**（`references/viewer-authoring.md` §四）：内置品牌标记目录未随引擎分发（`brands` 内置发现返回空），仅显式 `brands capture` 路径可用且需网络。

### 修订

- 去痕迹中性化：`references/viewer-authoring.md` 开篇移除来源过程性表述，改为能力承诺声明 + 差距登记指针；`references/THIRD-PARTY-NOTICE.md`「外部同步约定」改用「重新同步」称谓并新增演进登记入口与「修改说明」节。
- SKILL.md / README.md「目录结构」同步新增 reference 文件与 `tests/run_exec_tests.py` 条目。

### 修复（真实执行测试发现，三轮回归 31/31 通过）

- **引擎兼容性（关键）**：`scripts/viewer/bin/viewer.mjs` `runNode` 新增 worker 线程回退——在禁止 node.exe 派生子进程的 Windows 安全策略环境（spawnSync 对任意子进程返回 EBUSY）下，validate/deliver/compare/render 此前 100% 失败（"Renderer process could not start"）；现改经 `worker_threads` 进程内执行并保持 spawnSync 形结果契约，spawn 可用时行为不变。
- **产物零外部依赖（单文件铁律）**：`scripts/viewer/assets/template.html` 移除 Google Fonts 两处外部 `<link>`；此前每张 viewer 成品均引用 fonts.googleapis.com/gstatic.com，离线或不可达网络下阻塞首屏。全部 font-family 已有本地/系统回退链，移除无渲染影响。
- **CLI 静默吞错**：`commandValidate`/`commandRender` 补未知 `--选项` 与超量位置参数守卫（exit 2），对齐 commandDeliver 既有守卫。
- **组装器健壮性**：`scripts/build_html.py` 渲染阶段异常兜底为 `[ERROR][渲染]` + exit 2（此前以裸堆栈崩溃）；输出目录缺失时结构化报错 exit 2。
- **文档勘误**：`references/engine-evolution-notes.md` E3 更正——内置品牌发现实测可用（标记编译于 generated 模块），非「返回空」；E5 更新为「已轻量修复外部字体引用」。`references/viewer-authoring.md` 品牌基线说明同步更正。

### 新增

- **可执行面自动化测试**：`tests/run_exec_tests.py`（31 用例：引擎探测/CLI 正常·边界·异常/组装与降级链/版本门四态 simulate 注入），真实执行 + 硬性断言 + JSON 报告，退出码=失败数；报告落 `.tribro/html-exec-tests/`。

## [1.2.2] - 2026-09-18

### 新增

- **质量标准补「产出前自检清单」**：新增四检通用自检（结构/合规/溯源/可验证），对齐 `docs/guides/skill-写作规范.md` §3；重试仍失败回到对应门或走 `tri-true` 兜底。

## [1.2.1] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手架构问题的直接修复（tri-coding/tri-fix）、审计清单生成（tri-checklist）、代码级深度剖析报告（tri-code-analyzer）与意图识别（tri-intent），强化「只分析不改码」边界。

## [1.2.0] - 2026-08-28

### 新增

- **内置高精度图表引擎
  - 五类技术图确定性渲染：architecture / workflow / sequence / dataflow / lifecycle，各有 JSON Schema（`scripts/viewer/schemas/`）
  - showcase 客观门禁：9 项检查（Schema/布局/HTML·SVG/线路/标签净空）全过才原子提交；失败输出结构化诊断（code/subject/evidence/supportedFixes）
  - 单文件交互 HTML 成品：深浅主题、搜索聚焦、路径探查、角色透镜、故事播放、演示模式、PNG/SVG/WebM/1200×630 分享卡导出
  - `validate` / `deliver` / `render` / `preview` / `visual-check` / `guide` / `brands` / `doctor` / `demo` 全套 CLI
  - `compare` 架构差分（显式启用）：两份已校验架构快照 → Before / Delta / After + 机器回执
- **渲染引擎双模机制**：新增「§渲染引擎双模」（SKILL.md），图表按类型分流——五类技术图走 viewer 引擎高精模式，目录树/类图/ER/旅程图继续走 Mermaid 兼容模式；`build_html.py --check-engine` 探测 Node ≥ 18 与引擎文件，缺失时自动整体回落 Mermaid 并在报告标注降级原因，**绝不阻断交付**
- **build_html.py viewer 集成**：`analysis.json` 新增可选顶层 `viewer_diagrams[]`（type/title/ir/quality）；组装时逐张 deliver、报告嵌入链接卡片（含校验摘要 9/9、SHA-256）；无 viewer_diagrams 时行为与 1.1.1 完全一致（向后兼容）
- **作者契约参考** `references/viewer-authoring.md`：类型路由表、快速创作路径、创作不变量（主路径优先/间距=净空/标签语义/≤12 节点）、修复循环上限 2 轮、Mermaid→IR 转换方法、交付验收口径
- **门②升级**：交付确认材料新增 viewer `deliver` 客观回执（checksPassed/errors/warnings/SHA-256），主观审美让位于可验证事实
- **触发语义扩展**：拓扑/时序/数据流/状态机可视化、「交互式架构图」「可导出架构图」「架构差异对比」等触发词纳入本 skill（仍归属 I10 arch-viz，不新增路由键）

### 变更

- **单文件铁律细化**：主报告单文件 + 每张 viewer 图表独立单文件成品（各自零依赖）；viewer 成品与可选 analysis.json 不视为散装多文件
- **六维框架图表列更新**：架构设计/功能设计/特殊设计标注 viewer 优先或按语义分流
- **处理流程更新**：新增引擎探测步骤（门①前）；六维分析后新增 viewer IR 校验-修复-交付子流程
- **产物命名规范扩展**：viewer 成品 `<主报告stem>-view-<序号>-<类型>.html`；链路文档新增 `.viewer-ir/` 中间产物目录
- **质量标准新增 3 条**：viewer 门禁（9/9 + SHA-256 回执）、引擎降级诚实、修复循环上限

### 版本同步

- frontmatter version `1.1.1` → `1.2.0`；`_meta.json`、tests `based_on` 同步至 `1.2.0`

## [1.1.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源 `tri-intent/references/version-gate.md`，消除各 skill 内的重复表述
- frontmatter version `1.1.0` → `1.1.1`

## [1.1.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.0.0` → `1.1.0`

## [1.0.0] - 2026-08-02

### Added

- 初版发布。tri-xxx 家族下游执行 skill，认领 I10 arch-viz 子类。
- **六维架构分析方法论**：架构设计 / 目录结构 / 技术栈 / 代码设计 / 功能设计 / 特殊设计，每维度含检查项清单 + 数据采集命令 + 输出图表类型（详见 `references/analysis-dimensions.md`）。
- **Mermaid 图表模板库**：C4 Context/Container 图、目录树 mind map、文件类型饼图、技术栈矩阵、依赖关系图、类图、ER 图、功能模块协作图、用户旅程图、状态机、安全认证流程图、缓存架构图、监控拓扑图（详见 `references/mermaid-templates.md`）。
- **单文件 HTML 组装器** `scripts/build_html.py`：读取 analysis.json → 生成 HTML5 骨架 → 注入内联 CSS（深色/浅色主题切换）→ 注入 Mermaid.js v10.9.1（MIT）→ 注入交互 JS（折叠/展开/全屏/主题切换）→ Mermaid 语法校验 → 输出单文件 HTML。
- **双审批门**：门①分析范围确认 + 门②HTML 交付确认，禁跳门抢跑。
- **三态上游依赖检测**：A 快照模式 / A0 待识别 / B 引导安装 / C 降级模式。
- **架构观察机制**：发现的问题按 BLOCKER/MAJOR/MINOR 三级标注，含修复建议。
- **§3.13 代码版权与许可证合规**：四类风险（版权署名/许可证冲突/依赖供应链/标识披露）+ 提交前六项自检 + 底线声明。
- **完整配套**：README.md / CHANGELOG.md / tests/tri-html-full-testcases.md / references/×2 / scripts/×1。
