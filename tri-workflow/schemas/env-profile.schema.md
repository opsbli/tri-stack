# 环境能力清单 Schema（env-profile）

> 阶段 1 产出。定义工作流运行环境的完整能力画像，供阶段 5 依赖校验使用。

## Schema 定义

```yaml
# env-profile.yml — 环境能力清单
# 由阶段 1 环境感知扫描生成，只读，不修改已有配置

meta:
  scan_time: <ISO 8601 时间戳>
  scan_version: "1.0.0"
  workspace: <当前 workspace 路径>

# === 已安装 Skill 清单 ===
skills:
  - name: <skill 名称，与 SKILL.md 的 name 字段一致>
    version: <SemVer 版本号>
    slug: <skill slug>
    description: <一句话描述>
    capabilities:
      - <能力 1：如「代码审查」>
      - <能力 2：如「自动修复」>
    input_contract:
      description: <输入契约摘要>
      required_fields: [<必填字段列表>]
    output_contract:
      description: <输出契约摘要>
      output_types: [<输出类型列表>]
    status: <active|deprecated|incompatible>

# === 可用 MCP 服务 ===
mcp_services:
  - server: <server 名称>
    description: <一句话描述>
    tools:
      - name: <tool 名称>
        description: <tool 描述>
        parameters:
          required: [<必填参数>]
          optional: [<可选参数>]
    status: <connected|disconnected|unauthorized>

# === 外部 API 端点 ===
external_apis:
  - name: <API 名称>
    endpoint: <API 基础 URL>
    auth_type: <api_key|oauth|basic|none>
    status: <verified|unverified|unreachable>
    rate_limit: <速率限制，如 100/min>

# === 组织约束 ===
org_constraints:
  approval_required: <true|false>
  security_level: <high|medium|low>
  compliance:
    - <合规要求 1：如「SOC2」>
    - <合规要求 2：如「GDPR」>
  data_residency: <数据驻留要求，如「中国大陆」>
  audit_required: <true|false>

# === 技术栈 ===
tech_stack:
  ci_cd:
    platform: <GitHub Actions|Jenkins|GitLab CI|无>
    version: <版本号，如无则填 unknown>
  approval:
    platform: <飞书|钉钉|企业微信|无>
    version: <版本号>
  messaging:
    platform: <飞书|Slack|邮件|无>
    version: <版本号>
  storage:
    type: <本地|云盘|数据库|对象存储>
    detail: <具体实现，如「飞书云盘」>
  orchestration:
    platform: <Airflow|Prefect|Dagster|无>
    version: <版本号>

# === 缺失能力标注 ===
missing_capabilities:
  - category: <skill|mcp|api|platform>
    name: <缺失的能力名称>
    impact: <对工作流的影响描述>
    suggestion: <建议安装/配置方案>

# === 降级标记 ===
degradation:
  level: <none|partial|full>
  reason: <降级原因>
  affected_stages: [<受影响的阶段编号>]
```

## 扫描规则

### Skills 扫描

1. 递归遍历 `skills/` 目录，查找所有 `SKILL.md` 文件
2. 解析每个 SKILL.md 的 frontmatter（name/version/description）和 content（capabilities/contracts）
3. 若 SKILL.md 无 frontmatter，标记 `status: unknown`
4. 若 SKILL.md 有 `status: deprecated`，标记 `status: deprecated`

### MCP 服务扫描

1. 列举 MCP 文件系统中的所有 server 目录
2. 读取每个 server 的 `tools/` 目录下的 JSON schema 文件
3. 提取 tool name/description/parameters
4. 若服务连接失败，标记 `status: disconnected`

### 外部 API 扫描

1. 从对话中提取用户提到的 API 端点
2. 从项目配置文件（`.env`、`config.yml`、`settings.json`）中提取 API 配置
3. 不主动发起网络请求验证连通性（避免安全风险），标记 `status: unverified`
4. 若用户明确要求验证，可选的网络检查

### 组织约束提取

1. 从对话中提取用户提到的安全/合规/审批要求
2. 从快照 `任务要点` 中提取约束条件
3. 若用户未提供，使用默认值：
   - `approval_required: false`
   - `security_level: medium`
   - `compliance: []`
   - `audit_required: false`

### 技术栈检测

1. 从项目文件中检测：
   - `.github/workflows/` 存在 → `ci_cd: GitHub Actions`
   - `Jenkinsfile` 存在 → `ci_cd: Jenkins`
   - `.gitlab-ci.yml` 存在 → `ci_cd: GitLab CI`
2. 从对话中提取用户提到的平台工具
3. 若无法检测，标记为 `无`

## 降级规则

| 降级级别 | 触发条件 | 行为 |
|---|---|---|
| `none` | 所有扫描项正常 | 完整环境画像 |
| `partial` | 1-2 个扫描项失败 | 标注缺失项，继续流程 |
| `full` | 3+ 个扫描项失败 或 Skills 目录为空 | 降级为仅产出设计文档，跳过阶段 5 依赖校验 |