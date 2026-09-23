---
name: stack-react-native
description: React Native 栈卡——JS/原生桥、导航、状态、新架构分析要点。
---

# 栈卡：React Native

## 探测信号

- package.json 依赖含 `react-native`；存在 `ios/`、`android/` 原生工程目录；`react-native.config.js`；`app.json`。
- 架构线索：新架构（Fabric + TurboModules，`newArchEnabled=true`）vs 旧 Paper 架构。

## 工程惯例（分析要点校准基线）

- **分层**：`App.js|tsx` 入口；`src/` 内典型 `screens/`、`components/`、`navigation/`、`store/`、`services/`（API）、`utils/`；大型项目 feature-first。
- **导航（路由）**：事实标准 **React Navigation**（`@react-navigation/native` + native-stack/bottom-tabs）；分析时枚举 navigator 嵌套树、params 流转、auth 守卫（条件渲染 navigator 或 redirect）。
- **状态管理**：Redux Toolkit / Zustand / MobX / Jotai / Context——按依赖判定；服务端状态常配 React Query（TanStack Query）或 RTK Query。
- **异步与并发**：JS 单线程事件循环；原生模块桥接（新架构 TurboModules / 旧 NativeModules）；`InteractionManager`/Hermes 引擎特征。剖析重点：桥接数据序列化成本、原生线程回调。
- **实体与数据**：API 层 axios/fetch 封装；类型层 TypeScript interfaces 或 zod 校验。
- **配置项**：`react-native-config`（.env 多环境）、iOS Info.plist / Android build.gradle 渠道；密钥 MUST 在原生侧或服务端下发。
- **持久化**：AsyncStorage（MMKV 更快）、WatermelonDB/Realm（重数据）。

## 常见坑（剖析时重点核查）

1. 列表未用 FlatList 虚拟化 / 缺 keyExtractor 稳定 key。
2. 依赖数组缺失导致 effect 泄漏（定时器/订阅未清）。
3. 桥接频繁传大对象（JSON 序列化开销）。
4. release 包未关 console.log / 未配 Proguard/R8。
5. 权限申请缺平台分支处理（iOS/Android 差异）。

## 深读锚点

- `D:\demo\wikihub\react-native\`、`D:\demo\wikihub\refrerence\ohos_react_native\`（鸿蒙 RN 适配）。
- 官方：https://reactnative.dev/docs
