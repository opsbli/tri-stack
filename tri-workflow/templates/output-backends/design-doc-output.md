# 设计文档输出后端规范

> 阶段 6 输出后端之一。将工作流 DSL 编译为面向人类阅读的综合设计文档。

## 文档结构

```markdown
# {{meta.name}} — 工作流设计文档

> **文档类型**：工作流设计文档
> **生成方式**：由 tri-workflow 自动生成
> **DSL 源文件**：`workflows/{{meta.slug}}.wf.yml`
> **生成时间**：{{meta.created_at}}
> **版本**：{{meta.version}}

---

## 1. 背景与目标

### 1.1 业务背景
<从对话/快照中提取的业务背景描述>

### 1.2 工作流目标
{{meta.description}}

### 1.3 适用范围
- **工作流类型**：{{trigger.type}}
- **触发条件**：{{trigger_detail}}
- **适用团队**：<从对话中提取>

---

## 2. 工作流全景

### 2.1 流程图

```mermaid
graph TD
{# 遍历 jobs，按 needs 关系生成 Mermaid 流程图 #}
    {{job_id}}["{{job.name}}"]
    {{job_id}} --> {{next_job_id}}
```

### 2.2 关键指标

| 指标 | 值 |
|---|---|
| 总节点数 | {{jobs_count}} |
| 自动节点 | {{auto_count}} |
| 人工节点 | {{manual_count}} |
| 审批节点 | {{approval_count}} |
| 关键路径耗时 | {{critical_path_duration}} |
| 全局超时 | {{limits.timeout_minutes}} 分钟 |

---

## 3. 节点详细设计

{# 遍历 jobs #}
### 3.{{job_index}} {{job.name}}

| 属性 | 值 |
|---|---|
| 节点 ID | `{{job_id}}` |
| 类型 | {{job.type}} |
| 执行角色 | {{job.runner.type}} / {{job.runner.target}} |
| 前置依赖 | {{job.needs | join(", ") | default("无（起始节点）")}} |
| 执行条件 | {{job.if | default("始终执行")}} |
| 超时 | {{job_timeout}} 分钟 |
| 重试 | 最多 {{job.retry.max_attempts}} 次，间隔 {{job.retry.interval_seconds}} 秒 |

#### 步骤

{# 遍历 job.steps #}
1. **{{step.name}}**：使用 `{{step.uses}}`
   - 输入：{{step.with | yaml}}
   - 预期输出：<从 outputs 推断>

#### 异常处理

- **失败策略**：{{job 的 error_handling}}
- **降级方案**：<如有>

{# 若 job 有 approval #}
#### 审批流程

- 审批人：{{job.approval.approvers | join(", ")}}
- 审批策略：{{job.approval.strategy}}
- 自动通过时限：{{job.approval.auto_approve_after_hours}} 小时

---

## 4. 数据流设计

### 4.1 数据流向

| 数据项 | 来源节点 | 目标节点 | 数据类型 | 说明 |
|---|---|---|---|---|
{# 遍历 edges 和 inputs/outputs #}
| {{data_name}} | {{source_node}} | {{target_node}} | {{data_type}} | {{description}} |

### 4.2 数据存储

- **中间数据**：<存储位置>
- **最终产物**：<存储位置>
- **日志**：<存储位置>

---

## 5. 异常处理

### 5.1 错误分类

| 错误类型 | 处理策略 | 兜底节点 |
|---|---|---|
| 自动节点失败 | {{error_handling.strategy}} | {{error_handling.fallback_job}} |
| 人工节点超时 | 自动提醒 + 升级 | — |
| 审批超时 | 自动通过 / 升级 | — |
| 外部 API 不可用 | 重试 3 次 → 跳过 | — |

### 5.2 通知策略

| 事件 | 通知渠道 | 接收人 |
|---|---|---|
| 工作流启动 | {{notify.on_start}} | {{recipients}} |
| 工作流完成 | {{notify.on_complete}} | {{recipients}} |
| 工作流失败 | {{notify.on_failure}} | {{recipients}} |

---

## 6. 部署说明

### 6.1 前置条件

- [ ] 已安装依赖 Skill：{{required_skills | join(", ")}}
- [ ] 已配置 MCP 服务：{{required_mcp | join(", ")}}
- [ ] 已配置 API 密钥：{{required_apis | join(", ")}}
- [ ] 已配置通知渠道：{{notify_channels}}

### 6.2 部署步骤

1. 将 SKILL.md 放置到 `skills/{{meta.slug}}/` 目录
2. 将 CI 配置文件放置到 `.github/workflows/` 目录
3. 配置环境变量（见 `env` 节）
4. 触发测试运行

### 6.3 回滚方案

- 若工作流异常，手动停止当前运行
- 回滚到上一个版本的 DSL 文件
- 重新部署

---

## 7. 监控与迭代

### 7.1 监控指标

| 指标 | 目标值 | 告警阈值 |
|---|---|---|
| 工作流成功率 | ≥ 95% | < 90% |
| 平均执行时间 | ≤ {{critical_path_duration}} | > 1.5x |
| 人工节点等待时间 | ≤ 24h | > 48h |

### 7.2 反馈模板

> 使用以下模板记录工作流运行情况，反馈给 tri-workflow 进行迭代优化：

```yaml
feedback:
  run_id: <运行 ID>
  date: <运行日期>
  overall_status: <success|failure|partial>
  nodes:
    - id: <节点 ID>
      status: <success|failure|timeout|skipped>
      duration: <实际耗时>
      error: <错误信息，如有>
  suggestions: <优化建议>
```
```

## 生成约束

1. Mermaid 流程图按 `needs` 依赖关系生成，使用 `graph TD`（从上到下）
2. 审批节点使用特殊样式标注
3. 条件分支使用菱形节点
4. 数据流表格从 DSL 的 `inputs/outputs` 和 `edges` 自动推导
5. 部署说明中的前置条件从阶段 5 校验报告自动提取