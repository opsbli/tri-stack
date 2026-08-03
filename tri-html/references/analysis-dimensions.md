# 六维架构分析维度详细参考

> 本文件是 tri-html SKILL.md §方法论 六维分析框架的展开参考表。每维度给出：核心问题 / 检查项清单 / 数据采集命令 / 输出图表类型。SKILL.md 仅留概览，详细判定与采集命令在此检索。

> **grep 检索模式**：`grep -n "§<维度号>" references/analysis-dimensions.md`（如 `grep -n "§1" ` 定位架构设计维度）

---

## §1 架构设计维度

**核心问题**：整体架构是什么模式？组件如何分层？数据如何流动？

### 检查项清单

- [ ] 识别架构模式（单体/微服务/Serverless/事件驱动/CQRS/六边形/分层/插件式…）
- [ ] 识别组件分层（表现层/业务层/数据层/基础设施层）
- [ ] 识别数据流方向（同步/异步/事件驱动/批处理）
- [ ] 识别部署形态（单机/集群/分布式/边缘）
- [ ] 识别关键架构决策（为何选此架构？有何权衡？）

### 数据采集命令

```bash
# 识别架构特征文件
find . -maxdepth 3 -name "docker-compose*.yml" -o -name "Dockerfile" -o -name "serverless.yml" -o -name "*.tf" -o -name "k8s*.yaml"
# 识别微服务特征
find . -maxdepth 3 -name "services" -type d -o -name "microservices" -type d
# 识别事件驱动特征
grep -rl "kafka\|rabbitmq\|eventbridge\|nats\|pulsar" --include="*.{json,yaml,yml,toml,lock}" .
```

### 输出图表

- **主图**：Mermaid C4 Context 图（系统外部依赖）或 Container 图（内部组件）
- **辅图**：Mermaid flowchart（数据流方向）

---

## §2 目录结构设计维度

**核心问题**：目录如何组织？分层是否清晰？有无坏味（深嵌套/扁平/混合）？

### 检查项清单

- [ ] 识别目录组织模式（按层/按功能/按领域/混合）
- [ ] 统计目录深度（最深 N 层，平均深度）
- [ ] 统计文件分布（按类型/按目录）
- [ ] 识别命名一致性（kebab-case/snake_case/camelCase）
- [ ] 识别坏味（过深嵌套 >5 层 / 单目录文件过多 >50 / 命名混乱）

### 数据采集命令

```bash
# 目录树（限制深度，排除 node_modules/.git/dist）
find . -maxdepth 3 -type d -not -path "*/node_modules*" -not -path "*/.git*" -not -path "*/dist*" | sort
# 文件类型统计
find . -type f -not -path "*/node_modules*" -not -path "*/.git*" | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
# 目录深度统计
find . -type d -not -path "*/node_modules*" -not -path "*/.git*" | awk -F'/' '{print NF}' | sort -n | uniq -c
```

### 输出图表

- **主图**：Mermaid mind map 或 flowchart（目录树，限制深度 3-4 层）
- **辅图**：文件类型分布饼图（用 Mermaid pie）

---

## §3 技术栈选型维度

**核心问题**：用了哪些技术？版本？依赖关系？选型是否合理？

### 检查项清单

- [ ] 识别编程语言（主语言/辅语言）及版本
- [ ] 识别框架（前端/后端/移动/桌面）及版本
- [ ] 识别构建工具（webpack/vite/rollup/turbo/esbuild…）
- [ ] 识别包管理器（npm/pnpm/yarn/bun/pip/uv/cargo/go mod…）
- [ ] 识别运行时（Node/Python/Java/Go/Rust…）及版本要求
- [ ] 识别数据库/缓存/消息队列
- [ ] 识别第三方服务（云服务/API/SDK）

### 数据采集命令

```bash
# 包管理器锁定文件识别
ls package.json package-lock.json pnpm-lock.yaml yarn.lock bun.lockb requirements.txt Pipfile poetry.lock Cargo.toml go.mod pom.xml build.gradle 2>/dev/null
# package.json 依赖读取
cat package.json 2>/dev/null | python -c "import json,sys; d=json.load(sys.stdin); print(json.dumps({'deps':d.get('dependencies',{}),'devDeps':d.get('devDependencies',{}),'engines':d.get('engines',{})}, indent=2))"
# Python 依赖
cat requirements.txt 2>/dev/null; cat pyproject.toml 2>/dev/null
```

### 输出图表

- **主图**：Mermaid 技术栈矩阵（表格图，分类列示）
- **辅图**：Mermaid flowchart（核心依赖关系图）

---

## §4 代码设计维度

**核心问题**：模块如何划分？接口如何设计？数据模型如何组织？

### 检查项清单

- [ ] 识别模块划分（按功能/按领域/按层）
- [ ] 识别接口设计风格（REST/GraphQL/gRPC/RPC）
- [ ] 识别数据模型（ORM/Schema/Migration）
- [ ] 识别设计模式应用（ MVC/MVVM/Clean Architecture/Repository…）
- [ ] 识别代码组织约定（单一职责/DRY/分层依赖规则）

### 数据采集命令

```bash
# 识别接口定义文件
find . -maxdepth 4 -name "*.controller.*" -o -name "*.router.*" -o -name "*.handler.*" -o -name "*.resolver.*" -o -name "*schema*.graphql" -o -name "*.proto" 2>/dev/null
# 识别数据模型
find . -maxdepth 4 -name "*.model.*" -o -name "*.entity.*" -o -name "*.schema.*" -o -name "*.migration.*" 2>/dev/null
# 识别模块入口
find . -maxdepth 3 -name "index.*" -o -name "main.*" -o -name "app.*" -o -name "server.*" 2>/dev/null
```

### 输出图表

- **主图**：Mermaid classDiagram（核心类/接口关系）
- **辅图**：Mermaid erDiagram（数据模型 ER 图，若有数据库）

---

## §5 功能设计维度

**核心问题**：实现了哪些功能？功能模块如何协作？用户旅程如何？

### 检查项清单

- [ ] 识别核心功能模块（从 README/路由/控制器推断）
- [ ] 识别功能模块间依赖关系
- [ ] 识别用户旅程（关键路径：注册/登录/核心操作/支付…）
- [ ] 识别权限模型（RBAC/ABAC/ACL）
- [ ] 识别状态机（订单状态/任务状态/工作流状态）

### 数据采集命令

```bash
# 识别路由定义（REST）
find . -maxdepth 4 -name "*.route.*" -o -name "*.controller.*" 2>/dev/null | head -20
grep -rn "router\.\(get\|post\|put\|delete\|patch\)\|@Get\|@Post\|@Controller\|app\.\(get\|post\)" --include="*.{ts,js,py,java,go}" . 2>/dev/null | head -50
# 识别 README 功能描述
cat README.md 2>/dev/null | head -100
```

### 输出图表

- **主图**：Mermaid flowchart（功能模块协作图）
- **辅图**：Mermaid journey（关键用户旅程）或 stateDiagram-v2（状态机）

---

## §6 特殊设计维度

**核心问题**：安全/性能/可观测性/扩展性策略？

### 检查项清单

**安全设计**：
- [ ] 认证机制（JWT/Session/OAuth/API Key）
- [ ] 授权机制（RBAC/ABAC/中间件）
- [ ] 数据加密（传输 TLS/存储加密）
- [ ] 输入验证与防注入（参数化查询/XSS 防护/CSRF）
- [ ] 密钥管理（环境变量/密钥管理服务）

**性能设计**：
- [ ] 缓存策略（Redis/内存缓存/HTTP 缓存）
- [ ] 数据库优化（索引/连接池/读写分离/分库分表）
- [ ] 异步处理（队列/Worker/调度）
- [ ] CDN/静态资源优化
- [ ] 懒加载/代码分割

**可观测性**：
- [ ] 日志（结构化日志/日志级别/日志聚合）
- [ ] 监控（指标/告警/Prometheus/Grafana）
- [ ] 链路追踪（OpenTelemetry/Jaeger/Zipkin）
- [ ] 健康检查（liveness/readiness）

**扩展性**：
- [ ] 水平扩展能力（无状态/有状态）
- [ ] 插件机制（钩子/中间件/扩展点）
- [ ] 配置驱动（环境变量/配置中心）
- [ ] 多租户支持

### 数据采集命令

```bash
# 安全相关
grep -rn "jwt\|passport\|bcrypt\|argon2\|helmet\|cors\|csrf" --include="*.{ts,js,py,java,go,json}" . 2>/dev/null | head -20
# 性能相关
grep -rn "redis\|cache\|queue\|worker\|bull\|celery" --include="*.{ts,js,py,java,go,json}" . 2>/dev/null | head -20
# 可观测性
grep -rn "winston\|pino\|log4j\|prometheus\|grafana\|opentelemetry\|sentry" --include="*.{ts,js,py,java,go,json}" . 2>/dev/null | head -20
```

### 输出图表

- **主图**：Mermaid flowchart（特殊设计策略图，按实际识别到的策略绘制）
- **辅图**：按需绘制（如安全认证流程图、缓存架构图、监控拓扑图）

---

## 维度间关联

六维并非孤立，分析时须识别关联：

| 关联 | 说明 |
|---|---|
| 架构设计 ↔ 目录结构 | 架构分层应反映在目录组织上 |
| 技术栈选型 ↔ 代码设计 | 框架决定代码设计模式（如 NestJS → 装饰器模式） |
| 功能设计 ↔ 代码设计 | 功能模块对应代码模块 |
| 特殊设计 ↔ 架构设计 | 安全/性能策略影响架构选型 |

分析报告中须有「维度关联」章节，点明关键关联。
