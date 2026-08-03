---
name: tech-fastapi
description: FastAPI开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 FastAPI 特定的编码标准与质量检查。
tech_id: fastapi
tech_name: FastAPI
category: framework
---

# FastAPI 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 FastAPI 特定规范。

## 技术栈定义

FastAPI 是基于 Python 类型提示的现代异步 Web 框架，以 Pydantic 模型驱动数据校验与序列化，自动生成 OpenAPI 文档，内置依赖注入系统。核心特性：`async def` 异步路由、Pydantic 模型契约、`Depends` 依赖注入、自动文档（OpenAPI）、中间件、后台任务与 WebSocket 支持。

## 版本基线

- **FastAPI 0.95+**：引入 `Annotated` 风格依赖注入（`Annotated[T, Depends(...)]`），成为推荐写法；旧 `Depends(T)` 仍兼容
- **FastAPI 0.93+ / Pydantic v1**：早期基线，使用 `BaseSettings`、`parse_obj`、`Config` 内部类、`@validator` 装饰器；仅作遗留项目识别
- **FastAPI 0.100+ / Pydantic v2（破坏性变化）**：默认 Pydantic v2；`Config` 内部类 → `model_config = ConfigDict(...)`；`parse_obj` → `model_validate`；`@validator`/`@root_validator` → `@field_validator`/`@model_validator`；`.dict()` → `.model_dump()`；`.json()` → `.model_dump_json()`；ORM 模式 `orm_mode=True` → `from_attributes=True`
- **FastAPI 0.109+**：`lifespan` 上下文管理器替代 `@app.on_event("startup"/"shutdown")`（旧事件进入弃用周期），初始化与清理成对出现在同一函数中
- **FastAPI 0.110+ / Starlette 0.36+**：WebSocket 与中间件 API 稳定；`BackgroundTasks`（请求级、随响应调度）与 `asyncio.create_task`（独立、需自管取消/异常）的语义边界明确化

## 编码规范（技术特定）

### 接口契约

- **请求/响应模型明确**：请求体与响应体必须使用 Pydantic 模型定义，接口契约清晰可追踪
- **类型提示完整**：路径函数签名必须类型化，保证 OpenAPI 文档可用且一致
- **契约即文档**：以 Pydantic 模型与 OpenAPI 为核心文档来源，补充关键业务约束与鉴权说明
- **Pydantic v2 写法**：v2 项目使用 `model_config = ConfigDict(...)` 替代 `Config` 内部类；序列化用 `model_dump()`/`model_dump_json()`；校验用 `model_validate()`；自定义校验用 `@field_validator`/`@model_validator` 替代 `@validator`/`@root_validator`；ORM 模式用 `from_attributes=True`

### 分层组织

- **模块边界清晰**：路由、依赖、服务、数据访问分层组织，避免把所有逻辑堆在一个文件
- **APIRouter 拆分**：大型应用按业务域用 `APIRouter` 拆分路由，`prefix`/`tags` 集中声明，主 app 仅做 `include_router`

### 依赖注入

- **依赖注入优先**：使用 `Depends` 收敛通用能力（认证、权限、DB Session、限流等），避免重复代码
- **Annotated 写法优先**：FastAPI 0.95+ 优先用 `Annotated[T, Depends(...)]` 声明依赖，使签名可复用且更易测试；旧 `Depends(T)` 写法在存量代码中保持一致即可
- **yield 依赖做资源清理**：DB Session、外部连接等需清理的资源用 `yield` 依赖（`def get_session(): session = ...; try: yield session; finally: session.close()`），FastAPI 保证 finally 在请求结束执行
- **复用与一致性**：重复校验与通用逻辑提取为依赖项/工具函数，统一错误模型与返回格式

### 异步与性能

- **异步一致**：I/O 密集型路径使用 `async def`；阻塞操作必须放入线程池（`run_in_threadpool`）或改用异步库，禁止在 `async def` 路由中直接调用同步阻塞 I/O
- **数据库会话管理**：DB Session 的创建/提交/回滚/关闭必须集中管理并可审计
- **SQLAlchemy 2.0 异步 session**：异步项目使用 `AsyncSession` + `async_sessionmaker`，查询用 `select(...)` 新风格而非 `Query`；session 通过 `yield` 依赖注入，禁止跨请求复用
- **BackgroundTasks vs create_task 边界**：短小、需随响应返回后执行的清理性任务用 `BackgroundTasks`（由 Starlette 调度、请求级生命周期）；长时/独立后台任务用 `asyncio.create_task` 但必须自行管理取消与异常，避免"火并忘"导致异常静默

### 生命周期与中间件

- **lifespan 替代事件**：FastAPI 0.109+ 用 `lifespan` 异步上下文管理器替代 `@app.on_event("startup"/"shutdown")`；初始化与清理成对出现在同一函数中，便于保证资源对称释放
- **CORS 显式配置**：跨域场景显式配置 `CORSMiddleware`，`allow_origins` 用白名单而非 `["*"]`（与 `allow_credentials=True` 组合时禁止通配）
- **中间件顺序**：理解中间件"洋葱"执行顺序（添加顺序 = 外 → 内），安全/限流/日志中间件应靠近最外层

### WebSocket 与实时通信

- **WebSocket 资源管理**：`WebSocket` 端点必须处理断连与异常（`WebSocketDisconnect`），在 `finally` 中关闭连接与清理订阅
- **广播与连接表**：多连接广播用集中连接表/发布订阅，避免每连接独立轮询

### 错误处理

- **错误处理统一**：对外返回稳定错误码与错误结构，不把异常堆栈直接暴露给客户端；用 `HTTPException` 与全局 exception handler 统一映射业务异常

### 可测试性

- **可测试代码**：业务规则与外部依赖隔离，路由层易于通过 TestClient/依赖覆盖（`app.dependency_overrides`）进行测试
- **按项目约定测试**：为关键接口与边界条件提供单元/集成测试与回归用例

### 文档与安全

- **OpenAPI 自定义与安全**：通过 `responses`、`dependencies`、`security` 显式声明鉴权与响应 schema；生产环境按需关闭 `/docs` 与 `/redoc`（`docs_url=None`）

## 质量检查清单（技术特定）

- [ ] 请求体与响应体是否使用 Pydantic 模型定义
- [ ] 路径函数签名是否类型化（保证 OpenAPI 可用）
- [ ] Pydantic v2 项目是否使用 `model_config`/`model_dump`/`model_validate` 等新写法（无遗留 `Config`/`parse_obj`/`.dict()`）
- [ ] 通用能力（认证/权限/DB Session）是否通过 `Depends` 收敛
- [ ] 依赖是否优先用 `Annotated[T, Depends(...)]` 声明
- [ ] 需清理的资源是否用 `yield` 依赖（保证 finally 执行）
- [ ] I/O 密集型路径是否使用 `async def`
- [ ] 阻塞操作是否放入线程池或改用异步库
- [ ] DB Session 是否集中管理（创建/提交/回滚/关闭）
- [ ] 异步项目是否使用 SQLAlchemy 2.0 `AsyncSession` + `select()` 新风格
- [ ] 后台任务是否区分 `BackgroundTasks`（请求级）与 `asyncio.create_task`（独立、需自管取消/异常）
- [ ] 是否使用 `lifespan` 替代 `@app.on_event`
- [ ] CORS `allow_origins` 是否为白名单（非 `*`）
- [ ] WebSocket 端点是否处理 `WebSocketDisconnect` 与资源清理
- [ ] 对外错误响应是否统一结构（不暴露异常堆栈）
- [ ] 路由层是否可通过 TestClient/`app.dependency_overrides` 测试

## 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Starlette（FastAPI 底层）文档](https://www.starlette.io/)
- [FastAPI 最佳实践](https://github.com/zhanymkanov/fastapi-best-practices)
