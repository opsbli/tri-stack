# DAG 配置输出后端规范

> 阶段 6 输出后端之一。将工作流 DSL 编译为目标平台的 DAG 配置文件，适用于数据处理流（data-pipeline）类型。

## 平台检测

根据 `env-profile.tech_stack.orchestration` 选择目标平台：

| 平台 | 输出文件 | 格式 |
|---|---|---|
| Apache Airflow | `pipelines/<name>_dag.py` | Python（Airflow DAG） |
| Prefect | `pipelines/<name>_flow.py` | Python（Prefect Flow） |
| Dagster | `pipelines/<name>_job.py` | Python（Dagster Job） |
| 无（默认） | `pipelines/<name>-dag.yml` | YAML（通用 DAG 配置） |

## 通用 DAG 配置格式

```yaml
# {{meta.name}} — DAG 配置
# 由 tri-workflow 自动生成，基于 DSL: workflows/{{meta.slug}}.wf.yml
# 生成时间: {{meta.created_at}}

dag_name: {{meta.slug}}
description: {{meta.description}}
version: {{meta.version}}

# 调度配置
schedule:
  type: {{trigger.type}}
  cron: {{trigger.schedule | default("0 2 * * *")}}
  timezone: UTC

# 默认参数
default_args:
  owner: {{meta.author | default("airflow")}}
  retries: 3
  retry_delay_seconds: 60
  depends_on_past: false
  email_on_failure: true
  email_on_retry: false

# 任务定义
tasks:
  {% for job in jobs if job.type == "auto" %}
  - id: {{job_id}}
    name: {{job.name}}
    runner:
      type: {{job.runner.type}}
      target: {{job.runner.target}}
    upstream: {{job.needs | default([])}}
    timeout_minutes: {{job_timeout}}
    params:
      {% for key, value in job.steps[0].with %}
      {{key}}: "{{value}}"
      {% endfor %}
    retry:
      max_attempts: {{job.retry.max_attempts | default(3)}}
      interval_seconds: {{job.retry.interval_seconds | default(60)}}
      backoff: {{job.retry.backoff | default("exponential")}}
  {% endfor %}

# 通知配置
notifications:
  on_failure:
    channel: {{error_handling.notifications.channel | default("email")}}
    recipients: {{error_handling.notifications.recipients}}
  on_success:
    enabled: false
```

## Apache Airflow DAG 输出模板

```python
"""
{{meta.name}} — Airflow DAG
由 tri-workflow 自动生成，基于 DSL: workflows/{{meta.slug}}.wf.yml
生成时间: {{meta.created_at}}
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup

default_args = {
    "owner": "{{meta.author | default('airflow')}}",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
    "email_on_failure": True,
    "email_on_retry": False,
}

dag = DAG(
    dag_id="{{meta.slug}}",
    default_args=default_args,
    description="{{meta.description}}",
    schedule_interval="{{trigger.schedule | default('0 2 * * *')}}",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["tri-workflow", "auto-generated"],
)

# === 任务定义 ===
{% for job in jobs if job.type == "auto" %}
{{job_id}} = BashOperator(
    task_id="{{job_id}}",
    bash_command='echo "Executing {{job.name}} via {{job.runner.target}}"',
    dag=dag,
    execution_timeout=timedelta(minutes={{job_timeout}}),
    retries={{job.retry.max_attempts | default(3)}},
    retry_delay=timedelta(seconds={{job.retry.interval_seconds | default(60)}}),
)

{% endfor %}

# === 依赖关系 ===
{% for job in jobs if job.type == "auto" and job.needs %}
{% for need in job.needs %}
{{need}} >> {{job_id}}
{% endfor %}
{% endfor %}

# === 条件分支 ===
{% for job in jobs if job.type == "condition" %}
# 条件分支: {{job.name}}
# 分支逻辑需通过 Airflow BranchPythonOperator 实现
# {{job.conditions | tojson}}
{% endfor %}
```

## Prefect Flow 输出模板

```python
"""
{{meta.name}} — Prefect Flow
由 tri-workflow 自动生成
"""
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

{% for job in jobs if job.type == "auto" %}
@task(
    name="{{job.name}}",
    retries={{job.retry.max_attempts | default(3)}},
    retry_delay_seconds={{job.retry.interval_seconds | default(60)}},
    timeout_seconds={{job_timeout}} * 60,
)
def {{job_id}}({% for step in job.steps %}{{step.with.keys() | join(", ")}}{% endfor %}):
    """{{job.description}}"""
    # TODO: 实现 {{job.runner.target}} 调用逻辑
    pass

{% endfor %}

@flow(name="{{meta.name}}", log_prints=True)
def {{meta.slug | replace("-", "_")}}():
    {% for job in jobs if job.type == "auto" and not job.needs %}
    result_{{job_id}} = {{job_id}}.submit()
    {% endfor %}

    {% for job in jobs if job.type == "auto" and job.needs %}
    result_{{job_id}} = {{job_id}}.submit(
        {% for need in job.needs %}
        result_{{need}},{% endfor %}
    )
    {% endfor %}

    return { {% for job in jobs if job.type == "auto" %}
        "{{job_id}}": result_{{job_id}},{% endfor %}
    }

if __name__ == "__main__":
    {{meta.slug | replace("-", "_")}}()
```

## 生成约束

1. 平台检测优先使用 `env-profile.tech_stack.orchestration`，无则默认输出通用 YAML 格式
2. 只输出 `type=auto` 的节点到 DAG 配置（人工/审批节点在 DAG 中不可执行）
3. 条件分支（`type=condition`）需转换为平台的条件语法：
   - Airflow: `BranchPythonOperator`
   - Prefect: `case` 上下文管理器
   - 通用 YAML: 在 task 中标注 `condition` 字段
4. 通知节点（`type=notification`）转换为平台的通知回调
5. 并行任务通过 `upstream` / `>>` 依赖关系自动推导
6. 敏感参数使用平台的密钥管理（Airflow Connections / Prefect Secrets）
7. 生成的 DAG 配置是骨架——具体的任务执行逻辑由 tri-coding 补充
8. 生成时同时产出 `scripts/` 目录下的任务执行脚本骨架
