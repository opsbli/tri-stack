# Changelog

本文件记录 tri-frontend-design skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

> 来源与归属：动效/多变体知识蒸馏自 emilkowalski/skills（MIT License, Copyright (c) 2026 Emil Kowalski），去产品化改写，保留法律归属声明，不建 LICENSE 文件。

## [1.1.8] - 2026-09-28

### 新增

- **家族横切第 10 节「宿主兼容与提问呈现」**：紧跟「版本检查与更新机制」追加 `host-compat-stub v1` 自包含瘦节——
  在提供交互式提问工具的宿主（如 Proma 的 `AskUserQuestion`）中，🔴 STOP 用户确认检查点与 clarify-gate
  MUST 以**普通 Markdown 文本**呈现为聊天问题，**NEVER 调用交互式提问工具**
  （`AskUserQuestion` / `ask_user_question` / `request_user_input` / `clarify` 及等价物）；
  用户回复契约（逐条补充 / 按默认 / 继续 / 是·否）保持不变。
  **只管呈现形式，不改任何门控的判定条件、触发时机与处置动作**；在无交互式提问工具的宿主中本条自然空转。
  细则真源 `tri-intent/references/host-compat.md`；家族规范登记于 `tri-forge/references/family-spec.md`
  §四（第 10 节注）+ §五（待登记项）。

## [1.1.7] - 2026-09-27

### 修复

- **兜底表 ④ 引用路径补全**：`hooks/intent-gate.py` → `tri-intent/hooks/intent-gate.py`（与 §路由归属 的可执行真源表述一致；原先裸写会被读作本 skill 根下的相对路径 → 断链）。

## [1.1.6] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.1.5] - 2026-09-25

### 变更

- **新增「兜底处理（NEVER 静默失败）」章节**：补齐家族合规判据第 14 条要求的五类异常显式降级路径（版本检查异常 / 门禁不过 / 上游缺失 / hook 缺失 / 异常场景），并按本 skill 的触发源与既有机制定制。属文档补全，无行为变更（无代码改动）。

## [1.1.4] - 2026-09-25

### 变更

- **更正路由归属自述（口径修正，无行为变更）**：原文自称「独立工具 skill，不注册为 tri-intent 下游路由项」「不认领任何 L2/L3 编码」「不认领 tri-intent 下游路由」，与**路由真源**冲突 —— `tri-intent/SKILL.md` §一 路由映射表与 `tri-intent/doing/I11-coding.md` 均把本 skill 列为 `I11` 的 `L3=frontend-design` 子类**一跳覆写**下游，`tri-intent/hooks/intent-gate.py` 另有 `("I11","frontend-design") → "tri-frontend-design"` 可执行映射，`tri-intent/CHANGELOG` 亦记载该路由是「真空断链修复」的有意新增（此前本 skill 无任何路由入口）。
- 现改为：**本 skill 参与 I11 子类路由，同时也支持用户直接调用**（三态上游依赖检测保留，两条入口并存）；§触发时机 补「tri-intent 路由」触发行 + 路由归属注记；§职责边界 补齐与同层五落点（tri-coding / tri-lottie / tri-prototype / tri-html / tri-sdlc）的产出物形态 MECE；自检句 `下游=<否>` 改为 `路由=<I11/frontend-design 子类|用户直调>`。
- 非功能性变更（文档口径），无行为变更。

## [1.1.3] - 2026-09-24

### 变更

- **版本门节统一为 `version-stub v1` 形态**：`## 版本检查与更新机制` 收敛为 14 行（执行方式 + 真源指针）。原节为 11 行并**内联了四态判定 / 退出码语义**，违反 `references/version-check-spec.md` §六「≤30 行、禁内联细则」；细则唯一真源为该 spec，行为不变。
- 非功能性变更（文档口径），无行为变更。

## [1.1.2] - 2026-09-24

### 变更

- **分支收窄为编程工作流专线（22 skill）**：清理对已移除 skill 的交叉引用——职责边界表 / 不由本 skill 处理表的对应行改为「本分支未包含（原 tri-xxx）」或删除；已删的委派关系与相邻边界说明同步失效。非功能性变更（文档）。

## [1.1.1] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手完整工程代码/HTML 渲染实现（tri-html）、库选型工程决策与代码质量审查（tri-coding / tri-review）与意图识别（不经 tri-intent），强化「只定方向与令牌，不落地工程代码」边界。

## [1.1.0] - 2026-09-02

### 新增（双引擎 + references 分层 · 方案 B）

- **动效方向引擎（`motion` 模式）**：由"空间轴"扩展至"时间轴 + 物理轴"，补齐 tri-frontend-design 最大结构性缺口。
  - 强制契约三条红线：⑦频率硬门（100+ 次/天与键盘触发动作 MUST NOT 动画）、⑧动效令牌真源（曲线/时长/弹簧 MUST 取自 `motion-standards.md`，NEVER 近似）、⑨a11y 随动效同交（`prefers-reduced-motion` + hover/focus 门控不得后补）。
  - 七步判定序列：频率门 → 目的 → 工具 → 属性(GPU 白名单) → 曲线/弹簧 → 可中断与退出 → a11y 同交。
  - 子动作 `build` / `review` / `find` / `audit`：写实现 / 十条标准评审 + Block-Approve / 机会发现 + 强制否决清单 / 全库审计 + 自包含 plan。
- **锚点↔动效基线映射（1+1>2 独有能力）**：由八锚点自动推导动效基线（如瑞士克制 150–200ms、工业近乎无动效、有机 300–500ms 呼吸），`anchors.md` 八锚点各补 Motion baseline 段。
- **多变体探索（`variants` 模式）**：沿锚点内分歧轴（布局/密度/交互模型/动效叙事）产出 3–5 真正分歧变体 + picker harness + 权衡表；单锚点铁律不破（NEVER 跨锚点混搭）。
- **7 个新 references（知识下沉，硬约束 25 知识装配顺序）**：
  - `motion-standards.md`——动效数值单一真源（频率/曲线/时长/弹簧/物理性/可中断性/性能/a11y），含 6 项关键值核验表。
  - `motion-recipes.md`——13 个即用配方（按钮/下拉/tooltip/模态/抽屉/toast/手风琴/交错/长按/tab/clip 揭示/拖拽/blur 遮罩/WAAPI）+ 工具选择表。
  - `motion-review.md`——十条不可协商标准 + 升级触发 + 补救层级 + Before-After-Why 输出格式 + Block/Approve 裁决。
  - `motion-physics.md`——Apple 流体交互物理层（响应/直接操控/可中断/弹簧/速度交接/动量投射/橡皮筋/材质/排版光学 + 速查表）。
  - `motion-plan-template.md`——自包含改进计划模板（审计产出 `plans/`，假设执行者零上下文零品味）。
  - `variants-picker.md`——多变体方法论 + Picker 逐字规格 + 六阶段流程 + 单锚点铁律关系。
  - `motion-vocabulary.md`——100+ 动效术语反查词典（12 类，已中文化）。
- **职责边界升级为显式转介表**：库选型/RN/Swift → `tri-coding`；代码质量/安全/架构 → `tri-review`；HTML 渲染 → `tri-html`；意图识别 → `tri-intent`。
- **三模式七处同步（硬约束 26）**：触发时机 / 强制契约 / 输入契约 / 职责边界 / 落盘规则 / 产物清单 / 自检句 三模式全覆盖。
- **P0 合规红线全部达成**：不建 LICENSE 文件（仅 frontmatter `license: MIT` + 各文件归属行）；完全剥离作者站外引流内容与个人署名口径（客观规范表述）。

### 变更

- `SKILL.md` 232 → 341 行（余量 159 行，硬约束 13 行数上限达标）。
- `references/anchors.md` 八锚点各补 Motion baseline 段（grep `Motion baseline` == 8）。

### 修复

- **打包合规（skillhub 发布拦截）**：移除 `plans/.gitkeep`（平台拒绝 `.gitkeep` 文件类型，报 `不允许的文件类型`），改为正式 `plans/README.md`，说明该目录为 `motion.audit` 运行时产物目录及其四条硬规则（NEVER 改源码 / 计划自包含 / 必建 README / 令牌真源），与 `references/motion-plan-template.md` 第 82 行「MUST 创建或更新 `plans/README.md`」对齐。
- 目录结构同步：`SKILL.md` 与 `README.md` 的 `plans/` 条目补 `README.md` 子项（硬约束：目录结构与磁盘一致）。

## [1.0.0] - 2026-08-29

### 新增

- **初始版本（tri-forge 蒸馏）**：参照开源 `frontend-design` 技能，按 tri-xxx 家族规范（12/13 章结构 + 版本检查门 + 26 条硬约束）合规化、中文化蒸馏而成。
- **八个风格锚点**：瑞士风格 / 工业风 / 粗野主义 / 极光极繁主义 / 混沌极繁主义 / 复古未来主义 / 有机风 / 低保真，各自锁定配色/字体/结构/质感 CSS 令牌。
- **五步工作法**：情境 → 锚点（偏向出人意料）→ 差异化点 → 系统（匹配令牌）→ 实现。
- **单锚点铁律**：一个简报一个锚点，禁止杂交（范畴错误）。
- **内容纪律（§2）**：规则 + 五项禁止（冒充真实数据的捏造 / 填充标签 / 主题化替换标准 UI 文案 / Unicode 字形图标 / AI 腔套话）。
- **交付物（§4）**：明确的导向 / 令牌保真 / 内容节制 / 差异化点可见。
- **发布前自检（§5）**：出人意料搭配 / 令牌保真 / 内容节制 / 差异化点可见 / 抗杂交。
- **全量令牌规格**：`references/anchors.md` 作为令牌单一事实源，含每个锚点的 Surface / Typography / Accent / Structure / Breaks if。
- **版本检查门（第零步）**：自带 `scripts/check_update.py`（四态判定，与全家族同源一致），细则真源指向 `tri-forge/references/version-check-spec.md`。
- **上游依赖检测三态**：快照模式 / 引导安装 / 降级模式。
- **配套文件**：SKILL.md / README.md / CHANGELOG.md / _meta.json / scripts / references / tests。
