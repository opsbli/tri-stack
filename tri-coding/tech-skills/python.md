---
name: tech-python
description: Python 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Python 特定的编码标准与质量检查。
tech_id: python
tech_name: Python
category: language
---

# Python 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Python 特定规范。

## 技术栈定义

Python 是动态类型的解释型语言，以简洁可读著称。核心特性包括：PEP 8 风格规范、类型提示（Type Hints）、虚拟环境与包管理、异步（asyncio）、上下文管理器、丰富的标准库与生态。Python 3.x 适用于 Web 后端、数据处理、自动化、AI/ML 等场景。

## 版本基线

- **Python 3.10（2021）**：结构化模式匹配 `match-case`（PEP 634）、`X | Y` 联合类型注解语法（PEP 604，`int | str` 替代 `Union[int, str]`）、括号内上下文管理器多对象 `with (A() as a, B() as b):`、`zip` 严格模式 `strict=True`。3.10 是当前多数项目基线版本
- **Python 3.11（2022）**：性能提升（CPython 解释器优化，典型提升 10–60%）、`ExceptionGroup` 与 `except*`（PEP 654）、`asyncio.TaskGroup`（PEP 654，结构化并发）、`Self` 类型（PEP 673）、`Required`/`NotRequired`（PEP 655）、异常 `add_note`。引入"友好回溯"显著改善调试体验
- **Python 3.12（2023）**：PEP 695 类型参数语法（`def func[T](x: T) -> T:`、`type Point = tuple[float, float]` 类型别名语句）、f-string 解析器重写（支持嵌套引号、换行、任意表达式）、per-interpreter GIL（PEP 683，实验性）、弃用大量旧 distutils/bdb 模块
- **破坏性变化提示**：3.9 已移除 `collections` 别名（`collections.Mapping` 等需改 `collections.abc`）；3.10 起 `distutils` 标记弃用并于 3.12 移除；3.12 起 `imp` 模块移除；`asyncio` 在 3.12 中 `Task` 默认循环引用回收导致"Task was destroyed but it is pending!"行为变化

## 编码规范（技术特定）

### 风格与命名（PEP 8）

- **遵循 PEP 8**：保持一致的格式与命名风格
- **命名规范**：
  - 变量/函数/方法/模块：`snake_case`
  - 类名：`PascalCase`
  - 常量：`UPPER_SNAKE_CASE`
  - 私有成员：`_leading_underscore`
- **显式优于隐式**：逻辑要直观，避免"聪明但难懂"的写法

### 设计哲学（Zen of Python）

- **Zen of Python**：优美胜于丑陋，简单胜于复杂，扁平胜于嵌套
- **模块化与边界**：将 I/O（数据库、网络、文件）与业务规则分离，避免耦合
- **抽象克制**：列表推导式/生成器表达式用于简单场景；复杂逻辑使用普通循环以保证可读性

### 类型提示与异常处理

- **类型提示**：为公共函数签名与关键数据结构添加类型提示，并按项目约定使用类型检查工具（如 mypy/pyright）
- **异常处理**：捕获具体异常，保留上下文，禁止裸 `except:`
- **资源管理**：文件、锁、连接必须使用 `with` 上下文管理器正确释放
- **边界校验**：外部输入必须在边界层校验与清洗，不把"数据一定正确"当作前提
- **异步处理标准化**：使用 `async/await`，错误处理模式统一

### 现代语法与并发

- **善用 `match-case` 结构化模式匹配**（3.10+）：对多分支状态机、解构数据（`match point: case Point(x=0, y=y)`）、`Enum` 分发等场景使用 `match-case` 替代长 `if/elif` 链；简单布尔判断仍用 `if`
- **使用 `TaskGroup` 结构化并发**（3.11+）：并发任务优先用 `async with asyncio.TaskGroup() as tg: tg.create_task(...)`，自动收集异常为 `ExceptionGroup` 并在任一任务失败时取消其余；弃用手动 `gather(..., return_exceptions=True)` + 手工取消的脆弱模式
- **异常组与 `except*`**（3.11+）：当需要同时处理多个同类型异常或并发框架抛出的 `ExceptionGroup` 时使用 `except* ValueError`；普通单一异常路径仍用 `except`
- **取消传播规范**：协程必须响应 `CancelledError`——捕获后必须 `raise` 重抛（除非在清理路径中），禁止吞掉取消信号；`asyncio.timeout`/`wait_for` 依赖该语义

### 包管理与数据建模

- **统一包管理与虚拟环境**：项目必须使用 `pyproject.toml` 作为唯一构建/依赖元数据来源；库与应用按场景选型——应用用 `uv`（极快解析+锁定）或 `poetry`，库用 `hatch`/`setuptools`；禁止把依赖直接装进系统解释器，必须用 `venv`/`virtualenv` 隔离；锁文件（`uv.lock`/`poetry.lock`）提交版本库
- **数据建模选型**：纯数据容器优先 `dataclass`（标准库零依赖，配合 `frozen=True` 实现不可变）；外部边界（HTTP/配置/数据库）入参校验用 `pydantic`（v2 起基于 Rust 核心性能好）；需要 `__slots__`/细粒度校验/性能极致时用 `attrs`；禁止在同一项目混用三套模型体系
- **类型参数语法**（3.12+）：泛型函数/类用 PEP 695 新语法 `def first[T](xs: list[T]) -> T:` 替代 `TypeVar` + `Generic`；类型别名用 `type` 语句 `type Vector = list[float]` 替代 `Vector = list[float]`，获得更好的作用域与错误信息

### 测试规范

- **测试框架与 fixture**：统一使用 `pytest`；跨用例共享的 setUp 数据用 `@pytest.fixture`，作用域按需选 `function`/`session`；禁止在测试中复制粘贴构造逻辑
- **Mock 边界**：用 `unittest.mock.patch`/`AsyncMock` 仅替换外部依赖（HTTP/时钟/文件系统），禁止 mock 被测代码自身内部方法；断言调用次数用 `assert_called_once_with` 而非手动检查

### 文档化

- **Docstrings**：公共 API 使用一致的 Docstring 风格（Google/NumPy 任选其一并保持一致）
- **约束说明**：对重要边界条件、异常语义、性能假设进行简洁说明

## 质量检查清单（技术特定）

- [ ] 是否遵循 PEP 8 命名规范（snake_case/PascalCase/UPPER_SNAKE_CASE）
- [ ] 公共函数与关键数据结构是否添加类型提示
- [ ] 是否按项目约定运行类型检查工具（mypy/pyright）
- [ ] 异常处理是否捕获具体异常，禁止裸 `except:`
- [ ] 文件/锁/连接是否使用 `with` 上下文管理器
- [ ] 外部输入是否在边界层校验与清洗
- [ ] 公共 API 是否提供一致的 Docstring（Google/NumPy 风格）
- [ ] I/O 是否与业务规则分离
- [ ] 多分支/解构场景是否使用 `match-case`（3.10+）替代冗长 `if/elif`
- [ ] 并发任务是否使用 `asyncio.TaskGroup`（3.11+）并正确处理取消传播
- [ ] 包管理是否统一到 `pyproject.toml`，是否使用虚拟环境隔离且锁文件入库
- [ ] 数据建模选型（dataclass/pydantic/attrs）是否与场景匹配，是否避免混用
- [ ] 泛型/类型别名是否采用 PEP 695 新语法（3.12+）
- [ ] 测试是否使用 pytest fixture 共享数据，是否仅 mock 外部依赖而非被测代码内部

## 参考资料

- [Python 官方文档](https://docs.python.org/3/)
- [PEP 8 风格指南](https://peps.python.org/pep-0008/)
- [PEP 484 类型提示](https://peps.python.org/pep-0484/)
- [PEP 634 结构化模式匹配](https://peps.python.org/pep-0634/)
- [PEP 654 异常组与 TaskGroup](https://peps.python.org/pep-0654/)
- [PEP 695 类型参数语法](https://peps.python.org/pep-0695/)
- [The Zen of Python (PEP 20)](https://peps.python.org/pep-0020/)
- [Google Python 风格指南](https://google.github.io/styleguide/pyguide.html)
- [pydantic v2 文档](https://docs.pydantic.dev/latest/)
