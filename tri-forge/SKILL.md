---
name: tri-forge
slug: tri-forge
version: 1.0.5
displayName: 技能锻造（tri-forge）
description: 内部专用工具 skill（不注册为 tri-intent 下游路由项，由用户直接调用）。用于「按家族硬规范生成 / 补全 / 审计一个 skill」：以 references/family-spec.md 为生成单一事实源，通过三模式（A 规范顾问·不落盘 / B 补全审计 / C 锻造生成·五门流程）产出或修复**合规的 skill 包**，并以 references/compliance-checklist.md 的 22 条硬约束在门④逐条自检，全过方可落盘；生成物若具备 tri-intent 下游身份，MUST 在门③同步回填路由映射表 / L3 子类 note / 下游依赖检测路径 / README 表，NEVER 只生成 skill 而不接通路由。同时承接家族的四点版本一致性校验（原 sync_registry.py 职能）。支持独立安装，含上游依赖检测三态逻辑（快照模式 / 引导安装 / 降级模式）。
summary: 三模式技能锻造工具（A 规范顾问 / B 补全审计 / C 锻造生成五门流程）+ 家族硬规范单源 + 22 条合规硬约束门④自检 + 门③路由回流强制 + 四点版本一致性校验 + 四平台安装。
tags: [skill-forge, compliance, family-spec, scaffolding, version-registry, internal-tool]
license: MIT
---

# 技能锻造（内部专用工具 · 三模式）

> 本 skill 是 tri-xxx 家族的**内部专用工具**，**不注册为 tri-intent 的下游路由项**——用户直接调用，不经意图识别。
> 用户心智：把 AI 当「家族规范的守门人与工匠」——你说「按家族规范造一个 skill」或「审计这个 skill 合不合规」，
> 它拿家族硬规范当尺子，缺什么补什么，造完先按 22 条硬约束自检，全过才交给你。

> **来源说明**：上游作者将此 skill 私有化（上游 `.gitignore` 显式排除 `tri-forge/`，平台亦未发布）。
> 本仓库为自维护 fork，依据仓库内 `tri-mece-audit/tri-mece-audit.html` 记录的规格自行重建
> （定位、职责边界、四分支触发、三模式、五门流程、门④ 22 条约束来源、自检句格式），
> 并以家族现有 skill 的实际形态为校准基准。

## 强制执行契约（Execution Contract · 最高优先级）

> 本节定义 skill「被激活后必须做什么」，优先级高于 Agent 的通用默认行为。**读取本文件即视为激活本工作流**，不得仅将其当作参考文档。

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（按 `references/version-check-spec.md` 契约执行，本仓库为自维护 fork，走本地一致性校验；不一致时按态处置）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：激活后 MUST 先判定本次**执行模式**（A 规范顾问 / B 补全审计 / C 锻造生成），再读取对应输入，NEVER 跳过判定直接动手。若本次来自 tri-intent 快照（兼容分支），MUST 先读取快照 §三；独立使用时 MUST 先走 §上游依赖检测 判定模式。
2. **单一事实源强制**：生成 / 补全 / 审计 skill MUST 以 `references/family-spec.md` 为**生成单一事实源**，以 `references/compliance-checklist.md` 的 **22 条硬约束**为**合规判定唯一标准**。NEVER 凭印象或自创标准替代。
3. **门④ 逐条自检强制**：C 模式下产物落盘前 MUST 逐条执行 22 条硬约束自检，**全部 PASS / N/A（须附理由）方可落盘**；任一条 FAIL → 回炉门② 修正，NEVER 带缺口交付。可执行实现见 `scripts/compliance_check.py`。
4. **门③ 路由回流强制**：生成物若**具备 tri-intent 下游身份**（认领 L2/L3 意图编码），MUST 在门③同步回填——路由映射表 / L3 子类 note / 下游依赖检测路径 / 家族计数 / README 相关表。**NEVER 只生成 skill 而不接通路由**。回填规则见 `references/tri-intent-integration.md`。
5. **跨真源交叉比对强制**：门④ 的「意图认领 MECE 不重叠」一条 MUST 以 `tri-intent/SKILL.md` 的**路由映射表**（路由真源）为比对基准，**不得**以 `family-spec.md` 内的路由副本为唯一依据。
6. **职责边界（NEVER 越界）**：本 skill 产出的是「**合规的 skill 包**」，不是业务代码、不是普通答复、不是内容成果物。不做纯咨询作答（本分支未包含，原 tri-ask）、不做常规编码开发（→ tri-coding）、不做缺陷修复（→ tri-fix）、不做非 skill 类蒸馏（→ tri-god，见 §职责边界）。A 模式**不落盘**，NEVER 借 A 模式之名写入任何文件。
7. **版本一致性校验（家族承接职能）**：本 skill 承接家族**四点版本一致性校验**（`SKILL.md` frontmatter / `CHANGELOG.md` 首条 / `_meta.json` / 平台注册表）的 `--check` 与 `--apply` 两模式。本仓库额外有 `README` 版本声明这第 5 处（见 `references/version-check-spec.md`）。检出漂移 MUST 报告；`--apply` 只回写可由规则化的位点，**CHANGELOG 首条属人工内容，NEVER 代写**。
8. **最小化原则**：只做 `任务要点` 或用户明确要求范围内的生成 / 补全 / 审计工作，NEVER 擅自扩展范围（如顺手重构无关 skill、批量改无关文件）。扩大范围须先向用户说明并确认。
9. **自检句**：每次响应前 MUST 声明「本次模式=&lt;A/B/C&gt;，触发分支=&lt;快照路由/直接触发/补全触发/顾问触发&gt;，已读取&lt;快照§三/family-spec/compliance-checklist/目标 skill&gt;，当前门=&lt;门①–门⑤ / 不适用&gt;」，若与上述规则冲突则停止并纠正。

## 触发时机

本 skill 为**内部专用工具**，激活由**触发分支**决定（四分支穷尽全部激活来源）：

| 触发分支 | 典型信号 | 判定的模式 |
|---|---|---|
| **快照路由（兼容分支）** | tri-intent 快照 `下游路由建议` 指向本 skill（历史遗留路径；新路由不指向本 skill） | 视快照 `任务要点` 判 A/B/C |
| **直接触发** | 「按家族规范生成一个 skill」「造一个 xxx skill」「补全这个 skill」「给这个 skill 按规范审一遍」 | C 或 B |
| **补全触发** | 已有 skill 包但缺文件/缺章节/缺依赖检测，要求按规范补上 | B 补全审计 |
| **顾问触发** | 「家族规范是什么」「生成一个合规 skill 要满足哪些约束」「这条约束怎么判」——只问不做 | A 规范顾问 |

**不由本 skill 处理**（命中以下信号 MUST 指向对应 skill，NEVER 在本工作流内代办）：

| 信号 | 归属 |
|---|---|
| 蒸馏「一个人的思维方式 / 一套工作流 / 一门专业技能」为 skill | tri-god（I21 蒸馏造物） |
| 写业务代码 / 实现功能 | tri-coding（I11） |
| 修 bug / 调试 | tri-fix（I12） |
| 审查**业务代码**质量 | tri-review（CR） |
| 生成普通内容 / 文章 / 翻译 | 本分支未包含（原 tri-content / tri-article / tri-translate） |
| 审 AI agent skill **安全性、可信性、可否安装**（供应链风险） | 本分支未包含（原 tri-guard） |
| 识别用户意图 / 路由 | tri-intent |

> **与 tri-god 的关键边界**：二者都以「产出 skill」为表象，判据是**依据什么生成**——
> tri-god 依据**蒸馏对象的素材**（人/流程/方法论的语料）产出新 skill；
> tri-forge 依据**家族硬规范**生成 / 补全 / 审计**合规的 skill 包**。
> 一句话：tri-god 造「内容」，tri-forge 保「合规」。

## 上游依赖检测（独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent 是否可用，据检测结果选择执行模式（**三态**）：

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟） | 读取快照 §三，按其 `任务要点` 判 A/B/C 后推进 |
| **B · 引导安装** | 未检测到 `tri-intent/`，或存在但无可用快照 | MUST 输出提示语引导安装，等待用户选择 |
| **C · 降级模式** | 用户明确拒绝安装 tri-intent | MUST 自构造等价输入（见下）并**显式声明降级**，再推进 |

**模式 B 提示语**：
> 本 skill 依赖上游 tri-intent 进行意图识别与输入校验（用于快照模式）。当前未检测到 tri-intent 或可用快照。
> 请安装：`python ops/install-skills.py --target <目标目录>`
> 安装后重新发起请求，即可获得完整的「意图识别 → 澄清 → 锻造」工作流。
> 若不便安装，可回复「降级执行」，我将基于自构造输入推进，但意图识别精度低于标准链路。

**模式 C 降级声明**（推进前 MUST 原样声明）：
> 未检测到 tri-intent 快照，已进入降级模式：本次基于自构造的等价输入执行，意图识别精度低于标准链路，
> 生成物的路由回填可能存在偏差，建议后续安装 tri-intent 以获得完整效果。

**模式 C 自构造等价输入**：从用户描述中提取「一句话复述 / 目标 skill 名与职责 / 是否为 tri-intent 下游 / 交付预期」，
写入交付物的「输入来源」区并标注 `degraded`。

> **对称双向检测**：tri-intent 侧的下游依赖检测会检查本 skill 是否存在（用于提示可委派）；
> 本 skill 侧检查 tri-intent 是否可用。任一端缺失都会被检测到。

## 输入契约

### 模式 A / B（顾问 / 补全审计）

| 输入 | 来源 | 用途 |
|---|---|---|
| 目标 skill 目录 | 用户指定路径（默认当前仓库内的 `tri-*`） | 审计 / 补全对象 |
| 审计范围 | 用户指定（全量 / 指定章节 / 指定约束条目） | 决定自检覆盖度 |
| 家族规范 | 本 skill 的 `references/family-spec.md`（只读） | 判定标准 |
| 合规清单 | 本 skill 的 `references/compliance-checklist.md`（只读） | 门④ 判据 |

### 模式 C（锻造生成）

| 输入 | 必填 | 说明 |
|---|---|---|
| skill 名与 slug | ✅ | `<category>-<name>`；须与现有 slug 不冲突 |
| 一句话职责 | ✅ | 该 skill 做什么、不做什么 |
| 是否为 tri-intent 下游 | ✅ | 决定门③ 是否需要路由回填；是则须给 L2 编码（或 L3 子意图） |
| 上游检测态数 | ✅ | 两态（咨询/表达/元操作型）或三态（须含降级声明） |
| 交付形态 | ⬜ | 默认 `SKILL.md + README.md + CHANGELOG.md + references/ + scripts/ + templates/ + tests/` |
| 落盘位置 | ⬜ | 默认仓库根 `<slug>/` |

> 必填项缺失且无法从快照 / 对话推断时，MUST 在门① 提出澄清，NEVER 凭默认值猜。

## 职责边界

- **本 skill 负责**：判定执行模式 → 依家族硬规范生成 / 补全 / 审计 skill 包 → 门④ 22 条合规自检 → 门③ 路由回流 → 交付；并承接家族四点版本一致性校验。
- **不负责**：意图识别（tri-intent）、业务代码（tri-coding）、缺陷修复（tri-fix）、业务代码审查（tri-review）、内容与多媒体产出（本分支未包含，原 tri-content / tri-article / tri-mm）、非 skill 类蒸馏（tri-god）、skill 安全审计（本分支未包含，原 tri-guard）。
- **与 tri-intent 的关系**：**不注册为下游**。本 skill 的产物若具备下游身份，由**本 skill 在门③主动回填** tri-intent——即本 skill 是「下游的制造者」，而不是下游之一。
- **产物归属**：本 skill 产出**合规的 skill 包**（可被独立安装、被路由、被检测）。产物落盘后即脱离本 skill 管辖，后续维护由维护者按家族规范进行。

## 核心能力方法论（三模式 · 可扩展）

> 三种模式共享同一套判据（`family-spec.md` + `compliance-checklist.md`），差别只在**是否落盘**与**深度**。

### 模式总览

| 模式 | 是否落盘 | 深度 | 适用 | 门的范围 |
|---|---|---|---|---|
| **A · 规范顾问** | ❌ 不落盘 | 只读 | 回答「家族规范是什么」「这条约束怎么判」 | 不适用（不产生产物） |
| **B · 补全审计** | ✅ 产出审计报告；补全产物视用户确认 | 逐条对照 22 条 | 已有 skill 包，按规范审计并补齐缺口 | 门① 范围确认 → 门②（可选：补全） → 门④ 自检 → 门⑤ 交付 |
| **C · 锻造生成** | ✅ 产出完整 skill 包 | 五门全流程 | 从零生成一个合规 skill | 门①→②→③→④→⑤ |

### 兜底处理（四类，NEVER 静默失败）

| 场景 | 处置 |
|---|---|
| **版本检查异常** | 自维护模式下版本声明不一致 → 标注漂移明细并**放行**（附修订动作）；脚本自身异常 → 兜底降级放行 |
| **门④ 自检不过** | 回炉门② 修正；同一约束连续 3 轮不过 → 停止自动回炉，向用户报告卡点并请求人工介入 |
| **上游缺失** | 降级模式 C（自构造等价输入 + 显式声明精度降低） |
| **安装评估不通过** | **不阻断交付**，但 MUST 记录原因到交付摘要（如目标目录不可写、slug 冲突） |

### 可扩展性

1. **新增硬约束**：仅在 `references/compliance-checklist.md` 追加一行（编号顺延），`scripts/compliance_check.py` 的判定逻辑自动覆盖
2. **新增模式**：在 §模式总览 追加一行，并在 §触发分支表 补上对应信号
3. **新增模板**：在 `templates/` 增文件，并在 `family-spec.md` §骨架清单 登记
4. **替换审计实现**：只要 `compliance_check.py` 的输入输出契约不变（读合规清单 → 输出逐条判定 JSON），可整体替换实现

## 版本检查与更新机制（强制技术约束 · 硬红线）

<!-- version-stub v1 · 瘦指针节点；细则唯一真源见 references/version-check-spec.md -->

> 任一执行入口启动后的**第零步**，先于核心执行阶段。细则唯一真源：`references/version-check-spec.md`；
> 可执行实现（逻辑唯一真源）：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、状态判定 MUST 由脚本完成；prompt 层 ONLY
> 「调用脚本 + 解析其 JSON 输出 + 按 `state` 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

```bash
python scripts/check_update.py --slug tri-forge --json
```

- 处置：按脚本输出放行或阻断（判据与 `block_code` 语义见真源）；NEVER 因版本门自身故障阻断 skill 启动。

**家族承接职能（四点版本一致性校验）**

除自身版本门外，本 skill 还承接**家族级**版本一致性校验（原 `sync_registry.py` 职能），两模式：

```bash
python scripts/check_registry.py --check     # 报告漂移，非零退出码表示存在不一致
python scripts/check_registry.py --apply     # 规则化回写可自动修正的位点（CHANGELOG 首条属人工内容，NEVER 代写）
```

校验位点见 `references/version-check-spec.md`（本仓库为 **5 处**：`SKILL.md` frontmatter /
`CHANGELOG.md` 首条 / `_meta.json` / 平台注册表 / `README.md` 版本声明）。

## 处理流程

> 三种模式共享同一套判据（`family-spec.md` + `compliance-checklist.md`），差别在**门数**与**是否落盘**；C 模式走完整五门，B 模式跳过门③。

### 五门流程（C 模式 · 完整链路）

```
门① 需求确认        ── 澄清 skill 名/slug/职责/是否下游/上游态数；向用户复述供确认
   │ 通过
门② 骨架生成        ── 依 family-spec 生成目录骨架与各文件初稿（SKILL.md 九章 + README + CHANGELOG + references/scripts/templates/tests）
   │ 通过
门③ 回流约束        ── 【强制】若为 tri-intent 下游：同步回填路由映射表 / L3 子类 note / 下游依赖检测路径 / 家族计数 / README 表；并确保 .tribro/ 落盘约定写入
   │ 通过
门④ 合规自检        ── 【门禁】逐条执行 22 条硬约束（scripts/compliance_check.py）；全部 PASS/N-A 方可继续；任一条 FAIL → 回炉门②
   │ 全过
门⑤ 落盘交付        ── 写入目标目录；产出交付摘要（产物清单 + 22 条自检结果 + 路由回填记录）
```

**门③ 与门④ 的顺序不可颠倒**：先接通路由，再自检合规——因为第 8 条「意图认领 MECE 不重叠」
需要比对**已回填后**的路由表，顺序颠倒会漏检路由冲突。

## 🔴 检查点与红灯清单（STOP · NEVER）

### 🔴 用户确认检查点（STOP）
- 🔴 **STOP**：门① 需求确认——澄清 skill 名/slug/职责/是否下游/上游态数并向用户复述供确认，未获用户确认 NEVER 进入门②。
- 🔴 **STOP**：门④ 合规自检——22 条硬约束逐条自检，任一条 FAIL 回炉门②，未全过 NEVER 落盘交付。
- 🔴 **STOP**：关键输入缺失——C 模式必填项缺失且无法从快照/对话推断时在门① 提出澄清，未获用户答复 NEVER 凭默认值猜。

### 🚫 红灯清单（NEVER）
- NEVER 只生成 skill 而不接通路由，具备下游身份 MUST 门③回填（§强制执行契约）
- NEVER 凭印象或自创标准替代 `family-spec.md` / `compliance-checklist.md` 判定（§强制执行契约）
- NEVER 借 A 模式之名写入任何文件（§强制执行契约）
- NEVER 擅自扩展范围（如顺手重构无关 skill、批量改无关文件）（§强制执行契约）
- NEVER 代写 CHANGELOG 首条（§强制执行契约）

## 交付产物

### 一、本 skill 直接产出

| 产物 | 文件名 | 内容 | 触发模式 |
|---|---|---|---|
| 规范顾问答复 | 不落盘 | 家族规范说明 / 单条约束的判定方法与示例 | A |
| 合规审计报告 | `reports/<slug>-compliance.md` | 22 条逐条判定（PASS/FAIL/N-A + 证据位置）+ 缺口清单 + 修订建议 | B |
| 锻造交付摘要 | `reports/<slug>-forge.md` | 产物清单 + 门④ 22 条自检结果 + 门③ 路由回填记录 + 安装评估 | C |
| 生成的 skill 包 | `<slug>/` | 见下「骨架清单」 | C |

### 二、生成的 skill 包骨架（C 模式产物）

```
<slug>/
├── SKILL.md          # 九章：强制执行契约 / 触发时机 / 上游依赖检测 / 输入契约 /
│                     #       职责边界 / 核心能力方法论 / 处理流程 / 交付产物 / 版本检查与更新机制
├── README.md         # 特性 / 安装 / 用法 / 目录结构 / 设计原则
├── CHANGELOG.md      # Keep a Changelog + SemVer，首条 = frontmatter version
├── _meta.json        # 安装元数据（ownerId / publishedAt / slug / version）
├── references/       # 静态参考资料（非流程逻辑）
│   └── version-check-spec.md   # 版本检查执行规范（内部化，满足第 22 条）
├── scripts/
│   └── check_update.py         # 版本门（与家族同源）
├── templates/        # 该 skill 的链路文档模板
└── tests/
    └── <slug>-full-testcases.md  # 全场景测试用例
```

> 骨架清单的**唯一事实源**是 `references/family-spec.md` §骨架清单；本表为速查，冲突时以 family-spec 为准。

### 三、落盘规则

- **本 skill 的审计报告 / 交付摘要**落 `.tribro/` 之外的 `reports/`（由调用方指定，默认仓库根 `reports/`）
- **生成的 skill 包**落用户指定目录（默认仓库根 `<slug>/`）——这是**实际技能产物**，不是 tri 链路文档
- 生成过程中若引用 tri-intent 快照，快照由 tri-intent 落于 `.tribro/snapshots/`，本 skill **只读不改**

## 目录结构

```
tri-forge/
├── SKILL.md                       主入口：三模式判定 + 五门流程 + 22 条门禁 + 路由回流
├── README.md                      特性/安装/用法/目录结构/设计原则
├── CHANGELOG.md                   版本变更记录
├── references/                    静态参考资料（非流程逻辑）
│   ├── family-spec.md             家族硬规范（生成单一事实源；含骨架清单与 12 条家族硬约束）
│   ├── compliance-checklist.md    22 条合规核对清单（12 家族 + 8 增强 + 1 安装 + 1 版本检查去重）
│   ├── version-check-spec.md      版本检查执行规范（内部化持有，满足硬约束第 22 条）
│   └── tri-intent-integration.md  门③ 下游同步回填规则（单一事实源）
├── scripts/                       可执行实现（确定性逻辑）
│   ├── check_update.py            版本门（与家族同源，自维护模式）
│   ├── check_registry.py          家族五点版本一致性校验（--check / --apply）
│   └── compliance_check.py        门④ 22 条硬约束自检（读合规清单 → 逐条判定 JSON）
├── templates/                     生成物模板
│   ├── skill-md.md                SKILL.md 九章骨架
│   ├── readme.md                  README.md 骨架
│   └── changelog.md               CHANGELOG.md 骨架（Keep a Changelog）
└── tests/
    ├── tri-forge-full-testcases.md  全场景测试用例（含 22 条硬约束自检用例）
    └── mutation-gate.py             门④ 负向测试（mutation testing，验证判据有牙）
```
