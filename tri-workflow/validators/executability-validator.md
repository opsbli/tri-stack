# 可执行性验证规则（Executability Validator）

> 阶段 5 校验模块。对工作流模型进行静态分析，验证死锁、可达性、超时合理性等可执行性指标。

## 校验流程

```
workflow-model.yml ──→ 可执行性验证引擎 ──→ validation-report.md
```

## 校验规则

### 规则 1：死锁检测（Deadlock Detection）

**规则**：状态机中不存在互相等待的节点。

**检测方法**：资源分配图（Resource Allocation Graph）分析

```
构建等待图（Wait-For Graph）：
1. 每个节点为一个进程
2. 若节点 A depends_on B，则 A → B 有一条边
3. 检测图中是否存在环：
   - 若存在环 → 死锁风险
   - 排除审批回退环（合法）
```

**示例**：
```
# 死锁示例
node_03 depends_on: [node_02]
node_02 depends_on: [node_01]
node_01 depends_on: [node_03]  ← 环！node_01 → node_03 → node_02 → node_01

# 非死锁（审批回退，合法）
发起申请 → 一级审批 → (驳回) → 发起申请  ← 审批回退环，允许
```

### 规则 2：不可达状态检测（Unreachable State Detection）

**规则**：所有节点必须从起始节点（`depends_on: []` 的节点）可达。

**检测方法**：从起始节点 BFS 遍历

```
1. 找到所有 depends_on: [] 的节点（起始节点）
2. 从起始节点 BFS/DFS 遍历 DAG
3. 未被遍历到的节点 → 不可达状态
```

**示例**：
```
node_01: depends_on: []       ← 起始节点
node_02: depends_on: [node_01] ← 可达
node_03: depends_on: [node_04] ← 不可达！（node_04 不存在或不可达）
```

### 规则 3：孤立节点检测（Orphan Node Detection）

**规则**：所有节点（除起始节点外）必须有前置节点，所有节点（除终止节点外）必须有后继节点。

**检测方法**：
```
# 适配两种输入格式：
# 格式 A（workflow-model）：有显式 edges 列表
# 格式 B（workflow-dsl）：边通过 jobs.<id>.needs 隐式表达

if input_format == "workflow-model":
    # 格式 A：直接使用 edges
    all_nodes = nodes[*].id
    referenced_as_target = edges[*].to + nodes[*].depends_on[]
    referenced_as_source = edges[*].from
elif input_format == "workflow-dsl":
    # 格式 B：从 needs 推导边
    all_nodes = jobs.keys()
    referenced_as_target = flatten(jobs[*].needs[])
    # 源节点 = 所有出现在 needs 中的 job_id
    referenced_as_source = [job_id for job_id in jobs if jobs[job_id].needs exists and len > 0]

# 起始节点 = depends_on 为空 或 needs 为空的节点
start_nodes = [node for node in all_nodes if node not in referenced_as_target]
# 终止节点 = 不在任何 needs 中且不作为 source 出现的节点（实际为 DAG 叶节点）
# 孤立节点 = 既不是起始节点，也不在任何边/needs 中出现
orphan_nodes = [node for node in all_nodes
                if node not in start_nodes
                and node not in referenced_as_target
                and node not in referenced_as_source]
if orphan_nodes:
    → 🟡 警告：孤立节点「{orphan_nodes}」既无前置也无后继
```

### 规则 4：超时合理性校验（Timeout Rationality）

**规则**：自动节点的 `sla.timeout` 必须 ≥ 预估执行时间。

**检测方法**：
```
for each node where node.type == "auto":
    if node.sla.timeout.exists and node.sla.expected_duration.exists:
        if node.sla.timeout < node.sla.expected_duration:
            → 🟡 警告：超时时间({timeout})小于预估执行时间({expected})
```

**默认超时检查**：
- 若节点无超时配置，不警告（阶段 4 会注入默认超时）
- 若节点超时 < 1 分钟，检查是否合理（大多数自动任务 ≥ 1min）

### 规则 5：重试策略合理性校验（Retry Strategy Rationality）

**规则**：重试次数和间隔应合理。

**检测方法**：
```
for each node where node.retry.exists:
    if node.retry.max_attempts > 10:
        → 🟡 警告：重试次数过多({attempts})，建议 ≤ 5
    if node.retry.interval < 5s:
        → 🟡 警告：重试间隔过短({interval}s)，建议 ≥ 10s
    if node.retry.backoff == "fixed" and node.retry.max_attempts > 3:
        → 🟡 警告：固定间隔重试次数过多，建议使用 exponential
```

### 规则 6：人工节点 SLA 校验（Manual Node SLA）

**规则**：人工节点和审批节点必须有合理的 SLA。

**检测方法**：
```
for each node where node.type in ["manual", "approval"]:
    if not node.sla.timeout.exists:
        → 🟡 警告：人工节点「{name}」缺少超时配置，可能导致工作流卡死
    if node.sla.timeout > 168h:  # 7 天
        → 🟡 警告：人工节点超时超过 7 天，建议缩短
```

### 规则 7：关键路径分析（Critical Path Analysis）

**规则**：工作流的关键路径耗时应在合理范围内。

**检测方法**：
```
1. 计算每个节点的预期耗时
2. 对 DAG 进行拓扑排序
3. 计算最早开始时间和最晚开始时间
4. 关键路径 = 总浮动时间为 0 的路径
5. 输出关键路径的总耗时
```

### 规则 8：条件分支完整性校验（Condition Branch Completeness）

**规则**：条件节点的所有分支必须指向有效节点，且应覆盖所有可能情况。

**检测方法**：
```
for each node where node.type == "condition":
    target_nodes = [c.target_node for c in node.conditions]
    for each target in target_nodes:
        if target not in all_node_ids:
            → 🟡 警告：条件分支指向不存在的节点「{target}」
    if len(node.conditions) == 1:
        → 🟡 警告：条件节点只有一个分支，可能缺少 else 分支
```

## 验证报告格式

```markdown
# 可执行性验证报告 · <workflow-name>

## 摘要

| 指标 | 值 |
|---|---|
| 总校验项 | <N> |
| 🔴 阻断 | <N> |
| 🟡 警告 | <N> |
| ✅ 通过 | <N> |
| 关键路径耗时 | <总耗时> |
| 可否进入阶段 6 | <是/否> |

## 🔴 阻断项

| # | 规则 | 节点 | 问题 | 解决方案 |
|---|---|---|---|---|
| 1 | 死锁检测 | node_01,node_03 | 节点间存在循环等待 | 调整依赖关系 |

## 🟡 警告项

| # | 规则 | 节点 | 问题 | 建议 |
|---|---|---|---|---|
| 1 | 超时合理性 | node_05 | 超时 5min < 预估 10min | 增加超时或优化执行 |

## ✅ 通过项

| # | 规则 | 详情 |
|---|---|---|
| 1 | 死锁检测 | 无死锁 |
| 2 | 不可达状态 | 所有节点可达 |

## 关键路径

```
起始节点 → node_02 (5min) → node_03 (10min) → node_05 (8min) → 终止
总耗时: 23min
```

## 沙箱 Dry-Run 结果（可选）

| 节点 | 状态 | 耗时 | 输出 |
|---|---|---|---|
| node_01 | ✅ 通过 | 12s | 代码检出完成 |
| node_02 | ✅ 通过 | 45s | 静态检查通过 |
| node_03 | ⚠️ 跳过 | — | 外部 API 不可达，跳过 |
```

## 沙箱 Dry-Run 规范

### 触发条件

- 工作流类型为 `ci-cd-pipeline` 或 `data-pipeline`
- 环境中有可用的沙箱执行环境
- 用户明确要求 dry-run

### 执行策略

1. 仅执行关键路径节点（自动节点 + 无副作用的步骤）
2. 跳过人工节点和审批节点
3. 跳过外部 API 调用（除非用户明确允许）
4. 使用 mock 数据替代真实输入

### Dry-Run 失败处理

- 失败 → 降级为 🟡 警告，标注风险
- 在报告中列出失败节点的错误信息
- 不阻断阶段 6 输出（但标注风险）