---
name: tech-flask
description: Flask开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Flask 特定的编码标准与质量检查。
tech_id: flask
tech_name: Flask
category: framework
---

# Flask 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Flask 特定规范。

## 技术栈定义

Flask 是 Python 生态中的微框架（micro-framework），核心极简，通过路由装饰器、蓝图（Blueprint）、上下文机制（app/request/session）与扩展生态组合出完整应用。核心特性：Application Factory 模式、Blueprint 模块化路由、请求/应用上下文、扩展机制（SQLAlchemy/Migrate 等）、Jinja2 模板引擎。

## 版本基线

- **Flask 2.x（2.0+）**：引入原生 `async def` 视图支持（基于 `asgiref` 同步桥接）；`before_first_request` 进入弃用周期（2.3 移除）；`flask` 命令稳定
- **Flask 2.3+（破坏性变化）**：移除 `before_first_request`；`flask.json` 适配 `orjson`/`simplejson`；`app.json` 配置对象化；部分旧 API 移除（如 `flask.Markup` 移至 `markupsafe`）
- **Flask 3.x（破坏性变化）**：最低 Python 3.9+；移除更多已弃用 API（`flask.Markup`、旧 `json` 接口）；`Blueprint` 的 `url_prefix` 与嵌套蓝图语义正式稳定；`@app.route` 对尾部斜杠歧义严格化
- **Flask-SQLAlchemy 3.x（破坏性变化）**：从全局 `db` 推断改为显式 `SQLAlchemy()` + `db.init_app(app)`（应用上下文初始化）；查询 API 推荐 SQLAlchemy 2.0 `db.session.execute(select(...))` 风格，`Query.get`/`Query.filter_by` 旧风格进入兼容期

## 编码规范（技术特定）

### 应用结构

- **Application Factory**：必须使用 `create_app` 工厂模式，以支持多环境配置与测试隔离
- **Blueprints 模块化**：路由按业务域拆分到蓝图，避免单文件巨石应用；蓝图通过 `url_prefix`/子域名隔离
- **职责清晰**：视图负责请求编排，业务逻辑沉淀到 service 层，数据访问集中管理

### 扩展与配置

- **扩展集中管理**：数据库、迁移、序列化等扩展按项目约定统一初始化与注入，避免散落导入副作用；Flask-SQLAlchemy 3.x 用 `db = SQLAlchemy()` 在工厂中 `db.init_app(app)` 初始化
- **配置可控**：配置来自环境与配置对象（`app.config.from_object`/`from_envvar`），避免硬编码与"隐式读取"

### 异步视图与 WSGI 兼容性

- **异步视图边界**：Flask 2.x+ 支持 `async def` 视图，但底层仍为 WSGI 同步桥接（`asgiref.sync_to_async`），仅适合少量 I/O 并发；高并发异步场景应改用 ASGI 框架（FastAPI/Starlette）而非在 Flask 中堆 async
- **async/await 与 WSGI 取舍**：不要在 `async def` 视图中调用同步阻塞 I/O（会阻塞 worker）；阻塞操作用 `run_in_threadpool` 或移到后台任务；WSGI 部署下 async 视图不带来真正并发收益
- **SQLAlchemy 2.0 写法**：查询优先用 `db.session.execute(select(Model)).scalars()` 新风格；旧 `Model.query`/`Query.get` 在 Flask-SQLAlchemy 3.x 进入兼容期，新代码不再使用

### 上下文与钩子

- **上下文边界明确**：理解 `current_app`/`g`/`request` 的生命周期，避免跨请求共享状态
- **g 对象语义**：`g` 仅在单次请求生命周期内有效，多 worker/多进程下不共享；跨请求持久数据用数据库/缓存，不要存 `g`
- **钩子分层**：`before_request`（前置鉴权/初始化）、`after_request`（统一修改响应/日志）、`teardown_request`（资源清理、无论异常均执行）职责分明；不要在 `after_request` 中做资源释放（异常时不执行），释放放 `teardown_request`

### 数据校验与错误处理

- **数据校验**：外部输入必须验证（Marshmallow/Pydantic 或项目既定方案），不相信客户端数据
- **统一错误响应**：为 API 提供一致的错误结构与状态码，避免到处 `return` 不同格式；用统一错误处理器（`@app.errorhandler`）

### 模板与安全

- **Jinja2 自动转义**：Flask 对 `.html`/`.jinja` 模板默认开启自动转义；输出用户内容时禁止滥用 `|safe`/`Markup`，确需输出富文本时用白名单清洗（bleach）
- **CSRF 防护**：表单与状态变更接口启用 Flask-WTF 的 `CSRFProtect`；API 走 JWT/Token 时显式豁免并补齐其它防护

### 鉴权与会话

- **Session/Cookie**：服务端 Session 用 `flask.session`（签名 Cookie），`SECRET_KEY` 必须来自环境变量；`session.permanent` + `PERMANENT_SESSION_LIFETIME` 控制有效期
- **JWT 边界**：无状态 API 用 JWT 时，签发/校验集中在一个装饰器/依赖中；刷新令牌与访问令牌分离，敏感操作不依赖 JWT 单点校验

### 后台任务与信号

- **后台任务**：耗时任务（邮件、报表、第三方调用）外移到 Celery/RQ，不在请求周期内同步执行
- **信号（blinker）边界**：信号仅用于解耦副作用（日志、缓存失效、通知）；核心业务流程不要用信号串联，调用链不可追踪是反模式；信号接收器必须可重入

### 部署

- **WSGI 服务器**：生产部署用 Gunicorn/uWSGI + 同步或多 worker，禁止用 `flask run`/开发服务器上线；worker 数按 CPU 核数与 I/O 模型调整
- **反向代理与超时**：前置 Nginx 处理 TLS/静态资源/超时；长请求显式调大 worker timeout 或改用异步通道

### 可测试性

- **可测试代码**：依赖可注入，核心业务逻辑可独立于请求上下文测试
- **按项目约定测试**：为关键接口与回归问题提供可复现用例

### 文档化

- **契约可追踪**：接口输入输出、错误码、鉴权方式需要清晰说明并保持一致

## 质量检查清单（技术特定）

- [ ] 是否使用 `create_app` 工厂模式
- [ ] 路由是否按业务域拆分到 Blueprint
- [ ] 扩展是否统一初始化与注入（Flask-SQLAlchemy 3.x 用 `db.init_app(app)`）
- [ ] 配置是否来自环境与配置对象（而非硬编码）
- [ ] 是否正确理解 `current_app`/`g`/`request` 生命周期（无跨请求共享状态，`g` 不跨 worker）
- [ ] `before_request`/`after_request`/`teardown_request` 职责是否分明（资源释放放 `teardown_request`）
- [ ] 异步视图内是否避免同步阻塞 I/O（或用线程池）
- [ ] 查询是否用 SQLAlchemy 2.0 `select()` 新风格（而非 `Model.query`）
- [ ] 外部输入是否经过校验（Marshmallow/Pydantic）
- [ ] 是否避免滥用 `|safe`/`Markup`（富文本用白名单清洗）
- [ ] 表单/状态变更是否启用 CSRFProtect
- [ ] `SECRET_KEY` 是否来自环境变量；Session/JWT 鉴权是否集中
- [ ] 耗时任务是否外移到 Celery/RQ
- [ ] 信号是否仅用于解耦副作用（非核心业务串联）
- [ ] 生产是否用 Gunicorn/uWSGI（而非 `flask run`）
- [ ] API 错误响应是否统一结构与状态码
- [ ] 核心业务逻辑是否可独立于请求上下文测试

## 参考资料

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Flask Application Factory 模式](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
- [Flask Blueprints](https://flask.palletsprojects.com/en/stable/blueprints/)
- [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
