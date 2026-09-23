# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

## [1.1.2] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手项目整体架构可视化分析（tri-html）、代码级深度剖析（tri-code-analyzer）、清单问题的直接修复/编码（tri-coding/tri-fix）与意图识别（tri-intent），强化「审计清单生成」边界。

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

- 初版发布。tri-xxx 家族下游执行 skill，认领 I10 audit-checklist 子类。
- **四维审计方法论**：改动点 / 审查点 / 测试点 / 测试步骤，审查点与 tri-review Phase 1+2 对齐（详见 `references/audit-checklist-template.md`）。
- **三种 Git 输入模式**：暂存区（`git diff --cached`）/ 工作区（`git diff` + 未跟踪文件）/ commit id（`git diff <commit>..HEAD`），命令参考详见 `references/git-diff-commands.md`。
- **Git diff 解析器** `scripts/parse_git_diff.py`：按模式执行对应 git 命令 → 解析改动文件清单（路径/状态/增删行数）→ 解析改动函数清单（基于 hunk 头）→ 检测敏感文件 → 检测测试文件 → 输出 diff.json。零第三方依赖（仅 Python 标准库）。
- **Markdown checklist 组装器** `scripts/build_checklist.py`：读取 diff.json + template.json → 生成 Markdown 骨架 → 注入复选框（`- [ ]`）→ 注入严重程度标签（`[BLOCKER]`/`[MAJOR]`/`[MINOR]`，与 tri-review 对齐）→ 三级分组（维度/检查类别/检查项）→ 输出单文件 checklist。
- **双审批门**：门①审计范围确认 + 门②checklist 交付确认，禁跳门抢跑。
- **三态上游依赖检测**：A 快照模式 / A0 待识别 / B 引导安装 / C 降级模式。
- **敏感文件检测**：自动识别 .env / secret / key / credential / password / token 文件改动，门①提示用户关注。
- **与 tri-review 对齐**：审查点检查项与 tri-review Phase 1（规格合规）+ Phase 2（代码质量）维度对齐，支持「tri-checklist 生成清单 → 开发者自检 → tri-review 执行审查」串联工作流。
- **§3.13 代码版权与许可证合规**：四类风险（版权署名/许可证冲突/依赖供应链/标识披露）+ 提交前六项自检 + 底线声明。
- **完整配套**：README.md / CHANGELOG.md / tests/tri-checklist-full-testcases.md / references/×2 / scripts/×2。
