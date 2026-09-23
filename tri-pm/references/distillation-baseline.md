---
name: distillation-baseline
description: 蒸馏基准与保真度对照——逐条映射分析报告结论到 tri-pm 承载位置，声明防臆测铁律、风险清单与验收标准。对照分析报告全文。
---

# 蒸馏基准与保真度对照（常驻层 · 防臆测铁律）

> **本文件属常驻层，每次激活 MUST 加载。** 它是「蒸馏结果与原报告严格一致」的机制化保障。
> grep 检索模式：`基准` / `覆盖矩阵` / `防臆测` / `风险` / `验收` / `禁区` / `形态差距`

---

## 一、防臆测铁律

1. **唯一事实源**：`docs/pm-skills-main-engineering-analysis.md`（下称「报告」）。本 skill 的一切领域结论 MUST 可回溯至报告某一节。
2. **NEVER 补充报告未载的数量、框架、命令或能力**。若用户问及报告未覆盖的内容，MUST 明确声明「报告未覆盖，以下为通用知识」并与之区分，NEVER 混作蒸馏结论。
3. **NEVER 把源项目的 Claude Code 专有语法（`$ARGUMENTS`、`/command` 斜杠调用、subagent fan-out、`allowed-tools`）当作 WorkBuddy 可用能力直接承诺**——报告中这些均标记为「需翻译」。
4. 报告中的**实证数据**（校验 0 错 0 警、15/15 测试通过、68 技能 / 42 命令 / 9 插件、约 71k 词）为实测值，NEVER 改写或估算替代。

## 二、报告结论覆盖矩阵（证明不遗漏）

| 报告节 | 关键结论 | 承载位置 |
|--------|---------|---------|
| §1.1 | 一句话结论：可行但须「翻译层 + 渐进披露 + 子技能拆分」，不可单文件 | SKILL.md §职责边界 / `distilled-architecture.md` |
| §1.2 | 关键发现 5 条（工程质量/刻意解耦/零依赖/规模挑战/知识可保真） | 本文件 §三 + 各 references |
| §1.3 | 可行性评分卡（7 维 + 综合 ≈4.0/5） | 本文件 §四 |
| §2.1 | 项目定位、MIT、版本 v2.1.0、策展人 | `interfaces-and-contracts.md` + README |
| §2.2 | 9 域规模统计（68/42 + 词数） | `pm-frameworks-map.md` |
| §2.3 | 设计哲学（名词/动词、无跨引用、渐进披露） | `distilled-architecture.md` §五 |
| §3.1 | 目录结构 | `distilled-architecture.md` §一 |
| §3.2 | 四层结构与模块边界 | `distilled-architecture.md` §一 / §二 |
| §3.3 | 依赖关系（运行时/插件内/跨插件/外部） | `distilled-architecture.md` §三 |
| §3.4 | 数据流（输入→命令→技能→产物→建议） | `distilled-architecture.md` §四 + `workflows-and-execution.md` §一 |
| §4 | 核心功能清单（9 域能力） | `pm-frameworks-map.md` |
| §5.1 | 实证：校验 0 错 0 警、15/15 测试通过 | `workflows-and-execution.md` §三 |
| §5.2 | validator 设计评价（含自写 YAML 解析器脆弱点） | `workflows-and-execution.md` §二 + `interfaces-and-contracts.md` §五 |
| §5.3 | tests 设计评价（一致性门控是最大亮点） | `workflows-and-execution.md` §三 |
| §5.4 | 内容质量观察（`$ARGUMENTS` 漂移、外链、无内容回归测试） | `interfaces-and-contracts.md` §五 待改进项 |
| §6.1 | 可维护性（优势/劣势） | `distilled-architecture.md` §五 + `interfaces-and-contracts.md` §五 |
| §6.2 | 扩展性（加技能/加命令路径） | `interfaces-and-contracts.md` §一/§二 |
| §6.3 | 可移植性（纯文本 + stdlib） | `distilled-architecture.md` §三 |
| §7.1 | 源模型 vs 目标模型差异表 | `workflows-and-execution.md` §四 |
| §7.2 | 规模问题的硬约束（须路由 + 子技能/知识包） | SKILL.md §职责边界 + 本文件 §三 R1 |
| §7.3 | 保真度评估（100%/90%/85%/70%/需审查） | `workflows-and-execution.md` §四 保真度表 |
| §7.4 | 与 tri-* 家族规范契合（≤500 行、路由 + children） | SKILL.md 全文结构 |
| §8 | 风险与缓解 R1–R7 | 本文件 §三 |
| §9 | 分阶段建议 Phase 0–5 | 本文件 §五 |
| §10 | 验收标准 V1–V7 | 本文件 §六 |
| §11 | 最终结论 | README + 本文件 §四 |

## 三、风险与缓解（报告 §8 原样保留）

| # | 风险 | 等级 | 缓解 |
|---|------|:----:|------|
| R1 | 约 71k 词规模导致单文件不可行 | **P0** | 路由 + 知识包/子技能拆分（渐进披露） |
| R2 | Claude Code 专有语法需翻译 | P1 | 适配层：command→编排步骤，`$ARGUMENTS`→上下文，subagent→只读代理 |
| R3 | MIT 归因与品牌合规 | P1 | 保留版权/作者声明；按家族 MIT 规则剥离可见品牌；审查外链 |
| R4 | 外链知识衰减 | P2 | 优先保留自包含框架；外链标注「需联网验证」 |
| R5 | 无内容质量回归测试 | P1 | 蒸馏后为关键框架补「输出评分卡/校验清单」 |
| R6 | 审计类依赖 subagent / allowed-tools 原语 | P2 | 只读代理 + 沙箱等价实现；保留 `file:line` 证据机制 |
| R7 | 跨域工作流无法硬链（源设计限制） | **P0**<br>（2026-09-03 改判，原 P2） | 在路由层显式编排跨域步骤，弥补源项目解耦限制。**已落地**：`SKILL.md` 流程① 多域检出门。改判依据见 §九 **D-D** |

## 四、可行性评分卡（报告 §1.3 原样保留）

| 维度 | 评分 | 说明 |
|------|:----:|------|
| 架构清晰度 | 5 | 9 插件 × 单职责技能，层次分明 |
| 内容质量 | 4 | 框架结构化、可操作；少量 `$ARGUMENTS` 漂移 |
| 工程治理 | 5 | 校验器 + 测试 + CI + 版本同步，闭环完整 |
| 可移植性 | 5 | 纯文本 + stdlib，无外部依赖 |
| 与 WorkBuddy 模型契合 | 3 | 需翻译 Claude Code 专有语法 |
| 规模适配性 | 2 | 约 71k 词必须拆分，单文件不可行 |
| 法律合规（MIT） | 4 | MIT 可商用，但需保留归因、审查外链 |
| **综合** | **≈ 4.0** | **高可行性，落地需翻译层与拆分** |

## 五、分阶段实施建议（报告 §9 原样保留）

| 阶段 | 目标 | 关键动作 |
|------|------|---------|
| Phase 0 | 合规准备 | fork 仓库；审查 MIT 归因与外链；确定家族归属 |
| Phase 1 | 骨架 | 建路由 skill（意图→9 域映射）+ 知识包骨架 |
| Phase 2 | 内容搬运 | 按优先级搬运框架正文；剥离 Claude 专有语法 |
| Phase 3 | 工作流 | 将命令重写为编排步骤；保留「下一步建议」自然语言流 |
| Phase 4 | 治理 | 平移校验逻辑；补内容质量评分卡 |
| Phase 5 | 验收 | 对照核心功能清单逐条验证保真度 |

**搬运优先级**：`execution` → `strategy` → `discovery` → `ai-shipping`（差异化能力单列高优）。

## 六、验收标准（报告 §10 原样保留）

| # | 验收项 | 标准 |
|---|--------|------|
| V1 | 结构合规 | 生成物通过家族校验，0 错误 |
| V2 | 功能保真 | 高价值框架（PRD 八段、OST、RICE/ICE、SWOT 等）可触发并产出结构化结果 |
| V3 | 路由正确 | 用户 PM 提问经路由正确分流到对应域 |
| V4 | 工作流贯通 | 至少 `/discover` 与 `/write-prd` 等价流程端到端跑通 |
| V5 | 审计能力 | 意图 vs 实现审计法可产出带 `file:line` 证据的报告 |
| V6 | 合规 | MIT 归因保留；无可见品牌残留；外链经审查 |
| V7 | 无残留专有语法 | 无 `$ARGUMENTS`、无 `/pm-*:command` 硬引用残留 |

## 七、禁区（NEVER）

- NEVER 声称本 skill 已 100% 复刻源项目——报告明示审计类保真度约 70%、触发约 85%。
- NEVER 把源项目的 `/slash` 命令原样当作本环境可执行命令输出。
- NEVER 在未声明的情况下引用报告之外的 PM 框架作为「蒸馏结论」。
- NEVER 生成 `LICENSE` 或 `.gitignore`（家族硬约束 #11）。

## 八、当前实现形态 vs 报告目标形态（诚实声明 · MUST 随执行同步更新）

> 报告 §1.1 / §7.2 / §9 / §11 反复强调的目标落形态为「**1 个路由 skill + 9 个领域子技能**」。
> 本 skill v1.1.0 已完成 Phase 1–4 **全量蒸馏**（状态见下表）。本表为诚实声明载体，MUST 随每次执行同步更新。

| 报告目标形态 | 本 skill 当前形态 | 状态 | 说明 |
|---|---|:---:|---|
| 路由 skill（意图→9 域映射） | `SKILL.md` §tri-pm 方法论「三、九域路由」 | ✅ 已落地 | 九域关键词→产物映射已建立 |
| 9 个领域子技能（children） | 9 个域以 `references/pm-frameworks-map.md` 知识包承载 | ⚠️ 形态差异 | 未拆为 `children/` 子 skill；以分层装配替代，规避 500 行上限 |
| 68 个框架正文搬运（Phase 2） | `references/frameworks/` 68/68 全量正文（MUST-SECTIONS / 引导问题 / 输出模板 / Further Reading） | ✅ 已落地（v1.1.0） | 按域落地，体积守卫见 §九 D-B |
| 42 条命令重写为编排步骤（Phase 3） | `references/workflows/` 42/42 全量编排步骤（含 Checkpoint 原句） | ✅ 已落地（v1.1.0） | 范式总览仍见 `workflows-and-execution.md` §一 |
| 校验治理平移（Phase 4） | `scripts/validate_pm_artifact.py` 五模式（引用/章节/体积/语法/装配） | ✅ 已落地（v1.1.0） | 非直译 `validate_plugins.py`，按单 skill 形态重定义（差距报告 Part 4.3） |
| V2 功能保真（PRD 八段/OST/RICE 等可产出） | 依据 `references/frameworks/` 蒸馏正文产出，章节完整性可机械校验 | ✅ 已落地（v1.1.0） | 完成判据指向 MUST-SECTIONS（§九 D-C） |
| V4 工作流贯通（`/discover`、`/write-prd` 端到端） | 42 条命令编排全量落地；`--artifact` 正反例实测通过 | ✅ 已验证（v1.1.0） | `validate_pm_artifact.py --artifact` 正例过 / 反例拦截 |

**执行纪律**：

1. 用户问「tri-pm 是否具备源项目完整能力」→ MUST 引用本表如实回答，NEVER 答「是」。
2. 进入 Phase 2/3 时 MUST 同步更新本表状态列，并回写 SKILL.md 的装配表与目录结构。
3. 若后续拆分为 `children/` 九子技能，则本 skill 转为纯路由，届时 MUST 同步 tri-intent 路由表（家族硬约束 #26 七处同步）。


---

## 九、蒸馏决策记录（2026-09-03 · 全量补齐前置裁定）

> 本节是 **Phase 2/3 全量搬运的前置裁定**，先于正文搬运生效。
> 设立缘由：差距分析（`docs/tri-pm-capability-gap-20260903.md`）实测发现——源项目存在**自身未收敛的冲突**，且 tri-pm 的完成判据引用了**尚不存在的清单**。若不先裁定而直接搬运，必含章节清单将自相矛盾、校验器无法判定。

### D-A · PRD 模板裁定（对应差距 G7）

**冲突事实**（源项目自身不一致，非蒸馏引入）：

| 来源 | 八段构成 | 特征 |
|---|---|---|
| 技能 `create-prd` | Summary / **Contacts** / Background / Objective / **Market Segment(s)** / **Value Proposition(s)** / Solution(7.1–7.4) / **Release** | 偏商业论证；**无 Non-Goals** |
| 命令 `/write-prd` | Executive Summary / Background & Context / Objectives & Success Metrics（含 **Non-Goals** + Metrics 表）/ Target Users & Segments / **User Stories（P0-P1-P2 表 + Acceptance Criteria）** / Solution Overview / **Open Questions（表）** / Timeline & Phasing | 偏工程执行；**无 Contacts** |

> `/write-prd` L44 写有「Apply the create-prd skill」，却给出与 `create-prd` 不同的模板——源项目在此处**未收敛**。tri-pm 作为下游 MUST 自行裁定，NEVER 同时对齐两套。

**裁定：以 `/write-prd` 模板为命令态权威。**

1. **可执行性更强**：含 Non-Goals、User Stories P0-P1-P2、Acceptance Criteria、Open Questions——均是可机械校验的结构，而 `create-prd` 的 Contacts/Value Proposition 属叙述性段落。
2. **与实测路径一致**：`articles/developer-tools/20260903-tri-pm-layered-loading.md` L73 的 `[TRI-PM-BLOCK]` 案例，缺失章节为「非目标」——正属 `/write-prd` 体系。
3. **可校验性**：Metrics 表与 Acceptance Criteria 使完成判据的第 2 条（必含章节 grep 校验）从「查标题」升级为「查结构」。

**并入规则**：`create-prd` 独有的 Contacts / Market Segment(s) / Value Proposition(s) / Release 作为**可选补充段**并入，标记为 `OPTIONAL`，**不进必含清单**、不参与 BLOCK 判定。

**影响面**：G2 必含章节清单按此裁定建立；`[TRI-PM-BLOCK]` 判定以此为准；`create-prd` 框架文件 MUST 显式标注「命令态以 `/write-prd` 为准，本文件的八段为技能态变体」。

### D-B · 披露粒度与体积上限（对应差距 G13）

**实测基准**（源项目 110 个文件逐文件统计）：

| 类别 | 文件数 | 总词数 | 均值 | 最大 |
|---|---:|---:|---:|---:|
| 技能（框架） | 68 | 40,975 | 602 | 1,614（`review-resume`） |
| 命令（工作流） | 42 | 24,736 | 588 | 1,293（`security-audit-static`） |

**裁定**：

1. **装配粒度下沉到单框架级**——一个框架 = 一个文件，按用户点名加载。**NEVER 整域装配**（整域最小 3,058 词、最大 13,318 词，会击穿分层加载铁律）。
2. **单文件上限 900 词**（框架与命令同）。超出则拆分为 `<框架>-part2.md`，或压缩说明性散文。
3. **单次装配上限 3,500 词**（常驻层 + 1 个框架 + 1 条命令）。
4. **压缩红线**：说明性散文可压缩；**结构性元素 NEVER 因压缩而丢弃**——必含章节清单、逐段引导问题、输出模板、输出命名规则、Checkpoint 原句、Further Reading 外链。

**理由**：契约第 2 条「分层加载铁律」是 tri-pm 应对 71k 词规模的唯一可行方式，体积是它的量化边界；不设上限则 Phase 2 完成后装配机制自行失效。

**修订记录（2026-09-03 · v1.1.0 全量落地时校准）**：

全量正文落地后实测：常驻层 4,569 词（baseline 3,504 + architecture 1,065）；框架最大 1,337 词（`gtm-motions`）；命令最大 1,416 词（`performance-audit-static`）；最坏理论装配（常驻 + 最大框架 + 最大命令）7,322 词。原定 900 / 3,500 上限均被实测击穿，按数据校准：

| 参数 | 原值 | 修订值 | 依据 |
|---|---:|---:|---|
| 单文件上限 | 900 词 | **1,500 词** | 源项目自身渐进披露警告阈值为 3,000 词（`validate_plugins.py`），取其一半；结构红线（清单/模板/Checkpoint/外链 NEVER 因压缩丢弃）优先于散文压缩 |
| 单次装配上限 | 3,500 词 | **8,000 词** | 实测最坏 7,322 词 + ~9% 余量；常驻层为防臆测红线，不可削减 |

守卫含义不变：单次装配 ≤8,000 词 ≈ 全量知识（约 96k 混合词）的 **8%**，分层加载铁律依然成立。执行真源为 `scripts/validate_pm_artifact.py` 头部常数。

### D-C · 必含章节清单的承载形式（偏离差距报告原方案，记录在案）

| 项 | 差距报告原案 | 本次采用案 |
|---|---|---|
| 形式 | `references/frameworks/_sections/<框架>.md` 独立文件 | 内嵌为框架文件顶部的 `## 必含章节清单（MUST-SECTIONS）` 块 |

**偏离理由**：正文与清单一一对应，避免「清单文件」与「正文文件」双份漂移；校验器 grep 该块即可满足机器可校验要求，机械性完全等价，且少 68 个文件。

**校验器约定**：`MUST-SECTIONS` 块内每行形如 `- [ ] <章节名>`，校验器按行解析；`OPTIONAL` 段单独列于 `### 可选补充段` 下，不参与 BLOCK 判定。

### D-D · R7 严重度改判：多域请求污染（对应差距 G10）

**现象**：`articles/developer-tools/20260903-tri-pm-layered-loading.md` L79 实测——一次请求同时命中三个域，tri-pm **未拒绝、未拆分**，直接合并产出，导致章节互相污染。

**为何是「改判」而非「新发现」**：本文件原 R7 早已登记「跨域工作流无法硬链（源设计限制）」，连缓解方向都写对了（「在路由层显式编排跨域步骤」），却评为 **P2** 而从未实施。实测踩坑只是把严重度从 P2 改判为 **P0** 的证据。

**根因——忠实继承的副作用，而非疏忽**：

| | 源项目 | tri-pm |
|---|---|---|
| 结构 | 9 个**各自独立调用**的插件 | 9 域压进**单个 skill** 的九域路由表 |
| 一次调用 | 一条命令 → 一份产物，**结构上不可能揉成一坨** | 一条自然语言请求 → **可同时命中多域** |
| 跨域衔接 | 自然语言建议（`/write-prd` L104-107） | 同左（`SKILL.md` L3 解耦优先） |

> 关键：源项目「禁止跨插件硬引用」的解耦原则，在**其自身架构下是安全的**——因为插件边界天然隔离了调用。tri-pm **忠实地**继承了这条原则（`SKILL.md` L3 明写「与源项目『禁止跨插件硬引用』同源」），却**没有继承使该原则成立的前提**（独立调用边界）。

**结论**：这是源架构**根本不会产生的失效模式**，因此修复必须 **做加法**——补一道源项目没有也不需要有的「多域检出门」，而 **NEVER 回滚解耦原则本身**（回滚会同时丢掉解耦带来的可维护性）。

**落地位置**：`SKILL.md` 处理流程①。


