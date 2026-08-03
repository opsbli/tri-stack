# CI/CD 配置输出后端规范

> 阶段 6 输出后端之一。将工作流 DSL 编译为目标平台的 CI/CD 配置文件。

## 平台检测

根据 `env-profile.tech_stack.ci_cd` 选择目标平台：

| 平台 | 输出文件 | 语法 |
|---|---|---|
| GitHub Actions | `.github/workflows/<name>.yml` | YAML |
| Jenkins | `Jenkinsfile` | Groovy |
| GitLab CI | `.gitlab-ci.yml` | YAML |
| 无（默认） | `.github/workflows/<name>.yml` | YAML（GitHub Actions 作为默认） |

## GitHub Actions 输出模板

```yaml
# {{meta.name}} — CI/CD Pipeline
# 由 tri-workflow 自动生成，基于 DSL: workflows/{{meta.slug}}.wf.yml
# 生成时间: {{meta.created_at}}

name: {{meta.name}}

on:
  {# 根据 trigger 类型生成 #}
  {% if trigger.type == "schedule" %}
  schedule:
    - cron: "{{trigger.schedule}}"
  {% elif trigger.type == "event" %}
  {{trigger.event.source}}:
    types: [{{trigger.event.types | join(", ")}}]
  {% elif trigger.type == "webhook" %}
  repository_dispatch:
    types: [{{trigger.webhook.path}}]
  {% else %}
  workflow_dispatch:  # 手动触发
  {% endif %}

env:
  {# 遍历 DSL env #}
  {% for var in env %}
  {% if var.secret %}
  {{var.name}}: ${{"{{"}} secrets.{{var.name}} {{"}}"}}
  {% else %}
  {{var.name}}: "{{var.value}}"
  {% endif %}
  {% endfor %}

jobs:
  {# 遍历 DSL jobs，仅输出 type=auto 的节点 #}
  {% for job in jobs if job.type == "auto" %}
  {{job_id}}:
    name: {{job.name}}
    {% if job.needs %}
    needs: [{{job.needs | join(", ")}}]
    {% endif %}
    {% if job.if and job.if != "always()" %}
    if: {{job.if}}
    {% endif %}
    runs-on: ubuntu-latest
    timeout-minutes: {{job_timeout}}

    steps:
      {% for step in job.steps %}
      - name: {{step.name}}
        id: {{step.id}}
        uses: {{step.uses}}
        {% if step.with %}
        with:
          {% for key, value in step.with %}
          {{key}}: "{{value}}"
          {% endfor %}
        {% endif %}
        timeout-minutes: {{step.timeout_minutes}}
        {% if step.retry and step.retry.max_attempts > 1 %}
        continue-on-error: true
        {% endif %}
      {% endfor %}

      {# 若配置了重试 #}
      {% if job.retry and job.retry.max_attempts > 1 %}
      - name: Retry on failure
        if: failure()
        uses: nick-fields/retry@v2
        with:
          max_attempts: {{job.retry.max_attempts}}
          timeout_minutes: {{job_timeout}}
          command: echo "Retry completed"
      {% endif %}

  {% endfor %}

  {# 通知 job（若配置了通知） #}
  {% if error_handling.notifications.on_failure %}
  notify-failure:
    name: Notify Failure
    needs: [{{all_job_ids | join(", ")}}]
    if: failure()
    runs-on: ubuntu-latest
    steps:
      - name: Send failure notification
        uses: <通知 action>
        with:
          channel: {{error_handling.notifications.channel}}
          message: "Workflow {{meta.name}} failed"
  {% endif %}
```

## Jenkins Pipeline 输出模板

```groovy
// {{meta.name}} — Jenkins Pipeline
// 由 tri-workflow 自动生成

pipeline {
    agent any

    environment {
        {% for var in env %}
        {% if var.secret %}
        {{var.name}} = credentials('{{var.name}}')
        {% else %}
        {{var.name}} = '{{var.value}}'
        {% endif %}
        {% endfor %}
    }

    options {
        timeout(time: {{limits.timeout_minutes}}, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    {% if trigger.type == "schedule" %}
    triggers {
        cron('{{trigger.schedule}}')
    }
    {% endif %}

    stages {
        {% for job in jobs if job.type == "auto" %}
        stage('{{job.name}}') {
            {% if job.if and job.if != "always()" %}
            when {
                expression { {{job.if}} }
            }
            {% endif %}
            steps {
                {% for step in job.steps %}
                // {{step.name}}
                script {
                    retry({{step.retry.max_attempts}}) {
                        timeout(time: {{step.timeout_minutes}}, unit: 'MINUTES') {
                            // {{step.uses}}
                            sh 'echo "Executing {{step.uses}}"'
                        }
                    }
                }
                {% endfor %}
            }
        }
        {% endfor %}
    }

    post {
        failure {
            // {{error_handling.notifications}}
        }
    }
}
```

## 生成约束

1. 平台检测优先使用 `env-profile.tech_stack.ci_cd`，无则默认 GitHub Actions
2. 只输出 `type=auto` 的节点到 CI 配置（人工/审批节点在 CI 中不可执行）
3. 敏感信息（`env[].secret=true`）使用平台的密钥管理机制（GitHub Secrets/Jenkins Credentials）
4. 并行 job 通过 `needs` 依赖关系自动推导并标记
5. 通知 job 使用 `if: failure()` 条件，仅在失败时触发
6. 条件分支使用各平台的条件语法（GitHub Actions: `if`、Jenkins: `when`）