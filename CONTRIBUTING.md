# 贡献指南

欢迎贡献 tri-stack 项目！本文档说明了如何参与贡献。

## 目录

- [提交 Issue](#提交-issue)
- [提交 Pull Request](#提交-pull-request)
- [开发规范](#开发规范)
- [Skill 开发标准](#skill-开发标准)
- [代码审查](#代码审查)

---

## 提交 Issue

### Bug 报告

使用 [Bug Report 模板](.github/ISSUE_TEMPLATE/bug_report.md) 提交，请提供：

- 问题描述（发生了什么，期望什么）
- 复现步骤
- 环境信息（AI 工具类型、版本等）
- 相关 skill 名称和版本

### 功能请求

使用 [Feature Request 模板](.github/ISSUE_TEMPLATE/feature_request.md) 提交，请提供：

- 功能描述
- 使用场景
- 期望行为

### 新 Skill 请求

使用 [Skill Request 模板](.github/ISSUE_TEMPLATE/skill_request.md) 提交，请提供：

- Skill 名称和职责描述
- 与现有 skill 的边界划分
- 触发条件和典型用例

---

## 提交 Pull Request

### 流程

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feat/your-feature-name`
3. 提交变更：遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范
4. 运行测试：确保所有已有测试通过
5. 提交 PR：使用 [PR 模板](.github/PULL_REQUEST_TEMPLATE.md)

### 分支命名

- `feat/<name>` — 新功能
- `fix/<name>` — 修复
- `docs/<name>` — 文档变更
- `refactor/<name>` — 重构
- `test/<name>` — 测试
- `chore/<name>` — 工具/配置变更

### 提交信息格式

```
<type>(<scope>): <简短描述>

<详细描述（可选）>
```

示例：

```
feat(tri-coding): 添加 TypeScript 模板支持

- 新增 ts-function 模板
- 更新 ts-class 模板的接口定义
```

---

## 开发规范

### 文件结构

每个 tri-xxx skill 必须包含以下文件：

```
tri-<name>/
├── SKILL.md          # Skill 定义（必须）
├── README.md         # 使用说明（必须）
├── CHANGELOG.md      # 变更记录（必须）
├── templates/        # 模板文件（推荐）
└── tests/            # 测试用例（必须）
```

### SKILL.md 规范

SKILL.md 必须包含以下章节（按顺序）：

1. 强制执行契约 — 前置条件、核心规则、最小化原则
2. 触发时机 — 何时激活该 skill
3. 上游依赖检测 — 依赖的三方 skill 或工具
4. 输入契约 — 接受的输入格式
5. 职责边界 — 明确负责和不负责的范围
6. 核心能力方法论 — 方法论原则和概览
7. 处理流程 — 带 ASCII 流程图和阶段速查表
8. 交付产物 — 产物规范和存储规则
9. 版本 — 版本号与兼容性说明

### 版本管理

- 使用语义化版本（SemVer）：`主版本.次版本.修订号`
- `+0.1.0` — 新增功能或依赖检测变更
- `+0.0.1` — 非功能性变更（文档、格式）
- 每次发布前需更新 `CHANGELOG.md`

---

## 代码审查

所有 PR 必须通过至少一位维护者的审查。审查重点：

- 是否符合 MECE 原则（职责互斥且穷尽）
- 是否遵循最小化原则（不超出任务范围）
- 是否是完整的接口契约、依赖检测、版本检查
- 测试用例是否覆盖核心路径

---

## 行为准则

请阅读并遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。