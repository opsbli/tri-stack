---
name: tech-java
description: Java 语言开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Java 特定的编码标准与质量检查。
tech_id: java
tech_name: Java
category: language
---

# Java 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Java 特定规范。

## 技术栈定义

Java 是面向对象、跨平台、强类型的编译型语言，运行于 JVM 之上，以"一次编写、到处运行"、成熟生态（Spring/Spring Boot）、完善异常体系和强并发支持著称。适合构建企业级后端服务、分布式系统，通过 Maven/Gradle 管理依赖。

## 版本基线

- **Java 17 LTS（语法现代化基线）**：引入 `sealed` 类/接口、`record` 不可变数据载体、`switch` 模式匹配（pattern matching for switch，预览至 21 正式）、文本块（text blocks）。属长期支持基线，多数主流框架与工具链以 Java 17 为最低运行版本；强封装 JDK 内部 API（`--illegal-access` 失效）、`SecurityManager` 弃用，影响依赖反射/序列化的旧框架
- **Java 21 LTS（并发模型演进）**：虚拟线程（Virtual Thread / `Thread.ofVirtual`）正式发布，显著提升 IO 密集型吞吐；结构化并发（Structured Concurrency）与作用域值（Scoped Values）以预览特性引入；新增 `SequencedCollection` 等有序集合接口。注意：虚拟线程与 `synchronized`/`ThreadLocal` 的交互有限制（pinning 问题），迁移时需审查锁使用与 `ThreadLocal` 依赖
- **Spring Boot 3.x（生态迁移）**：命名空间从 `javax.*` 全面迁移到 `jakarta.*`（Servlet/JPA/Validation），属破坏性变化，旧依赖、自定义 starter 与第三方库必须同步升级；最低基线提升至 Java 17；原生镜像（GraalVM Native Image）支持通过 Spring AOT 落地，影响构造期与运行期行为（如反射、动态代理需显式注册）

## 编码规范（技术特定）

### 架构分层

- **Controller**：仅处理 HTTP 请求/响应、参数校验，不包含业务逻辑
- **Service**：包含核心业务逻辑，事务边界（`@Transactional`）
- **Repository**：数据访问层，优先使用 Spring Data JPA 或 MyBatis 接口

### 依赖注入（IoC）

- **构造器注入优先**：优先使用构造器注入（Constructor Injection）而非字段注入（`@Autowired` on field），以保证不可变性和易测试性。推荐使用 Lombok 的 `@RequiredArgsConstructor`
- **Bean 生命周期**：理解 Bean 的生命周期和作用域（Singleton、Prototype）

### 配置管理

- **application.yml**：优先使用 YAML 格式配置
- **@ConfigurationProperties**：使用类型安全的配置类读取属性，避免直接使用 `@Value` 散落在代码中
- **Profiles**：使用 Profiles（`dev`、`prod`、`test`）隔离不同环境的配置

### 异常与响应

- **统一异常处理**：使用 `@RestControllerAdvice` 和 `@ExceptionHandler` 进行全局异常处理，返回统一的 API 响应格式
- **精准错误处理**：使用 try/catch 捕获预期异常，提供有意义的错误上下文，避免静默吞掉错误
- **入参校验**：使用 Bean Validation（JSR-380）注解（`@NotNull`、`@Size`）验证入参

### 日志记录

- 优先使用日志框架（如 SLF4J、Logback）记录错误信息，避免使用 `System.out.println`

### 异步处理

- 使用 `CompletableFuture` 或 `@Async`，错误处理模式统一

### 类型安全

- 充分利用 Java 的强类型系统，避免不安全的类型转换

### 可测试性

- 编写可测试的代码，依赖抽象（接口），方便 Mock/Stub
- 使用 `final` 修饰不可变变量
- 在代码的关键逻辑处添加调试日志

### 文档化

- 符合官方 Javadoc 注释规范

### 泛型与集合

- **泛型使用**：优先使用泛型（`List<T>`）替代裸类型（raw type `List`），通配符遵循 PECS 原则（Producer `extends`、Consumer `super`）
- **集合选型**：根据场景选择合适集合（`ArrayList` 随机访问、`LinkedList` 队列、`HashMap` 键值、`ConcurrentHashMap` 并发），禁止在 foreach 中直接增删元素（用 `Iterator.remove` 或 `removeIf`）
- **Stream API**：集合批量操作优先使用 Stream API（`stream().filter().map().collect()`），副作用操作避免在 `peek` 中执行，并行流谨慎使用（需线程安全的下游操作）

### 并发与异步

- **并发工具**：优先使用 `java.util.concurrent` 包工具（`ExecutorService`/`CompletableFuture`/`CountDownLatch`/`ConcurrentHashMap`），避免手写 `wait`/`notify` 与 `synchronized` 大粒度锁
- **虚拟线程**：Java 21+ IO 密集型场景优先使用虚拟线程（`Thread.ofVirtual`/`Executors.newVirtualThreadPerTaskExecutor`），注意避免 `synchronized` 长时占用导致 pinning

### 现代特性与异常

- **Optional 表达可空**：方法返回值用 `Optional<T>` 表达可能缺失的结果，禁止将 `Optional` 作为字段或参数类型，避免 `Optional.of(null)` 改用 `Optional.ofNullable`
- **try-with-resources**：实现 `AutoCloseable` 的资源（IO/DB 连接/锁）使用 try-with-resources 自动关闭，避免 `finally` 中手动 close 漏关或异常掩盖
- **异常分类**：受检异常（Checked）用于可恢复业务异常，非受检异常（`RuntimeException`）用于编程错误，自定义业务异常继承 `RuntimeException` 避免接口签名污染
- **Record 不可变数据**：Java 16+ 优先使用 `record` 表达纯数据载体（DTO/VO），替代 Lombok `@Data` 样板代码，保证不可变性与相等性语义
- **注解约定**：自定义注解通过 `@Target`/`@Retention` 明确作用范围与生命周期，组合注解（meta-annotation）提升可读性，避免滥用注解做隐式逻辑分支
- **模块化（JPMS）**：库类项目考虑使用 `module-info.java` 显式声明依赖与导出包，避免类路径（classpath）全可见带来的隐式耦合

## 质量检查清单（技术特定）

### 架构与依赖注入

- [ ] Controller 是否仅处理 HTTP 请求/响应，不包含业务逻辑
- [ ] Service 层是否使用 `@Transactional` 划分事务边界
- [ ] 是否优先使用构造器注入（而非字段 `@Autowired`）
- [ ] 是否使用 `@ConfigurationProperties` 而非散落的 `@Value`

### 异常与校验

- [ ] 是否使用 `@RestControllerAdvice` 统一异常处理
- [ ] API 响应格式是否统一
- [ ] 入参是否使用 Bean Validation 注解校验
- [ ] 是否避免静默吞掉异常

### 配置与日志

- [ ] 是否使用 Profiles 隔离环境配置
- [ ] 是否使用 SLF4J/Logback 而非 `System.out.println`
- [ ] 是否避免硬编码（使用常量或枚举替代）

### 测试

- [ ] 核心逻辑是否依赖抽象（接口）以便 Mock
- [ ] 不可变变量是否使用 `final` 修饰

## 参考资料

- [Java 编码规范](https://www.oracle.com/java/technologies/javase/codeconventions-contents.html) - Oracle 官方编码规范
- [Spring Boot 最佳实践](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#best-practices) - Spring 官方指南
- [JSR-380 Bean Validation](https://beanvalidation.org/2.0-jsr380/) - 入参校验规范
- [Maven 官方文档](https://maven.apache.org/guides/) - 依赖管理与构建
- [Effective Java](https://www.oreilly.com/library/view/effective-java/9780134686097/) - Joshua Bloch
