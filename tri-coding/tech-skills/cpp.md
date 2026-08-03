---
name: tech-cpp
description: C++ 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 C++ 特定的编码标准与质量检查。
tech_id: cpp
tech_name: C++
category: language
---

# C++ 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 C++ 特定规范。

## 技术栈定义

C++ 是静态类型、编译型语言，以零开销抽象、手动资源控制和高性能著称。现代 C++（C++11/14/17/20）通过 RAII、智能指针、移动语义、auto 类型推导、lambda 等特性，在性能与安全之间取得平衡。适合构建系统软件、游戏引擎、嵌入式和高性能服务，通过 CMake 管理构建。

## 版本基线

- **C++17（实用特性基线）**：引入 `std::optional`/`std::variant`/`std::any`、`std::string_view`（零拷贝字符串视图）、结构化绑定（structured bindings）、`if constexpr`、折叠表达式、`std::filesystem`、内联变量。属主流编译器与库的事实基线；同时移除部分 deprecated 特性（如 `std::auto_ptr`、`std::tr1`），属破坏性变化
- **C++20（范式级演进）**：引入 Concepts（概念约束）、Ranges（范围库）、Coroutines（协程）、Modules（模块化）、`<=>` 三向比较、指定初始化、`std::span`、`std::format`。Modules 与传统头文件机制互斥并存，影响构建系统与 CMake 配置；Ranges/Concepts 改变模板 API 设计范式，属破坏性演进，需校验编译器版本（GCC 10+/Clang 10+/MSVC 19.29+）与标准库实现完整度
- **C++23（标准库增强）**：新增 `std::expected`（错误处理语义类型，替代异常/返回码的折中方案）、`std::print`/`std::println`（类型安全格式化输出）、`std::flat_map`/`std::flat_set`、`std::generator` 协程、`if consteval`、多维下标运算符。`std::print` 替代 `printf`/`iostream` 部分场景，类型更安全；部分特性依赖较新编译器（GCC 14+/Clang 18+/MSVC 19.39+）

## 编码规范（技术特定）

### 资源管理（RAII）

- **RAII 优先**：使用 RAII（Resource Acquisition Is Initialization）管理资源生命周期，资源获取即对象构造，资源释放即对象析构
- **智能指针**：使用 `std::unique_ptr`（独占所有权）、`std::shared_ptr`（共享所有权）管理动态内存，避免裸 `new`/`delete`
- **避免裸指针所有权**：除与 C 接口交互或性能关键路径外，避免使用裸指针管理资源所有权
- **异常安全**：保证代码具备基本异常安全保证，避免资源泄漏

### 类型安全

- 充分利用 C++ 类型系统，减少不安全的类型转换
- 避免 C 风格强制转换（`(T)x`），使用 `static_cast`/`dynamic_cast`/`reinterpret_cast` 等具名转换
- 使用 `auto` 进行类型推导，提高可读性与可维护性

### 移动语义

- 优先实现移动构造与移动赋值，避免不必要的深拷贝
- 使用 `std::move` 转移所有权，使用 `std::forward` 完美转发
- 大对象按值传递时考虑移动语义而非拷贝

### 现代 C++ 特性使用

- 优先使用 STL 容器与算法（`std::vector`、`std::string`、`std::algorithm`），避免手写数据结构
- 使用 `constexpr`/`consteval` 进行编译期计算
- 使用 lambda 表达式与 `std::function` 进行函数式编程
- 使用范围 for、结构化绑定等提高可读性

### 构建管理

- 使用 CMake 管理构建过程，目标（target）划分清晰
- 区分头文件与源文件目录结构，保持模块边界清晰

### 智能指针细化

- **make_unique/make_shared 优先**：使用 `std::make_unique`/`std::make_shared` 创建智能指针，避免裸 `new` 带来的异常安全与二次内存分配问题
- **weak_ptr 打断循环**：共享所有权场景出现循环引用时，使用 `std::weak_ptr` 打断环，并通过 `lock()` 提升为 `shared_ptr` 前判空
- **unique_ptr 自定义删除器**：管理 C 接口资源（FILE*/fd/handle）时使用 `std::unique_ptr<T, Deleter>` 配合自定义删除器，避免资源泄漏

### const 与 noexcept

- **const 正确性**：对所有不应修改的成员函数、参数、局部变量使用 `const`，遵循 const-correctness 原则，提升接口可表达性与编译期优化空间
- **noexcept 标注**：对不抛异常的函数（移动构造、析构、swap 等）显式标注 `noexcept`，提升移动语义与 STL 容器性能
- **constexpr 编译期计算**：优先使用 `constexpr`/`constinit`/`consteval` 将计算前移到编译期，避免运行期开销

### 模板与概念

- **概念约束（Concepts）**：C++20 起优先使用 Concepts（`template <std::integral T>`）替代 SFINAE/`static_assert`，让模板约束更清晰
- **模板特化规范**：模板特化不应破坏原模板语义，全特化需放在源文件而非头文件以避免 ODR（One Definition Rule）冲突
- **CRTP 静态多态**：性能关键场景使用 CRTP（Curiously Recurring Template Pattern）实现静态多态，避免虚函数开销

### 现代 C++ 标准库

- **std::string_view**：函数参数优先使用 `std::string_view` 接收只读字符串，避免不必要的 `std::string` 拷贝
- **std::optional/std::variant**：使用 `std::optional` 表达可缺失值，`std::variant` 表达类型安全的联合体，替代裸指针/nullptr 与 union
- **std::expected**：C++23 起优先使用 `std::expected<T,E>` 表达可能失败的计算，避免异常的开销与控制流跳跃
- **范围库（Ranges）**：C++20 起使用 `std::ranges` 算法与视图，配合管道式 `|` 组合，提升链式表达可读性

### 并发编程

- **并发原语选型**：使用 `std::jthread`/`std::thread`、`std::mutex`/`std::scoped_lock`/`std::lock_guard`、`std::atomic` 管理并发，避免数据竞争（UB）
- **scoped_lock 多锁**：同时锁定多个互斥量时使用 `std::scoped_lock`（C++17）避免死锁，禁止手写 lock 顺序
- **atomic 无锁编程**：简单标志/计数器优先 `std::atomic`，明确内存序（`memory_order_relaxed`/`acquire`/`release`），避免无谓的顺序一致性开销

### 头文件与命名空间

- **头文件自包含**：头文件使用 include guard 或 `#pragma once`，并保证自包含（self-contained），前向声明减少编译依赖
- **命名空间隔离**：避免在头文件中 `using namespace std`，使用命名空间隔离模块 API，避免全局命名空间污染
- **内存对齐**：使用 `alignas`/`alignof` 控制对齐，避免未对齐访问导致的 UB 与性能损失
- **未定义行为规避**：禁止依赖未定义行为（有符号整数溢出、空指针解引用、悬垂指针、越界访问），开启 `-fsanitize=undefined` 验证

## 质量检查清单（技术特定）

### 资源管理

- [ ] 动态内存是否使用智能指针（`unique_ptr`/`shared_ptr`）管理
- [ ] 是否避免裸 `new`/`delete` 操作
- [ ] 资源获取是否遵循 RAII 模式
- [ ] 代码是否具备基本异常安全保证（无资源泄漏）

### 类型安全

- [ ] 是否避免 C 风格强制转换，使用具名转换
- [ ] 是否合理使用 `auto` 提高可读性

### 现代特性

- [ ] 是否优先使用 STL 容器与算法
- [ ] 大对象是否实现/使用移动语义避免深拷贝
- [ ] 是否使用 `constexpr` 进行编译期计算

### 构建

- [ ] CMake 目标划分是否清晰
- [ ] 模块边界是否与架构文档一致

## 参考资料

- [cppreference.com](https://en.cppreference.com/) - C++ 标准库权威参考
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) - C++ 核心准则
- [Modern C++ Features](https://github.com/AnthonyCalandra/modern-cpp-features) - 现代 C++ 特性汇总
- [CMake 官方文档](https://cmake.org/documentation/) - 构建系统文档
- [Effective Modern C++](https://www.oreilly.com/library/view/effective-modern-c/9781491908419/) - Scott Meyers
