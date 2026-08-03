# 多 Agent 协作编排模板

> 模板 ID：`multi-agent-orchestration`
> 适用场景：多 Agent 并行/串行协作完成复杂任务
> 核心节点：任务分解 → 并行分发 → 结果聚合 → 冲突检测 → 最终输出

## 模板定义

```yaml
workflow_name: <任务名>-multi-agent
workflow_type: multi-agent-orchestration
template_id: multi-agent-orchestration
template_confidence: 100

nodes:
  - id: task_decompose
    name: 任务分解
    type: auto
    role: { type: skill, target: tri-plan, version: ">=1.0.0" }
    action: 将复杂任务分解为可并行执行的子任务
    inputs:
      - { name: task_description, type: string, source: user_input, required: true }
    outputs:
      - { name: sub_tasks, type: array, description: 子任务列表 }
    sla: { expected_duration: 2m, timeout: 5m, unit: m }
    depends_on: []

  - id: dispatch_parallel
    name: 并行分发
    type: parallel
    action: 将子任务并行分发给多个 Agent
    inputs:
      - { name: sub_tasks, type: array, source: task_decompose.outputs.sub_tasks, required: true }
    depends_on: [task_decompose]

  - id: agent_a
    name: Agent A 执行
    type: auto
    role: { type: skill, target: <Skill A> }
    action: 执行子任务 A
    inputs:
      - { name: sub_task, type: object, source: dispatch_parallel, required: true }
    outputs:
      - { name: result_a, type: object, description: Agent A 的执行结果 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    retry: { max_attempts: 2, interval: 60s, backoff: fixed, on_failure: skip }
    depends_on: [dispatch_parallel]

  - id: agent_b
    name: Agent B 执行
    type: auto
    role: { type: skill, target: <Skill B> }
    action: 执行子任务 B
    inputs:
      - { name: sub_task, type: object, source: dispatch_parallel, required: true }
    outputs:
      - { name: result_b, type: object, description: Agent B 的执行结果 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    retry: { max_attempts: 2, interval: 60s, backoff: fixed, on_failure: skip }
    depends_on: [dispatch_parallel]

  - id: agent_c
    name: Agent C 执行
    type: auto
    role: { type: skill, target: <Skill C> }
    action: 执行子任务 C
    inputs:
      - { name: sub_task, type: object, source: dispatch_parallel, required: true }
    outputs:
      - { name: result_c, type: object, description: Agent C 的执行结果 }
    sla: { expected_duration: 5m, timeout: 15m, unit: m }
    retry: { max_attempts: 2, interval: 60s, backoff: fixed, on_failure: skip }
    depends_on: [dispatch_parallel]

  - id: aggregate_results
    name: 结果聚合
    type: auto
    role: { type: system, target: aggregator }
    action: 收集所有 Agent 的执行结果并聚合
    inputs:
      - { name: result_a, type: object, source: agent_a.outputs.result_a, required: false }
      - { name: result_b, type: object, source: agent_b.outputs.result_b, required: false }
      - { name: result_c, type: object, source: agent_c.outputs.result_c, required: false }
    outputs:
      - { name: aggregated, type: object, description: 聚合后的结果 }
    sla: { expected_duration: 1m, timeout: 5m, unit: m }
    depends_on: [agent_a, agent_b, agent_c]

  - id: conflict_detect
    name: 冲突检测
    type: auto
    role: { type: system, target: conflict-resolver }
    action: 检测多个 Agent 结果之间的冲突和矛盾
    inputs:
      - { name: aggregated, type: object, source: aggregate_results.outputs.aggregated, required: true }
    outputs:
      - { name: conflicts, type: array, description: 冲突列表 }
      - { name: has_conflict, type: boolean, description: 是否存在冲突 }
    sla: { expected_duration: 2m, timeout: 5m, unit: m }
    depends_on: [aggregate_results]

  - id: conflict_decision
    name: 冲突判断
    type: condition
    conditions:
      - { expression: "has_conflict == true", target_node: resolve_conflict }
      - { expression: "has_conflict == false", target_node: final_output }
    depends_on: [conflict_detect]

  - id: resolve_conflict
    name: 冲突解决
    type: auto
    role: { type: skill, target: tri-ask }
    action: 分析冲突原因并给出解决方案
    inputs:
      - { name: conflicts, type: array, source: conflict_detect.outputs.conflicts, required: true }
    outputs:
      - { name: resolution, type: object, description: 冲突解决方案 }
    sla: { expected_duration: 3m, timeout: 10m, unit: m }
    depends_on: [conflict_decision]

  - id: final_output
    name: 最终输出
    type: auto
    role: { type: skill, target: tri-content }
    action: 生成最终的结构化输出
    inputs:
      - { name: aggregated, type: object, source: aggregate_results.outputs.aggregated, required: true }
      - { name: resolution, type: object, source: resolve_conflict.outputs.resolution, required: false }
    outputs:
      - { name: final_result, type: object, description: 最终输出结果 }
    sla: { expected_duration: 3m, timeout: 10m, unit: m }
    depends_on: [conflict_decision]

edges:
  - { from: task_decompose, to: dispatch_parallel, condition: always }
  - { from: dispatch_parallel, to: agent_a, condition: always }
  - { from: dispatch_parallel, to: agent_b, condition: always }
  - { from: dispatch_parallel, to: agent_c, condition: always }
  - { from: agent_a, to: aggregate_results, condition: always }
  - { from: agent_b, to: aggregate_results, condition: always }
  - { from: agent_c, to: aggregate_results, condition: always }
  - { from: aggregate_results, to: conflict_detect, condition: always }
  - { from: conflict_detect, to: conflict_decision, condition: always }
  - { from: conflict_decision, to: resolve_conflict, condition: "has_conflict == true" }
  - { from: conflict_decision, to: final_output, condition: "has_conflict == false" }
  - { from: resolve_conflict, to: final_output, condition: always }

triggers:
  type: manual
  detail: 用户提交复杂任务时触发

global:
  error_handling:
    strategy: skip
  notifications:
    on_start: false
    on_complete: true
    on_failure: true
  logging:
    level: debug
    retention: 14
```

## 可定制参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| 任务名 | — | 必填 |
| Agent 数量 | 3 | 2-8 个并行 Agent |
| Agent 分配 | 自动 | 自动分配或手动指定 Skill |
| 超时策略 | 10min/Agent | 单个 Agent 超时时间 |
| 冲突解决 | 自动 | 冲突检测与解决策略 |