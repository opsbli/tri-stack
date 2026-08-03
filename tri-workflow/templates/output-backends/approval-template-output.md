# 审批流模板输出后端规范

> 阶段 6 输出后端之一。将工作流 DSL 编译为目标平台的审批流模板。

## 平台检测

根据 `env-profile.tech_stack.approval` 选择目标平台：

| 平台 | 输出文件 | 格式 |
|---|---|---|
| 飞书审批 | `approval/<name>-feishu.json` | JSON（飞书审批 API 格式） |
| 钉钉审批 | `approval/<name>-dingtalk.json` | JSON（钉钉审批 API 格式） |
| 企业微信 | `approval/<name>-wecom.json` | JSON（企业微信审批 API 格式） |
| 无（默认） | `approval/<name>-template.json` | JSON（通用格式） |

## 通用审批模板格式

```json
{
  "_meta": {
    "name": "{{meta.name}}",
    "slug": "{{meta.slug}}",
    "version": "{{meta.version}}",
    "generated_by": "tri-workflow",
    "generated_at": "{{meta.created_at}}",
    "dsl_source": "workflows/{{meta.slug}}.wf.yml"
  },
  "approval_flow": {
    "name": "{{meta.name}}",
    "description": "{{meta.description}}",
    "initiator": {
      "roles": ["<发起人角色>"],
      "description": "谁可以发起此审批"
    },
    "nodes": [
      {% for job in jobs if job.type == "approval" %}
      {
        "id": "{{job_id}}",
        "name": "{{job.name}}",
        "type": "approval",
        "order": {{loop.index}},
        "approvers": {{job.approval.approvers | json}},
        "strategy": "{{job.approval.strategy}}",
        "auto_approve_after_hours": {{job.approval.auto_approve_after_hours}},
        "timeout_action": "escalate",
        "conditions": [
          {% if job.if %}
          {
            "expression": "{{job.if}}",
            "action": "skip"
          }
          {% endif %}
        ]
      }{% if not loop.last %},{% endif %}
      {% endfor %}
    ],
    "notifications": [
      {% for job in jobs if job.type == "notification" %}
      {
        "event": "approval_{{job_id}}",
        "channel": "{{job.notify.channel}}",
        "recipients": {{job.notify.recipients | json}},
        "template": "{{job.notify.template}}"
      }{% if not loop.last %},{% endif %}
      {% endfor %}
    ],
    "conditions": [
      {% for job in jobs if job.type == "condition" %}
      {
        "id": "{{job_id}}",
        "name": "{{job.name}}",
        "branches": [
          {% for cond in job.conditions %}
          {
            "expression": "{{cond.expression}}",
            "target": "{{cond.target_node}}"
          }{% if not loop.last %},{% endif %}
          {% endfor %}
        ]
      }{% if not loop.last %},{% endif %}
      {% endfor %}
    ],
    "archive": {
      "enabled": true,
      "retention_days": 90,
      "storage": "{{env-profile.tech_stack.storage.type}}"
    }
  }
}
```

## 飞书审批模板格式

```json
{
  "approval_code": "{{meta.slug}}",
  "approval_name": "{{meta.name}}",
  "description": "{{meta.description}}",
  "nodes": [
    {% for job in jobs if job.type == "approval" %}
    {
      "node_name": "{{job.name}}",
      "node_type": "approval",
      "approver_type": "{{job.approval.strategy}}",
      "approvers": [
        {% for approver in job.approval.approvers %}
        {
          "approver_type": "user",
          "approver_id": "{{approver}}"
        }{% if not loop.last %},{% endif %}
        {% endfor %}
      ],
      "auto_approve": {{job.approval.auto_approve_after_hours > 0}},
      "auto_approve_hours": {{job.approval.auto_approve_after_hours}}
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ],
  "cc_nodes": [
    {% for job in jobs if job.type == "notification" %}
    {
      "cc_type": "user",
      "cc_ids": {{job.notify.recipients | json}}
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ],
  "conditions": [
    {% for job in jobs if job.type == "condition" %}
    {
      "condition_name": "{{job.name}}",
      "branches": [
        {% for cond in job.conditions %}
        {
          "condition": "{{cond.expression}}",
          "next_node": "{{cond.target_node}}"
        }{% if not loop.last %},{% endif %}
        {% endfor %}
      ]
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ]
}
```

## 生成约束

1. 仅输出审批流相关节点（`type=approval`、`type=notification`、`type=condition`）
2. 审批节点按 `needs` 依赖顺序排列
3. 条件分支保持原逻辑不变
4. 通知节点映射为抄送人（飞书）或通知接收人（通用）
5. 归档策略默认 90 天保留
6. 若平台不支持自动通过，降级为手动配置提醒
7. 生成的审批模板是骨架——具体的审批人 ID 需用户手动填充