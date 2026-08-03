# CI/CD 持续集成流水线模板

> 模板 ID：`ci-cd-pipeline`
> 适用场景：代码提交 → 自动构建 → 测试 → 部署
> 核心节点：代码检出 → 静态检查 → 构建 → 单元测试 → 集成测试 → 部署 → 通知

## 模板定义

```yaml
workflow_name: <项目名>-ci-cd-pipeline
workflow_type: ci-cd-pipeline
template_id: ci-cd-pipeline
template_confidence: 100

nodes:
  - id: checkout
    name: 代码检出
    type: auto
    role: { type: system, target: git }
    action: 从仓库拉取最新代码
    inputs: []
    outputs: [{ name: source_code, type: directory, description: 源代码目录 }]
    sla: { expected_duration: 30s, timeout: 2m, unit: m }
    retry: { max_attempts: 3, interval: 30s, backoff: fixed, on_failure: abort }
    depends_on: []

  - id: static_check
    name: 静态代码检查
    type: auto
    role: { type: skill, target: tri-review, version: ">=1.0.0" }
    action: 运行代码规范检查和安全扫描
    inputs:
      - { name: source_code, type: directory, source: checkout.outputs.source_code, required: true }
    outputs:
      - { name: check_result, type: object, description: 检查结果报告 }
      - { name: check_passed, type: boolean, description: 是否通过 }
    sla: { expected_duration: 3m, timeout: 10m, unit: m }
    retry: { max_attempts: 2, interval: 60s, backoff: fixed, on_failure: abort }
    depends_on: [checkout]

  - id: build
    name: 构建打包
    type: auto
    role: { type: system, target: npm/docker }
    action: 安装依赖并构建项目
    inputs:
      - { name: source_code, type: directory, source: checkout.outputs.source_code, required: true }
    outputs:
      - { name: build_artifact, type: file, description: 构建产物 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    retry: { max_attempts: 3, interval: 60s, backoff: exponential, on_failure: abort }
    depends_on: [static_check]

  - id: unit_test
    name: 单元测试
    type: auto
    role: { type: system, target: npm/pytest }
    action: 运行单元测试套件
    inputs:
      - { name: source_code, type: directory, source: checkout.outputs.source_code, required: true }
    outputs:
      - { name: test_result, type: object, description: 测试结果 }
      - { name: coverage, type: number, description: 代码覆盖率 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    retry: { max_attempts: 2, interval: 60s, backoff: fixed, on_failure: abort }
    depends_on: [checkout]

  - id: integration_test
    name: 集成测试
    type: auto
    role: { type: system, target: npm/pytest }
    action: 运行集成测试
    inputs:
      - { name: build_artifact, type: file, source: build.outputs.build_artifact, required: true }
    outputs:
      - { name: test_result, type: object, description: 集成测试结果 }
    sla: { expected_duration: 10m, timeout: 30m, unit: m }
    retry: { max_attempts: 2, interval: 120s, backoff: exponential, on_failure: abort }
    depends_on: [build, unit_test]

  - id: deploy_staging
    name: 部署到预发布环境
    type: auto
    role: { type: system, target: docker/k8s }
    action: 将构建产物部署到预发布环境
    inputs:
      - { name: build_artifact, type: file, source: build.outputs.build_artifact, required: true }
    outputs:
      - { name: deploy_url, type: string, description: 预发布环境 URL }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    retry: { max_attempts: 3, interval: 60s, backoff: exponential, on_failure: abort }
    depends_on: [integration_test]

  - id: smoke_test
    name: 冒烟测试
    type: auto
    role: { type: system, target: curl }
    action: 验证预发布环境基础功能
    inputs:
      - { name: deploy_url, type: string, source: deploy_staging.outputs.deploy_url, required: true }
    outputs:
      - { name: smoke_result, type: boolean, description: 冒烟测试结果 }
    sla: { expected_duration: 2m, timeout: 5m, unit: m }
    retry: { max_attempts: 2, interval: 30s, backoff: fixed, on_failure: abort }
    depends_on: [deploy_staging]

  - id: approve_production
    name: 生产部署审批
    type: approval
    action: 生产环境部署审批
    inputs:
      - { name: build_artifact, type: file, source: build.outputs.build_artifact, required: true }
      - { name: smoke_result, type: boolean, source: smoke_test.outputs.smoke_result, required: true }
    outputs:
      - { name: approval_result, type: boolean, description: 审批结果 }
      - { name: approval_comment, type: string, description: 审批意见 }
    approval:
      approvers: [<发布负责人>]
      strategy: any
      auto_approve_after: 24h
    sla: { expected_duration: 1h, timeout: 24h, unit: h }
    depends_on: [smoke_test]

  - id: deploy_production
    name: 部署到生产环境
    type: auto
    role: { type: system, target: docker/k8s }
    action: 将构建产物部署到生产环境
    inputs:
      - { name: build_artifact, type: file, source: build.outputs.build_artifact, required: true }
      - { name: approval_result, type: boolean, source: approve_production.outputs.approval_result, required: true }
    outputs:
      - { name: deploy_url, type: string, description: 生产环境 URL }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    retry: { max_attempts: 2, interval: 60s, backoff: exponential, on_failure: abort }
    depends_on: [approve_production]

  - id: notify_result
    name: 通知结果
    type: notification
    role: { type: mcp, target: lark-im }
    notification:
      channel: 飞书
      template: ci-result
      recipients: [<团队群/频道>]
    depends_on: [deploy_production]

edges:
  - { from: checkout, to: static_check, condition: always }
  - { from: checkout, to: unit_test, condition: always }
  - { from: static_check, to: build, condition: check_passed == true }
  - { from: build, to: integration_test, condition: always }
  - { from: unit_test, to: integration_test, condition: always }
  - { from: integration_test, to: deploy_staging, condition: test_result.passed == true }
  - { from: deploy_staging, to: smoke_test, condition: always }
  - { from: smoke_test, to: approve_production, condition: smoke_result == true }
  - { from: approve_production, to: deploy_production, condition: always }
  - { from: deploy_production, to: notify_result, condition: always }

triggers:
  type: event
  detail: 代码推送到主分支时触发

global:
  error_handling:
    strategy: stop
    fallback_node: notify_result
  notifications:
    on_start: false
    on_complete: true
    on_failure: true
  logging:
    level: info
    retention: 30
```

## 可定制参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| 项目名 | — | 必填，工作流名称前缀 |
| 构建工具 | npm | npm/docker/gradle/maven |
| 测试框架 | jest/pytest | 单元测试框架 |
| 部署目标 | docker/k8s | 部署平台 |
| 通知渠道 | 飞书 | 飞书/Slack/邮件 |
| 分支触发 | main | 触发分支名 |
| 预发布环境 | 需要 | 是否需要预发布环境 |
| 自动部署生产 | 否 | 是否需要人工确认 |