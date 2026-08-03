---
name: tech-tailwind
description: Tailwind CSS 框架开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Tailwind CSS 特定的编码标准与质量检查。
tech_id: tailwind
tech_name: Tailwind CSS
category: framework
---

# Tailwind CSS 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Tailwind CSS 特定规范。

## 技术栈定义

Tailwind CSS 是 Utility-first 的 CSS 框架，通过原子化工具类直接在 HTML 中构建样式，配合 `tailwind.config.*` 集中管理设计令牌，通过 PurgeCSS/内容扫描按需生成 CSS，产出体积小、一致性高的样式系统。

## 版本基线

- **Tailwind v3 vs v4 配置范式迁移**：v3 用 `tailwind.config.js`（JS 配置）；v4 改为 CSS-first 配置，通过 CSS 中 `@theme` 指令定义设计令牌，`tailwind.config.*` 退化为可选且仅用于插件/内容扫描兼容；升级需迁移 `theme.extend` 到 `@theme`
- **v4 CSS 变量驱动**：v4 所有设计令牌默认生成为 CSS 自定义属性（如 `--color-primary`），可直接在任意 CSS 中引用 `var(--color-primary)`；运行时主题切换（明暗/品牌）通过覆盖 CSS 变量实现，无需重新编译
- **v4 `@layer`/`@variant`/`@apply` 新语义**：v4 中 `@layer` 用于声明自定义工具层（替代 v3 的 `layerUtilities`）；`@variant` 替代 v3 的 `variants` 配置定义自定义状态变体（如 `@variant pointer-coarse`）；`@apply` 仍可用但在 CSS-first 模式下应优先组合工具类
- **v4 引擎与内容扫描**：v4 使用 Oxide 引擎，默认自动扫描入口文件无需显式 `content` 配置；JIT 模式下动态类名（`bg-[${color}]`）仍不被支持，需用安全列表或静态类名

## 编码规范（技术特定）

### 类名组织

- **类名排序一致**：保持稳定的类名顺序（如布局→盒模型→排版→视觉→交互），优先使用自动排序工具（按项目约定）
- **响应式与状态前缀**：合理使用 `sm:`/`md:`/`lg:` 等断点与 `hover:`/`focus:`/`disabled:` 等状态前缀
- **避免"堆类"失控**：当类名过长或语义不清时，拆分为组件或抽取可复用的 UI 片段
- **group/peer 状态联动**：父子/兄弟状态联动使用 `group-hover:`/`group-[.is-active]:`/`peer-checked:`/`peer-focus:` 等；利用 `has-[]` 选择器（如 `has-[:checked]`）表达父依赖子状态的样式，避免用 JS 维护本应由 CSS 表达的关系

### 配置与设计令牌

- **配置优先**：设计令牌（颜色、间距、字体）优先在 `tailwind.config.*`（v3）或 `@theme` 指令（v4）集中配置
- **抽象克制**：`@apply` 谨慎使用，确保不会制造不可追踪的样式耦合与冲突
- **暗色模式一致**：统一使用 `dark:` 或项目既定方案，避免两套暗色策略并存
- **插件与 Preset 规范**：官方插件（`@tailwindcss/forms`、`@tailwindcss/typography`、`@tailwindcss/aspect-ratio`）按需引入；自定义插件用 `plugin()` 函数封装并通过 Preset 复用；禁止直接复制插件源码到项目造成维护负担
- **容器查询（@container）**：组件级响应式优先使用容器查询（`@container`+`@sm:`/`@md:` 变体）而非仅依赖视口断点，使组件在不同父容器尺寸下自适应；v4 内置支持，v3 需 `@tailwindcss/container-queries` 插件

### 一致性约束

- **减少 arbitrary values**：除非一次性且必要，否则避免 `w-[123px]`、`text-[17px]` 破坏一致性
- **避免权重战**：不通过内联样式和高权重选择器"打补丁"，回到设计令牌与组件边界解决问题
- **组件库集成样式覆盖**：与 Headless UI/Radix/shadcn 集成时，优先通过组件库提供的 props、data 属性、CSS 变量定制；shadcn/ui 应编辑其源码（拷贝式组件）而非用高权重选择器外部覆盖；避免 `!important` 打补丁

### JIT 与内容扫描

- **JIT 内容扫描配置**：确保 `content`（v3）或入口（v4 自动）覆盖所有含类名的文件（模板、组件、JS/TS）；漏配会导致类名被 purge 丢失样式；动态拼接的类名（`bg-${color}`）不被 JIT 识别，必须用完整类名字符串或 `safelist` 声明

### 可测试性

- **可验证样式**：关键布局与交互态应有可复现场景（组件预览/截图对比等按项目约定）

### 文档化

- **约束可见**：断点、主题令牌、组件样式规范需要集中说明并保持一致

## 质量检查清单（技术特定）

### 类名与组织

- [ ] 类名顺序是否一致（或使用自动排序工具）
- [ ] 是否合理使用响应式前缀（`sm:`/`md:`/`lg:`）与状态前缀（`hover:`/`focus:`）
- [ ] 类名过长时是否拆分为组件或抽取可复用片段
- [ ] 父子/兄弟状态联动是否使用 `group:`/`peer:`/`has-[]` 而非 JS 维护

### 配置与令牌

- [ ] 设计令牌是否在 `tailwind.config.*`（v3）或 `@theme`（v4）集中配置
- [ ] `@apply` 是否谨慎使用（避免样式耦合）
- [ ] 暗色模式策略是否统一（`dark:` 或项目既定方案）
- [ ] 插件是否按需引入并通过 Preset 复用，是否避免复制插件源码
- [ ] 组件级响应式是否优先使用容器查询（`@container`）

### 一致性

- [ ] 是否滥用 arbitrary values（`w-[123px]`）破坏设计系统一致性
- [ ] 是否避免在 HTML 中混用 Tailwind 类和内联 `style` 属性
- [ ] 是否避免通过堆叠高权重样式解决问题而不回收设计令牌
- [ ] 组件库（Headless UI/Radix/shadcn）定制是否通过 props/源码编辑/CSS 变量而非 `!important` 覆盖

### JIT 与扫描

- [ ] `content`/入口配置是否覆盖所有含类名的文件（是否漏配导致 purge 丢样式）
- [ ] 是否避免动态拼接类名（`bg-${color}`），动态类名是否用 `safelist` 或完整字符串

### 可验证性

- [ ] 关键布局与交互态是否有可复现场景

## 参考资料

- [Tailwind CSS 官方文档](https://tailwindcss.com/docs) - 框架权威文档
- [Tailwind v4 升级指南](https://tailwindcss.com/docs/upgrade-guide) - v3→v4 迁移与破坏性变化
- [Tailwind 配置参考](https://tailwindcss.com/docs/configuration) - 配置定制指南
- [Tailwind 响应式设计](https://tailwindcss.com/docs/responsive-design) - 断点与响应式前缀
- [Tailwind 暗色模式](https://tailwindcss.com/docs/dark-mode) - 暗色模式实现
- [Tailwind 容器查询](https://tailwindcss.com/docs/container-queries) - 组件级响应式
- [Headless UI](https://headlessui.com/) - 无样式组件库（配合 Tailwind）
- [shadcn/ui](https://ui.shadcn.com/) - 拷贝式组件库（配合 Tailwind）
