# 变更日志

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [1.1.1] - 2026-09-28

### 新增

- **家族横切第 10 节「宿主兼容与提问呈现」**：紧跟「版本检查与更新机制」追加 `host-compat-stub v1` 自包含瘦节——
  在提供交互式提问工具的宿主（如 Proma 的 `AskUserQuestion`）中，🔴 STOP 用户确认检查点与 clarify-gate
  MUST 以**普通 Markdown 文本**呈现为聊天问题，**NEVER 调用交互式提问工具**
  （`AskUserQuestion` / `ask_user_question` / `request_user_input` / `clarify` 及等价物）；
  用户回复契约（逐条补充 / 按默认 / 继续 / 是·否）保持不变。
  **只管呈现形式，不改任何门控的判定条件、触发时机与处置动作**；在无交互式提问工具的宿主中本条自然空转。
  细则真源 `tri-intent/references/host-compat.md`；家族规范登记于 `tri-forge/references/family-spec.md`
  §四（第 10 节注）+ §五（待登记项）。

## [1.1.0] - 2026-09-28

### 变更

- **AGENTS.md 模板 ⭐ 强制规则区补两条**：① 每完成一个里程碑（功能可用 + 测试通过）MUST `git commit`，禁止把大量变更长期悬空在工作区；② 沙箱/环境降级（如 bun 缺失、electron postinstall 跳过）MUST 在 `delivery-manifest.md` 中列明并提示用户复验，NEVER 静默降级（审计 #8）。

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
