---
name: tech-django
description: Django开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Django 特定的编码标准与质量检查。
tech_id: django
tech_name: Django
category: framework
---

# Django 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Django 特定规范。

## 技术栈定义

Django 是 Python 生态中成熟的 "batteries-included" 全栈 Web 框架，采用 MTV（Model-Template-View）架构，内置 ORM、中间件、模板引擎、Admin 后台、认证系统与迁移管理。核心特性：ORM 驱动的数据建模、CBV/FBV 双视图体系、中间件管道、自动 Admin、settings 配置驱动。

## 版本基线

- **Django 3.x（已停止支持）**：异步支持引入（3.1 ASGI、3.2 async views），但 ORM 仍以同步为主；仅作遗留项目识别
- **Django 4.2 LTS**：推荐稳定基线；内置 ASGI/异步视图与部分异步 ORM 接口（`acreate`/`aget` 等）；`CSRF_TRUSTED_ORIGINS` 改为含 scheme 的完整 origin（破坏性配置变化）
- **Django 5.0+（破坏性变化）**：最低 Python 3.10+；`USE_L10N` 移除（统一为 `USE_I18N`）；`DEFAULT_FILE_STORAGE`/`STATICFILES_STORAGE` 弃用，改为 `STORAGES` 字典配置；表单渲染默认值调整
- **Django 5.1+**：异步 ORM 查询增强（`aget()`/`acount()` 等扩展），但写操作与复杂查询仍受限于同步数据库驱动；DB 默认连接池（`OPTIONS` 内置 pool）

## 编码规范（技术特定）

### 架构分层

- **Fat Models, Thin Views**：避免把业务逻辑堆进 View/Serializer，业务规则优先沉淀在 Model/Manager/Service（按项目约定）
- **View 职责单一**：View 只做请求编排与输入输出，不承载核心业务规则
- **模板保持简洁**：Template 只负责展示，逻辑搬到 View/Context 或后端处理

### ORM 与数据模型

- **ORM 优先**：以 ORM 表达领域模型与查询逻辑，减少散落的原生 SQL
- **ORM 性能**：使用 `select_related`/`prefetch_related` 规避 N+1 查询；避免循环查询；合理建索引
- **批量操作**：批量写用 `bulk_create`/`bulk_update`（注意 `bulk_update` 需显式指定 `fields` 且不触发 `save()`/信号）；字段级条件用 `F()` 表达式避免竞态，复杂 OR/NOT 用 `Q()` 组合而非 Python 层过滤
- **可扩展用户体系**：项目需要用户体系时优先自定义 `AUTH_USER_MODEL`，避免后续迁移灾难
- **select_for_update 与事务隔离**：在事务内对竞态敏感行使用 `select_for_update` 加行锁；明确 `ATOMIC_REQUESTS` 与显式 `transaction.atomic()` 的取舍，避免长事务持有锁

### DRF（Django REST Framework）

- **Serializer 与 ViewSet 分离**：序列化逻辑收敛在 Serializer，视图逻辑收敛在 ViewSet/GenericView；不在视图里手写字典拼装
- **权限与节流分层**：认证/权限/分页/节流通过 DRF `DEFAULT_AUTHENTICATION_CLASSES`/`DEFAULT_PERMISSION_CLASSES`/`throttle_classes` 统一声明，避免散落
- **嵌套写明确边界**：嵌套写入（WritableNestedSerializer）需显式实现 `create`/`update`，避免隐式覆盖关联对象

### 异步视图与 ASGI

- **异步视图边界**：Django 4.2+ 异步视图（`async def`）仅用于 I/O 等待（外部 HTTP/缓存/异步 ORM 接口）；禁止在 `async def` 视图内调用同步阻塞 ORM/数据库操作，会阻塞事件循环
- **ASGI 部署**：高并发/长连接/SSR 流式场景用 ASGI（Daphne/Uvicorn）；纯同步 CRUD 可仍用 WSGI；混用需保证中间件兼容 async

### 后台任务与 Celery

- **耗时任务外移**：发邮件、报表生成、第三方调用等耗时任务交给 Celery/RQ 等后台任务，不在请求/响应周期内同步执行
- **任务幂等**：后台任务设计为可重试且幂等（带去重键/状态机），避免重试导致重复副作用
- **任务结果与监控**：任务状态/结果可查询（结果后端或业务表标记），失败有告警与重试上限

### 信号（Signals）

- **信号使用边界**：信号仅用于"解耦的副作用"（如用户创建后发欢迎邮件、缓存失效）；核心业务流程不要用信号串联，调用链不可追踪是反模式
- **避免信号反模式**：不要在信号中执行重逻辑或触发其他信号形成链；信号接收器必须可重入

### 迁移管理

- **迁移可回滚**：每个 `RunPython` 必须提供 `reverse_code`；数据迁移与 schema 迁移分离，避免一次性大迁移难以回滚
- **迁移与数据一致性**：数据迁移在 schema 迁移之后单独成 migration；上线前在测试环境验证前向与回滚路径

### 缓存

- **缓存框架统一**：统一用 Django cache 框架（`cache.get`/`cache.set`/`cache.delete`），后端可切换 Redis/Memcached；不散落直接操作 Redis 客户端
- **缓存失效策略**：明确缓存键与失效时机（写时失效/TTL），避免脏数据；缓存击穿用锁或 `cache.get_or_set`

### 配置与安全

- **配置分环境**：配置按环境拆分（如 `base/dev/prod`），避免混杂与误用
- **安全默认值**：利用 Django 内置 CSRF/XSS/SQL 注入防护；外部输入严格校验与清洗
- **敏感信息隔离**：`SECRET_KEY`、数据库密码、第三方密钥必须来自环境变量或安全配置系统，禁止硬编码

### 可测试性

- **业务逻辑可独立测试**：业务逻辑可被独立测试，不依赖请求上下文
- **按项目约定测试**：为核心逻辑与关键接口编写单元/集成测试与回归用例

### 文档化

- **约束可见**：权限模型、错误响应、关键数据约束需要集中说明

## 质量检查清单（技术特定）

- [ ] 业务逻辑是否沉淀在 Model/Manager/Service，而非堆在 View/Serializer
- [ ] 查询是否使用了 `select_related`/`prefetch_related` 规避 N+1
- [ ] 批量写是否用 `bulk_create`/`bulk_update`（注意不触发 save/信号）
- [ ] 字段级条件是否用 `F()`，复杂条件是否用 `Q()`（而非 Python 层过滤）
- [ ] 竞态敏感行是否在事务内用 `select_for_update`
- [ ] 用户体系是否使用了自定义 `AUTH_USER_MODEL`（而非直接扩展 User）
- [ ] DRF 序列化是否收敛在 Serializer，权限/节流是否统一声明
- [ ] 异步视图内是否避免同步阻塞 ORM/数据库操作
- [ ] 耗时任务是否外移到 Celery/RQ，且任务幂等可重试
- [ ] 信号是否仅用于解耦副作用（非核心业务串联）
- [ ] `RunPython` 是否提供 `reverse_code`，数据/schema 迁移是否分离
- [ ] 缓存是否统一走 cache 框架，失效策略明确
- [ ] settings 是否按环境拆分（base/dev/prod）
- [ ] `SECRET_KEY` 与密钥是否来自环境变量
- [ ] 是否启用了 Django 内置 CSRF/XSS/SQL 注入防护
- [ ] 外部输入是否经过校验与清洗
- [ ] 核心业务逻辑是否可独立于请求上下文测试

## 参考资料

- [Django 官方文档](https://docs.djangoproject.com/)
- [Django ORM 参考](https://docs.djangoproject.com/en/stable/ref/models/)
- [Django 安全最佳实践](https://docs.djangoproject.com/en/stable/topics/security/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
