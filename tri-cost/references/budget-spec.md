# tri-cost Token 预算闸门规范（COST_BUDGET · 代码级强约束）

> 唯一真源：本文件定义 tri-cost 的 token 预算闸门与自动优化执行器的配置 schema 与行为契约。
> 可执行实现：`scripts/token_budget.py`（纯 Python、零外部运行时，复用 `scripts/token_optimize.py` 的 detect/compress/count/accuracy/recovery）。
> 本规范覆盖基准报告（`docs/analysis-caveman-main-20260919.md`）§9.1 提出的**全部待优化点**，重点补齐 `token_optimize.py` 此前仅 md 约定、未代码化的两项：
> - **⑤ 令牌预算打包启发式**（BM25 相关性 + 近因 + 错误信号 + Pin 贪心装袋）→ `pack_context`
> - **⑥ safety 等级 S0–S4**（变换风险分级）→ `safety_class_of`
> 并新增流程级强约束 `enforce_node`（写入前预算闸门 + 自动优化）与 `gate_index`（全链路预算核查）。

## 0. 设计目标（用户要求）

> 以**代码方式**实现 token 优化逻辑的**强约束**，而非仅通过 md 文档进行口头约定；脚本覆盖报告指出的**所有待优化点**；token 使用**在流程中被自动校验与限制**；相关能力**集成进 skill 的执行链路**（COST_TRACK 写入前闸门、COST_AUDIT 全链路核查）。

| 报告待优化点（§9.1） | 代码落地 | 强约束形态 |
|---|---|---|
| ① 输出风格压缩规则 | `token_optimize.compress_style` | v1.2.0 已落地（md + 代码） |
| ② 载荷分类法（detect 13 类） | `token_optimize.detect_type` | v1.2.0 已落地 |
| ③ fail-closed 设计哲学 | `enforce_node` / `token_optimize` | 本规范代码化（超硬上限即 BLOCK，保留原文） |
| ④ recovery-handle 心智模型 | `enforce_node.original_text` | 本规范代码化（压缩必留原文） |
| ⑤ BM25 令牌预算打包 | `pack_context` | **本规范新增代码** |
| ⑥ S0–S4 风险分级 | `safety_class_of` | **本规范新增代码** |
| 流程级：自动校验与限制 | `enforce_node` + `gate_index` | **本规范新增代码** |

## 1. 预算配置 Schema（`_meta.json` 的 `budget` 段）

> 缺省合并 `token_budget.DEFAULT_BUDGET`；任何未显式配置字段一律回退默认值，避免配置缺失而放行超预算内容（强约束铁律）。

| 字段 | 类型 | 默认 | 语义 |
|---|---|---|---|
| `enabled` | bool | `true` | 总开关；`false` 时 `enforce_node`/`gate_index` 仅统计不阻断 |
| `node_caps` | map | 见下 | 各节点 per-node token 预算上限（估算 token） |
| `session_cap` | int | `30000` | 单会话全链路 token 合计上限 |
| `auto_optimize_nodes` | list | `["N4","N5","N7","N8"]` | 超预算时允许自动压缩的节点（写入前自动优化） |
| `auto_optimize_intensity` | str | `"full"` | 自动优化强度（lite/full/off，见 token_optimize） |
| `hard_cap_policy` | str | `"block"` | 超硬上限处置：`block`（阻断保留原文）/ `warn`（仅告警） |
| `critical_retention_min` | float | `0.90` | 安全关键类型关键事实保留率下限 |
| `safety_critical_types` | list | `["log","diff","code","json"]` | 关键事实保留率收紧的类型 |

`node_caps` 默认：`N1=2000 N2=1500 N3=1500 N4=4000 N5=6000 N6=3000 N7=4000 N8=4000`。

## 2. `enforce_node` 流程级强约束（写入前预算闸门）

> 在 COST_TRACK「落盘」**之前**调用：对节点 content 估算 token，超 `node_caps` 时按下列状态机处置。

```
enforce_node(record, meta, content):
  cap = node_caps[node_id]
  before = estimate_tokens(content)
  if cap is None:           → PASS（未配置该节点预算，仅记录）
  if before <= cap:         → PASS
  if before > cap:
    if node_id in auto_optimize_nodes:
        opt = run_optimize(content, "auto", intensity)
        if opt.after_tokens <= cap AND crit_retention >= critical_retention_min:
            → OPTIMIZED（用 opt.compressed_text 落盘，original_text 留作 recovery）
        else:
            → BLOCKED（hard_cap_policy=block） / WARN（=warn）   # fail-closed 保留原文
    else:
        → BLOCKED / WARN（超预算且未配自动优化）
```

**状态语义**：
- `PASS`：未超预算，原样落盘。
- `OPTIMIZED`：超预算但安全压缩至下限内且关键事实保留率达标，落盘压缩文本 + `original_text`（recovery）。
- `BLOCKED`：超硬上限且无法安全压缩（仍超限或保留率不达标），**fail-closed 保留原文**并阻断「无损放行」，交由人工/下游处置。
- `WARN`：`hard_cap_policy=warn` 时的非阻断等价物（保留原文 + 告警）。

**fail-closed 铁律**：`original_text` 始终随结果返回，绝不因压缩而丢失原文；`BLOCKED` 时绝不把压缩后仍超限/失真的文本当作「零收益」放行。

## 3. `gate_index` 全链路预算核查

> 在 COST_AUDIT 审计流程中调用：逐节点合计 vs `node_caps` + 逐会话合计 vs `session_cap`，产出违规报告 `{"passed", "violations", "node_totals", "session_totals"}`。`violations` 含 `level`（node/session）、`over`（超出量），供审计报告列为高消耗/超预算项。

## 4. ⑤ `pack_context`（BM25 式上下文裁剪）

> 蒸馏自 caveman `engine/contextwindow/contextwindow.go` 的 Pack 思路；纯 Python Okapi BM25 近似（k1=1.5, b=0.75，无 embedding/网络）。

`items: [{"id","text","priority"(0),"age_hours"(0),"error_signal"(False),"pinned"(False)}]`

- `score = BM25(query, item) + priority + exp(-age/half_life) + error_boost(0.8 if error) + pin_bonus(1e6 if pinned)`
- 按 score 降序贪心装袋至 `budget_tokens - reserve_tokens`；输出按**原始时序**重排（保持对话 chronology）。
- **fail-closed**：`error_signal` / `pinned` 项**强制保留**（即便超预算也不丢），与 caveman「错误信号 +ErrorBoost、Pin +1e6」一致。
- 适用：COST_TRACK 在 N4/N5 注入上下文前裁剪历史；COST_OPTIMIZE 对多段载荷做相关性优选。

## 5. ⑥ `safety_class_of`（S0–S4 风险分级）

> 蒸馏自 caveman `engine/safety/safety.go:14-48`。

| 等级 | 含义 | 触发 | 本 skill 处置 |
|---|---|---|---|
| S0 | 字节安全（元数据/记账） | 极小散文内容（≤120 token 估算） | 可自由摘要 |
| S1 | 提供商原生提示（缓存/路由） | config / tabular | 低风险，结构压缩 |
| S2 | 结构化（需 SDK 协作） | json | 结构压缩保错误键 |
| S3 | 行为级（eval-gated） | code / diff / 普通散文 | 压缩需评估门控 |
| S4 | 有损结构化（改模型可见字节，**必须 CCR**） | log / 含错误·不可逆·失败信号的散文 | 压缩 MUST 保留 recovery_handle（原文） |

`enforce_node` 在压缩 S4 内容且关键事实保留率不达标时，依 `hard_cap_policy` 阻断/告警（fail-closed）。

## 6. BSL 边界

本规范与 `token_budget.py` 仅执行 caveman 的 **MIT 方法层**（BM25 打分思路、S0–S4 分级概念、fail-closed 哲学）；**不打包**其 BSL-1.1 引擎（Go 代理/SQLite CCR 字节恢复/真实 tokenizer）。BM25 为纯 Python 近似实现，与 caveman 真实计数存在偏差（置信度：中 · 推断 inferred · 来源：基准报告 §3.2）。

## 7. CLI 速查

```bash
python scripts/token_budget.py --runsyntax                                  # 冒烟自检
python scripts/token_budget.py --enforce-node --node N5 --content-file p.txt # 单节点闸门
python scripts/token_budget.py --gate --index cost-index.jsonl              # 全链路核查
python scripts/token_budget.py --pack --items items.json --budget 4000 --query "修复登录"  # BM25 裁剪
python scripts/token_budget.py --safety --text "<日志>" --type auto          # S0–S4 分级
```
