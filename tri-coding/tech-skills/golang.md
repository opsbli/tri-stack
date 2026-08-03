---
name: tech-golang
description: Go 语言开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Go 特定的编码标准与质量检查。
tech_id: golang
tech_name: Go
category: language
---

# Go 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Go 特定规范。

## 技术栈定义

Go 是 Google 推出的静态类型、编译型语言，以简洁语法、原生并发支持（goroutine/channel）、高效编译和强大标准库著称。适合构建高并发后端服务、云原生应用和命令行工具，强调"少即是多"的工程哲学，通过 `go mod` 管理依赖、`go fmt` 统一代码风格。

## 版本基线

- **Go 1.18+（泛型引入）**：引入类型参数（type parameters）与泛型，标准库开始提供 `constraints` 包（1.21 起迁至 `cmp`/`slices`/`maps`）；为库设计带来范式转变，新增泛型约束语法（`[T any]`、`interface{ ~int }`）。属 Go 最重要的语言级演进，影响可复用数据结构与算法的写法，升级需重新评估第三方库的泛型依赖
- **Go 1.21+（slog / errors.Join）**：标准库新增结构化日志包 `log/slog`，统一日志抽象；`errors.Join` 支持合并多个错误；`slices`、`maps`、`cmp` 包进入标准库，替代大量第三方工具库。注意 1.21 起引入 toolchain directive 与 `GODEBUG` 版本管理机制，旧项目升级需校验 `go.mod` 与依赖兼容性
- **Go 1.22+（range over int / for range func）**：`for range` 支持整数范围（`for i := range 10`）与函数迭代器（`for range func(yield func(T) bool)`），简化循环写法；同时修复 `for` 循环变量复用问题（loop var per-iteration），属语义级破坏性变化，依赖旧闭包捕获循环变量行为的外部库需重新测试

## 编码规范（技术特定）

### 命名规范

- **包名**：使用小写单词，不使用下划线或混合大小写（如 `model`、`logic`）
- **文件命名**：使用小写字母，下划线分隔（如 `user_service.go`）
- **变量命名**：驼峰命名法。局部变量小驼峰（`userID`），全局变量大驼峰（`UserService`）
- **常量命名**：全大写，下划线分隔（`MAX_RETRY_COUNT`）
- **接口/结构体**：大驼峰。接口以 "er" 结尾（如 `Reader`），避免 "I" 前缀

### 代码组织

- **结构体字段顺序**：导出字段在前，非导出字段在后
- **函数顺序**：类型/常量 -> 变量 -> `init()` -> 方法（按重要性）
- **Import 分组**：标准库 -> 第三方库 -> 内部包，分组间空行分隔

### 架构模式

- **DDD 分层架构**：`controller`（HTTP 请求、参数验证）-> `logic`（核心业务逻辑）-> `model`（数据访问、数据结构定义）-> `framework`（基础设施）
- **依赖方向**：严格遵循 `controller -> logic -> model`，禁止循环依赖

### 错误处理

- 使用 `common.Error` 统一封装业务错误
- 逻辑层使用 `errors.Wrap` 保留堆栈信息
- 只在错误源头记录日志，避免重复记录

### 并发处理

- 使用 `context` 进行超时控制和取消传播
- 使用 `mutex`/`atomic`/`channel` 保护共享资源
- 避免 Goroutine 泄漏，使用 `errgroup` 管理并发生命周期

### 性能优化

- 预分配切片/Map 容量（`make([]T, 0, n)`）
- 大结构体使用指针传递，避免值拷贝
- 使用 `sync.Pool` 复用对象，减少 GC 压力
- 使用缓冲 IO 和批量 DB 操作

### 可测试性

- 使用**表驱动测试**（Table-driven Tests）方法
- 测试文件与源码同目录（`xxx_test.go`）
- 使用接口和依赖注入 Mock 外部依赖
- 为性能关键路径编写 Benchmark

### 文档化

- 为导出函数/结构体编写清晰文档注释（以函数名开头）
- API 文档清晰描述接口用途、参数和返回值

### 并发模式

- **Goroutine 生命周期管理**：每个 goroutine 必须有明确退出路径，使用 `context.Context` 或 `errgroup.Group` 统一管理，禁止裸 `go func()` 无控制启动
- **Channel 方向约束**：函数参数中 channel 显式标注方向（`chan<- T`/`<-chan T`），表达生产/消费意图，编译期防误用
- **Context 传播**：所有可能阻塞的函数首参必为 `context.Context`，禁止将 `context.Background`/`TODO` 作为参数传入，避免上下文丢失取消信号

### 错误处理细化

- **错误包装（Error Wrapping）**：使用 `fmt.Errorf("xxx: %w", err)` 包装错误保留链路，调用方通过 `errors.Is`/`errors.As` 解包判断类型，Go 1.20+ 可用 `errors.Join` 合并多错误
- **错误哨兵值**：包级错误变量以 `Err` 前缀命名（`var ErrNotFound = errors.New(...)`），可比较错误使用 `errors.Is`，避免字符串匹配判断错误类型

### 接口与包设计

- **接口隔离**：接口定义在消费方而非实现方，保持小接口（单一方法优先），通过组合（embedding）构建大接口，遵循"接受接口返回结构体"惯例
- **包内聚**：一个包只做一件事，避免 `utils`/`common` 大杂烩包，包名与目录名一致且为单数小写
- **零值可用**：类型设计尽量"零值可用"（zero value），减少 `NewXXX` 工厂函数与初始化样板代码

### 资源与标签

- **defer 资源释放**：资源获取后立即 `defer` 释放（`defer f.Close()`），循环中的 defer 需封装为函数调用，避免 defer 栈堆积
- **结构体标签**：JSON/DB/校验字段使用 struct tag 显式声明（`` `json:"name,omitempty"` ``），输出字段名遵循 snake_case，避免大小写不一致问题

## 质量检查清单（技术特定）

### 命名与组织

- [ ] 包名是否符合小写单词规范（无下划线、无混合大小写）
- [ ] 接口命名是否以 "er" 结尾（如 `Reader`、`Writer`）
- [ ] Import 是否按标准库/第三方/内部包分组
- [ ] 结构体字段是否导出字段在前

### 并发与错误

- [ ] 共享资源是否使用 `mutex`/`atomic`/`channel` 保护
- [ ] Goroutine 是否有明确退出机制（避免泄漏）
- [ ] 是否使用 `context` 进行超时控制
- [ ] 错误是否使用 `errors.Wrap` 保留堆栈
- [ ] 是否避免在多处重复记录同一错误日志

### 性能

- [ ] 切片/Map 是否预分配容量
- [ ] 大结构体是否使用指针传递
- [ ] 性能关键路径是否使用 `sync.Pool` 复用对象

### 测试

- [ ] 关键逻辑是否使用表驱动测试
- [ ] 测试文件是否与源码同目录（`_test.go`）
- [ ] 性能关键路径是否有 Benchmark

## 参考资料

- [Effective Go](https://go.dev/doc/effective_go) - Go 官方最佳实践
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments) - Go 代码评审规范
- [Go 官方文档](https://go.dev/doc/) - 语言与标准库文档
- [Go Concurrency Patterns](https://go.dev/blog/pipelines) - 并发模式指南
- [Go Modules Reference](https://go.dev/ref/mod) - 包管理官方参考
