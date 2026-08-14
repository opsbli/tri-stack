# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/spec/v2.0.0.html).

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
