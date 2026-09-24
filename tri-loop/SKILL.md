---
name: 循环启动
slug: tri-loop
version: 1.2.4
displayName: 循环启动
description: 知识库 loop（domain）启动下游执行 skill。读取 tri-intent 快照 §三，处理 I14（操作执行·loop/domain 创建子类）意图，在基于文件的知识库中 bootstrap substrate、收集 loop charter、scaffold loop README、执行一次真实测试运行并记录到 Timeline 和 LOG.md。当 tri-intent 快照下游路由建议指向本 skill 时激活。支持独立安装，含上游依赖检测三态逻辑（快照模式/引导安装/降级模式）。
summary: 依据 tri-intent 快照处理 I14 loop/domain 创建子类意图，含 substrate bootstrap、loop charter 收集、README scaffold、真实测试运行、Timeline+LOG.md 记录全链路，确保 loop 可验证运行。
tags: [loop, domain, knowledge-base, bootstrap, scaffold, execution]
license: MIT
---

# 循环启动（下游路由 · I14 · loop/domain 创建子类）

> 本 skill 是 tri-intent 的下游执行 skill，依据快照 `snapshot.md` §三 结构化结论直接执行，不再重新识别意图。
> 用户心智：把 AI 当执行者，期望真实「跑起来」一个可验证的知识库 loop。
> 蒸馏自 new-loop 开源项目，保留全量能力，适配 tri-intent 下游 skill 规范。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（运行 `scripts/check_update.py` 做本地版本一致性校验，本仓库为自维护 fork、不做远端比对；按脚本输出与退出码处置）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：收到 tri-intent 快照且 `下游路由建议` 指向本 skill，MUST 先读取快照 §三，再按 loop 启动工作流推进，NEVER 跳过直接创建文件。**核心铁律：没有 charter 的 loop 不启动——无 goal/cadence 的 loop 是空壳。** 独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式。
2. **Charter 收集 + Scaffold + 真实测试运行 + 记录（硬性规则）**：I14 loop 创建涉及真实文件操作，MUST 严格按「检测 substrate → 收集 charter → scaffold README → 真实测试运行 → 记录 → 回报」串行推进：
   - **Substrate 检测**：检查知识库仓库根目录是否有 `ARCHITECTURE.md` + `LOG.md` + 含 "Knowledge base" 章节的 `CLAUDE.md`。全部存在 → 跳到 charter 收集；有缺失 → 执行 substrate bootstrap（见 §substrate bootstrap 流程）。
   - **Charter 收集**：从快照 §三 `任务要点` 推断 loop 的 5 项输入（name、goal、cadence、做什么、工具/数据）；推断不全时做一轮简短澄清。请求已足够具体则直接推断并确认。
   - **Scaffold**：从 `templates/loop-readme.md` 模板创建 `domains/<name>/README.md`，填入 charter。冲突检查：若 `domains/<name>/` 已存在，停止并询问是否更新而非覆盖。
   - **真实测试运行**：真正运行一次 loop（小规模），做它该做的事。产出 artifact 可选；但 MUST 向 README `## Timeline` 追加一行带日期记录 + 向 `LOG.md` 追加一条记录。
   - **记录**：两个必需输出——Timeline 一行 + LOG.md 一条。无论测试运行是否产出 artifact，这两个记录 MUST 有。
   - **回报**：总结 charter、测试运行结果、创建的 artifact、缺失项、如何再次运行。
   - 完整链路：`substrate 检测 → charter 收集 → scaffold → 真实测试运行 → Timeline+LOG.md 记录 → 回报`。charter 不完整的 loop 不得 scaffold。
3. **最小化原则（门禁规则）**：进入执行阶段前 MUST 校验操作范围是否最小化——只执行 `任务要点` 范围内的操作（创建指定的 loop、运行指定的测试），不执行未明确授权的附加操作（不擅自创建额外 domain、不擅自修改已有 loop、不擅自重构 substrate）。若执行中发现需扩大操作范围，MUST 向用户说明并确认，NEVER 默默扩大范围。
4. **职责边界**：本 skill 负责「读取快照 → 检测 substrate → 收集 charter → scaffold README → 真实测试运行 → 记录 → 回报」全链路。意图识别（由 tri-intent）、编码开发（由 tri-coding）、内容文本产出（本分支未包含）不属于本 skill。
5. **自检**：作答前用一句话声明「本次意图=I14 loop 创建，已读取快照，substrate 状态=<已就绪/已 bootstrap>，loop charter=<已收集 N 项>，测试运行=<已执行/已跳过>，Timeline+LOG=<已记录>」，若与上述规则冲突则停止并纠正。

## 触发时机

- tri-intent 产出的快照中 `下游路由建议` 指向本 skill
- 意图编码范围：I14 操作执行（loop/domain 创建子类）
- 任务要点含以下语义之一：loop、domain、循环、知识库、beat、workstream、charter、cadence

## 上游依赖检测（独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟） | 读取快照 §三，按工作流推进（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | MUST 提示用户「本次请求尚未经意图识别」，引导先经 tri-intent 产出快照；NEVER 按空上下文静默执行 |
| **B · 引导安装** | 以上均不满足 且 用户拒绝降级 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 以上均不满足 且 用户选择直接使用 | 内联澄清：向用户询问 loop 的 5 项输入（name/goal/cadence/做什么/工具数据），自构造输入后按工作流推进 |

> 本 skill 支持降级模式——loop 创建是高频操作，用户可直接调用 tri-loop 而无需先经 tri-intent。降级模式下通过内联澄清自构造快照等价输入。

**模式 B 提示语**：
> 本 skill 依赖 tri-intent 进行意图识别与输入校验。当前未检测到 tri-intent。
> 请安装：`python ops/install-skills.py --target <目标目录>`
> 安装后重新发起请求，即可获得完整的意图识别→澄清→执行工作流。
> 或选择降级模式：直接告诉我 loop 的名称、目标、节奏，我将内联构造输入并执行。

**模式 C 降级流程**：
1. 向用户说明当前为降级模式，tri-intent 未安装
2. 询问 5 项输入（已有信息直接推断，仅问缺失项）：
   - name：kebab-case，loop 的主文件夹名
   - goal：一句话，该 loop 驱动的成果
   - cadence：manual / daily / weekly / cron 表达式（默认 manual）
   - 做什么：消费什么 + 产出什么
   - 工具/数据：数据源或凭证（指向 setup skill 或 .env）
3. 用户确认后，构造等价快照输入，按标准工作流推进

## 输入契约

### 快照模式（Mode A）

读取 `.tribro/snapshots/<命名>.md` 的 §三 结构化结论区：

| 字段 | 用途 |
|---|---|
| `intent.L2_核心意图` | 必须为 I14，否则不应激活本 skill |
| `dimensions.D1_任务领域` | 决定 loop 的领域上下文 |
| `dimensions.D2_输入形态` | loop 消费的数据形态 |
| `dimensions.D4_输出期望` | loop 产出的 artifact 类型 |
| `任务要点` | loop 的 5 项 charter 输入来源 |
| `交付预期` | 用户期望的最终交付物（loop README + 测试运行记录） |

### 降级模式（Mode C）

通过内联澄清收集 5 项 charter 输入，构造等价输入。

## 职责边界

- **本 skill 负责**：依据快照结论或内联输入，bootstrap substrate、收集 charter、scaffold loop README、执行真实测试运行、记录 Timeline + LOG.md
- **不负责**：意图识别（由 tri-intent）、编码开发（由 tri-coding）、内容文本产出（本分支未包含）、通用操作执行（由 tri-action）
- **关键边界**：本 skill「创建并验证知识库 loop」——只创建指定的 loop 并做一次测试运行，不擅自创建额外 domain、不擅自修改已有 loop
- **与 tri-action 的协作**：tri-action 处理通用 I14 操作；当 I14 任务要点含 loop/domain 创建语义时，tri-intent 路由到 tri-loop 而非 tri-action
- **与 tri-coding 的协作**：对于提交代码的 loop，loop 的运行在隔离 git worktree 中进行，通过 `/verify` skill 提交
- **不触发场景（Not-Trigger）**：本 skill 不接手「一次性完成即交付的任务执行」（属对应 I 落点 skill，本 skill 建的是长期运行的知识域/循环体）；不接手「对既有代码的单点调试修复」（属 tri-fix）；不接手「识别用户意图」（由 tri-intent / 自身快照驱动）。

## 核心能力（蒸馏自 new-loop · 全量保留）

> 六项能力的**权威执行步骤统一定义在 §处理流程**，本节只做索引，避免同一套 scaffold/bootstrap 叙述两处漂移。

| # | 能力 | 一句话定义 | 权威定义位置 |
|---|---|---|---|
| 1 | Substrate Bootstrap | 知识库底层基座的一次性、idempotent 设置——仅创建缺失内容，绝不覆盖已有文件 | §Substrate Bootstrap 流程 |
| 2 | Loop Charter 收集 | 5 项输入（name/goal/cadence/做什么/工具数据）定义 loop 是什么、做什么、怎么跑 | §处理流程 · Charter 5 项输入 |
| 3 | Loop README Scaffold | 从 `templates/loop-readme.md` 创建 `domains/<name>/README.md` 并填入 charter | §处理流程 + §交付产物 · loop README 结构 |
| 4 | 真实测试运行 | 小规模真跑一次，证明 loop 能跑而不只是文件夹存在 | §处理流程 · 真实测试运行 |
| 5 | Timeline + LOG.md 记录 | 两个必需输出，无论是否产出 artifact | §处理流程 · 记录格式 + §交付产物 |
| 6 | 回报 | charter + 测试结果 + artifact + 缺失项 + 如何再运行，保持简洁 | §处理流程 |

## Substrate Bootstrap 流程

> 仅当 substrate 缺失时执行。一次性、idempotent。

从**知识库仓库根目录**运行（loop 在此处读写——通常是持有 `CLAUDE.md` 的仓库，而非应用代码仓库）：

1. **`ARCHITECTURE.md`** —— 若根目录缺失，从 `templates/architecture.md` 逐字拷贝
2. **`LOG.md`** —— 若根目录缺失，从 `templates/log.md` 逐字拷贝
3. **`signals/`、`docs/`、`domains/`** —— 对每个缺失的文件夹，创建它并从对应模板写入其 `README.md`（这些 README *就是* schema）：
   - `signals/README.md` ← `templates/signals-readme.md`
   - `docs/README.md` ← `templates/docs-readme.md`
   - `domains/README.md` ← `templates/domains-readme.md`
4. **`CLAUDE.md`** ——
   - 若已存在但没有 "Knowledge base" 章节 → 追加 `templates/claude-kb-section.md` 块（不要碰其余部分）
   - 若不存在 → 提议从 `templates/claude-template.md` scaffold 生成一个（由用户填充 `{{PLACEHOLDER}}`）
5. **不要**预建 `tasks/` 或任何其他 kind——那些是后续赢得的


### 可扩展性

1. **新增 substrate kind**：在 `templates/` 追加 kind 的 README（即 schema），bootstrap 自动创建
2. **新增 loop 模板字段**：在 `templates/loop-readme.md` 追加 frontmatter 字段，charter 收集自动覆盖
3. **新增记录格式**：在 Timeline / LOG.md 约定追加字段，记录逻辑零改动

## 版本检查与更新机制（强制技术约束 · 硬红线）

<!-- version-stub v1 · 瘦指针节点；细则唯一真源见 references/version-check-spec.md -->

> 任一执行入口启动后的**第零步**，先于核心执行阶段。细则唯一真源：`references/version-check-spec.md`；
> 可执行实现（逻辑唯一真源）：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、状态判定 MUST 由脚本完成；prompt 层 ONLY
> 「调用脚本 + 解析其 JSON 输出 + 按 `state` 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

```bash
python scripts/check_update.py --slug tri-loop --json
```

- 处置：按脚本输出放行或阻断（判据与 `block_code` 语义见真源）；NEVER 因版本门自身故障阻断 skill 启动。

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 核心执行。版本检查未通过前 NEVER 进入以下任一执行步骤。

> 基于「substrate 检测 → charter 收集 → scaffold → 真实测试运行 → 记录 → 回报」的执行链路，确保 loop 可验证运行。

```
tri-intent 快照 §三 (I14 · loop 创建子类)
        │
        ▼
  Substrate 检测
  · 检查 ARCHITECTURE.md + LOG.md + CLAUDE.md(Knowledge base)
  · 全部存在 → 跳到 charter 收集
        │
        ├── 缺失 ──→ Substrate Bootstrap
        │             · 拷入 ARCHITECTURE.md + LOG.md
        │             · 创建 signals/ docs/ domains/ + 各自 README
        │             · 注入/创建 CLAUDE.md
        │             · idempotent：仅创建缺失部分
        │                   │
        │                   ▼
        │             Charter 收集 ←─────────┐
        │                                   │
        ▼                                   │
  Charter 收集（从快照 §三 任务要点推断）      │
  · name / goal / cadence / 做什么 / 工具数据  │
  · 推断不全 → 一轮简短澄清 ──→ 用户补充 ────┘
  · 请求已具体 → 直接推断并确认
        │
        ▼
  Scaffold Loop README
  · 从 templates/loop-readme.md 创建 domains/<name>/README.md
  · 冲突检查：domains/<name>/ 已存在 → 停止并询问
        │
        ▼
  真实测试运行
  · 真正运行一次 loop（小规模）
  · 尽量用真实工具/数据；凭证缺失做最远 dry run
  · 产出 artifact 可选
        │
        ▼
  Timeline + LOG.md 记录
  · Timeline：向 README ## Timeline 追加一行
  · LOG.md：追加一条记录（What + Refs）
  · 两个记录 MUST 有，无论是否产出 artifact
        │
        ▼
  回报
  · charter + 测试结果 + artifact + 缺失项 + 如何再运行
  · 保持简洁
        │
        ▼
  交付（loop README + Timeline 记录 + LOG.md 条目）
```

### Charter 5 项输入

> 核心铁律：没有 charter 的 loop 不启动。收集策略——从请求中推断；仅对无法推断的部分做一轮简短澄清；请求已足够具体时直接推断全部五项并在总结中确认。

| 输入项 | 说明 | 默认值 |
|---|---|---|
| name | kebab-case，loop 的主文件夹（`domains/<name>/`） | — |
| goal | 一句话：该 loop 驱动的成果 | — |
| cadence | `manual` / `daily` / `weekly` / cron 表达式 | `manual` |
| 做什么 | 消费什么（signal？数据？收件箱？URL？）+ 产出什么（signal？doc？报告？代码变更？） | — |
| 工具/数据 | 数据源或凭证（指向 setup skill 或 `.env`；切勿内联密钥） | — |

### 真实测试运行

> 本 skill 的核心：证明该 loop 确实能跑。典型小规模动作——分诊几张真实工单 / 拉一条真实 SERP / 抓取收件箱 / 起草一条评论 / 运行一个分析查询 / 界定一个代码变更。
> 尽量使用真实工具/数据；凭证缺失则做能达到的最远 dry run 并记录差距。产出 artifact 可选，仅当确实产出 `signal`/`doc` 时才创建。

### 记录格式（两个必需输出）

**Timeline（`domains/<name>/README.md` 的 `## Timeline` 追加一行）**
```
YYYY-MM-DD | test run — <你做了什么及发现了什么 / "nothing actionable yet">
```

**LOG.md（全局日志追加一条）**
```
## YYYY-MM-DD · <loop-name> loop created + first run · #ops
What: <一行——该 loop 是什么以及首次运行做了/发现了什么>。
Refs: domains/<name>/README.md (new)[, 创建的任何 artifact]。
```

### 阶段速查表

| 阶段 | 关键动作 | 产出 |
|---|---|---|
| 1 | 读取快照 §三，校验 L2 = I14 + loop 创建语义 | — |
| 2 | Substrate 检测（ARCHITECTURE.md + LOG.md + CLAUDE.md） | substrate 状态 |
| 3 | Substrate Bootstrap（若缺失，idempotent 创建） | substrate 文件 |
| 4 | Charter 收集（5 项输入，推断 + 澄清） | loop charter |
| 5 | Scaffold README（从模板创建 domains/<name>/README.md） | loop README |
| 6 | 真实测试运行（小规模，真实工具/数据） | 测试结果 |
| 7 | Timeline + LOG.md 记录（两个必需输出） | 记录 |
| 8 | 执行结果落盘 `.tribro/loops/<命名>/result.md` | result.md |
| 9 | 回报（charter + 结果 + 缺失项 + 如何再运行） | 回报 |

## 交付产物

### 一、文件命名规范

沿用 tri-intent 快照命名：`<问题类型>_<日期>_<时间>_<会话ID>`

- 示例：`I14_20250211_143022_6a5c037d`

### 二、存放目录

> 知识库内容文件存放在知识库仓库根目录；tri-loop 链路文档存放在 `.tribro/loops/` 下，与 tri-intent（`.tribro/snapshots/`）、tri-action（`.tribro/actions/`）保持一致。

```
<知识库仓库根>/
├── ARCHITECTURE.md           # substrate（bootstrap 时创建）
├── LOG.md                    # 全局日志（bootstrap 时创建，loop 创建时追加）
├── CLAUDE.md                 # 运行上下文（bootstrap 时注入/创建）
├── signals/                  # 证据文件夹（bootstrap 时创建）
│   └── README.md             # schema
├── docs/                     # 持久知识文件夹（bootstrap 时创建）
│   └── README.md             # schema
├── domains/                  # loop 文件夹（bootstrap 时创建）
│   ├── README.md             # domain 模板/schema
│   └── <name>/               # ← 本 skill 创建的 loop
│       └── README.md         # loop README（charter + Timeline）
└── .tribro/                  # tri 链路文档（若不存在则先创建）
    ├── snapshots/            # tri-intent 产出（已存在）
    └── loops/                # tri-loop 链路文档
        └── <命名>/           # 命名同快照：<问题类型>_<日期>_<时间>_<会话ID>
            └── result.md     # 执行结果（最终交付物）
```

### 三、产物清单

| 产物 | 位置 | 内容 | 适用 |
|---|---|---|---|
| 执行结果 | `.tribro/loops/<命名>/result.md` | loop charter + 测试运行结果 + artifact 记录 + 缺失项 + 如何再运行 | 全部（必需） |
| loop README | `domains/<name>/README.md` | charter（frontmatter + 描述）+ Current focus + Backlog + Timeline | 全部 |
| Timeline 记录 | `domains/<name>/README.md` 的 `## Timeline` | 一行带日期的测试运行记录 | 全部（必需） |
| LOG.md 条目 | `<仓库根>/LOG.md` | `## YYYY-MM-DD · <loop-name> loop created + first run · #ops` + What + Refs | 全部（必需） |
| 测试运行 artifact | `signals/` 或 `docs/` | 若测试运行产出有价值的 signal/doc | 可选 |
| substrate 文件 | `<仓库根>/ARCHITECTURE.md` 等 | 知识库底层基座 | substrate 缺失时 |

### 四、产物结构规格

**result.md 结构**（基于 `templates/result.md` 模板，落盘于 `.tribro/loops/<命名>/`）：
- loop charter（5 项输入：name/goal/cadence/做什么/工具数据）
- substrate 状态（已就绪 / 已 bootstrap + 创建了哪些文件）
- 测试运行摘要（做了什么 + 发现了什么 + dry run 标注）
- artifact 记录（创建的 signal/doc 路径，或"无——本次运行无可执行事项"）
- 缺失项（待接入的工具/凭证，指向 setup skill 或 .env）
- 如何再次运行（cadence + 入口点）
- 引用（快照路径 + loop README 路径 + LOG.md 条目位置）

**loop README 结构**（基于 `templates/loop-readme.md`）：
- frontmatter：`kind: domain`、`domain`、`status: active`、`goal`、`cadence`
- 标题 + 2-4 行描述（loop 做什么、消费什么、产出什么）
- `## Current focus`：当前最重要的一件事
- `## Backlog`：内联 backlog 项（带 `- [ ]` 复选框）
- `## Evidence & analysis`：证据链接（占位）
- `## Metrics`：指标占位
- `## Timeline`：测试运行记录（一行）

**LOG.md 条目结构**：见 §处理流程 · 记录格式（两个必需输出）。

## 落盘规则

> 与 tri-intent（`.tribro/snapshots/`）、tri-action（`.tribro/actions/`）保持一致，tri-loop 的链路文档落盘到 `.tribro/loops/` 下。

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- **tri-loop 执行结果**落盘于 `.tribro/loops/<命名>/result.md`（若 `.tribro/` 目录不存在，MUST 先创建）
- **知识库内容文件**（substrate + loop README + LOG.md 条目）落盘于知识库仓库根目录——这些是知识库的实际内容，不是 tri 链路文档
- 知识库内容文件可覆盖更新（loop README 是实时状态，LOG.md 是追加日志）；tri-loop 执行结果落盘后不修改（审计完整性）

## 质量标准

| 质量维度 | 标准 | 校验方式 |
|---|---|---|
| loop 可验证运行 | README 存在 + Timeline 有测试运行记录 | 检查 `domains/<name>/README.md` 有 `## Timeline` 且非空 |
| 执行结果落盘 | result.md 存在于 `.tribro/loops/<命名>/` | 检查 `.tribro/loops/<命名>/result.md` 存在且非空 |
| charter 完整 | 5 项输入（name/goal/cadence/做什么/工具数据）全部有值 | frontmatter 有 goal/cadence + 正文有描述 |
| substrate 一致 | ARCHITECTURE.md + LOG.md + CLAUDE.md(Knowledge base) 存在 | 根目录文件存在性检查 |
| 记录可追溯 | Timeline 一行 + LOG.md 一条 + result.md 一份 | 三个记录均存在且内容匹配 |
| idempotent | bootstrap 仅创建缺失文件 | 重复运行不覆盖已有文件 |
| 最小化 | 只创建指定 loop，不擅自扩展 | 未创建未授权的额外 domain |
| .tribro 目录一致 | 链路文档在 `.tribro/loops/` 下，与 snapshots/actions 同级 | 路径检查 `.tribro/loops/` 存在 |

## 安全约束

> loop 创建涉及文件操作，但风险等级较低（创建文件、非删除/覆盖）。以下操作需注意：

| 操作 | 等级 | 确认要求 |
|---|---|---|
| 创建新 domain 文件夹 + README | L1 可逆 | 无需确认，直接执行 |
| 追加 Timeline / LOG.md 记录 | L1 可逆 | 无需确认，直接执行 |
| 创建 signal/doc artifact | L1 可逆 | 无需确认，直接执行 |
| Substrate bootstrap（创建缺失文件） | L1 可逆 | 无需确认，直接执行（idempotent） |
| **覆盖已存在的 domain** | L2 不可逆 | **必须确认**：询问是否更新而非覆盖 |
| **修改已有 CLAUDE.md** | L2 不可逆 | **必须确认**：仅追加 Knowledge base 章节，不碰其余部分 |

## 注意事项

- **不要过度装饰 scaffold。** loop README 是实时状态，不是规格说明——从简开始；让它通过 Timeline 自然增长。
- **一个 loop = 一条可分离的 workstream。** 若用户描述的内容实际上属于某个已有 loop 的一部分，将其添加到那里（一行 backlog 项 + 一个 `domain:` 标签）而非创建近似副本。
- 对于**提交代码**的 loop，loop 的运行在隔离的 git worktree 中进行，并通过 `/verify` skill 提交（验证 + PR），通过 `crabbox-setup` 为每个并行 agent 提供独立的隔离栈。将 README 的 Backlog 指向它们。
- **Substrate 不预建。** 不要预建 `tasks/` 或任何其他 kind——那些是后续赢得的。从 `signal` + `doc` 开始。

## 目录结构

```
tri-loop/
├── SKILL.md                    # 主入口：loop 启动工作流 + substrate bootstrap + 全链路
├── README.md                   # 说明文档
├── CHANGELOG.md                # 变更日志
├── templates/
│   ├── loop-readme.md          # domain README 模板（loop charter + Timeline）
│   ├── architecture.md         # ARCHITECTURE.md 模板（知识库架构模型）
│   ├── log.md                  # LOG.md 模板（全局工作日志）
│   ├── claude-template.md      # CLAUDE.md 完整模板（运行上下文）
│   ├── claude-kb-section.md    # CLAUDE.md 知识库章节（追加块）
│   ├── signals-readme.md       # signals/ README（signal schema）
│   ├── docs-readme.md          # docs/ README（doc schema）
│   ├── domains-readme.md       # domains/ README（domain schema + 模板）
│   ├── knowledge-setup.md      # 知识库引导搭建流程文档
│   └── result.md               # 执行结果模板（落盘于 .tribro/loops/<命名>/）
└── tests/
    └── tri-loop-full-testcases.md  # 全场景测试用例
```
