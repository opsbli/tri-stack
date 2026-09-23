---
name: tri-frontend-design
slug: tri-frontend-design
version: 1.1.1
displayName: 前端设计
description: 前端设计技能——为构建或重塑前端提供"风格锚点"驱动的可视化方向（静态视觉层），并补齐"时间维度 + 交互物理层"：动效引擎（频率闸门/缓动/弹簧/可中断性/GPU 属性/性能/a11y）、动效评审与全库审计、多变体探索。通过配色/字体/结构/质感锁定具体 CSS 令牌，并要求屏幕内容命名真实信息而非编造。支持独立安装，含上游依赖检测三态逻辑（快照/引导/降级）。当用户要"做/改一个前端界面""设计一套有风格的 UI""给界面加动效/评审动效""想看几个方向再选"时激活。
summary: 把"前端设计"变成可由 AI 稳定执行的可视化方向引擎——八个风格锚点各自锁定 CSS 令牌（空间轴），加上由锚点自动推导的动效基线（时间轴 + 物理轴），配合"内容不是设计"纪律与发布前自检，交付高保真、动起来不浮、不套话、不编造的前端。
tags: [frontend, design, css, aesthetic, ui, anchor, token, typography, motion, animation, review, variants, accessibility]
license: MIT
---

# 前端设计技能（tri-frontend-design）

> 八个风格锚点，每个都是一片独特的美学疆域，锁定到具体的 CSS 令牌。每个设计简报选取一个锚点，并精确匹配其令牌。

> **追求出人意料。忠于锚点。内容有节制。动效不浮。绝不落入默认。**

---

## 强制执行契约（Execution Contract · 最高优先级）

> 本节定义本 skill「被激活后必须做什么」，优先级高于通用默认行为。

0. **版本检查前置硬门（第零步）**：MUST 先运行 `scripts/check_update.py --slug tri-frontend-design --json`，按 `state` 处置（A/B/C/D 一律放行，BLOCK 绝对禁止执行）；四态判定与升级流程细则唯一真源为 `references/version-check-spec.md`。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。
1. **强制前置**：激活后 MUST 先走 §上游依赖检测 判定模式，再执行核心设计流程；NEVER 跳过依赖检测静默执行。
2. **单锚点铁律**：MUST 为每个设计简报选定**且仅选定一个**风格锚点，并精确匹配其全部令牌；杂交（"瑞士风带粗野边缘"）是范畴错误，MUST 拒绝。
3. **令牌保真**：渲染出的 CSS MUST 落在所选锚点允许的令牌范围内（色值/字体/结构/质感）；出现锚点不允许的令牌即"锚点没守住"，MUST 回炉修正。
4. **内容纪律**：屏幕上每个字符串、数字、标签 MUST 要么指称真实产品信息，要么是"清楚自己是什么"的创作内容；MUST NOT 编造数据、堆填充标签、以主题化措辞替换标准 UI 文案、用 Unicode 字形当图标、写 AI 腔套话。
5. **最小化原则**：MUST 只交付 `输入契约` 范围内的设计产物，NEVER 自行扩大范围；如需增补（如新增锚点变体），MUST 向用户说明并确认。
6. **自检句**：每次执行前 MUST 声明「本次模式=<design|motion|variants>，触发源=<用户直接|委派>，锚点=<已选X|待选>，下游=<否>，版本门=<A/B/C/D>」；与已确认需求冲突时 MUST 停止并纠正。
7. **频率硬门**：为任何 UI 元素添加动效前，MUST 先按 `references/motion-standards.md §1` 判定使用频率；100+ 次/天或键盘触发类动作（命令面板开合、核心导航、快捷键）MUST NOT 动画；频率判定未完成 NEVER 进入曲线/时长选择。
8. **动效令牌真源**：所有缓动曲线、时长预算、弹簧参数、阈值与 GPU 属性白名单 MUST 取自 `references/motion-standards.md`，原样复制，NEVER 近似或臆造；`cubic-bezier(0.23, 1, 0.32, 1)` 写成 `0.25` 即视为缺陷。
9. **a11y 随动效同交**：任何动效 MUST 同步交付 `prefers-reduced-motion` 降级与 hover/focus 门控（见 `motion-standards.md §8`）；a11y 不得作为后续补丁后补，缺席即视为动效未交付。

## 触发时机

| 触发源 | 激活条件 | 模式 |
|---|---|---|
| 用户直接请求（设计） | "帮我做一个前端页面""把这个界面改成 X 风格""设计一套有辨识度的 UI" | `design` |
| 用户直接请求（动效） | "给这个按钮加动效""评审一下我的界面动效""把整个站点的动效审计一遍""哪些地方该动、哪些不该" | `motion` |
| 用户直接请求（变体） | "我想看几个方向再选""出 3 个瑞士风 dashboard 变体" | `variants` |
| 其它 skill 委派 | tri-content / tri-coding 在产出前端界面时需先定可视化方向 | `design` |

> 本 skill 是**独立工具 skill**，不注册为 tri-intent 下游路由项；用户直接调用，不经意图识别。`motion` / `variants` 模式也由用户显式触发，模型不自主激活。

## 上游依赖检测（独立安装 · 三态逻辑）

> 本 skill 可独立安装。激活时据上游可用性选择模式：

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 快照模式** | 检测到可用 tri-intent 快照（`.tribro/LATEST.md` 指针且 ≤30 分钟） | 读取快照 §三 提取上下文（D1 任务领域 / D4 输出期望）增强设计语境感知 |
| **B · 引导安装** | 未检测到 tri-intent 且用户希望获得完整链路 | 提示安装 tri-intent 以获得意图识别→澄清→执行工作流 |
| **C · 降级模式** | 用户明确拒绝安装上游 / 无快照 | 自构造等价输入（任务领域=前端设计，目标读者=未指定），声明降级精度低后按核心流程执行 |

## 输入契约

| 字段 | 用途 | 默认 |
|---|---|---|
| `brief` | 设计简报：用途、受众、领域、内容密度 | 用户描述 |
| `anchor`（可选） | 用户指定锚点；未指定则由 skill 推荐 | 待选 |
| `differentiator`（可选） | 用户指定的差异化动作 | 由 skill 提出 |
| `real_content` | 屏幕需呈现的真实信息（文案/数据/标签） | 用户提供或留空 |
| `target_lang` | 界面文案语言 | zh-CN |
| `mode` | 执行模式：`design`（默认）/ `motion` / `variants` | `design` |
| `action`（仅 `motion`） | 子动作：`build`（写实现）/ `review`（评审既有）/ `find`（找机会）/ `audit`（全库审计 + 自包含 plan） | `build` |
| `motion_scope`（仅 `motion`） | 作用范围：单组件 / 单页 / 全站 | 由 skill 与用户确认 |
| `effort`（仅 `motion.audit` 可选） | 审计深度：`quick` / `standard` / `deep` | `standard` |
| `variant_count`（仅 `variants`） | 产出变体数量 | 3（范围 3–5） |

> 若关键信息（用途/受众/真实内容）缺失，MUST 先向用户澄清再执行，NEVER 用编造内容填充。

## 职责边界

本 skill 显式「只做一件事 + 以下不是它的事」：

- **本 skill 负责**：前端视觉方向（锚点+令牌+内容纪律）+ 动效方向引擎（频率/曲线/弹簧/可中断/a11y）+ 动效评审与全库审计 + 多变体探索。
- **以下不是它的事（显式转介）**：
  - **库选型**（21 库对照、Framer Motion vs WAAPI 取舍）→ 委派 `tri-coding`（tech-skills/react.md）；本 skill 只给"目的→工具"判定，不下工程依赖决策。
  - **RN/Expo 动效、SwiftUI 动效** → 委派 `tri-coding`（tech-skills/react-native.md / swiftui.md）。
  - **代码质量 / 安全 / 架构审查** → 委派 `tri-review`；本 skill 只判"动效感觉对不对"（设计域），不判代码工程质量。
  - **HTML/CSS 工程渲染实现** → 委派 `tri-html`；本 skill 产出方向与令牌规格，不写完整工程代码。
  - **意图识别** → `tri-intent`；本 skill 不认领任何 L2/L3 编码。
- **MECE**：本 skill 不认领 tri-intent 下游路由，作为独立工具存在，不破坏家族下游 MECE 划分。
- **不触发场景（Not-Trigger）**：本 skill 不接手「完整工程代码 / HTML/CSS 渲染实现」（转 tri-html）；不接手「库选型工程决策 / 代码质量审查」（属 tri-coding / tri-review，本 skill 只给「目的→工具」方向判定）；不接手「识别用户意图」（由用户显式触发，不经 tri-intent 路由）。

---

## 知识装配顺序（硬约束 25 · references ≥ 3 必读）

> 不同模式按需加载，节省 token；所有精确数值 MUST 取自对应 references，NEVER 近似。

| 加载层 | 文件 | 何时装 | 关键内容 grep |
|---|---|---|---|
| L0 令牌 | `references/anchors.md` | 所有模式 | `grep -n "Swiss\|Industrial\|Brutalist\|Aurora\|Chaotic\|Retro-Futuristic\|Organic\|Lo-Fi" references/anchors.md` |
| L1 动效数值 | `references/motion-standards.md` | `motion` 模式 | `grep -n "频率\|cubic-bezier\|spring\|scale(\|0.11\|reduced-motion\|GPU" references/motion-standards.md` |
| L2 配方 | `references/motion-recipes.md` | `motion.build` | `grep -n "配方\|WAAPI\|transition\|@starting-style" references/motion-recipes.md` |
| L3 评审 | `references/motion-review.md` | `motion.review` | `grep -n "不可协商\|Block\|Approve\|补救\|Before-After" references/motion-review.md` |
| L4 物理层 | `references/motion-physics.md` | `motion` 需深度时 | `grep -n "弹簧\|速度交接\|动量\|橡皮筋\|材质\|排版光学" references/motion-physics.md` |
| L5 审计计划 | `references/motion-plan-template.md` | `motion.audit` | `grep -n "自包含\|severity\|plans/" references/motion-plan-template.md` |
| L6 变体 | `references/variants-picker.md` | `variants` 模式 | `grep -n "分歧\|picker\|harness\|权衡" references/variants-picker.md` |
| L7 术语 | `references/motion-vocabulary.md` | `motion` 需术语反查时 | `grep -n "术语\|easing\|spring\|stagger" references/motion-vocabulary.md` |

> 去重规则：数值仅存于 `motion-standards.md`（单一真源）；`motion-recipes.md` 引用数值而 NEVER 重定义；`motion-review.md` 只留评审方法论，数值指针回 L1。覆盖优先级：L1 数值 > SKILL.md 流程描述 > 任何口头近似。

---

## 前端设计核心能力

> 核心理念：**设计不是逐字映射——风格锚点传达方向，令牌保信退守，内容命名真实，质量自检兜底。**

### 1. 工作方法（五步序列 · `design` 模式）

在编写任何代码之前，MUST 按以下顺序执行：

1. **情境（Context）**——明确用途、受众、领域、内容密度。用一句话陈述问题。
2. **锚点（Anchor）**——选取一个，偏向出人意料。瑞士风格的朋克唱片厂牌、工业风的花店、粗野主义的奢华手表制造商、极光风格的报税应用、混沌风格的律所、复古未来主义的婚礼摄影师、有机风的交易终端、低保真的豪华酒店——每一个都比"稳妥"的同款更有辨识度。
3. **差异化点（Differentiator）**——定义一个令人印象深刻的锚点内部动作：一个标志性交互、一个排版手势、一个布局母题，或一种材质处理。一句话。可被描述。在渲染输出中可见。
4. **系统（System）**——精确匹配所选锚点的令牌。选了瑞士风格，就意味着白底 + 无衬线 + 网格。
5. **实现（Implementation）**——先勾勒结构，再着手构建。屏幕内容需遵循 §2 纪律创作。

**彻底投入于一个锚点。** 混合杂交（"带粗野主义边缘的瑞士风"）是一种范畴错误——每种风格在构造上本就相互排斥。

### 2. 内容不是设计

设计是视觉层面的——配色、字体、结构、质感。**内容——屏幕上每一个字符串、数字与标签——是单独创作的，自有其准则。** 令牌保真并不能为内容垃圾（content slop）开脱。

**规则**：屏幕上的每个字符串，要么指称来自产品的真实信息，要么就是"清楚自己是什么"的创作内容。所禁止的，是让内容伪装成它本不是的东西。

**五项禁止（Forbidden）：**

- **冒充真实数据的捏造**——虚构的会话角色、伪造的遥测数据。若某个位置没有真实内容，就留空——不要为了显得"有内容"而编造。
- **填充标签**——无人要求的等宽大写副标题、以 `//` 开头假装是代码注释的导语。若删掉某字符串后信息毫无损失，那它就是填充。
- **以主题化措辞替换标准 UI 文案**——用 `Authenticate Session` 取代 `Next`。标准动作就用标准文案。
- **用 Unicode 字形充当图标替身**——`▣ Dashboard`、`◊ Market Navigator`。要么用真正的图标集，要么什么都别用。
- **AI 腔套话（AI-slop register）**——矫情副文案、合成科幻感状态条、伪装成结构元素的装饰性点缀。要在你自己的产出中识别出它，赶在审阅者之前把它砍掉。

### 3. 八个风格锚点

每个锚点都锁定特定的 CSS 令牌。选定锚点，即承诺遵循这些令牌。若渲染输出偏离了它们，说明该锚点没有"守住"。

**速查表：**

| 锚点 | 一句话令牌 |
|---|---|
| **瑞士风格（Swiss）** | 纯白 + Akzidenz/Helvetica/Söhne 无衬线 + 瑞士红/国际橙点缀 + 可见网格 |
| **工业风（Industrial）** | 纯黑 + 全文等宽体（IBM Plex Mono 等）+ 一种语义信号色 + 扁平 |
| **粗野主义（Brutalist）** | 纯原色 + 系统字体 + 硬边缘偏移阴影 `8px 8px 0 #000` + 原生控件 |
| **极光极繁主义（Aurora Maximalism）** | 暗色高饱和渐变 + Inter/PP Neue Machina + 网格渐变 + 霓虹辉光 |
| **混沌极繁主义（Chaotic Maximalism）** | 冲突粉彩+霓虹 + 混排字体 + 满屏图案 + 超大展示字 |
| **复古未来主义（Retro-Futuristic）** | 纯黑 + 年代字体（VT323/Orbitron 等）+ CRT 扫描线/色差 |
| **有机风（Organic）** | 大地色系 + 人文衬线/暖几何无衬线 + 圆角 + 细微颗粒 |
| **低保真（Lo-Fi）** | 纸黄 + 混排系统字体 + 旋转元素 + 半调网点 + 套印错位 |

> **全量令牌规格**（每个锚点的 Surface / Typography / Accent / Structure / Breaks if / **Motion baseline**）见 `references/anchors.md`（单一事实源）。运行时 MUST 读取该文件以精确匹配令牌与动效基线。

### 4. 交付物（`design` 模式）

每次实现都应交付：

- **明确的导向（Stated direction）**——在代码之前，用设计师的口吻写一段简短前言：所选锚点、为何选这个搭配而非稳妥的那个、差异化点，以及从锚点提取的关键配色/字体/质感选择。
- **令牌保真（Token fidelity）**——渲染出的 CSS 与锚点令牌精确匹配。
- **内容节制（Content discipline）**——屏幕上的每个字符串、数字与标签，要么指称真实信息，要么是"清楚自己是什么"的创作内容。
- **差异化点可见（Differentiator visible）**——那一个令人印象深刻的动作要落实在渲染输出中。
- `motion` / `variants` 模式的额外产物见 §交付产物。

### 5. 发布前自检（`design` 模式）

- **出人意料的搭配（Unexpected pairing）**——是否追求了创意张力，还是默认落回了稳妥搭配？
- **令牌保真（Token fidelity）**——每个渲染出的令牌是否都落在锚点允许的范围内？
- **内容节制（Content discipline）**——每个标签都指称真实信息；标准动作用标准 UI 文案；无编造、无填充、无字形图标、无 AI 套话。
- **差异化点可见（Differentiator visible）**——那个标志动作是否真的被渲染出来了？
- **抗杂交（Hybrid resistance）**——是否守住了一个锚点，还是漂移成了"带粗野主义边缘的瑞士风"？
- **动效不浮**（`motion` 模式追加）——动效是否过了频率门（§6 步骤1）？曲线/时长是否取自 `motion-standards.md`？`prefers-reduced-motion` 降级是否同交（契约⑨）？

---

### 6. 动效方向引擎（`motion` 模式核心）

> 把"这个界面用什么感觉"变成可由 AI 稳定执行的七步序列。所有数值 MUST 取自 `references/motion-standards.md`（契约⑧）。

1. **该不该动（频率门 · 契约⑦）**——先按 `motion-standards.md §1` 判定使用频率：100+ 次/天或键盘触发动作 MUST NOT 动画；同类动效在不同频率下可对可错，判断 MUST 从频率起。
2. **目的（六选一）**——Feedback / Spatial consistency / State indication / 防止突兀 / Explanation（仅营销页/引导）。MUST 能指名，指不出就不动。
3. **工具（最便宜能用的）**——首选原生 CSS `transition` / `@starting-style` / `clip-path` / `backdrop-filter`；编程控制用 WAAPI（`element.animate()`）；动态/手势用 Motion / Pointer Events。不为一个 fade 装动效库。
4. **属性（GPU 白名单）**——只动 `transform` / `opacity` / `clip-path` / `backdrop-filter`（合成层，不触发布局）；`width` / `height` / `top` / `left` / `margin` MUST NOT 作动画属性（触发布局抖动）。
5. **曲线 / 弹簧**——`ease-out` `cubic-bezier(0.23, 1, 0.32, 1)`、`ease-in-out` `cubic-bezier(0.77, 0, 0.175, 1)`、`ease-drawer` `cubic-bezier(0.32, 0.72, 0, 1)`；弹簧参数见 `motion-standards.md §4`；`scale(0)` 弹出 MUST NOT 用，按压反馈 `scale(0.97)`。
6. **可中断与退出**——优先 `transition` 而非 `keyframes`（可被新状态打断）；弹簧天生可中断且携带速度；任何动效 MUST 可干净退出。
7. **a11y 同交（契约⑨）**——`prefers-reduced-motion` 下降级为瞬时切换/位移保留；hover 动效 MUST 配 focus 等价态。缺席即视为未交付。

> 子动作路由：`build`→§4 配方（`motion-recipes.md`）；`review`→`motion-review.md` 十条标准 + Block/Approve；`find`→四问闸门 + **强制输出被否决候选**（克制机制）；`audit`→四阶段 + 自包含 plan（`motion-plan-template.md`，产出 `plans/NNN-*.md`）。

### 7. 锚点↔动效基线映射（由锚点自动推导动效）

> 本表是整合后的独有能力：动效的"个性（Cohesion）"恰好等于锚点。选定锚点即锁定下列动效基线，无需用户另行指定。

| 锚点 | 动效基线（Motion baseline） |
|---|---|
| 瑞士风格 | 克制：`ease-out` 150–200ms，无弹簧、无 bounce，纯 opacity/transform |
| 工业风 | 近乎无动效：状态切换瞬时，仅保留 100–160ms 按压反馈（终端界面不该有花活） |
| 粗野主义 | 反潮流：`steps()` 阶跃或零过渡硬切；硬边阴影不参与动画 |
| 极光极繁 | 弹簧编排 `bounce 0.2`，滚动联动视差，霓虹辉光呼吸 |
| 混沌极繁 | 允许违规美学：多轨不同步动效，但仍守 GPU 属性与 reduced-motion |
| 复古未来 | CRT 抖动/扫描线循环 + 阶跃式打字机，`linear` 而非 `ease` |
| 有机风 | 300–500ms 轻柔 `ease-in-out`，主视觉"呼吸"循环 |
| 低保真 | 手作抖动：小角度 `rotate` 微扰，`steps()` 半调过渡 |

> 八锚点的逐锚点 Motion baseline 细则（含触发条件与禁忌）已写入 `references/anchors.md` 各锚点段，本表与之 MUST 一致。

### 8. 多变体探索（`variants` 模式）

> 用户"想看几个方向再选"时使用。**分歧轴必须锁定在锚点内部**，NEVER 跨锚点混搭（单锚点铁律不破）。

- **分歧轴要求**：在已定锚点内，沿以下轴产生**真正分歧**的变体——布局母题 / 内容密度 / 交互模型 / 动效叙事。变体间 MUST 有可感知差异，而非同一稿的微调。
- **picker 是 chrome 不是选手**：`variants-picker.md` 规定逐字 picker 规格（含权衡表模板），picker 只负责呈现与收集选择，不参与设计决策。
- **六阶段流程**：① 锁定锚点 ② 定分歧轴 ③ 生成 3–5 变体 ④ 给每个变体一句话定位 + 取舍说明 ⑤ 产出 picker harness + 权衡表 ⑥ 用户选定一版后转 `design`/`motion` 精修。
- 指针：`references/variants-picker.md`（多变体方法论 + Picker 逐字规格 + 六阶段流程 + 单锚点铁律关系）。

---

### 可扩展性

1. **新增视觉锚点 / 令牌预设**：在 `references/` 追加预设条目（锚点 / 色板 / 字阶），多变体探索自动纳入
2. **新增动效预设**：在动效方向引擎追加速度曲线 / 弹簧参数预设，评审基线自动适用
3. **新增审计规则**：在动效评审与全库审计追加规则行，判定逻辑零改动

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级，为执行流程**第零步**。
> **细则唯一真源**：`references/version-check-spec.md`。**可执行实现**：本 skill 自带 `scripts/check_update.py`（与全家族同源一致，按 `--slug` 自动适配）。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

**执行方式（MUST）**：任一执行入口启动后、核心执行前，运行
```bash
python scripts/check_update.py --slug tri-frontend-design --json
```
解析 `state`：A/B/C/D → 一律放行进入后续阶段；BLOCK → 绝对禁止执行并输出恢复指引。退出码 `<20` 放行，`>=20` 阻断；脚本自身异常兜底降级放行，NEVER 因版本门故障阻断启动。

## 处理流程

```
用户需求 / 委派
   │
   ▼
版本检查（第零步：scripts/check_update.py）
   │ 放行
   ▼
上游依赖检测（A/B/C 模式）
   │
   ▼
┌────────────── 按 mode 分支 ──────────────┐
│ design（默认）：                           │
│   ① 情境 → ② 锚点 → ③ 差异化点 →          │
│   ④ 系统（匹配令牌）→ ⑤ 实现              │
│   → 内容纪律审查（§2）→ 交付物（§4）→ 自检（§5）│
│ motion：                                   │
│   ⑥ 动效引擎七步（§6）→ 锚点↔基线（§7）    │
│   → 子动作 build/review/find/audit         │
│   → 交付物（§交付产物）                    │
│ variants：                                 │
│   ⑧ 多变体六阶段（§8）→ picker harness     │
│   → 用户选定 → 转 design/motion 精修       │
└───────────────────────────────────────────┘
   │
   ▼
完成判据外化（§完成判据）→ 交付
```

**完成判据（外化）**：`design` 模式当且仅当 §5 发布前自检六项全部「过」且 §4 交付物四项齐备；`motion` 模式当且仅当动效过频率门（契约⑦）、数值取自真源（契约⑧）、a11y 同交（契约⑨）、评审裁决明确（Block/Approve）；`variants` 模式当且仅当产出 ≥3 个锚点内分歧变体 + picker harness + 用户已选定。任一项不过 MUST 回炉修正，NEVER 以模型自述「完成」替代上述判定。

## 交付产物

| 模式 | 产物 | 内容 | 适用 |
|---|---|---|---|
| `design` | 设计方向说明 | 锚点选择 + 理由 + 差异化点 + 关键令牌提取 | 每次 |
| `design` | 令牌规格 | 从 `references/anchors.md` 提取的所选锚点 CSS 令牌清单 | 每次 |
| `design` | 内容纪律清单 | 屏幕字符串/数据/标签的真实信息核对 | 含 UI 时 |
| `design` | 自检报告 | §5 六项逐条判定（过/不过 + 证据） | 每次 |
| `motion.build` | 动效实现 | 频率判定 + 目的 + 工具 + 属性 + 曲线/弹簧 + a11y 降级代码 | 写实现时 |
| `motion.review` | 评审报告 | Before-After-Why 表 + 十条标准逐条 + Block/Approve 裁决 | 评审既有时 |
| `motion.find` | 机会表 + 否决表 | 该动/不该动清单 + **强制输出被否决候选及理由** | 找机会时 |
| `motion.audit` | 分级发现表 + `plans/NNN-*.md` | 全库审计四阶段 + 自包含改进计划 | 全库审计时 |
| `variants` | 变体集 + picker harness | 3–5 分歧变体 + 逐字 picker + 权衡表 | 要多方案时 |

> 产物默认以对话回应交付；若用户显式指定目标文件/目录，写用户指定路径；`motion.audit` 计划落盘 `plans/`。

## 质量标准

| 维度 | 标准 | 验证方式 |
|---|---|---|
| 锚点保真 | 渲染令牌全部落在所选锚点允许范围，无杂交 | 比对 `references/anchors.md` |
| 内容真实 | 无编造数据/填充标签/主题化替换/字形图标/AI 套话 | §2 五项逐条核对 |
| 差异化可见 | 标志动作落实在输出中 | 渲染产物检查 |
| 出人意料 | 非稳妥默认搭配，有创意张力 | §5 第一项 |
| 最小化 | 仅交付约定范围内的产物 | 范围比对 |
| 频率适配 | 100+ 次/天 / 键盘触发动作无动画；动效先过频率门 | 契约⑦ + `motion-standards.md §1` |
| 曲线合规 | 缓动/时长/弹簧取自真源，无近似 | 契约⑧ + grep `motion-standards.md` |
| GPU 属性 | 仅动 transform/opacity/clip-path/backdrop-filter | 契约⑧ 属性白名单 |
| a11y 门 | `prefers-reduced-motion` + hover/focus 同交 | 契约⑨ + `motion-standards.md §8` |
| 变体分歧度 | variants 变体在锚点内真正分歧，未跨锚点混搭 | §8 分歧轴 + 单锚点铁律 |

## 落盘规则

> 本 skill 自身为生成物，落盘于 `.tribro/skills/tri-frontend-design/`（用户指定位置）；NEVER 生成 `LICENSE` 或 `.gitignore`（许可证仅由 frontmatter `license: MIT` 声明）。
> 蒸馏自 emilkowalski/skills（MIT License, Copyright (c) 2026 Emil Kowalski）的动效/变体知识，归属行写入各 references 头、README 与 CHANGELOG，NEVER 建 LICENSE 文件。

- 全量令牌规格（含 Motion baseline）落盘于 `references/anchors.md`。
- 动效数值单一真源落盘于 `references/motion-standards.md`。
- 动效配方库落盘于 `references/motion-recipes.md`。
- 动效评审方法论落盘于 `references/motion-review.md`。
- 流体交互物理层落盘于 `references/motion-physics.md`。
- 审计自包含计划模板落盘于 `references/motion-plan-template.md`。
- 多变体 picker 规格落盘于 `references/variants-picker.md`。
- 术语反查词典落盘于 `references/motion-vocabulary.md`。
- 版本检查脚本落盘于 `scripts/check_update.py`。
- 测试集落盘于 `tests/tri-frontend-design-full-testcases.md`。
- `motion.audit` 计划落盘于 `plans/`（运行时生成）。

## 进化契约

> 本 skill 是一个可自进化的设计引擎：它从反馈中修正偏好、从偏差中沉淀经验。

- **接收反馈**：用户对锚点选择、令牌匹配、内容纪律、动效基线的任何纠正，MUST 被显式采纳并反映到下次执行；若属普遍性偏差，MUST 回写对应 references。
- **沉淀经验**：跨会话积累的高频偏好可记入项目记忆，作为 §1 步骤2 的默认偏置参考。
- **自我修订**：任何令牌规格/纪律条款/动效数值的变更 MUST 走版本联动（SKILL.md `version` → CHANGELOG → _meta.json → tests frontmatter 同步 bump），NEVER 只改单处。

## 目录结构

```
tri-frontend-design/
├── SKILL.md                       # 主入口：八锚点设计引擎 + 动效方向引擎 + 多变体（三模式双引擎）
├── README.md                      # 特性/目录结构/安装/使用/测试/归属
├── CHANGELOG.md                   # Keep a Changelog + SemVer
├── _meta.json                     # 注册元数据（slug/version）
├── scripts/
│   └── check_update.py            # 版本检查与强制自动更新（四态判定，同源）
├── references/
│   ├── anchors.md                 # 八个锚点全量令牌规格（含 Motion baseline）
│   ├── motion-standards.md        # 动效数值单一真源（频率/曲线/时长/弹簧/物理性/可中断性/性能/a11y）
│   ├── motion-recipes.md          # 13 个即用动效配方（按钮/下拉/模态/抽屉/toast/...）
│   ├── motion-review.md           # 十条不可协商标准 + 升级触发 + 补救层级 + 输出格式
│   ├── motion-physics.md          # Apple 流体交互物理层（弹簧/速度交接/动量投射/橡皮筋/材质/排版光学）
│   ├── motion-plan-template.md    # 自包含改进计划模板（审计产出 plans/）
│   ├── variants-picker.md         # 多变体方法论 + Picker 逐字规格
│   └── motion-vocabulary.md       # 100+ 动效术语反查词典（12 类）
├── plans/
│   └── README.md                  # 运行时产物目录说明（audit 产出 plans/NNN-*.md）
└── tests/
    └── tri-frontend-design-full-testcases.md  # 全场景测试用例（覆盖三模式）
```
