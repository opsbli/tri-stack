# 工作流模型 Schema（workflow-model）

> 阶段 2-4 的中间产物。定义工作流的完整逻辑模型，从初版→完整版→优化版逐步演进。

## Schema 定义

```yaml
# workflow-model.yml — 工作流逻辑模型
# v1: 阶段 2 模板匹配产出（初版）
# v2: 阶段 3 对话补全产出（完整版）
# v3: 阶段 4 编译优化产出（优化版）

meta:
  workflow_name: <工作流名称，唯一标识>
  workflow_type: <ci-cd-pipeline|code-review-flow|approval-flow|data-pipeline|release-flow|multi-agent-orchestration|incident-response|custom>
  version: <模型版本，v1|v2|v3>
  template_id: <匹配到的模板 ID，自定义则填 custom>
  template_confidence: <匹配度 0-100>
  created_at: <创建时间>
  updated_at: <最后更新时间>

# === 触发配置 ===
triggers:
  type: <manual|schedule|event|webhook>
  detail: <触发条件详情>
  schedule:
    cron: <cron 表达式，type=schedule 时必填>
    timezone: <时区>
  event:
    source: <事件源，如 GitHub Push>
    filter: <事件过滤条件>
  webhook:
    path: <webhook 路径>
    method: <POST|GET>
    auth: <认证方式>

# === 节点定义 ===
nodes:
  - id: <唯一节点 ID，如 node_01>
    name: <节点显示名称>
    type: <auto|manual|approval|notification|condition|parallel|gateway>
    description: <节点功能描述>

    # 执行角色（BPMN 五要素之一）
    role:
      type: <skill|mcp|api|human|system>
      target: <具体目标名称，如 tri-coding / lark-im / 张三>
      version: <若 type=skill，标注版本要求>

    # 动作（BPMN 五要素之二）
    action: <节点执行的具体动作描述>

    # 输入（BPMN 五要素之三）
    inputs:
      - name: <输入名称>
        type: <string|number|boolean|object|array|file>
        source: <数据来源，如 node_01.outputs.result>
        required: <true|false>
        default: <默认值>

    # 输出（BPMN 五要素之四）
    outputs:
      - name: <输出名称>
        type: <string|number|boolean|object|array|file>
        description: <输出描述>

    # SLA（BPMN 五要素之五）
    sla:
      expected_duration: <预期耗时，如 5m>
      timeout: <超时时间，如 10m>
      unit: <s|m|h>

    # 容错配置
    retry:
      max_attempts: <最大重试次数，默认 3>
      interval: <重试间隔，默认 30s>
      backoff: <fixed|exponential>
      on_failure: <skip|abort|fallback>

    # 前置依赖
    depends_on: [<前置节点 ID 列表>]

    # 分支条件（type=condition 时）
    conditions:
      - expression: <条件表达式>
        target_node: <满足条件时跳转的目标节点 ID>

    # 审批配置（type=approval 时）
    approval:
      approvers: [<审批人列表>]
      strategy: <any|all|sequence>  # 任一人/所有人/按顺序
      auto_approve_after: <自动通过时限，如 24h>

    # 通知配置（type=notification 时）
    notification:
      channel: <飞书|Slack|邮件|企业微信>
      template: <通知模板>
      recipients: [<接收人列表>]

# === 边（转移）定义 ===
edges:
  - id: <边 ID>
    from: <源节点 ID>
    to: <目标节点 ID>
    condition: <转移条件，无条件则填 always>
    label: <边的显示标签>

# === 全局配置 ===
global:
  error_handling:
    strategy: <stop|skip|retry|fallback>
    fallback_node: <全局兜底节点 ID>
  notifications:
    on_start: <true|false>
    on_complete: <true|false>
    on_failure: <true|false>
  logging:
    level: <debug|info|warn|error>
    retention: <日志保留天数>
```

## 节点类型规范

| 类型 | 说明 | 必填字段 | 可选字段 |
|---|---|---|---|
| `auto` | 自动执行节点（由 Skill/MCP/API 执行） | role, action, inputs, outputs | retry, sla |
| `manual` | 人工操作节点 | name, action, depends_on | sla |
| `approval` | 审批节点 | name, approval | sla |
| `notification` | 通知节点 | name, notification | — |
| `condition` | 条件分支节点 | name, conditions | — |
| `parallel` | 并行网关节点 | name | — |
| `gateway` | 排他/包容网关 | name, conditions | — |

## 模型演进规则

### v1 → v2（对话补全）

- 补全所有 `action` 为空或模糊的节点
- 为所有 `auto` 节点映射 `role.target`
- 补全所有 `inputs` 的 `source` 字段
- 为所有 `approval` 节点设定 `approval.approvers`

### v2 → v3（编译优化）

- 合并连续同类型自动节点
- 标记无依赖节点为并行
- 注入默认超时和重试配置
- 记录优化变更日志