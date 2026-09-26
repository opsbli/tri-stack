# Changelog

本文件记录 tri-cr（tri-sdlc P5 代码评审子SKILL）的版本变更历史。

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

- 初始版本：tri-sdlc 九阶段编排的 P5 代码评审子SKILL
- 12 条强制执行契约：强制前置（校验 P4 已通过）、面向门禁产出、静态先行、意见三要素、零待修复交付、四维必答、变更-用例映射、复审闭环、只评不改（默认）、无占位交付、不越权、自检句
- 六维评审方法论：静态检查三项 / 四维人工审查 / 意见分级定位 / Blocker 清零 / 变更-用例映射 / 复审闭环，逐维对应 `P5-M1`–`P5-M6`
- 静态检查三项执行规范（lint / 类型检查 / 构建，各记录命令与失败数；无类型系统时的替代声明答法）
- 四维审查要点表（可读性与命名 / 逻辑正确性与边界 / 性能 / 安全）及典型问题清单，安全维度强制覆盖输入校验、鉴权越权、敏感信息三项
- 意见四级标准（Blocker / Major / Minor / Nit）与统一条目格式（级别 + 位置 + 问题 + 建议 + 状态）
- Blocker 清零与回炉判据表（未修回炉 P4、已修未复审不得交付、Major 确认不改需理由）
- 变更-用例映射表规范，变更点须与 P4 源码清单一一对齐
- 复审闭环四要素（复审对象 / 复审人角色 / 复审结论 / 轮次）
- 建议项落地方式（Fowler 坏味基线逐项结论 `P5-R1`、与 design.md 规格一致性核对 `P5-R2`）
- 只评不改机制：默认不动业务代码，修复由 `tri-impl` 执行；获授权直接修复须登记「本轮直接修复」区
- 与 P4 / P6 / `tri-review` 的三条关系边界说明（自检 vs 评审、核对 vs 测试结论、方法论复用 vs 门禁归属）
- 上游依赖检测两态（编排模式 / 引导安装，含改用 `tri-review` 的建议与「仅出评审报告」降级）
- 落盘 `.tribro/sdlc/<命名>/P5-code-review/review-report.md`，回炉覆盖更新且复审记录累积
- 配套 README.md 与 tests/tri-cr-full-testcases.md
