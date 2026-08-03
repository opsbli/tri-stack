---
name: tech-gitflow
description: Git Flow分支管理规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Git Flow 特定的分支策略与质量检查。
tech_id: gitflow
tech_name: Git Flow
category: tool
---

# Git Flow 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Git Flow 特定规范。

## 技术栈定义

Git Flow 是基于 Git 的分支管理模型，通过 main/develop 双主干与 feature/release/hotfix/bugfix 辅助分支的职责划分，隔离功能开发、发布准备与热修复，确保历史可追踪、回滚成本可控。核心特性：分支职责清晰、命名约定统一、合并路径可预测、版本标签管理。

## 编码规范（技术特定）

### 分支模型

**核心分支**：

- **main（或 master）**：可发布分支，随时可部署到生产环境
- **develop**：集成分支，承载下一版本的集成成果

**辅助分支**：

- **feature/**：从 `develop` 切出，完成后合并回 `develop`
- **release/**：从 `develop` 切出，发布完成后合并回 `main` 与 `develop` 并打 Tag
- **hotfix/**：从 `main` 切出，紧急修复生产问题，完成后回灌 `main` 与 `develop`
- **bugfix/**：从 `develop` 切出，修复开发阶段问题，完成后合并回 `develop`

### 分支命名

- **命名可读**：分支命名体现目的与范围（feature/release/hotfix/bugfix），必要时带 issue 标识

### 工作流规则

1. **开发新功能**：从 `develop` 切 `feature/*`，开发完成后 PR 到 `develop`
2. **版本发布**：从 `develop` 切 `release/*`，冻结功能、只修复与准备版本，完成后合并到 `main` 与 `develop` 并打 Tag
3. **紧急修复**：从 `main` 切 `hotfix/*`，修复后合并回 `main` 与 `develop` 并打 Tag

### 合并规则

- **合并路径可预测**：合并规则固定，避免"随手合并"导致历史不可追踪
- **合并前自检**：发起 PR 前解决冲突并确保测试通过，避免把风险转移给集成阶段
- **强制评审**：合并到 `develop`/`main` 的变更必须经过 Code Review
- **保护主分支**：`main/master` 禁止直接 Push，只能通过 PR 合并并有审查

### 发布与热修复

- **发布可控**：发布前通过 release 分支冻结功能，只处理修复与版本准备
- **热修复独立**：生产问题走 hotfix 分支，修复后回灌到 main 与 develop，保持一致性

### PR 规范

- **PR 描述完整**：PR 描述必须包含变更内容与验证方式（UI 变更附截图/录屏按项目约定）

### 绝对禁止

- 在 `main/master` 直接 Push
- 绕过提交钩子（如使用 `--no-verify`）
- 在共享分支强推（`push --force`）

### 版本与标签管理

- **语义化版本**：版本号遵循 `MAJOR.MINOR.PATCH`（SemVer），MAJOR 为不兼容变更、MINOR 为向后兼容新增功能、PATCH 为修复；release 分支命名应与目标版本号一致（如 `release/1.2.0`），便于追溯发布目标
- **Tag 规范**：在 `main` 合并时打 Tag，Tag 命名 `v<版本号>`（如 `v1.2.0`），Tag 提交信息包含版本说明与变更摘要；禁止在非 `main` 分支打正式版本 Tag，避免产生未被验证的版本标记
- **热修复版本递增**：hotfix 完成后版本号递增 PATCH（如 `v1.2.0` → `v1.2.1`），hotfix 分支命名体现目标版本（如 `hotfix/1.2.1`），修复后回灌 `main` 与 `develop` 并同步打 Tag

### 分支生命周期

- **分支及时清理**：合并完成的 feature/bugfix/release/hotfix 分支及时删除（本地与远端），避免分支堆积干扰选支；仅保留活跃开发分支与必要的长期分支
- **长期分支对齐**：develop 与 main 长期共存时，定期将 main 的 hotfix 回灌同步到 develop，避免两条主干长期分叉导致合并冲突累积

## 质量检查清单（技术特定）

- [ ] feature 分支是否从 `develop` 切出并合并回 `develop`
- [ ] release 分支是否从 `develop` 切出，完成后合并到 `main` 与 `develop` 并打 Tag
- [ ] hotfix 分支是否从 `main` 切出，修复后回灌 `main` 与 `develop`
- [ ] 分支命名是否体现目的与范围（feature/release/hotfix/bugfix）
- [ ] `main/master` 是否禁止直接 Push（仅通过 PR 合并）
- [ ] 合并到 `develop`/`main` 是否经过 Code Review
- [ ] PR 前是否已解决冲突并通过测试
- [ ] PR 描述是否包含变更内容与验证方式
- [ ] 是否未在共享分支强推（`push --force`）

## 参考资料

- [A successful Git branching model（Vincent Driessen 原文）](https://nvie.com/posts/a-successful-git-branching-model/)
- [Git Flow 扩展工具](https://github.com/nvie/gitflow)
- [Pro Git Book - 分支工作流](https://git-scm.com/book/zh/v2/Git-分支-分支工作流)
