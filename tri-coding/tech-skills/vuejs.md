---
name: tech-vuejs
description: Vue.js 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Vue.js 特定的编码标准与质量检查。
tech_id: vuejs
tech_name: Vue.js
category: framework
---

# Vue.js 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Vue.js 特定规范。

## 技术栈定义

Vue.js 是渐进式 JavaScript 框架，核心采用声明式渲染与组件化模型。Vue 3 推荐使用 Composition API 与单文件组件（SFC）。核心特性包括：响应式系统（`ref`/`reactive`/`computed`）、`<script setup>` 语法糖、指令系统（`v-if`/`v-for`/`v-model`/`v-show` 等）、组合式函数（`useXxx`）复用逻辑、Pinia 状态管理。

## 版本基线

- **Vue 3 Composition API（vs Vue 2 Options API）**：Vue 3 以 Composition API + `<script setup>` 为推荐写法，`setup()` 与组合式函数（`useXxx`）替代 Vue 2 的 `data`/`methods`/`mixins` 心智模型；属破坏性演进，`mixins` 隐式合并、`this` 上下文、全局 API（`new Vue()` → `createApp()`）、过滤器（`filters` 废弃）等旧模式在 Vue 3 中不复存在，Vue 2 项目迁移需重构状态与逻辑复用层
- **Vue 3.3（defineModel / defineSlots 等实验特性）**：`defineModel`（实验性）替代手动 `props` + `emits` 实现 `v-model`；新增 `defineSlots`、`defineOptions`、`defineSlots` 类型增强、`generic` 泛型组件支持、外部类型导入改进（`defineProps` 直接引用 `.ts` 类型）。注意 3.3 的 `defineModel` 仍为实验特性，需显式开启，生产环境慎用
- **Vue 3.4（defineModel 稳定）**：`defineModel` 正式稳定，模板解析器重写带来解析与渲染性能提升；`v-model` 多绑定与 `defineModel` 成为标准模式；解构 `props` 的响应性丢失问题通过保持响应性（reactivity destructure，仍需显式开启）改善。升级 3.4 时需校验依赖库（vue-router/pinia/vue-i18n 等）的兼容版本，并回归测试模板边界场景

## 编码规范（技术特定）

### 组件与组合式 API

- **Composition API 优先**：统一使用 `<script setup>`，避免 Options API 混用导致心智负担
- **命名约定**：组件使用 `PascalCase`，组合式函数使用 `useXxx`
- **组件职责明确**：页面负责编排，组件负责展示与交互，复用逻辑沉淀到 `useXxx` 组合式函数

### 响应式系统

- **Reactivity 正确使用**：基本类型用 `ref`，对象/数组用 `reactive`（或 `ref` 包裹对象并整体替换）
- **Computed 优先**：派生状态用 `computed`，避免在模板中写复杂表达式与重复计算
- **副作用集中管理**：请求、订阅、计时器等副作用必须可追踪、可清理，避免散落在渲染路径中

### 状态管理

- **状态边界清晰**：局部状态就地管理，跨页面/跨层级状态集中到统一状态管理方案（如项目已使用 Pinia 则遵循现有约定）
- **依赖最小化**：避免组件之间通过隐式全局（window、全局事件）耦合

### Props / Emits 与模板

- **Props & Emits 显式定义**：使用 `defineProps` / `defineEmits` 并提供 TypeScript 类型标注
- **模板规则**：`v-for` 必须配合稳定 `:key`；避免同元素 `v-if` + `v-for`
- **渲染策略**：频繁切换用 `v-show`，条件不满足无需渲染用 `v-if`
- **空值与边界**：对可空数据在脚本层收敛与兜底，避免模板中出现不可控的空引用

### 样式与契约

- **样式边界明确**：默认使用 `<style scoped>`；需要覆盖子组件样式时使用 `:deep()`
- **公共 API 清晰**：组件对外 props、emits、slot 语义需要清楚，避免"猜用法"

### 类型与异步

- **类型安全强化**：充分利用 TypeScript 类型系统，减少 `any` 类型使用
- **异步处理标准化**：使用 `async/await`，错误处理模式统一

## 质量检查清单（技术特定）

- [ ] 是否统一使用 `<script setup>`，避免 Options API 混用
- [ ] 组件命名是否 `PascalCase`，组合式函数是否 `useXxx`
- [ ] 基本类型是否用 `ref`，对象/数组是否用 `reactive`
- [ ] 派生状态是否用 `computed` 而非模板内复杂表达式
- [ ] `defineProps` / `defineEmits` 是否提供 TypeScript 类型标注
- [ ] `v-for` 是否配合稳定 `:key`；是否避免同元素 `v-if` + `v-for`
- [ ] 频繁切换是否用 `v-show`，条件渲染是否用 `v-if`
- [ ] 是否使用 `<style scoped>`，覆盖子组件样式是否用 `:deep()`
- [ ] 跨页面状态是否集中到 Pinia 等统一方案

## 参考资料

- [Vue.js 官方文档](https://vuejs.org/)
- [Vue 3 组合式 API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [单文件组件规范](https://vuejs.org/guide/scaling-up/sfc.html)
- [Pinia 状态管理](https://pinia.vuejs.org/)
