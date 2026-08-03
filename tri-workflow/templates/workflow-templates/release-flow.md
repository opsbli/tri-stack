# 发布流水线模板

> 模板 ID：`release-flow`
> 适用场景：版本发布 → 灰度 → 全量 → 监控
> 核心节点：版本打包 → 灰度发布 → 监控观察 → 全量发布 → 通知 → 回滚预案

## 模板定义

```yaml
workflow_name: <项目名>-release
workflow_type: release-flow
template_id: release-flow
template_confidence: 100

nodes:
  - id: version_package
    name: 版本打包
    type: auto
    role: { type: system, target: docker/npm }
    action: 构建发布版本并打标签
    inputs: []
    outputs:
      - { name: release_artifact, type: file, description: 发布产物 }
      - { name: release_version, type: string, description: 版本号 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    depends_on: []

  - id: pre_release_check
    name: 发布前检查
    type: auto
    role: { type: system, target: validator }
    action: 检查发布清单（测试通过/文档更新/变更日志）
    inputs:
      - { name: release_version, type: string, source: version_package.outputs.release_version, required: true }
    outputs:
      - { name: checklist_passed, type: boolean, description: 清单是否全部通过 }
      - { name: checklist_detail, type: object, description: 清单详情 }
    sla: { expected_duration: 2m, timeout: 5m, unit: m }
    depends_on: [version_package]

  - id: checklist_decision
    name: 清单检查判断
    type: condition
    conditions:
      - { expression: "checklist_passed == true", target_node: canary_deploy }
      - { expression: "checklist_passed == false", target_node: notify_blocked }
    depends_on: [pre_release_check]

  - id: notify_blocked
    name: 阻断通知
    type: notification
    notification:
      channel: 飞书
      template: release-blocked
      recipients: [<发布负责人>]
    depends_on: [checklist_decision]

  - id: canary_deploy
    name: 灰度发布
    type: auto
    role: { type: system, target: docker/k8s }
    action: 发布到灰度环境（10% 流量）
    inputs:
      - { name: release_artifact, type: file, source: version_package.outputs.release_artifact, required: true }
    outputs:
      - { name: canary_url, type: string, description: 灰度环境 URL }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    retry: { max_attempts: 2, interval: 60s, backoff: fixed, on_failure: rollback }
    depends_on: [checklist_decision]

  - id: monitor_canary
    name: 灰度监控观察
    type: auto
    role: { type: api, target: <监控系统> }
    action: 观察灰度环境 30 分钟，监控错误率/延迟/资源使用
    inputs:
      - { name: canary_url, type: string, source: canary_deploy.outputs.canary_url, required: true }
    outputs:
      - { name: monitor_result, type: object, description: 监控指标 }
      - { name: canary_healthy, type: boolean, description: 灰度是否健康 }
    sla: { expected_duration: 30m, timeout: 60m, unit: m }
    depends_on: [canary_deploy]

  - id: canary_decision
    name: 灰度结果判断
    type: condition
    conditions:
      - { expression: "canary_healthy == true", target_node: full_deploy }
      - { expression: "canary_healthy == false", target_node: rollback }
    depends_on: [monitor_canary]

  - id: full_deploy
    name: 全量发布
    type: auto
    role: { type: system, target: docker/k8s }
    action: 全量发布到所有生产节点
    inputs:
      - { name: release_artifact, type: file, source: version_package.outputs.release_artifact, required: true }
    outputs:
      - { name: deploy_result, type: object, description: 全量发布结果 }
    sla: { expected_duration: 10m, timeout: 30m, unit: m }
    depends_on: [canary_decision]

  - id: post_deploy_check
    name: 发布后验证
    type: auto
    role: { type: system, target: curl/monitor }
    action: 验证全量发布后的服务健康状态
    inputs:
      - { name: deploy_result, type: object, source: full_deploy.outputs.deploy_result, required: true }
    outputs:
      - { name: health_status, type: boolean, description: 服务是否健康 }
    sla: { expected_duration: 5m, timeout: 10m, unit: m }
    depends_on: [full_deploy]

  - id: notify_success
    name: 发布成功通知
    type: notification
    notification:
      channel: 飞书
      template: release-success
      recipients: [<团队群>]
    depends_on: [post_deploy_check]

  - id: rollback
    name: 回滚
    type: auto
    role: { type: system, target: docker/k8s }
    action: 回滚到上一个稳定版本
    inputs:
      - { name: release_artifact, type: file, source: version_package.outputs.release_artifact, required: true }
      - { name: release_version, type: string, source: version_package.outputs.release_version, required: true }
    outputs:
      - { name: rollback_result, type: object, description: 回滚结果 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    depends_on: [canary_decision]

  - id: notify_rollback
    name: 回滚通知
    type: notification
    notification:
      channel: 飞书
      template: release-rollback
      recipients: [<团队群>, <发布负责人>]
    depends_on: [rollback]

edges:
  - { from: version_package, to: pre_release_check, condition: always }
  - { from: pre_release_check, to: checklist_decision, condition: always }
  - { from: checklist_decision, to: canary_deploy, condition: "checklist_passed == true" }
  - { from: checklist_decision, to: notify_blocked, condition: "checklist_passed == false" }
  - { from: canary_deploy, to: monitor_canary, condition: always }
  - { from: monitor_canary, to: canary_decision, condition: always }
  - { from: canary_decision, to: full_deploy, condition: "canary_healthy == true" }
  - { from: canary_decision, to: rollback, condition: "canary_healthy == false" }
  - { from: full_deploy, to: post_deploy_check, condition: always }
  - { from: post_deploy_check, to: notify_success, condition: always }
  - { from: rollback, to: notify_rollback, condition: always }

triggers:
  type: manual
  detail: 发布负责人手动触发

global:
  error_handling:
    strategy: rollback
  notifications:
    on_start: true
    on_complete: true
    on_failure: true
  logging:
    level: info
    retention: 90
```

## 可定制参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| 项目名 | — | 必填 |
| 灰度比例 | 10% | 灰度流量百分比 |
| 灰度观察时间 | 30min | 灰度环境观察时长 |
| 发布清单 | 测试/文档/日志 | 发布前检查项 |
| 部署平台 | docker/k8s | 部署目标 |