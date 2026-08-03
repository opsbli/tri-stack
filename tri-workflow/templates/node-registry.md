# 可复用节点注册表（Node Registry）

> 高频节点市场。积累可复用的工作流节点，新工作流优先从注册表组合，缺失的从零设计。遵循"glue programming"原则。

## 注册表结构

每个节点包含：名称、类型、执行角色、输入、输出、适用场景、使用次数。

## 节点分类

### 一、代码工程类

| ID | 节点名称 | 类型 | 执行角色 | 描述 | 适用模板 |
|---|---|---|---|---|---|
| `code-checkout` | 代码检出 | auto | system/git | 从仓库拉取代码 | ci-cd, code-review, release |
| `static-analysis` | 静态代码检查 | auto | skill/tri-review | 自动代码审查，检查代码规范 | ci-cd, code-review |
| `unit-test` | 单元测试 | auto | system/npm/pytest | 运行单元测试套件 | ci-cd, code-review |
| `build` | 构建打包 | auto | system/npm/docker | 编译构建项目 | ci-cd, release |
| `integration-test` | 集成测试 | auto | system/npm/pytest | 运行集成测试 | ci-cd, release |
| `security-scan` | 安全扫描 | auto | system/trivy/snyk | 扫描依赖安全漏洞 | ci-cd, release |
| `deploy-staging` | 部署到预发布 | auto | system/docker/k8s | 部署到预发布环境 | ci-cd, release |
| `deploy-production` | 部署到生产 | auto | system/docker/k8s | 部署到生产环境 | release |
| `smoke-test` | 冒烟测试 | auto | system/curl | 部署后基础功能验证 | ci-cd, release |
| `rollback` | 回滚 | auto | system/docker/k8s | 回滚到上一个版本 | release |

### 二、协作沟通类

| ID | 节点名称 | 类型 | 执行角色 | 描述 | 适用模板 |
|---|---|---|---|---|---|
| `notify-feishu` | 飞书消息通知 | notification | mcp/lark-im | 发送飞书消息通知 | 全部 |
| `notify-slack` | Slack 通知 | notification | api/slack | 发送 Slack 消息通知 | 全部 |
| `notify-email` | 邮件通知 | notification | api/smtp | 发送邮件通知 | 全部 |
| `create-doc` | 创建飞书文档 | auto | skill/lark-doc | 创建飞书云文档 | approval, incident |
| `create-task` | 创建飞书任务 | auto | skill/lark-task | 创建待办任务 | approval, incident |
| `add-calendar` | 创建日程 | auto | skill/lark-calendar | 创建日历日程 | approval |

### 三、审批流程类

| ID | 节点名称 | 类型 | 执行角色 | 描述 | 适用模板 |
|---|---|---|---|---|---|
| `approval-first` | 一级审批 | approval | human/manager | 直属上级审批 | approval |
| `approval-second` | 二级审批 | approval | human/director | 部门负责人审批 | approval |
| `approval-final` | 终审 | approval | human/vp | 高管审批 | approval |
| `approval-auto` | 自动审批 | auto | system/rule-engine | 符合条件自动通过 | approval |

### 四、数据处理类

| ID | 节点名称 | 类型 | 执行角色 | 描述 | 适用模板 |
|---|---|---|---|---|---|
| `data-ingest` | 数据采集 | auto | api/source | 从数据源采集数据 | data-pipeline |
| `data-validate` | 数据质量校验 | auto | system/validator | 校验数据完整性/准确性 | data-pipeline |
| `data-clean` | 数据清洗 | auto | system/etl | 清洗/去重/格式化 | data-pipeline |
| `data-transform` | 数据转换 | auto | system/etl | 数据格式转换/聚合 | data-pipeline |
| `data-load` | 数据加载 | auto | api/database | 加载到目标数据库 | data-pipeline |
| `report-generate` | 报表生成 | auto | skill/tri-content | 生成分析报表 | data-pipeline |

### 五、监控告警类

| ID | 节点名称 | 类型 | 执行角色 | 描述 | 适用模板 |
|---|---|---|---|---|---|
| `monitor-check` | 监控检查 | auto | api/monitor | 检查监控指标 | release, incident |
| `alert-trigger` | 告警触发 | auto | api/alert | 触发告警通知 | incident |
| `incident-create` | 创建工单 | auto | api/itsm | 创建故障工单 | incident |
| `health-check` | 健康检查 | auto | system/curl | 服务健康检查 | release |

### 六、条件分支类

| ID | 节点名称 | 类型 | 描述 |
|---|---|---|---|
| `cond-test-pass` | 测试通过判断 | condition | 测试全部通过 → 继续；失败 → 通知 |
| `cond-approval-result` | 审批结果判断 | condition | 通过 → 执行；驳回 → 回退 |
| `cond-env-match` | 环境匹配判断 | condition | 预发布 → 灰度部署；生产 → 全量部署 |
| `cond-data-quality` | 数据质量判断 | condition | 质量过关 → 继续；不过关 → 告警 |

## 使用方式

### 阶段 2 模板匹配时

1. 根据用户需求的关键词匹配注册表中的节点
2. 匹配到的节点直接填入工作流模型的 `nodes` 列表
3. 未匹配到的节点标记为 `custom`，进入阶段 3 对话补全

### 阶段 3 对话补全时

1. 对 `custom` 节点，向用户提问确认节点细节
2. 确认后的 `custom` 节点若具有通用性，建议加入注册表

### 注册表维护

1. 每次成功设计一个工作流后，提取其中可复用的节点
2. 评估通用性（是否在其他场景也有用）
3. 通用 → 加入注册表，记录适用场景
4. 专用 → 保留在工作流内部，不加入注册表

## 扩展规范

新增节点时，需包含以下信息：

```yaml
- id: <kebab-case 唯一 ID>
  name: <节点显示名称>
  type: <auto|manual|approval|notification|condition|parallel>
  role:
    type: <skill|mcp|api|human|system>
    target: <具体目标>
  description: <一句话描述>
  inputs: [<输入数据>]
  outputs: [<输出数据>]
  sla: <预期耗时>
  applicable_templates: [<适用模板 ID 列表>]
  usage_count: <被引用次数>
  added_at: <加入日期>
```