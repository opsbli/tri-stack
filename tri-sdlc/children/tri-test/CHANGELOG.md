# Changelog

本文件记录 tri-test（tri-sdlc P6 测试验证子SKILL）的版本变更历史。

## [1.2.1] - 2026-09-29

### 变更

- **维度 3 判据 ②「反同源静态检查」落地为可执行载体**：由
  `tri-coding/scripts/gate_lint.py mock --file <test.ts>` 承担。脚本抽取测试文件中被 stub
  的符号与被测源码的直接调用依赖求交集，命中返回码 1 并回显符号名；登记技术理由
  （`// gate-lint: same-origin-ok <理由>`）后命中降为 `acknowledged` 并回显理由，
  与本节「降级兼容」的登记要求对齐。脚本落在 `tri-coding` 下——实际写测试的路径是
  `tri-coding` I11 直调，本 skill 是 SDLC 流程的家，条文在此、载体在 `tri-coding`。
  **动机**：本条判据 tt3 批登记为「prompt 层约束，无校验器实现」的诚实边界，本批关掉。
  **边界**：纯正则、无 TS 解析器，只识别 `vi.fn()` / `vi.mocked()` / `jest.spyOn()` /
  `mock*.mockX()` 四种惯用法；`vi.importActual` 不作豁免；判据 ①③ 仍为 prompt 层约束。
  判据原文与召回边界详见 `tri-coding` 1.11.1 变更条目。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.2.0] - 2026-09-29

### 变更

- **维度 3 新增「反同源假设」三条判据 + 降级兼容**：① 断言来源可追溯——期望值 MUST 可追溯到
  `acceptance-criteria.md`，NEVER 从被测代码当前行为反推；② 反同源静态检查——mock 目标 MUST NOT 是
  被测对象**直接调用**的那个依赖函数，命中即补一条走真实实现的对照用例；
  ③ 分支覆盖 ≠ 正确——覆盖率与分支覆盖数 NEVER 计入功能正确性证据，须与通过率分开登记。
  降级兼容：目标依赖确实不可替换（进程原生 API / Electron 全局对象）时 MUST 登记技术理由 + 降级证据形式，
  并在 `test-report.md` 显式标注「该用例结论不含功能正确性证据」，NEVER 静默计入通过率。
  **动机**：tri-stack-train M4a 实证——`shell-probe` 的探测缺陷（`existsSync('cmd.exe')` 在 Windows
  只查 CWD）被测试夹具 `mockExistsSync.mockReturnValue(false)` 固化成期望行为，112/112 全绿而真机全失败。
  **与既有 P6-M3「真实执行」的关系**：P6-M3 约束**执行侧**（结果必须真跑出来），本条约束**编写侧**
  （期望值必须独立产生）；两侧缺一，绿灯都不算证据。

## [1.1.9] - 2026-09-28

### 新增

- **家族横切第 10 节「宿主兼容与提问呈现」**：紧跟「版本检查与更新机制」追加 `host-compat-stub v1` 自包含瘦节——
  在提供交互式提问工具的宿主（如 Proma 的 `AskUserQuestion`）中，🔴 STOP 用户确认检查点与 clarify-gate
  MUST 以**普通 Markdown 文本**呈现为聊天问题，**NEVER 调用交互式提问工具**
  （`AskUserQuestion` / `ask_user_question` / `request_user_input` / `clarify` 及等价物）；
  用户回复契约（逐条补充 / 按默认 / 继续 / 是·否）保持不变。
  **只管呈现形式，不改任何门控的判定条件、触发时机与处置动作**；在无交互式提问工具的宿主中本条自然空转。
  细则真源 `tri-intent/references/host-compat.md`；家族规范登记于 `tri-forge/references/family-spec.md`
  §四（第 10 节注）+ §五（待登记项）。

## [1.1.8] - 2026-09-26

### 更改

- **红灯②（上游闸门）剖面口径同步**：P5 状态合法组合收紧为「已通过（full/standard 剖面）/已跳过（仅 lite 剖面）」，与契约第 1 条精确对齐——堵住「full/standard 剖面下 P5 标已跳过」被宽口径放行的缺口。

## [1.1.7] - 2026-09-26

### 变更

- **兜底⑤补 Must 级用例冲突裁决（NEVER 交付、回报 tri-sdlc）+ 契约第 1 条 lite 修饰消歧 + 自检句实体修复。**

## [1.1.6] - 2026-09-26

### 变更

- **新增「兜底处理」章节（#14 children 补齐，四行聚合既有语义 + ⑤ 阶段定制）**。

## [1.1.5] - 2026-09-26

### 修复

- **目录结构节补登**：`references/version-check-spec.md` 与 `scripts/check_update.py`（与 f12 README 树对齐）。

## [1.1.4] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.1.3] - 2026-09-25

### 修复

- **契约第 1 条修复**：`&**：` 损坏行恢复为 `1. **强制前置**：`（模板复制事故；darwin-skill 基线评估 P0 批）。

## [1.1.2] - 2026-09-25

### 变更

- **强制契约第 0 步「版本检查前置硬门」回归自维护口径**：`skillhub` 远端校验 +
  `skillhub upgrade <slug>` → 运行自带 `scripts/check_update.py` 做本地版本一致性校验
  （本仓库为自维护 fork，不做远端比对；按脚本输出与退出码处置）
- **§版本检查与更新机制 收敛为瘦指针 STUB（v1）**：移除内联的四态判定与端点配置细则，
  改为指向 `references/version-check-spec.md`（细则真源）与 `scripts/check_update.py`（实现真源）
- **引导安装提示改为自维护安装器**：`skillhub install tri-sdlc --dir <目标目录>` →
  `python ops/install-skills.py --target <目标目录>`
- **补齐自带 `scripts/check_update.py`**：本子 skill 此前不带 `scripts/`，而版本节 STUB 引用了
  该路径（悬空引用）；现与顶层 skill 对等，单 skill 可独立安装
- frontmatter version `1.1.1` → `1.1.2`
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

### 新增

- 初始版本：tri-sdlc 九阶段编排的 P6 测试验证子SKILL
- 12 条强制执行契约：强制前置（校验 P4 齐备、P5 已通过/已跳过）、面向门禁产出、验收标准全覆盖、三层必答、真实执行、缺陷四要素、Critical 清零、复测闭环、不改代码、无占位交付、不越权、自检句
- 六维验证方法论：验收标准覆盖 / 三层测试 / 通过率达标 / 缺陷登记 / 严重缺陷清零 / 复测闭环，逐维对应 `P6-M1`–`P6-M6`
- 验收标准覆盖映射表（AC ↔ 需求 ID ↔ 用例 ↔ 层级 ↔ 结果），覆盖率须 100%，无法自动化须出人工验收用例
- 三层测试定义表（单元 / 集成 / 用户验收）及各层不适用时的显式答法
- 用例八要素（ID / 标题 / 关联验收标准 / 前置条件 / 步骤 / 预期结果 / 实际结果 / 结论）
- 通过率三口径规则（Must 级 100%、总体 ≥95% 或 manifest 覆写值、阻塞用例计入分母）
- 缺陷条目统一格式与四级分级表（Critical/Blocker 阻断门禁，Major/Minor/Trivial 不阻断但须登记处置）
- 严重缺陷清零与回炉判据表（未修回炉 P4、已修未复测不得交付、Major 确认不修需理由与影响评估）
- 复测与回归规范（单缺陷复测、回归范围写入报告、复测不通过重开并计入遗留）
- 建议项落地方式（性能与兼容性结论 `P6-R1`、测试数据与环境可复现说明 `P6-R2`）
- 与 P4 / P5 / P7 的三条职责边界说明（单测 vs 三层统一执行、静态审查 vs 动态验证、本阶段测试 vs 发布冒烟）
- 上游依赖检测两态（编排模式 / 引导安装，含「仅出测试文档」降级）
- 落盘 `.tribro/sdlc/<命名>/P6-testing/`，自动化脚本落工作区并登记，历史执行与复测记录累积保留
- 配套 README.md 与 tests/tri-test-full-testcases.md
