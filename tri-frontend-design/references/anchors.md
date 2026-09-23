# 八个风格锚点 · 全量令牌规格（anchors.md）

> 本文件是 `tri-frontend-design` 的**令牌单一事实源**。SKILL.md §3 仅作速查，运行时 MUST 读取本文件以精确匹配令牌。
> grep 检索：`grep -n "Swiss\|Industrial\|Brutalist\|Aurora\|Chaotic\|Retro-Futuristic\|Organic\|Lo-Fi" references/anchors.md`
> 每个锚点锁定具体的 CSS 令牌；渲染令牌 MUST 全部落在其允许范围内，否则该锚点"没守住"。
> 每个锚点附「动效基线」段，与 SKILL.md §7 映射表 MUST 一致；动效数值取自 `references/motion-standards.md`。

---

## 1. 瑞士风格（Swiss）

**Surface（表面）：** 纯白 `#FFFFFF` 或中性灰 `#F7F7F8`。
**Typography（字体）：** Akzidenz-Grotesk、Helvetica Neue 或 Söhne——展示体与正文统一为一种无衬线家族。
**Accent（点缀色）：** 瑞士红 `#E4002B`、国际橙 `#FF4F00` 或克莱因蓝（Yves Klein Blue）`#002FA7`——只取其一，刻意使用。
**Structure（结构）：** 可见的网格线或 1px 发丝线。左对齐排版；非对称平衡。将数字作为构图元素（日期、页码、页标记用紧凑无衬线体排印）。
**Motion baseline（动效基线）：** 克制：`ease-out`（取自 `motion-standards.md`）150–200ms，无弹簧、无 bounce，仅 `opacity` / `transform`，无霓虹/辉光动画。
**Breaks if（崩坏条件）：** 出现暖色纸张、衬线展示体、颗粒质感或居中排版。

---

## 2. 工业风（Industrial）

**Surface（表面）：** 纯黑 `#000000` 或暖黑 `#0B0C0A`。
**Typography（字体）：** IBM Plex Mono、JetBrains Mono 或 Berkeley Mono——展示体与正文皆为等宽体。
**Signal color（信号色）：** 一种语义色——绿 `#00E676`、红 `#FF3B30`、琥珀 `#FFB800` 或酸性青柠 `#C6FF4A`。
**Structure（结构）：** 扁平；用 1px 边框取代阴影。表格数字通过 `font-variant-numeric: tabular-nums` 实现。
**Motion baseline（动效基线）：** 近乎无动效：状态切换瞬时；仅保留 100–160ms 按压反馈（`scale(0.97)`），终端界面不该有花活，无入场/退场动画。
**Breaks if（崩坏条件）：** 出现衬线字体、比例字体、暖色纸张、任何颗粒、装饰性阴影或圆角。

---

## 3. 粗野主义（Brutalist）

**Surface（表面）：** 纯原色或反原色——`#FF0000`、`#0000FF`、`#FFFF00`、`#000000`、`#FFFFFF`。选取 2–3 种，等量竞争。
**Typography（字体）：** 仅用系统字体——Times New Roman、Helvetica、Courier、Arial、system-ui。刻意混排不同字族。
**Shadows（阴影）：** 硬边缘偏移、无模糊——`box-shadow: 8px 8px 0 #000`。
**Controls（控件）：** 原生浏览器——未加样式的 `<button>`、默认 `<select>`、保持蓝色的下划线蓝色链接。边距被压到极限；文字铺满到边缘。
**Motion baseline（动效基线）：** 反潮流：`steps()` 阶跃或零过渡硬切；硬边偏移阴影 `8px 8px 0 #000` 不参与动画；无弹簧、无缓动。
**Breaks if（崩坏条件）：** 出现网络字体、超出纯原色的微调色值、柔和阴影、圆角或居中布局。

---

## 4. 极光极繁主义（Aurora Maximalism）

**Surface（表面）：** 暗色高饱和渐变——`linear-gradient` 或 `conic-gradient` 穿越 紫 `#5D34D0` → 品红 `#FF006E` → 青 `#00F0FF`，或 `#3B82F6 → #A855F7 → #EC4899`。
**Typography（字体）：** Inter Variable、PP Neue Machina 或 Sharp Grotesk 用于超大号展示字（15–25 vw）。
**Texture（质感）：** 以网格渐变（mesh gradient）作为主表面特征；点缀色上的霓虹 `text-shadow` 辉光（`0 0 20px <accent>`）。
**Motion（动效）：** 弹簧物理编排，滚动联动视差。
**Motion baseline（动效基线）：** 弹簧编排 `bounce 0.2`（取自 `motion-standards.md §4`），滚动联动视差，霓虹辉光呼吸；可多轨不同步但仍守 GPU 属性与 `prefers-reduced-motion`。
**Breaks if（崩坏条件）：** 出现纯色背景、暖色纸张、克制感，或以发丝线作为主要结构。

---

## 5. 混沌极繁主义（Chaotic Maximalism）

**Surface（表面）：** 冲突的色板——在同一构图中同时出现粉彩 *和* 霓虹。亮粉 `#FF71CE` + 酸性黄 `#DFFF00` + 青 `#00FFFF` + 任意第三种。
**Typography（字体）：** 刻意让不同字族碰撞——同一页面上 3 种以上来自不同语域的字族。
**Texture（质感）：** 每个表面都有图案（波浪线、圆点、锯齿、棋盘格——SVG 或 `repeating-linear-gradient`）。超大号展示字撞击在繁忙的底纹之上。
**Motion baseline（动效基线）：** 允许违规美学：多轨不同步动效、夸张错位；但仍守 GPU 属性白名单与 `prefers-reduced-motion` 降级，不得动 `width`/`height` 触发布局抖动。
**Breaks if（崩坏条件）：** 出现协调的色板、单一字族、作为结构元素的留白，或 60/30/10 主从占比。

---

## 6. 复古未来主义（Retro-Futuristic）

**Surface（表面）：** 纯黑 `#0A0014` 或深海军黑。
**Typography（字体）：** 年代特定——VT323（CRT）、Orbitron（合成波 synthwave）、Space Mono（赛博朋克 cyberpunk）、Monoton（迈阿密霓虹）、Press Start 2P（街机 arcade）、IBM Plex Mono（终端 terminal）。
**Accent（点缀色）：** 霓虹双色——品红 `#FF006E` + 青 `#00FFFF`（合成波）或磷光绿 `#00FF41` + 琥珀 `#FFB000`（终端）。
**Texture（质感）：** 通过 `::before` 的 `repeating-linear-gradient` 叠加层实现 CRT 扫描线，或色差（chromatic aberration，`text-shadow: 2px 0 #FF0000, -2px 0 #00FFFF`），或两者兼具。辉光须贯彻始终。
**Motion baseline（动效基线）：** CRT 抖动 / 扫描线循环 + 阶跃式打字机，`linear` 而非 `ease`；辉光贯穿，但 `prefers-reduced-motion` 下退化为瞬时显隐。
**Breaks if（崩坏条件）：** 出现扁平感、现代无衬线体（Inter、Söhne）、纸质表面，或质感的缺失。

---

## 7. 有机风（Organic）

**Surface（表面）：** 大地色系——鼠尾草绿 `#8B9D83`、陶土 `#B08B6E`、赤陶 `#C66B3D`、赭石 `#C08E3A`、苔绿 `#606C38`。需要浅色表面时：沙色 `#E8DCC7` 或燕麦色 `#D4B895`。**绝不用奶油色 `#F0-F8` 暖纸范围。**
**Typography（字体）：** 人文衬线体（Freight、Caslon、Fraunces——Fraunces 仅限本锚点使用）或暖调几何无衬线体（Greycliff、Epilogue、Recoleta）。
**Structure（结构）：** 圆角 16–32px。
**Texture（质感）：** 通过 SVG feTurbulence 实现 1–3% 的颗粒。
**Motion（动效）：** 轻柔缓动 300–500ms，主视觉元素上的"呼吸"动画。
**Motion baseline（动效基线）：** 300–500ms 轻柔 `ease-in-out`（取自 `motion-standards.md`），主视觉"呼吸"循环；无硬切、无 bounce。
**Breaks if（崩坏条件）：** 出现奶油色背景（暖调 `#F0+`）、冷灰、纯白、纯黑，或硬边矩形。

---

## 8. 低保真（Lo-Fi）

**Surface（表面）：** 纸黄 `#E8E0C0` 或 `#EDE4CF`——比奶油色更饱和。
**Typography（字体）：** 同一页面混排系统字体（Times + Helvetica + Courier 刻意碰撞）。
**Structure（结构）：** 旋转元素（通过 `transform: rotate` 偏离网格 2–8°）。
**Texture（质感）：** 图像上的半调网点过渡（SVG 图案或 `radial-gradient` 平铺）；Risograph 套印错位（通过 `text-shadow: 3px 0 #FF006E, -3px 0 #00FFCC` 实现 2–4px 的 RGB 通道偏移）。SVG 订书钉、胶带、撕边元素。
**Motion baseline（动效基线）：** 手作抖动：小角度 `rotate` 微扰、`steps()` 半调过渡；拒绝"平滑动效"——抖动即风格，但 `prefers-reduced-motion` 下退化为瞬时切换。
**Breaks if（崩坏条件）：** 出现精确感、单一字族、平滑动效、对齐网格的矩形，或奶油色（该表面特指更饱和的纸黄）。

---

## 锚点选择决策要点

- **一个简报 = 一个锚点**，MUST 精确匹配其全部令牌（含动效基线），禁止杂交。
- **偏向出人意料**：在"稳妥搭配"与"有辨识度的搭配"之间，优先后者（如工业风花店、瑞士风朋克厂牌）。
- **令牌漂移即失败**：任何不在锚点允许范围内的色值/字体/结构/质感 = 该锚点没守住，MUST 回炉。
- **内容独立纪律**：令牌保真不替内容背书，§2 五项禁止（编造/填充/主题化替换/字形图标/AI 套话）同样 MUST 遵守。
