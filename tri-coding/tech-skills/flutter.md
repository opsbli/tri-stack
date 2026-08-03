---
name: tech-flutter
description: Flutter 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Flutter 框架与 Dart 语言特定的编码标准与质量检查。
tech_id: flutter
tech_name: Flutter
category: framework
---

# Flutter 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Flutter 与 Dart 特定规范。

## 技术栈定义

Flutter 是 Google 推出的跨平台 UI 框架，使用 Dart 语言构建声明式 UI。核心特性：Widget 树组合构建 UI、声明式 UI 范式、StatefulWidget/StatelessWidget 状态管理、单次编译多端运行（iOS/Android/Web/桌面）、Dart 强类型语言、平台通道（Platform Channel）调用原生能力。

## 版本基线

- **Dart 3.0 健全空安全（Sound Null Safety）**：空安全成为默认且强制，未迁移的旧代码无法在 Dart 3+ 上运行；类型系统区分可空（`String?`）与不可空（`String`），`!` 操作符与 `??`/`?.` 运算符需谨慎使用
- **Dart 3.0 Records 与模式匹配**：新增 Records（`({String name, int age})`）与 Pattern Matching（switch 表达式、解构赋值、`if` 模式匹配），应优先使用 switch 表达式替代链式 if-else，利用解构简化多值返回
- **Flutter 3.x Impeller 渲染引擎**：iOS 上默认启用 Impeller 替代 Skia，Android 14+ 逐步推进；自定义 shader 与平台视图渲染行为有差异，需在目标平台实测
- **Flutter 3.16+ Material 3 默认**：`useMaterial3` 默认为 true，组件外观与 Material 2 有显著差异；若需保持旧外观需显式关闭

## 编码规范（技术特定）

### Dart 语言特性

- **类型安全**：强制使用类型注解（Type Annotations），利用 Dart 的强类型系统
- **final/const 优先**：使用 `final` 或 `const`，不要使用 `var`
- **避免全局变量**：避免使用全局变量
- **代码风格**：符合官方 [Dart Style Guide](https://dart.dev/guides/language/effective-dart/style) 和 [Flutter Style Guide](https://docs.flutter.dev/development/tools/flutter-build/style)
- **空安全规范**：Dart 3 健全空安全下，禁止滥用 `!` 强制解空；优先通过类型设计（可空 vs 不可空）表达空值语义，使用 `??`、`?.`、`late`（仅当初始化时机确定时）替代运行时断言
- **Records 与模式匹配**：优先使用 Records 封装多返回值替代 `List<dynamic>` 临时结构；利用 switch 表达式与解构处理分支逻辑，避免冗长 if-else 链
- **原有代码**：在修复原有代码时，务必先阅读并理解原有代码，尽量不要修改原有代码逻辑

### Widget 与状态管理

- **目录结构**：使用适当的文件夹结构组织代码（models、screens、widgets、services）
- **主题一致性**：使用主题（themes）在整个应用中保持一致的样式
- **状态管理方案选型**：按场景选型——简单/局部状态用 `setState`+`Provider`；中大型应用优先 `Riverpod`（编译期安全、可测试）；复杂事件流/领域驱动用 `Bloc`；`GetX` 因隐式全局状态不推荐用于新项目，团队需明确统一选型
- **Widget 性能规范**：能标记为 `const` 的构造器一律加 `const`（触发编译期常量折叠、减少重建）；列表渲染使用 `ListView.builder`/`GridView.builder` 而非 `Column`+`List`；频繁重绘的独立区域用 `RepaintBoundary` 隔离重绘范围；避免在 `build` 中做重计算或创建新对象

### 路由与异常

- **路由管理**：使用命名路由和 `Navigator.pushNamed()` 进行导航；大型应用推荐 `go_router` 声明式路由
- **调试输出**：使用 `debugPrint` 函数，避免使用 `print`，并提供有价值的错误信息
- **异常处理**：使用 try/catch 捕获预期异常，提供有意义的错误上下文，避免静默吞掉错误；捕获后区分 `Error`（不应捕获）与 `Exception`（预期异常）

### 平台通道与依赖管理

- **平台通道**：原生能力通过 `MethodChannel`（请求-响应）或 `EventChannel`（事件流）桥接；通道名加业务前缀防冲突，参数使用基础类型与 `Map`，复杂结构用 `Pigeon` 生成类型安全代码
- **依赖管理**：依赖声明集中在 `pubspec.yaml`，版本使用 caret 语法（`^x.y.z`）；谨慎使用 `pub upgrade --major-versions`，升级前查看 CHANGELOG 与 breaking change；锁文件 `pubspec.lock` 必须提交版本控制

### 国际化与测试

- **国际化（i18n）**：使用 `flutter_localizations` + `intl` 包，遵循 `.arb` 文件 + `gen-l10n` 代码生成流程；禁止在 Widget 中硬编码用户可见文案，统一走 `AppLocalizations.of(context)`
- **测试规范**：分层覆盖——纯逻辑用 Unit Test（`test` 包）；UI 交互用 Widget Test（`flutter_test`，优先 `pumpWidget`+`Finder` 验证渲染）；跨页面/原生能力用 Integration Test（`integration_test` 包，真机或模拟器）；测试文件与源码同结构组织

## 质量检查清单（技术特定）

- [ ] 是否强制使用类型注解，利用 Dart 强类型系统
- [ ] 是否使用 `final`/`const` 而非 `var`
- [ ] 代码风格是否符合 Dart Style Guide 和 Flutter Style Guide
- [ ] 目录结构是否清晰（models/screens/widgets/services）
- [ ] 是否使用 themes 保持应用样式一致
- [ ] 路由是否使用命名路由和 `Navigator.pushNamed()`
- [ ] 调试输出是否使用 `debugPrint` 而非 `print`
- [ ] 异常是否使用 try/catch 捕获并提供有意义的错误上下文
- [ ] 修复原有代码时是否先阅读理解，未随意修改原有逻辑
- [ ] 空安全是否健全——是否避免滥用 `!`，优先用类型设计与 `??`/`?.`/`late`
- [ ] 是否合理使用 Records 与 switch 表达式替代冗长分支与临时结构
- [ ] 状态管理方案是否按场景选型，团队是否统一（Provider/Riverpod/Bloc）
- [ ] Widget 是否最大化使用 `const` 构造器、`ListView.builder`、`RepaintBoundary`
- [ ] 平台通道是否命名规范、是否用 Pigeon 保证类型安全
- [ ] 依赖版本是否使用 caret 语法，`pubspec.lock` 是否提交
- [ ] 用户可见文案是否全部走 `AppLocalizations`，无硬编码
- [ ] 是否分层覆盖 Unit/Widget/Integration Test

## 参考资料

- [Flutter 官方文档](https://docs.flutter.dev/)
- [Dart Effective Style Guide](https://dart.dev/guides/language/effective-dart/style)
- [Dart 语言教程](https://dart.dev/language)
- [Riverpod 文档](https://riverpod.dev/)
- [go_router 文档](https://pub.dev/packages/go_router)
- [Pigeon 平台通道代码生成](https://pub.dev/packages/pigeon)
- [Flutter 国际化](https://docs.flutter.dev/ui/accessibility-and-internationalization/internationalization)
- [Flutter 测试](https://docs.flutter.dev/testing)
