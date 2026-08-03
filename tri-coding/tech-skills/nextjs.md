---
name: tech-nextjs
description: Next.js 框架开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Next.js 特定的编码标准与质量检查。
tech_id: nextjs
tech_name: Next.js
category: framework
---

# Next.js 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Next.js 特定规范。

## 技术栈定义

Next.js 是基于 React 的全栈框架，通过 App Router 提供文件约定式路由、Server Components、Server Actions、SSR/SSG/ISR 等多种渲染策略，内置 API Routes 与缓存层，适合构建高性能 Web 应用。

## 版本基线

- **Next.js 14 → 15 fetch 缓存默认行为变更（破坏性）**：Next.js 14 默认 `force-cache`，Next.js 15 默认改为不缓存（`no-store` 语义）；升级后原依赖隐式缓存的 `fetch` 请求会变成每次重新请求，必须显式声明 `cache: 'force-cache'` 或 `revalidate`/`tags` 以保持原行为
- **App Router vs Pages Router 并存**：App Router（`app/`）支持 RSC、布局嵌套、流式渲染；Pages Router（`pages/`）仅 CSR/SSR/SSG；新项目应统一用 App Router，迁移期两套路由可共存但同一路径不可同时存在，边界需明确隔离
- **React 19 支持**：Next.js 15 要求 React 19，Server Actions 稳定、`use()` 与 `useFormStatus`/`useOptimistic` 等新特性可用；React 18 项目需评估升级成本
- **Turbopack 稳定化**：Next.js 15 中 Turbopack 用于开发模式稳定，生产构建仍以 Webpack 为主；`next dev --turbo` 可用，但自定义 Webpack loader 在 Turbopack 下可能不支持

## 编码规范（技术特定）

### 路由与目录约定

- **App Router 约定**：遵循文件约定（`page.tsx`、`layout.tsx`、`loading.tsx`、`error.tsx`），保持路由结构可预测
- **Server/Client 边界清晰**：默认 Server Components，只有需要交互时才使用 `'use client'`
- **数据流清晰**：数据获取与变更路径明确，避免同一数据在多处重复拉取与维护
- **路由组织模式**：使用 Route Groups（`(group)` 不影响 URL）组织同域页面；Dynamic Segments（`[id]`/`[...slug]`）定义动态路由；Parallel Routes（`@slot`）与 Intercepting Routes（`(.)`/`(..)`）处理模态与并行布局，避免用客户端状态模拟本应由路由表达的结构
- **App Router vs Pages Router 边界**：新代码统一 App Router；迁移时按路由逐个迁移，禁止 `app/` 与 `pages/` 下出现同路径文件；共享逻辑抽取到 `lib/` 或 `components/` 而非跨路由树引用

### 渲染与缓存策略

- **RSC 优先**：将数据获取尽量放到服务端，减少客户端 bundle 与 hydration 成本
- **Server Actions（按项目约定）**：在适用场景使用 Server Actions 处理表单提交与数据变更，避免额外 API 样板
- **缓存策略明确**：理解并显式控制 `fetch` 缓存/重验证行为，避免隐式缓存导致"看似随机"的数据不一致
- **缓存控制 API 选择**：静态内容用 `generateStaticParams` 预生成；按需重验证用 `revalidate: N`（基于时间）或 `tags` + `revalidateTag()`（按需失效）；明确不缓存的用 `noStore()` 或 `cache: 'no-store'`；禁止依赖版本默认行为，必须显式声明意图
- **Streaming 与 Suspense**：在 RSC 中用 `<Suspense fallback={...}>` 包裹慢数据获取组件实现流式渲染；fallback 必须是有意义的骨架屏而非空白；避免在 Suspense 边界内做客户端交互逻辑
- **静态生成元数据**：动态路由页面使用 `generateStaticParams` 声明预渲染路径；使用 `generateMetadata` 异步生成 SEO 元数据（title/description/openGraph），禁止在客户端组件中设置 document.title

### 内置优化组件

- **next/image 优先**：所有 `<img>` 必须替换为 `next/image` 的 `<Image>`，自动响应式、懒加载、格式优化；本地静态图用 `import` 引入，远程图需配置 `remotePatterns`；`priority` 仅用于 LCP 图片
- **next/font 字体优化**：使用 `next/font/google` 或 `next/font/local` 自动子集化与字体回退，禁止通过 `<link>` 引入 Google Fonts 造成渲染阻塞
- **next/link 客户端导航**：内部跳转统一使用 `next/link`，无需手动加 `<a>`（Next 13+ 已不需要且会警告）；`<a>` 仅用于外链

### 中间件与安全边界

- **Middleware 执行边界**：`middleware.ts` 在 Edge Runtime 运行，每次请求执行，仅用于鉴权、重定向、请求头改写；禁止在 Middleware 中做重计算或数据库查询（Edge 限制）；执行路径通过 `matcher` 精确配置，避免拦截静态资源
- **敏感信息保护**：绝不在客户端暴露密钥与敏感配置；权限校验与鉴权在服务端完成
- **外部输入校验**：URL 参数、表单输入在边界做校验，不把 TypeScript 类型当运行时保障

### 错误与降级

- 使用 `error.tsx`/`loading.tsx` 做错误与加载态收敛，避免组件内零散处理

### 类型安全

- 充分利用 TypeScript 类型系统，减少 `any` 类型使用

### 文档化

- 记录缓存策略、鉴权边界与关键路由约定，降低维护成本

## 质量检查清单（技术特定）

### 路由与组件边界

- [ ] 是否遵循 App Router 文件约定（`page.tsx`/`layout.tsx`/`loading.tsx`/`error.tsx`）
- [ ] 是否默认使用 Server Components，仅在需要交互时使用 `'use client'`
- [ ] 数据获取路径是否清晰，避免重复拉取
- [ ] 是否使用 Route Groups/Dynamic Segments/Parallel & Intercepting Routes 表达路由结构
- [ ] 是否避免 `app/` 与 `pages/` 同路径冲突

### 渲染与缓存

- [ ] 数据获取是否尽量放到服务端（RSC 优先）
- [ ] `fetch` 缓存/重验证行为是否显式控制（`revalidate`/`tags`/`noStore`）
- [ ] 是否避免依赖版本默认缓存行为（Next 14→15 默认变更）
- [ ] Streaming 场景是否用 `<Suspense>` 包裹慢组件且 fallback 为有意义的骨架屏
- [ ] 动态路由是否使用 `generateStaticParams`/`generateMetadata` 声明预渲染与 SEO

### 内置优化组件

- [ ] 图片是否统一使用 `next/image`，远程图是否配置 `remotePatterns`
- [ ] 字体是否使用 `next/font` 而非 `<link>` 阻塞渲染
- [ ] 内部跳转是否使用 `next/link`，外链才用 `<a>`

### 中间件与安全

- [ ] Middleware 是否仅用于鉴权/重定向/头改写，是否通过 `matcher` 精确配置
- [ ] 是否避免在客户端暴露密钥与敏感配置
- [ ] 权限校验与鉴权是否在服务端完成
- [ ] URL 参数、表单输入是否在边界做运行时校验

### 错误处理

- [ ] 是否使用 `error.tsx`/`loading.tsx` 收敛错误与加载态
- [ ] 是否避免组件内零散处理错误状态

### 类型安全

- [ ] 是否减少 `any` 类型使用
- [ ] 是否避免将 TypeScript 类型当作运行时保障

## 参考资料

- [Next.js 官方文档](https://nextjs.org/docs) - 框架权威文档
- [App Router 文档](https://nextjs.org/docs/app) - App Router 路由约定
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components) - 服务端组件指南
- [Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions) - 服务端动作
- [Next.js 缓存策略](https://nextjs.org/docs/app/building-your-application/caching) - 缓存机制说明
- [Next.js 15 升级指南](https://nextjs.org/docs/app/building-your-application/upgrading) - 版本升级与破坏性变化
- [next/image 文档](https://nextjs.org/docs/app/building-your-application/optimizing/images) - 图片优化
- [next/font 文档](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) - 字体优化
- [Middleware 文档](https://nextjs.org/docs/app/building-your-application/routing/middleware) - 中间件边界
