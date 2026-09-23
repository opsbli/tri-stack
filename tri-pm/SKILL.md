---
name: tri-pm
slug: tri-pm
version: 1.1.1
displayName: 产品管理（PM）产物与工作流
description: "产品管理（PM）领域产物与工作流 skill，以 9 大 PM 域、68 个框架、42 条链式工作流为知识底座，产出 PRD、战略画布、路线图、OKR、GTM、竞品分析、数据分析与 AI 交付审计包等结构化产物。认领 I06 的 PM 产物子类（L3_子意图=pm，与 tri-article 并列，非独占 I06）。支持独立安装，含上游依赖检测三态逻辑；可经 tri-intent 下游路由建议接入。"
summary: 蒸馏 pm-skills 的产品管理（PM）领域 skill——覆盖探索、战略、执行、研究、分析、上市、增长、工具与 AI 交付审计九域。
tags:
  - product-management
  - prd
  - strategy
  - roadmap
  - gtm
  - discovery
  - analytics
  - distillation
license: MIT
---

# tri-pm — 产品管理（PM）产物与工作流

> **下游执行 skill**：本 skill 是 tri-intent 在 I06（内容生成）下的 **PM 产物子类**（`L3_子意图 = pm`）执行者。
> **用户心智**：把 AI 当「资深产品经理」——给一个模糊想法或一堆素材，拿到一份结构严谨、可直接评审的 PM 产物，而不是一段泛泛而谈的文字。

---

## 强制执行契约（Execution Contract · 最高优先级）

> 本节定义 skill「被激活后必须做什么」，优先级高于 Agent 的通用默认行为。**读取快照且 `L2 = I06` 且 `L3_子意图 = pm` 即视为激活本工作流**，MUST NOT 仅将其当作参考文档。

0. **版本检查前置硬门（第零步）**：任一执行入口启动后、核心执行前，MUST 先运行 `python scripts/check_update.py --slug tri-pm --json`，并按 `references/version-check-spec.md` 的四态判定处置（退出码 `<20` 放行，`>=20` 阻断）。**版本检查完成前 NEVER 进入后续步骤**。本条目优先级高于所有其它强制前置条目。
1. **基准一致铁律**：本 skill 输出的一切 PM 领域结论 MUST 可回溯至蒸馏基准报告 `docs/pm-skills-main-engineering-analysis.md` 的某一节；**NEVER 引入报告之外的框架、数量或能力作为「蒸馏结论」**。报告未覆盖的内容 MUST 显式声明为「通用知识」并与之区分。
2. **分层加载铁律（规模约束）**：源项目约 71k 词，**NEVER 一次性灌入全部域知识**。MUST 按 `## 知识装配顺序` 分层、按需加载——先加载常驻层，再按用户点名加载对应框架/命令文件（框架级粒度，§九 D-B）。
3. **专有语法翻译铁律**：源项目的 Claude Code 专有语法（`$ARGUMENTS`、`/command` 斜杠调用、subagent fan-out、`allowed-tools`）在本环境**不可用**，MUST 翻译为对话上下文 / 编排步骤 / 只读代理，NEVER 原样输出给用户当作可执行命令。
4. **保真度诚实铁律**：MUST 按保真度分级陈述能力——框架知识 100%、工作流编排 90%、自动触发 85%、审计类 70%、外链需审查。**NEVER 声称「100% 复刻源项目」或「已具备源项目完整能力」**——当前交付为 Phase 1 骨架形态，差距表见 `## tri-pm 方法论` §四 与 `distillation-baseline.md` §八，回答能力类提问时 MUST 如实引用。
5. **合规铁律**：保留 MIT 归因与作者声明；NEVER 生成 `LICENSE` 或 `.gitignore`；NEVER 残留可见品牌信息。
6. **完成判据外化**：MUST 按 `## 完成判据（外化）` 以可机械校验的产物/标记判定完成，NEVER 依赖模型自述「已完成」。

---

## 触发时机

- **主触发（独立运行）**：用户点名 `tri-pm`，或提出 PM 产物类需求（PRD / 路线图 / OKR / 战略画布 / 竞品分析 / GTM / 增长闭环 / 用户故事 / 机会解树 / 预验尸 / North Star 等）。直接执行（无需快照），按域/框架关键词装配对应知识文件。
- **次触发（tri-intent 接入）**：若上游 `tri-intent` 下游路由建议指向本 skill（即 `L2 = I06 内容生成` 且 `L3_子意图 = pm`，`下游 slug = tri-pm`），读取快照 §三 后按本契约执行。
- **审计意图特例**：用户要求审计 AI 生成代码（意图 vs 实现缺口）→ 装配 `ai-shipping` 域，启用 `file:line` 证据机制。
- 任一触发成立即激活。

**不触发**（移交其它 skill）：文章/博客撰写 → `tri-article`；通用内容生成 → `tri-content`；格式转换 → `tri-pdf2md` 等子类；项目规划拆解 → `tri-plan`。

> **路由登记状态**：本 skill 与 `tri-article` / `tri-html` / `tri-checklist` 并列，同属 **I06 下的产物子类**，以 `L3_子意图` 区分、由上游按 `下游 slug` 分发；**非独占 I06 顶层路由**（I06–I10 的顶层认领方为 `tri-content`）。路由表登记为**待办项**，见 `## 进化契约` 与合规报告。

> **约束 26 适用声明**：本 skill **无运行模式 / 子命令 / 子 SKILL**——9 个 PM 域以 `references/` 知识包形式按用户指定层加载，非运行模式。故「新模式落地七处同步」判定为**不适用**（显式声明，非遗漏）。

## 上游依赖检测（三态）

本 skill 属内容生成类（可降级），采用三态：

| 态 | 触发条件 | 行为 |
|:--:|---------|------|
| **A · 标准模式** | tri-intent 可用且存在可用快照 | 读取快照 §三，按工作流推进 |
| **B · 引导安装** | 未检测到 tri-intent | 提示用户：`skillhub install tri-intent --dir <目标目录>` 后重试 |
| **C · 降级模式** | 用户明确拒绝安装 tri-intent | 声明「降级模式，路由归属需人工复核」，从用户请求自构造等价输入后推进 |

> 降级模式下，意图判定精度低于完整工作流，交付物 MUST 提示用户复核域归属。

## 输入契约

| 字段 | 用途 | 默认值 |
|------|------|--------|
| `intent.L2_核心意图` | 须为 `I06`（内容生成） | `I06` |
| `intent.L3_子意图` | 须为 `pm`（PM 产物子类） | `pm` |
| `dimensions.目标域` | 9 域之一，决定装配哪个知识包 | 由关键词推断，歧义时询问 |
| `dimensions.输入形态` | 模糊想法 / 问题陈述 / 素材文件 / 既有文档 | 模糊想法 |
| `任务要点` | 要产出的 PM 产物类型（PRD/画布/路线图/…） | 必填 |
| `交付预期` | 产物格式（Markdown 为主）、详略、是否落盘 | Markdown + 默认落 `.tribro/pm/`（用户指定交付路径时同步交付） |
| `保真度要求` | 是否严格贴合源项目框架 | 严格贴合（默认） |

## 职责边界

**本 skill 负责**

- 基于蒸馏知识产出结构化 PM 产物：PRD、战略/精益/商业模型画布、产品愿景、价值主张、OKR、结果导向路线图、冲刺计划与回顾、发布说明、预验尸、干系人地图、用户故事 / Job Stories / WWA、测试场景、优先级排序、用户画像与细分、客户旅程、市场规模测算、竞品分析、情感分析、SQL/队列/A-B 分析、GTM 战略、滩头细分、ICP、增长闭环、战斗卡、定位与命名、North Star、简历评审、NDA、隐私政策、语法校对。
- AI 交付审计：文档化 AI 生成应用、静态安全与性能审计、测试覆盖映射、**意图 vs 实现缺口审计**（带 `file:line` 证据）。
- 按知识装配顺序分层加载域知识，控制上下文开销。

**本 skill 不负责**

- 文章/博客/技术写作（→ `tri-article`）；通用内容生成（→ `tri-content`）。
- 项目规划与工作流拆解（→ `tri-plan`）；代码编写（→ `tri-coding`）；缺陷修复（→ `tri-fix`）。
- 把人/工作流/方法论蒸馏为 skill（→ `tri-god`）；按家族规范生成 skill（→ `tri-forge`）。
- 格式转换（→ `tri-pdf2md` / `tri-docx2md` / `tri-pptx2md` / `tri-xlsx2md` / `tri-html2md`）。
- **不触发场景（Not-Trigger）**：本 skill 不接手「文章/博客/技术写作」（→ tri-article）；不接手「通用内容生成」（→ tri-content）；不接手「项目规划与工作流拆解」（→ tri-plan）；不接手「代码编写」（→ tri-coding）；不接手「缺陷修复」（→ tri-fix）；不接手「把人/工作流/方法论蒸馏为 skill」（→ tri-god）；不接手「按家族规范生成 skill」（→ tri-forge）；不接手「格式转换」（→ x2md 族）。

**与相邻 skill 的边界（MECE）**：I06 下已有「文章撰写子类 → `tri-article`」「格式转换子类族」「知识库搭建子类 → `tri-wiki`」。本 skill 认领 **PM 产物子类**——PRD、画布、路线图等 PM 专属产物，与文章、格式转换无重叠；以 `L3_子意图` 区分，一跳直达。

## tri-pm 方法论

### 一、蒸馏定位

本 skill 承载的是源项目的**领域知识**（框架、模板、分析结构），而非其运行机制。源项目的「技能=名词/命令=动词」二分，在本 skill 内映射为：

| 源概念 | 本 skill 承载形式 |
|--------|------------------|
| 68 个技能（框架知识） | `references/pm-frameworks-map.md` 九域清单 |
| 42 条命令（链式工作流） | `references/workflows-and-execution.md` 编排范式 |
| 四层架构与设计决策 | `references/distilled-architecture.md` |
| 接口契约与 schema | `references/interfaces-and-contracts.md` |

### 二、三条可复用原则

1. **框架与流程分离**：知识（画布/矩阵/模板）可被多处复用，流程（探索→排序→验证）独立演进。
2. **渐进式披露**：概览常驻，细节按域按需加载——这是应对 71k 词规模的唯一可行方式。
3. **解耦优先**：域之间不硬链；跨域衔接用自然语言建议「下一步」，与源项目「禁止跨插件硬引用」同源。

### 三、九域路由

| 域 | 触发关键词 | 典型产物 |
|----|-----------|---------|
| 探索 | 构思、假设、实验、机会解树、访谈、优先级 | 发现计划、假设矩阵、实验设计 |
| 战略 | 愿景、画布、SWOT、PESTLE、五力、安索夫、定价 | 战略画布、变现与定价方案 |
| 执行 | PRD、OKR、路线图、冲刺、回顾、预验尸、故事 | PRD、OKR、路线图、用户故事 |
| 研究 | 画像、细分、旅程、市场规模、竞品、情感 | 画像、TAM/SAM/SOM、竞品分析 |
| 分析 | SQL、留存队列、A/B | 查询语句、留存曲线、显著性结论 |
| 上市 | GTM、滩头、ICP、增长闭环、战斗卡 | GTM 方案、战斗卡 |
| 增长 | 定位、命名、价值主张文案、North Star | 定位方案、North Star 指标树 |
| 工具 | 简历、NDA、隐私政策、校对 | 法律文本、简历评审 |
| AI 交付 | 审计、安全、性能、测试覆盖、交付打包 | 审计包（含 `file:line` 证据） |

> 完整技能/命令清单见 `references/pm-frameworks-map.md`（grep：`<域名>`）。

### 四、当前形态与路线图差距（诚实声明）

> 报告 §1.1 / §7.2 / §9 / §11 的目标形态是「**1 路由 skill + 9 领域子技能**」。
> 本 skill v1.1.0 = **全量蒸馏**（Phase 1–4 已落地，见下表）；领域结论以 `references/frameworks/` 与 `references/workflows/` 蒸馏正文为事实源，NEVER 以模型背景知识替代。

| 项 | 状态 |
|---|:---:|
| 九域路由映射 | ✅ 已落地（见上表） |
| 9 个子技能拆分 | ⚠️ 以 `references/` 知识包 + 分层装配替代（规避 500 行上限） |
| 68 框架正文搬运（Phase 2） | ✅ 已落地——`references/frameworks/` 68/68（含 MUST-SECTIONS / 引导问题 / 输出模板 / 外链） |
| 42 命令全量重写（Phase 3） | ✅ 已落地——`references/workflows/` 42/42（含 Checkpoint 原句 / 输出模板） |
| 内容校验器移植（Phase 4） | ✅ 已落地——`scripts/validate_pm_artifact.py`（引用 / 章节 / 体积 / 语法 / 装配五模式） |

> 完整差距表、更新纪律见 `references/distillation-baseline.md` §八（grep：`形态差距`）。

## 处理流程

```
第零步  版本检查门（scripts/check_update.py）── 未过 → 阻断
   ↓
① 输入解析   → 判定目标域：命中 1 域 → 进②；命中 ≥2 域 → 触发【多域检出门】（见下）
   ↓
② 知识装配   → 常驻层（基准 + 架构）→ 用户指定层（框架级：frameworks/<域>/<框架>.md ＋ workflows/<域>/<命令>.md）→ 模式层（契约，按需）
   ↓
③ 信息补齐   → 按框架必需字段对话式提问；已提供素材则只问缺口
   ↓
④ 框架产出   → 套用对应框架模板，产出结构化 Markdown 产物
   ↓
⑤ 保真核对   → 对照 references/distillation-baseline.md 校验未越界、未臆测
   ↓
⑥ 完成判据   → 产物落盘 + 必含章节校验 + 输出 [TRI-PM-PASS] 标记
   ↓
⑦ 下一步建议 → 以自然语言建议后续动作（NEVER 硬引用其它 skill 命令）
```

**检查点**：步骤 ③ 与 ④ 之间设一处，用户可重定向、跳过或深入（沿用源项目 checkpoint 范式）。

### 【多域检出门】（流程① 分支 · 硬约束）

> **触发**：一次请求命中九域中的 **≥2 个域**。
>
> **为何源项目没有这道门**：源项目 9 个插件各自独立调用，一命令只产一产物，**结构上不可能揉成一坨**；本 skill 把 9 域压进单个 skill 的九域路由表，一条自然语言请求可同时命中多域——这是**源架构根本不存在的失效模式**。故本门是 tri-pm 特有的**加法**，NEVER 回滚解耦原则本身（回滚会一并丢掉解耦的可维护性）。依据见 `references/distillation-baseline.md` §九 D-D。

**检出后 MUST 执行**：

1. **声明检出结果**——向用户明示命中了哪几个域、各自对应什么产物类型。
2. **默认按域拆分**——MUST 拆为多份独立产物，每份各自走完整的 ②→⑦；**NEVER 静默合并**。
3. **逃生舱**——用户明确坚持合并时：MUST 先声明章节污染风险，在产物头部标注 `> 多域合并件（含 <域A>/<域B>/<域C>，章节可能互相污染）`，再放行。
4. **停车态**——检出 ≥2 域且用户未表态：声明「停车待续 · 等待用户选择拆分或合并」，NEVER 直接开工。

> **实测教训**：缺省合并曾造成真实损害（三域请求被揉进一份产物，章节互相污染），见 `articles/developer-tools/20260903-tri-pm-layered-loading.md` L79。

## 知识装配顺序

> 依家族硬约束 25（`references/` ≥3 文件须声明分层装配）。

| 顺序 | 层 | 文件 | 加载条件 | grep 模式 |
|:----:|---|------|---------|----------|
| 1 | **用户指定层·框架级** | `references/frameworks/<域>/<框架>.md`（68 个） | 用户点名框架/产物类型时加载**单个框架文件**（§九 D-B 裁定 1：NEVER 整域装配） | 框架名（create-prd、swot-analysis、lean-canvas…） |
| 2 | **用户指定层·命令级** | `references/workflows/<域>/<命令>.md`（42 条） | 需要链式工作流时加载**单条命令文件** | 命令名（write-prd、discover、ship-check…） |
| 3 | **用户指定层·导航** | `references/pm-frameworks-map.md` | 不确定用哪个框架时，先查九域导航清单 | `<域名>`（探索/战略/执行/…）、`技能`、`命令` |
| 4 | **用户指定层·范式** | `references/workflows-and-execution.md` | 需要命令链范式或翻译映射总览时 | `命令链`、`校验流程`、`翻译映射` |
| 5 | **模式/角色层** | `references/interfaces-and-contracts.md` | 需要产出契约/schema 或做审计时 | `契约`、`frontmatter`、`引用协议`、`CLI` |
| 6 | **常驻层** | `references/distillation-baseline.md` | **始终加载** | `基准`、`覆盖矩阵`、`防臆测`、`风险`、`验收`、`决策记录` |
| 7 | **常驻层** | `references/distilled-architecture.md` | **始终加载** | `四层`、`模块职责`、`依赖关系`、`数据流`、`设计决策` |
| 8 | **外部覆盖层** | 外部注册目录同名文件 | 存在即覆盖内置版本 | — |

**装配体积守卫**（§九 D-B 修订）：单文件 ≤1,500 词；单次装配（常驻层 + 1 框架 + 1 命令）≤8,000 词；`python scripts/validate_pm_artifact.py --check-assembly <框架> <命令>` 机械校验。

**去重与覆盖规则**

- 同名文件**只保留首次出现**（按上表顺序，先出现者胜）。
- 外部覆盖为**替换而非追加**：外部目录同名文件替换内置版本，位置沿用原层次。
- **常驻层不可被挤掉**：`distillation-baseline.md` 与 `distilled-architecture.md` MUST 始终装配（防臆测纪律与架构认知是最低纪律）。

## 交付产物机制

| 产物 | 命名 | 内容 | 落盘 |
|------|------|------|------|
| PM 文档 | `PRD-<产品名>.md` / `<框架名>-<主题>.md` | 按框架模板产出的结构化文档 | 默认 `.tribro/pm/`（用户显式指定时落用户工作区并保留 `.tribro` 副本） |
| 审计包 | `reports/<审计类型>-<范围>.md` | 证据化审计结论（每条含 `file:line`） | 默认 `.tribro/pm/<命名>/reports/`（用户显式指定时落用户工作区 `reports/` 并保留副本） |
| 分析产物 | `<分析类型>-<对象>.md` | SQL、留存曲线、显著性结论 | 默认 `.tribro/pm/<命名>/`（用户显式指定时落用户工作区并保留副本） |
| 校验记录 | 随产物输出 | 保真核对结果 + `[TRI-PM-PASS]` 标记 | 不单独落盘 |

> `.tribro/` 不存在时 MUST 先创建；所有产物默认统一落 `.tribro/pm/` 下，用户显式指定交付路径时可同步交付到用户指定位置，但 MUST 在 `.tribro` 保留副本，保证产物可追溯。

> 产物格式以 Markdown 为主；表格优先（源项目大量采用表格承载结构化结论）。

## 质量标准

| 维度 | 标准 | 验证方式 |
|------|------|---------|
| 基准一致 | 每条领域结论可回溯至蒸馏报告某节 | 对照 `distillation-baseline.md` §二 覆盖矩阵 |
| 无臆测 | 无报告外框架/数量被当作蒸馏结论 | grep 产物是否含未标注的外部框架 |
| 框架完整 | 产物含该框架 MUST-SECTIONS 清单全部必含章节 | `scripts/validate_pm_artifact.py --artifact <产物> --framework <框架>` 退出码 0 |
| 分层加载 | 未一次性灌入全部域知识 | 检查装配记录 |
| 无专有语法残留 | 产物无 `$ARGUMENTS`、无 `/pm-*:command` 硬引用 | grep 产物 |
| 合规 | MIT 归因保留，无可见品牌残留 | 人工复核 |
| 完成判据 | 产物落盘且必含章节齐全，输出 `[TRI-PM-PASS]` | 文件存在性 + 章节 grep |

## 落盘规则

- **产物**：落用户工作区，默认 `.tribro/pm/`；审计类产物落 `reports/`；路径须在交付时向用户明示。用户指定路径时以用户指定为准。
- **本 skill 自身**：按用户显式指令落盘于源码树 `tri-pm/`（与 `tri-ask` / `tri-article` 同级）。家族默认生成位为 `.tribro/skills/tri-pm/`，**本次由用户覆写**，已记入合规报告提请确认。
- **NEVER** 在产物目录或本 skill 目录生成 `LICENSE` 或 `.gitignore`；许可证仅由 frontmatter `license: MIT` 声明。

## 完成判据（外化）

> 依家族硬约束 24：完成 MUST 由可机械校验的判据判定，NEVER 依赖模型自述。

**结束态判据**（全满足方可输出 `[TRI-PM-PASS]`）：

1. 目标产物文件已落盘且非空（文件存在性校验）；
2. 产物含该框架 `MUST-SECTIONS` 清单全部必含章节（`python scripts/validate_pm_artifact.py --artifact <产物> --framework <框架名>` 退出码 0）；
3. 产物无 `$ARGUMENTS`、无 `/pm-*:command` 硬引用（grep 为空）；
4. 保真核对通过：无报告外框架被当作蒸馏结论（对照 baseline）；
5. 输出标记行 `[TRI-PM-PASS]`。

**停车态（非结束）**：等待用户选择目标域、等待补齐框架必需字段、等待用户确认检查点——此类状态 MUST 明确声明为「停车待续」，NEVER 标记为完成。

**未完成态**：版本检查门阻断（退出码 `>=20`）、目标域无法确定、必需字段缺失且用户未提供——输出 `[TRI-PM-BLOCK]` 并说明阻塞项。

## 版本检查与更新机制（约束 22 · 前置第零步硬门）

> 家族级强制技术约束，优先级与「强制执行契约」同级。任一执行入口启动后的**第零步**，先于核心执行。

- MUST 运行：`python scripts/check_update.py --slug tri-pm --json`
- 四态 `A`/`B`/`C`/`D` 一律放行；`BLOCK` 绝对禁止执行。
- 退出码 `<20` 放行，`>=20` 阻断；脚本异常时兜底降级放行，NEVER 因版本门故障阻断启动。
- 节流：`24h` 内仅校验一次，`--force` 强制重查，`--dry-run` 只判定不升级。

> **细则唯一真源**：`references/version-check-spec.md`（与 tri-forge 同源的自包含副本）。
> 本章为瘦指针 STUB，**NEVER 内联**四态判定 / 升级流程 / 版本比较算法 / 节流缓存等细则。

## 目录结构

```
tri-pm/
├── SKILL.md                              # 主入口
├── README.md
├── CHANGELOG.md
├── _meta.json                            # 安装元数据（install_skill.py 生成，版本 1.1.0）
├── scripts/
│   ├── check_update.py                   # 版本检查门（第零步）
│   └── validate_pm_artifact.py           # 产物与知识包校验器（引用/章节/体积/语法/装配五模式）
├── references/
│   ├── distilled-architecture.md         # 【常驻层】四层架构 / 模块职责 / 依赖 / 数据流 / 设计决策
│   ├── distillation-baseline.md          # 【常驻层】防臆测铁律 / 覆盖矩阵 / 风险 / 验收 / 决策记录 D-A~D-D
│   ├── interfaces-and-contracts.md       # 【模式层】schema / frontmatter / 引用协议 / CLI
│   ├── pm-frameworks-map.md              # 【用户指定层·导航】九域 68 技能 + 42 命令清单
│   ├── workflows-and-execution.md        # 【用户指定层·范式】命令链范式 / 校验流程 / 翻译映射
│   ├── version-check-spec.md             # 版本检查门细则真源（与 tri-forge 同源）
│   ├── frameworks/                       # 【用户指定层·框架级】68 框架全量正文（9 域子目录 + 6 个 partN 拆分）
│   │   └── <域>/<框架>.md                #   每文件含 MUST-SECTIONS / 逐段引导问题 / 输出模板 / Further Reading
│   └── workflows/                        # 【用户指定层·命令级】42 命令全量编排步骤（9 域子目录 + 3 个 partN 拆分）
│       └── <域>/<命令>.md                #   每文件含工作流步骤 / Checkpoint / 输出模板 / 下一步建议
└── tests/
    └── tri-pm-full-testcases.md
```

> 本 skill 已由 `install_skill.py` 安装至 `C:\Users\bingo\.workbuddy\skills\tri-pm`（**junction → 源码树单源同步**），注册表已登记，运行时冒烟通过。

## 进化契约

> 依家族硬约束 23：生成物 MUST 可进化，而非仅合规。

| 要素 | 声明 |
|------|------|
| **反馈接收点** | 用户对产物质量、框架覆盖度、域归属的修正意见；以及 `docs/pm-skills-main-engineering-analysis.md` 的后续修订 |
| **经验沉淀位** | `references/distillation-baseline.md` §七 禁区与 §三 风险表；新增教训追加为该文件的「蒸馏修正记录」段 |
| **自我修订触发条件** | ① 蒸馏基准报告更新 → MUST 同步覆盖矩阵与评分卡；② 源项目版本升级（当前 v2.1.0）→ MUST 复核九域清单与实证数据；③ 用户指出臆测或缺失 → MUST 修正并回写禁区；④ 新增域知识包 → MUST 同步「知识装配顺序」表与目录结构 |
| **待办登记（待用户确认后执行）** | ① **路由表登记**：在 `tri-forge/references/family-spec.md` §1.3 的 `I06–I10` 行追加「PM 产物子类→`tri-pm`」，并同步家族下游计数（现行 24 个）→ 属跨 skill 改动，MUST 经用户确认后再动；② **拆分为 children**：若后续拆为 9 个子 skill，按硬约束 #26 同步七处并新登记「独立领域入口型」或「父包分发型」形态 |

> 进化时 MUST 保持「版本强一致」：SKILL.md `version` == CHANGELOG 最新 `[x.y.z]` == tests frontmatter 版本。

---

**自检句（作答前声明）**：

> 本次意图=I06（L3_子意图=pm），已读取快照=<是/否>，当前步骤=<第零步/①~/⑦>，装配层=<常驻层+用户指定层(域) >，保真度=<按分级声明>，落盘=<用户工作区路径>，完成态=<[TRI-PM-PASS]/[TRI-PM-BLOCK]/停车待续>，版本门=<state/退出码>。
