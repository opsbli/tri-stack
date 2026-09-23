# Changelog（tri-cost）

All notable changes to this project will be documented in this file.

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.3.0] - 2026-09-19

### 新增

- **代码级 token 预算闸门（COST_BUDGET · 强约束）**：把 token 节省方法论落成**代码级强约束**（非仅 md 口头约定），确保 token 使用在流程中被**自动校验与限制**。新增 `scripts/token_budget.py`（纯 Python、零外部运行时，复用 `token_optimize.py` 的 detect/compress/count/accuracy/recovery）。
  - **`enforce_node`（写入前闸门）**：COST_TRACK 在节点内容落盘前调用；超 `node_caps` 的 N4/N5/N7/N8 自动执行 token_optimize 压缩并校验前后 token 与关键事实保留率；超硬上限或保留率不达标按 `hard_cap_policy`（block 阻断 / warn 告警）处置，fail-closed 始终保留 `original_text`。
  - **`gate_index`（全链路核查）**：COST_AUDIT 调用，逐节点合计 vs `node_caps` + 逐会话合计 vs `session_cap`，产出违规报告（含 `over` 超出量）。
  - **报告待优化点全覆盖**：① 输出风格压缩 / ② 13 类载荷 detect / ③ fail-closed / ④ recovery-handle（token_optimize 已落地）；**⑤ BM25 令牌预算打包**（`pack_context`，k1=1.5,b=0.75，错误/钉住项强制保留）/ **⑥ S0–S4 风险分级**（`safety_class_of`）由本脚本代码化。
- **预算配置单一真源**：`_meta.json` 新增 `budget` 段（`node_caps` / `session_cap` / `auto_optimize_nodes` / `auto_optimize_intensity` / `hard_cap_policy` / `critical_retention_min` / `safety_critical_types`），缺省合并安全默认值。
- **规范文档**：新增 `references/budget-spec.md`（预算 schema + enforce_node/gate_index/pack_context/safety_class 状态机，代码级强约束唯一真源）。
- **执行链集成**：强制契约新增第 10 条「预算闸门强约束」铁律；COST_TRACK 流程新增"写入前预算闸门"步骤；COST_AUDIT 流程新增"预算闸门核查"步骤；SKILL.md 新增「token 预算闸门（COST_BUDGET · 代码级强约束）」小节。

### 变更

- **保持 BSL 边界**：BM25 为纯 Python 近似（非 caveman 真实 tokenizer/embedding）；仍不打包 caveman Go 运行时（置信度：中；依据：推断 inferred；来源：基准报告 §3.2/§3.3）。
- **版本联动**：SKILL.md / README / `_meta.json` / tests frontmatter 同步至 1.3.0。

## [1.2.0] - 2026-09-19

### 新增

- **主动节省方法论执行（COST_OPTIMIZE 模式）**：tri-cost 从"只观测建议"升级为"主动执行 + 量化前后对比"。新增 `scripts/token_optimize.py`，蒸馏 caveman 的 token 节省方法论（输出风格压缩 + 13 类载荷感知摘要）落成确定性可执行逻辑：detect（启发式识别载荷类型，fail-open 归 text）→ compress（类型级摘要 + 风格压缩）→ count（前后 token 估算）→ accuracy（原子事实保留率 + 关键事实保障）→ recovery（recovery_handle，原文可找回）→ report。
- **前后对比产物**：COST_OPTIMIZE MUST 输出 (a) token 消耗对比（before/after_tokens + saved_pct）；(b) 内容准确性对比（retention_pct + critical_fact_retention_pct + dropped_facts_sample）。新增 `COST_<命名>.md` 前后对比报告结构。
- **Auto-Clarity 回退 + fail-closed**：命中安全/不可逆信号不压风格并告警；关键事实保留率不达标（安全关键类型 <90%）保留原文或标注「未压缩」，绝不伪造零收益。
- **触发时机与流程扩展**：触发表与处理流程新增 COST_OPTIMIZE 分支；职责边界重构为"账房层 + 节流执行层（methodology）"；强制契约第 9 条新增"主动优化必出对比"铁律。

### 变更

- **保持 BSL 边界**：仍不打包 caveman 运行时（Go 代理/引擎/SQLite CCR），仅执行其 MIT 方法层（置信度：中；依据：推断 inferred；来源：基准报告 §9 / caveman-distill §九）。
- **版本联动**：SKILL.md / README / `_meta.json` / tests frontmatter 同步至 1.2.0。

## [1.1.0] - 2026-09-19

### 新增

- **蒸馏知识底座**：新增 `references/caveman-distill.md`，蒸馏自开源项目 caveman（JuliusBrussee/caveman, v2.7.0）的 token 节省方法论——核心架构、关键模块、执行流程、依赖、接口与设计决策，含与 tri-cost 全面对比（节流层 vs 账房层）及可蒸馏 / 不可蒸馏边界；作为降本增效建议的方法来源。
- **降本增效建议扩展**：在 `references/cost-model.md` 建议类型速查新增「输出风格压缩」「载荷类型感知摘要」两类可执行动作；SKILL.md 新增「token 节省方法论参考（蒸馏自 caveman）」小节与 caveman 边界声明。

### 变更

- **保持定位不变**：tri-cost 仍只观测与评估 token 消耗，不落地省 token 改造、不引入 Go 运行时；caveman 引擎为 BSL-1.1，仅引用其 MIT 方法，不复制源码。
- **版本联动**：SKILL.md / README / `_meta.json` / tests frontmatter 同步至 1.1.0。

## [1.0.1] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手意图识别、省 token 改造落地、缓存复用与学习调优，只观测评估 token 消耗，转出/归属对应 skill 呼应家族 MECE。

## [1.0.0] - 2026-08-15

### 新增

- 首个版本：横向方法论型 token 成本审计 skill。
- 全链路分账：标准链路八节点（N1–N8）逐节点记录 token 消耗。
- 逐节点三问：必要性 / 可优化性 / 改进建议 三要素评估。
- 成本估算与高消耗标记：按模型单价分账，超阈值节点自动标记（`scripts/cost_eval.py`）。
- 降本增效闭环：报告 → 建议 → 基线对比 → 再审计。
- 三大模式：COST_TRACK（节点取样）/ COST_AUDIT（全链路审计）/ COST_ADMIN（管理）。
- 版本检查与更新机制：自包含 `scripts/check_update.py` + `references/version-check-spec.md`。