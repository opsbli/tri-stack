---
name: tech-react-native
description: React Native 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 React Native 跨平台移动应用特定的编码标准与质量检查。
tech_id: react-native
tech_name: React Native
category: framework
---

# React Native 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 React Native 特定规范。

## 技术栈定义

React Native 是 Meta 推出的跨平台移动应用开发框架，使用 JavaScript/TypeScript 与 React 编写原生移动应用。核心特性：原生组件映射、Bridge/JSI 通信机制、平台特定代码分离、Flexbox 布局、热更新支持。

## 版本基线

- **New Architecture（Fabric + TurboModules）**：Fabric（新渲染器）与 TurboModules（新原生模块系统）从 0.68 起可选适配，0.74 起默认启用，0.76+ 在 iOS/Android 默认全量开启。需配合 JSI 同步通信，移除 Bridge 后旧架构原生模块需迁移；C++ TurboModule 与 `codegen` 是新架构强制要求
- **Hermes 引擎**：0.70 起在 Android 与 iOS 双平台默认启用（取代 JSC）。Hermes 提前编译字节码、降低启动时间与内存，但禁用 `eval`/`new Function`（影响部分动态代码库）；调试依赖 Hermes Inspector 而非 Chrome DevTools 直接连接
- **Bridgeless 模式**：0.74 起默认开启，移除旧 Bridge 单线程瓶颈，JS<->Native 调用走 JSI 同步路径；依赖旧 Bridge 全局事件 `DeviceEventEmitter`/`NativeAppEventEmitter` 的库需迁移
- **Expo SDK 与 Bare workflow**：Expo SDK 50+ 默认推荐 `expo-router` 文件式路由；Expo 应用从 SDK 49 起支持 `expo prebuild` 生成原生代码（CNG），可平滑过渡到 Bare；纯原生集成/私有原生模块/深度定制系统服务时用 Bare workflow + React Native CLI

## 编码规范（技术特定）

### 组件与列表

- **原生组件**：优先使用 `View`, `Text`, `Image`, `FlatList` 等核心组件
- **列表性能**：长列表必须使用 `FlatList` 或 `SectionList`，严禁使用 `ScrollView` + `map`
- **StyleSheet**：使用 `StyleSheet.create` 定义样式，提升性能，避免在渲染循环中创建新的样式对象

### 虚拟化列表与性能优化

- **列表性能深度优化**：`FlatList`/`SectionList` 必须提供稳定的 `keyExtractor`；等高列表提供 `getItemLayout` 以支持跳转到任意行而不渲染中间项；开启 `removeClippedSubviews`（Android 长列表）；`initialNumToRender`/`maxToRenderPerBatch`/`windowSize` 按帧率调优；列表项用 `React.memo` 包裹并保证 props 引用稳定
- **`React.memo` 与重渲染控制**：列表项、卡片等高频渲染组件用 `React.memo` 包裹；传给子组件的回调用 `useCallback` 稳定引用（仅当确实作为 memo 组件 props 时）；避免在 `renderItem` 内联创建对象/数组/函数
- **交互调度**：耗时同步计算或导航跳转用 `InteractionManager.runAfterInteractions` 延迟到动画/手势结束后执行，避免掉帧；新架构下优先用 `useFrameCallback`（reanimated）或并发特性替代

### 布局与响应式

- **Flexbox**：熟练使用 Flexbox 布局。注意 RN 中 `flexDirection` 默认是 `column`
- **响应式**：考虑不同屏幕尺寸和安全区域（SafeArea）

### 平台差异处理

- **平台判断**：使用 `Platform.OS` 或 `Platform.select` 处理平台特定逻辑
- **文件后缀**：必要时使用 `.ios.js` 和 `.android.js` 分离特定平台代码

### 架构适配与引擎

- **New Architecture 适配**：新项目默认开启新架构；既有库升级前用 `npx @react-native-community/cli config` 检查兼容性，不兼容库用 `newArchEnabled=false` 临时回退并提 issue 推动迁移；原生模块必须实现 TurboModule spec（`Native*.ts` + codegen），不得再用旧 Bridge `NativeModules` 直连
- **Hermes 兼容性**：默认启用 Hermes，禁止在 Hermes 环境依赖 `eval`/`new Function`/动态 `require`；性能分析用 `Hermes Profiler`（Chrome DevTools/Safari）而非旧 JSC 工具链；如确需 JSC（罕见，如依赖动态执行）需显式配置并记录理由

### 工作流选型

- **Expo 与 Bare workflow 选型**：默认优先 Expo（托管构建、EAS、OTA、开箱即用模块）；仅在需要修改原生 AndroidManifest/Info.plist、集成私有 SDK、深度定制启动流程或已有大量原生代码时选 Bare workflow + RN CLI；Expo 项目通过 `expo prebuild` + `expo-dev-client` 在保留托管优势的同时接入原生模块，避免非此即彼

### 导航、动画与手势

- **导航**：使用 React Navigation 处理路由和堆栈
- **动画**：简单动画使用 `LayoutAnimation`，复杂动画使用 `Animated` API 或 `react-native-reanimated`
- **手势处理**：复杂手势（拖拽、缩放、滑动删除、底部抽屉）使用 `react-native-gesture-handler`（运行在 UI 线程，不阻塞 JS），配合 `react-native-reanimated` 在 UI 线程做动画；禁止用 `PanResponder` 处理高交互手势（运行在 JS 线程，跨线程通信导致卡顿）

### 资源管理与热更新

- **图片资源管理**：网络图/远程图优先用 `react-native-fast-image`（基于原生 SDWebImage/Glide，支持缓存、优先级、预加载）；本地静态资源用 `require()` 静态引入让打包器内联与压缩；大图必须提供 `resizeMode` 与显式尺寸避免布局抖动；图标统一用 `react-native-vector-icons` 并按需 subset 减小体积
- **OTA 热更新**：使用 EAS Update（Expo 体系）或 CodePush（Bare 体系）分发 JS bundle 热更新；热更新仅用于 JS/资源层修复与轻量迭代，禁止通过热更新改变应用核心权限或上架审核承诺的功能行为（合规风险）；必须配置回滚机制与灰度比例，并遵守应用商店热更新政策

## 质量检查清单（技术特定）

- [ ] 长列表是否使用 `FlatList`/`SectionList`，而非 `ScrollView` + `map`
- [ ] 样式是否使用 `StyleSheet.create`，未在渲染循环中创建新的样式对象
- [ ] 是否注意 RN 中 `flexDirection` 默认为 `column`
- [ ] 是否处理了不同屏幕尺寸和安全区域（SafeArea）
- [ ] 平台特定逻辑是否使用 `Platform.OS`/`Platform.select` 或文件后缀分离
- [ ] 是否使用 React Navigation 处理导航
- [ ] 动画是否按复杂度选择合适方案（LayoutAnimation / Animated / reanimated）
- [ ] 是否处理了 Android 的权限请求流程
- [ ] `FlatList`/`SectionList` 是否提供 `keyExtractor`、等高列表是否提供 `getItemLayout`
- [ ] 高频渲染组件是否用 `React.memo` 包裹，`renderItem` 内是否避免内联对象/函数
- [ ] 耗时操作是否用 `InteractionManager.runAfterInteractions` 延迟执行
- [ ] 原生模块是否迁移到 TurboModule spec（新架构），是否避免直接用旧 `NativeModules`
- [ ] 是否避免依赖 `eval`/`new Function`（Hermes 不兼容），性能分析是否用 Hermes Profiler
- [ ] Expo/Bare workflow 选型是否合理，是否优先 Expo + `expo prebuild`/`expo-dev-client`
- [ ] 复杂手势是否用 `react-native-gesture-handler` + reanimated，是否避免 `PanResponder` 处理高交互手势
- [ ] 网络图是否用 `react-native-fast-image`，本地图是否用 `require()`，大图是否提供尺寸与 `resizeMode`
- [ ] OTA 热更新是否配置回滚与灰度，是否仅限 JS/资源层且符合应用商店政策

## 参考资料

- [React Native 官方文档](https://reactnative.dev/docs/getting-started)
- [React Navigation](https://reactnavigation.org/docs/getting-started)
- [Reanimated](https://docs.swmansion.com/react-native-reanimated/)
- [New Architecture 指南](https://reactnative.dev/docs/the-new-architecture/why)
- [Hermes 引擎](https://reactnative.dev/docs/hermes)
- [react-native-gesture-handler](https://docs.swmansion.com/react-native-gesture-handler/docs/)
- [react-native-fast-image](https://github.com/DylanVann/react-native-fast-image)
- [EAS Update](https://docs.expo.dev/eas-update/introduction/)
- [CodePush](https://github.com/microsoft/react-native-code-push)
