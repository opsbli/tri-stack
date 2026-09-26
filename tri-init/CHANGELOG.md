# 变更日志

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [1.0.4] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.0.3] - 2026-09-25

### 新增

- **AGENTS.md 模板新增「通用编码行为规则（8 条）」章节**：最简实现 / 分层成长 / 先用已有依赖等 8 条写码纪律（第 1 条采用兼容安全版），与项目特定编码规范正交；配套测试用例 T31。来源：社区 600 亿 token 实践总结（2026-09 收录）。

## [1.0.2] - 2026-09-24

### 变更

- **版本门节统一为 `version-stub v1` 形态**：`## 版本检查与更新机制` 收敛为 14 行（执行方式 + 真源指针）。原节为 12 行并**内联了四态判定 / 退出码语义**，违反 `references/version-check-spec.md` §六「≤30 行、禁内联细则」；细则唯一真源为该 spec，行为不变。
- 非功能性变更（文档口径），无行为变更。

## [1.0.1] - 2026-09-24

### 变更

- **AGENTS.md 模板工具链表更新**：`skills-install.py`（平台取包器，已移除）替换为 `install-skills.py`（junction 安装到 AI 工具）。

## [1.0.0] - 2026-09-24

### 新增

- **首版发布**：项目初始化 skill——扫描技术栈 → 生成 AGENTS.md + project-profile → 创建 .tribro/
- 技术栈检测规则表（Java/Maven/Spring Boot/RuoYi/TS/Vite/Vue/React/Go/Python）
- 代码生成器规范提取（RuoYi 租户字段 / 审计字段 / 逻辑删除字段）
- project-scan.py 项目扫描脚本（确定性逻辑）
- AGENTS.md / project-profile.json 模板
- 测试用例
