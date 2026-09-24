# Proposal：hook 多平台适配层（A / B / C 三形态）

- **日期**：2026-09-24
- **基线**：`main @ 0637a05`（24 skill）· 家族规则 `family-spec.md` §1.5
- **前置审计**：`reports/audit-hooks-20260924.md`（4 个 hook · 实现数 0）
- **状态**：`Approved: no` —— 本文件是设计，**未写任何实现代码**

---

## 一、目标

把 hook 从「文档里的隐性外部依赖」变成**一份契约 + 三个平台的适配器**，使同一 hook 在
A（shell）/ B（in-process）/ C（instructions-file）三种宿主上都能接线。

**不改变** hook 的语义与归属 —— 只补实现与接线方式。

---

## 二、现状（据审计）

| 项 | 实测 |
|---|---|
| 真 hook 依赖 | 4 个：`evolve-hook` / `cache-hook` / `cost-hook` / `guard-hook` |
| 实现数 | **0** |
| 平台分类学 | 仓库已有（`tri-code-analyzer/references/tech-stacks/agent-skills-plugin.md`）：A=shell-hook / **B=in-process（pi TS）** / C=instructions-file |
| 规则 | `family-spec.md` §1.5 已立四条（降级声明 / 登记 / 命名 / `hooks/` 目录纪律） |

---

## 三、设计

### 3.1 平台无关的 hook 契约（单一事实源）

每个 hook 用**语义事件**描述，不绑定平台：

```
hook:        <域>-hook
语义事件:     <何时触发，用平台无关的语言描述>
入参:        <结构>
出参:        <结构，或「无出参，仅落盘」>
幂等要求:    <同一事件重复投递时必须如何>
宿主降级:    <无 hook 时的替代路径（§1.5 规则 ① 要求）>
```

`evolve-hook` 的契约示例（本次唯一在 main 上的 hook）：

```
hook:        evolve-hook
语义事件:     一次「用户↔代理」交互彻底结束后（不会再自动继续）
入参:        { session_id, exchange_id, source_skill, answer, user_feedback? }
出参:        无（落盘信号事件）
幂等要求:    同一 (session_id, exchange_id) 只采集一次
宿主降级:    用户显式录入 / 跳过（OBSERVE 不可用 → LEARN 空转）
```

### 3.2 目录结构（依 §1.5 规则 ④：`hooks/` 只放宿主 hook 实现）

```
<skill>/hooks/
├── spec.md                    # 平台无关契约（3.1 的四段式）
├── pi/index.ts                # 形态 B · in-process（pi，jiti 直跑 TS）
├── shell/<hook>.sh            # 形态 A · shell-hook（stdout 必为合法 JSON）
└── instructions.md            # 形态 C · instructions-file 声明（给 @-include 类宿主）
```

> 三种形态**共享 `spec.md`** —— 各适配器只做「语义事件 → 平台接线」的翻译，不重复描述语义。
> 这满足 §1.5 规则 ①：**声明 hook 的地方（`spec.md`）必须同时给出降级路径**。

### 3.3 平台映射

| 语义事件 | A · shell-hook | **B · pi（in-process TS）** | C · instructions-file |
|---|---|---|---|
| 交互彻底结束 | 宿主 `Stop` 类事件 → 脚本读 stdin JSON，stdout 回 JSON | **`pi.on("agent_settled")`** — 官方定义为「最终、只通知，用于需要知道 Pi 不会再自动继续时」 | 指令文件里声明「每轮结束时执行 X」 |
| 消息定型 | `PostMessage` 类 | `pi.on("message_end")` | 同上 |
| 工具调用前 | `PreToolUse` 类 | `pi.on("tool_call")`（可改输入或 `{block:true}`） | 同上 |
| 会话开始 / 结束 | 宿主 session 事件 | `pi.on("session_start")` / `session_shutdown`（**幂等**） | 同上 |

### 3.4 pi 适配器的三条硬约束（来自 pi 官方文档，非推测）

pi 文档对扩展运行时有三条明确要求，直接决定实现形态：

1. **工厂里不得启动常驻资源** ——「Do not start processes, sockets, watchers, or timers in the factory
   because some invocations load extensions without starting a session.」
   → 所有初始化放 `session_start`；所有清理放**幂等的** `session_shutdown`。
2. **`ctx.reload()` 会替换扩展运行时，旧状态不可复用**。
   → **禁止用模块级变量做幂等标志位**（这是栈卡「坑 4：in-process 适配器需生命周期标志位防重」的根因）。
3. **状态应持久化在 session 内**：用 `pi.appendEntry()` 写入 session JSONL —— 官方说明它能
   **跨 restart 与 compaction 存活**。
   → `evolve-hook` 的「已处理水位」写 `appendEntry`，启动时读回；因此 **reload 后仍幂等**，
   而 `evolve-hook` 已有的 `run-log.jsonl` 水位机制（`last_processed_offset`）正好可复用同一思路。

**可用的 pi API（本次需用到的）**：`pi.on()` · `pi.appendEntry()` · `ctx.ui.notify()` ·
`ctx.mode`（tui/rpc/print/json，决定可否用 UI）· `pi.registerCommand()`（给降级路径提供
显式入口，如 `/evolve learn`）。

---

## 四、与现有 4 个 hook 的映射（实施优先级）

| hook | 归属 | 是否在 main | pi 事件 | 建议批次 |
|---|---|---|---|---|
| `evolve-hook` | `tri-evolve` | ✅ | `agent_settled` | **第 1 批**（唯一有真实需求 + 最小闭环） |
| `cache-hook` | `tri-cache` | ❌ 归档分支 | `message_end` | 第 2 批（恢复该 skill 后） |
| `cost-hook` | `tri-cost` | ❌ 归档分支 | `message_end` | 第 3 批 |
| `guard-hook` | `tri-guard` | ❌ 归档分支 | `tool_call` / `resources_discover` | 第 3 批 |

**先做 `evolve-hook` × pi** —— 因为它是 main 上唯一的真 hook，且能验证整条适配层设计是否成立。
验证通过后再决定是否铺开三形态 × 4 hook（12 个适配器的量级）。

---

## 五、实施顺序（dependency order）

1. **写 `spec.md` 契约**（平台无关四段式）—— 先定语义，再写接线。**缺此步则三形态必然漂移**
2. **写 pi 适配器**（`tri-evolve/hooks/pi/index.ts`）：`agent_settled` + `appendEntry` 水位 + `session_shutdown` 幂等清理
3. **补 A / C 两形态**（同 spec，不同接线）—— 可在 pi 验证通过后进行
4. **`family-spec.md` §1.5 登记表更新**：把「❌ 未交付」改为逐平台状态
5. **`compliance-checklist.md`**：第 14 条已是「五类含 hook 缺失」，可再加判定「多形态 hook 须三形态齐备或显式标注缺失平台」

---

## 六、风险与未知

| 项 | 说明 | 处理 |
|---|---|---|
| 🔴 我未验证 pi 的 `agent_settled` 是否真在「用户交互结束」时触发 | 官方措辞是「Pi will not continue automatically」，但**自动重试/恢复/压缩/排队工作可能在其后继续** | 写适配器时先做**真机探测**：装一个只打日志的极简扩展，跑一轮对话，确认事件时序 |
| 🟠 `ctx.ui` 在 headless 模式（`mode=print/json`）不可用 | pi 有 `ctx.hasUI` | 按 `hasUI` 分支：无 UI 时静默落盘，不用 `notify` |
| 🟠 三形态语义可能不等价 | 例：shell-hook 无「会话不自动继续」概念 | 在 `spec.md` 里标注**各形态的语义偏差**，不假装等价 |
| 🟡 pi 扩展有完整系统权限 | 官方安全提示 | 适配器只读 session 事件 + 写 `.tribro/`，不引入网络与非必要文件写 |

---

## 七、验收标准（第 1 批）

1. pi 中加载扩展后，一轮对话结束能产出 `.tribro/evolve/signals.jsonl` 新条目
2. **同一轮对话重复触发不产生重复条目**（幂等）
3. `/reload` 后再跑一轮，幂等仍成立（**证明未依赖模块级变量**）
4. headless 模式（无 UI）下不报错
5. 无 hook 环境（未装扩展）下，`tri-evolve` 的行为与 §触发时机 表声明的降级路径一致

---

## 八、审批

```
Approved: no
```
