# 业务审批流模板

> 模板 ID：`approval-flow`
> 适用场景：申请 → 多级审批 → 执行 → 归档
> 核心节点：发起申请 → 一级审批 → 二级审批 → 执行 → 通知 → 归档

## 模板定义

```yaml
workflow_name: <业务名>-approval
workflow_type: approval-flow
template_id: approval-flow
template_confidence: 100

nodes:
  - id: submit_request
    name: 发起申请
    type: manual
    action: 申请人填写申请表单并提交
    inputs: []
    outputs:
      - { name: request_form, type: object, description: 申请表单 }
    sla: { expected_duration: 10m, timeout: 1h, unit: h }
    depends_on: []

  - id: first_approval
    name: 一级审批（直属上级）
    type: approval
    action: 直属上级审批
    inputs:
      - { name: request_form, type: object, source: submit_request.outputs.request_form, required: true }
    outputs:
      - { name: first_approval_result, type: boolean, description: 审批结果 }
      - { name: first_approval_comment, type: string, description: 审批意见 }
    approval:
      approvers: [<直属上级>]
      strategy: any
      auto_approve_after: 48h
    sla: { expected_duration: 4h, timeout: 48h, unit: h }
    depends_on: [submit_request]

  - id: first_result_check
    name: 一级审批结果判断
    type: condition
    conditions:
      - { expression: "first_approval_result == true", target_node: second_approval }
      - { expression: "first_approval_result == false", target_node: notify_first_reject }
    depends_on: [first_approval]

  - id: second_approval
    name: 二级审批（部门负责人）
    type: approval
    action: 部门负责人审批
    inputs:
      - { name: request_form, type: object, source: submit_request.outputs.request_form, required: true }
      - { name: first_comment, type: string, source: first_approval.outputs.first_approval_comment, required: false }
    outputs:
      - { name: second_approval_result, type: boolean, description: 审批结果 }
    approval:
      approvers: [<部门负责人>]
      strategy: any
      auto_approve_after: 72h
    sla: { expected_duration: 8h, timeout: 72h, unit: h }
    depends_on: [first_result_check]

  - id: second_result_check
    name: 二级审批结果判断
    type: condition
    conditions:
      - { expression: "second_approval_result == true", target_node: execute_action }
      - { expression: "second_approval_result == false", target_node: notify_second_reject }
    depends_on: [second_approval]

  - id: notify_first_reject
    name: 一级驳回通知
    type: notification
    notification:
      channel: 飞书
      template: approval-rejected
      recipients: [<申请人>]
    depends_on: [first_result_check]

  - id: notify_second_reject
    name: 二级驳回通知
    type: notification
    notification:
      channel: 飞书
      template: approval-rejected
      recipients: [<申请人>]
    depends_on: [second_result_check]

  - id: execute_action
    name: 执行审批事项
    type: auto
    role: { type: system, target: <执行系统> }
    action: 执行审批通过后的具体事项
    inputs:
      - { name: request_form, type: object, source: submit_request.outputs.request_form, required: true }
    outputs:
      - { name: execute_result, type: object, description: 执行结果 }
    sla: { expected_duration: 10m, timeout: 1h, unit: h }
    retry: { max_attempts: 3, interval: 60s, backoff: exponential, on_failure: abort }
    depends_on: [second_result_check]

  - id: notify_approve
    name: 通过通知
    type: notification
    notification:
      channel: 飞书
      template: approval-approved
      recipients: [<申请人>, <执行人>]
    depends_on: [execute_action]

  - id: archive
    name: 归档
    type: auto
    role: { type: system, target: <归档系统> }
    action: 将审批记录归档
    inputs:
      - { name: request_form, type: object, source: submit_request.outputs.request_form, required: true }
      - { name: execute_result, type: object, source: execute_action.outputs.execute_result, required: true }
    outputs:
      - { name: archive_id, type: string, description: 归档记录 ID }
    sla: { expected_duration: 1m, timeout: 5m, unit: m }
    depends_on: [notify_approve]

edges:
  - { from: submit_request, to: first_approval, condition: always }
  - { from: first_approval, to: first_result_check, condition: always }
  - { from: first_result_check, to: second_approval, condition: "first_approval_result == true" }
  - { from: first_result_check, to: notify_first_reject, condition: "first_approval_result == false" }
  - { from: second_approval, to: second_result_check, condition: always }
  - { from: second_result_check, to: execute_action, condition: "second_approval_result == true" }
  - { from: second_result_check, to: notify_second_reject, condition: "second_approval_result == false" }
  - { from: execute_action, to: notify_approve, condition: always }
  - { from: notify_approve, to: archive, condition: always }

triggers:
  type: manual
  detail: 申请人手动发起

global:
  error_handling:
    strategy: stop
  notifications:
    on_start: false
    on_complete: false
    on_failure: true
  logging:
    level: info
    retention: 90
```

## 可定制参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| 业务名 | — | 必填，审批流名称 |
| 审批级数 | 2 | 1-4 级审批 |
| 一级审批人 | 直属上级 | 可指定具体人或角色 |
| 二级审批人 | 部门负责人 | 可指定具体人或角色 |
| 审批策略 | any | any（任一人）/ all（所有人）/ sequence（按顺序） |
| 自动通过时限 | 48h / 72h | 各级审批超时自动通过时间 |
| 执行动作 | 系统操作 | 审批通过后自动执行的动作 |
| 通知渠道 | 飞书 | 飞书/钉钉/企业微信 |
| 归档保留 | 90 天 | 审批记录保留天数 |