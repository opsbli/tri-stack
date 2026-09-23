---
name: stack-uniapp
description: uni-app / uni-app x 栈卡——pages.json 路由、Vue 语法、uts/uvue 分析要点。
---

# 栈卡：uni-app / uni-app x（DCloud）

## 探测信号

- `manifest.json`（应用配置）+ `pages.json`（页面与路由注册）+ 依赖含 `@dcloudio/uni-app`；HBuilderX 工程（`.hbuilderx/`）或 cli 工程（`vite.config.js` + uni 插件）。
- uni-app x 判定：`.uvue` 页面文件 + `uni.enableUniAppX`（编译到原生，ArkTS/Kotlin 目标）。

## 工程惯例（分析要点校准基线）

- **分层**：`pages/`（页面）、`components/`、`store/`（Vuex/Pinia 可选）、`api/`、`common/` 或 `utils/`、`static/`；uni-app x 为 `pages/*.uvue` + uts 逻辑。
- **路由**：`pages.json` 是**路由总表**（pages 数组、tabBar、condition）；跳转 `uni.navigateTo/switchTab/redirectTo/reLaunch`；参数 `onLoad(options)`。剖析 MUST 从 pages.json 枚举全页面清单 + 功能映射。
- **状态管理**：Vuex/Pinia（Vue3）或 globalData（简易）；uni-app x 用 reactive 组合式。
- **异步与并发**：Promise 化 uni.xxx API + 回调双轨；`uni.request` 封装拦截器；uni-app x 的 uts 有原生线程能力（UI 同步刷新是其差异点）。
- **条件编译（核心）**：`#ifdef MP-WEIXIN / H5 / APP-PLUS / APP-ANDROID` 注释块——跨端分歧 MUST 枚举。
- **配置项**：`manifest.json`（appid、模块权限、各端 SDK 配置）、`pages.json` 的 style（导航栏）；`uni-id` 特征（DCloud 统一登录）。
- **持久化**：`uni.setStorageSync`（KV）；plus.sqlite（App 端）。
- **uni-app x 特有**：编译产物为 ArkTS（鸿蒙）/Kotlin（安卓）原生；无 webview；CSS 子集。剖析时按目标原生栈（见 arkts.md）双卡联查。

## 常见坑（剖析时重点核查）

1. 条件编译遗漏端分支（尤其小程序与 App 差异 API）。
2. pages.json 页面注册与磁盘文件不一致（死页面/404）。
3. onLoad 与 onShow 生命周期用错（参数重复加载）。
4. uni.request 未封装统一错误处理。
5. uni-app x 误用 web 专属 CSS/DOM API。

## 深读锚点

- `D:\demo\wikihub\uni-app\`、`D:\demo\wikihub\refrerence\uni-app-uni-app-x\`（uni-app x API 全集）。
- 官方：https://uniapp.dcloud.net.cn/
