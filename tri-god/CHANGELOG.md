# Changelog

本项目所有值得记录的变更均记录于此文件。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本 SemVer](https://semver.org/lang/zh-CN/)。

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

- frontmatter version `1.0.1` → `1.1.0`

## [1.0.1] - 2026-08-01

### 修复

#### 目录结构图清理（合规）
- 删除 SKILL.md「目录结构 / 配套文件」中列出的 `LICENSE` / `.gitignore` 条目，遵循《tri-skill-规范与生成指南》§4.1「禁止生成的文件」硬约束（许可证仅由 frontmatter `license` 字段声明，忽略策略由仓库统一管控）。
- 本版本无功能变更，仅文档合规修正（PATCH）。

## [1.0.0] - 2026-07-31

### Added

- 主 `SKILL.md`：蒸馏元 skill 路由框架，含强制执行契约、触发时机、输入契约、职责边界、处理流程与交付产物定义
- `methodologies/registry.md`：方法论注册表（唯一注册入口），定义「蒸馏对象类型 → 方法论文件」映射及扩展指南
- 5 个蒸馏方法论文件：
  - `distill-human.md`：蒸馏人类思维/表达/决策方式
  - `distill-workflow.md`：蒸馏可复用工作流/流程/SOP
  - `distill-skill.md`：蒸馏专业技能/手艺/方法
  - `distill-thing.md`：蒸馏书/视频/课程等长内容知识框架
  - `distill-general.md`：通用兜底方法论
- 三态上游依赖检测（模式 A 快照 / B 引导安装 / C 降级），支持独立安装并与 tri-intent 集成
- 双审批门 + 执行前确认流程（门①需求 → 门②设计 → 门③执行前确认 → 执行 → 报告）
- 配套文件：`README.md`、`CHANGELOG.md`、`.gitignore`
- 测试用例：`tests/tri-god-full-testcases.md`，覆盖全部能力点
