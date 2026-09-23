---
name: 成本审计
slug: tri-cost
version: 1.3.0
displayName: 成本审计
description: 横向方法论型 skill，为 tri-xxx 家族提供 token 成本审计、主动优化与预算闸门能力——统计从用户提问到最终答案全过程每个关键节点的 token 消耗，逐节点评估「是否必要 / 是否可优化 / 改进建议」，产出成本审计报告；并主动执行蒸馏自 caveman 的 token 节省方法论（输出风格压缩 + 载荷类型感知摘要），产出前后 token 消耗对比与内容准确性对比；更以代码级强约束落地 token 预算闸门（per-node/session 限额 + 写入前自动优化 + 全链路核查 + S0–S4 风险分级 + BM25 上下文裁剪），确保 token 使用在流程中被自动校验与限制；COST_TRACK 模式节点 hook 取样并过预算闸门，COST_AUDIT 模式全链路汇总评估与预算核查，COST_OPTIMIZE 模式执行方法论并量化前后对比，COST_ADMIN 模式管理基线/阈值/模型单价/历史/预算；hook 或用户显式调用激活；支持独立安装，含上游依赖检测三态逻辑（快照模式/引导安装/降级模式）。
summary: 全链路八节点 token 分账 + 逐节点必要/可优化判定 + 主动节省方法论执行 + 前后 token/准确性对比 + 代码级预算闸门（自动校验与限制）——让每一笔 token 消耗有处可查、有据可评、有方可省、省得可量化、且被流程自动约束。
tags: [tri, cost, token, audit, optimization, efficiency, budget]
license: MIT
---

# token 成本审计方法论（横向 · 全链路分账）

> 本 skill 是 tri-xxx 家族的横向方法论型 skill，为全家族提供 token 成本观测、审计与优化能力作为服务。
> COST_TRACK 读取各关键节点入参并取样 token；COST_AUDIT 读取成本索引与快照 §三（若可用）汇总评估；COST_ADMIN 管理成本基线/阈值/模型单价/历史报告。不认领 L2 意图编码，不破坏家族 MECE 划分。
> 用户心智：让 AI 像"成本会计"一样工作——每一笔 token 消耗都记到具体节点，逐节点判断"这笔该不该花、能不能省、怎么省"，最终把省下来的钱转成更聪明的提问与更精简的 skill。

## 强制执行契约（Execution Contract · 最高优先级）

> 本契约优先级高于 Agent 通用默认行为。**触发源命中（cost-hook 触发、用户显式调用 COST_AUDIT / COST_TRACK / COST_ADMIN）即视为激活本工作流**，不得仅将其当作参考文档。

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（运行 `scripts/check_update.py`，按 `references/version-check-spec.md` 判定处置；非最新版自动升级，升级通道不可用则标注态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：
   - COST_TRACK 模式：MUST 先读取节点入参（`node_id` / `input_tokens` / `output_tokens` / `source_skill`），NEVER 缺字段直接写入。
   - COST_AUDIT 模式：MUST 先读取成本索引（`.tribro/cost/cost-index.jsonl`）与快照 §三（若可用），NEVER 全量猜测节点消耗。
   - COST_ADMIN 模式：MUST 先校验操作合法性（改基线/阈值/单价须 schema 通过）。
   - 独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式。
2. **全链路分账（铁律）**：每条成本记录 MUST 归属到具体关键节点（见 `references/cost-model.md` 八节点），NEVER 将节点消耗混记或归并到"总消耗"一笔带过。
3. **逐节点三问（铁律）**：COST_AUDIT 对每个节点 MUST 评估「是否必要 / 是否可优化 / 改进建议」三要素，NEVER 只报数字不给结论。
4. **高消耗必标**：单节点消耗 ≥ 全链路 20% 或超阈值，MUST 标记为高消耗节点并给出针对性建议（阈值判定逻辑见 `scripts/cost_eval.py`）。
5. **最小化原则**：MUST 只审计考核范围内的节点消耗，NEVER 掺入与本链路无关的 token 估算；多模型场景按模型单价分别分账。
6. **隐私过滤**：MUST 在写入前扫描节点内容的密钥模式（token / secret / api_key / sk- / AKIA / PRIVATE KEY），命中则脱敏为 `***REDACTED***`；敏感度过高（≥3 处）NEVER 记录节点原文。
7. **降本优先**：改进建议 MUST 给出可执行动作（精简提问 / 裁剪上下文 / 复用缓存 / 收敛工具调用等），NEVER 只给"建议降低 token"这类空话。
8. **自检句**：每次操作前 MUST 声明「本次操作=<COST_TRACK|COST_AUDIT|COST_OPTIMIZE|COST_ADMIN>，触发源=<hook|显式>，已读取<节点入参|成本索引|快照§三|成本基线|原始载荷>，节点数/记录数=<...>」；与快照冲突时 MUST 停止并纠正，NEVER 擅自继续。
9. **主动优化必出对比（COST_OPTIMIZE 铁律）**：COST_OPTIMIZE MUST 执行蒸馏方法论（detect → compress → count → accuracy → recovery），并 MUST 产出**前后 token 消耗对比**（before/after_tokens + saved_pct）与**内容准确性对比**（原子事实保留率 + 关键事实保障）；二者缺一视为优化未完成。MUST fail-closed：关键事实保留率不达标（安全关键类型 <90%）或命中安全/不可逆信号时，保留原文或显式告警，NEVER 伪造「零 token 收益」。
10. **预算闸门强约束（COST_BUDGET 铁律 · 代码级）**：token 使用 MUST 在流程中被**自动校验与限制**，不得仅停留于 md 约定。MUST 由 `scripts/token_budget.py` 落地：`COST_TRACK` 在节点内容落盘**前**调用 `enforce_node`，超 `node_caps` 的 N4/N5/N7/N8 内容 MUST 自动执行 token_optimize 压缩并校验前后 token 与内容准确性；超硬上限或关键事实保留率不达标 MUST 按 `hard_cap_policy` 处置（`block`→阻断并 fail-closed 保留原文 / `warn`→告警）；`COST_AUDIT` MUST 调用 `gate_index` 做全链路（per-node + session）预算核查并产出违规报告。S0–S4 风险分级与 BM25 上下文裁剪 MUST 由代码执行（见 `references/budget-spec.md`）。预算配置单一真源为 `_meta.json` 的 `budget` 段。

## 触发时机

本 skill 为横向方法论型，不认领单一 L2 编码，激活由**触发源**决定：

| 触发源 | 模式 | 激活条件 |
|--------|------|----------|
| cost-hook（各关键节点执行遂触发） | COST_TRACK | hook 传入 `{node_id, input/output_tokens, source_skill}` |
| 用户显式审计请求（「统计一下刚才花了多少 token」「这份回答贵不贵」） | COST_AUDIT | 用户发起全链路成本审计 |
| 用户显式审计请求（「这次执行分节点花多少」） | COST_AUDIT | 用户指定会话/链路审计 |
| 用户显式管理请求（stats/基线/阈值/单价/history/cleanup） | COST_ADMIN | 用户发起成本管理命令 |
| 主动节省 token（「帮我把这段输出/日志压缩一下」「按 caveman 方法省 token」） | COST_OPTIMIZE | 用户要求执行蒸馏方法论并出前后对比 |
| 降本增效复盘（「这批建议怎么落地」「沉淀优化经验」） | COST_OPTIMIZE + 门⑥沉淀 | 用户对历史报告/优化结果做复盘，闭环沉淀 |

> 注：tri-intent 快照下游路由建议**不指向**本 skill（本 skill 非下游执行 skill）。本 skill 通过 cost-hook 或显式请求独立激活。

## 上游依赖检测（独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟） | COST_AUDIT 读取快照 §三 提取链路上下文（D1 任务领域 / 下游 slug），增强节点分账与建议针对性（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | 跳过快照上下文增强，按基础链路分账直接执行（声明「未加载快照上下文」） |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户明确拒绝安装 | 从用户请求自构造等价输入（链路=通用标准八节点，domain=general），声明降级精度低 |

**模式 B 提示语**：

> 本 skill 的 COST_AUDIT 依赖上游 tri-intent 产出的快照上下文（任务领域 / 下游 slug）以增强节点分账精度。当前未检测到 tri-intent。
> 请安装：`skillhub install tri-intent --dir <目标目录>`
> 安装后审计可结合快照上下文（领域 / 下游 skill）提升建议针对性。若仅需基础链路分账可进入降级模式。

**模式 C 降级声明**：

> 未检测到 tri-intent 快照，已进入降级模式：本次基于通用标准八节点链路执行成本审计（domain=general，无快照上下文增强），节点分账与建议针对性低于标准链路，建议后续安装 tri-intent 以获得完整效果。

> **对称双向检测**：本 skill 检上游 tri-intent；tri-intent 亦可在快照路由后检测本 skill 是否存在以决定是否追加 cost-hook。任一端缺失都被发现。

## 输入契约

### COST_TRACK 模式输入

| 输入源 | 字段 | 用途 |
|--------|------|------|
| hook 入参 | `node_id` | 关键节点标识（N1–N8，见 `references/cost-model.md`） |
| hook 入参 | `input_tokens` / `output_tokens` | 该节点输入/输出 token 数 |
| hook 入参 | `source_skill` | 触发该节点的来源 skill |
| hook 入参 | `model`（可选） | 使用的模型（用于按单价分账） |
| hook 入参 | `session_id`（可选） | 会话标识（供按会话审计） |
| 配置模板 | `_meta.json` | 模型单价 / 阈值 / 基线 |
| 快照 §三（若可用） | `intent.L2_核心意图` / `下游 slug` | 写入成本记录元数据 |

> 若澄清门状态=待澄清，COST_TRACK 不应写入（待澄清内容的链路分账缺乏锚点）。

### COST_AUDIT 模式输入

| 输入源 | 字段 | 用途 |
|--------|------|------|
| 审计请求 | `session_id`（可选） | 指定会话审计（默认最近一次） |
| 审计请求 | `time_range`（可选） | 时间区间审计 |
| 审计请求 | `node_id`（可选） | 单节点聚焦审计 |
| 成本索引 | `cost-index.jsonl` | 全链路成本记录 |
| 快照 §三（若可用） | `D1_任务领域` / `下游 slug` | 分账上下文 + 建议针对性 |

### COST_ADMIN 模式输入

| 输入源 | 字段 | 用途 |
|--------|------|------|
| 管理命令 | `command` | stats / baseline / threshold / price / history / cleanup |
| 管理命令 | `target` | 模型单价 / 阈值 / 基线 / 历史报告 |
| 管理命令 | `payload` | 操作数据 |

### 模式 C 降级输入

无快照输入；COST_AUDIT 基于通用标准八节点链路 + 内置默认模型单价执行；COST_TRACK 接收裸节点入参直接写入。

## 职责边界

- **本 skill 负责**：观测并记录各关键节点 token 消耗；全链路汇总与逐节点评估（必要/可优化/建议）；产出成本审计报告与降本增效建议；**主动执行蒸馏自 caveman 的 token 节省方法论（输出风格压缩 + 载荷类型感知摘要，纯 Python 方法论层执行，见 `scripts/token_optimize.py`）**，并产出**前后 token 消耗对比**与**内容准确性对比**；管理成本基线/阈值/模型单价/历史报告。
- **不负责**：意图识别（由 tri-intent）；产出任何业务作答（由各下游执行 skill）；打包 caveman 运行时（Go 代理/引擎/SQLite CCR，其引擎为 BSL-1.1，方法可借鉴、源码不可再许可）—— 但其方法论层已由 `scripts/token_optimize.py` 落地执行，与审计能力互补。
- **与 tri-cache 的边界**：tri-cache 是"记忆层"（通过缓存复用省 token）；本 skill 是"账房层 + 节流执行层"（观测评估 token 花在哪、能否省，并主动执行方法论省 token、量化前后对比）。tri-cache 充当本 skill 的省 token 建议落地手段之一。
- **与 tri-evolve 的边界**：tri-evolve 从历史学习调整行为；本 skill 的成本审计报告与优化前后对比是 tri-evolve 的输入信号之一（哪类节点长期高消耗 / 哪类载荷优化收益最大 → 触发行为优化）。
- **与 tri-meta 的边界**：tri-meta 处理 M01–M04 元操作（澄清/纠偏/细化）；本 skill 是成本观测 + 优化层。用户问"这花了多少 token"归本 skill；用户问"你刚才什么意思"归 tri-meta。
- **与 caveman（外部开源 token 节省工具）的边界**：caveman 是**节流层**（主动省 token：输出风格压缩 + 输入/上下文压缩，依赖 Go 运行时）；本 skill 现已通过 `scripts/token_optimize.py` **主动执行** caveman 蒸馏出的方法论（输出风格压缩 + 13 类载荷感知摘要），并量化**前后 token 消耗对比**与**内容准确性对比**；二者互补非竞争——caveman 是"重型真压缩引擎"，本 skill 是"轻量方法论执行 + 观测账房"。本 skill 仅引用 caveman 的 MIT 方法、不打包其 BSL-1.1 运行时。
- **MECE 边界**：本 skill 不认领任何 L2 意图编码，不破坏家族下游 skill 的 MECE 划分；属横切关注点，同 tri-cache / tri-evolve / tri-translate / tri-true 同属横向层（横向清单见 family-spec §1.3）。
- **不触发场景（Not-Trigger）**：本 skill 不接手「意图识别」（转 tri-intent）；不接手「实际省 token 的改造落地」（属对应 skill / 用户执行，本 skill 只出审计结论）；不接手「记忆层缓存复用省 token」（属 tri-cache）；不接手「学习调优行为变更」（属 tri-evolve，本 skill 仅提供成本观测信号）。

## token 成本审计方法论（核心能力 · 可扩展）

> 成本审计方法论是 tri-cost 的核心能力。通过「全链路分账 + 逐节点三问 + 高消耗标记 + 降本闭环」四件套，确保每一笔 token 消耗有处可查、有据可评、有方可省。

### 核心理念

> **Cost 不是敌人，浪费才是——先看清每一笔 token 花在哪，再判断值不值，最后给出怎么省。**

### 关键节点划分（标准链路八节点）

> 完整节点定义、输入输出锚点、判定规则见 `references/cost-model.md`（grep 模式：节点 N1–N8）。概览：

| 节点 | 名称 | 典型消耗来源 |
|------|------|--------------|
| N1 | 用户提问输入 | 用户 prompt 编码 |
| N2 | 意图识别 | tri-intent 识别 + 快照字段 |
| N3 | 快照落盘 | 快照生成 |
| N4 | 下游读取快照 | 下游 skill 读取快照 §三 |
| N5 | 核心执行 / 工具调用 | 多轮推理 + 工具调用结果注入 |
| N6 | 推理思考 | CoT / 反思 token |
| N7 | 最终答案生成 | 回答输出 token |
| N8 | 输出 | 交付渲染 token |

### 逐节点三问评估（核心）

COST_AUDIT 对每个节点输出三要素：

1. **是否必要（necessity）**：该节点是否产生不可替代价值？
   - 高：产生最终答案不可替代的输入（如核心执行、答案生成）
   - 中：产生可复用/可裁剪的辅助价值（如意图识别、快照落盘）
   - 低：价值可被其它节点替代或可省略（如冗余推理、重复上下文注入）
2. **是否可优化（optimizability）**：是否存在省 token 空间？
   - 高：有明显省 token 空间（如长上下文反复注入、冗余工具重试）
   - 中：有部分优化空间（如可改用摘要 / 缓存）
   - 低：已较精简，空间有限
3. **改进建议（suggestion）**：给出具体可执行动作（见 `references/cost-model.md` 建议类型速查）。

### 成本估算与高消耗标记（确定性逻辑 → 脚本）

- **成本估算**：`cost = Σ(input_tokens + output_tokens) × 模型单价`（输入/输出单价可不同，见 `_meta.json`）。
- **高消耗标记**：单节点 `total_tokens` ≥ 全链路 20% 或 ≥ 阈值（默认 4000），标记 `high_cost=true`。
- **ROI 评分**：`roi = 价值注入度 / 归一化成本`，低 ROI 节点优先给优化建议。
- 聚合、估算、标记、评分实现见 `scripts/cost_eval.py`，用法：`python scripts/cost_eval.py --index .tribro/cost/cost-index.jsonl --report .tribro/cost/`。

### 降本增效建议类型速查

> 完整建议类型与触发条件见 `references/cost-model.md`（grep 模式：建议类型）。常见动作：

| 建议类型 | 动作示例 | 适用节点 |
|----------|----------|----------|
| 精简提问 | 收敛问题范围、去掉多余背景 | N1 |
| 裁剪上下文 | 只注入近 2 轮摘要而非全文 | N4 / N5 |
| 复用缓存 | 命中 tri-cache 历史作答 | N4 / N5 |
| 收敛工具调用 | 合并重复检索、减少无效调用 | N5 |
| 缩短推理 | 简单任务关闭 CoT 或限步数 | N6 |
| 摘要输出 | 交付用摘要替代全文 | N7 / N8 |
| 输出风格压缩 | 用 concise/terse 风格生成、删填充客套、保代码与错误串 | N7 / N8 |
| 载荷类型感知摘要 | 对 json/log/code/diff 等工具输出按类型摘要，保留错误/结构/变更行 | N4 / N5 |

> **方法底座**：上表后两行（输出风格压缩、载荷类型感知摘要）蒸馏自开源项目 caveman（JuliusBrussee/caveman, v2.7.0），其完整架构、13 类载荷分类法、fail-closed 设计与可蒸馏/不可蒸馏边界见 `references/caveman-distill.md`。caveman 是「节流层」（主动省 token），本 skill 是「账房层」（观测与评估）；二者互补非竞争（置信度：中；依据：推断 inferred；来源：基准报告 §10）。本 skill 仅把上述方法作为**建议动作**引用，不落地压缩、不打包 caveman 运行时。

### token 节省方法论参考（蒸馏自 caveman）

> 本小节为 `references/caveman-distill.md` 的入口与结论锚。caveman 与 tri-cost 的差异与优劣势、核心架构（skill 双结构 + proxy/engine）、关键模块职责、执行流程、依赖、重要接口（detect 13 类分类法 / fail-closed / recovery-handle / S0–S4 / BM25 打包）、可蒸馏与不可蒸馏边界，均严格依据 `docs/analysis-caveman-main-20260919.md`，不引入报告外臆测。

- **可直接借用的建议知识**：① 输出侧——强度档位（lite/full/ultra/wenyan）+ ASD-STE100 + Auto-Clarity 回退；② 输入侧——13 类载荷「如何读/如何摘要」规则（json/log/code/diff/search-result/text/html/terminal/tabular/config）；③ 设计纪律——fail-closed（不确定即原样保留）、recovery-handle（摘要标注原文可找回）、S0–S4 风险分级。
- **不可借用（需运行时）**：Go 代理二进制、SQLite CCR 字节恢复、确定性字节级压缩器、pixel 渲染、浏览器自动化、BM25/tokenizer 实现、BSL-1.1 引擎源码（方法可借鉴，源码不可打包进本 skill）。
- **方法论已落地执行**：上述可借用的「输出风格压缩 + 13 类载荷感知摘要」已由 `scripts/token_optimize.py` 落成确定性可执行逻辑（COST_OPTIMIZE 模式），主动执行并量化**前后 token 消耗对比**与**内容准确性对比**；详见本文件「token 节省方法论执行（COST_OPTIMIZE · active）」小节。
- **结论置信标注**：本小节引用的对比与可行性结论，其置信度与依据详见 `references/caveman-distill.md` 附录与基准报告附录；凡属推测（guess）者已标注低置信并提示需人工验证。

### 降本增效闭环（核心价值）

> COST_AUDIT 不只是出报告，而是闭环：报告 → 建议 → 落地 → 再审计。

1. 审计产出报告（分节点明细 + 逐节点三问 + 高消耗标记 + 改进建议）。
2. 用户 / 对应 skill 落地建议（精简提问、裁剪上下文、复用缓存等）。
3. 下次审计对比基线，验证 token 是否下降（`baseline` 对比）。
4. 长期高消耗节点作为 tri-evolve 的优化信号。

### token 节省方法论执行（COST_OPTIMIZE · active）

> 本小节把 `references/caveman-distill.md` 的方法论**落地为可执行动作**，使 tri-cost 从"只观测建议"升级为"主动执行 + 量化前后对比"。
> 确定性实现：`scripts/token_optimize.py`（纯 Python、零外部运行时）。用法：`python scripts/token_optimize.py --input <载荷文件> --type auto --intensity full --report <报告.json>`。

- **执行契约（6 步）**：`detect`（启发式识别载荷类型，严格遵循 caveman detect 顺序，fail-open 归 text）→ `compress`（按类型/强度做规则级摘要 + 输出风格压缩）→ `count`（前后 token 估算）→ `accuracy`（内容准确性：原子事实保留率 + 关键事实保障）→ `recovery`（recovery_handle，原文始终可从报告 `original_text` 找回）→ `report`（结构化前后对比）。
- **强度档位**（仅散文型生效）：`lite`（去填充/客套）/ `full`（默认，删冠词外填充、片段化、保代码与错误串）/ `off`（只做类型摘要、不压风格）。结构化载荷（json/diff/log/code/tabular/config）的压缩由类型级摘要完成，不叠加风格压缩以免破坏显著空白。
- **Auto-Clarity 回退**：命中安全/不可逆信号（警告/危险/不可逆/删除数据/密钥/rm -rf 等）时**不压风格**，保留常规表达并显式告警（fail-closed）。
- **fail-closed**：关键事实保留率不达标（安全关键类型 <90%）或命中安全信号时，保留原文或显式标注「未压缩」，绝不伪造「零 token 收益」。
- **前后对比产物**：COST_OPTIMIZE MUST 同时输出 (a) **token 消耗对比**——`before_tokens / after_tokens / saved_tokens / saved_pct`；(b) **内容准确性对比**——`retention_pct`（原子事实表面保真度）+ `critical_fact_retention_pct`（类型级关键事实保障）+ `dropped_facts_sample`（被丢弃事实样本，供人工核对）。
- **方法论来源标注**：token 节省方法蒸馏自 caveman（JuliusBrussee/caveman, v2.7.0）MIT 方法层；本脚本不打包其 BSL-1.1 引擎（置信度：中；依据：推断 inferred；来源：基准报告 §9 / caveman-distill §九）。

> **与 COST_AUDIT 的分工**：COST_AUDIT 观测"钱花在哪、该不该省"；COST_OPTIMIZE 实际"省下来并量化省了多少、丢没丢内容"。二者闭环：先用 COST_AUDIT 找到高消耗节点（如 N4/N5 工具输出冗长、N7/N8 输出啰嗦），再用 COST_OPTIMIZE 对对应载荷/输出执行方法论并出前后对比验证收益。

### token 预算闸门（COST_BUDGET · 代码级强约束）

> 本小节把基准报告 §9.1 提出的 token 节省方法论**落成代码级强约束**——不是 md 口头约定，而是可在流程中"自动校验与限制" token 使用的可执行闸门。
> 确定性实现：`scripts/token_budget.py`（纯 Python、零外部运行时，复用 `scripts/token_optimize.py` 的 detect/compress/count/accuracy/recovery）。完整 schema 与状态机见 `references/budget-spec.md`。

- **覆盖报告全部待优化点**：① 输出风格压缩、② 13 类载荷 detect、③ fail-closed、④ recovery-handle（已由 token_optimize 落地）；**⑤ BM25 令牌预算打包**（`pack_context`）、**⑥ S0–S4 风险分级**（`safety_class_of`）以及**流程级自动校验与限制**（`enforce_node` + `gate_index`）——均由本脚本代码化。
- **预算配置（唯一真源 `_meta.json` 的 `budget` 段）**：`node_caps`（per-node 限额）/ `session_cap`（会话限额）/ `auto_optimize_nodes`（写入前可自动压缩的节点，默认 N4/N5/N7/N8）/ `auto_optimize_intensity`（默认 full）/ `hard_cap_policy`（block 阻断 / warn 告警）/ `critical_retention_min`（0.90）/ `safety_critical_types`（log/diff/code/json）。缺省合并安全默认值，绝不因配置缺失而放行超预算内容。
- **`enforce_node`（写入前闸门）**：节点 content 估算 token > `node_caps` 时，自动优化节点 MUST 自动执行 token_optimize 压缩并校验前后 token 与关键事实保留率；压缩后仍超限或保留率不达标 → 按 `hard_cap_policy` 处置（block→阻断且 fail-closed 保留原文 / warn→告警）。输出 `PASS / OPTIMIZED / BLOCKED / WARN` 四态，`original_text` 始终随结果返回。
- **`gate_index`（全链路核查）**：COST_AUDIT 中调用，逐节点合计 vs `node_caps` + 逐会话合计 vs `session_cap`，产出违规报告（含 `over` 超出量），供审计报告列为超预算专项。
- **`pack_context`（报告⑤ BM25 裁剪）**：纯 Python Okapi BM25（k1=1.5, b=0.75）+ priority + 近因 + error_boost + pin_bonus 打分，贪心装袋至预算；含错误/钉住项强制保留（fail-closed），输出按原始时序重排。用于 N4/N5 注入上下文前裁剪历史。
- **`safety_class_of`（报告⑥ S0–S4 分级）**：log→S4（有损必须 recovery）、json/config/tabular→S2/S1、code/diff→S3、极小散文→S0、含错误信号的散文→S4。`enforce_node` 在压缩 S4 内容且保留率不达标时阻断/告警。
- **CLI 速查**：
  ```bash
  python scripts/token_budget.py --runsyntax                                   # 冒烟自检
  python scripts/token_budget.py --enforce-node --node N5 --content-file p.txt  # 单节点闸门
  python scripts/token_budget.py --gate --index .tribro/cost/cost-index.jsonl   # 全链路核查
  python scripts/token_budget.py --pack --items items.json --budget 4000 --query "修复登录"  # BM25 裁剪
  python scripts/token_budget.py --safety --text "<日志>" --type auto           # S0–S4 分级
  ```

### 可扩展性

> 新增成本观测无需修改核心工作流：

1. **新增关键节点**：在 `references/cost-model.md` 节点表追加（N9、N10…），COST_TRACK 按新节点取样，COST_AUDIT 自动分账。
2. **新增模型单价**：在 `_meta.json` 的 price 表追加（model/input_price/output_price），成本估算自动按新单价分账。
3. **调整阈值**：改 `_meta.json` 的 `high_cost_ratio` / `high_cost_tokens`，标记逻辑自动按新阈值。
4. **新增建议类型**：在 `references/cost-model.md` 建议类型速查追加（类型/动作/触发条件）。
5. **接入新落地手段**：如接入 tri-cache 复用 / tri-evolve 行为优化，作为建议的动作落点。

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：本 skill 内部 `references/version-check-spec.md`（不依赖任何外部上游 skill）。**可执行实现**：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。修订规则只改真源一处，脚本与真源保持同步。

**执行方式（MUST）**

1. 任一执行入口启动后、核心执行前，运行脚本并取 JSON：
   ```bash
   python scripts/check_update.py --slug tri-cost --json
   ```
   - 节流：24h 内仅校验一次，`--force` 强制重查，`--dry-run` 只判定不真升级。
   - 脚本自动定位 skill 目录（默认脚本上级目录），`--slug` 显式指定自身 slug。
2. 解析 JSON 的 `state` 字段，按态处置：
   - `A`/`B`/`C`/`D` → **一律放行**，进入后续阶段；据 `warnings`/`notes`/`actions` 在交付物或日志标注对应口径。
   - `BLOCK` → **绝对禁止执行**，按 `block_code` 输出结构化恢复指引。
3. 退出码语义：`<20` 放行，`>=20` 阻断。脚本自身异常时兜底降级放行，NEVER 因版本门自身故障阻断 skill 启动。

**执行细则**：四态判定、升级流程、版本比较算法、节流缓存均在 `references/version-check-spec.md`。本章节 NEVER 内联上述细则。发布前 MUST 通过 `python tri-forge/scripts/sync_registry.py --check`。

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 核心执行。版本检查未通过前 NEVER 进入以下任一执行步骤。

> 轻量工作流，无审批门；按模式分三支执行。

### COST_TRACK 流程（节点取样 · 被动写）

1. **接收**：cost-hook 传入 `{node_id, input_tokens, output_tokens, source_skill, model?, session_id?}`
2. **声明自检句**：「本次操作=COST_TRACK，触发源=hook，已读取节点入参，node=<N1–N8>」
3. **去重**：查 `cost-index.jsonl`，同 `session_id + node_id` 已存在 → 更新计数，不重复追加
4. **隐私过滤**：扫描节点内容密钥模式 → 命中脱敏或跳过
5. **预算闸门（强约束）**：调用 `token_budget.py enforce_node` 对节点 content 估算 token；超 `node_caps` 的自动优化节点（N4/N5/N7/N8）MUST 自动压缩并校验前后 token 与内容准确性，超硬上限或保留率不达标 → `BLOCKED`（fail-closed 保留原文，阻断无损放行）/`WARN`；落盘记录附预算 verdict（status/saved_tokens/safety_class）。见 `references/budget-spec.md`。
6. **成本估算**：`cost_eval.py` 按模型单价估算节点成本
7. **落盘**：追加一行到 `cost-index.jsonl` + 更新 `cost-index.db` 索引（含预算 verdict）
8. **返回**：写入确认（无需业务输出）

### COST_AUDIT 流程（全链路审计 · 主动产报告）

1. **接收**：审计请求 `{session_id?, time_range?, node_id?}`
2. **声明自检句**：「本次操作=COST_AUDIT，触发源=显式，已读取成本索引+快照§三，记录数=<待查>，节点=<N1–N8>」
3. **读取**：读 `cost-index.jsonl`（按条件过滤）+ 快照 §三（若可用）
4. **聚合**：`cost_eval.py` 分节点聚合 input/output/total/cost + 全链路合计
5. **标记**：`cost_eval.py` 高消耗标记 + ROI 评分 + 基线对比
6. **预算闸门核查（强约束）**：调用 `token_budget.py gate_index` 做全链路（per-node + session）预算核查，产出违规报告；超预算项列为高消耗/超预算专项
7. **逐节点三问**：对每个节点评估 必要/可优化/建议（结合 `cost-model.md` 建议类型）
8. **产物组装**：生成 `cost-report.md`（分节点明细 + 逐节点三问 + 高消耗标记 + 预算违规 + 改进建议 + 基线对比）
9. **交付**：输出报告 + 摘要结论（含降本增效建议 Top 建议）

### COST_ADMIN 流程（管理命令）

| 命令 | 行为 |
|------|------|
| `stats` | 返回成本索引统计（记录数/各节点合计/总成本） |
| `baseline set/list` | 设定/查看成本基线（对比基准） |
| `threshold set/list` | 调整高消耗标记阈值 |
| `price set/list` | 管理模型单价表 |
| `history` | 列出历史成本报告 |
| `cleanup` | 归档/清理过期成本记录 |

### COST_OPTIMIZE 流程（主动执行方法论 · 出前后对比）

1. **接收**：优化请求 `{text|input_file, type=auto|指定, intensity=full|lite|off}`
2. **声明自检句**：「本次操作=COST_OPTIMIZE，触发源=显式，已读取原始载荷，detected_type=<类型>」
3. **detect**：`token_optimize.py` 启发式识别载荷类型（13 类，fail-open 归 text）
4. **compress**：按类型/强度做规则级摘要 + 输出风格压缩；命中安全信号则 Auto-Clarity 回退（不压风格）
5. **count**：估算 before/after token，得 saved_tokens / saved_pct
6. **accuracy**：计算原子事实保留率 + 类型级关键事实保障；低于阈值或命中安全信号 → 保留原文或告警（fail-closed）
7. **recovery**：报告内含 `original_text` 与 `recovery_handle`，原文始终可找回
8. **产物组装**：生成 `COST_<命名>.md`（前后 token 对比表 + 内容准确性对比表 + 压缩文本 + 告警）
9. **交付**：输出压缩文本 + 前后对比结论（含 accuracy 与告警，供人工核对）

## 交付产物

### 一、文件命名规范

沿用家族规范：`<问题类型>_<日期>_<时间>_<会话ID>`（问题类型取 `COST`）。

### 二、存放目录

```
.tribro/                    # 若不存在则先创建
├── snapshots/              tri-intent 产出（已存在，本 skill 只读）
└── cost/                   tri-cost 链路产物
    ├── cost-index.db       SQLite 成本记录主索引（WAL）
    ├── cost-index.jsonl    JSONL 增量日志（容灾）
    ├── meta.json           配置（模型单价/阈值/基线）
    └── <命名>/
        ├── cost-report.md  成本审计报告（最终交付物）
        └── baseline.json   基线快照
```

### 三、产物清单

| 产物 | 文件名 | 内容 | 审批门 |
|---|---|---|---|
| 成本索引 | `cost-index.db` + `cost-index.jsonl` | 全链路分节点成本记录（双轨容灾） | 无（自动写） |
| 成本报告 | `cost-report.md` | 分节点明细 + 逐节点三问 + 高消耗标记 + 改进建议 + 基线对比 | COST_AUDIT |
| 基线快照 | `baseline.json` | 某次审计的成本基线（供下次对比） | COST_ADMIN |

### 四、cost-report.md 结构

```markdown
---
audit_id: <UUID>
mode: <COST_AUDIT>
upstream_mode: <A_snapshot|A0_pending|B_install|C_degraded>
session_id: <会话ID>
total_input_tokens: <N>
total_output_tokens: <N>
total_tokens: <N>
estimated_cost: <金额>
baseline_delta: <较基线变化% 或 null>
created_at: <ISO8601>
schema_version: 1
---

## 审计结论

<全链路总成本 + 高消耗节点 + Top 降本建议 + 基线对比结论>

## 分节点明细

| 节点 | 名称 | 输入 | 输出 | 合计 | 占比 | 估算成本 | 必要性 | 可优化 | 建议 |
|---|---|---|---|---|---|---|---|---|---|
| N1 | 用户提问输入 | … | … | … | … | … | 高 | 中 | 精简提问 |

## 高消耗节点

<列出 high_cost 节点 + 针对性建议>

## 降本增效建议

<Top 建议，按 ROI 排序，各含落地动作>
```

### 五、COST 前后对比报告结构（COST_OPTIMIZE）

> 命名沿用家族规范：`<问题类型>_<日期>_<时间>_<会话ID>`，问题类型取 `COST`。

```markdown
---
optimize_id: <UUID>
mode: <COST_OPTIMIZE>
detected_type: <json|log|code|diff|text|...>
intensity: <lite|full|off>
style_applied: <true|false>
methodology_source: 蒸馏自 caveman (v2.7.0) MIT 方法层
created_at: <ISO8601>
schema_version: 1
---

## 前后 token 消耗对比

| 指标 | 优化前 | 优化后 | 节省 |
|---|---|---|---|
| tokens | <before_tokens> | <after_tokens> | <saved_tokens> (<saved_pct>%) |

## 内容准确性对比

| 指标 | 数值 |
|---|---|
| 原子事实保留率（表面保真度） | <retention_pct>% |
| 关键事实保障率（类型级重要事实） | <critical_fact_retention_pct>% |
| 被丢弃事实样本 | <dropped_facts_sample> |

## 压缩结果

<compressed_text>

## 告警

<warnings：Auto-Clarity 回退 / 关键事实保留率不达标 等；无则填「无」>

## 原文（fail-closed 可找回）

<original_text 或 recovery_handle 指向的原始文件>
```

## 质量标准

| 质量维度 | 标准 | 验证方式 |
|---|---|---|
| 分账完整性 | 每条记录归属具体节点，无"总消耗"一笔带过 | 逐条 node_id 校验 |
| 逐节点三问 | 每个节点含 必要/可优化/建议 三要素 | 报告字段核对 |
| 高消耗标记 | 超阈值节点均被标记且给出建议 | 阈值逻辑校验 |
| 成本估算 | 按模型单价正确分账（输入/输出单价可区） | price 表核对 |
| 基线对比 | 报告含 baseline_delta（或显式 null） | 字段校验 |
| 隐私安全 | 密钥模式命中即脱敏，节点原文不可见敏感信息 | 正则扫描成本记录 |
| 索引一致性 | cost-index.db 与 cost-index.jsonl 可双向重建，零丢失 | rebuild 校验 |
| 建议可执行 | 改进建议含具体动作，无"建议降低 token"空话 | 建议质量评审 |

## 落盘规则

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- 本 skill 成本产物落盘于 `.tribro/cost/`（含 cost-index.db / cost-index.jsonl / meta.json，可覆盖更新）
- 成本报告落盘于 `.tribro/cost/<命名>/cost-report.md`（最终交付物）
- 基线快照落盘于 `.tribro/cost/<命名>/baseline.json`
- COST_TRACK 为被动写，返回即时确认，不额外落业务报告
- 降级模式（模式 C）仍落盘成本记录，但报告标注"降级模式，建议精度低"

## 目录结构

```
tri-cost/
├── SKILL.md                          主入口：成本审计契约 + 全链路分账 + 逐节点三问 + 降本闭环
├── README.md                         特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      Keep a Changelog + SemVer
├── _meta.json                        平台元数据 + 模型单价/阈值/基线配置
├── references/
│   ├── cost-model.md                 节点划分/评估维度/建议类型速查（单一事实源，grep 检索）
│   ├── caveman-distill.md            蒸馏自 caveman 的 token 节省方法论（架构/模块/流程/对比/13类载荷摘要/输出风格规则，方法底座）
│   ├── budget-spec.md               token 预算闸门规范（COST_BUDGET：schema + enforce_node/gate_index/pack_context/safety_class 状态机，代码级强约束）
│   └── version-check-spec.md         版本检查与更新规范（内部唯一真源）
├── scripts/
│   ├── cost_eval.py                  token 聚合/成本估算/高消耗标记/ROI 评分（确定性逻辑）
│   ├── token_optimize.py             主动 token 节省方法论执行器（detect/compress/count/accuracy/recovery 前后对比，蒸馏自 caveman）
│   ├── token_budget.py              token 预算闸门与自动优化执行器（enforce_node 写入前闸门 / gate_index 全链路核查 / pack_context BM25 裁剪 / safety_class S0–S4，代码级强约束）
│   └── check_update.py               版本检查与更新（家族同源）
└── tests/
    └── tri-cost-full-testcases.md    全场景全能力测试用例（审计版）
```

### 运行时落盘结构（`.tribro/cost/`）

```
.tribro/cost/
├── cost-index.db            SQLite 成本索引（WAL）
├── cost-index.jsonl         JSONL 增量日志（容灾）
├── meta.json                配置（模型单价/阈值/基线）
└── <命名>/
    ├── cost-report.md       成本审计报告
    └── baseline.json        基线快照
```

## 进化契约

> 本 skill 生成物 MUST 自带进化契约（compliance #23）——本 skill 如何接收反馈、沉淀经验、自我修订：

- **反馈接收点**：用户或调用方通过 `COST_ADMIN` 提交改进建议，或在本 skill 报告评审时提出；改进建议写入 `.tribro/cost/feedback/`。
- **经验沉淀位**：每次审计暴露的降本教训、建议落地效果写入 `.tribro/cost/lessons.md`；规范/节点/建议类型的修订回写 `references/cost-model.md`。
- **自我修订触发条件**：当连续 ≥3 次审计同一节点高消耗且建议未落地，触发本 skill 修订自身节点划分或建议类型；当模型单价表失效（成本估算偏差 >20%）触发修订 `_meta.json` 单价。
- **降本增效闭环归属**：本 skill 负责"观测与建议"，实际落地由用户/对应 skill 执行；tri-evolve 可作为长期行为优化出口。