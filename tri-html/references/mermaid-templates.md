# Mermaid 图表语法模板

> 本文件是 tri-html 六维分析输出图表的 Mermaid 语法模板库。build_html.py 将这些模板填充实际数据后内联到 HTML。SKILL.md 仅留指针，详细语法在此检索。

> **grep 检索模式**：`grep -n "## <图表类型>" references/mermaid-templates.md`（如 `grep -n "## C4 Context" `）

---

## C4 Context 图（架构设计主图）

> 适用于 §1 架构设计维度，展示系统与外部依赖的关系。

```mermaid
C4Context
    title 系统架构 Context 图 - <项目名>
    Person(user, "用户", "系统使用者")
    System(system, "<项目名>", "<一句话描述>")
    System_Ext(ext1, "<外部系统1>", "<描述>")
    System_Ext(ext2, "<外部系统2>", "<描述>")
    Rel(user, system, "使用")
    Rel(system, ext1, "调用")
    Rel(system, ext2, "读取")
```

## Container 图（架构设计辅图）

> 适用于 §1 架构设计维度，展示系统内部容器/组件。

```mermaid
C4Container
    title Container 图 - <项目名>
    Container_Boundary(c, "<项目名>") {
        Container(web, "Web 前端", "<技术栈>", "提供 UI")
        Container(api, "API 服务", "<技术栈>", "提供业务 API")
        ContainerDb(db, "数据库", "<技术栈>", "存储数据")
    }
    Rel(web, api, "调用 API")
    Rel(api, db, "读写")
```

## 目录树 mind map（目录结构主图）

> 适用于 §2 目录结构维度，展示目录组织。

```mermaid
mindmap
  root((<项目名>))
    src
      components
      pages
      utils
      services
    tests
    docs
    config
    scripts
```

## 文件类型饼图（目录结构辅图）

> 适用于 §2 目录结构维度，展示文件类型分布。

```mermaid
pie title 文件类型分布
    "TypeScript" : 45
    "JavaScript" : 20
    "JSON" : 15
    "CSS" : 10
    "Markdown" : 5
    "其他" : 5
```

## 技术栈矩阵（技术栈选型主图）

> 适用于 §3 技术栈选型维度，分类列示技术栈。

> Mermaid 无原生表格图，用 flowchart 模拟：

```mermaid
flowchart LR
    subgraph 前端
        FE[框架: React 18.2<br/>构建: Vite 5.0<br/>状态: Zustand]
    end
    subgraph 后端
        BE[框架: NestJS 10.0<br/>ORM: Prisma 5.0<br/>运行时: Node 20 LTS]
    end
    subgraph 数据
        DB[数据库: PostgreSQL 16<br/>缓存: Redis 7.2<br/>队列: BullMQ]
    end
    subgraph 基础设施
        INF[容器: Docker<br/>CI: GitHub Actions<br/>部署: Vercel]
    end
```

## 依赖关系图（技术栈选型辅图）

> 适用于 §3 技术栈选型维度，展示核心依赖关系。

```mermaid
flowchart TD
    APP[应用入口] --> CORE[核心框架]
    CORE --> DB_DRIVER[数据库驱动]
    CORE --> AUTH[认证库]
    CORE --> CACHE[缓存库]
    AUTH --> JWT[JWT 库]
    CACHE --> REDIS[Redis 客户端]
```

## 类图（代码设计主图）

> 适用于 §4 代码设计维度，展示核心类/接口关系。

```mermaid
classDiagram
    class User {
        +String id
        +String name
        +String email
        +login()
        +logout()
    }
    class UserController {
        +create()
        +update()
        +delete()
    }
    class UserRepository {
        +findById()
        +save()
    }
    UserController --> User
    UserController --> UserRepository
    UserRepository --> User
```

## ER 图（代码设计辅图）

> 适用于 §4 代码设计维度，展示数据模型关系（若有数据库）。

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "ordered in"
    USER {
        string id PK
        string name
        string email
    }
    ORDER {
        string id PK
        string user_id FK
        datetime created_at
    }
```

## 功能模块协作图（功能设计主图）

> 适用于 §5 功能设计维度，展示功能模块协作。

```mermaid
flowchart LR
    AUTH[认证模块] --> USER[用户模块]
    USER --> ORDER[订单模块]
    ORDER --> PAYMENT[支付模块]
    ORDER --> INVENTORY[库存模块]
    PAYMENT --> NOTIFY[通知模块]
```

## 用户旅程图（功能设计辅图）

> 适用于 §5 功能设计维度，展示关键用户旅程。

```mermaid
journey
    title 用户下单旅程
    section 浏览
      访问首页: 5: 用户
      查看商品: 4: User
    section 下单
      加入购物车: 5: User
      提交订单: 3: User
      支付: 2: User, System
    section 完成
      收到确认: 5: User
      物流追踪: 4: User
```

## 状态机图（功能设计辅图）

> 适用于 §5 功能设计维度，展示状态机（订单/任务/工作流）。

```mermaid
stateDiagram-v2
    [*] --> 待支付
    待支付 --> 已支付: 支付成功
    待支付 --> 已取消: 取消订单
    已支付 --> 已发货: 商家发货
    已发货 --> 已签收: 用户签收
    已签收 -->已完成: 确认完成
    已取消 --> [*]
    已完成 --> [*]
```

## 特殊设计策略图（特殊设计主图）

> 适用于 §6 特殊设计维度，按实际识别到的策略绘制。示例为安全认证流程：

```mermaid
flowchart TD
    REQ[请求到达] --> MW[中间件链]
    MW --> AUTH{认证检查}
    AUTH -->|失败| REJECT[401 拒绝]
    AUTH -->|通过| RBAC{授权检查}
    RBAC -->|无权限| FORBID[403 禁止]
    RBAC -->|通过| CTRL[业务控制器]
    CTRL --> VALID[输入验证]
    VALID -->|失败| BAD[400 错误]
    VALID -->|通过| BIZ[业务逻辑]
    BIZ --> RESP[响应]
```

## 缓存架构图（特殊设计辅图）

> 适用于 §6 特殊设计维度，展示缓存策略。

```mermaid
flowchart LR
    CLIENT[客户端] --> CDN[CDN]
    CDN --> LB[负载均衡]
    LB --> APP[应用层]
    APP --> CACHE{Redis 缓存}
    CACHE -->|命中| RESP1[返回]
    CACHE -->|未命中| DB[(数据库)]
    DB --> APP
```

## 监控拓扑图（特殊设计辅图）

> 适用于 §6 特殊设计维度，展示可观测性架构。

```mermaid
flowchart TD
    APP[应用] --> METRICS[指标]
    APP --> LOG[日志]
    APP --> TRACE[链路]
    METRICS --> PROM[Prometheus]
    LOG --> LOKI[Loki]
    TRACE --> JAEGER[Jaeger]
    PROM --> GRAF[Grafana]
    LOKI --> GRAF
    JAEGER --> GRAF
    GRAF --> ALERT[告警]
```

---

## 模板填充规则

1. **占位符替换**：模板中 `<项目名>`、`<技术栈>`、`<描述>` 等占位符 MUST 替换为实际数据
2. **语法校验**：build_html.py 内置 Mermaid 语法校验，语法错误的图表 MUST 修正后再注入
3. **按需选择**：每维度主图必选，辅图按实际识别到的内容选择（无数据库则不画 ER 图）
4. **节点数控制**：单图节点数建议 ≤15，超出时分图绘制（避免 Mermaid 渲染性能问题）
5. **特殊字符转义**：节点文本含 `()[]{}|` 等特殊字符时用引号包裹（如 `Node["文本(含括号)"]`）
