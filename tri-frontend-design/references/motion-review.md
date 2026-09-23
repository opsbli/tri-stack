# 动效评审标准（motion-review.md）

> `motion` 模式 `action=review` 的判定方法论。**数值一律指针引用 `motion-standards.md`，NEVER 在本文件内联或近似。**
> 评审姿态：你是眼光苛刻的资深设计工程师。**默认挑刺，通过需要挣得。** 一个"能跑"但发沉、落点原点错、触发过频或掉帧的过渡，是 regression 而非 pass。
> 来源与归属：蒸馏自 emilkowalski/skills（MIT License, Copyright (c) 2026 Emil Kowalski），去产品化改写。
> grep 检索：`grep -n "标准\|升级触发\|补救\|Block\|Approve" references/motion-review.md`

---

## 一、十条不可协商标准

diff 中的每一个动效都按这十条度量。违反一条即一个 finding。

| # | 标准 | 判定口径 |
|---|---|---|
| 1 | **动效须有理由（Justified）** | 每个动效 MUST 能回答"为什么动"——空间一致性 / 状态指示 / 反馈 / 解释说明 / 防止突兀。**"看起来酷"出现在高频元素上是 block。** |
| 2 | **频率适配（Frequency-appropriate）** | 键盘触发与 100+次/天的动作**不动画**；数十次/天须减弱；偶发用标准；罕见/首次可 delight。（四档表见 `motion-standards.md` §1） |
| 3 | **响应性缓动（Responsive easing）** | 入场/出场用 `ease-out` 或强自定义曲线。**UI 上的 `ease-in` 是 block**——它延迟了用户注视最集中的那一刻。CSS 内置缓动太弱，应见到自定义 cubic-bezier。 |
| 4 | **UI 动效 <300ms** | 更慢的 UI 元素动效若无书面理由即是 finding。逐元素预算见 `motion-standards.md` §4。 |
| 5 | **原点与物理正确** | Popover/下拉/tooltip 从触发器缩放（`transform-origin`），而非中心。NEVER 从 `scale(0)` 起——用 `scale(0.9–0.97)` + opacity。（模态框豁免，保持居中） |
| 6 | **可中断性** | 被快速触发或手势驱动的动效（toast、开关、拖拽）MUST 可中断——CSS transition 或能从当前状态重定向的 spring，而非从零重启的 keyframes。 |
| 7 | **仅 GPU 属性** | 只动 `transform` 与 `opacity`。动 `width`/`height`/`margin`/`padding`/`top`/`left`（或负载下 Motion 的 `x`/`y`/`scale` 简写）即为性能 finding。 |
| 8 | **无障碍** | `prefers-reduced-motion` 被遵守（更轻柔而非为零——保留 opacity/颜色，去掉位移）。Hover 动效须门控于 `@media (hover: hover) and (pointer: fine)`。 |
| 9 | **非对称进出** | 主动动作（按压、长按、破坏性确认）动画更慢；系统响应要利落。按压-释放或长按交互上的对称时序是 finding。 |
| 10 | **内聚（Cohesion）** | 动效匹配组件个性与产品其余部分——玩趣的可更弹，仪表盘保持 crisp。个性错配，或该用轻微 blur 桥接却做出生硬交叉淡入，均是 finding。**拿不准动效是否感觉对时，最强的动作往往是删掉它。** |

---

## 二、强升级触发（见即重罚）

以下模式 MUST 一看到就 hard flag：

- `transition: all`（无边界属性动画）
- `scale(0)`，或纯淡入入场且无初始 transform
- UI 交互上的 `ease-in`；郑重动效上用弱内置缓动
- 键盘快捷键、命令面板开合、100+次/天动作上的动画
- UI 时长 > 300ms 且无说明理由
- 触发器锚定的 popover/下拉/tooltip 上用 `transform-origin: center`
- Toast、开关或任何被快速添加/触发的东西上用 keyframes
- 动画布局属性（`width`/`height`/`margin`/`padding`/`top`/`left`）
- 页面繁忙时运行的动效上使用 Motion 的 `x`/`y`/`scale` 简写
- 更新父元素 CSS 变量以驱动子元素 transform（样式重算风暴）
- 位移动效缺失 `prefers-reduced-motion` 处理
- 未门控的 `:hover` 动效
- 按压-释放或长按交互上的对称进出时序
- 本该 30–80ms 交错却一拥而上的入场

---

## 三、补救偏好层级（Remedial Preference Hierarchy）

提修复建议时，**优先靠前的动作**：

| 序 | 动作 | 适用 |
|---|---|---|
| 1 | **删掉动效** | 高频 / 无目的 / 键盘触发 |
| 2 | **减弱** | 缩短时长、缩小 transform、减少动画属性 |
| 3 | **修缓动** | `ease-in` → `ease-out` 或自定义曲线；用强 cubic-bezier |
| 4 | **修原点/物理性** | 纠正 `transform-origin`；`scale(0)` → `scale(0.95)` + opacity |
| 5 | **改为可中断** | keyframes → transitions；手势驱动改用 spring |
| 6 | **搬上 GPU** | 布局属性 → `transform`/`opacity`；简写 → 完整 `transform` 字符串；程序化 CSS 用 WAAPI |
| 7 | **非对称时序** | 主动阶段放慢，系统响应利落 |
| 8 | **打磨** | blur 遮罩交叉淡入、成组交错、`@starting-style` 入场、"活着"的元素用 spring |
| 9 | **无障碍与内聚** | 补 reduced-motion + hover 门控；调到匹配组件个性 |

---

## 四、输出格式（REQUIRED · 两部分，按序）

### Part 1 — Findings 表（必交）

**一张 markdown 表，一行一个问题。NEVER 写成 "Before:/After:" 列表。**

| Before | After | Why |
| --- | --- | --- |
| `transition: all 300ms` | `transition: transform 200ms ease-out` | 指明确切属性；`all` 会把非预期属性带到 GPU 之外 |
| `transform: scale(0)` | `transform: scale(0.95); opacity: 0` | 没有东西从虚无中出现——`scale(0)` 看起来像凭空冒出来 |
| `ease-in` on dropdown | `ease-out` + 自定义曲线 | `ease-in` 延迟了用户注视最集中的那一刻；感觉发沉 |
| `transform-origin: center` on popover | `var(--transform-origin)`（Base UI） | Popover 从触发器缩放而非中心（模态框豁免） |

### Part 2 — 裁决（必交）

按影响层级分组，最高层在前，空层省略：

1. **手感破坏型 regression** —— 发沉的缓动、凭空出现、高频/键盘动作上触发。
2. **错失的简化** —— 本该删除或大幅减弱的动效。
3. **性能** —— 非 GPU 属性、掉帧风险、样式重算风暴。
4. **可中断性与时序** —— 该用 transition/spring 处用了 keyframes；该非对称处用了对称。
5. **原点、物理性与内聚** —— 原点错误、个性错配、生硬交叉淡入。
6. **无障碍** —— reduced-motion 与 pointer/hover 门控。

以明确裁决收尾：

- **Block** —— 存在任一手感破坏型 regression、键盘/高频动作上的动画、UI 上的 `scale(0)`/`ease-in`，或有便捷 GPU 修复方案却用了非 GPU 动画。
- **Approve** —— 无手感破坏型 regression、无明显该删的动效、时长与缓动在界内、该处已处理可中断性、reduced-motion 已遵守。

---

## 五、评审准则

- 判定 MUST 具体并引用 `file:line`。
- 需要数值（曲线、时长、spring 配置）时，MUST 从 `motion-standards.md` 取**确切的那一个**，NEVER 近似。
- 预定动效优先 CSS transition / `@starting-style` / WAAPI；动态、可中断、手势驱动的用 JS/spring。
- 拿不准手感时，MUST 建议用慢放/逐帧复核，并在隔天用新鲜眼睛再看一遍，NEVER 猜。
- **本 skill 只判"动效与交互手感"。** 代码质量 / 安全 / 架构属 tri-review，MUST 转介，NEVER 越界。
