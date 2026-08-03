# 数据处理流水线模板

> 模板 ID：`data-pipeline`
> 适用场景：数据采集 → 清洗 → 转换 → 加载 → 报表
> 核心节点：数据采集 → 质量校验 → 清洗 → 转换 → 聚合 → 加载 → 报表生成

## 模板定义

```yaml
workflow_name: <项目名>-data-pipeline
workflow_type: data-pipeline
template_id: data-pipeline
template_confidence: 100

nodes:
  - id: data_ingest
    name: 数据采集
    type: auto
    role: { type: api, target: <数据源 API> }
    action: 从数据源采集原始数据
    inputs: []
    outputs:
      - { name: raw_data, type: file, description: 原始数据 }
      - { name: record_count, type: number, description: 采集记录数 }
    sla: { expected_duration: 10m, timeout: 30m, unit: m }
    retry: { max_attempts: 3, interval: 5m, backoff: exponential, on_failure: abort }
    depends_on: []

  - id: data_validate
    name: 数据质量校验
    type: auto
    role: { type: system, target: validator }
    action: 校验数据完整性、准确性、一致性
    inputs:
      - { name: raw_data, type: file, source: data_ingest.outputs.raw_data, required: true }
    outputs:
      - { name: validated_data, type: file, description: 通过校验的数据 }
      - { name: quality_report, type: object, description: 质量报告（通过率/异常项） }
      - { name: quality_passed, type: boolean, description: 质量是否达标 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    depends_on: [data_ingest]

  - id: quality_check
    name: 质量判断
    type: condition
    conditions:
      - { expression: "quality_passed == true", target_node: data_clean }
      - { expression: "quality_passed == false", target_node: alert_quality }
    depends_on: [data_validate]

  - id: alert_quality
    name: 质量告警
    type: notification
    notification:
      channel: 飞书
      template: data-quality-alert
      recipients: [<数据团队>]
    depends_on: [quality_check]

  - id: data_clean
    name: 数据清洗
    type: auto
    role: { type: system, target: etl }
    action: 去重、格式化、填充缺失值、异常值处理
    inputs:
      - { name: validated_data, type: file, source: data_validate.outputs.validated_data, required: true }
    outputs:
      - { name: cleaned_data, type: file, description: 清洗后的数据 }
    sla: { expected_duration: 10m, timeout: 30m, unit: m }
    depends_on: [quality_check]

  - id: data_transform
    name: 数据转换
    type: auto
    role: { type: system, target: etl }
    action: 数据类型转换、字段映射、维度聚合
    inputs:
      - { name: cleaned_data, type: file, source: data_clean.outputs.cleaned_data, required: true }
    outputs:
      - { name: transformed_data, type: file, description: 转换后的数据 }
    sla: { expected_duration: 10m, timeout: 30m, unit: m }
    depends_on: [data_clean]

  - id: data_aggregate
    name: 数据聚合
    type: auto
    role: { type: system, target: etl }
    action: 按维度聚合计算指标
    inputs:
      - { name: transformed_data, type: file, source: data_transform.outputs.transformed_data, required: true }
    outputs:
      - { name: aggregated_data, type: file, description: 聚合结果 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    depends_on: [data_transform]

  - id: data_load
    name: 数据加载
    type: auto
    role: { type: api, target: <目标数据库/数仓> }
    action: 将处理后的数据加载到目标存储
    inputs:
      - { name: aggregated_data, type: file, source: data_aggregate.outputs.aggregated_data, required: true }
    outputs:
      - { name: load_result, type: object, description: 加载结果（行数/状态） }
    sla: { expected_duration: 10m, timeout: 30m, unit: m }
    retry: { max_attempts: 2, interval: 5m, backoff: exponential, on_failure: abort }
    depends_on: [data_aggregate]

  - id: report_generate
    name: 报表生成
    type: auto
    role: { type: skill, target: tri-content }
    action: 生成数据分析报表
    inputs:
      - { name: aggregated_data, type: file, source: data_aggregate.outputs.aggregated_data, required: true }
    outputs:
      - { name: report_file, type: file, description: 报表文件 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    depends_on: [data_load]

  - id: notify_done
    name: 完成通知
    type: notification
    notification:
      channel: 飞书
      template: data-pipeline-complete
      recipients: [<数据团队>]
    depends_on: [report_generate]

edges:
  - { from: data_ingest, to: data_validate, condition: always }
  - { from: data_validate, to: quality_check, condition: always }
  - { from: quality_check, to: data_clean, condition: "quality_passed == true" }
  - { from: quality_check, to: alert_quality, condition: "quality_passed == false" }
  - { from: data_clean, to: data_transform, condition: always }
  - { from: data_transform, to: data_aggregate, condition: always }
  - { from: data_aggregate, to: data_load, condition: always }
  - { from: data_load, to: report_generate, condition: always }
  - { from: report_generate, to: notify_done, condition: always }

triggers:
  type: schedule
  detail: 每日定时执行

global:
  error_handling:
    strategy: skip
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
| 项目名 | — | 必填 |
| 数据源 | — | 数据来源 API/数据库 |
| 目标存储 | — | 数据加载目标 |
| 调度频率 | 每日 | cron 表达式 |
| 质量阈值 | 95% | 数据质量通过率阈值 |
| 通知渠道 | 飞书 | 飞书/Slack/邮件 |