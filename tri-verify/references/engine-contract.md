# 引擎契约与登记表

> 本文件是 `tri-verify` 的**引擎层单一事实源**。SKILL.md §引擎抽象 只定义七方法契约的语义；
> 具体引擎的命令映射、退出码语义、能力矩阵与降级触发条件，全部登记在此。
>
> **可扩展性**：新增引擎只需在 §二 登记表追加一行 + 在 §三 补命令映射，**无需修改 SKILL.md**。

---

## 一、引擎契约（七方法 · 平台无关）

```
reachability(target: url | port) -> bool
    派发前的可达性预检。用途：避免一次注定失败的计费执行。
    判据：DNS 解析失败 / 连接被拒 / 网关 5xx 均返回 false。

create(contract) -> testId
    把行为契约登记为引擎侧可反复执行的测试实体。
    注意：创建与执行 MUST 是两个独立动作（决定花钱 ≠ 真正花钱）。

run(testId, {target}) -> { status, exitCode, runId, stepSummary }
    触发一次执行。status ∈ {passed, failed, blocked, cancelled, inconclusive, queued}。
    stepSummary 至少含 { total, completed, passedCount, failedCount }。

summary(testId) -> { failureKind, hypothesis, fixTarget }
    一屏快速分流。用途：先读摘要拿 failureKind，再决定是否下载完整证据包（省 IO）。

fetch_failure(runId) -> bundle
    同源失败证据包。**一致性约束**：bundle 内 snapshotId / testId / runId 必须同源。
    不一致时引擎 MUST 拒绝交付；本 skill 收到不一致信号 MUST 拒收并按 C 类处置。

diff(runA, runB) -> { verdictMatch, regressions, codeVersionDrift }
    运行对比。用途：修复后复验，机械判定有无回归（防「修好 A 破坏 B」）。
    verdictMatch=false 即存在回归。

cancel(runId) -> void
    成本兜底。**为什么必须有**：中断（Ctrl-C）在多数引擎中只 detach，
    任务仍在云端执行并计费 —— 没有 cancel，轮次上限在成本上是假的。
```

---

## 二、引擎登记表

| 引擎 id | 类型 | 前置条件 | 定位 | 适用层 |
|---|---|---|---|---|
| `local` | 本地 | Playwright（前端）/ pytest + requests（后端） | 零外部依赖、可离线、零成本、结果确定 | 全部层（默认） |
| `testsprite` | 云端 | `TESTSPRITE_API_KEY` + 网络可达 + 额度 > 0 | 语义定位（抗 UI 漂移）+ 真浏览器 + 同源证据包 | **冒烟层**（高价值路径） |

**前后端不对称是刻意的**：前端模糊性有收益（语义定位抗 UI 漂移），
后端契约必须精确（字段名 / 类型 / 状态码的模糊性只增加假阳性）。故：
- 前端 → 可交云端引擎的语义 Agent
- 后端 → 保留确定性脚本（`requests` + 精确断言），即使走云端引擎也只作托管执行

---

## 三、`testsprite` 引擎命令映射（v0.12.0 实测）

> 实测报告：`reports/probe-testsprite-cli-20260925.md`。本节所有命令与退出码均为**实机核对**，
> 非文档推测。**基线差异**：参考文章实测版本为 v0.10.0，本登记以 v0.12.0 为准。

| 契约方法 | 命令 | 备注 |
|---|---|---|
| `reachability` | `test run --target-url <url>` 的**派发前预检**（内置） | 官方原文：探测在**本机**执行、不在执行 Lambda 上，故**只是启发式**；可用 `--skip-preflight` 覆盖 |
| `create` | `test create --plan-from <file>` | 单文件；`--plans` 收 **JSONL**（传单对象会逐行报 JSON 无效，且**不提示**该换参数） |
| `create`（批量） | `test create-batch --plans <file.jsonl>` | ≤50 specs/次；50/min 节流；服务端 60/min 上限 |
| `run` | `test run <id> --wait --timeout <s> --output json` | `--wait` 阻塞至终态 |
| `run`（本地目标） | `test run <id> --local <port>` | **仅前端**；只接受 loopback（不是 LAN/RFC1918 逃生舱）；需 key 具备隧道 scope |
| `summary` | `test failure summary <id>` | 一屏摘要（status / failureKind / hypothesis / fix target） |
| `fetch_failure` | `test artifact get <run-id>` | 按 run 取**同源**包；默认落 `./.testsprite/runs/<run-id>/` |
| `fetch_failure`（最新失败） | `test failure get <test-id> --out <dir>` | 面向「最近一次失败运行」 |
| `diff` | `test diff <run-a> <run-b>` | **exit 0 = 判定一致 / exit 1 = 有回归**（含 per-step 状态翻转与 codeVersion drift） |
| `cancel` | `test cancel <run-id>` | Ctrl-C 仅 detach（**继续计费**），必须显式 cancel |
| 续等超时 | `test wait <run-id>` | 退出码 7（超时）后的续等入口 |
| 额度查询 | `usage`（别名 `credits`） | 大轮次执行前的预防性检查 |
| 零成本自测 | 全局 `--dry-run` | 官方原文：**不需要 API key**，输出符合 OpenAPI 契约的样例 |
| 契约本地校验 | `test lint --plan-from <file>` | **纯本地、零凭证**；exit 0 全合法 / 5 有问题（收集**全部**问题不短路） |
| 契约批量校验 | `test lint --plan-from-dir <dir>` | 一目录 `*.json` 全量校验 —— 正对回归层 |
| 骨架 | `test scaffold` / `test create --plan-template` | 纯本地，产出 schema-correct 骨架 |

### 3.1 退出码语义（实测）

| 码 | 含义 | `tri-verify` 归类 |
|---|---|---|
| 0 | passed（或未加 `--wait` 时的 queued） | 通过 |
| **1** | failed / blocked / cancelled | **读证据包做 A/B 归因** |
| 3 | auth error（含缺隧道 scope） | C |
| 4 | 未找到（用例 / 运行） | B（配置缺陷） |
| 5 | validation error（含 `meta.runId` 不一致） | B（契约缺陷） |
| 6 | conflict（已有运行中实例 / snapshot 生成中） | C |
| 7 | timeout | C |
| 10 | transport / network failure | C |
| 11 | rate limited（遵守 `Retry-After`） | C |

> **设计要点**：C 类**不由语义判断**，由退出码机械判定。这把「环境不稳定被误判成产品缺陷
> → 自动修复制造缺陷」这一最危险的失败模式从机制上排除。

### 3.2 plan 契约形态

- 本地 schema 副本随 CLI 包分发：`<pkg>/schemas/plan.schema.json`
- 必需字段：`["projectId", "type", "name", "planSteps"]`
- `planSteps[].type` ∈ `{ "action", "assertion" }`；`type` ∈ `{ "frontend", "backend" }`
- **一个 plan 文件 = 恰好一个测试**；顶层 JSON 数组会被**拒绝**（多用例走 `create-batch`）
- 文件 **≤ 256 KB**
- 官方自我声明：schema 与实际校验器不一致时，**以校验器的实际接受行为为准**

---

## 四、权威纪律（`testsprite` 引擎专属）

⚠️ 该引擎**自带一套验证循环 skill**（实测 `agent list` 输出）：

| 落点 | 目标 |
|---|---|
| `testsprite-verify` | `.claude/skills/` · `.cursor/rules/` · `.kiro/skills/` · **`AGENTS.md`（codex）** 等 |
| `testsprite-onboard` | 同上 |

**三个冲突点**：

1. **命名**：其 skill 名与本 skill 语义同名，易被混为一谈。
2. **落点**：codex 目标写 **`AGENTS.md`** —— 与家族 `tri-init` 的 AGENTS.md 生成职责**争抢同一文件**。
3. **语义**：其自带循环（自决「何时跑/何时跳」、二分归因、无轮次上限）与本 skill 的门禁语义**双权威并存**。

**强制处置**：

| 时机 | 动作 |
|---|---|
| 安装 | MUST `testsprite setup --api-key <KEY> --no-agent` —— **只配凭证，不装 agent skill** |
| 预检 | SHOULD `testsprite agent status`（官方原文：**exit 1 when anything needs attention, so it can gate CI**）探测竞争性 skill |
| 检出竞争 | MUST 报告 + 请用户裁定（移除 / 显式确认共存），**NEVER 静默共存** |
| 落点冲突 | MUST 在报告中点名（如 `AGENTS.md` 与 `tri-init`） |
| 语义 | 门禁判据（触发规则 / 三类归因 / 轮次上限 / 盖章四态）**不外包** |

---

## 五、降级触发条件（引擎层判定信号）

| 信号 | 判据 | 降级动作 |
|---|---|---|
| 无凭证 | 环境变量 `TESTSPRITE_API_KEY` 缺失 | → `local` |
| 凭证无效 | 命令返回退出码 3 | → `local`，并明示所需 scope |
| 额度不足 | `usage` 返回 0，或执行前预防性检查失败 | → `local`（本地引擎不耗额度） |
| 依赖缺失 | Playwright / pytest 探测失败 | → 后端-only 模式，前端层标 `N/A` |
| 目标不可达 | `reachability` 返回 false | 盖章「未执行（目标不可达）」，**不降级引擎**（换引擎也一样不可达） |
| 引擎契约偏离 | 返回未知退出码 / 缺字段 | 按 C 类处置 + 记录「引擎契约偏离」 |
| 官方排除路径 | OAuth/SSO/2FA、原生文件对话框、iframe、多标签页 | 契约层标「不适用」 |

> **本地引擎的诚实边界**：它不提供语义定位，UI 选择器漂移会导致契约失修 ——
> 这是**用维护成本换零依赖**的显式取舍，MUST 在契约中标注选择理由。
