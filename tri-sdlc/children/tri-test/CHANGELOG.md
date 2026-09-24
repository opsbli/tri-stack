# Changelog

本文件记录 tri-test（tri-sdlc P6 测试验证子SKILL）的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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
