# tri-cost（成本审计）

> 横向方法论型 skill：统计从用户提问到最终答案全过程每个关键节点的 token 消耗，逐节点评估「是否必要 / 是否可优化 / 改进建议」，产出成本审计报告；并主动执行token 节省方法论（输出风格压缩 + 载荷类型感知摘要），产出前后 token 消耗对比与内容准确性对比，反哺优化提问与 skill。

## 特性

- **全链路分账**：标准链路八节点（N1–N8）逐节点记录 token 消耗，绝不"总消耗一笔带过"。
- **逐节点三问**：每个节点输出 必要性 / 可优化性 / 改进建议 三要素。
- **成本估算**：按模型单价（输入/输出可区分）估算成本，见 `_meta.json` price 表。
- **高消耗标记**：超阈值节点自动标记并发起针对性建议（阈值/比例可调）。
- **主动节省 + 前后对比（COST_OPTIMIZE）**：通过 `scripts/token_optimize.py` 主动执行蒸馏方法论（输出风格压缩 + 13 类载荷感知摘要），并量化**前后 token 消耗对比**（before/after/saved_pct）与**内容准确性对比**（原子事实保留率 + 关键事实保障），fail-closed 保内容不丢。
- **代码级预算闸门（COST_BUDGET · 强约束）**：通过 `scripts/token_budget.py` 把 token 节省方法论落成**代码级强约束**——不是 md 口头约定，而是流程中"自动校验与限制" token 使用：`enforce_node` 在节点内容落盘前对超预算的 N4/N5/N7/N8 自动压缩并校验前后 token 与内容准确性（超硬上限则 fail-closed 阻断保留原文），`gate_index` 在审计时做全链路（per-node + session）预算核查，`pack_context` 做 BM25 式上下文裁剪（错误/钉住项强制保留），`safety_class_of` 做 S0–S4 风险分级。预算配置单一真源为 `_meta.json` 的 `budget` 段。
- **降本闭环**：报告 → 建议 → 落地 → 基线对比再审计，长期高消耗节点作为 tri-evolve 优化信号。
- **隐私过滤**：密钥模式命中即脱敏，敏感度过高不记录节点原文。
- **蒸馏知识底座 + 方法论落地**：引入 `references/caveman-distill.md`（架构/模块/流程/对比/13类载荷摘要/输出风格规则，方法底座），并由 `scripts/token_optimize.py` 落地为可执行动作（caveman 为 BSL-1.1 引擎，本 skill 仅引用 MIT 方法、不打包其运行时）。

## 目录结构

```
tri-cost/
├── SKILL.md                          主入口：成本审计契约 + 全链路分账 + 逐节点三问 + 主动节省方法论执行 + 降本闭环
├── README.md                         本文档
├── CHANGELOG.md                      Keep a Changelog + SemVer
├── _meta.json                        平台元数据 + 模型单价/阈值/基线配置
├── references/
│   ├── cost-model.md                 节点划分/评估维度/建议类型速查（单一事实源）
│   ├── caveman-distill.md            蒸馏自 caveman 的 token 节省方法论（架构/模块/流程/对比/13类载荷摘要/输出风格规则，方法底座）
│   ├── budget-spec.md               token 预算闸门规范（COST_BUDGET：schema + 状态机，代码级强约束）
│   └── version-check-spec.md         版本检查与更新规范（内部唯一真源）
├── scripts/
│   ├── cost_eval.py                  token 聚合/成本估算/高消耗标记/ROI 评分（确定性逻辑）
│   ├── token_optimize.py             主动 token 节省方法论执行器（detect/compress/count/accuracy/recovery 前后对比，蒸馏自 caveman）
│   ├── token_budget.py              token 预算闸门与自动优化执行器（enforce_node/gate_index/pack_context/safety_class，代码级强约束）
│   └── check_update.py               版本检查与更新（家族同源，按 --slug 适配）
└── tests/
    └── tri-cost-full-testcases.md    全场景全能力测试用例（审计版）
```

## 安装

从 skillhub 安装（与家族其它 skill 一致）：

```bash
skillhub install tri-cost              # 安装到默认平台 skills 目录
skillhub install tri-cost --dir <目标目录>   # 指定安装目录
```

安装后即可斜杠激活 `tri-cost`。

## 使用

| 模式 | 触发 | 说明 |
|------|------|------|
| `COST_TRACK` | cost-hook 在各关键节点触发 | 记录单节点 token 消耗 |
| `COST_AUDIT` | 用户显式调用（"统计一下花了多少 token"） | 全链路汇总 + 逐节点三问 + 成本报告 |
| `COST_OPTIMIZE` | 用户显式调用（"帮我把这段输出/日志压缩一下"） | 执行蒸馏方法论 + 前后 token/准确性对比 |
| `COST_ADMIN` | 用户管理命令（stats/基线/阈值/单价/history） | 管理成本基线/阈值/模型单价/历史 |

**审计示例**：

```
python scripts/cost_eval.py --index .tribro/cost/cost-index.jsonl --report .tribro/cost/audit
```

**主动节省 + 前后对比示例**：

```
python scripts/token_optimize.py --input payload.txt --type auto --intensity full --report .tribro/cost/optimize/report.json
# 输出：detected_type / before_tokens / after_tokens / saved_pct / 内容准确性(retention + 关键事实保障) / 压缩文本 / 告警
```

**代码级预算闸门示例**：

```
# 单节点写入前闸门（超预算自动优化 / 超硬上限 fail-closed 阻断）
python scripts/token_budget.py --enforce-node --node N5 --content-file payload.txt

# 全链路预算核查（per-node + session 违规报告）
python scripts/token_budget.py --gate --index .tribro/cost/cost-index.jsonl

# BM25 式上下文裁剪（错误/钉住项强制保留）
python scripts/token_budget.py --pack --items items.json --budget 4000 --query "修复登录失败"

# S0–S4 风险分级
python scripts/token_budget.py --safety --text "<日志>" --type auto
```

## 测试

全场景测试用例见 `tests/tri-cost-full-testcases.md`；确定性算法冒烟：

```
python scripts/cost_eval.py --runsyntax
```

## 运行时落盘（`.tribro/cost/`）

```
.tribro/cost/
├── cost-index.db            SQLite 成本索引（WAL）
├── cost-index.jsonl         JSONL 增量日志（容灾）
├── meta.json                配置（模型单价/阈值/基线）
└── <命名>/
    ├── cost-report.md       成本审计报告
    └── baseline.json        基线快照
```

## 设计原则

- **观测与主动执行结合**：COST_AUDIT 只"观测与建议"；COST_OPTIMIZE 主动执行蒸馏方法论（输出风格压缩 + 载荷感知摘要）并量化前后对比。执行限于纯 Python 方法论层，不打包 caveman 的 Go 运行时。
- **确定性下沉**：聚合/估算/标记/ROI 在 `scripts/cost_eval.py`；detect/compress/count/accuracy/recovery 在 `scripts/token_optimize.py`；预算闸门/自动优化/BM25 裁剪/S0–S4 分级在 `scripts/token_budget.py`；SKILL.md 不内联算法。
- **代码级强约束**：token 预算以 `scripts/token_budget.py` 落实为可执行闸门（写入前自动优化 + 全链路核查 + fail-closed 阻断），配置单一真源为 `_meta.json` 的 `budget` 段；md 文档仅作规范说明，不替代代码校验。
- **参考表外移**：节点/评估/建议类型在 `references/cost-model.md` 单点维护。
- **fail-closed**：任何压缩/摘要不确定或命中安全信号即保留原文或显式告警，绝不伪造"零 token 收益"。