# 工作流 DSL Schema（workflow-dsl）

> 阶段 6 统一输出。所有工作流在输出前编译为声明式 DSL，作为可版本管理的单一事实来源（Single Source of Truth）。

## Schema 定义

```yaml
# <name>.wf.yml — 工作流声明式 DSL
# 由阶段 6 多目标输出编译生成，是所有交付形态的统一中间表示

dsl_version: "1.0.0"

# === 元信息 ===
meta:
  name: <工作流名称>
  slug: <kebab-case slug>
  version: <SemVer 版本号>
  description: <工作流描述>
  author: <作者>
  created_at: <创建时间>
  updated_at: <更新时间>

# === 触发配置 ===
trigger:
  type: <manual|schedule|event|webhook>
  schedule: <cron 表达式，type=schedule 时>
  event:
    source: <事件源标识>
    types: [<事件类型列表>]
  webhook:
    path: <webhook 路径>
    method: <POST|GET>

# === 环境变量 ===
env:
  - name: <变量名>
    value: <变量值或引用>
    secret: <true|false>  # 是否敏感信息

# === 工作流节点 ===
jobs:
  <job_id>:
    name: <job 显示名称>
    type: <auto|manual|approval|notification|condition|parallel>
    description: <job 描述>

    # 前置依赖
    needs: [<前置 job_id 列表>]

    # 执行条件
    if: <条件表达式，如 "always()"、"success()"、"failure()">

    # 执行角色
    runner:
      type: <skill|mcp|api|human>
      target: <具体目标>
      version: <版本约束>

    # 执行步骤
    steps:
      - id: <步骤 ID>
        name: <步骤名称>
        uses: <skill/mcp/api 引用>
        with:
          <参数名>: <参数值>
        timeout_minutes: <超时分钟数>
        retry:
          max_attempts: <最大重试>
          interval_seconds: <重试间隔秒>

    # 审批配置（type=approval 时）
    approval:
      approvers: [<审批人>]
      strategy: <any|all|sequence>
      auto_approve_after_hours: <自动通过小时数>

    # 通知配置（type=notification 时）
    notify:
      channel: <飞书|Slack|邮件>
      template: <通知模板引用>
      recipients: [<接收人>]

    # 输出
    outputs:
      <key>: <value>

# === 错误处理 ===
error_handling:
  strategy: <stop|continue|rollback>
  fallback_job: <兜底 job_id>
  notifications:
    on_failure: <true|false>
    recipients: [<接收人>]

# === 超时与并发 ===
limits:
  timeout_minutes: <全局超时分钟数>
  max_concurrency: <最大并发数>

# === 多目标输出映射 ===
outputs:
  - target: <skill|design-doc|ci-config|approval-template|dag-config>
    file: <输出文件路径>
    format: <yaml|json|markdown|yml>
    generated: <true|false>
```

## 编译规则

### 从 workflow-model.yml 到 workflow-dsl.yml

| workflow-model 字段 | workflow-dsl 字段 | 转换规则 |
|---|---|---|
| `nodes[].id` | `jobs.<job_id>` | 直接映射为 job ID |
| `nodes[].name` | `jobs.<job_id>.name` | 直接映射 |
| `nodes[].type` | `jobs.<job_id>.type` | 直接映射 |
| `nodes[].role` | `jobs.<job_id>.runner` | type+target 解构 |
| `nodes[].action` | `jobs.<job_id>.steps[].name` | 单步骤时直接映射 |
| `nodes[].inputs` | `jobs.<job_id>.steps[].with` | 参数平铺 |
| `nodes[].sla.timeout` | `jobs.<job_id>.steps[].timeout_minutes` | 单位转换 |
| `nodes[].retry` | `jobs.<job_id>.steps[].retry` | 直接映射 |
| `nodes[].depends_on` | `jobs.<job_id>.needs` | 直接映射 |
| `edges` | 隐含在 `needs` 和 `if` 中 | 条件边转 `if` 表达式 |
| `triggers` | `trigger` | 直接映射（model 和 dsl 统一使用 webhook 类型） |
| `global.error_handling` | `error_handling` | 直接映射 |

## 多目标输出映射

DSL 编译完成后，各输出后端从 DSL 提取对应字段生成目标格式：

| 目标格式 | 提取字段 | 生成器 |
|---|---|---|
| SKILL.md | meta + jobs + error_handling | `templates/output-backends/skill-output.md` |
| 设计文档 | 全部字段（人类可读） | `templates/output-backends/design-doc-output.md` |
| CI 配置 | trigger + jobs + env + limits | `templates/output-backends/ci-config-output.md` |
| 审批模板 | meta + approval jobs + notify | `templates/output-backends/approval-template-output.md` |
| DAG 配置 | jobs + needs + limits | 直接映射为 DAG 引擎配置 |