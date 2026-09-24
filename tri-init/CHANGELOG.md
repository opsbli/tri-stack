# 变更日志

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

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
