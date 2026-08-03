---
name: tech-git
description: Git版本管理规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Git 特定的版本控制标准与质量检查。
tech_id: git
tech_name: Git
category: tool
---

# Git 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Git 特定规范。

## 技术栈定义

Git 是分布式版本控制系统，通过暂存区（staging area）、分支与提交历史管理代码变更。核心特性：暂存区精细化控制、分支与合并策略、合并/变基（merge/rebase）、冲突解决、`.gitignore` 规范与 hooks 自动化。

## 编码规范（技术特定）

### 提交信息规范（Conventional Commits）

所有 Commit Message 必须遵循 [Conventional Commits](https://www.conventionalcommits.org/)。

**格式**：

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**Type（类型）**：

- `feat`：新功能
- `fix`：修复 Bug
- `docs`：文档变更
- `style`：格式调整（不影响运行）
- `refactor`：重构
- `perf`：性能优化
- `test`：测试变更
- `chore`：工具/构建/杂项
- `revert`：回滚
- `build`：构建系统或依赖变更
- `ci`：CI 配置变更

**Scope（范围，可选）**：用于说明影响范围（如 `auth`、`user`、`api`、`ui`）。

**Subject（主题）**：

- 简短明确（建议 ≤ 50 字符）
- 使用祈使句、现在时
- 首字母小写，结尾不加句号

**Body / Footer（可选）**：

- Body 说明动机与权衡
- Footer 标记破坏性变更或关联 issue（如 `Closes #123`）

**示例**：

```text
feat(auth): add login with google

Implement OAuth2 flow for Google login.

Closes #42
```

```text
fix(user): handle null pointer exception in profile view
```

### 提交粒度

- **原子提交**：一个提交只包含一个逻辑变更，避免把无关修改混在一起
- **变更可审计**：提交内容要可解释、可复现、可回滚
- **增量提交**：以"增量"方式提交可运行的代码，优先让每一步都可回滚、可验证

### 分支与历史

- **分支策略一致**：遵循项目既定分支策略（Git Flow/Trunk Based 等），不要引入第二套流程
- **历史即文档**：通过良好的提交粒度与信息表达，降低未来定位问题的成本
- **同步上游**：推送前同步远端，避免无意义的冲突与合并噪音
- **重写历史有边界**：仅在私有分支使用 `rebase`/`push --force-with-lease`，并遵循团队约定

### 暂存区与忽略

- **避免提交垃圾文件**：维护好 `.gitignore`，禁止提交编译产物、临时文件、IDE 配置等

### 绝对禁止

- 绕过提交钩子（如使用 `--no-verify`）
- 在受保护分支上强推（`push --force`）
- 提交无法编译或无法运行的代码

### 合并与变基

- **Merge vs Rebase 选择**：公共分支（main/release）合并使用 `--no-ff` merge 保留特性分支拓扑，私有特性分支同步上游使用 `rebase` 保持线性历史；禁止在已推送的共享分支上 rebase
- **Cherry-pick 定点移植**：跨分支移植单个提交使用 `git cherry-pick <sha>`，注意冲突解决与原 commit hash 变化；禁止用 cherry-pick 替代正常的分支合并流程

### 标签与版本

- **标签管理**：发布版本使用附注标签（`git tag -a v1.0.0 -m "release"`）而非轻量标签，标签命名遵循 SemVer（`vMAJOR.MINOR.PATCH`），正式发布用签名标签（`-s`）
- **Commit Message Body 规范**：Body 每行 ≤ 72 字符，说明"为什么"而非"做了什么"（代码已说明 what），关联 issue/PR 编号，破坏性变更在 Footer 用 `BREAKING CHANGE:` 标记

### Hooks 与子模块

- **Git Hooks 自动化**：在 `pre-commit`/`pre-push`/`commit-msg` 钩子中执行 lint、格式化、测试与提交信息校验，钩子脚本纳入版本库并通过 `core.hooksPath` 或 `husky`/`lefthook` 同步
- **Submodule 谨慎使用**：跨仓库复用独立子项目时使用 `git submodule`，明确子模块指针 commit；频繁联动的内部代码优先拆分为独立包通过包管理器依赖，避免 submodule 的复杂性
- **Git LFS 大文件**：二进制大文件（图片、视频、模型、二进制依赖）使用 `git lfs` 跟踪，避免仓库膨胀与 clone 缓慢；`.gitattributes` 中明确 LFS 过滤规则

### 临时保存与回溯

- **Stash 临时保存**：切换分支前用 `git stash`（命名 `stash push -m "msg"`）保存未完成工作，避免随意 commit 半成品；stash 不作为长期存储，定期清理
- **二分查找（bisect）定位回归**：出现回归时使用 `git bisect` 二分定位引入问题的提交，配合 `git bisect run` 自动执行测试脚本，快速锁定责任提交
- **Reflog 兜底恢复**：误删分支/误 reset 后通过 `git reflog` 找回历史 HEAD 指针，90 天内本地操作可恢复；理解 reflog 是本地私有历史，不随 push 同步

## 质量检查清单（技术特定）

- [ ] Commit Message 是否遵循 Conventional Commits 格式
- [ ] 提交是否为原子提交（一个提交一个逻辑变更）
- [ ] Subject 是否简短明确（≤ 50 字符，祈使句，首字母小写，无句号）
- [ ] 是否同步了远端再推送
- [ ] `rebase`/`push --force-with-lease` 是否仅用于私有分支
- [ ] `.gitignore` 是否覆盖了编译产物、临时文件、IDE 配置
- [ ] 是否未绕过提交钩子（无 `--no-verify`）
- [ ] 是否未在受保护分支强推

## 参考资料

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git 官方文档](https://git-scm.com/doc)
- [Pro Git Book（中文）](https://git-scm.com/book/zh/v2)
- [Gitignore 模板集合](https://github.com/github/gitignore)
