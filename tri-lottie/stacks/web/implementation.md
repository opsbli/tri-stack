---
name: web-implementation
description: Web 端动效实现——lottie-web / dotLottie Web 与声明式动画（CSS/Framer Motion/GSAP）选型、API 映射、资产规范、代码模板。核验于 2026-09，lottie-web 主版本 3.x。
---

# Web 端实现（stacks/web）

## 一、库选型决策树

```
动效需求
├── 简单属性动效（hover/按压/淡入位移 <5 元素）→ CSS transition/animation（零依赖，transform+opacity only）
├── 复杂编排/手势驱动/React 组件级 → Framer Motion（React）或 GSAP（框架无关，时间线编排最强）
└── 设计师导出的复杂矢量动效 → Lottie 资产
    ├── 标准 JSON 资产 → lottie-web（SVG 渲染器：图标/UI 清晰可交互；Canvas 渲染器：复杂多元素高性能）
    └── .lottie 压缩资产/主题化 → dotLottie Web 运行时
```

**选型铁律**：CSS 能表达的不用 JS 库；Lottie 资产用于「手写代码无法复现的复杂矢量动效」。NEVER 为一个 hover 引入 lottie-web。

## 二、安装与版本约束

```bash
npm i lottie-web          # 主力（SVG/Canvas/HTML 三渲染器）
npm i dotlottie-web       # 备选（.lottie 格式）
```

现代浏览器即可（ES5+）；框架封装（lottie-react / lottie-vue）按项目框架选用。CDN 引入亦可（生产建议锁版本）。

## 三、概念 → API 映射

| 决策概念 | Web 实现 |
|---------|---------|
| ease-out | `cubic-bezier(0, 0, 0.2, 1)`（CSS）/ lottie 资产内置 |
| ease-in-out | `cubic-bezier(0.4, 0, 0.2, 1)` |
| 过冲（Playful） | `cubic-bezier(0.175, 0.885, 0.32, 1.275)`（CSS）/ JS spring 库 |
| 时长 | CSS `transition-duration` / lottie 帧率内嵌 |
| stagger | CSS `transition-delay: calc(var(--i) * 50ms)` / GSAP `stagger: 0.05` |
| 播放/暂停/停止 | `anim.play()` / `anim.pause()` / `anim.stop()` |
| 循环 | `loop: true`（loadAnimation 参数） |
| 速度 | `anim.setSpeed(x)` |
| 跳帧/分段 | `anim.goToAndStop(frame, true)` / `anim.playSegments([s,e], true)` |
| 方向 | `anim.setDirection(-1)` |
| 完成回调 | `anim.addEventListener('complete', fn)` |
| 主题换色 | 资产预处理（Web 端运行时换色支持有限，优先导出时定色） |
| 销毁 | `anim.destroy()`（组件卸载 MUST 调用，防内存泄漏） |

## 四、资产规范与坑位

1. JSON 放 `public/animations/`（或打包进 bundle 用 import）；带图资产打 .zip 随 JSON 引用
2. **组件卸载必须 `anim.destroy()`**——React/Vue SPA 高频挂载页必查（内存泄漏首因）
3. SVG 渲染器：清晰、DOM 可交互、适合 <50 图层的 UI 动效；Canvas 渲染器：复杂多元素、大面积场景；HTML 渲染器基本弃用
4. AE 表达式（Expressions）在 Web 运行时支持不全——导出前在预览工具验证
5. 大 JSON（>100KB）考虑压缩格式或简化图层；首屏关键动画同步加载，非关键 `requestIdleCallback` 延迟初始化

## 五、代码模板（黄金用例）

规格单：〔卡片入场|Premium|position+opacity|350ms|cubic-bezier(0.4,0,0.2,1)|0%|primary+secondary(shadow 延迟 50ms)〕

**分支 A：声明式（CSS，本规格推荐）**

```html
<div class="card-enter" style="--stagger: 0">
  <div class="card-enter__shadow"></div>
  <p class="card-enter__content">Card content</p>
</div>
```

```css
/* CRITICAL 自检：transform+opacity only，非 linear，非纯 opacity */
.card-enter {
  opacity: 0;
  transform: translateY(20px);
  animation: card-enter 350ms cubic-bezier(0.4, 0, 0.2, 1) forwards;
  animation-delay: calc(var(--stagger) * 60ms);
}
.card-enter__shadow {
  opacity: 0;
  animation: shadow-in 300ms cubic-bezier(0.4, 0, 0.2, 1) 50ms forwards; /* secondary 延迟 50ms */
}
.card-enter__content {
  opacity: 0;
  animation: fade-in 250ms ease-out 100ms forwards;
}
@keyframes card-enter { to { opacity: 1; transform: translateY(0); } }
@keyframes shadow-in  { to { opacity: 1; } }
@keyframes fade-in    { to { opacity: 1; } }

/* a11y 降级（HIGH：H6） */
@media (prefers-reduced-motion: reduce) {
  .card-enter, .card-enter__shadow, .card-enter__content {
    animation-duration: 1ms;
    animation-delay: 0ms;
  }
}
```

**分支 B：Lottie 资产（复杂矢量动效时）**

```javascript
import lottie from 'lottie-web';

// 在组件挂载后调用；卸载时必须 destroy()
function mountCardAnimation(container, jsonUrl) {
  const anim = lottie.loadAnimation({
    container,              // 挂载 DOM 元素
    renderer: 'svg',        // UI 动效用 svg；复杂多元素换 canvas
    loop: false,            // 入场动画单次
    autoplay: true,
    path: jsonUrl,          // '/animations/card-enter.json'
  });
  anim.addEventListener('complete', () => { /* 预备回调整理 */ });
  return anim;              // 保存引用，卸载时 anim.destroy()
}
```

## 六、性能与 a11y

- 动画属性仅 `transform` + `opacity`（GPU 合成层）；`width/height/margin/box-shadow` 动画 = 掉帧
- 视口内动画元素 < 20；多元素用 stagger 摊平峰值
- `will-change: transform` 仅用于确将动画的元素，用完移除
- 60fps 目标；环境动效 30fps 可接受
- **reduced-motion**：`@media (prefers-reduced-motion: reduce)` 全量降级（去位移/去循环/时长趋零/保留 opacity 淡入）；关键信息 NEVER 仅靠动效传达
- 暗色模式：动效强度 -10-20%，禁纯白闪烁
