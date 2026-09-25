# 真机探测报告：TestSprite CLI v0.12.0

- **日期**：2026-09-25
- **目的**：为 `tri-verify`（`reports/proposal-tri-verify-20260925.md`）的实施第 1 步做真机验证
- **方法**：隔离安装（**未使用 `npm install -g`**），零凭证探测；`--dry-run` 与纯本地命令全程实跑
- **环境**：`@testsprite/testsprite-cli@0.12.0` · Node `v22.22.2`（CLI 声明支持范围 `20.19+ / 22.13+ / 24+` ✅）· License `Apache-2.0`
- **安装位**：`C:\Users\sam\.workbuddy\binaries\node\workspace\node_modules\@testsprite\testsprite-cli`

> **基线差异**：参考文章实测版本为 **v0.10.0**（数据核查日 2026-09-10）。本次实测 **v0.12.0**，
> 半个月内跃升两个小版本 —— 下文 §四 列出文章未记载、但直接影响 `tri-verify` 设计的命令。

---

## 一、结论摘要（三条硬事实）

| # | 事实 | 对设计的影响 |
|---|---|---|
| **1** | `--dry-run` 是**全局开关**，官方原话「Skip the network and credentials; emit a canned sample matching the OpenAPI contract. Useful for learning the CLI surface **without an API key**」 | `tri-verify` 的引擎一致性自测**不需要凭证**，可在无 key 环境验证引擎契约是否通 |
| **2** | TestSprite **自带一个名为 `testsprite-verify` 的 agent skill**（29.7 KB），对 codex 目标直接写入 **`AGENTS.md`** | ⚠️ **权威冲突**：若 `tri-verify` 只跑 `testsprite setup`，项目里会多出一个**竞争性验证权威**。→ 设计强制：`setup` MUST 加 `--no-agent` |
| **3** | 「零凭证本地环路」实测成立：`test scaffold` / `test create --plan-template` / `test lint` 三个命令**全本地、不触网、不扣费** | `tri-verify` 的**契约质量门必须先走这一环**，通过后才允许派发到云端（成本前移） |

---

## 二、退出码实测（文章只记载 4 个，实测有 9 个）

**实测确认**（`doctor` 在缺凭证时返回 1；`--version` 返回 0）：

```
doctor exit = 1        （凭证缺失）
--version exit = 0
```

**官方文档给出的完整码表**（`testsprite test run --help` 原文）：

| 码 | 含义 | `tri-verify` 归类 |
|---|---|---|
| 0 | passed（或 `--wait` 未加时的 queued） | 通过 |
| **1** | failed / blocked / cancelled | **进三类归因** |
| **3** | auth error | 环境/基础设施（非产品缺陷） |
| 4 | test not found | 配置缺陷 |
| 5 | validation error | 契约缺陷（B 类） |
| **6** | conflict — already running（见 `nextAction` 的 active runId） | 环境/基础设施 |
| **7** | timeout — 用 `test wait <run-id>` 续等，或 `test cancel <run-id>` 停 | 环境/基础设施 |
| **10** | transport / network failure（UNAVAILABLE），可重试 | 环境/基础设施 |
| **11** | rate limited — 遵守 `Retry-After` | 环境/基础设施 |

> **设计结论**：`tri-verify` 的 C 类（环境抖动）**不再靠语义判断，而由退出码机械判定** ——
> `{3, 6, 7, 10, 11}` 一律归 C，**不修代码**；`{4, 5}` 归 B（契约/配置）；
> 仅 `1` 需要读证据包做 A/B 归因。这把最易误判的一类变成了确定性判据。

---

## 三、零凭证本地环路（实测）

| 命令 | 实测退出码 | 输出 | 备注 |
|---|---|---|---|
| `test scaffold` | **0** | 前端 plan JSON 骨架（含 `projectId` 占位、`type`、`name`、`planSteps[]`） | 纯本地 |
| `test create --plan-template` | **0** | 带 `$schema` 的完整 plan 骨架 | 纯本地，`--plan-from` 的配套 |
| `test lint --plan-from <合法>` | **0** | `1/1 valid, 0 problem(s)` | 纯本地 |
| `test lint --plan-from <非法>` | **5** | 逐条列出**全部**问题 | 纯本地，收集 EVERY problem 不短路 |
| `test lint --plans <单个 JSON 对象>` | **5** | `plan.json:1..12: plans: line N is not valid JSON` | **复现文章踩坑**：逐行报错却**不提示**该换 `--plan-from` |

**`test lint --help` 原文（四个输入通道）**：

```
--plan-from <file>       single plan JSON file
--plan-from-dir <dir>    directory of *.json plan files（每个都查，报全部错）
--plans <file>           JSONL file with one plan spec per line
--steps <file>           plan-steps JSON file
```

> `--plan-from-dir` 是文章未记载的**批量校验入口** —— 正对 `tri-verify` 的**回归层**（一目录契约全量校验，零成本）。

---

## 四、文章未记载、但设计必需的四个命令

### 4.1 `test diff <run-a> <run-b>` —— 复验的机械判据

原文：
> Compare two runs and print what regressed: verdict, failureKind, failedStepIndex,
> per-step status flips, **codeVersion drift**. **Exit 0 when verdicts match, 1 when they differ.**

**这是 `tri-verify` 「修复后复验」的关键**：对齐修复前的 `runId` 与修复后的 `runId`，
`exit 0` = 判定无回归，`exit 1` = 有回归（含 `codeVersion drift` 检测）。
**「修好 A 破坏 B」由此从「希望没破坏」变成「机械可比对」**。

### 4.2 `test artifact get <run-id>` —— 按 run 取证据包

原文退出码：`0` 写入成功 · `3` 认证 · `4` run 不存在/未就绪/无失败/已取消 ·
`5` 校验错（`--out` 非法、**`meta.runId` 不一致**）· `6` snapshot 生成中（重试一次）·
`10` 传输失败（**留 `.partial`**）。

> `meta.runId` 不一致 → 退出 5，**这就是文章所述同源校验的可执行落点**。
> `tri-verify` 的「异源包拒收」判据 = **由 CLI 自身执行**，我们不重复实现。

### 4.3 `test failure summary <test-id>` —— 一屏摘要

原文：`Print a one-screen summary of the latest failing run (status, failureKind, hypothesis, fix target)`。

> 适合作为**归因前的快速分流**：先读 summary 拿到 `failureKind` + `hypothesis`，再决定是否下载完整证据包（省 IO）。

### 4.4 `test cancel <run-id>` —— 成本兜底

原文警告：
> Ctrl-C during `--wait` **detaches only**（the run keeps executing and billing）;
> stop it for real with `testsprite test cancel <run-id>`

> **必须写进 `tri-verify`**：Ctrl-C 不等于停止，会继续计费。有限重试机制在**超时/中断**分支
> MUST 显式调用 `test cancel`，否则「有限重试」在成本上是假的。

---

## 五、⚠️ 权威冲突（本次最重要的发现）

`testsprite agent list` 实测输出（节选）：

```
AGENT                SKILL                PATH
claude               testsprite-verify    .claude/skills/testsprite-verify/SKILL.md
claude               testsprite-onboard   .claude/skills/testsprite-onboard/SKILL.md
...
codex (exp.)         testsprite-verify    AGENTS.md
codex (exp.)         testsprite-onboard   AGENTS.md
```

**三个冲突点**：

| # | 冲突 | 说明 |
|---|---|---|
| 1 | **命名** | 对方 skill 名 `testsprite-verify` 与 `tri-verify` 同名语义 —— 二者会被混为一谈 |
| 2 | **落点** | codex 目标写 **`AGENTS.md`** —— 而 `tri-init` 的职责正是「生成 AGENTS.md」。**两个 skill 会争抢同一文件** |
| 3 | **权威** | 内置 skill 自带一套「何时跑 / 何时跳 / 怎么判」的循环语义（29.7 KB）→ 与 `tri-verify` 的门禁语义**双权威并存** |

**内置 skill 的语义与 `tri-verify` 的差异（实测对比）**：

| 维度 | `testsprite-verify`（内置） | `tri-verify`（本设计） |
|---|---|---|
| 归因 | §4a「plan, or product?」**二分** + 零散提 infra | **三分**（产品/契约/环境），且 C 类由退出码机械判定 |
| 重试 | 「tighten via `test plan put` and re-run **once（two runs total）**」 | ≤2 轮 + **连续同类失败即停并升级人审** |
| 触发 | 自决「When to run / When to skip」 | **确定性触发规则表 V1–V5**，无人工判断 |
| 门禁地位 | 无（自由裁量） | **硬门**，失败阻断交付（或盖章升级人审） |
| 落盘 | 无规定 | `.tribro/verify/<命名>/` + `verdict.md` 四态封闭判据 |
| 降级 | 「Credentials are unavailable → 说明缺失，不声称已验证」 | **降级矩阵**（两引擎不可用/目标不可达/欠费 → 逐条处置，NEVER 阻断） |
| 家族集成 | 无 | 委派自 tri-coding / tri-fix / tri-sdlc；证据包作 tri-true 的 T1 信源 |

> **设计决议（强制）**：`tri-verify` 安装引擎 B 时 MUST 使用
> **`testsprite setup --api-key <key> --no-agent`** —— 只配凭证，**不安装对方的 agent skill**。
> 理由：单一门禁权威。若用户此前已被写入 `testsprite-verify`，`tri-verify` 的预检 SHOULD 用
> `testsprite agent status`（原文：**exits 1 when anything needs attention, so it can gate CI**）检出并提示。

---

## 六、成本与配额实测线索

| 项 | 实测/官方数据 |
|---|---|
| 免费档 | 150 credits/月（文章） |
| `--dry-run usage --output json` 样例字段 | `{credits, subPlan, creditsPerRun, v3Enabled, activeOrg{remaining, includedCredits, seats}}` |
| 前端已部署用例重放（V3 FE） | **0.5 credit**（内置 skill 原文） |
| 派发前预检 | `--target-url` 可达性探测（DNS 失败 / 连接拒绝 / 502-503-504 网关错）→ **拒绝派发，避免注定失败的计费** |
| 预检的诚实边界 | 官方原文：「The probe runs from **this machine**, not from the Lambda that executes the test, so it can **occasionally be wrong**」→ 可用 `--skip-preflight` 覆盖 |
| 批量限流 | `create-batch` ≤50 specs/次；50/min 节流；服务端 60/min 上限；`RATE_LIMITED` 重试 |
| **成本兜底** | `test cancel <run-id>`（Ctrl-C 仅 detach，继续计费） |

> `tri-verify` 的**成本前移链**：`--dry-run`（0 成本验形状）→ `test lint`（0 成本验契约）
> → `usage`（查余额）→ 派发。任何一环不过，**不产生费用**。

---

## 七、`--local <port>` 与 tunnel（文章标注「未在实测范围内」，本次核实）

- `test run <id> --local <port>` 存在，且**自动开关一次隧道**
- 官方约束：**仅前端用例**；后端用例的 target 烘焙在生成代码里，`--target-url` 对它**是惰性的**
- 需 API key 具备 **`run:tunnel` scope**；旧 key 缺该 scope 会**以 exit 3 明示**
- `--local` 只接受 **loopback**（`localhost` / `127.0.0.1` / `::1`），**不是** LAN/RFC1918 逃生舱
- 独立隧道命令 `tunnel start/status/stop`；官方原文：**「no background daemon, because the credential
  that authorises an inbound network path into this machine is never written to disk」**

> `tri-verify` 的前端本地验证路径据此确定；安全属性（凭证不落盘）可写进 references 佐证。

---

## 八、plan schema（本地副本已随包分发）

- 包内路径：`node_modules/@testsprite/testsprite-cli/schemas/plan.schema.json`（4,325 B）
- 远端版本化 URL：`https://raw.githubusercontent.com/TestSprite/testsprite-cli/v0.12.0/schemas/plan.schema.json`
- 必需字段：`["projectId", "type", "name", "planSteps"]`
- 关键约束（原文）：
  - **一个 plan 文件 = 恰好一个 test**；顶层 JSON 数组会被**拒绝**（多用例须走 `create-batch`）
  - `planSteps[].type` ∈ `{ "action", "assertion" }`
  - `type` ∈ `{ "frontend", "backend" }`
  - 文件 **≤ 256 KB**
- 官方自我声明（值得记录）：「if the two ever disagree, **the validator's actual acceptance behavior
  is authoritative** and this file is out of date」

> `tri-verify` 的 `templates/contract.md` 以本地副本为准，**不联网取 schema**（保证离线可用）。

---

## 九、对提案的修正

| 提案处 | 原表述 | 修正 |
|---|---|---|
| §4.3 触发规则 | 无退出码归类 | **新增**：C 类环境抖动由 `{3,6,7,10,11}` 机械判定，不由语义判断 |
| §4.5 引擎抽象 | `fetch_failure(runId)` | 改为 `test artifact get <run-id>`（按 run）+ `test failure summary`（快速分流）；同源校验**由 CLI 执行**（exit 5 on `meta.runId` mismatch） |
| §六 第 1 步 | 「先做真机探测」 | **✅ 已完成**（本报告） |
| **新增 §4.9** | —— | **权威纪律**：`setup` MUST 加 `--no-agent`；预检用 `agent status` 检竞争权威 |
| §八 D2 | CLI / MCP / 两者 | **因证据裁定为 CLI** —— 本机 `~/.workbuddy/mcp.json` 不存在，且 CLI 的退出码/`--dry-run` 是引擎契约所需；MCP 留作后续 |
| **新增** | —— | **复验机制**：用 `test diff <run-a> <run-b>`（exit 0 无回归 / 1 有回归）机械判定「修好 A 破坏 B」 |
| **新增** | —— | **成本纪律**：`test cancel <run-id>` —— Ctrl-C 不停止且继续计费 |

---

## 十、未验证项（诚实边界）

| 项 | 原因 | 影响 |
|---|---|---|
| 云端真实执行（`test create --run --wait`） | **无 API key / credits** —— 需要用户提供 `TESTSPRITE_API_KEY` | 前端真实耗时、`stepSummary` 字段、录像 URL 未经本机独立复核（沿用文章数据） |
| 失败证据包 9 文件的**实际磁盘布局** | 同上（`--out` 需要一次真实失败运行） | 只依官方 help 与文章；`tri-verify` 的 `failure-<runId>/` 与之**不做结构耦合**（只保留 `meta.json` 同源校验 + 原始 bundle 原样归档） |
| MCP 形态（`@testsprite/testsprite-mcp`） | D2 已裁定 CLI 优先 | 未探测；留作后续可选入口 |

> 上述三项**不阻塞** `tri-verify` 骨架落地（其引擎契约以退出码 + JSON 为准，不依赖具体 bundle 内部结构）。
> 待用户提供 API key 后补一次端到端实测，并回填本节。
