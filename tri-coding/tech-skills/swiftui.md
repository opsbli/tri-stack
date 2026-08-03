---
name: tech-swiftui
description: SwiftUI 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 SwiftUI 框架与 Swift 语言特定的编码标准与质量检查。
tech_id: swiftui
tech_name: SwiftUI
category: framework
---

# SwiftUI 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 SwiftUI 与 Swift 特定规范。

## 技术栈定义

SwiftUI 是 Apple 推出的声明式 UI 框架，使用 Swift 语言构建跨 Apple 平台（iOS/macOS/watchOS/tvOS）应用。核心特性：声明式 UI 范式、View 协议、修饰符链（Modifier Chain）、Property Wrappers 状态管理、单一数据源（Source of Truth）、Preview 实时预览。

## 版本基线

- **iOS 13+ / macOS 10.15+**：SwiftUI 1.0 首发，确立声明式 UI 范式与 `NavigationView` 导航体系；建议作为最低部署目标评估基线
- **iOS 15+**：引入 `AsyncImage`、`@FocusState`、`refreshable`、`AttributedString`；Swift Concurrency（async/await）落地，`@MainActor`/`Sendable` 引入
- **iOS 16+（破坏性变化）**：`NavigationStack`/`NavigationSplitView` 替代 `NavigationView`（旧 API 进入弃用周期）；新增 `Grid`/`AnyLayout`/`Table`/Charts 框架；导航从命令式 push/pop 转向值驱动的 `navigationDestination`
- **iOS 17+（破坏性变化）**：`@Observable` 宏替代 `ObservableObject`+`@Published`（旧写法仍兼容，新项目优先用宏）；`#Preview` 宏替代 `PreviewProvider` 协议；`@Bindable` 配合 `@Observable`；`@State` 可直接持有引用类型（语义扩展）；`withAnimation` 增加 completion handler

## 编码规范（技术特定）

### 声明式 UI 与视图

- **声明式语法**：遵循声明式 UI 范式，描述"UI 应该是什么样"，而不是"怎么修改 UI"
- **小组件**：将复杂的视图拆解为小的、可复用的 `View` 结构体，单个 `body` 避免嵌套过深
- **Preview 优先**：为每个视图提供预览；iOS 17+ 使用 `#Preview` 宏替代 `PreviewProvider` 协议，旧项目沿用 `PreviewProvider` 时保持一致即可
- **Layout**：熟练使用 `HStack`/`VStack`/`ZStack`/`LazyHStack`/`LazyVStack`；长列表用 `List`/`LazyVStack` 懒加载，避免一次性渲染全部子视图
- **Modifiers 顺序**：理解修饰符顺序对布局的影响（如 `padding` 与 `background` 的顺序），将"影响布局"与"影响外观"的修饰符分组编排

### 导航（iOS 16+）

- **NavigationStack 取代 NavigationView**：iOS 16+ 必须使用 `NavigationStack`，配合 `navigationDestination(for:)` 进行值驱动的导航，避免使用已弃用的 `NavigationView`
- **NavigationSplitView 用于分栏**：iPad/macOS 分栏场景使用 `NavigationSplitView`，不要用 `NavigationView` 模拟分栏
- **路由数据化**：将导航目标建模为 `Hashable` 值/枚举，导航路径由数据驱动（`navigationDestination` + path binding），便于测试与深度链接

### 状态管理（Property Wrappers）

- **iOS 17+ 优先用 @Observable**：新项目用 `@Observable` 宏替代 `ObservableObject`+`@Published`；在视图中用 `@State`（拥有）或 `@Bindable`（绑定）持有，消除 `@StateObject`/`@ObservedObject` 的拥有者歧义
- **正确使用 Property Wrappers（iOS 16 及以下）**：
  - `@State`：视图私有的简单状态
  - `@Binding`：父子视图间的双向绑定
  - `@StateObject`：视图拥有的引用类型数据源（生命周期管理）
  - `@ObservedObject`：外部传入的引用类型数据源
  - `@EnvironmentObject`：跨层级全局数据
- **Source of Truth**：坚持"单一数据源"原则，数据沿一个方向流动，子视图通过 `@Binding` 回写而非各自持有副本
- **避免在 body 中产生副作用**：`body` 必须保持纯函数语义，副作用放到 `onAppear`/`.task`/按钮 action 中

### 架构模式

- **MVVM**：推荐使用 MVVM 模式
  - **Model**：数据结构
  - **View**：SwiftUI 视图
  - **ViewModel**：`@Observable` 类（iOS 17+）或 `ObservableObject` 类，处理业务逻辑，将数据转换为视图可用的形式
- **环境值收敛**：跨层级共享的依赖（如服务、配置）通过 `Environment`/`@Environment` 注入，避免层层透传

### 类型安全与异步

- **类型安全强化**：充分利用 Swift 的强类型系统，优先用枚举表达有限状态，避免字符串/魔数
- **Swift Concurrency 优先**：I/O 与耗时操作使用 `async/await`；标注 `@MainActor` 确保 UI 更新在主线程；跨 actor 边界的模型实现 `Sendable`
- **.task 与 onAppear 取舍**：异步初始化用 `.task`（自动跟随视图生命周期取消）；纯同步且无需取消的一次性副作用可用 `onAppear`；不要在 `onAppear` 中手写 `Task { }` 替代 `.task`
- **Task 取消与资源释放**：长任务在 `.task` 中检查 `Task.isCancelled` 或使用协作式取消，避免视图销毁后继续占用资源
- **Combine 与 AsyncSequence 取舍**：新代码优先用 `AsyncSequence`/`AsyncStream` 消费流式数据；仅当需要复杂操作符链（debounce/throttle/合并多源）且已有 Combine 管线时才使用 Combine，避免两套并存的混合心智负担

### Accessibility

- **可访问性默认化**：所有可交互控件提供 `accessibilityLabel`/`accessibilityHint`；图标按钮必须显式标注
- **语义分组**：用 `accessibilityElement(children: .combine)` 将一组相关视图合并为单个可访问性元素，减少 VoiceOver 噪音
- **动态类型支持**：使用语义字体（`.title`/`.body` 等）以支持 Dynamic Type，避免硬编码字号与固定高度导致文本截断

## 质量检查清单（技术特定）

- [ ] 是否遵循声明式 UI 范式，描述"UI 是什么样"而非"怎么修改"
- [ ] 复杂视图是否拆解为小的、可复用的 `View` 结构体
- [ ] 每个视图是否提供了预览（iOS 17+ 用 `#Preview`，旧项目用 `PreviewProvider`）
- [ ] Property Wrappers 是否正确使用（@State/@Binding/@StateObject/@ObservedObject/@EnvironmentObject，或 iOS 17+ 的 @Observable/@Bindable）
- [ ] 是否混淆 `@StateObject` 和 `@ObservedObject`（拥有者 vs 外部传入）
- [ ] 是否坚持"单一数据源"原则，数据单向流动
- [ ] 是否理解修饰符顺序对布局的影响
- [ ] 是否避免在 `body` 中执行耗时副作用操作
- [ ] 是否使用 MVVM 模式组织 Model/View/ViewModel
- [ ] iOS 16+ 是否使用 `NavigationStack`/`NavigationSplitView`（而非已弃用的 `NavigationView`）
- [ ] 异步初始化是否使用 `.task`（而非 `onAppear` + 手写 `Task`）
- [ ] UI 更新是否标注 `@MainActor`，跨 actor 模型是否实现 `Sendable`
- [ ] 长任务是否处理了取消（`Task.isCancelled`/协作式取消）
- [ ] 可交互控件是否提供 `accessibilityLabel`/`accessibilityHint`
- [ ] 是否使用语义字体以支持 Dynamic Type

## 参考资料

- [SwiftUI 官方文档](https://developer.apple.com/documentation/swiftui/)
- [Swift 官方文档](https://docs.swift.org/swift-book/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Swift Concurrency 文档](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
