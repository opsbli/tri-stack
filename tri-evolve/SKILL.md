---
name: tri-evolve
slug: tri-evolve
version: 1.1.9
displayName: tri-evolve
description: 横向学习/进化型 skill，为 tri-xxx 家族提供多渠道信号驱动的持续改进与用户画像构建能力；EVOLVE_OBSERVE 模式采集作答后信号，EVOLVE_LEARN 模式批量归因学习，EVOLVE_APPLY 模式向下游 skill 提供画像与经验复用；hook/定时/请求激活；支持独立安装，含上游依赖检测三态逻辑（完整模式/引导安装/降级模式）。
summary: OODA 进化闭环（观察-归因-提议-验证-沉淀）+ 经验条目库（embedding 检索复用）+ 用户画像（静态/动态分层+时间衰减）+ A/B 验证门 + 安全回滚，纯自我批判禁沉淀。
tags: [tri, evolve, learning, feedback, profiling, ab-testing]
license: MIT
---

# 自进化学习

> 本 skill 是 tri-xxx 家族的横向学习/进化型 skill，为全家族提供持续改进与用户画像构建能力。
> 通过多渠道信号采集 → 归因 → 提议 → A/B 验证 → 沉淀的 OODA 闭环，提升 skill 命中率与回答质量；构建演进式用户画像使回答风格贴合用户偏好。
> 不认领 L2 意图编码，不破坏家族 MECE 划分，是横切关注点（学习层）。
> 用户心智：「让我的助手越用越懂我，越用越准。」

## 强制执行契约（Execution Contract · 最高优先级）

> 本契约优先级高于 Agent 通用默认行为。**触发源命中（作答后 hook / 定时批量 / 下游请求画像经验）即视为激活本工作流**，不得仅将其当作参考文档。

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（运行 `scripts/check_update.py` 做本地版本一致性校验，本仓库为自维护 fork、不做远端比对；按脚本输出与退出码处置）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：
   - EVOLVE_OBSERVE：MUST 先接收作答事件（含 skill/intent/user_id/session_id），NEVER 在无事件时凭空采集。
   - EVOLVE_LEARN：MUST 先聚合信号窗口（近 N 条同 skill/intent），NEVER 单条信号即归因。
   - EVOLVE_APPLY：MUST 先校验 user_id 与场景，NEVER 返回他人画像或未验证经验。
   - 独立使用时 MUST 先走 §上游依赖检测 判定模式。
2. **外部信号锚定（generator-verifier gap 防护）**：
   - 改进提议 MUST 锚定外部信号（用户显式反馈 / 隐式行为 / 缓存命中 / 纠偏记录 / 执行结果），NEVER 基于纯自我批判生成提议。
   - 无外部信号锚定的提议 NEVER 沉淀。
3. **验证门强制**：
   - 提议 MUST 经 A/B 验证（小流量对照），lift ≥ 阈值（默认 5%）且统计显著（p<0.05）才沉淀为 verified 经验。
   - 未验证（status=pending/validating）的经验 NEVER 注入下游 skill 提示。
4. **高风险人工审批**：
   - 修改 skill 核心契约（强制执行契约 / 自检句 / 激活语义）MUST 人工审批，NEVER 自动沉淀。
   - 中风险（经验沉淀 / 配置覆盖）经 A/B 验证；低风险（画像更新）自动应用。
5. **画像隐私保护**：
   - 敏感属性（health / political / religious / sexual）NEVER 推断，NEVER 写入画像。
   - 用户画像 MUST 支持导出（export）/ 删除（delete）/ 脱敏。
6. **回滚机制**：
   - 每次沉淀 MUST 带版本号，可回滚至上一稳定版。
   - 错误学习（被回滚）MUST 记录原因，避免重复学习。
7. **自检句**：每次操作前 MUST 声明「本次操作=<EVOLVE_OBSERVE|EVOLVE_LEARN|EVOLVE_APPLY>，触发源=<hook|定时|请求>，已读取<信号|经验库|画像>，产物=<信号事件|经验条目|画像/经验>」；与快照冲突时 MUST 停止并纠正，NEVER 擅自继续。

## 触发时机

本 skill 为横向学习型，不认领 L2 编码，激活由**触发源**决定：

| 触发源 | 模式 | 激活条件 | **无 hook / 无调度时的降级路径** |
|--------|------|----------|----------------------------------|
| evolve-hook（下游 skill 作答后触发） | EVOLVE_OBSERVE | hook 传入作答事件 + 用户行为 | **pi（形态 B）：✅ 已交付**（`hooks/pi/index.ts`，落点 `agent_settled`，真机验证一轮恰好 1 条、幂等）。**其他宿主**：❌ 形态 A/C 未交付 → 该模式不可用，信号采集改由用户显式录入或跳过，`LEARN` 将无原料 |
| 定时/批量触发（tri-evolve learn --batch） | EVOLVE_LEARN | 聚合信号窗口 + 历史经验（**默认手动触发**；定时为 opt-in，见 §调度安全门） | ✅ 默认即手动：`tri-evolve learn --batch` |
| 下游 skill 请求画像/经验 | EVOLVE_APPLY | 请求含 user_id + 场景描述 | ✅ 本身即显式，无降级需求 |
| 用户管理请求（stats/profile/rollback） | EVOLVE_ADMIN | 用户发起管理命令 | ✅ 本身即显式，无降级需求 |

> 注：tri-intent 快照下游路由建议**不指向**本 skill（本 skill 非下游执行 skill）。本 skill 通过 hook、定时或显式请求独立激活。
>
> **hook 依赖声明（家族规则 §1.5）**：`EVOLVE_OBSERVE` 依赖 `evolve-hook`，该 hook **不随本包交付**，需宿主另行配置。
> **未配置时本 skill 可正常工作的只有 `EVOLVE_APPLY`（下游取画像/经验）与 `EVOLVE_ADMIN`（管理命令）**；
> `EVOLVE_OBSERVE` 不可用、`EVOLVE_LEARN` 因无信号原料而空转。此事实 MUST 显式声明，NEVER 让用户误以为拿到的是完整模式。

## 调度安全门（自主执行约束 · P0）

> **本 skill 默认为手动批处理技能，不是自主 Agent。** 定时/批量能力依赖外部调度器（cron/hook），未配置时降级为手动触发。NEVER 在无 human-in-loop 的情况下静默后台改写 `.tribro/evolve/`。

1. **手动优先**：`EVOLVE_LEARN` 默认仅接受用户显式指令（`tri-evolve learn --batch`）；定时触发为 opt-in，须 `templates/meta.json` 中 `schedule.enabled=true` 显式开启，默认 `false`。
2. **批次幂等**：每批写 `run.lock` + `run-log.jsonl`（run_id / 开始 / 结束 / 状态 / 处理水位 `last_processed_offset`）；同窗口重跑按水位续跑，不重复归因。
3. **失败重试**：批次崩溃后按 run_id 续跑；连续 3 次失败自动停用定时并通知用户，NEVER 无限重试。
4. **副作用门控**：画像更新（低风险）自动写 `profile.db` 但带版本可回滚；`signals.jsonl` 仅追加；`baseline.db` 自动更新。**所有自动写入 MUST 可回滚**；中/高风险（经验沉淀/配置覆盖/契约修改）经 A/B 验证门或人工审批，NEVER 静默自动应用。
5. **配额与轮转**：`signals.jsonl` / `run-log.jsonl` 按容量轮转（默认 100MB），NEVER 无界增长。
6. **如实标注**：未配置外部调度器时 `EVOLVE_LEARN` 仅手动触发；SKILL.md / README / 对外文档 MUST 标注「定时能力依赖外部调度器，未配置时为手动批处理技能」，NEVER 宣称「自动/自主学习」而实际无人触发。

## 上游依赖检测（独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent 是否可用，据检测结果选择执行模式（原 tri-cache 缓存层本分支未包含，其「缓存命中」信号渠道随之不可用）：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| **A · 完整模式** | 检测到 `tri-intent/` 且 `.tribro/snapshots/` 有快照 | 六渠道信号全采集（显式/隐式/缓存命中/纠偏/快照分布/会话轨迹）；画像持久化；经验库 embedding 检索 |
| **B · 引导安装** | 未检测到 tri-intent | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户拒绝安装 | 退化为仅会话内反馈学习（无跨会话沉淀、无画像持久化、无经验复用），声明降级精度低 |

> 注：缓存层原 tri-cache 本分支未包含，「缓存命中」信号渠道（渠道 ③）在本分支不可用；其余五渠道不受影响。

**模式 B 提示语**：

> 本 skill 的完整进化能力依赖上游 tri-intent（快照分布信号）；缓存命中统计信号原由 tri-cache 提供，该 skill 本分支未包含。
> 请安装：`python ops/install-skills.py --target <目标目录>`
> 安装后方可采集六渠道信号、构建持久化画像、复用历史经验。若仅需会话内反馈学习可进入降级模式。

**模式 C 降级声明**：

> 未检测到 tri-intent，已进入降级模式：仅采集会话内显式/隐式反馈，无跨会话画像沉淀、无经验库检索、无 A/B 验证。进化精度低于标准链路，建议后续安装 tri-intent 以获得完整效果。

> **对称双向检测**：本 skill 检上游；tri-intent 亦可检测本 skill 是否存在以决定是否触发 evolve-hook。任一端缺失都被发现。

## 输入契约

### EVOLVE_OBSERVE 模式输入

| 输入源 | 字段 | 用途 |
|--------|------|------|
| evolve-hook | 作答事件（skill / intent_l2 / user_id / session_id） | 信号归因到 skill/intent |
| evolve-hook | 作答内容（提问 + 回答） | 质量评估输入 |
| 用户行为 | 隐式信号（采纳 / 修改 / 重试 / 中断 / 复制） | 满意度推断 |
| 用户输入 | 显式反馈（赞 / 踩 / 评分 / 纠偏文本） | 质量标注 |

### EVOLVE_LEARN 模式输入

| 输入源 | 字段 | 用途 |
|--------|------|------|
| 信号库 | 信号窗口（近 N 条同 skill/intent） | 模式识别 |
| 原 tri-cache（本分支未包含） | 命中统计（hits / misses / stale 比例） | 命中率归因 |
| tri-meta | 纠偏记录 | 缺陷归因 |
| 快照目录 | 意图分布 / 澄清门触发率 | 意图识别准确度信号 |
| 会话历史 | 多轮交互轨迹 | 偏好线索挖掘 |

### EVOLVE_APPLY 模式输入

| 输入源 | 字段 | 用途 |
|--------|------|------|
| 下游请求 | user_id | 取用户画像 |
| 下游请求 | 场景描述（skill / intent / 任务） | 经验复用检索 embedding |
| 下游请求 | apply_type（profile / lesson_reuse / config_override） | 决定返回内容 |

### 模式 C 降级输入

仅会话内显式/隐式反馈；无快照/缓存/纠偏/会话轨迹输入。

## 职责边界

- **本 skill 负责**：多渠道进化信号采集；归因分析；改进提议生成与 A/B 验证；经验条目库沉淀与检索复用；用户画像构建（静态/动态分层+时间衰减）；配置覆盖建议；安全回滚。
- **不负责**：意图识别（tri-intent）；业务作答（各下游 skill）；缓存存储（原 tri-cache，本分支未包含）；元操作纠偏（tri-meta）。
- **与缓存层的边界**：原 tri-cache（本分支未包含）是「记忆层」（存历史作答）；本 skill 是「学习层」（从历史中学习）。设计上缓存层提供「命中率」信号给本 skill，本 skill 输出「调优建议」可影响缓存层的差异化 TTL 配置；该协作在本分支暂不可用。
- **与 tri-meta 的边界**：tri-meta 处理 M01-M04 元操作（实时澄清/纠偏）；本 skill 处理离线归因与长期学习。tri-meta 的纠偏记录是本 skill 的信号源之一。
- **MECE 边界**：本 skill 不认领任何 L2 意图编码，不破坏家族全部路由型下游执行 skill 的 MECE 划分；它是横切关注点（学习层）。
- **不触发场景（Not-Trigger）**：本 skill 不接手「意图识别」（转 tri-intent）；不接手「业务作答」（属各下游执行 skill）；不接手「历史作答缓存存储」（原属 tri-cache，本分支未包含，本 skill 是学习层不是记忆层）；不接手「元操作实时纠偏/细化」（属 tri-meta）。

## 自进化方法论（核心能力 · 可扩展）

> 自进化方法论是 tri-evolve 的核心能力。通过「OODA 闭环 + 经验条目库 + 用户画像分层 + A/B 验证门 + 安全回滚」五件套，确保进化有据、有验、可回滚、不越界。这是 tri-evolve 区别于其它家族 skill 的核心差异化能力。

### 核心理念

> **进化不是瞎改——学要有据，改要有验，错要能回滚，隐私要护住。**

### OODA 进化闭环

```
观察(Observe) → 归因(Attribute) → 提议(Propose) → 验证(Prove) → 沉淀(Persist)
   多渠道信号      模式识别          带置信度         A/B 小流量     验证通过
   采集聚合        归因到            改进建议         对照验证       入经验库/画像
                  skill/意图                        lift≥阈值
```

| 阶段 | 动作 | 产物 |
|------|------|------|
| 观察 | 六渠道信号采集 → 信号事件流（signals.jsonl） | 信号事件 |
| 归因 | 信号聚合 → 异常检测（低于基线 σ）→ 归因到 skill/intent 缺陷 | 归因报告 |
| 提议 | 生成改进建议（锚定外部信号，带置信度）→ proposals（pending） | 调优建议 |
| 验证 | A/B 小流量对照 → lift + 显著性检验 | 验证结果 |
| 沉淀 | verified → lessons + 配置覆盖；rejected → 记录原因 | 经验条目 |

### 六渠道信号源

| 渠道 | 信号 | 来源 |
|------|------|------|
| ① 显式反馈 | 赞 / 踩 / 评分 / 纠偏文本 | 用户主动输入 |
| ② 隐式行为 | 采纳 / 修改 / 重试 / 中断 / 复制 | 作答后用户行为 |
| ③ 缓存命中 | 命中率 / 未命中模式 / stale 比例 | 原 tri-cache `cache_meta`（本分支未包含） |
| ④ 纠偏记录 | M02 纠偏事件 | tri-meta |
| ⑤ 快照分布 | 意图识别分布 / 澄清门触发率 | `.tribro/snapshots/` |
| ⑥ 会话轨迹 | 多轮交互偏好线索 | 会话历史 |

### 经验条目库（Voyager 式可检索复用）

经验条目 ≠ append-only 反思日志。每条经验带 embedding 索引，可语义检索复用。条目字段（scenario / attribution / proposal / confidence / status / ab_result / embedding 等）全集见 `schemas/evolve-schema.md`（单一事实源），SKILL.md 不重复；新增字段在 schema 单点追加。

### 用户画像四层 schema

| 层 | 内容 | 稳定性 | 更新方式 |
|----|------|--------|----------|
| 静态属性 | 年龄 / 职业 / 地域 / 技术栈 | 稳定 | 显式提供优先，保守推断 |
| 风格偏好 | 语气（正式/口语）、长度（简短/详尽）、格式（列表/段落） | 中稳定 | 时间衰减加权（半衰期 30 天） |
| 主题偏好 | 擅长领域、兴趣主题、术语偏好 | 动态 | 时间衰减 + 频次 |
| 交互习惯 | 提问风格、常用意图分布、活跃时段 | 动态 | 滑动窗口统计 |

> 偏好演变：每次更新写 `prefs_history`（带时间戳），可追溯演进（应对 PERSONAMEM 揭示的偏好动态演进问题）。

### 安全分级与回滚

| 风险级 | 变更类型 | 审批方式 |
|--------|----------|----------|
| 低 | 画像动态偏好更新 | 自动应用，带版本 |
| 中 | 经验沉淀 / 配置覆盖 | A/B 验证门 |
| 高 | skill 核心契约修改 | MUST 人工审批 |

回滚：`tri-evolve rollback --lesson <id>` 回滚经验；`tri-evolve restore --version <v>` 恢复画像。

### 可扩展性

> 新增进化能力无需修改核心闭环：

1. **新增信号渠道**：在六渠道表追加一行（如「外部 API 反馈」），观察阶段自动采集。
2. **新增画像维度**：在四层 schema 追加字段（如「语言偏好」），更新策略复用衰减加权。
3. **新增验证方式**：在验证门追加方式（如「专家审核」替代 A/B），通过后统一入 verified。
4. **切换存储后端**：从 SQLite 切换至向量库（经验 embedding 检索），保持 schema 不变。



## 版本检查与更新机制（强制技术约束 · 硬红线）

<!-- version-stub v1 · 瘦指针节点；细则唯一真源见 references/version-check-spec.md -->

> 任一执行入口启动后的**第零步**，先于核心执行阶段。细则唯一真源：`references/version-check-spec.md`；
> 可执行实现（逻辑唯一真源）：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、状态判定 MUST 由脚本完成；prompt 层 ONLY
> 「调用脚本 + 解析其 JSON 输出 + 按 `state` 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

```bash
python scripts/check_update.py --slug tri-evolve --json
```

- 处置：按脚本输出放行或阻断（判据与 `block_code` 语义见真源）；NEVER 因版本门自身故障阻断 skill 启动。

## 宿主兼容与提问呈现（横切硬约束 · 呈现纪律）

<!-- host-compat-stub v1 · 自包含瘦节；细则唯一真源见 tri-intent/references/host-compat.md（本节点文本自洽，独立安装时不依赖该文件可达） -->

> 本 skill 的「需要用户决策」时机全部以宿主中立自然语言书写（如「是否…？（是 / 否）」、clarify-gate 的
> 「逐条补充 / 按默认 / 继续」）。在**提供交互式提问工具**的宿主中（如 Proma 的 `AskUserQuestion`），
> 运行时会自动把这类句式升级为交互式问答横幅——**呈现形式由宿主决定，不由本 skill 决定**。
>
> **家族约定（MUST）**：凡触发 🔴 STOP 用户确认检查点或 clarify-gate 的时机，MUST 以**普通 Markdown 文本**
> 呈现为聊天问题，**NEVER 调用交互式提问工具**（`AskUserQuestion` / `ask_user_question` /
> `request_user_input` / `clarify` 及等价物）；用户回复契约（逐条补充 / 按默认 / 继续 / 是·否）
> **保持不变**。
>
> **边界**：本条只管呈现形式，MUST NOT 改动任何门控的判定条件、触发时机与处置动作；
> 在无交互式提问工具的宿主中本条自然空转；用户明确要求交互式提问时优先用户指令；
> 跨宿主判据只认「🔴 STOP 用户确认检查点」这一形态，NEVER 在 skill 内硬编码宿主工具名。
## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 核心执行。版本检查未通过前 NEVER 进入以下任一执行步骤。

> 三模式分流程，无审批门（验证门替代，A/B 验证非人工审批门）。

### EVOLVE_OBSERVE 流程（被动观察）

1. **接收**：evolve-hook 传入作答事件 + 用户行为
2. **声明自检句**：「本次操作=EVOLVE_OBSERVE，触发源=hook，已读取信号，产物=信号事件」
3. **信号采集**：六渠道事件入库 signals.jsonl
4. **质量分计算**：赞踩比 / 重试率 / 纠偏率 / 命中率
5. **异常检测**：低于基线 σ → 标记待归因
6. **画像增量更新**：隐式行为更新动态偏好（时间衰减加权）

### EVOLVE_LEARN 流程（主动学习）

1. **接收**：定时/批量触发
2. **声明自检句**：「本次操作=EVOLVE_LEARN，触发源=定时，已读取信号库+经验库，产物=经验条目/调优建议」
3. **信号聚合**：按 (skill, intent) 聚合窗口
4. **归因分析**：模式识别 → 归因到缺陷
5. **提议生成**：锚定外部信号 → proposals（pending，带置信度）
6. **A/B 验证**：小流量分流 → 累积样本 → lift + 显著性
7. **沉淀决策**：lift ≥ 5% 且 p<0.05 → verified 入 lessons；否则 rejected
8. **基线更新**：baseline 表追加时序记录

### EVOLVE_APPLY 流程（主动应用）

1. **接收**：下游请求 {user_id, 场景, apply_type}
2. **声明自检句**：「本次操作=EVOLVE_APPLY，触发源=请求，已读取画像+经验库，产物=画像/经验/配置覆盖」
3. **画像返回**（apply_type=profile）：取 user_id 画像（静态+动态），冷启动用 default
4. **经验复用**（apply_type=lesson_reuse）：场景 embedding 检索 top-k verified 经验
5. **配置覆盖**（apply_type=config_override）：返回 verified proposal 的 config_override
6. **隐私校验**：敏感属性 NEVER 返回
7. **返回**：画像 / 经验 / 配置覆盖

## 兜底处理（NEVER 静默失败）

本 skill 在下列五类异常下 MUST 走显式降级路径并**在回执中标注**，NEVER 静默失败：

| 异常类 | 触发 | 兜底路径 |
|---|---|---|
| ① 版本检查异常 | `scripts/check_update.py` 返回非 A/D 或 ≥20（BLOCK） | 按 §版本检查与更新机制 处置；BLOCK 时停止本轮进化并报告 |
| ② 门禁不过 | A/B 验证门未通过、或 §调度安全门 未放行 | 停止应用本轮经验，回滚至上一稳定画像 / 经验库快照（§安全分级与回滚） |
| ③ 上游缺失 | 无 tri-intent 快照 | 走 §上游依赖检测 的降级模式，按 §模式 C 降级输入 向用户追问进化目标与范围 |
| ④ hook 缺失 | 以 hook / 定时为触发源 | §触发时机 表已声明**无 hook / 无调度时的降级路径**：退化为**手动批处理**（EVOLVE_LEARN / EVOLVE_APPLY 由用户显式发起），NEVER 假装已自动运行 |
| ⑤ 异常场景 | 信号源不可读、经验库损坏、画像写入失败 | 保留现场并标注「未分类异常」；**先回滚再报告**，NEVER 带着损坏状态继续进化 |

## 🔴 检查点与红灯清单（STOP · NEVER）

### 🔴 用户确认检查点（STOP）

- 🔴 **STOP**：高风险人工审批——修改 skill 核心契约（强制执行契约/自检句/激活语义）MUST 人工审批，未获用户确认 NEVER 继续。
- 🔴 **STOP**：调度安全门（定时 opt-in）——定时/批量改写 `.tribro/evolve/` 前须在 `templates/meta.json` 显式开启 `schedule.enabled=true`，未获用户确认 NEVER 继续。
- 🔴 **STOP**：A/B 验证门——中风险经验沉淀/配置覆盖须 lift ≥ 阈值（默认 5%）且 p<0.05，未获验证通过 NEVER 继续。

### 🚫 红灯清单（NEVER）

- NEVER 基于纯自我批判生成改进提议（§强制执行契约）
- NEVER 将未验证（pending/validating）经验注入下游 skill 提示（§强制执行契约）
- NEVER 推断或写入敏感属性（health/political/religious/sexual）到用户画像（§强制执行契约）
- NEVER 在无 human-in-loop 的情况下静默后台改写 `.tribro/evolve/`（§调度安全门）
- NEVER 宣称「自动/自主学习」而实际无人触发（§调度安全门）
- NEVER 带着损坏状态继续进化，先回滚再报告（§兜底处理）

## 交付产物

| 产物 | 文件名 | 内容 | 审批门 |
|------|--------|------|--------|
| 信号事件流 | `signals.jsonl` | 每行一信号事件 | 无（自动采集） |
| 经验条目库 | `lessons.db` | verified 经验 + embedding | A/B 验证门 |
| 用户画像 | `profile.db` | 静态/动态分层 + 演变历史 | 无（自动更新） |
| 调优建议 | `proposals.db` | pending/validating/verified/applied | A/B 验证门 |
| 质量基线 | `baseline.db` | 各 skill 各意图质量时序 | 无（自动记录） |
| 画像/经验返回 | 即时对话回应 | 画像 + 复用经验 + 配置覆盖 | 无 |

### 经验条目格式（lessons.db）

```yaml
lesson_id: <UUID>
scenario: <场景描述>
attribution: <归因：skill/intent/缺陷>
proposal: <改进建议>
confidence: 0.85
status: verified
ab_result: {lift: 0.08, sample: 50, p_value: 0.03}
embedding: <向量>
source_channels: [explicit_feedback, cache_hit]
target_skill: tri-coding
target_intent: I11
created_at: <ISO时间>
verified_at: <ISO时间>
schema_version: 1
```

## 质量标准

| 维度 | 标准 | 验证方式 |
|------|------|----------|
| 信号完整性 | 六渠道信号全采集入库 | 事件计数核对 |
| 外部锚定 | 提议 100% 锚定外部信号 | 提议源校验 |
| 验证门 | verified 经验均经 A/B（lift≥5% 且 p<0.05） | ab_result 字段校验 |
| 高风险审批 | 核心契约修改 100% 人工审批 | 审批记录核对 |
| 画像分层 | 静态/动态分层 + 时间衰减 | schema 字段校验 |
| 隐私保护 | 敏感属性 NEVER 入画像 | 画像扫描校验 |
| 回滚可用 | 每次沉淀可回滚 | rollback 命令验证 |
| 经验复用 | embedding 检索延迟 <30ms | 基准测试 |
| 错误学习率 | 被回滚沉淀比例 <10% | 统计监控 |

## 落盘规则

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- 本 skill 进化产物落盘于 `.tribro/evolve/`（含 signals.jsonl / lessons.db / profile.db / proposals.db / baseline.db，可覆盖更新）
- 信号事件流落盘于 `.tribro/evolve/signals.jsonl`（追加写）
- 画像/经验返回为即时对话回应，不落盘
- 降级模式（模式 C）仅会话内学习，不跨会话落盘

## 目录结构

```
tri-evolve/
├── SKILL.md                          主入口：进化契约 + OODA 闭环 + 画像分层 + 验证门
├── README.md                         特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      Keep a Changelog + SemVer
├── schemas/
│   └── evolve-schema.md             进化数据 schema（lessons/profile/proposals/baseline 表）
├── templates/
│   └── meta.json                     配置模板（A/B 阈值/衰减/风险分级/敏感属性/schedule）
└── tests/
    └── tri-evolve-full-testcases.md  全场景全能力测试用例（审计版）
```

### 运行时落盘结构（`.tribro/evolve/`）

```
.tribro/evolve/
├── signals.jsonl                     信号事件流（追加写）
├── lessons.db                        经验条目库（SQLite + embedding）
├── profile.db                        用户画像（静态/动态/演变历史）
├── proposals.db                      调优建议（pending/validating/verified/applied）
├── baseline.db                       质量基线时序
└── meta.json                         进化元信息（统计 + 配置）
```
