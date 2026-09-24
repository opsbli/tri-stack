# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-09-24

### 变更

- **落盘目录改名 `tri-jobhunt/` → `jobhunt/`**：求职物料与 legacy 追踪默认落 `.tribro/jobhunt/`（原 `.tribro/tri-jobhunt/`）；链路审计文档同步改为 `.tribro/forge/jobhunt/`。命名判据见 §1.4。**旧目录不自动迁移**。

## [1.0.3] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手意图识别、AI 业务代码生成、代码修复/审查与非求职场景通用内容创作，只做求职全流程路由分发。

## [1.0.2] - 2026-09-02

### 修复
- 6 个 children 子 skill SKILL.md 补「落盘」声明条款（2026-08-30 审计修复，此前未随版本发布），明确产物写入路径与不可覆盖既有文件约束。
- frontmatter version `1.0.1` -> `1.0.2`

## [1.0.1] - 2026-08-30

### 修复

- displayName 去除全角括号 slug 后缀（如「求职全流程路由（tri-jobhunt）」→「求职全流程路由」），
  同步修复 6 个 children 的 displayName；版本随发布要求联动升至 1.0.1。

## [1.0.0] - 2026-08-30

### 新增

- 初版锻造：tri-forge 依据《蒸馏分析报告-ResumeSkills-main.md》生成。
- 单入口主 skill `tri-jobhunt`：求职全流程路由，R1-R11 决策规则分发到 6 个 children 子 skill。
- 6 个 children 子 skill：tri-jd / tri-resume-core / tri-docs / tri-interview / tri-negotiate / tri-role。
- 共享 references 资源层：jobhunt-routes / quantification / ats-compliance / star-framework / role-branches。
- 版本检查门：自带 `scripts/check_update.py` + 版本检查章节（STUB 指向 version-check-spec.md）。
- 自带知识装配顺序（references 覆盖层）、完成判据（结束态/停车态）、进化契约。
- 不含任何参考技能版权/作者信息，仅含通用方法论与可执行规则。