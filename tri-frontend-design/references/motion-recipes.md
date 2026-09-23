# 动效配方库（motion-recipes.md）

> 高频场景的即用实现。**从配方起步再适配，NEVER 从零重建。**
> 曲线统一引用 `motion-standards.md` §3.2 的 `--ease-out` / `--ease-in-out` / `--ease-drawer` 三个令牌；MUST 原样使用，NEVER 近似。
> 来源与归属：蒸馏自 emilkowalski/skills（MIT License, Copyright (c) 2026 Emil Kowalski），去产品化改写。数值与代码原样保留。
> grep 检索：`grep -n "^## " references/motion-recipes.md`

---

## 1. 按钮按压

任何可按压元素。即时反馈"界面听见了你"。

```css
.button {
  transition: transform 160ms var(--ease-out);
}

.button:active {
  transform: scale(0.97);
}
```

`scale()` 会连子元素一起缩放——标签与图标跟着走，这正是它读起来像物理按压的原因。
此处**无需 hover 门控**：`:active` 在触屏上是真实按压。任何 `:hover` 样式须单独门控。

---

## 2. 下拉 / 弹出层 / 菜单 / 选择器

从触发器长出，而非凭空出现。

```css
.popover {
  transform-origin: var(--transform-origin); /* Base UI 提供该变量 */
  transition:
    opacity 200ms var(--ease-out),
    transform 200ms var(--ease-out);
}

.popover[data-starting-style],
.popover[data-ending-style] {
  opacity: 0;
  transform: scale(0.95);
}
```

`transform-origin` 是全部要点——面板应当看起来是从你点的那个东西里长出来的。

---

## 3. Tooltip

与 popover 同形，更快，加上大多数实现漏掉的那一手。

```css
.tooltip {
  transform-origin: var(--transform-origin);
  transition:
    transform 125ms var(--ease-out),
    opacity 125ms var(--ease-out);
}

.tooltip[data-starting-style],
.tooltip[data-ending-style] {
  opacity: 0;
  transform: scale(0.97);
}

/* 一旦有一个 tooltip 打开，相邻的即时打开 */
.tooltip[data-instant] {
  transition-duration: 0ms;
}
```

初始延迟用于防误触。此后**同时跳过延迟与动画**，让整个工具栏感觉更快。

---

## 4. 模态框

唯一保持居中的弹出层。

```css
.modal {
  transform-origin: center; /* 豁免——不锚定触发器 */
  transition:
    opacity 250ms var(--ease-out),
    transform 250ms var(--ease-out);
}

.modal[data-starting-style],
.modal[data-ending-style] {
  opacity: 0;
  transform: scale(0.96);
}

.backdrop {
  transition: opacity 250ms var(--ease-out);
}
```

遮罩的 opacity 必须与模态框**同时**动画，让两者读起来是一个整体表面。

---

## 5. 抽屉 / 面板（Drawer / Sheet）

```css
.drawer {
  transform: translateY(0);
  transition: transform 500ms var(--ease-drawer);
}

.drawer[data-closed] {
  transform: translateY(100%);
}
```

这是 Vaul 在动画入场前隐藏抽屉的方式。
加上拖拽就变成手势问题——见 §12「拖拽消除」。

---

## 6. Toast

```css
.toast {
  opacity: 1;
  transform: translateY(0);
  transition:
    opacity 400ms ease,
    transform 400ms ease;

  @starting-style {
    opacity: 0;
    transform: translateY(100%);
  }
}
```

- 这里用 **`ease` 而非 `ease-out`**，且比典型 UI 略慢：Sonner 读起来优雅，部分正因它的动效是**按组件个性**调的，而非按通用 UI 预算。
- `@starting-style` 不可用时，回退到挂载标记：

```jsx
useEffect(() => { setMounted(true); }, []);
// <div data-mounted={mounted}>
```

多个 toast 堆叠导致列表重排时，opacity 变化要与 height 变化对抗。**这一对没有公式**——调到感觉对，然后隔天再看一次。

---

## 7. 手风琴 / 折叠

```css
.content {
  overflow: hidden;
  transition:
    height 200ms var(--ease-out),
    opacity 200ms var(--ease-out);
}
```

MUST 保持短——这是少数**每一帧都要付出 layout 代价**的动画之一，长时长既迟钝又昂贵。
用 JS 测量内容高度（或用提供高度的 headless 原语），NEVER 动画到 `auto`。

---

## 8. 成组入场交错

用于用户**偶发**看到的列表或网格——不是他们整天滚来滚去的列表。

```css
.item {
  opacity: 0;
  transform: translateY(8px);
  animation: fadeIn 300ms var(--ease-out) forwards;
}

.item:nth-child(2) { animation-delay: 50ms; }
.item:nth-child(3) { animation-delay: 100ms; }
.item:nth-child(4) { animation-delay: 150ms; }

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

交错是装饰性的——**NEVER 在播放期间阻塞交互**。

---

## 9. 长按确认

用于"一次普通点击太容易误触"的破坏性操作。

```css
.overlay {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 200ms var(--ease-out); /* 释放：利落 */
}

.button:active .overlay {
  clip-path: inset(0 0 0 0);
  transition: clip-path 2s linear;             /* 按压：慢而郑重 */
}

.button:active {
  transform: scale(0.97);
}
```

此处 `linear` 是正确的——填充是进度指示，进度不该缓动。

---

## 10. Tab 指示器（色彩过渡）

逐个 tab 做颜色过渡怎么调都落不到位。**改用裁剪。**
复制一份 tab 列表，把副本样式设为激活态（不同背景、不同文字色），裁剪副本只露出激活项，切换时动画裁剪区域：

```css
.tabs-active-copy {
  clip-path: inset(0 60% 0 20%); /* 由激活 tab 的位置驱动 */
  transition: clip-path 250ms var(--ease-in-out);
}
```

文字与背景**完全同步**地变化，因为它们是同一个元素在被揭示，而不是两个颜色在被插值。

---

## 11. 滚动揭示

**仅限营销页面。NEVER 对每天使用的功能性 UI 这么做。**

```css
.reveal {
  clip-path: inset(0 0 100% 0);
  transition: clip-path 600ms var(--ease-in-out);
}

.reveal[data-visible] {
  clip-path: inset(0 0 0 0);
}
```

用 `IntersectionObserver` 或 Motion 的 `useInView` 配 `{ once: true, margin: "-100px" }` 触发。
**只触发一次**——每次滚过都重播，是界面在与读者作对。

---

## 12. 拖拽消除

手势配方。用**弹簧而非时长**，因为用户可能中途反向。

```js
// 靠一次轻扫消除，而非仅靠距离
const timeTaken = Date.now() - dragStartTime.current;
const velocity = Math.abs(swipeAmount) / timeTaken;

if (Math.abs(swipeAmount) >= SWIPE_THRESHOLD || velocity > 0.11) {
  dismiss();
}
```

```js
// 直接在被拖元素上设 transform。
// 经父元素 CSS 变量驱动会为每个子元素重算样式。
element.style.transform = `translateY(${distance}px)`;
```

区分好拖拽与坏拖拽的四个细节：

- **指针捕获**：拖拽开始即捕获，指针离开元素边界后继续跟踪。
- **多点触控保护**：新触点 `if (isDragging) return`，否则中途换指元素会跳。
- **越界阻尼**：越过自然边界后拖得越远移动越少。真实物体在停下前会减速。
- **摩擦而非墙**：允许越界并施加递增阻力，而不是直接拒绝。

用弹簧收尾，让被打断的拖拽保留速度：

```js
{ type: "spring", duration: 0.5, bounce: 0.2 }
```

---

## 13. 交叉淡入遮罩

当过渡中两个状态明显重叠，且无论怎么调缓动与时长都解决不了时，**模糊那条接缝**：

```css
.content {
  transition:
    filter 200ms ease,
    opacity 200ms ease;
}

.content.transitioning {
  filter: blur(2px);
  opacity: 0.7;
}
```

没有 blur，眼睛读到的是两个不同物体在互换；blur 把它们融为一次感知上的形变。
blur MUST 保持在 20px 以下——重模糊很贵，Safari 尤甚。

---

## 14. 无需依赖的程序化动效（WAAPI）

当动效需要 JS 控制但不想引入依赖时，WAAPI 给出 CSS 级性能：

```js
element.animate(
  [{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }],
  { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' }
);
```

硬件加速、可中断、零打包成本。

---

## 工具选择（能用的最便宜工具）

自上而下匹配，命中即停：

| 需要 | 工具 |
|---|---|
| Hover / 按压 / 颜色 / 用 class 或属性控制的状态切换 | **CSS transition** |
| 挂载入场，无 JS 状态 | **CSS `@starting-style`** |
| 预定动效，且页面繁忙加载时仍须平滑 | **CSS animation**（跑在主线程之外） |
| 程序化控制 + CSS 性能，不要库 | **WAAPI**（`element.animate()`） |
| 弹簧 / 布局动画 / 出场动画 / 手势驱动的值 | **Motion**（motion.dev） |

> **NEVER 为一个 fade 装动效库。**
> 若需要的其实是**组件**（toast、抽屉、命令菜单、下拉）而非动画，MUST 停止并转介 tri-coding 做库选型——手搓这些的下场是一个没有焦点管理的 `<div>` 下拉。
