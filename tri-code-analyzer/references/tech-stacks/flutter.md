---
name: stack-flutter
description: Flutter / Dart 栈卡——Widget 树、路由、状态管理、Isolate 并发分析要点。
---

# 栈卡：Flutter / Dart

## 探测信号

- `pubspec.yaml` + `lib/main.dart`；平台目录 `android/`、`ios/`（桌面：`windows/`、`macos/`、`linux/`；Web：`web/`）。

## 工程惯例（分析要点校准基线）

- **分层**：`lib/` 典型为 `pages|screens|views/`、`widgets/`（复用组件）、`models/`、`services/` 或 `providers/`（业务+状态）、`utils/`；大型项目用 feature-first（`features/<域>/data|domain|presentation`，Clean Architecture 痕迹）。先判定组织风格。
- **入口与路由**：`main.dart` → `runApp`。路由两代：命名路由 `MaterialApp.routes`/`onGenerateRoute` 与官方推荐 **go_router**（声明式、深链接、路由守卫 redirect）。剖析时枚举路由表与守卫链。
- **状态管理**：按依赖判定——`provider`、`riverpod`（编译期安全）、`bloc/flutter_bloc`（事件驱动，严格分层）、`getx`（全家桶但耦合高）。分析 Mutation/Action 流转路径与状态不可变性。
- **异步与并发**：Dart 单线程事件循环 + `Future`/`Stream`；CPU 密集用 **Isolate**（`compute()` 或 Isolate.run）。剖析重点：Stream 订阅泄漏（未 cancel）、BuildContext 跨 async 使用（mounted 检查）。
- **实体与数据**：`models/` + `json_serializable`/`freezed`（代码生成）或手写 `fromJson`。数据层常分层 `data/`（Repository、API client: dio/http）+ `domain/`。
- **配置项**：`--dart-define` / `--dart-define-from-file`、flavor（Android productFlavors / iOS scheme）；密钥 MUST 不硬编码在 dart 常量。
- **持久化**：shared_preferences（KV）、sqflite/drift（关系型）、hive/isar（NoSQL）。

## 常见坑（剖析时重点核查）

1. setState 滥用导致整树重建（应局部化状态）。
2. Stream/Timer/AnimationController 未 dispose。
3. async 回调后使用 context（未查 mounted）。
4. GetX 服务与 UI 强耦合，难测试。
5. 密钥硬编码于 const（反编译即泄露）。

## 深读锚点

- `D:\demo\wikihub\flutter\`、`D:\demo\wikihub\refrerence\flutter_samples\`。
- 官方：https://docs.flutter.dev/
