---
name: stack-taro
description: Taro 栈卡——多端编译、页面配置、跨端条件编译分析要点。
---

# 栈卡：Taro（京东多端框架）

## 探测信号

- package.json 依赖含 `@tarojs/taro`；`config/index.js|ts`（编译配置，含多端 targets）；`src/app.config.js|ts`（页面注册）。
- 技术栈绑定：React 或 Vue 语法写法，编译目标微信/支付宝小程序 + H5 + RN。

## 工程惯例（分析要点校准基线）

- **分层**：`src/` 内 `pages/`、`components/`、`services/` 或 `api/`、`store/`、`utils/`；`app.config.ts` 注册页面路径与 tabBar——这是路由总表，剖析 MUST 先读。
- **路由（多端）**：`Taro.navigateTo/switchTab/redirectTo` + 页面栈；参数经 `Taro.getCurrentInstance().router.params` 或 `useRouter`。与原生小程序路由语义对齐，注意 tab 页不可 navigateTo。
- **状态管理**：Redux/Zustand/MobX/Context 均可；小程序端无 window，注意状态库兼容层。
- **异步与并发**：`Taro.request` 封装层（拦截器）；Promise 化 API；`Taro.cloud`（微信云开发）特征。
- **条件编译（核心）**：`process.env.TARO_ENV` 判断 + 文件后缀 `.weapp.tsx/.h5.tsx`——剖析跨端分歧逻辑时 MUST 枚举平台分支。
- **配置项**：`config/index.ts`（defineConstants、编译产物配置）、`project.config.json`（微信开发者配置）、`app.config.ts` 的 permission/window。
- **原生能力**：`Taro.getStorageSync` 等存储、`Taro.login/getUserProfile` 鉴权链路。

## 常见坑（剖析时重点核查）

1. API 在某端不存在未做可用性判断（如 H5 无 getProvider）。
2. 条件编译遗漏平台分支导致白屏。
3. 包体积超限（分包 subPackages 配置缺失）。
4. request 无统一超时/重试/错误码拦截。
5. tabBar 页面用错跳转 API。

## 深读锚点

- `D:\demo\wikihub\taro\`、`D:\demo\wikihub\refrerence\taro\`。
- 官方：https://docs.taro.zone/
