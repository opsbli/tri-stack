---
name: tech-uniapp
description: uni-app 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 uni-app 跨端框架特定的编码标准与质量检查。
tech_id: uniapp
tech_name: uni-app
category: framework
---

# uni-app 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 uni-app 特定规范。

## 技术栈定义

uni-app 是基于 Vue 3 的跨端开发框架，一套代码可编译到小程序（微信/支付宝/百度等）、H5、App（iOS/Android）多端。核心特性：Vue 3 Composition API + TypeScript、条件编译（#ifdef/#ifndef）、uni.xxx 跨端 API、pages.json 配置驱动。

## 版本基线

- **Vue 2 / Vue 3 版本差异**：uni-app 同时支持 Vue 2 与 Vue 3 两种运行时；Vue 3 版本基于 `@dcloudio/uni-app` + Vite 构建，采用 Composition API + `<script setup>`，性能与生态更优；Vue 2 版本基于 webpack 构建，使用 Options API。两套运行时在响应式系统、生命周期、`v-model` 实现、`mixins` 行为上存在差异，属破坏性分歧，新项目应选 Vue 3，存量项目需明确运行时版本并隔离差异
- **HBuilderX 版本要求**：HBuilderX 版本与 uni-app 编译器、CLI、各端运行时强耦合；Vue 3 + Vite 模式需 HBuilderX 3.4.10+，部分新特性（如 `easycom` 自动导入增强、uts/uvue、`uni-app x`）需更高版本（3.99+/4.x）。版本不一致会导致编译产物与预期不符，属常见破坏性来源，团队需统一 HBuilderX 版本并在 CI 中校验
- **小程序基础库版本要求**：编译到微信/支付宝/百度/字节等小程序时，目标基础库版本决定可用 API 与渲染行为；微信基础库 2.x → 3.x 存在组件行为与 API 兼容差异（如 `getUserInfo` 返回匿名数据、部分组件默认样式调整），Skyline 渲染引擎需更高基础库。需在 `manifest.json` 中配置 `mp-weixin.libVersion` 等最低基础库版本，并在 CI 中校验 API 调用的版本门控

## 编码规范（技术特定）

### 组件与组合式函数

- **Composition API 优先**：统一使用 `<script setup lang="ts">`，避免 Options API 混用
- **Reactivity 正确使用**：基本类型用 `ref`，对象/数组用 `reactive`（或 `ref` 包裹对象并整体替换）
- **Computed 优先**：派生状态用 `computed`，模板只做展示
- **命名约定**：组件 `PascalCase`，组合式函数 `useXxx`
- **页面 = 流程编排**：页面组件负责生命周期编排与数据流动，业务规则沉淀到 `useXxx` 与 `services`
- **公共 API 清晰**：组件对外 props、emits 与事件载荷需要有 TS 类型

### 跨端与平台差异

- **基础组件优先**：优先使用 `view/text/image/scroll-view` 等 uni-app 基础组件，降低兼容风险
- **跨端差异收敛**：将平台差异集中到适配层（如 `utils/adapters`），业务层不散落 `#ifdef` 逻辑
- **统一走 `uni.*`**：不依赖 `window/document/localStorage` 等 Web 专属对象，使用 `uni.request`、`uni.setStorage*`、`uni.getSystemInfo` 等能力
- **网络与存储封装**：请求与存储必须有统一入口（错误码处理、超时、鉴权、重试、数据版本）

### 生命周期与模板

- **页面生命周期优先**：页面中优先使用 `onLoad / onShow / onHide / onUnload` 组织业务流程
  - `onLoad`：解析路由参数、初始化页面所需数据
  - `onShow`：刷新可能变化的数据（缓存/全局状态）
  - `onUnload`：释放定时器、监听器、长连接等资源
- **模板规则**：`v-for` 必须稳定 `:key`；避免同元素 `v-if` + `v-for`

### 样式

- **样式边界明确**：默认 `<style scoped>`；覆盖子组件样式使用 `:deep()`

### 条件编译

- **条件编译收敛**：使用 `#ifdef`/`#ifndef`/`#endif` 处理端差异，条件编译块需成对闭合且缩进规范；条件编译应集中在适配层或组件级，业务逻辑不散落平台分支，便于维护与端切换
- **平台标识准确**：条件编译平台标识（`MP-WEIXIN`/`MP-ALIPAY`/`H5`/`APP-PLUS` 等）需与 `manifest.json` 中启用的平台一致，避免无效条件分支；多端组合用 `||` 连接（如 `#ifdef MP-WEIXIN || MP-ALIPAY`），反向排除用 `#ifndef`

### 跨端适配

- **rpx 单位优先**：尺寸单位优先使用 `rpx`（750 设计稿基准），保证小程序与 App 端自适应；仅 H5 端固定尺寸用 `px`，避免混用导致各端显示不一致
- **平台能力门控**：调用端特有能力（如微信支付、App 推送、H5 路由）前用 `uni.getSystemInfo` 或条件编译判断平台，避免在不可用端调用导致运行时错误

### uniCloud 与扩展

- **uniCloud 逻辑收敛**：uniCloud 云函数/云对象作为后端入口，业务逻辑收敛到 `uniCloud-aliyun`/`uniCloud-tcb` 目录下的 `controller`/`service` 分层；DB Schema 驱动表单与权限校验，前端不重复实现校验规则
- **DB Schema 单一来源**：表结构、字段校验、权限规则统一在 `*.schema.json` 中定义，通过 `uniCloud.database()` 生成的客户端代码与表单组件共享同一份 schema，避免前后端校验规则不一致

## 质量检查清单（技术特定）

- [ ] 是否统一使用 `<script setup lang="ts">`，未混用 Options API
- [ ] 基本类型用 `ref`，对象/数组用 `reactive`，派生状态用 `computed`
- [ ] 组件命名为 PascalCase，组合式函数为 useXxx
- [ ] 平台差异是否收敛到适配层，业务层无散落的 `#ifdef`
- [ ] 是否使用 `uni.*` API 而非 Web 专属对象（window/document/localStorage）
- [ ] 网络请求与存储是否走统一封装入口
- [ ] 页面生命周期职责是否清晰（onLoad 初始化 / onShow 刷新 / onUnload 释放）
- [ ] `v-for` 是否有稳定 `:key`，是否存在同元素 `v-if` + `v-for`
- [ ] 组件 props/emits 是否有 TS 类型定义
- [ ] 样式是否默认 `scoped`，跨组件覆盖是否用 `:deep()`

## 参考资料

- [uni-app 官方文档](https://uniapp.dcloud.net.cn/)
- [Vue 3 组合式 API](https://cn.vuejs.org/guide/extras/composition-api-faq.html)
