---
name: tech-wechat
description: 微信小程序开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供微信小程序特定的编码标准与质量检查。
tech_id: wechat
tech_name: 微信小程序
category: platform
---

# 微信小程序 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加微信小程序特定规范。

## 技术栈定义

微信小程序是腾讯提供的跨平台应用开发框架，采用 WXML（视图层）、WXSS（样式层）、JS/TS（逻辑层）三段式结构，通过 app.json/pages.json 配置驱动，运行于微信客户端沙箱环境。核心特性包括：双线程渲染模型、组件化系统（Component）、丰富的 wx.xxx 原生 API、分包加载机制与 rpx 响应式单位。

## 版本基线

- **基础库版本差异（2.x → 3.x）**：微信小程序基础库从 2.x 演进到 3.x，3.x 调整了部分组件默认行为与 API 返回结构：`wx.getUserProfile` 废弃、`wx.getUserInfo` 返回匿名数据，需改用 `wx.login` + 后端换取 `openid`；部分组件（如 `button` `open-type`、`input` 键盘行为）默认值变化，属破坏性变化。需在管理后台设置最低基础库版本，并在代码中对低版本做 API 存在性判断与版本门控（`wx.getDeviceInfo`/`wx.getAppBaseInfo` 拆分自 `wx.getSystemInfo`）
- **Skyline 渲染引擎**：基础库 3.0+ 引入 Skyline 渲染引擎（基于自研渲染层，配合 worklet 动画），默认 WebView 渲染仍可用；Skyline 在滚动性能、长列表、复杂动画上更优，但对部分 CSS 特性、`position: fixed`、`scroll-view` 行为、事件冒泡存在差异，且 worker/worklet 线程模型与 WebView 模式不同。在页面 `json` 中开启 `"renderer": "skyline"` 后需回归测试 UI 与交互，并关注 `componentFramework` 配置
- **TypeScript 支持版本**：微信开发者工具与基础库对 TypeScript 的支持随版本演进；较新版本（开发者工具 + 基础库）原生支持 TS 编译与类型提示，旧版本需借助构建工具（如 miniprogram-ci、构建 npm、`tsc` 预编译）处理。团队应统一开发者工具版本与 `tsconfig.json` 配置，避免类型检查行为与 `miniprogram_npm` 构建结果不一致；`ts` 类型文件不参与小程序包体积，可放心编写 `.d.ts`

## 编码规范（技术特定）

### 视图层（WXML）

- **语义化标签**：合理选择标签表达意图（`view`、`text`、`image`、`button`、`scroll-view`），不滥用 `view` 嵌套
- **数据绑定简洁**：保持 WXML 简洁，避免在模板中编写复杂的 JavaScript 逻辑
- **复杂逻辑下沉**：复杂逻辑应在 JS/TS 的计算属性中处理，或使用 **WXS** 模块（性能更优，减少通信损耗）
- **禁止内联复杂表达式**：禁止在模板中编写复杂内联表达式（如 `{{ a + b * c > d ? 'x' : 'y' }}`），应移至 WXS 或 JS
- **列表渲染规范**：使用 `wx:for` 时**必须**指定 `wx:key`
  - 静态列表：`wx:key="*this"`
  - 对象数组：使用唯一 ID 字段（如 `wx:key="id"`）
- **避免列表嵌套过深**：`wx:for` 中嵌套过深会影响渲染性能

### 条件渲染策略

- **频繁切换显示状态**使用 `hidden`（保留节点，切换 display）
- **不常切换或初始化判断**使用 `wx:if` / `wx:else`（条件不满足时不渲染）

### 组件系统

- **组件拆分**：将复杂页面拆分为多个独立的 Component，保持页面逻辑清晰
- **Props 明确定义**：明确定义组件的 `properties`，并指定类型
- **Slot 合理使用**：合理使用插槽（`slot`）提高组件的灵活性和复用性
- **样式隔离**：理解并正确配置组件的 `styleIsolation`

### 样式层（WXSS）

- **响应式单位**：使用 `rpx`（responsive pixel）进行布局，实现不同屏幕宽度自适应
  - 设计稿基准：通常以 iPhone 6（750rpx）为准
- **全局样式组织**：通用原子类、主题色定义在 `app.wxss` 中；使用 `@import` 导入公共样式片段
- **选择器规范**：
  - 优先使用**类选择器**（`.class`）
  - 避免使用级联选择器（如 `view > text`）以减少渲染开销和样式隔离问题
- **禁止本地图片资源**：在 WXSS 中引用背景图必须使用**网络图片**、**Base64** 或 `<image>` 标签，禁止引用本地图片资源

### 类型安全

- **TypeScript 优先**：充分利用 TypeScript 类型系统，减少 `any` 类型使用

## 质量检查清单（技术特定）

- [ ] `wx:for` 是否都指定了 `wx:key`
- [ ] 模板中是否存在复杂内联表达式（应移至 WXS 或 JS）
- [ ] 条件渲染策略是否正确（频繁切换用 `hidden`，条件判断用 `wx:if`）
- [ ] 组件 `properties` 是否明确定义类型
- [ ] 复杂页面是否已拆分为独立 Component
- [ ] WXSS 是否使用了 `rpx` 进行响应式布局
- [ ] WXSS 背景图是否使用了网络图片/Base64（而非本地资源）
- [ ] 组件 `styleIsolation` 是否正确配置
- [ ] 是否避免了 `wx:for` 嵌套过深

## 参考资料

- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [小程序组件文档](https://developers.weixin.qq.com/miniprogram/dev/component/)
- [小程序 API 文档](https://developers.weixin.qq.com/miniprogram/dev/api/)
- [WXS 语法参考](https://developers.weixin.qq.com/miniprogram/dev/reference/wxs/)
