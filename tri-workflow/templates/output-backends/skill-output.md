# SKILL.md 输出后端规范

> 阶段 6 输出后端之一。将工作流 DSL 编译为可独立执行的 SKILL.md 文件。

## 生成规则

### 从 DSL 到 SKILL.md 的映射

| DSL 字段 | SKILL.md 字段 | 转换规则 |
|---|---|---|
| `meta.name` | `name` | 直接映射 |
| `meta.slug` | `slug` | 直接映射 |
| `meta.version` | `version` | 直接映射 |
| `meta.description` | `description` | 追加「由 tri-workflow 生成」 |
| `meta.*` | `summary` | 拼接 meta 字段为摘要 |
| `trigger` | 执行契约 §触发时机 | 描述触发条件 |
| `jobs` | 工作流步骤 | 每个 job 映射为一个执行步骤 |
| `error_handling` | 执行契约 §错误处理 | 描述错误处理策略 |
| `limits` | 执行契约 §约束 | 描述超时/并发限制 |

## 输出模板

```markdown
---
name: {{meta.name}}
slug: {{meta.slug}}
version: {{meta.version}}
displayName: {{meta.name}}
description: {{meta.description}}（由 tri-workflow 自动生成）
summary: {{meta.description}}
tags: [workflow, auto-generated]
license: MIT
---

# {{meta.name}}

> 本 Skill 由 tri-workflow 自动生成，基于工作流 DSL `{{meta.slug}}.wf.yml`。
> 生成时间：{{meta.created_at}}
> 最后更新：{{meta.updated_at}}

## 强制执行契约

1. **触发条件**：{{trigger.type}}
   - {{trigger_detail}}
2. **执行顺序**：按工作流步骤顺序执行，NEVER 跳过步骤
3. **错误处理**：{{error_handling.strategy}}
   - 失败时执行：{{error_handling.fallback_job}}
4. **超时限制**：全局超时 {{limits.timeout_minutes}} 分钟
5. **并发限制**：最大并发 {{limits.max_concurrency}}

## 工作流步骤

{# 遍历 jobs #}
### {{job_id}}. {{job.name}}

- **类型**：{{job.type}}
- **执行角色**：{{job.runner.type}} / {{job.runner.target}}
- **前置依赖**：{{job.needs | join(", ") | default("无")}}
- **执行条件**：{{job.if | default("always()")}}

#### 步骤详情

{# 遍历 job.steps #}
1. **{{step.name}}**
   - 使用：{{step.uses}}
   - 参数：{{step.with | yaml}}
   - 超时：{{step.timeout_minutes}} 分钟
   - 重试：最多 {{step.retry.max_attempts}} 次，间隔 {{step.retry.interval_seconds}} 秒

{# 若 job 有 approval #}
#### 审批配置

- 审批人：{{job.approval.approvers | join(", ")}}
- 策略：{{job.approval.strategy}}
- 自动通过：{{job.approval.auto_approve_after_hours}} 小时后

{# 若 job 有 notify #}
#### 通知配置

- 渠道：{{job.notify.channel}}
- 接收人：{{job.notify.recipients | join(", ")}}

## 错误处理

- **策略**：{{error_handling.strategy}}
- **兜底步骤**：{{error_handling.fallback_job}}
- **失败通知**：{{error_handling.notifications.on_failure | default(false)}}

## 质量标准

| 维度 | 标准 |
|---|---|
| 步骤完整性 | 所有步骤均可执行，无缺失依赖 |
| 错误处理 | 每个步骤有重试和超时配置 |
| 可观测性 | 关键步骤有日志输出 |

## 版本历史

| 版本 | 日期 | 变更说明 |
|---|---|---|
| {{meta.version}} | {{meta.created_at}} | 初始版本（由 tri-workflow 生成） |
```

## 生成约束

1. 生成的 SKILL.md 必须遵循 SKILL.md 标准格式（frontmatter + markdown body）
2. `name` 字段：使用 kebab-case，如 `ci-cd-pipeline`
3. `description` 和 `summary` 必须追加「由 tri-workflow 自动生成」标记
4. 工作流步骤按 `needs` 依赖排序输出
5. 若 job 的 `if` 条件为 `always()`，可省略不写
6. 生成的 SKILL.md 是骨架——节点内部的具体实现逻辑由 tri-coding 补充