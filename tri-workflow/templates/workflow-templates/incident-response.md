# 故障响应流程模板

> 模板 ID：`incident-response`
> 适用场景：告警 → 诊断 → 修复 → 复盘
> 核心节点：告警触发 → 影响评估 → 诊断定位 → 修复执行 → 验证 → 复盘报告

## 模板定义

```yaml
workflow_name: <服务名>-incident-response
workflow_type: incident-response
template_id: incident-response
template_confidence: 100

nodes:
  - id: alert_trigger
    name: 告警触发
    type: auto
    role: { type: api, target: <监控系统> }
    action: 接收监控告警
    inputs: []
    outputs:
      - { name: alert_info, type: object, description: 告警信息（服务/指标/时间/严重级别） }
      - { name: severity, type: string, description: P0|P1|P2|P3 }
    depends_on: []

  - id: severity_check
    name: 严重级别判断
    type: condition
    conditions:
      - { expression: "severity == 'P0'", target_node: notify_oncall }
      - { expression: "severity == 'P1'", target_node: impact_assess }
      - { expression: "severity in ['P2','P3']", target_node: create_ticket }
    depends_on: [alert_trigger]

  - id: notify_oncall
    name: 紧急通知（电话/加急）
    type: notification
    notification:
      channel: 飞书
      template: incident-p0-alert
      recipients: [<值班人>, <技术负责人>]
    depends_on: [severity_check]

  - id: impact_assess
    name: 影响评估
    type: auto
    role: { type: system, target: <监控系统> }
    action: 评估故障影响范围（用户数/业务损失/受影响服务）
    inputs:
      - { name: alert_info, type: object, source: alert_trigger.outputs.alert_info, required: true }
    outputs:
      - { name: impact_report, type: object, description: 影响评估报告 }
    sla: { expected_duration: 5m, timeout: 10m, unit: m }
    depends_on: [severity_check]

  - id: diagnose
    name: 诊断定位
    type: auto
    role: { type: skill, target: tri-fix, version: ">=1.0.0" }
    action: 分析日志/指标/链路追踪，定位根因
    inputs:
      - { name: alert_info, type: object, source: alert_trigger.outputs.alert_info, required: true }
      - { name: impact_report, type: object, source: impact_assess.outputs.impact_report, required: true }
    outputs:
      - { name: root_cause, type: object, description: 根因分析结果 }
      - { name: confidence, type: number, description: 诊断置信度 0-100 }
    sla: { expected_duration: 10m, timeout: 30m, unit: m }
    depends_on: [impact_assess]

  - id: fix_execute
    name: 修复执行
    type: auto
    role: { type: skill, target: tri-fix, version: ">=1.0.0" }
    action: 执行修复操作（回滚/热修复/扩容/配置变更）
    inputs:
      - { name: root_cause, type: object, source: diagnose.outputs.root_cause, required: true }
    outputs:
      - { name: fix_result, type: object, description: 修复结果 }
    sla: { expected_duration: 10m, timeout: 30m, unit: m }
    retry: { max_attempts: 2, interval: 60s, backoff: fixed, on_failure: escalate }
    depends_on: [diagnose]

  - id: verify
    name: 修复验证
    type: auto
    role: { type: api, target: <监控系统> }
    action: 验证服务恢复（错误率/延迟/可用性）
    inputs:
      - { name: alert_info, type: object, source: alert_trigger.outputs.alert_info, required: true }
    outputs:
      - { name: recovered, type: boolean, description: 是否恢复 }
      - { name: verify_detail, type: object, description: 验证详情 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    depends_on: [fix_execute]

  - id: recovery_check
    name: 恢复判断
    type: condition
    conditions:
      - { expression: "recovered == true", target_node: notify_recovered }
      - { expression: "recovered == false", target_node: escalate }
    depends_on: [verify]

  - id: escalate
    name: 升级处理
    type: notification
    notification:
      channel: 飞书
      template: incident-escalate
      recipients: [<技术总监>, <值班经理>]
    depends_on: [recovery_check]

  - id: notify_recovered
    name: 恢复通知
    type: notification
    notification:
      channel: 飞书
      template: incident-recovered
      recipients: [<团队群>, <受影响方>]
    depends_on: [recovery_check]

  - id: create_ticket
    name: 创建工单
    type: auto
    role: { type: api, target: <工单系统> }
    action: 创建故障工单，记录全过程
    inputs:
      - { name: alert_info, type: object, source: alert_trigger.outputs.alert_info, required: true }
    outputs:
      - { name: ticket_id, type: string, description: 工单 ID }
    depends_on: [severity_check]

  - id: postmortem
    name: 复盘报告
    type: auto
    role: { type: skill, target: tri-content }
    action: 生成故障复盘报告（5 Why / 时间线 / 改进措施）
    inputs:
      - { name: alert_info, type: object, source: alert_trigger.outputs.alert_info, required: true }
      - { name: root_cause, type: object, source: diagnose.outputs.root_cause, required: true }
      - { name: fix_result, type: object, source: fix_execute.outputs.fix_result, required: true }
    outputs:
      - { name: postmortem_doc, type: file, description: 复盘报告 }
    sla: { expected_duration: 30m, timeout: 2h, unit: h }
    depends_on: [notify_recovered]

  - id: close_ticket
    name: 关闭工单
    type: auto
    role: { type: api, target: <工单系统> }
    action: 关闭 P2/P3 工单并记录处理结果
    inputs:
      - { name: ticket_id, type: string, source: create_ticket.outputs.ticket_id, required: true }
      - { name: alert_info, type: object, source: alert_trigger.outputs.alert_info, required: true }
    outputs:
      - { name: close_result, type: object, description: 工单关闭结果 }
    sla: { expected_duration: 1m, timeout: 5m, unit: m }
    depends_on: [create_ticket]

  - id: archive
    name: 归档
    type: auto
    role: { type: system, target: <知识库> }
    action: 将复盘报告归档到知识库
    inputs:
      - { name: postmortem_doc, type: file, source: postmortem.outputs.postmortem_doc, required: true }
    outputs:
      - { name: archive_url, type: string, description: 归档链接 }
    depends_on: [postmortem]

edges:
  - { from: alert_trigger, to: severity_check, condition: always }
  - { from: severity_check, to: notify_oncall, condition: "severity == 'P0'" }
  - { from: severity_check, to: impact_assess, condition: "severity == 'P1'" }
  - { from: severity_check, to: create_ticket, condition: "severity in ['P2','P3']" }
  - { from: notify_oncall, to: impact_assess, condition: always }
  - { from: impact_assess, to: diagnose, condition: always }
  - { from: diagnose, to: fix_execute, condition: always }
  - { from: fix_execute, to: verify, condition: always }
  - { from: verify, to: recovery_check, condition: always }
  - { from: recovery_check, to: notify_recovered, condition: "recovered == true" }
  - { from: recovery_check, to: escalate, condition: "recovered == false" }
  - { from: notify_recovered, to: postmortem, condition: always }
  - { from: create_ticket, to: close_ticket, condition: always }
  - { from: postmortem, to: archive, condition: always }

triggers:
  type: event
  detail: 监控告警触发时自动启动

global:
  error_handling:
    strategy: escalate
  notifications:
    on_start: true
    on_complete: true
    on_failure: true
  logging:
    level: debug
    retention: 90
```

## 可定制参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| 服务名 | — | 必填 |
| 监控系统 | — | 告警来源 |
| P0 响应人 | 值班人 | 7x24 值班人员 |
| 升级链 | 技术总监 | 升级通知链 |
| 工单系统 | — | 工单/ITSM 系统 |
| 复盘模板 | 5 Why | 复盘分析方法 |