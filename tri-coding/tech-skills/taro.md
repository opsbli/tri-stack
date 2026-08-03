---
name: tech-taro
description: Taro 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Taro 特定的编码标准与质量检查。
tech_id: taro
tech_name: Taro
category: framework
---

# Taro 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Taro 特定规范。

## 技术栈定义

Taro 是一套多端统一开发框架，支持使用 React 语法 + TypeScript 一次编写、多端运行（微信/支付宝/百度/字节等小程序、H5、React Native 等）。核心特性包括：多端适配、React 函数式组件 + Hooks 模型、跨端条件编译、统一组件 API、现代 UI/UX 框架集成（Tailwind CSS、Shadcn UI、Radix UI 等）。

## 版本基线

- **Taro 3 → 4 升级**：Taro 4 重写底层编译为基于 Webpack5/Vite 的统一架构，编译插件 API 有破坏性变化；自定义编译插件与 `Taro.plugin` 扩展需按 v4 适配；建议升级前查阅官方 Migration Guide
- **Taro 4 与 React 18 兼容性**：Taro 4 全面支持 React 18，可使用 Automatic JSX Runtime、Concurrent Features（按端支持情况）；React 17 及以下 `defaultProps` 行为变更需注意
- **Taro 3.x 端能力差异**：Taro 3 采用运行时方案，各小程序端 API 支持度不一，部分新 API（如隐私协议、Skyline 渲染）需通过 `Taro.canIUse` 探测后才可使用
- **编译产物体积变化**：Taro 3+ 运行时方案产物较 Taro 1/2 静态编译更大，需配合分包与按需引入控制主包体积

## 编码规范（技术特定）

### 多端适配

- **多端适配意识**：编写组件与逻辑时考虑各端差异，优先使用 Taro 提供的统一 API 而非端特有 API
- **跨端条件编译**：针对端差异使用 Taro 的环境变量与条件编译机制处理（如 `process.env.TARO_ENV`）
- **样式多端兼容**：使用主题（ThemeProvider、CSS 变量等）在整个应用中保持一致的样式，注意各端样式支持差异
- **平台 API 差异处理**：各小程序平台 API 存在差异（如微信的 `wx.`、支付宝的 `my.`），统一通过 `Taro.*` 调用；不确定的能力必须先 `Taro.canIUse` 探测，探测失败需提供降级方案而非直接调用导致报错

### React 语法与组件

- **React 函数式组件 + Hooks**：遵循 React 代码风格指南，统一使用函数式组件与 Hooks
- **目录结构**：代码组织遵循前端推荐目录方式（`components`、`pages`、`hooks`、`services`、`utils`、`store` 等）
- **模块化与复用**：设计可复用的组件/函数/类，优先使用稳定、维护良好的官方/社区库，避免重复造轮子
- **可扩展性**：模块/类/函数/组件设计应考虑 Should-Have、Could-Have、Must-Not-Have 等特性
- **Taro 生命周期 Hooks**：页面级使用 `useReady`（页面首次渲染完成）、`useDidShow`/`useDidHide`（显示/隐藏）、`usePullDownRefresh`（下拉刷新）、`useReachBottom`（上拉触底）、`useShareAppMessage`（分享）；禁止在普通 `useEffect` 中模拟页面生命周期，易导致端行为不一致

### 编译配置与分包

- **taro.config.ts 编译配置**：`config/index.ts` 中 `designWidth`（默认 750）与 `deviceRatio` 决定 rpx 换算基准；`mini.postcss`、`h5` 各端配置需按需开启；编译模式（`watchMode`/`buildMode`）与 `cache` 开关影响开发体验与产物
- **分包与预下载规范**：小程序主包体积受限（微信 2MB），非首屏页面必须配置 `subPackages` 分包；分包路径在 `app.config.ts` 中声明；高频跳转的分包通过 `Taro.preloadSubPackage` 预下载降低跳转白屏；`preloadRule` 配置规则预加载分包

### 类型与健壮性

- **类型安全强化**：充分利用 TypeScript 类型系统，减少 `any` 类型使用
- **使用 `const` 或 `let`，不要使用 `var`**
- **异常处理**：优先使用 `console.info` / `console.warn` / `console.error`，并提供有价值的错误信息
- **原有代码**：修复原有代码时务必先阅读并理解原有逻辑，尽量不要修改原有代码逻辑
- **关键逻辑调试日志**：在代码的关键逻辑处添加调试日志

### 样式与单位

- **CSS 单位规范**：小程序端使用 `rpx`（响应式像素，750 设计稿基准）；H5 端 `rpx` 会被转换为 `rem`；禁止混用 `px` 与 `rpx` 导致多端不一致；需精确像素的边框/阴影可用 `px`，但需评估端兼容性
- **样式隔离**：页面与组件样式默认隔离（`styleIsolation: 'apply-shared'` 或 `'isolated'`）；组件库样式通过 `addGlobalClass` 或 CSS 变量定制，避免通过高权重选择器覆盖

### 代码风格

- 遵循官方 [React 代码风格指南](https://react.dev/learn/coding-style) 和 [Airbnb JavaScript/TypeScript 风格指南](https://github.com/airbnb/javascript)
- 文档注释符合官方 JSDoc 注释规范

## 质量检查清单（技术特定）

- [ ] 是否使用 Taro 统一 API 而非端特有 API
- [ ] 端差异是否通过条件编译（`process.env.TARO_ENV`）处理
- [ ] 样式是否考虑多端兼容性，是否使用主题保持一致
- [ ] 不确定的能力是否先 `Taro.canIUse` 探测并提供降级方案
- [ ] 目录结构是否遵循 components/pages/hooks/services/utils/store 组织
- [ ] 是否使用 `const`/`let` 而非 `var`
- [ ] 异常处理是否使用 `console.info`/`warn`/`error` 并提供有价值信息
- [ ] 修改原有代码前是否充分理解原有逻辑
- [ ] 关键逻辑是否添加调试日志
- [ ] 是否避免 `any` 类型
- [ ] 页面生命周期是否使用 Taro Hooks（`useReady`/`useDidShow`/`usePullDownRefresh` 等）而非 `useEffect` 模拟
- [ ] `taro.config.ts` 中 `designWidth`、各端配置是否正确，编译配置是否版本对应
- [ ] 非首屏页面是否配置分包，高频分包是否预下载（`preloadRule`/`Taro.preloadSubPackage`）
- [ ] CSS 单位是否统一使用 `rpx`，是否避免 `px`/`rpx` 混用导致多端不一致
- [ ] 组件样式是否正确隔离，组件库定制是否通过 `addGlobalClass`/CSS 变量而非权重覆盖

## 参考资料

- [Taro 官方文档](https://docs.taro.zone/)
- [Taro Hooks 文档](https://docs.taro.zone/docs/hooks)
- [Taro 分包配置](https://docs.taro.zone/docs/app-config#subpackages)
- [React 代码风格指南](https://react.dev/learn/coding-style)
- [Airbnb JavaScript/TypeScript 风格指南](https://github.com/airbnb/javascript)
