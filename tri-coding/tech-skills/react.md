---
name: tech-react
description: React 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 React 特定的编码标准与质量检查。
tech_id: react
tech_name: React
category: framework
---

# React 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 React 特定规范。

## 技术栈定义

React 是用于构建用户界面的声明式组件库，采用函数式组件 + Hooks 模型。核心特性包括：组件化、虚拟 DOM、单向数据流、Hooks 状态管理、副作用隔离，适用于 Web 应用与跨端渲染场景。

## 版本基线

- **React 18（2022）**：并发特性（Concurrent Features）正式可用并默认通过 `createRoot` 启用；自动批处理（Automatic Batching）扩展到异步回调中的状态更新；新增 `useTransition`/`useDeferredValue`/`useSyncExternalStore`/`useId`；Suspense 支持数据获取；`ReactDOM.render` 弃用，必须迁移到 `createRoot`/`hydrateRoot`，这是破坏性 API 变更
- **React 17（2020）**：事件委托从 `document` 移到根容器（破坏性，影响多 React 实例与原生事件混用）；无新特性，定位为"升级桥梁版"
- **React 16.8（2019）**：Hooks 引入（`useState`/`useEffect`/`useContext` 等），开启函数式组件范式
- **React 19（2024）**：Actions 与 `useActionState`/`useFormStatus`/`useOptimistic` 简化表单与异步流程；`use` 可在条件分支中读取 Promise/Context；Server Components 稳定；移除 `propTypes`/`defaultProps`（函数组件）等旧 API

## 编码规范（技术特定）

### 组件与 Hooks

- **函数式组件优先**：统一使用函数式组件 + Hooks，避免类组件混用
- **Hooks 规则**：
  - 只在顶层调用 Hooks，不在循环/条件/嵌套函数中调用
  - 只在 React 函数组件或自定义 Hook 中调用 Hooks
  - 自定义 Hook 必须以 `use` 开头
- **Props 类型明确**：优先使用 TypeScript 为 Props/Events 建模，避免隐式 `any`
- **可复用抽象**：复用逻辑沉淀到自定义 Hooks 与纯函数，避免复制粘贴

### 状态与副作用

- **状态边界清晰**：局部状态用 `useState`，复杂状态用 `useReducer`；跨层级共享状态遵循项目既定方案
- **副作用可控**：`useEffect` 依赖必须完整，避免闭包陷阱与无限循环
- **清理与取消**：订阅、计时器、请求必须支持清理/取消，避免内存泄漏与竞态
- **职责分离**：UI 展示、业务规则、数据访问分层组织，避免组件成为"巨石组件"；核心业务规则写成纯函数/Hook，组件只负责组合与渲染

### 并发特性与性能（React 18+）

- **合理使用并发特性**：将非紧急更新（搜索过滤、大列表排序、数据切换）包裹在 `startTransition` 或 `useTransition` 中，让紧急输入（打字、点击）优先响应；避免对受控输入直接用 transition 导致输入卡顿。`useDeferredValue` 用于"延迟渲染昂贵结果"而非延迟输入本身
- **`useMemo`/`useCallback` 克制使用**：仅当引用相等性确实引发问题（子组件重渲染昂贵、作为 Hook 依赖、作为 props 传给 memo 组件）时才记忆化；默认不记忆化原始值与简单组件——过早优化反而增加开销与心智负担。对昂贵子树优先用 `React.memo` 包裹组件本身
- **Context 使用边界与性能**：Context 适合低频更新（主题、用户身份、locale、路由）的全局共享；Context value 变化会使所有消费者重渲染，高频更新值避免放 Context（改用状态库或 `useSyncExternalStore`）；拆分 Context 避免无关消费者连带重渲染；Provider value 用 `useMemo` 稳定引用

### 状态管理方案选型

- **状态分层选型**：组件局部状态用 `useState`/`useReducer`；跨组件共享但范围有限用 Context；全局/高频更新客户端状态按约定选型——中大型用 Redux Toolkit（不可变 + DevTools 生态）、中小型用 Zustand（极简 API、无 Provider）、细粒度原子状态用 Jotai（派生/异步原子）。一个项目内状态库不混用，按团队约定取一种为主

### 错误边界与可访问性

- **错误边界（Error Boundaries）**：必须在应用路由层级与关键特性区域放置错误边界（目前仍需类组件 `componentDidCatch`/`getDerivedStateFromError`，或用库封装），捕获子树渲染错误显示降级 UI；错误边界不捕获事件处理函数与异步错误——后者需 `try/catch` 或全局 `window.onerror`/`unhandledrejection`
- **可访问性（a11y）默认达标**：交互元素用语义化标签（`button`/`nav`/`main`/`section`）；图片必填 `alt`（装饰性用 `alt=""`）；表单 `label` 关联 `input`；可聚焦元素有可见 focus 样式；动态变更用 `aria-live` 通告；颜色对比度满足 WCAG AA。禁用 `div` 模拟按钮

### 列表渲染

- **列表渲染稳定**：列表渲染必须使用稳定唯一的 `key`，避免使用索引作为 key（除非列表静态且不会重排）

### 组件契约

- **公共组件契约清晰**：组件 props、回调约束与副作用行为应明确可追踪

## 质量检查清单（技术特定）

- [ ] 是否统一使用函数式组件，避免类组件混用
- [ ] 是否在循环/条件/嵌套函数中调用 Hooks（必须禁止）
- [ ] 自定义 Hook 是否以 `use` 开头
- [ ] Props 是否有明确的 TypeScript 类型标注
- [ ] `useEffect` 依赖数组是否完整，是否存在闭包陷阱/无限循环风险
- [ ] 订阅/计时器/请求是否在 effect 清理函数中取消
- [ ] 列表渲染是否使用稳定唯一的 `key`，是否误用索引作 key
- [ ] 是否直接修改 State（如 `state.x = 1`，必须禁止）
- [ ] 是否在渲染路径中执行副作用或昂贵计算
- [ ] 非紧急更新是否用 `startTransition`/`useTransition`/`useDeferredValue` 标记，紧急输入是否避免被 transition 阻塞
- [ ] `useMemo`/`useCallback` 是否仅用于确有引用相等性问题的场景，是否避免无差别记忆化
- [ ] Context 是否仅承载低频更新；高频值是否改用状态库或 `useSyncExternalStore`
- [ ] 是否在路由与关键特性层级放置错误边界；异步错误是否另行 `try/catch` 处理
- [ ] 交互元素是否语义化，`alt`/`label`/focus 样式/`aria-live` 是否达标
- [ ] 状态管理是否按场景分层选型且项目内不混用多套状态库

## 参考资料

- [React 官方文档](https://react.dev/)
- [React 代码风格指南](https://react.dev/learn/coding-style)
- [Hooks 规则](https://react.dev/reference/rules)
- [React 18 升级指南](https://react.dev/blog/2022/03/08/react-18-upgrade-guide)
- [useTransition 与并发 UI](https://react.dev/reference/react/useTransition)
- [错误边界](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [可访问性 (a11y) 指南](https://react.dev/reference/react-dom/components/common#common-accessibility-patterns)
- [Airbnb JavaScript/TypeScript 风格指南](https://github.com/airbnb/javascript)
