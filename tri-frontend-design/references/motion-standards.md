# 动效数值标准（motion-standards.md）

> 本文件是 `tri-frontend-design` 的**动效数值单一事实源**。SKILL.md §6/§7 只给判定流程，所有曲线、时长、弹簧参数、阈值 MUST 取自本文件。
> **铁律：NEVER 近似本文件中出现的任何数值——原样复制。** `cubic-bezier(0.23, 1, 0.32, 1)` 写成 `cubic-bezier(0.25, ...)` 即视为缺陷。
> 来源与归属：蒸馏自 emilkowalski/skills（MIT License, Copyright (c) 2026 Emil Kowalski），去产品化改写。数值与代码原样保留。
> grep 检索：`grep -n "频率\|ease\|cubic-bezier\|spring\|scale(\|0.11\|stagger\|reduced-motion" references/motion-standards.md`

---

## 1. 频率闸门（第一道门 · 未过此门不写任何动效）

| 使用频率 | 裁决 |
|---|---|
| **100+ 次/天**（键盘快捷键、命令面板开合、核心导航） | **不动画。永不。** 到此为止 |
| **数十次/天**（hover 态、列表导航、高频开关） | 仅允许近乎不可感知的动效——快且极弱，或干脆不做 |
| **偶发**（模态框、抽屉、Toast、设置） | 标准动效 |
| **罕见 / 首次**（引导、空状态、成功、庆祝） | 这里是 delight 预算的所在 |

- **键盘触发的动作是取消资格项，不是判断题。** Raycast 的命令面板没有开合动画——那正是每天开合数百次的正确体验。
- 同类动效在不同频率下可以是**对的**也可以是**错的**。判断动效质量 MUST 先问频率。

## 2. 合法目的（六选一，MUST 能指名）

| 目的 | 含义 |
|---|---|
| **Feedback 反馈** | 确认界面听见了用户（按压缩放、长按填充） |
| **Spatial consistency 空间一致性** | 说明某物从哪来、往哪去（Toast 从同一边缘进出、面板从触发器长出） |
| **State indication 状态指示** | 让状态变化可读（按钮形变、手风琴展开） |
| **Preventing a jarring change 防止突兀** | 桥接本会瞬移/凭空出现/消失的内容 |
| **Explanation 解释说明** | 演示功能如何工作（**仅限**营销页/引导） |
| **Delight 愉悦** | **仅允许**出现在「罕见/首次」频率档 |

> **"看起来很酷"不在列表里。** 若指名不了上述任一目的，MUST 不写该动效——这是成功，不是推诿。
> 附加功能检查：用户正在**阅读或据以操作**的数据，MUST NOT 为风格而动。装饰性鼠标跟随属于营销页，不属于银行 App 的图表。

## 3. 缓动（Easing）

### 3.1 决策序（自上而下匹配，命中即停）

| 场景 | 缓动 |
|---|---|
| 入场 / 出场 | `ease-out` |
| 屏上移动 / 形变 | `ease-in-out` |
| Hover / 颜色变化 | `ease` |
| 匀速运动（跑马灯、进度） | `linear` |
| 默认兜底 | `ease-out` |

### 3.2 强自定义曲线（CSS 内置缓动太弱）

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);        /* UI 强 ease-out */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);    /* 屏上移动的强 ease-in-out */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);     /* iOS 风格抽屉曲线 */
```

- **NEVER 在 UI 上使用 `ease-in`。** 它起步慢，恰好延迟了用户注视最集中的那一刻。`ease-out` 200ms **感觉上**比 `ease-in` 200ms 更快。
- 需要这三條之外的曲线，取自 easing.dev / easings.co，**NEVER 手搓**。

## 4. 时长预算

| 元素 | 时长 |
|---|---|
| 按钮按压反馈 | 100–160ms |
| Tooltip、小型 popover | 125–200ms |
| 下拉、选择器 | 150–250ms |
| 模态框、抽屉 | 200–500ms |
| 营销 / 解释性 | 可以更长 |

- **铁律：UI 动效 MUST 停留在 300ms 以内。** 180ms 的下拉比 400ms 的更"响应"。
- 超过 300ms 的 UI 动效若无书面理由，即是缺陷。
- 更快的 spinner 让加载**感觉**更快（实际耗时相同）。Toolbar 上第一个 tooltip 之后应跳过延迟与动画，让整个工具栏感觉更快。

## 5. 物理性与原点

- **NEVER `scale(0)`。** MUST 从 `scale(0.9–0.97)` + `opacity: 0` 起步——现实中没有东西是从虚无中出现的。
- **原点感知的弹出层。** Popover / 下拉 / tooltip MUST 从触发器缩放，而非中心：
  ```css
  .popover { transform-origin: var(--transform-origin); } /* Base UI 提供该变量 */
  ```
  **模态框豁免**——它在视口居中，保持 `transform-origin: center`。
- **按压反馈。** 任何可按压元素：`:active` 时 `transform: scale(0.97)`，`transition: transform 160ms ease-out`。幅度保持克制（0.95–0.98）。

## 6. 弹簧（Springs）

弹簧自然是因为它模拟物理；**没有固定时长**——它按参数自行收敛。适用于：带惯性的拖拽、"活着"的元素（Dynamic Island）、可中断手势、装饰性鼠标跟随。

```js
// Apple 风格（更易推理）—— 推荐
{ type: "spring", duration: 0.5, bounce: 0.2 }

// 传统物理（控制更细）
{ type: "spring", mass: 1, stiffness: 100, damping: 10 }
```

- bounce MUST 保持克制（**0.1–0.3**）；大多数 UI 避免 bounce——仅在拖拽消除与玩趣性交互中预留。
- 弹簧在被打断时**保留速度**（keyframes 从零重启），因此是用户可能中途反向的手势的首选。
- 鼠标交互：用 `useSpring` 插值，NEVER 把值直接绑死到鼠标位置（直接绑定 = 人工感、无惯性）。仅当动效是装饰性时这样做。

## 7. 可中断性

CSS **transitions** 可在动画中途被中断并重定向；**keyframes** 从零重启。任何被快速触发或可逆的动效（Toast 堆叠、开关、拖拽、展开/折叠）MUST 用 transition 或 spring。

```css
/* 可中断 —— 适合动态 UI */
.toast { transition: transform 400ms ease; }

/* 不可中断 —— 动态 UI 应避免 */
@keyframes slideIn { from { transform: translateY(100%); } to { transform: translateY(0); } }
```

无 JS 入场用 `@starting-style`：

```css
.toast {
  opacity: 1; transform: translateY(0);
  transition: opacity 400ms ease, transform 400ms ease;
  @starting-style { opacity: 0; transform: translateY(100%); }
}
```

旧环境兜底：`useEffect(() => setMounted(true), [])` + `data-mounted` 属性。

## 8. 非对称时序（Asymmetric timing）

用户**决策**处慢，系统**响应**处快。

```css
.overlay { transition: clip-path 200ms ease-out; }            /* 释放：快 */
.button:active .overlay { transition: clip-path 2s linear; }  /* 按压：慢而郑重 */
```

按压-释放或长按交互上的**对称时序即是缺陷**。

## 9. 性能

- **只动 `transform` 和 `opacity`**——它们跳过 layout/paint，跑在 GPU 上。`padding`/`margin`/`height`/`width`/`top`/`left` 会触发全部三个渲染步骤。
  - `clip-path` 是获准的"第四个属性"（见 `motion-recipes.md`）。
  - `height` 仅在手风琴处被容忍（那里没有 transform 等价物），且时长 MUST 短。
- **`transition: all` 一律是缺陷**——它会把非预期属性带到 GPU 之外。
- **NEVER 通过父元素的 CSS 变量驱动子元素 transform**——它会为所有子元素重算样式。MUST 直接在元素上设 `transform`：
  ```js
  element.style.setProperty('--swipe-amount', `${d}px`); // 错：所有子元素重算
  element.style.transform = `translateY(${d}px)`;        // 对：只影响该元素
  ```
- **Motion/Framer Motion 的 `x`/`y`/`scale` 简写不是硬件加速的**——它们走主线程 rAF，页面繁忙时掉帧。MUST 用完整 transform 字符串：
  ```jsx
  <motion.div animate={{ x: 100 }} />                          // 繁忙时掉帧
  <motion.div animate={{ transform: "translateX(100px)" }} />  // 硬件加速
  ```
- **负载下 CSS 动画胜过 JS**——CSS 跑在主线程之外；rAF 动画在浏览器加载/执行脚本/绘制时会卡顿。预定动效用 CSS，动态/可中断用 JS。
- **WAAPI** 兼得 JS 控制与 CSS 性能（硬件加速、可中断、零依赖）：
  ```js
  element.animate([{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)' }],
    { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' });
  ```
- 过渡期间的 `filter: blur()` MUST < 20px——重模糊很贵，Safari 尤甚。

## 10. Transform 与 clip-path

- **`translate` 百分比相对元素自身尺寸**——`translateY(100%)` 无论内容多高都移动自身高度（Sonner/Vaul 定位 toast/抽屉的方式）。优先于硬编码 px。
- **`scale()` 会连子元素一起缩放**（字号、图标、内容）——这正是按压反馈读起来"物理"的原因。
- **3D**：`rotateX/rotateY` + `transform-style: preserve-3d` 无需 JS 即可做出深度/环绕/翻转。
- **`clip-path: inset(t r b l)`** 是强力动画工具：每个值从对应边内啃。用途：滚动揭示（`inset(0 0 100% 0)` → `inset(0 0 0 0)`）、长按删除覆盖层、无缝 tab 色彩过渡（复制一份再裁剪激活副本）、对比滑块。

## 11. 手势与拖拽

- **动量消除**：NEVER 只要求跨过距离阈值——MUST 计算速度 `Math.abs(distance)/elapsedMs`，`> ~0.11` 即消除。一次轻扫就该够。
- **边界阻尼**：拖过自然边界时，越远移动越少（真实物体在停下前会减速）。
- **指针捕获**：拖拽开始即 `setPointerCapture`，指针离开边界后继续跟踪。
- **多点触控保护**：拖拽开始后忽略新增触点（`if (isDragging) return`），否则中途换指会让元素跳。
- **摩擦优于硬停**——允许越界拖拽并施加递增阻力，而非一堵看不见的墙。

## 12. 交错（Stagger）

成组入场做交错，项间 **30–80ms**。更长的延迟会让人觉得慢。
**交错是装饰性的——NEVER 在它播放期间阻塞交互。**

```css
.item { opacity: 0; transform: translateY(8px); animation: fadeIn 300ms ease-out forwards; }
.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
@keyframes fadeIn { to { opacity: 1; transform: translateY(0); } }
```

## 13. 无障碍（a11y）

```css
@media (prefers-reduced-motion: reduce) {
  .element { animation: fade 0.2s ease; } /* 保留 opacity/颜色，去掉 transform 位移 */
}
@media (hover: hover) and (pointer: fine) {
  .element:hover { transform: scale(1.05); } /* 触屏点击会误触发 hover */
}
```

```jsx
const reduce = useReducedMotion();
const closedX = reduce ? 0 : '-100%';
```

- **reduced-motion 意味着更少、更轻柔的动效，而非零动效**——保留有助理解的过渡，去掉位移与位置变化。
- 另两个独立信号（见 `motion-physics.md` §14）：`prefers-reduced-transparency: reduce`、`prefers-contrast: more`。
- reduced-motion 与 hover 门控 MUST **随动效一同交付**，NEVER 作为后续补做。

## 14. 交叉淡入遮罩（Masking imperfect crossfades）

当交叉淡入在调过缓动与时长后仍显出两个重叠状态，在过渡期间加一点 `filter: blur(2px)`，把两者融为一次感知上的形变。blur MUST < 20px。

无 blur 时，眼睛读到的是两个不同物体在互换；blur 让它们融为一个形变过程。

## 15. 内聚（Cohesion）

动效 MUST 匹配组件的**个性**：玩趣的可以更弹，专业仪表盘应当 crisp 而快。
SONNER 之所以感觉对，部分因为缓动、时长、设计乃至命名彼此和谐——略慢、用 `ease` 而非 `ease-out`，以显得优雅。进场/出场列表中的 opacity 与 height 配合属试错范畴，**没有公式**——调到感觉对为止。

> 本 skill 把这条标准提升为**可执行能力**：个性即锚点，见 SKILL.md §7「锚点↔动效基线映射」。

## 16. 调试（手感不确定时必做）

- **慢放**：时长放大 2–5× 或用 DevTools 动画检查器。检查颜色是否干净地交叉淡入、缓动是否戛然而止、`transform-origin` 是否正确、协同属性是否同步。
- **逐帧**：Chrome DevTools Animations 面板能暴露协同属性之间的时序漂移。
- **真机**测手势（抽屉、滑动）——连上手机，用 IP 访问开发服务器，用 Safari 远程调试。
- **隔天用新鲜眼睛看**——开发期间看不见的瑕疵之后会浮出来。

> 当手感无法从代码判定时，MUST 明说并给出 feel-check 步骤，**NEVER 猜一个值了事**。

---

## 数值保真核验（6 项关键值）

| # | 值 | 出现位置 |
|---|---|---|
| 1 | `cubic-bezier(0.23, 1, 0.32, 1)` | §3.2 `--ease-out` |
| 2 | `cubic-bezier(0.77, 0, 0.175, 1)` | §3.2 `--ease-in-out` |
| 3 | `cubic-bezier(0.32, 0.72, 0, 1)` | §3.2 `--ease-drawer` |
| 4 | `0.11`（动量消除速度阈值） | §11 |
| 5 | `scale(0.97)`（按压反馈） | §5 |
| 6 | 30–80ms（交错） | §12 |
