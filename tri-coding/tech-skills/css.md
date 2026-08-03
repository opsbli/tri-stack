---
name: tech-css
description: CSS 样式开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 CSS 特定的编码标准与质量检查。
tech_id: css
tech_name: CSS
category: language
---

# CSS 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 CSS 特定规范。

## 技术栈定义

CSS 是层叠样式表语言，用于描述网页的呈现与布局。现代 CSS 通过 Flexbox/Grid 布局、CSS 变量（自定义属性）、媒体查询响应式设计等特性，配合 SCSS/Sass 等预处理器，实现可维护、可复用的样式系统。

## 版本基线

- **CSS Nesting（2023+ 原生嵌套）**：主流浏览器（Chrome 112+ / Safari 16.5+ / Firefox 117+）原生支持嵌套语法（`& > .child { }`），减少对 SCSS/Sass 等预处理器的依赖；注意 `&` 必须显式书写且解析规则与预处理器存在差异（如裸标签嵌套的隐式 `&` 行为），从预处理器迁移到原生嵌套时需校验选择器组合与编译产物
- **Container Queries（容器查询）**：`@container` 与 `container-type: inline-size`（Chrome 105+ / Safari 16+ / Firefox 110+）支持"按容器尺寸"而非"按视口"做响应式布局，颠覆传统媒体查询思路；旧浏览器需 polyfill，且容器查询尺寸上下文与视口单位（`vw`/`vh`）行为不同，`cqw`/`cqh` 等容器单位需在容器内生效
- **:has() 选择器（父选择器）**：`:has()`（Safari 15.4+ / Chrome 105+ / Firefox 121+）提供前所未有的"父级/前置兄弟"选择能力，改变状态驱动样式写法；属功能性破坏性变化（旧代码无法实现的能力），但需关注降级策略与性能影响（避免在大型 DOM 上过度使用）
- **@layer 层级（Cascade Layers）**：`@layer`（Chrome 99+ / Safari 15.4+ / Firefox 97+）显式控制层叠优先级，从根本上解决权重战争问题；但分层规则与未分层规则的优先级关系容易误用（未分层规则优先级高于具名层），引入后需统一项目分层约定，否则反而加剧样式混乱

## 编码规范（技术特定）

### 选择器与优先级

- **避免权重战争**：不通过堆叠选择器或 `!important` 提高优先级，回到命名约定与组件边界解决问题
- **选择器简洁**：避免过深嵌套，优先使用类选择器，避免标签选择器与 ID 选择器用于样式
- **BEM 命名**：按项目约定采用 BEM（Block Element Modifier）等命名规范，保持类名语义化与可预测

### 布局

- **Flexbox 优先**：一维布局优先使用 Flexbox（`display: flex`）
- **Grid 用于二维布局**：二维布局使用 CSS Grid（`display: grid`）
- **避免浮动布局**：除特殊场景外，避免使用 `float` 进行布局

### 响应式设计

- **策略明确**：遵循移动优先或桌面优先（按项目约定），避免两套断点并存
- **媒体查询**：使用 `@media` 断点适配不同视口，断点值集中管理

### CSS 变量

- **设计令牌集中**：颜色、间距、字体等设计令牌使用 CSS 自定义属性（`--var`）在 `:root` 集中定义
- **主题切换**：通过修改变量实现主题切换（如暗色模式）

### 兼容与降级

- **降级路径**：对兼容性敏感属性提供降级路径，避免"只在某端可用"的样式依赖
- **渐进增强**：先保证基础可用，再叠加增强特性

### 预处理器（按项目约定）

- **SCSS/Sass**：按项目约定使用预处理器，变量、混入、嵌套提高复用性
- **避免过度嵌套**：嵌套层级不超过 3 层，保持编译后选择器简洁

### 现代特性

- **CSS Layers**：使用 `@layer` 显式控制层叠优先级（如 `@layer reset, base, components, utilities;`），将第三方样式、重置样式、组件样式分层管理，从根本上解决权重战争；未分层规则优先级高于具名层，项目需统一分层约定，避免引入后反而加剧样式混乱
- **容器查询**：组件级响应式优先使用 `@container` 与 `container-type: inline-size`，按容器尺寸而非视口适配布局，适配可复用组件内嵌不同容器的场景；容器单位 `cqw`/`cqh` 需在已声明 `container-type` 的容器内生效，旧浏览器需 polyfill
- **:has() 选择器**：合理使用 `:has()` 实现父级/兄弟状态联动样式，避免在大型 DOM 树上高频使用导致性能问题；兼容性敏感场景需提供降级路径

### 动画与性能

- **动画属性优选**：动画优先使用 `transform` 与 `opacity`（GPU 加速、不触发重排），避免动画 `width`/`height`/`top`/`left` 等触发重排的属性
- **will-change 谨慎使用**：对已知会动画的元素预先声明 `will-change`，动画结束及时移除，避免长期占用 GPU 资源导致内存膨胀

## 质量检查清单（技术特定）

### 选择器与命名

- [ ] 是否避免使用 `!important` 打补丁
- [ ] 类名是否符合 BEM 等项目命名约定
- [ ] 选择器嵌套是否过深（建议不超过 3 层）
- [ ] 是否避免 ID 选择器用于样式

### 布局与响应式

- [ ] 一维布局是否使用 Flexbox，二维布局是否使用 Grid
- [ ] 是否避免 `float` 布局
- [ ] 响应式策略是否统一（移动优先或桌面优先）
- [ ] 断点值是否集中管理

### 设计令牌

- [ ] 颜色、间距、字体是否使用 CSS 变量集中定义
- [ ] 是否避免硬编码魔法值

### 兼容性

- [ ] 兼容性敏感属性是否提供降级路径
- [ ] 是否避免"只在某端可用"的样式依赖

## 参考资料

- [MDN CSS 文档](https://developer.mozilla.org/zh-CN/docs/Web/CSS) - CSS 权威参考
- [CSS Flexbox 布局](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_flexible_box_layout) - Flexbox 指南
- [CSS Grid 布局](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_grid_layout) - Grid 指南
- [BEM 命名规范](https://getbem.com/) - Block Element Modifier
- [Sass 官方文档](https://sass-lang.com/documentation/) - 预处理器文档
