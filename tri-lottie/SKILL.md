---
name: tri-lottie
slug: tri-lottie
version: 1.0.6
displayName: 跨端动效执行
description: >
  跨端动效决策与执行库——先把任意动效需求转化为技术栈无关的「动效规格单」（情绪→人格→属性→时长→缓动→层次），
  再按用户技术栈路由到 stacks/ 子目录生成对应动画代码：Web(lottie-web)、Android(lottie-android/lottie-compose)、
  iOS(lottie-ios)、鸿蒙 ArkTS(@ohos/lottie)、React Native(lottie-react-native)、Flutter(lottie 包)。
  覆盖动画、过渡、微交互、加载态、转场、Lottie 资产集成与动效审查。支持独立安装，含上游依赖检测三态逻辑。
summary: 决策与执行分离的动效 skill——8 步规格单保证设计质量，六端实现模板保证代码可运行，质量门（CRITICAL/HIGH/MEDIUM）映射 P0/P1/P2 一票否决。
tags: [motion-design, lottie, animation, frontend, android, ios, harmonyos, react-native, flutter, tri-family]
license: MIT
---

# tri-lottie — 跨端动效

> 本 skill 是 tri-intent 下游执行者（I11 编码开发 · motion 动效实现子类）。
> 用户心智：给一句动效需求 + 一个技术栈，拿到一段「先符合动效设计方法论、再符合该端最佳实践」的可运行代码；只给需求不给技术栈时，先产出规格单再追问目标端。
> 与 tri-frontend-design 边界：那边产出「设计方向与令牌规格」，本 skill 产出「动效实现代码与集成方案」。

## 强制执行契约（Execution Contract · 最高优先级）

> 直接命中 §触发时机 任一分支，或快照 `L2 = I11 且 L3_子意图 = motion` 即视为激活本 skill 工作流，不得仅将本文件当作参考文档。

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（运行 `scripts/check_update.py`，按四态判定处置；非最新版自动升级，升级通道不可用则降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。
1. **决策先行强制**：任何动画代码生成前 MUST 先完成「动效规格单」（§方法论 8 步清单），NEVER 跳过决策层直接写代码——跳步产物 MUST 判不合格。
2. **技术栈路由强制**：规格单完成后 MUST 按用户技术栈路由到 `stacks/<端>/implementation.md` 生成代码；NEVER 凭记忆内联端上 API——六端知识以 stacks/ 文档为唯一事实源。用户未指定技术栈时 MUST 先出规格单再追问，NEVER 猜测目标端。
3. **坑位前置强制**：生成某端代码前 MUST 通读该端 implementation.md 的「资产规范与坑位」节并逐条规避（如 ArkTS 相对路径禁令、Expo 版本匹配）；NEVER 输出与坑位清单冲突的代码。
4. **质量门强制**：交付前 MUST 过 §质量标准 引用的质量门（CRITICAL 项一票否决），NEVER 带一级缺陷交付。
5. **上游信息零残留**：本 skill 全部产物 NEVER 包含任何上游作者/版权/品牌/Logo/外链署名信息；第三方库仅以标准安装坐标引用。
6. **自检**：作答前用一句话声明「本次意图=I11(motion)，已读取快照=<是/否>，模式=<规格单/实现/审查>，目标端=<端|待澄清>，质量门=<未检/已过>」。

## 触发时机

| 触发分支 | 典型信号 | 处理 |
|---|---|---|
| 快照路由 | 快照 `L2=I11`、`L3_子意图=motion`、下游路由建议=tri-lottie | 标准链路 |
| 直接触发 | 「给这个按钮加动画」「用 Lottie 实现加载态」「鸿蒙/Android/iOS/RN/Flutter/Web 上做转场」「审查我的动画代码」 | 标准链路 |
| 审查触发 | 「看看这段动画代码有什么问题」「动画为什么卡/廉价/太快」 | 走质量门排障链路 |
| 不由本 skill 处理 | 界面设计方向/配色/布局（→tri-frontend-design）；一般编码任务（→tri-coding）；调试非动画缺陷（→tri-fix） | 指回对应 skill |

## 上游依赖检测（三态 · 编码类可降级）

| 模式 | 触发条件 | 行为 |
|---|---|---|
| A · 快照模式 | 快照 `L2=I11 & L3=motion` 指向本 skill | 读取快照 §三任务要点，按 §处理流程 推进 |
| A0 · 待识别 | 有 tri-intent 但无可用快照 | 提示用户先经 tri-intent 产出快照；用户直接下达明确动效需求时，可按「直接触发」分支推进（视为降级输入） |
| B · 引导安装 | 未检测到 tri-intent 且无快照 | 提示安装 `python ops/install-skills.py --target <目标目录>`；用户可改用直接触发 |
| C · 降级模式 | 用户明确拒绝安装 | 自构造等价输入（需求要点 + 目标端 + 人格关键词），声明降级模式后照常推进 |

## 输入契约

| 字段 | 必需 | 说明 |
|------|------|------|
| 动效需求描述 | 是 | 情绪/元素/场景（如「支付成功庆祝动画」） |
| 目标技术栈 | 否 | web/android/ios/harmonyos-arkts/react-native/flutter 之一；缺省则先出规格单再追问 |
| 实现偏好 | 否 | Lottie 资产 vs 框架内置动画系统（缺省由 stacks/ 选型决策树判定） |
| 人格关键词 | 否 | fun/elegant/clean/bold 等（缺省按内容类型默认表取） |
| 既有代码 | 审查模式必需 | 待审查的动画代码片段 |

## 职责边界

- **本 skill 负责**：动效规格单产出；六端动画代码生成（Lottie 资产集成 + 框架属性动画）；Lottie 播放控制/资产加载/坑位规避；动效代码审查与修复建议；reduced-motion 降级实现。
- **不负责**：界面视觉设计（tri-frontend-design）；通用编码任务（tri-coding）；非动画类缺陷调试（tri-fix）；Lottie JSON 动画的设计制作（那是设计师/AE 工具链的职责，本 skill 只消费资产）。
- **MECE 声明**：I11 下 tri-coding（默认实现）/ tri-frontend-design（设计方向子类）/ tri-lottie（motion 实现子类）三者以交付对象区分，互不重叠。
- **不触发场景（Not-Trigger）**：本 skill 不接手「界面视觉设计 / 动效方向规格」（转 tri-frontend-design）；不接手「通用编码任务」（属 tri-coding）；不接手「非动画类缺陷调试」（属 tri-fix）；不接手「Lottie JSON 动画的原创设计与制作」（属设计师/AE 工具链，本 skill 只消费资产）；不接手「识别用户意图」（由 tri-intent / 自身快照驱动）。

## tri-lottie 方法论（核心能力 · 可扩展）

### 一、决策层：动效规格单（8 步，任何代码生成前 MUST 完成）

1. **情绪目标**——观众该感受什么（joy/calm/urgency/elegance...）→ 查 `references/emotion-mapping.md`
2. **人格原型**——Playful / Premium / Corporate / Energetic 四选一 → 查 `references/motion-personality.md`（未指定：UI 默认 Corporate，插画默认 Playful）
3. **主属性**——position/scale/rotation/opacity 最少够用（两个属性是甜点）
4. **时长**——按元素类型查 `references/motion-tokens.md`（×距离缩放系数；出场=入场 65-75%）
5. **缓动族**——入场 ease-out / 出场 ease-in / 屏内 ease-in-out / 循环 sine / 旋转进度 linear
6. **主角元素**——每时刻一个 hero，其余元素降级为次要
7. **三层运动**——primary(100%) + secondary(30-50%，延迟 50-100ms) + ambient(10-20%)；缺层=扁平
8. **1/3 法则校验**——位移不超容器 1/3；3+ 元素同时活跃不超 1/3；stagger 总预算 < 500ms

**规格单输出格式**（技术栈无关，六端复用）：

```
〔意图|人格|主属性|时长|缓动|过冲|层次〕
例：〔卡片入场|Premium|position+opacity|350ms|cubic-bezier(0.4,0,0.2,1)|0%|primary+secondary(shadow 延迟 50ms)〕
```

### 二、执行层：六端路由与选型

| 用户技术栈 | 实现文档 | 要点 |
|-----------|---------|------|
| Web / H5 / React / Vue | `stacks/web/implementation.md` | lottie-web（SVG/Canvas 渲染器选型）+ 声明式动画选型树 |
| Android / Compose | `stacks/android/implementation.md` | View 与 Compose 双轨（两个独立 artifact 勿混引） |
| iOS / SwiftUI / UIKit | `stacks/ios/implementation.md` | iOS 13.0+，SwiftUI LottieView / UIKit AnimationView |
| 鸿蒙 ArkTS | `stacks/harmonyos-arkts/implementation.md` | API 12+，仅 Canvas 渲染，路径坑最多 |
| React Native / Expo | `stacks/react-native/implementation.md` | RN 0.71+，Expo 双工作流与版本匹配 |
| Flutter / Dart | `stacks/flutter/implementation.md` | 纯 Dart 实现六平台，AnimationController 精控 |

选型总原则：**Lottie 资产动画用于「设计师导出的复杂矢量动效」；框架内置动画系统用于「代码可表达的简单属性动效」**——各端文档第一节均有选型决策树，简单 hover/按压反馈 NEVER 引入 Lottie 资产。

### 三、播放控制概念集（跨端通用词 → 端上 API 见各 stacks/ 映射表）

play / pause / stop / loop / speed / seek / playSegments / reverse / colorTheme / complete 回调 / destroy 释放。

### 四、质量门（三级，映射家族 P0/P1/P2）

- **CRITICAL（一票否决）**：空间移动禁 linear；重要状态变更禁纯 opacity；单段移动 > 1/3 容器；缺 primary 层；stagger 总时长 > 500ms；动画触发 layout 属性致掉帧。
- **HIGH**：时长不匹配元素类型；方向性缓动错误；人格不一致；缺 follow-through；缺 reduced-motion 降级。
- **MEDIUM**：缺 ambient 层；缺 anticipation；过冲失配；缺 counter-motion。
- 完整清单 + 8 类症状排障表 + 10 条快速诊断：见 `references/quality-gate.md`（grep 模式：症状名/缺陷名）。

## 处理流程

```
需求进入（快照或直接触发）
   │
   ▼
第零步：python scripts/check_update.py --slug tri-lottie --json   （state=A/B/C/D 放行；BLOCK 停止）
   │
   ▼
门L1 决策层：8 步清单 → 动效规格单（无技术栈 → 交付规格单并追问目标端 = 停车态）
   │
   ▼
门L2 执行层路由：定位 stacks/<端>/implementation.md → 读库选型树 + 坑位清单
   │   ├── 简单属性动效 → 框架内置动画系统分支
   │   └── 复杂矢量动效 → Lottie 资产集成分支（含加载工厂 + 资产位置规范）
   ▼
门L3 代码生成：规格单 → 端上代码（黄金用例模板为骨架，按需求改参）
   │
   ▼
门L4 质量门：CRITICAL → HIGH → MEDIUM 逐级检查（不过则回到门L2 修复，NEVER 带一级缺陷交付）
   │
   ▼
交付：代码 + 规格单 + 该端坑位核对记录（审查模式：症状→根因→修复选项）
```

> **停车态 vs 结束态**：交付规格单等待用户选择技术栈 = 停车（任务未完，等输入）；质量门全过 + 代码交付 = 结束。审查模式下输出修复建议清单且用户未采纳 = 停车。

## 兜底处理（NEVER 静默失败）

本 skill 在下列五类异常下 MUST 走显式降级路径并**在回执中标注**，NEVER 静默失败、NEVER 交出未过质量门的动画：

| 异常类 | 触发 | 兜底路径 |
|---|---|---|
| ① 版本检查异常 | `scripts/check_update.py` 返回非 A/D 或 ≥20（BLOCK） | 按 §版本检查与更新机制 处置；BLOCK 时停止生成 |
| ② 门禁不过 | §四、质量门（三级，映射家族 P0/P1/P2） 未通过 | 回到规格单与执行层修正；**P0 未达标时不得交付**，明确告知未过门的维度 |
| ③ 上游缺失 | 无 tri-intent 快照 | 走 §上游依赖检测（三态 · 编码类可降级）：由用户口头描述动效需求，先产出规格单再生成 |
| ④ hook 缺失 | 触发源为快照 / 用户直呼 | 不适用 |
| ⑤ 异常场景 | 目标端不在 `stacks/` 覆盖范围、Lottie 运行时不可用、资源缺失 | 显式报告「该端未支持 / 前置不可用」并给出替代端或降级方案；NEVER 生成跑不起来的代码 |

## 🔴 检查点与红灯清单（STOP · NEVER）

### 🔴 用户确认检查点（STOP）

- 🔴 **STOP**：停车态（规格单交付）——用户未指定目标技术栈时 MUST 交付规格单并追问目标端，未获用户确认 NEVER 继续。
- 🔴 **STOP**：停车态（审查模式）——修复建议清单已输出但用户未采纳时保持停车，未获用户确认 NEVER 继续。

### 🚫 红灯清单（NEVER）

- NEVER 跳过决策层直接写代码，跳步产物 MUST 判不合格（§强制执行契约 · 决策先行强制）
- NEVER 凭记忆内联端上 API，六端知识以 stacks/ 文档为唯一事实源（§强制执行契约 · 技术栈路由强制）
- NEVER 猜测目标技术栈（§强制执行契约 · 技术栈路由强制）
- NEVER 带一级缺陷（CRITICAL）交付（§处理流程 · 门L4 质量门）
- NEVER 生成跑不起来的代码（§兜底处理 · 异常场景）
- NEVER 为简单 hover/按压反馈引入 Lottie 资产（§执行层 · 选型总原则）

## 交付产物机制

| 场景 | 产物 | 判定 |
|------|------|------|
| 实现模式 | 可运行代码块 + 规格单 + 坑位核对记录 + 降级说明（reduced-motion） | 质量门全过 = 完成 |
| 纯决策模式 | 规格单 + 推荐实现路径 | 交付规格单 = 完成（无代码场景） |
| 审查模式 | 问题清单（CRITICAL/HIGH/MEDIUM 分级）→ 修复方案 → 变更摘要 | 清单 + 方案齐 = 完成 |
| 生成物落盘 | 本 skill 自身维护于 `.tribro/skills/tri-lottie/` | 见 §落盘规则 |

## 质量标准

| 维度 | 标准 | 验证方式 |
|------|------|---------|
| 决策完整性 | 每份代码可回溯到一张 8 步规格单 | 交付物含规格单行 |
| 端知识一致性 | 代码与 stacks/ 端文档 API/坑位零冲突 | 对照该端 §概念→API 映射 与 §坑位 |
| 质量门 | CRITICAL 全过、HIGH 声明处置、MEDIUM 建议项 | 逐项核对 `references/quality-gate.md` |
| 时长纪律 | 元素时长落在 tokens 表区间；stagger 总预算 < 500ms | 对照 `references/motion-tokens.md` |
| 可访问性 | 每份动效代码附 reduced-motion 降级 | 该端 §性能与 a11y 节 |
| 零残留 | 产物无上游品牌署名 | `python scripts/compliance_check.py` T2 |
| 诚实边界 | 本机无法编译的端如实标注「未真实编译」 | 测试报告逐端标注 |

## 落盘规则

- 本 skill 包落盘于 `.tribro/skills/tri-lottie/`（tri-forge 生成物指定位置；毕业机制成熟后迁入源码树）。
- 链路审计文档（需求卡/合规报告/测试报告）落盘于 `.tribro/forge/<命名>/`。
- 用户工作区产物（规格单/代码/审查报告）随对话交付，或按用户指定路径落盘；`.tribro/` 不存在时 MUST 先创建，交付时在 `.tribro/forge/<命名>/` 落 `delivery-manifest.md` 记录交付物路径清单，保证产物可追溯。
- NEVER 在本 skill 目录生成 LICENSE 或 .gitignore（许可由 frontmatter `license: MIT` 声明）。

### 可扩展性

1. **新增动效预设**：在方法论追加预设条目（用途 / 曲线 / 参数），实现时自动可查
2. **新增集成目标**：在接入说明追加平台（如小程序 / RN），审查清单自动适用
3. **新增审查规则**：在质量标准追加条目，命中即回炉——判定逻辑零改动

## 版本检查与更新机制（强制技术约束 · 硬红线）

<!-- version-stub v1 · 瘦指针节点；细则唯一真源见 references/version-check-spec.md -->

> 任一执行入口启动后的**第零步**，先于核心执行阶段。细则唯一真源：`references/version-check-spec.md`；
> 可执行实现（逻辑唯一真源）：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、状态判定 MUST 由脚本完成；prompt 层 ONLY
> 「调用脚本 + 解析其 JSON 输出 + 按 `state` 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

```bash
python scripts/check_update.py --slug tri-lottie --json
```

- 处置：按脚本输出放行或阻断（判据与 `block_code` 语义见真源）；NEVER 因版本门自身故障阻断 skill 启动。

## 目录结构

```
tri-lottie/
├── SKILL.md                        # 主入口：决策规格单工作流 + 六端路由 + 质量门
├── README.md                       # 特性/结构/安装/使用/测试
├── CHANGELOG.md                    # 版本历史（Keep a Changelog）
├── scripts/
│   ├── check_update.py             # 版本门第零步（与 tri-forge 同源）
│   └── compliance_check.py         # 结构合规 + 零残留 + 坑位断言 + 版本一致性（确定性测试执行器）
├── references/                     # 决策层（技术栈无关）
│   ├── motion-tokens.md            # 时长/距离/缓动/过冲/stagger 数值表
│   ├── motion-personality.md       # 4 人格原型 + 关键词匹配 + 品牌三常量
│   ├── emotion-mapping.md          # 情绪→路径/缓动/时长 + 场景默认
│   ├── quality-gate.md             # 三级质量门 + 排障表 + 快速诊断
│   ├── recipe-patterns.md          # 按钮/卡片/状态反馈/加载/编排成品配方
│   └── version-check-spec.md       # 版本门第零步细则（唯一真源）
├── stacks/                         # 执行层（六端）
│   ├── web/implementation.md
│   ├── android/implementation.md
│   ├── ios/implementation.md
│   ├── harmonyos-arkts/implementation.md
│   ├── react-native/implementation.md
│   └── flutter/implementation.md
└── tests/
    └── tri-lottie-full-testcases.md # 全场景测试用例（结构/决策/六端/审查）
```

## 知识装配顺序（约束 25 · 分层加载）

| 层 | 文件 | 加载时机 | grep 检索模式 |
|----|------|---------|--------------|
| 常驻层 | 本 SKILL.md | 激活即载 | — |
| 决策层 | `references/motion-tokens.md` | 规格单第 4/5 步 | grep `时长\|距离\|过冲\|stagger` |
| 决策层 | `references/motion-personality.md` | 规格单第 2 步 | grep `Playful\|Premium\|Corporate\|Energetic` |
| 决策层 | `references/emotion-mapping.md` | 规格单第 1 步 | grep `<情绪名>` |
| 决策层 | `references/quality-gate.md` | 门L4 或审查模式 | grep `<症状>\|CRITICAL` |
| 决策层 | `references/recipe-patterns.md` | 常见场景直接套配方 | grep `<场景名>` |
| 执行层 | `stacks/<端>/implementation.md` | 门L2 按目标端**单文件**加载 | grep `<库名>\|坑位\|reduced-motion` |

去重与覆盖：同一知识在 SKILL.md 只留摘要，详细表唯一存在于 references/；stacks/ 文档互不引用（端差异只写增量）；用户显式指定的参数覆盖默认表值。

## 进化契约（自进化）

- **反馈接收点**：用户对生成代码/规格单的任何纠正，经本会话记录；结构性问题沉淀到 `.tribro/forge/` 的 forge-lessons.md（经 tri-forge 门⑥）。
- **经验沉淀位**：端上新增坑位 → 对应 stacks/ 端文档「坑位清单」；新数值基线 → `references/motion-tokens.md`；新场景配方 → `references/recipe-patterns.md`。
- **自我修订触发条件**：① 库主版本变更导致 API 漂移（implementation.md 头部「核验于」标注过期）；② 同一坑位在 3 次交付中重复被踩（升级为前置防御）；③ 家族规范新增硬约束。

## 完成判据（外化 · 可机械校验）

| 判据 | 校验方式 |
|------|---------|
| 实现模式完成 | 交付物含规格单行 + 代码块 + 坑位核对记录 + 降级说明四要素 |
| 审查模式完成 | 产出三级问题清单且每条含修复方案 |
| 结构合规完成 | `python scripts/compliance_check.py` 全部用例 PASS（退出码 0） |
| 路由接通完成 | `verify_sync.py --slug tri-lottie` 输出 status=OK |
| 停车态 | 规格单已交付但目标端未定 / 审查建议未被采纳（任务未结束） |
