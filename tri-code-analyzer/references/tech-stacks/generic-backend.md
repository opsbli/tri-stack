---
name: stack-generic-backend
description: 通用后端/全栈栈卡——Spring Boot、Django、FastAPI、Flask、Go、Node Express/NestJS、.NET 的分表探测信号与分析要点。
---

# 栈卡：通用后端与全栈（分表）

> 按下表信号匹配具体子栈；一库多服务（前后端同仓、微服务群）逐服务匹配。

## 子栈分表

### Spring Boot（Java/Kotlin）

- **信号**：`pom.xml`（spring-boot-starter-*）或 `build.gradle(.kts)`；`src/main/java/.../@SpringBootApplication`；`application.yml|properties`。
- **分析要点**：分层 Controller→Service→Repository（by-layer 惯例极强）；路由=`@RestController`+`@RequestMapping` 扫描；横切=AOP 切面 + `@Aspect` + Bean 生命周期；异步=`@Async`+ThreadPoolTaskExecutor 配置、`CompletableFuture`；实体=JPA `@Entity`/MyBatis mapper XML；配置=profile 多环境 + `@ConfigurationProperties` + Nacos/Apollo 特征；事务=`@Transactional` 传播行为；全局异常=`@ControllerAdvice`。
- **坑**：@Transactional 自调用失效；@Async 线程池未自定义（用 SimpleAsyncTaskExecutor）；循环依赖 @Autowired 注入。

### Django / FastAPI / Flask（Python）

- **信号**：`requirements.txt`/`pyproject.toml`；Django：`manage.py`+`settings.py`+`urls.py`；FastAPI：`FastAPI()`+`uvicorn`；Flask：`Flask(__name__)`。
- **分析要点**：Django=MTV 分层 + ORM models.py + urls.py 路由表 + middleware 列表 + Celery 异步任务 + settings 多环境拆分；FastAPI=路由装饰器 + Pydantic 模型（DTO 事实标准）+ Depends 依赖注入 + async 端点 + background_tasks；Flask=blueprint 蓝图路由 + 扩展生态（SQLAlchemy）。
- **坑**：Django N+1 查询（select_related 缺失）；FastAPI 同步阻塞调用进 async 端点；密钥硬编码 settings。

### Go

- **信号**：`go.mod` + `main.go`；常见框架 gin/echo/fiber/chi 或标准库 `net/http`。
- **分析要点**：按领域分包（`internal/` 惯例）；路由=gin Engine 路由组；并发=goroutine + channel + `sync.WaitGroup/Mutex` + context 取消链（剖析 MUST 查 goroutine 泄漏与 channel 死锁风险）；实体=struct + sqlx/gorm；配置=viper + `.env`；错误处理=显式 error 返回链。
- **坑**：goroutine 无退出机制；map 并发读写（缺 sync.RWMutex）；error 被吞（`_ =`）。

### Node.js（Express / NestJS）

- **信号**：`package.json`；Express：`express()` + `app.use`；NestJS：`@nestjs/core` + `@Module()` 装饰器 + `main.ts` bootstrap。
- **分析要点**：Express=中间件链（剖析按 app.use 注册顺序画管道图）+ 路由表 + 手工分层；NestJS=模块化 DI（Module/Provider/Controller 三件套）+ Guard/Interceptor/Pipe 横切链 + `@nestjs/config` + TypeORM/Prisma 实体；异步=async/await + 事件循环阻塞检查（CPU 密集任务应出进程）。
- **坑**：中间件顺序错误（错误处理必须最后注册）；Nest 循环依赖 forwardRef；未捕获的 promise rejection（process 级 handler 缺失）。

### .NET（ASP.NET Core）

- **信号**：`*.csproj`（TargetFramework net8.0 等）+ `Program.cs`（minimal hosting）或 `Startup.cs`。
- **分析要点**：DI 容器注册链（Program.cs 即拓扑图）+ Controller/Minimal API 路由 + Middleware 管道（`app.Use...` 顺序）+ EF Core 实体/Migration + `appsettings.{Env}.json` 多环境 + Options 模式强类型配置。
- **坑**：sync-over-async（.Result/.Wait 死锁）；DbContext 生命周期错用（singleton 注入 scoped）；密钥进 appsettings 提交仓库。

## 通用核查清单（任意后端子栈）

1. 鉴权链路：token 校验位置（中间件/守卫）+ 会话存储。
2. 数据访问：ORM 选型 + 连接池配置 + 迁移机制。
3. 异步基建：任务队列（Celery/BullMQ/MQ）+ 定时任务注册点。
4. 配置与密钥：多环境隔离 + 密钥注入方式（env/secret manager/硬编码=债）。
5. 错误体系：全局异常处理位置 + 错误码规范。
6. 可观测性：日志框架 + 链路追踪特征（traceId 透传）。
