# Changelog

本文件记录 tri-design（tri-sdlc P2 方案设计子SKILL）的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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

- 初始版本：tri-sdlc 九阶段编排的 P2 方案设计子SKILL
- 11 条强制执行契约：强制前置（校验 P1 四件套齐备）、面向门禁产出、需求覆盖 100%、选型必对比、接口五要素、指标可度量、不越范围、无占位交付、回炉逐条闭环、不越权、自检句
- 八维设计方法论：总体架构与模块划分 / 需求落点映射 / 数据模型 / 接口契约 / 核心链路建模 / 技术选型 / 安全设计 / 容量与性能，逐维对应 `P2-M1`–`P2-M8`
- 架构四检验点（分层 / 模块职责一句话 / 依赖单向无循环 / 边界）
- 需求落点映射表（Must 级 100% 覆盖，落点类型五取值）
- 数据模型规范：主外键与索引说明，无数据库项目须给等价数据结构定义
- 接口契约五要素表 + 错误码 ≥2 类规则，覆盖 HTTP / CLI / SDK 三类形态
- 核心链路建模（时序图或状态机，状态机须含状态集合/迁移条件/非法迁移处理）
- 技术选型对比表（候选 ≥2 + 选定 + 关联项目约束的理由）
- 安全设计三项（鉴权 / 加密 / 越权防护）及单机项目等价答法
- 容量与性能四类指标与阈值优先级（manifest 覆写 > P1 非功能 > 默认推导）
- 三件套结构要点（design / api-contract / data-model）
- 上游依赖检测两态（编排模式 / 引导安装），与 tri-sdlc 对称双向校验
- 落盘 `.tribro/sdlc/<命名>/P2-design/`，文件名固定，回炉覆盖更新且修订记录累积
- 配套 README.md 与 tests/tri-design-full-testcases.md
