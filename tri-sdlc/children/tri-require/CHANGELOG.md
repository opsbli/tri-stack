# Changelog

本文件记录 tri-require（tri-sdlc P1 需求分析子SKILL）的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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

- 初始版本：tri-sdlc 九阶段编排的 P1 需求分析子SKILL
- 10 条强制执行契约：强制前置（校验 P0 已通过）、面向门禁产出、ID 唯一且贯穿、验收标准可判定、不越范围、矩阵双向连通、无占位交付、回炉逐条闭环、不越权、自检句
- 六步需求工程方法论：需求采集与分类 / ID 与优先级 / 用户故事 / 验收标准 / 可追溯矩阵 / 基线冻结，逐步对应 `P1-M1`–`P1-M7`
- 需求分类矩阵：功能性三子类 + 非功能性性能·安全·兼容三类强制覆盖（不适用需显式声明理由）
- ID 规则（`REQ-nnn` 统一编号空间、作废只标记不删号）与双优先级体系（MoSCoW / RICE）
- 用户故事三段式检验表（角色 / 能力 / 价值，含反例）
- 验收标准 Given-When-Then 范式 + 可观测·可复现·单一断言三检验点 + 反例清单
- 可追溯矩阵双向检查规则（孤儿需求 / 无源验收标准 / 矩阵不全 / 悬空回链）
- 需求基线冻结声明（基线版本 + 冻结时间 + 冻结声明，回炉递增）
- 四件套模板要点（requirements / user-stories / acceptance-criteria / traceability-matrix）
- 上游依赖检测两态（编排模式 / 引导安装），与 tri-sdlc 对称双向校验
- 落盘 `.tribro/sdlc/<命名>/P1-requirements/`，文件名固定，回炉覆盖更新且修订记录累积
- 配套 README.md 与 tests/tri-require-full-testcases.md
