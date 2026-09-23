---
name: stack-arkts
description: ArkTS / HarmonyOS（鸿蒙）栈卡——识别信号、工程惯例、分析要点、常见坑。
---

# 栈卡：ArkTS / HarmonyOS（鸿蒙应用）

## 探测信号

- `module.json5`（模块配置）+ `oh-package.json5`（依赖）+ `AppScope/` 目录；源码为 `.ets`（ArkTS）或 `.uvue`（uni-app x 编译目标时归 uni-app 栈）。
- 版本线索：`build-profile.json5` 的 `compileSdkVersion` / compatibleSdkVersion（API 9/11/12+ 差异大）。

## 工程惯例（分析要点校准基线）

- **分层**：Stage 模型下 `entry/src/main/ets/` 内典型为 `entryability/`（UIAbility 入口）、`pages/`（页面）、`components/`（自定义组件）、`model/` 或 `viewmodel/`（状态与业务）、`utils/`。分析时先判 by-layer 还是 by-feature。
- **入口**：`EntryAbility.ets`（UIAbility 生命周期）→ `windowStage.loadContent` → 首页。链路穿透从这里开始。
- **页面与路由**：官方推荐 **Navigation + NavPathStack**（API 10+）；旧项目用 `@Entry` + `router.pushUrl`。判定项目用哪套，路由表在 `main_pages.json`（router 时代）或代码内 navDestination 注册。
- **状态管理**：装饰器体系——组件内 `@State`、父子 `@Prop/@Link`、跨组件 `@Provide/@Consume`、应用级 `AppStorage`、持久化 `PersistentV`（PersistentStorage）、嵌套对象 `@Observed/@ObjectLink`（V1）与 `@ObservedV2/@Trace`（V2，鸿蒙 NEXT）。分析时标注所用体系版本（V1/V2 混用是常见债）。
- **异步与并发**：Promise/async-await（主线程单事件循环）；CPU 密集用 **TaskPool**（推荐）或 **Worker**（独立线程，通信序列化）。分析并发隐患重点：共享状态跨线程传递、@Concurrent 函数限制。
- **配置项**：`module.json5`（权限 requestPermissions、abilities、extensionAbilities）、`app.json5`；多环境用 buildProfile 的 targets/productFlavors 类机制。
- **网络**：`@ohos.net.http`；封装层常在 `utils/http` 或 `network/`。
- **持久化**：Preferences（KV）、关系型数据库 RelationalStore、分布式 KV。

## 常见坑（剖析时重点核查）

1. V1/V2 状态装饰器混用导致刷新失效或过度刷新。
2. @State 深层对象嵌套不刷新（V1 无深度观测），必须 @Observed+@ObjectLink。
3. Worker 与主线程传递含方法/非序列化对象报错。
4. 权限在 module.json5 声明但运行时未 requestPermissionsFromUser。
5. 大图/列表未用 LazyForEach + 组件复用，性能差。

## 深读锚点

- `D:\demo\wikihub\arkts\`（应用开发文档）、`D:\demo\wikihub\refrerence\arkts\`（API 参考）。
- 官方：https://developer.huawei.com/consumer/cn/doc/
