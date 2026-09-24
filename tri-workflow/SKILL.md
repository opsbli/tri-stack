---
name: 工作流设计引擎
slug: tri-workflow
version: 1.2.4
displayName: 工作流设计引擎
description: 企业级 AI 工作流设计 skill。读取 tri-intent 快照 §三，处理 I13（规划拆解）中工作流设计类意图，或独立使用接收用户需求描述，通过 7 阶段混合智能流水线（环境感知→模板匹配→对话补全→编译优化→校验验证→多目标输出→迭代反馈）产出可执行的工作流产物。支持 5 种交付形态：SKILL.md、设计文档、CI/CD 配置、审批流模板、DAG 配置。遵循 MECE 原则，支持独立安装，含上游依赖检测三态逻辑（快照模式/待识别模式/独立降级模式），独立使用完整闭环，作为下游 skill 不越界。
summary: 依据 tri-intent 快照或独立对话，通过 7 阶段混合智能流水线设计企业级工作流，产出多形态可执行产物。融合模板驱动、状态机校验、编译器多目标后端三种架构范式。
tags: [workflow, orchestration, pipeline, ci-cd, approval, automation, state-machine, dsl, enterprise]
license: MIT
---

# 工作流设计引擎（下游路由 · I13-I14 工作流设计子类）

> 本 skill 是 tri-intent 的下游执行 skill，依据快照 `snapshot.md` §三 结构化结论直接执行，不再重新识别意图。
> 用户心智：帮我设计一个工作流/流水线/审批流/自动化流程，期望获得可执行的工作流产物。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级；升级成功后继续，升级通道不可用则标注 D 态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：收到 tri-intent 快照且 `下游路由建议` 指向本 skill，MUST 先读取快照 §三，校验 `intent.L2_核心意图` ∈ {I13, I14}，NEVER 跳过校验直接执行。若 L2 越界 → 停止并回退 tri-intent 重新路由。独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式。
2. **7 阶段流水线强制推进**：MUST 按阶段 1→7 顺序推进，每阶段产出中间产物，NEVER 跳过阶段。阶段 1（环境感知）为强制前置，若环境扫描失败 → 降级为仅产出设计文档，并显式标注缺失能力。
3. **渐进式交付**：MUST 每阶段产出可独立交付的中间产物，用户可在任意阶段确认/调整/终止，NEVER 一步到位出最终产物不给中间确认机会。
4. **多形态输出**：MUST 根据 `工作流类型` 选择至少一种交付形态，NEVER 所有工作流只出一种格式。交付形态与工作流类型的映射见 §多目标输出后端。
5. **依赖校验硬阻断**：阶段 5 依赖校验若发现阻断项（缺失关键 Skill/API），MUST 停止并报告阻断原因，NEVER 产出无法执行的工作流。
6. **最小化原则**：仅实现快照 `任务要点` 或独立对话中用户明确要求的工作流范围，NEVER 擅自扩展工作流节点或增加未要求的交付形态。
7. **作答前声明**：用一句话声明「本次意图=<I13/I14>，已读取快照=<是/否>，模式=<快照/待识别/降级>，当前阶段=<1-7>」。

## 触发时机

- tri-intent 产出的快照中 `下游路由建议` 指向本 skill
- 意图编码范围：I13 规划拆解（工作流设计子类）、I14 操作执行（工作流编排子类）
- 独立使用时：用户明确要求设计工作流/流水线/审批流/自动化流程

## 上游依赖检测（三态 · 独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式（三态：A 快照模式 / A0 待识别 / B 独立降级）：

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟） | 读取快照 §三，按工作流推进（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | MUST 提示用户「本次请求尚未经意图识别」，引导先经 tri-intent 产出快照；NEVER 按空上下文静默执行 |
| **B · 独立降级模式** | 以上均不满足 | 跳过快照读取，直接从对话提取需求，阶段 1 环境感知降级为仅扫描本地 Skills 目录 |

> 模式 B 为降级模式：不依赖 tri-intent，直接从用户对话提取必填字段（见 §输入契约 模式 B）。
> 降级限制：无法获得 tri-intent 的意图校验和澄清门禁，阶段 1 环境感知仅扫描本地 Skills/MCP，无法提取组织约束（使用默认值）。
> 若用户需要完整的意图识别→澄清→执行体验，建议安装 tri-intent：`skillhub install tri-intent --dir <目标目录>`

## 输入契约

### 模式 A：下游执行（读取快照）

读取 `.tribro/snapshots/<命名>.md` 的 §三 结构化结论区：

| 字段 | 用途 |
|---|---|
| `intent.L2_核心意图` | 必须为 I13 或 I14，否则不应激活本 skill |
| `dimensions.D1_任务领域` | 决定工作流的专业域（编程/商业/办公等） |
| `dimensions.D5_确定性` | 决定是否需要多轮澄清 |
| `dimensions.D4_格式约束` | 输出格式要求 |
| `任务要点` | 工作流须覆盖的节点、约束与交付形态 |
| `交付预期` | 用户期望的最终工作流产物 |

### 模式 B：独立使用（对话输入）

直接从用户对话中提取以下必填信息，缺失时主动澄清：

| 必填字段 | 说明 | 示例 |
|---|---|---|
| 工作流类型 | 多步骤任务编排 / 协作流水线 / 业务审批流 / 数据处理流 | 协作流水线 |
| 业务领域 | 研发/运营/HR/财务/销售/通用 | 研发 |
| 触发方式 | 手动/定时/事件/Webhook | 事件（Git Push） |
| 核心节点 | 工作流包含的关键步骤列表 | 代码检查→构建→测试→部署 |
| 交付形态 | SKILL.md / 设计文档 / CI配置 / 审批模板 | CI配置 + 设计文档 |
| 技术栈约束 | 已有工具/平台限制 | GitHub Actions, 飞书审批 |

## 职责边界

- **本 skill 负责**：依据快照结论或独立对话，通过 7 阶段流水线设计工作流，产出可执行的多形态产物
- **不负责**：意图识别（由 tri-intent）、编码实现工作流节点内的具体逻辑（由 tri-coding）、调试修复（由 tri-fix）、内容生成（本分支未包含）
- **关键边界**：
  - 本 skill 产出**工作流设计**（流程定义 + 编排配置 + 节点映射），不产出节点内部的业务代码
  - 若工作流中某个节点需要新建 Skill，本 skill 产出该 Skill 的 SKILL.md 骨架，具体实现由 tri-coding 完成
  - 环境感知为只读扫描，不修改已有 Skill/配置
- **不触发场景（Not-Trigger）**：本 skill 不接手「节点内的具体业务逻辑编码实现」（转 tri-coding，本 skill 只产出流程定义与编排配置）；不接手「驱动一个真实项目走完流程的落地交付」（属 tri-sdlc，本 skill 产流程定义即交付）；不接手「单次带副作用的动作执行」（属 tri-action）；不接手「识别用户意图」（由 tri-intent / 自身快照驱动）。

---

## 核心架构：7 阶段混合智能流水线

> 7 阶段混合智能流水线架构图（含各阶段职责与关键产物 `env-profile.json` 等）见 `references/workflow-architecture.md`。核心设计原则见下。

### 设计原则

1. **编译器三段式映射**：前端（阶段 1-2）解析需求 → 中端（阶段 3-4）优化工作流 → 后端（阶段 5-6）校验与输出
2. **混合智能四阶段**：模板匹配(快) → 对话补充(灵) → 状态机校验(准) → 多目标输出(全)
3. **Terraform plan-apply 模式**：阶段 2-4 为 plan（设计预览），阶段 5 为校验，阶段 6 为 apply（生成产物），用户可在 plan 阶段确认/调整
4. **BPMN 五要素节点模型**：每个工作流节点含角色（谁执行）、动作（做什么）、输入（需要什么）、输出（产出什么）、SLA（多久完成）
5. **GitHub Actions 可复用市场**：Node Registry 积累高频节点，新工作流优先组合已有节点，缺失的从零设计

---


### 可扩展性

1. **新增工作流模板**：在 `templates/workflow-templates/` 建模板并在 §模板库 追加一行（适用场景 / 核心节点）——语义匹配自动纳入
2. **新增输出后端**：在 `templates/output-backends/` 建后端规范并在 §交付形态映射 追加行，多目标输出自动可达
3. **新增校验规则**：在 `validators/` 追加规则，阶段 5 自动执行；新增节点类型在 `schemas/` 扩展

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：`references/version-check-spec.md`。**可执行实现（single source of truth for logic）**：本 skill 自带 `scripts/check_update.py`（与 tri-intent 同源一致，按 `--slug` 自动适配）。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。修订规则只改真源一处，脚本与真源保持同步。

**执行方式（MUST）**

1. 任一执行入口启动后、核心执行前，运行脚本并取 JSON：
   ```bash
   python scripts/check_update.py --slug tri-workflow --json
   ```
   - 节流：结果持久化缓存（默认 1440 分钟 / 24h 仅校验一次），`--force` 强制重查，`--dry-run` 只判定不真升级。
   - 脚本自动定位 skill 目录（默认脚本上级目录），`--slug` 显式指定自身 slug（如上）。
2. 解析 JSON 的 `state` 字段，按态处置：
   - `A` 校验通过 / `B` 离线降级 / `C` 通道降级 / `D` 升级降级 → **一律放行**，进入后续阶段；并据 `warnings` / `notes` / `actions` 在交付物或日志标注对应口径（如「版本校验未完成（离线）」「版本陈旧·自动升级失败」）。
   - `BLOCK` → **绝对禁止执行**，按 `block_code`（P2/P3/P4）输出结构化恢复指引（手动命令见 `actions` 字段）。
3. 退出码语义（供 shell 编排）：`0`=A 放行；`10`=B；`11`=C；`12`=D；`20`=阻断。判定规则：`<20` 放行，`>=20` 阻断。脚本自身异常时兜底降级放行（退出码 11），NEVER 因版本门自身故障导致 skill 无法启动。

**执行要点**

1. **端点取自配置**：API 主机 MUST 读自 `~/.skillhub/metadata.json`，NEVER 硬编码域名。营销官网 `skillhub.cn` 与 API 主机 `api.skillhub.cn` 是两个站点——官网对任意路径都返回 `200 + HTML` 兜底页，绝不可作校验端点。读不到配置即判通道不可用。
2. **校验请求**：`GET {api_host}/api/v1/skills/{slug}`，超时 ≤ 5s，失败重试 1 次，会话内仅校验一次。
3. **最新版取值**：`latestVersion.version`，缺失时回退 `skill.tags.latest`。平台**不提供** `min_compatible` / `deprecated` / `checksum_sha256` / `signature`，NEVER 依赖这些字段。
4. **响应有效性**（三条件同时成立）：HTTP 200 **且** `Content-Type` 含 `application/json` **且** 能解析出版本字段。仅看状态码会被 SPA 兜底页击穿。
5. **版本比较**：按 [SemVer](https://semver.org/lang/zh-CN/) 逐段整数比较，NEVER 字符串比较。
6. **四态判定**：
   - **A 校验通过**（响应有效且 `current >= latest`）→ 放行。
   - **B 离线降级**（网络不可达）→ 标注「版本校验未完成（离线）」后以当前版本继续。
   - **C 通道降级**（可达但响应无效 / 404 / 405 / 读不到配置）→ 标注「版本校验未完成（通道不可用）」+ 输出通道异常告警后继续。
   - **D 升级降级**（陈旧且已真实尝试自动升级但未完成）→ 标注「版本陈旧·自动升级失败」+ 输出手动升级指引后继续。
   - 四态 NEVER 用于绕过「已检出陈旧却不尝试升级」——MUST 先真实执行一次自动升级，失败方可落 D 态。
7. **更新通道（自动执行）**：检出陈旧 MUST 自动执行 `skillhub upgrade <slug>` → `skillhub verify <slug>`，升级前备份、签名明确不一致则回滚。CLI 不在 PATH 时回退 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`；CLI 缺失或升级失败 → 落 D 态降级继续，NEVER 阻断。以 junction 指向源码树的 `source: local` skill 跳过自动更新，改为提示维护者手动同步。命令细则、CLI 定位顺序与已知陷阱见真源。
8. **阻断条件 P1–P4** 与四处版本同步点见真源。

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 核心执行。版本检查未通过前 NEVER 进入以下任一执行步骤。

### 阶段 1：环境感知（Environment Awareness）

> 强制前置。扫描运行环境中的所有可用能力，产出 `env-profile.json`。若扫描失败，降级为仅产出设计文档并显式标注缺失能力。

#### 1.1 扫描范围与产出

扫描五类能力并产出 `env-profile.json`：**Skills 目录**（列举 `skills/` 下 `SKILL.md`，提取 name/version/契约）、**MCP 服务**（server + tool schema）、**外部 API**（配置或对话提取端点）、**组织约束**（安全/合规/审批）、**技术栈**（CI/CD、审批、消息、编排平台）。缺失项按降级规则标注，不阻断流程。

> **完整 Schema 与扫描/降级规则**：详见 `schemas/env-profile.schema.md`（字段定义、Skills/MCP/API/组织约束/技术栈扫描规则、降级级别 `none/partial/full`）。

### 阶段 2：模板匹配（Template Matching）

> 从预置模板库中匹配最佳工作流模板，快速生成初版工作流模型。

#### 2.1 模板库

| 模板 ID | 模板名称 | 适用场景 | 核心节点 |
|---|---|---|---|
| `ci-cd-pipeline` | CI/CD 持续集成流水线 | 代码提交→自动构建→测试→部署 | 代码检出→静态检查→构建→单元测试→集成测试→部署→通知 |
| `code-review-flow` | 代码审查流水线 | PR 提交→自动审查→人工审查→合并 | PR 创建→自动审查→人工审查→CI 校验→合并→通知 |
| `approval-flow` | 业务审批流 | 申请→多级审批→执行→归档 | 发起申请→一级审批→二级审批→执行→通知→归档 |
| `data-pipeline` | 数据处理流水线 | 数据采集→清洗→转换→加载→报表 | 数据采集→质量校验→清洗→转换→聚合→加载→报表生成 |
| `release-flow` | 发布流水线 | 版本发布→灰度→全量→监控 | 版本打包→灰度发布→监控观察→全量发布→通知→回滚预案 |
| `multi-agent-orchestration` | 多 Agent 协作编排 | 多 Agent 并行/串行协作 | 任务分解→并行分发→结果聚合→冲突检测→最终输出 |
| `incident-response` | 故障响应流程 | 告警→诊断→修复→复盘 | 告警触发→影响评估→诊断定位→修复执行→验证→复盘报告 |

#### 2.2 匹配策略

1. 从用户需求/快照 `任务要点` 中提取关键词
2. 与模板库的 `适用场景` + `核心节点` 做语义匹配
3. 匹配度 ≥ 70% → 直接选用，进入阶段 3 对话补全
4. 匹配度 < 70% → 列出 Top 3 候选模板供用户选择，或选择「自定义」从零构建
5. 自定义模式：跳至阶段 3 对话补全，从零构建节点列表

#### 2.3 产出：workflow-model.json（初版）

模板匹配后产出初版工作流模型：含 `workflow_type` / `template_id` / `template_confidence` / `nodes[]`（id、type、action、role、inputs、outputs、sla、retry、depends_on）/ `edges[]` / `triggers`。

> **完整模型 Schema**：节点类型（auto/manual/approval/notification/condition/parallel/gateway）、字段定义、v1→v2→v3 演进规则，详见 `schemas/workflow-model.schema.md`。

### 阶段 3：对话补全（Dialogue Completion）

> 对阶段 2 产出的初版工作流模型，识别缺失信息并通过结构化提问补全。

#### 3.1 缺失信息检测

逐节点检查以下字段是否完整：

| 字段 | 检查规则 | 缺失时动作 |
|---|---|---|
| `action` | 不能为空 | 提问「节点 <name> 具体要做什么？」 |
| `role` | 自动节点必须映射到 env-profile 中的 skill/mcp/api | 提问「节点 <name> 由哪个工具/Skill 执行？」 |
| `inputs` | 自动节点必须明确输入数据来源 | 提问「节点 <name> 需要什么输入数据？」 |
| `sla` | 审批节点必须有时限 | 提问「节点 <name> 的预期完成时间？」 |
| `condition` | 条件分支边必须明确条件 | 提问「从 <from> 到 <to> 在什么条件下触发？」 |
| `retry` | 自动节点建议配置 | 使用默认值（重试 3 次，间隔 30s） |

#### 3.2 提问策略

- 每轮最多 3 个问题，避免对话疲劳
- 问题按优先级排序：阻断性缺失（无法执行）> 质量性缺失（影响可靠性）> 体验性缺失（影响可维护性）
- 提供默认建议值，用户可直接确认或修改
- 记录所有用户回答，回填到 workflow-model.json

#### 3.3 产出：workflow-model.json（完整版）

更新阶段 2 的工作流模型，所有必填字段完整。

### 阶段 4：编译优化（Compile & Optimize）

> 对完整工作流模型进行静态分析与优化，消除冗余、提升并行度、最小化依赖。

#### 4.1 优化规则

对完整工作流模型做静态优化：**冗余消除**（合并连续同类型自动节点）、**并行度提升**（无依赖节点标记并行）、**依赖最小化**（解除不必要串行）、**节点合并**（同角色相邻节点）、**超时注入**（默认 10min）、**重试注入**（默认 3 次）。

> **完整优化规则与示例**：详见 `schemas/workflow-model.schema.md` §模型演进规则（v2→v3 编译优化）。

#### 4.2 优化约束

- 不改变工作流的业务语义（审批顺序、数据流向不可变）
- 不合并人工节点与自动节点
- 优化后必须标注变更点，供用户审查

#### 4.3 产出：workflow-model.json（优化版）+ 优化变更日志

记录每条优化（`type` / `description` / `before` / `after`），供用户审查。

### 阶段 5：校验验证（Validation & Verification）

> 对照 env-profile.json 校验 workflow-model.json 的依赖完整性、状态机正确性、兼容性，必要时沙箱 dry-run。

#### 5.1 校验维度

对照 env-profile 校验 workflow-model，按 🔴 阻断 / 🟡 警告 分级，覆盖：依赖存在性、依赖版本兼容、权限充足性、死锁检测、不可达状态、循环依赖、数据流一致性、超时合理性、外部连通性。

> **完整校验规则与报告格式**：
> - **依赖校验**（8 规则：Skill/MCP/API 存在性、版本兼容、权限、平台兼容、循环依赖、数据流一致性）→ `validators/dependency-checker.md`
> - **可执行性验证**（8 规则：死锁/不可达/孤立节点/超时/重试/人工 SLA/关键路径/条件分支）→ `validators/executability-validator.md`

#### 5.2 阻断处理

- 🔴 阻断项：MUST 停止，生成阻断报告，列出缺失依赖及安装/配置命令
- 🟡 警告项：生成警告报告，用户可选择忽略或修正
- 所有阻断项解决后方可进入阶段 6

#### 5.3 沙箱 dry-run（可选）

- 若工作流类型为 `ci-cd-pipeline` 或 `data-pipeline`，建议在沙箱中 dry-run 关键路径
- Dry-run 失败 → 降级为 🟡 警告，标注风险

#### 5.4 产出

- `dependency-report.md`：依赖校验结果（通过/警告/阻断）
- `validation-report.md`：可执行性验证结果（通过/风险项/阻断项）

### 阶段 6：多目标输出（Multi-Target Output）

> 根据工作流类型和用户需求，生成一种或多种交付形态。

#### 6.1 交付形态映射

| 工作流类型 | 交付形态 | 优先级 | 输出文件 |
|---|---|---|---|
| 多步骤任务编排 | **SKILL.md** | P0 | `skills/<workflow-name>/SKILL.md` |
| 多步骤任务编排 | 设计文档 | P1 | `docs/<workflow-name>-design.md` |
| 协作流水线 | **CI/CD 配置** | P0 | `.github/workflows/<name>.yml` 或等价 |
| 协作流水线 | 设计文档 | P1 | `docs/<workflow-name>-design.md` |
| 业务审批流 | **审批流模板** | P0 | `approval/<name>-template.json` |
| 业务审批流 | 设计文档 | P1 | `docs/<workflow-name>-design.md` |
| 数据处理流 | **DAG 配置 + 执行脚本** | P0 | `pipelines/<name>-dag.yml` + `scripts/` |
| 数据处理流 | SKILL.md | P1 | `skills/<workflow-name>/SKILL.md` |
| 所有类型 | **工作流 DSL** | P2 | `workflows/<name>.wf.yml` |
| 所有类型 | 综合设计文档 | P2 | `docs/<workflow-name>-design.md` |

#### 6.2 各输出后端的生成规范

详见 `templates/output-backends/` 目录下的各后端规范文件：

| 后端 | 规范文件 | 核心要求 |
|---|---|---|
| SKILL.md 输出 | `skill-output.md` | 遵循 SKILL.md 标准格式，含 name/description/执行契约/工作流/质量标准 |
| 设计文档输出 | `design-doc-output.md` | 含背景/目标/节点设计/数据流/异常处理/部署说明 |
| CI 配置输出 | `ci-config-output.md` | 含平台检测/GitHub Actions 或 Jenkins 语法/环境变量/密钥管理 |
| 审批模板输出 | `approval-template-output.md` | 含审批节点定义/条件分支/通知配置/归档策略 |
| DAG 配置输出 | `dag-config-output.md` | 含平台检测/Airflow/Prefect/通用 YAML/任务依赖/条件分支转换 |

#### 6.3 产出的工作流 DSL（统一中间表示）

所有工作流在输出前，统一编译为声明式 DSL（`workflows/<name>.wf.yml`），作为可版本管理的单一事实来源。DSL Schema 定义见 `schemas/workflow-dsl.schema.md`。

### 阶段 7：迭代反馈（Feedback Loop）

> 工作流上线后，提供反馈收集与迭代优化机制。

#### 7.1 反馈渠道

- 在产出的设计文档末尾嵌入「反馈模板」，含：
  - 节点执行成功率
  - 平均耗时 vs SLA
  - 失败节点及原因
  - 优化建议

#### 7.2 迭代触发

- 用户反馈「节点 X 太慢/易出错」→ 重新进入阶段 4 编译优化，建议替代方案
- 用户反馈「新增节点 Y」→ 重新进入阶段 3 对话补全，追加节点
- 环境变化（新增 Skill/MCP）→ 重新进入阶段 1 环境感知，更新 env-profile

#### 7.3 版本管理

- 每次迭代产出新版本工作流，旧版本归档
- 版本号遵循 SemVer：`主版本.次版本.修订号`

#### 7.4 自动触发场景

> 除用户手动反馈外，支持以下自动触发机制，使工作流具备自我演进能力。

##### 7.4.1 Webhook 回调自动收集

- 在工作流设计文档中嵌入 Webhook 回调端点，供外部系统在执行完成后自动上报执行数据：
  - 回调 Payload：`{ workflow_id, node_id, status, duration, error, timestamp }`
  - 回调触发条件：`on_node_complete` / `on_node_fail` / `on_workflow_complete`
- 阶段 6 产出 CI/CD 配置时，自动注入 Webhook 回调步骤（如 GitHub Actions 的 `repository_dispatch`）
- 阶段 6 产出审批模板时，自动注入审批结果回调端点

##### 7.4.2 定时运行报告生成

- 若工作流触发类型为 `schedule` 或 `event`，在阶段 6 产出中附带定时报告生成配置：
  - 报告内容：节点执行成功率、P50/P95/P99 耗时、SLA 达标率、失败节点 TOP 5
  - 报告频率：每日/每周（由 `triggers.schedule` 派生）
  - 报告渠道：飞书消息卡片 / 邮件 / 文档链接
- 报告模板使用 `workflow-report` 预设格式，与阶段 6 的 `design-doc-output` 后端联动

##### 7.4.3 自动重入流水线

- 当 Webhook 回调或定时报告检测到以下条件时，自动触发重新进入流水线：
  - 任意节点 SLA 达标率 < 80%（连续 7 天）→ 重新进入阶段 4 编译优化
  - 新 Skill/MCP 在 env-profile 中注册 → 重新进入阶段 1 环境感知
  - 工作流版本落后当前模板版本 ≥ 1 个次版本 → 提示用户升级
- 重入行为默认为「建议模式」（生成优化建议但不自动修改），用户确认后切换为「自动模式」

---

## 交付产物

### 一、主产物（按工作流类型选择）

| 工作流类型 | 主产物 | 文件名 |
|---|---|---|
| 多步骤任务编排 | SKILL.md | `skills/<name>/SKILL.md` |
| 协作流水线 | CI/CD 配置 | `.github/workflows/<name>.yml` |
| 业务审批流 | 审批模板 | `approval/<name>-template.json` |
| 数据处理流 | DAG 配置 + 脚本 | `pipelines/<name>-dag.yml` |

### 二、辅助产物（所有类型通用）

| 产物 | 文件名 | 说明 |
|---|---|---|
| 工作流 DSL | `workflows/<name>.wf.yml` | 可版本管理的统一中间表示 |
| 综合设计文档 | `docs/<name>-design.md` | 含背景/节点/数据流/异常处理/部署说明 |
| 依赖校验报告 | `reports/<name>-dependency.md` | 阶段 5 产出 |
| 可执行性验证报告 | `reports/<name>-validation.md` | 阶段 5 产出 |

### 三、中间产物（阶段 1-4，供追溯）

| 产物 | 文件名 | 阶段 |
|---|---|---|
| 环境能力清单 | `reports/<name>-env-profile.yml` | 阶段 1 |
| 工作流模型（初版） | `reports/<name>-model-v1.yml` | 阶段 2 |
| 工作流模型（完整版） | `reports/<name>-model-v2.yml` | 阶段 3 |
| 工作流模型（优化版） | `reports/<name>-model-v3.yml` | 阶段 4 |
| 优化变更日志 | `reports/<name>-optimizations.yml` | 阶段 4 |

---

## 质量标准

| 维度 | 标准 | 验证方式 |
|---|---|---|
| 环境感知完整性 | 扫描 Skills/MCP/API/组织约束四项，缺失项标注 | 逐项核对 env-profile |
| 模板匹配准确度 | 匹配度 ≥ 70% 或提供 Top 3 候选 | 语义匹配得分 |
| 节点完整性 | 所有节点含 role/action/inputs/outputs/sla/retry | 字段完整性核对 |
| 依赖校验阻断 | 🔴 阻断项 = 0 方可进入阶段 6 | 阻断计数 |
| 死锁自由 | 状态机无可达死锁 | 状态机静态分析 |
| 循环自由 | DAG 无环（审批回退除外） | DAG 拓扑排序 |
| 多形态输出 | 至少产出 P0 级主产物 + 工作流 DSL | 文件存在性核对 |
| 最小化原则 | 不超出任务要点/用户需求范围 | 逐节点核对必要性 |
| 渐进式交付 | 每阶段有中间产物，用户可确认 | 阶段产物存在性核对 |

---

## 落盘规则

> 与 tri-intent（`.tribro/snapshots/`）、tri-action（`.tribro/actions/`）、tri-loop（`.tribro/loops/`）保持一致，tri-workflow 的链路文档落盘到 `.tribro/workflows/` 下。

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- **tri-workflow 执行结果**落盘于 `.tribro/workflows/<命名>/result.md`（若 `.tribro/` 目录不存在，MUST 先创建）
- **工作流产物**（SKILL.md / CI 配置 / 审批模板 / DAG 配置 / 设计文档）落盘于用户指定目录或默认业务目录——这些是实际工作流产物，不是 tri 链路文档
- **中间产物**（env-profile / workflow-model / 优化日志 / 校验报告）落盘于 `.tribro/workflows/<命名>/` 下，供追溯
- 执行结果落盘后不修改（审计完整性）；工作流产物可覆盖更新

### 执行结果落盘结构

```
.tribro/                    # 若不存在则先创建
├── snapshots/              # tri-intent 产出（已存在）
└── workflows/              # tri-workflow 链路文档
    └── <命名>/             # 命名同快照：<问题类型>_<日期>_<时间>_<会话ID>
        ├── result.md           # 执行结果（工作流摘要 + 产物清单 + 校验结果 + 引用）
        ├── env-profile.yml     # 阶段 1 产出（环境能力清单）
        ├── workflow-model.yml  # 阶段 4 产出（优化版工作流模型）
        └── validation-report.md # 阶段 5 产出（校验验证报告）
```

**result.md 结构**（落盘于 `.tribro/workflows/<命名>/`）：
- 工作流摘要（名称 + 类型 + 触发方式 + 核心节点数）
- 产物清单（各交付形态的文件路径列表）
- 模板匹配度 + 优化变更摘要
- 依赖校验结果（阻断项 + 警告项）
- 可执行性验证结果
- 引用（快照路径 + 产物路径）

---

## 目录结构

```
tri-workflow/
├── SKILL.md                              # 本文件
├── README.md                             # 特性/安装/用法/目录结构
├── CHANGELOG.md                          # 版本变更记录
├── references/
│   └── workflow-architecture.md          # 7 阶段混合智能流水线架构图（ASCII + 阶段职责速查）
├── tests/
│   └── tri-workflow-full-testcases.md    # 全场景测试用例（能力清单 + 真实用例）
├── templates/
│   ├── node-registry.md                  # 可复用节点注册表（Node Registry）
│   ├── workflow-templates/               # 预置工作流模板
│   │   ├── ci-cd-pipeline.md
│   │   ├── code-review-flow.md
│   │   ├── approval-flow.md
│   │   ├── data-pipeline.md
│   │   ├── release-flow.md
│   │   ├── multi-agent-orchestration.md
│   │   └── incident-response.md
│   └── output-backends/                  # 多目标输出后端规范
│       ├── skill-output.md
│       ├── design-doc-output.md
│       ├── ci-config-output.md
│       ├── approval-template-output.md
│       └── dag-config-output.md
├── schemas/
│   ├── env-profile.schema.md             # 环境感知 schema
│   ├── workflow-model.schema.md          # 工作流模型 schema
│   └── workflow-dsl.schema.md            # 工作流 DSL schema
└── validators/
    ├── dependency-checker.md             # 依赖校验规则
    └── executability-validator.md        # 可执行性验证规则
```

## 与 tri-intent 路由映射

> 本 skill 在 tri-intent 路由表中的位置：

| L2 意图 | 触发条件 | 路由 |
|---|---|---|
| I13 规划拆解 | `任务要点` 含工作流设计语义（流水线/审批流/自动化流程/编排） | → tri-workflow |
| I14 操作执行 | `任务要点` 含工作流编排语义（编排/串联/调度） | → tri-workflow |