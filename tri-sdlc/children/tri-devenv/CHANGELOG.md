# Changelog

本文件记录 tri-devenv（tri-sdlc P3 开发准备子SKILL）的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.1.5] - 2026-09-26

### 变更

- **新增「兜底处理」章节（#14 children 补齐，四行聚合既有语义 + ⑤ 阶段定制）**。

## [1.1.4] - 2026-09-26

### 修复

- **目录结构节补登**：`references/version-check-spec.md` 与 `scripts/check_update.py`（与 f12 README 树对齐）。

## [1.1.3] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。
- **契约第 1 条修复**：`&**：` 损坏行恢复为 `1. **强制前置**：`（模板复制事故；darwin 基线评估 P0 补遗）。

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

- 初始版本：tri-sdlc 九阶段编排的 P3 开发准备子SKILL
- 12 条强制执行契约：强制前置（校验 P2 三件套齐备）、面向门禁产出、步骤可执行、分支三类齐全、任务五要素、回链无悬空、任务覆盖设计、工作区落盘登记、无占位交付、回炉逐条闭环、不越权、自检句
- 六维准备方法论：仓库与分支策略 / 环境搭建 / 代码规范 / 提交规范 / 任务拆分 / 回链校验，逐维对应 `P3-M1`–`P3-M6`
- 分支策略三类表（主干 / 特性 / 发布，各含命名规则与合并规则、合并方式与前置条件）
- 环境搭建四项规范（可逐条执行 / 带版本号 / 有验证步骤 / 覆盖平台或声明）及反例
- 代码规范四项（工具 / 配置文件与关键规则 / 执行方式 / 例外机制）
- 提交规范（Conventional Commits 格式 + 钩子工具与触发时机）
- 任务看板五要素表（ID / 标题 / 关联需求 ID / 预估 / 负责角色）+ 状态与依赖列，状态供 `P4-M1` 校验
- 三向校验规则（任务→需求 / 需求→任务 / 设计→任务），杜绝悬空引用与设计无落地
- 建议项落地方式（CI 触发策略 `P3-R1`、一键启动脚本 `P3-R2`）
- 工作区产物登记机制：落工程配置骨架须登记路径，禁止静默写入，禁止写业务功能代码
- 上游依赖检测两态（编排模式 / 引导安装），与 tri-sdlc 对称双向校验
- 落盘 `.tribro/sdlc/<命名>/P3-devsetup/`，文件名固定，回炉覆盖更新且修订记录累积
- 配套 README.md 与 tests/tri-devenv-full-testcases.md
