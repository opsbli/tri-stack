# 多变体探索与 Picker 规格（variants-picker.md）

> `variants` 模式的方法论 + picker 的**逐字规格**。
> picker 的外观**不是设计决策**——它就是这个规格。MUST 逐字复制下面的标记、CSS 与接线；每轮运行只有变体名与数量会变。它在所有项目中保持一致，因此永远读作"harness chrome"，而绝不会被误当作被评审设计的一部分。**NEVER 用项目令牌、字体或颜色重新设计它。**
> 来源与归属：蒸馏自 emilkowalski/skills（MIT License, Copyright (c) 2026 Emil Kowalski），去产品化改写。
> grep 检索：`grep -n "proto-picker\|Phase\|分歧轴\|Completion criterion" references/variants-picker.md`

---

## Part A · 方法论：分歧即价值

> 本 skill 的全部价值是**分歧**：三个同一想法的色差变体是在浪费 picker——用户在它们之间翻来翻去学不到任何东西。每个变体 MUST 是一个你**能单独为它辩护并交付**的方向，探索对同一简报的一个真正不同的答案。

**分歧不是降低工艺门槛的借口。** 每个变体都单独达到 `motion-standards.md` 的标准——正确的缓动（入场 `ease-out`，NEVER `ease-in`）、UI 动效 <300ms、正确的 `transform-origin`、只动 `transform`/`opacity`、reduced-motion 已处理。一个潦草的变体不会拓宽探索，它只是输在执行上，且教不会用户任何关于那个方向的东西。

### 硬规则

1. **探索期间 NEVER 触碰生产代码。** 一切位于隔离的原型面（见 Phase 4）。集成只发生在 Phase 6，且只针对用户选中的那一个变体。
2. **变体 MUST 在一个被指名的轴上分歧**——布局、密度、个性、动效、交互模型。动工前，MUST 能用一句话说出每个变体的轴。共享项目令牌不算趋同；变体**应当**感觉是这个产品原生的。
3. **每个变体都完整可用。** 真实交互、真实动效、真实感内容——实际产品形态的文案、可信的姓名与数字。无 lorem ipsum、无死按钮、无"想象这里有什么"。
4. **picker 是 chrome，不是选手。** 其标记、样式与行为由本文件 Part B 规定，逐字复制。它的外观不是设计决策，NEVER 适配项目。
5. **选完即清理。** 胜出变体被提升后，删除原型面，除非用户要求保留。

### 与单锚点铁律的关系（MUST 遵守）

`variants` 模式的分歧轴是**锚点内部**的——布局 / 密度 / 交互模型 / 动效叙事。
**NEVER 跨锚点混搭。** 单锚点铁律在 `variants` 模式下不破：所有变体 MUST 同属一个锚点，在其令牌范围内各自探索。

### 六阶段流程

| Phase | 内容 |
|---|---|
| **1 · 划范围** | 一轮只做一件事。若描述跨越多个组件（"整个看板"），收窄：挑出杠杆最高的那一块，说明挑了哪个及理由，其余作为后续轮次。用一句话重述简报——它是什么、将存在于何处、必须做什么 |
| **2 · 侦察** | 设计前先测绘变体必须站立的地面：**技术栈**（框架、样式系统、动效库）；**令牌**（颜色、圆角、间距、字体、缓动/时长变量——变体 MUST 用这些，每个变体都要看起来明天就能上线）；**个性**（玩趣的消费级 App，还是 crisp 的仪表盘——这框定了最大胆变体能走多远）；**上下文**（它渲染在何处——什么背景之上、旁边是什么邻居、什么尺寸）。<br>若没有项目（空目录，或用户只是在探索），跳到 Phase 4 的独立分支，并选一个克制的默认外观：中性灰、一种强调色、系统字体栈 |
| **3 · 选方向** | 默认 **3 个**变体；用户要求或设计空间确实宽时可到 **5 个**。超过 5 个会稀释比较。<br>动工前先列出这一组：每个一个名字 + 一个轴。名字描述方向——"Quiet""Editorial""Playful""Dense"——NEVER "Option A/B/C"。若两个拟定方向只差强调色或文案，它们是同一个方向；把其中一个换成真正的替代方案（不同布局、不同交互模型、不同动效叙事）。<br>**完成判据：** 每个变体都有名字与声明的轴，且没有两个变体占据同一轴位置 |
| **4 · 建 picker harness** | 两条分支，按现状选：<br>**项目内有 dev server** —— 一条隔离路由或页面（`/prototypes/<slug>` 或框架等价物），每个变体一个文件 + 一个小 harness 文件。NOTHING 从原型面导入生产代码。<br>**无项目 / 静态上下文** —— 一个自包含 HTML 文件（内联 CSS/JS），用户可直接用浏览器打开。<br>picker 的标记、样式、键盘接线与位置取自 Part B，**逐字**照做。<br>除 picker 本身外，harness MUST **一次渲染一个变体、全尺寸、处于真实周边上下文**——一个 toast 需要身后有页面，一张卡片需要同级兄弟，一个按钮需要一张表单。并排缩略图会扭曲间距与尺度；NEVER 以邮票尺寸评审 UI。<br>切换是**瞬时**的——翻转是每会话 100+ 次的动作，按频率规则，变体切换**不配动画** |
| **5 · 验证与交接** | 跑起 harness。确认每个变体都能渲染、每个交互都有响应、控制台干净——在展示给用户前，MUST 自己翻完所有变体。若有浏览器工具可用，为每个变体截图。<br>然后呈现这一组并**停下——选择权属于用户**。<br>**完成判据：** 每个变体都能从 picker 到达且行为正确；无控制台错误；表格诚实说出每个变体的取舍 |
| **6 · 选中后提升** | 用户选中后：按项目既有约定（文件布局、命名、令牌用法）把该变体集成到它该在的地方，然后按硬规则 5 删除原型面。<br>若用户想要再来一轮：保留 harness，重跑 Phase 3，围绕他们被吸引的方向**重新分歧** |

### 呈现表格（Phase 5 MUST 输出）

| # | 变体 | 轴 | 何时它是正确选择 | 它的代价 |
| --- | --- | --- | --- | --- |
| 1 | Quiet | 极简动效，边框替代阴影 | 产品是每天使用的工具 | 最不令人难忘 |
| 2 | Editorial | 大字号，慷慨留白 | 这一刻配得上分量 | 吃掉纵向空间 |

以 picker 的运行位置（URL 或文件路径）与翻转按键收尾。

### 语气

诚实地推销每个变体——一行说它何时胜出，一行说它的代价。在表格里**NEVER 预先挑一个最爱**；若用户问你会选哪个，用根植于产品个性与使用频率的理由回答，而非仅凭美学。若两个变体在构建过程中趋同了，砍掉一个并说明：一个装着两个真正不同方向的 picker，胜过被凑数到三个的 picker。

---

## Part B · Picker 规格（逐字 · 唯一允许的改动已注明）

它是一个浮动于底部居中的深色药丸。深色玻璃在任何页面之上都成立——浅色或深色皆可——这正是它不做主题适配的原因。

### 标记

滑动高亮 span 在最前，每个变体一个按钮，一条发丝分隔线，然后是重播按钮（**仅当**至少一个变体有值得重触发的动效时）：

```html
<nav class="proto-picker" aria-label="Prototype variants">
  <span class="proto-picker-highlight" aria-hidden="true"></span>
  <button class="proto-picker-item" data-active aria-current="true">Quiet</button>
  <button class="proto-picker-item">Editorial</button>
  <button class="proto-picker-item">Playful</button>
  <span class="proto-picker-divider" aria-hidden="true"></span>
  <button class="proto-picker-item proto-picker-replay" aria-label="Replay animation (R)">↻</button>
</nav>
```

在框架中保留类名与结构，只改渲染语法。

### 样式

```css
.proto-picker {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2147483647;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(10, 10, 10, 0.82);
  -webkit-backdrop-filter: blur(12px) saturate(1.4);
  backdrop-filter: blur(12px) saturate(1.4);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.08) inset,
    0 8px 24px rgba(0, 0, 0, 0.24),
    0 2px 6px rgba(0, 0, 0, 0.12);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 13px;
  line-height: 1;
  -webkit-font-smoothing: antialiased;
  user-select: none;
  -webkit-user-select: none;
}

.proto-picker-highlight {
  position: absolute;
  top: 4px;
  left: 0;
  height: 28px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  will-change: transform;
}

/* 滑动只在首次绘制后启用（data-ready），因此加载过程不动画。 */
.proto-picker[data-ready] .proto-picker-highlight {
  transition:
    transform 250ms cubic-bezier(0.23, 1, 0.32, 1),
    width 250ms cubic-bezier(0.23, 1, 0.32, 1);
}

@media (prefers-reduced-motion: reduce) {
  .proto-picker[data-ready] .proto-picker-highlight { transition: none; }
}

.proto-picker-item {
  position: relative; /* 位于高亮之上 */
  display: flex;
  align-items: center;
  height: 28px;
  padding: 0 12px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: rgba(255, 255, 255, 0.55);
  font: inherit;
  cursor: pointer;
  transition: color 150ms ease-out;
}

.proto-picker-item:hover {
  color: rgba(255, 255, 255, 0.85);
}

.proto-picker-item:active {
  transform: scale(0.97);
}

.proto-picker-item:focus-visible {
  outline: 2px solid rgba(255, 255, 255, 0.4);
  outline-offset: 2px;
}

.proto-picker-item[data-active] {
  color: #fff;
}

.proto-picker-divider {
  width: 1px;
  height: 16px;
  margin: 0 4px;
  background: rgba(255, 255, 255, 0.12);
}

.proto-picker-replay {
  padding: 0 10px;
  font-size: 14px;
}

.proto-picker[data-position="top"] {
  bottom: auto;
  top: 24px;
}
```

### 规则

- **逐字。** 这些值就是规格。无项目字体、无品牌色、无主题切换、无额外阴影或边框。
- **高亮滑动；变体切换保持瞬时。** 激活药丸在按钮之间动画（250ms，强 ease-out），作为 picker 自身的空间反馈——但被预览的变体仍然**无过渡地**切换。`width` 过渡是对 transform/opacity 规则的一个刻意例外：该元素高 28px、绝对定位、无布局依赖，绘制成本可忽略。
- **唯一允许的改动：** 若某变体占据屏幕底部居中（toast 堆叠、bottom sheet、dock），设 `data-position="top"`，使 picker 永不遮挡作品。除此之外它 MAY NOT 移动或改变任何东西。
- **重播是有条件的。** 仅当至少一个变体有值得重触发的入场或状态动画时，才渲染重播按钮及其分隔线；纯静态比较用更短的药丸。

### 行为契约

契约固定，与 harness 如何渲染无关：

- 数字键 `1–N` 与 `←`/`→` 切换变体；`R` 重播。当焦点位于 input、textarea、select 或 contenteditable 中，或按住修饰键时，忽略按键事件。
- 点击某项即切到它；任意时刻**恰好一个**项带 `data-active` 与 `aria-current="true"`，高亮滑到它上面。
- 选中状态通过 URL 参数（`?v=2`）跨刷新保持，回退到变体 1。高亮的初始位置不带动画（`data-ready` 在首次绘制后加上）。
- 切换会重新挂载变体（因此入场动画会重跑）；重播键重新挂载但不切换。

### 参考接线

独立 HTML 分支逐字使用；在框架中保持同样行为但用地道写法表达（用 state 而非 `innerHTML`，用带 key 的重新挂载而非 `requestAnimationFrame`，用 refs + layout effect 做高亮测量）。

```js
// `variants` 是渲染函数数组，每个变体一个，按 picker 顺序。
const stage = document.getElementById('stage');
const picker = document.querySelector('.proto-picker');
const highlight = picker.querySelector('.proto-picker-highlight');
const items = [...picker.querySelectorAll('.proto-picker-item:not(.proto-picker-replay)')];
const replay = picker.querySelector('.proto-picker-replay');
let current = 0;

function moveHighlight() {
  const el = items[current];
  highlight.style.width = el.offsetWidth + 'px';
  highlight.style.transform = `translateX(${el.offsetLeft}px)`;
}

function mount(i) {
  stage.innerHTML = '';
  // 先清空，下一帧再渲染，让入场动画重跑。
  requestAnimationFrame(() => { stage.innerHTML = variants[i](); });
}

function setActive(i) {
  if (i < 0 || i >= variants.length) return;
  current = i;
  items.forEach((el, j) => {
    el.toggleAttribute('data-active', j === i);
    if (j === i) el.setAttribute('aria-current', 'true');
    else el.removeAttribute('aria-current');
  });
  moveHighlight();
  const url = new URL(location);
  url.searchParams.set('v', i + 1);
  history.replaceState(null, '', url);
  mount(i);
}

items.forEach((el, i) => el.addEventListener('click', () => setActive(i)));
replay?.addEventListener('click', () => mount(current));
window.addEventListener('resize', moveHighlight);

document.addEventListener('keydown', (e) => {
  if (/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.isContentEditable) return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const num = parseInt(e.key, 10);
  if (num >= 1 && num <= variants.length) setActive(num - 1);
  else if (e.key === 'ArrowRight') setActive((current + 1) % variants.length);
  else if (e.key === 'ArrowLeft') setActive((current - 1 + variants.length) % variants.length);
  else if (e.key === 'r' || e.key === 'R') mount(current);
});

setActive((parseInt(new URLSearchParams(location.search).get('v'), 10) || 1) - 1);
// 只在首次绘制后启用滑动，因此加载过程不动画。
requestAnimationFrame(() => requestAnimationFrame(() => picker.setAttribute('data-ready', '')));
```

### 调用变体

| 调用 | 行为 |
|---|---|
| `<描述>` | 完整流程：划范围 → 侦察 → 3 个变体 → picker → 等选择 |
| `<描述> x5` | 同上，但变体数为指定值（上限 5） |
| `riff <变体>` | 新一轮：保留 harness，围绕指定变体的方向生成一组新的分歧 |
| `keep <变体>` | 把该变体提升进代码库并删除原型面 |
| `keep <变体>, leave the picker` | 提升，但保留原型面 |
