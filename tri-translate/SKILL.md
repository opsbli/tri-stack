---
name: 完美翻译
slug: tri-translate
version: 1.1.2
displayName: 完美翻译
description: 横向方法论型 skill，为 tri-xxx 家族提供"意译优先 → 直译次之 → 不译兜底"三策略分层翻译能力；TRANSLATE_EXECUTE 模式执行深度翻译（含隔离区占位、术语表强制、MQM 质量自检），TRANSLATE_QUERY 模式查询术语译法，TRANSLATE_ADMIN 模式管理术语表/不译规则/风格示例；tri-content I08 委派或用户直接调用激活；支持独立安装，含上游依赖检测三态逻辑（快照模式/引导安装/降级模式）。
summary: 三策略分层（意译/直译/不译）+ 19 类不译规则集 + 三层术语表（A 不可译/B 批准/C 推荐）+ 隔离区占位法 + MQM Core 4 维质量自检 + Hallucination 子维幻觉检测。
tags: [tri, translate, i18n, glossary, mqm, free-translation, literal-translation]
license: MIT
---

# 完美翻译（横向 · 三策略分层）

> 本 skill 是 tri-xxx 家族的横向方法论型 skill，为全家族提供深度翻译能力作为服务。
> TRANSLATE_EXECUTE 读取快照 §三 上下文（若可用）+ 调用方入参；TRANSLATE_QUERY 读取术语表；TRANSLATE_ADMIN 管理术语表/不译规则/风格示例。不认领 L2 意图编码，不破坏家族 MECE 划分。
> 用户心智：让 AI 像专业译者一样翻译——意译优先传达意义，直译保信，路径代码专有名词保留原文，AI 还能自检翻译质量。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级；升级成功后继续，升级通道不可用则标注 D 态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：
   - TRANSLATE_EXECUTE 模式：MUST 先执行上下文收集（文档类型/目标读者/术语表/不译规则），再走隔离区提取，NEVER 跳过隔离区直接翻译。
   - TRANSLATE_QUERY 模式：MUST 先读取 `glossary.json`，NEVER 全文扫描规则文件。
   - TRANSLATE_ADMIN 模式：MUST 先校验操作合法性（增删术语/规则须 schema 通过）。
   - 独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式。
2. **隔离区占位法**：翻译前 MUST 用 19 类不译规则的正则模式扫描原文，提取所有不译要素（路径/代码/命令/URL/品牌名等）为占位符 `__<TYPE>_<N>__`；翻译过程 NEVER 翻译占位符；译后 MUST 还原所有占位符，残留则 NEVER 交付。
3. **三策略分层（铁律）**：
   - **意译优先**：MUST 据上下文+读者画像意译，传达原文意义而非逐字映射；意译 NEVER 偏离原文核心语义。
   - **直译次之**：触发退守条件（术语密集/命令上下文/法律精确性/数字版本号）MUST 退守直译；直译 MUST 仍符合中文表达习惯，NEVER 欧化生硬。
   - **不译兜底**：路径/代码/URL/API 端点/品牌名/商标/首字母缩写等 MUST 保留原文；专有名词按术语表 Priority A 处理（永不本地化）。
4. **术语表强制**：MUST 读取 `glossary.json` 并强制术语一致性——Priority A 不可译（永远保留原文），Priority B 必须用批准译法（屏蔽 block_synonyms），Priority C 推荐译法可上下文调整。
5. **质量自检（MQM Core 4 维 + Hallucination 子维）**：每段译文 MUST 自检——Accuracy（语义等价性）/ Fluency（中文通顺度）/ Terminology（术语一致性）/ Design（markup 保留度）/ Hallucination（无 AI 编造内容）；Accuracy+Design+Hallucination 的 Critical+Major 错误 MUST 0，否则 MUST 重译或退守直译。
6. **最小化原则**：MUST 只翻译 `任务要点` 范围内的内容，NEVER 添加未要求的额外解释、注释或脚注；若发现需扩大范围，MUST 向用户说明并确认。
7. **自检句**：每次操作前 MUST 声明「本次操作=<TRANSLATE_EXECUTE|TRANSLATE_QUERY|TRANSLATE_ADMIN>，触发源=<委派|显式>，已读取<快照§三|术语表|不译规则>，cache_key/段数=<...>」；与快照冲突时 MUST 停止并纠正，NEVER 擅自继续。

## 触发时机

本 skill 为横向方法论型，不认领单一 L2 编码，激活由**触发源**决定：

| 触发源 | 模式 | 激活条件 |
|--------|------|----------|
| tri-content I08 委派（复杂翻译场景） | TRANSLATE_EXECUTE | tri-content 判定需深度翻译，调用本 skill 的执行接口 |
| 用户直接调用翻译（"翻译这段"/"translate"） | TRANSLATE_EXECUTE | 用户发起翻译请求，含原文+目标语言 |
| 其它 skill 查询术语译法（"X 怎么译"） | TRANSLATE_QUERY | skill 发起术语查询 |
| 用户管理术语表/不译规则/风格示例 | TRANSLATE_ADMIN | 用户发起管理命令 |

> 注：tri-intent 快照下游路由建议**不指向**本 skill（本 skill 非下游执行 skill，I08 仍路由至 tri-content）。本 skill 通过 tri-content 委派或用户直接调用激活。

## 上游依赖检测（独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟） | 读取快照 §三 提取上下文（D1 任务领域 / D4 输出期望），增强翻译语境感知（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | 跳过快照上下文增强，按基础模式直接执行（声明「未加载快照上下文」） |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户明确拒绝安装 | 从用户请求自构造等价输入（任务领域=未指定，目标读者=未指定），声明降级精度低 |

**模式 B 提示语**：

> 本 skill 的上下文感知依赖上游 tri-intent 产出的快照元数据。当前未检测到 tri-intent。
> 请安装：`skillhub install tri-intent --dir <目标目录>`
> 安装后翻译可结合快照上下文（文档类型/读者画像）提升精度。若仅需基础翻译可进入降级模式。

**模式 C 降级声明**：

> 未检测到 tri-intent 快照，已进入降级模式：本次基于自构造的等价输入执行翻译（任务领域=未指定，目标读者=未指定），上下文语境感知精度低于标准链路，建议后续安装 tri-intent 以获得完整效果。

> **对称双向检测**：本 skill 检上游 tri-intent；tri-intent 亦可在快照路由后检测本 skill 是否存在以提示 tri-content 可委派。任一端缺失都被发现。

## 输入契约

### TRANSLATE_EXECUTE 模式输入

| 输入源 | 字段 | 用途 |
|--------|------|------|
| 调用方入参 | `source_text` | 待翻译原文 |
| 调用方入参 | `target_lang` | 目标语言（默认 zh-CN） |
| 调用方入参 | `context`（可选） | doc_type / audience / register / preserve_style / glossary_override |
| 快照 §三（若可用） | `dimensions.D1_任务领域` | 决定 register 与术语深度（技术/营销/UI/学术/对话/法律） |
| 快照 §三（若可用） | `dimensions.D4_输出期望` | 决定目标读者画像与篇幅 |
| 快照 §三（若可用） | `任务要点` | 翻译须满足的关键要求 |
| 内置资源 | `glossary.json` | 术语表（强制一致性） |
| 内置资源 | `never-translate.json` | 19 类不译规则集 |
| 内置资源 | `style-examples/*.md` | Few-shot 风格示例（可选） |

> 若澄清门状态=待澄清，TRANSLATE_EXECUTE 不应激活（待澄清的翻译请求缺乏明确目标）。

### TRANSLATE_QUERY 模式输入

| 输入源 | 字段 | 用途 |
|--------|------|------|
| 查询请求 | `term` | 待查询的术语/短语 |
| 查询请求 | `context`（可选） | 术语所在上下文（消歧义） |

### TRANSLATE_ADMIN 模式输入

| 输入源 | 字段 | 用途 |
|--------|------|------|
| 管理命令 | `command` | add/list/remove/import/export/test |
| 管理命令 | `target` | glossary / never-translate / style-examples |
| 管理命令 | `payload` | 操作数据（如术语条目） |

### 模式 C 降级输入

无快照输入；从用户原始请求自构造等价输入——任务领域=未指定，目标读者=未指定，register=按文档类型推断（默认 formal），术语表与不译规则仍加载（内置资源不依赖 tri-intent）。

## 职责边界

- **本 skill 负责**：执行深度翻译（三策略分层）；管理术语表与不译规则；提供术语译法查询；MQM 质量自检；不译要素隔离区占位保护。
- **不负责**：意图识别（由 tri-intent）；简单翻译/格式转换（由 tri-content I08 自处理）；咨询作答（由 tri-ask）；编码/调试（由 tri-coding）。
- **与 tri-content I08 的边界**：tri-content I08 处理轻量翻译与跨格式转换；本 skill 处理深度翻译（含代码路径保护、术语表强制、MQM 自检）。**委派决策由 `tri-content/SKILL.md` §职责边界 I08 行持有**（满足任一即委派本 skill：含代码块/路径/URL/API 等不译要素、有术语一致性硬要求、法律/医疗高保真场景、篇幅>2000 字或需 MQM 报告）；本 skill **不主动接管 I08**。产物上 `alignment.md`（本 skill）与 `对照表.md`（tri-content）二选一，NEVER 双份产出。
- **与 tri-cache 的边界**：tri-cache 是全家族缓存层；本 skill 可选启用翻译记忆（TM），但默认禁用。未来可扩展为 tri-cache 作为 TM 后端。
- **与 tri-evolve 的边界**：tri-evolve 可从用户对译文的反馈学习调整术语表 Priority C 推荐；本 skill 的 MQM 评分可作 tri-evolve 的进化信号。
- **MECE 边界**：本 skill 不认领任何 L2 意图编码，不破坏家族 21 个下游执行 skill（数量见 family-spec §1.3）的 MECE 划分；它是横切关注点（cross-cutting concern），同 tri-cache / tri-evolve 同属横向层。
- **不触发场景（Not-Trigger）**：本 skill 不接手「轻量翻译/跨格式转换」（属 tri-content I08 自处理，本 skill 只处理深度翻译）；不接管「已归 tri-content I08 的简单翻译」；不识别意图（由 tri-intent）；**不主动接管 I08 委派决策**（该决策由 `tri-content/SKILL.md` §职责边界持有）。

## 完美翻译（核心能力 · 可扩展）

> 完美翻译是 tri-translate 的核心能力。通过「三策略分层 + 19 类不译规则集 + 三层术语表 + 隔离区占位法 + MQM Core 质量自检」五件套，确保译文意译达旨、直译保信、不译要素原样保留、术语全文一致、质量可量化。这是 tri-translate 区别于其它家族 skill 的核心差异化能力。

### 核心理念

> **翻译不是逐字映射——意译传达意义，直译保信退守，不译保留原貌，质量自检兜底。**

三策略分层源自严复「信达雅」+ 奈达「功能对等」+ 李长栓「理解-表达-变通」+ 玄奘「五不翻」的古今融通。意译（达旨）对应表达阶段；直译（信）对应变通退守；不译（雅的边界）对应变通极限——技术场景的"不译"是玄奘"五不翻"的现代映射。

### 三策略分层

| 策略 | 触发场景 | 执行方式 | 退守条件 |
|------|----------|----------|----------|
| **① 意译优先** | 一般文本、解释性段落、营销文案、对话 | 据上下文+读者画像意译，传达原文意义而非逐字映射 | 术语密集 / 命令上下文 / 法律精确性 / 数字版本号 |
| **② 直译次之** | 术语密集、技术文档、法律条款、命令式语句 | 按字面直译但符合中文表达习惯，强制术语表 | 路径/代码/URL/品牌名/首字母缩写 |
| **③ 不译兜底** | 路径、代码块、命令、API、URL、品牌名、商标、首字母缩写 | 占位符保留原文，译后还原 | — |

### 19 类不译规则集

> 完整 19 类规则（路径/代码/命令/API/URL/域名/邮箱/配置键/环境变量/版本号/SHA/品牌名/商标/首字母缩写/技术标识符/数字单位/日期时间等）的正则模式与占位符映射详见 `references/no-translate-rules.md`，grep 模式：`grep -n "<类别>" references/no-translate-rules.md`。运行时载体为 `templates/never-translate.json`，二者保持一致；新增规则两处同步追加。

### 三层术语表（glossary.json）

| 优先级 | 处理 | 示例 |
|--------|------|------|
| **A · 不可译** | 永远保留原文，不进入翻译流程 | OpenAI / ChatGPT / GPT-4 / GitHub / npm |
| **B · 已批准** | MUST 用批准译法，屏蔽 block_synonyms | "agreement" → "协议"（屏蔽"合约"） |
| **C · 推荐** | 推荐使用，可上下文调整 | "deployment" → "部署" / "上线" |

术语条目字段：source / target / priority / context / block_synonyms / status / example / notes

### MQM Core 4 维 + Hallucination 子维质量自检

| 维度 | 标准 | 严重度 | 检测方式 |
|------|------|--------|----------|
| **Accuracy** | 译文与原文语义一致，无增删扭曲 | Critical/Major/Minor | 段落级原文对照核对 |
| **Fluency** | 符合中文表达习惯，无欧化、无病句 | Major/Minor | 中文语法 + 欧化检测 |
| **Terminology** | 术语全文统一，符合 glossary | Major/Minor | 术语表核对 + 全文扫描 |
| **Design** | 代码块/路径/URL/markup 原样保留 | Critical/Major | 占位符还原核对 + 结构扫描 |
| **Hallucination** | 无 AI 编造的原文没有的内容 | Critical | 原文不存在的内容检测 |

**质量门槛**：Accuracy+Design+Hallucination 的 Critical+Major 错误 MUST 0；Fluency/Terminology 允许 Minor（提示修正）。未达门槛 MUST 重译或退守直译，最多重试 2 次。

### 翻译策略矩阵（按场景）

| 场景 | 主策略 | 退守策略 | 不译要素 |
|------|--------|----------|----------|
| 技术文档（API/SDK） | 直译 | 意译（解释段） | 路径、代码、API、命令、版本号 |
| 营销文案 | 意译 | 直译（数据/承诺） | 品牌名、URL、商标 |
| UI 文案 | 意译（精简） | 直译（按钮/菜单术语） | UI key、变量名 |
| 学术论文 | 直译 | 意译（概念解释） | 公式、引用、首字母缩写 |
| 对话/聊天 | 意译 | 直译（事实陈述） | 人名、产品名 |
| 法律条款 | 直译 | 不译（条款编号） | 条款编号、专有名词、金额 |

### 可扩展性

> 新增翻译策略无需修改核心工作流：

1. **新增不译规则**：在 `never-translate.json` 追加一条规则（id/name/pattern/placeholder/description），隔离区提取自动按新规则扫描。
2. **新增术语条目**：在 `glossary.json.terms` 追加一条（source/target/priority/context/block_synonyms/status/example），三策略自动按新表强制。
3. **新增风格示例**：在 `templates/style-examples/` 追加 `.md` 文件（按场景命名，如 `marketing.md`），Few-shot 自动加载。
4. **新增质量维度**：在 MQM 自检表追加维度（如 Locale Convention），质量自检自动按新表评估。
5. **新增翻译场景**：在策略矩阵追加一行（场景/主策略/退守/不译要素），处理流程自动按新矩阵路由。


## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：`references/version-check-spec.md`。**可执行实现（single source of truth for logic）**：本 skill 自带 `scripts/check_update.py`（与 tri-intent 同源一致，按 `--slug` 自动适配）。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。修订规则只改真源一处，脚本与真源保持同步。

**执行方式（MUST）**

1. 任一执行入口启动后、核心执行前，运行脚本并取 JSON：
   ```bash
   python scripts/check_update.py --slug tri-translate --json
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

> 轻量工作流，无审批门；按模式分三支执行。

### TRANSLATE_EXECUTE 流程（深度翻译）

```
接收 {原文 + 目标语言 + 上下文}
        │
        ▼
  声明自检句 + 上下文收集（快照§三若可用 + 调用方入参 + 内置资源）
        │
        ▼
  隔离区提取（19 类不译规则扫描 → 占位符替换）
        │
        ▼
  策略① 意译优先（据上下文 + 风格示例）
        │
        ├─ 触发退守 ──→ 策略② 直译次之（术语表强制）
        │                  │
        │                  ├─ 触发退守 ──→ 策略③ 不译兜底（占位符保留）
        │                  │
        ▼                  ▼
  质量自检（MQM Core 4 维 + Hallucination）
        │
        ├─ Critical+Major 错误 ──→ 重译（最多 2 次）或退守直译
        │
        ▼
  占位符还原（验证残留 = 0）
        │
        ▼
  产物组装（译文 + 不译清单 + 原文对照 + 质量报告）
        │
        ▼
  交付
```

### TRANSLATE_QUERY 流程（术语查询）

```
接收 {term + context?}
        │
        ▼
  声明自检句 + 查 glossary.json
        │
        ▼
  匹配 source（精确 + 模糊）
        │
        ▼
  返回 {target + priority + source + status + example}
```

### TRANSLATE_ADMIN 流程（管理）

| 命令 | 行为 |
|------|------|
| `glossary add` | 添加术语（schema 校验通过后入表） |
| `glossary list` | 列出术语（按 priority/status 过滤） |
| `glossary remove` | 删除术语 |
| `glossary import` | 从 CSV/TBX 导入 |
| `glossary export` | 导出为 CSV/TBX |
| `never-translate add` | 添加不译规则 |
| `never-translate list` | 列出不译规则 |
| `never-translate remove` | 删除不译规则 |
| `style-examples add` | 添加风格示例 |
| `stats` | 翻译统计（条目数/平均 MQM/通过率） |
| `test --suite mqm` | 质量评估测试 |

## 交付产物

### 一、文件命名规范

沿用家族规范：`<问题类型>_<日期>_<时间>_<会话ID>`

- 示例：`TRANSLATE_20260801_143022_6a5c037d`

### 二、存放目录

```
.tribro/                    # 若不存在则先创建
├── snapshots/              tri-intent 产出（已存在）
│   └── <命名>.md
└── translate/              tri-translate 链路文档
    └── <命名>/
        ├── deliverable.md    # 译文（最终交付物）
        ├── preserved.md      # 不译清单（哪些被保留原文）
        ├── alignment.md      # 原文-译文段落级对照
        └── quality.md        # MQM 质量自检报告
```

### 三、产物清单

| 产物 | 文件名 | 内容 | 适用 |
|---|---|---|---|
| 译文 | `deliverable.md` | 三策略分层产出的最终译文 | 所有翻译 |
| 不译清单 | `preserved.md` | 列出所有保留原文的要素及类型 | 含不译要素时 |
| 原文对照 | `alignment.md` | 段落级原文-译文对照表 | 所有翻译 |
| 质量报告 | `quality.md` | MQM 4 维 + Hallucination 自检结果 | 所有翻译 |

### 四、产物结构规格

**deliverable.md 结构**：

```markdown
---
translation_id: <UUID>
source_lang: <源语言，如 en>
target_lang: <目标语言，如 zh-CN>
doc_type: <technical_doc|marketing|ui|academic|chat|legal>
audience: <developer|general|academic>
register: <formal|informal>
created_at: <ISO8601>
mqm_score: <0-100>
status: <pass|fail>
schema_version: 1
---

## 译文

<三策略分层产出的最终译文>
```

**preserved.md 结构**：

| 占位符 | 原文 | 类型 | 位置 |
|--------|------|------|------|
| `__URL_1__` | https://example.com | URL | 段落 2 |
| `__PATH_1__` | /usr/local/bin | 路径 | 段落 3 |

**alignment.md 结构**：

| 段落 | 原文 | 译文 | 策略 |
|------|------|------|------|
| 1 | Para 1... | 段 1... | 意译 |
| 2 | Para 2... | 段 2... | 直译 |

**quality.md 结构**：见 §3.5 / 4.3 的质量报告格式。

## 质量标准

| 质量维度 | 标准 | 验证方式 |
|---|---|---|
| 语义等价性（Accuracy） | 译文与原文语义一致，无增删扭曲 | 段落级原文对照核对 |
| 中文通顺度（Fluency） | 符合中文表达习惯，无欧化、无病句 | 中文语法 + 欧化检测 |
| 术语一致性（Terminology） | 术语全文统一，符合 glossary | 术语表核对 + 全文扫描 |
| markup 保留度（Design） | 代码块/路径/URL/markup 原样保留 | 占位符还原核对 + 结构扫描 |
| 幻觉检测（Hallucination） | 无 AI 编造的原文没有的内容 | 原文不存在的内容检测 |
| 占位符还原完整度 | 所有占位符 100% 还原 | regex 残留扫描 |
| 不译清单完整性 | 所有保留原文的要素都列出 | preserved.md 核对 |

## 落盘规则

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- 本 skill 链路文档落盘于 `.tribro/translate/<命名>/`（含 deliverable.md / preserved.md / alignment.md / quality.md，可覆盖更新）；`.tribro/` 不存在时 MUST 先创建
- 译文最终成果物默认落盘于 `.tribro/translate/<命名>/deliverable.md`（与链路文档同目录）；仅在用户显式指定目标文件时写用户指定路径，但 MUST 同时在 `.tribro/translate/<命名>/` 保留副本
- TRANSLATE_QUERY 返回为即时对话回应，不落盘
- 降级模式（模式 C）仍落盘链路文档，但 quality.md 标注"降级模式，精度低"

## 目录结构

```
tri-translate/
├── SKILL.md                          主入口：翻译契约 + 三策略 + 19 类不译规则 + MQM 自检
├── README.md                         特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      Keep a Changelog + SemVer
├── references/
│   └── no-translate-rules.md         19 类不译规则集正则模式（单一事实源，grep 检索）
├── schemas/
│   ├── glossary.schema.md            术语表 schema（三层优先级 + 字段定义）
│   └── never-translate.schema.md     不译规则集 schema（19 类 + 正则模式）
├── templates/
    ├── meta.json                     配置模板（默认语言/register/质量门槛/TM）
    ├── glossary.json                 默认术语表（含常见 Priority A 品牌名）
    ├── never-translate.json          默认不译规则集（19 类预置）
    ├── deliverable.md                译文模板
    ├── alignment.md                  原文对照表模板
    ├── quality.md                    MQM 质量报告模板
    └── style-examples/               风格示例（Few-shot）
        ├── technical-doc.md          技术文档风格示例
        └── marketing.md              营销文案风格示例
└── tests/
    └── tri-translate-full-testcases.md 全场景全能力测试用例（审计版）
```

### 运行时落盘结构（`.tribro/translate/`）

```
.tribro/translate/
└── <命名>/
    ├── deliverable.md                译文
    ├── preserved.md                  不译清单
    ├── alignment.md                  原文-译文对照
    └── quality.md                    MQM 质量报告
```
