# 依赖校验规则（Dependency Checker）

> 阶段 5 校验模块。对照 env-profile 校验 workflow-model 的依赖完整性。

## 校验流程

```
workflow-model.yml ──┐
                     ├──→ 依赖校验引擎 ──→ dependency-report.md
env-profile.yml ─────┘
```

## 校验规则

### 规则 1：Skill 存在性校验

**规则**：每个 `type=auto` 且 `role.type=skill` 的节点，其 `role.target` 必须在 `env-profile.skills[].name` 中存在。

**检查逻辑**：
```
for each node in workflow-model where node.type == "auto" and node.role.type == "skill":
    if node.role.target not in env-profile.skills[*].name:
        → 🔴 阻断：缺失 Skill「{target}」
```

**阻断处理**：
- 报告缺失 Skill 的名称
- 提供安装命令：`python ops/install-skills.py --target <目标目录>`
- 若 SkillHub 中未找到，提示用户手动创建

### 规则 2：Skill 版本兼容性校验

**规则**：若节点指定了 `role.version`，其版本约束必须与 env-profile 中的 Skill 版本兼容。

**检查逻辑**：
```
for each node where node.role.version exists:
    if not semver_satisfies(env-profile.skills[name].version, node.role.version):
        → 🔴 阻断：版本不兼容「{target}」要求 {required}，实际 {actual}
```

**版本约束语法**：
- `>=1.0.0`：最低版本
- `^1.0.0`：兼容版本（主版本不变）
- `~1.0.0`：近似版本（次版本不变）
- `1.0.0`：精确版本

### 规则 3：MCP 工具存在性校验

**规则**：每个 `role.type=mcp` 的节点，其 `role.target` 必须在 `env-profile.mcp_services[].tools[].name` 中存在。

**检查逻辑**：
```
for each node where node.role.type == "mcp":
    if node.role.target not in all_mcp_tools:
        → 🔴 阻断：缺失 MCP 工具「{target}」
```

### 规则 4：API 端点可达性校验

**规则**：每个 `role.type=api` 的节点，其 `role.target` 必须在 `env-profile.external_apis[].endpoint` 中存在。

**检查逻辑**：
```
for each node where node.role.type == "api":
    if node.role.target not in env-profile.external_apis[*].endpoint:
        → 🔴 阻断：缺失 API 端点「{target}」
```

**可选**：若用户明确要求，可对 API 端点发起 HEAD 请求验证连通性。
- 连通 → 通过
- 不连通 → 🟡 警告

### 规则 5：权限充足性校验

**规则**：若节点需要特定权限（如飞书审批、GitHub Write），必须检查 env-profile 中对应服务的权限范围。

**检查逻辑**：
```
for each node where node.role.type == "skill":
    required_permissions = infer_permissions(node.action)
    if required_permissions not subset of env-profile.skills[name].capabilities:
        → 🔴 阻断：权限不足，Skill「{name}」不具备「{required}」能力
```

### 规则 6：平台兼容性校验

**规则**：工作流的交付形态必须与 env-profile 的技术栈兼容。

**检查逻辑**：
```
if workflow requires CI/CD output and env-profile.tech_stack.ci_cd == "无":
    → 🟡 警告：未检测到 CI/CD 平台，CI 配置将使用 GitHub Actions 作为默认格式

if workflow requires approval output and env-profile.tech_stack.approval == "无":
    → 🟡 警告：未检测到审批平台，审批模板将使用通用格式
```

### 规则 7：循环依赖检测

**规则**：工作流 DAG 中不存在环（审批流中的驳回分支除外）。

**检查逻辑**：
```
使用拓扑排序检测 DAG 中是否存在环：
1. 构建邻接表
   - 格式 A（workflow-model）：从 edges 列表构建
   - 格式 B（workflow-dsl）：从 jobs[*].needs 反向构建（needs 中的 job_id → 当前 job_id）
2. 执行 Kahn 算法或 DFS 环检测
3. 若存在环 → 检查是否为审批驳回合法模式：
   合法模式 A（回退环）：type=approval → condition(reject) → 回退到前置节点（如 发起申请）
   合法模式 B（通知分支）：type=approval → condition(reject) → notification 节点（终止分支，无回退）
   - 若环中所有节点符合合法模式 A 或 B → 🟡 警告（允许）
   - 否则 → 🔴 阻断：存在非法循环依赖
注：合法模式 B（通知分支）实际不形成环，但条件分支中
   多个 condition 节点指向同一 notification 节点时需特别检查
   依赖是否为 AND 语义（会导致死锁）—— 若是，应拆分为独立节点
```

### 规则 8：数据流类型一致性校验

**规则**：上游节点的 `outputs` 类型必须与下游节点的 `inputs` 类型兼容。

**检查逻辑**：
```
for each edge in workflow-model.edges:
    source_outputs = nodes[edge.from].outputs
    target_inputs = nodes[edge.to].inputs
    for each input in target_inputs where input.source matches source_outputs:
        if input.type != source_outputs[matched].type:
            → 🟡 警告：类型不匹配「{from}.{output}」({type1}) → 「{to}.{input}」({type2})
```

## 校验报告格式

```markdown
# 依赖校验报告 · <workflow-name>

## 摘要

| 指标 | 值 |
|---|---|
| 总校验项 | <N> |
| 🔴 阻断 | <N> |
| 🟡 警告 | <N> |
| ✅ 通过 | <N> |
| 可否进入阶段 6 | <是/否> |

## 🔴 阻断项

| # | 规则 | 节点 | 问题 | 解决方案 |
|---|---|---|---|---|
| 1 | Skill 存在性 | node_03 | 缺失 Skill「tri-review」 | `python ops/install-skills.py --target <目标目录>` |

## 🟡 警告项

| # | 规则 | 节点 | 问题 | 建议 |
|---|---|---|---|---|
| 1 | 平台兼容性 | — | 未检测到 CI/CD 平台 | 将使用 GitHub Actions 作为默认格式 |

## ✅ 通过项

| # | 规则 | 节点 |
|---|---|---|
| 1 | Skill 存在性 | node_01 (tri-coding) |
| 2 | MCP 存在性 | node_02 (lark-im) |
```

## 特殊情况处理

### 审批驳回分支

审批流中的驳回有两种合法模式：

**模式 A（回退环）**：「驳回 → 回到发起人修改 → 重新提交」形成环：
- 检测到审批回退环时，降级为 🟡 警告
- 在报告中标注「审批回退环，已确认合法」

**模式 B（通知分支）**：「驳回 → 发送驳回通知 → 流程终止」不形成环：
- 多个 condition 节点指向同一 notification 节点时，检查 depends_on 是否为 AND 语义
- 若 AND 语义（如 `depends_on: [condition_a, condition_b]`）→ 🔴 阻断：死锁，需拆分为独立通知节点
- 若已拆分为独立通知节点（每个 condition 对应自己的 notification）→ ✅ 通过

### 可选依赖

若节点标注了 `role.optional: true`（如「如果有 tri-review 就自动审查，没有就跳过」）：
- 缺失时降级为 🟡 警告
- 在工作流中注入条件判断：`if skill_exists('tri-review') then ... else skip`

### 外部 API 未验证

若 `env-profile.external_apis[].status == "unverified"`：
- 不阻断，降级为 🟡 警告
- 在报告中标注「API 端点未验证连通性，请在部署前确认」