---
name: model-schema
description: tri-true 模型池数据模型 schema。定义异构要求（≥2 供应商 + ≥1 开源）+ UAF 权重字段 + 校准关联，供 models.json 与实现校验对齐。
---

# tri-true 模型池 Schema

> 本文件定义 tri-true 模型池的数据模型，是 models.json 的唯一权威定义。
> 实现时 MUST 严格对齐本 schema，NEVER 私自增删字段；扩展须经 SKILL.md §可扩展性 声明。

## 一、JSON 整体结构

```json
{
  "schema_version": 1,
  "models": [
    {
      "name": "<模型名，必填，唯一>",
      "vendor": "<供应商，必填>",
      "family": "<架构家族，必填>",
      "is_open_source": "<bool，必填>",
      "historical_accuracy": "<0-1，必填>",
      "self_assessment_ability": "<0-1，必填>",
      "ece": "<0-1，必填，期望校准误差>",
      "brier_score": "<0-1，必填>",
      "calibration_k": "<float，必填，校准系数>",
      "api_endpoint": "<API 端点，可选>",
      "api_key_env": "<环境变量名，可选>",
      "max_tokens": "<int，默认 4096>",
      "temperature": "<float，默认 0.0>",
      "cost_per_1k_tokens": "<float，可选>",
      "latency_p95_ms": "<int，可选>",
      "status": "<active|inactive，默认 active>",
      "notes": "<备注，可选>"
    }
  ],
  "pool_requirements": {
    "min_models": 3,
    "min_vendors": 2,
    "min_open_source": 1,
    "min_families": 2
  }
}
```

## 二、字段语义规约

### 2.1 必填字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `name` | string | 非空，唯一 | 模型名（如 gpt-4o / claude-3.5-sonnet / llama-3.1-70b） |
| `vendor` | string | 非空 | 供应商（OpenAI / Anthropic / Meta / Alibaba / 等） |
| `family` | string | 非空 | 架构家族（GPT / Claude / Llama / Qwen / Mistral / 等） |
| `is_open_source` | bool | 非空 | 是否开源（影响异构要求校验） |
| `historical_accuracy` | float | [0,1] | 历史准确度（基于 TruthfulQA/FActScore 等基准） |
| `self_assessment_ability` | float | [0,1] | 自评能力（1 - ECE，ECE 越低自评越准） |
| `ece` | float | [0,1] | 期望校准误差（越小越准） |
| `brier_score` | float | [0,1] | Brier 分数（越小越准） |
| `calibration_k` | float | 非空 | 校准系数 k（用于 CC = VC × k） |

### 2.2 可选字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_endpoint` | string (URL) | "" | API 端点 |
| `api_key_env` | string | "" | API key 环境变量名 |
| `max_tokens` | int | 4096 | 最大 token 数 |
| `temperature` | float | 0.0 | 采样温度（验证场景建议 0.0） |
| `cost_per_1k_tokens` | float | 0 | 每千 token 成本（用于成本控制） |
| `latency_p95_ms` | int | 0 | P95 延迟（ms） |
| `status` | enum | "active" | active / inactive |
| `notes` | string | "" | 备注 |

## 三、UAF 权重计算

每个模型的 UAF 权重：

```
uaf_weight = historical_accuracy × self_assessment_ability
```

- `historical_accuracy`：基于历史验证任务的准确度（TruthfulQA/FActScore 等基准 + 实际任务统计）
- `self_assessment_ability`：自评能力，= 1 - ECE（ECE 越小，自评越准，权重越高）

### 3.1 UAF 加权融合

防线三对多个模型的回答进行 UAF 加权融合：

```
final_answer = argmax(Σ uaf_weight_i × model_confidence_i × agreement_score_i)
```

- `uaf_weight_i`：第 i 个模型的 UAF 权重
- `model_confidence_i`：第 i 个模型的自评置信度（VC）
- `agreement_score_i`：第 i 个模型与多数派的一致度

## 四、异构要求校验

模型池 MUST 满足异构性，避免同源模型的系统性偏差：

| 要求 | 最小值 | 说明 |
|------|--------|------|
| 模型数 | ≥ 3 | 参与单次验证的模型数下限 |
| 供应商数 | ≥ 2 | 避免单供应商偏差 |
| 开源模型数 | ≥ 1 | 开源模型提供独立验证路径 |
| 架构家族数 | ≥ 2 | 不同架构家族降低同质化风险 |

### 4.1 异构性示例

```json
{
  "models": [
    {"name": "gpt-4o", "vendor": "OpenAI", "family": "GPT", "is_open_source": false},
    {"name": "claude-3.5-sonnet", "vendor": "Anthropic", "family": "Claude", "is_open_source": false},
    {"name": "llama-3.1-70b", "vendor": "Meta", "family": "Llama", "is_open_source": true}
  ]
}
```

满足：3 模型 / 3 供应商 / 1 开源 / 3 家族。

## 五、校准系数关联

每个模型的 `calibration_k` 与 `calibration.json` 关联：

| 字段 | 来源 | 用途 |
|------|------|------|
| `name` | models.json | 模型唯一标识 |
| `ece` | models.json + calibration.json | 期望校准误差（定期重算） |
| `brier_score` | calibration.json | Brier 分数 |
| `calibration_k` | calibration.json | 校准系数 k = 1 - ECE |

`VERIFY_ADMIN calibrate --model <name>` 命令重算 ECE/Brier/k 后，MUST 同步更新 models.json 和 calibration.json。

## 六、共识阈值判定

### 6.1 共识类型

| 共识类型 | 条件 | 判定 | 标注 |
|----------|------|------|------|
| 强共识 | 所有模型一致 + 均 ≥ 0.7 | verified | "N 模型强共识" |
| 弱共识 | ≥ 2/3 模型一致 | verified | "N 模型弱共识（M 同意 / K 总数）" |
| 分歧 | < 2/3 一致 | 触发防线四 | "模型分歧，进入自反思" |

### 6.2 冲突解决策略

当模型分歧时，按以下优先级解决：

1. **T1/T2 裁决**：若事实源验证已获 T1/T2 支撑，以事实源为准，模型分歧仅作参考。
2. **置信度加权投票**：按 `uaf_weight × model_confidence` 加权投票，取加权多数派。
3. **保守拒答**：若加权投票仍无明确多数派（差距 < 0.1），标记 uncertain，触发防线四或兜底。

## 七、状态机

```
active ──API 失效──> inactive ──API 恢复──> active
```

| 状态 | 含义 | 处理 |
|------|------|------|
| active | 活跃 | 可参与多模型验证 |
| inactive | 失效 | API 不可用，临时退出模型池 |

## 八、成本控制

- **单任务调用上限**：默认 5 次（防线三 3 模型 + 防线四 2 次重试）
- **超限降级**：超 5 次降级为单模型 + 自反思
- **成本统计**：每次调用记录 `cost_per_1k_tokens × 实际 token 数`，累计到任务成本
- **成本告警**：单任务成本 > 阈值（默认 $0.5）时告警

## 九、校验规则

1. **name 唯一性**：同一 name 在 models 数组中 MUST 唯一。
2. **vendor 非空**：每个模型 MUST 有 vendor。
3. **family 非空**：每个模型 MUST 有 family。
4. **historical_accuracy 范围**：MUST ∈ [0,1]。
5. **ece 范围**：MUST ∈ [0,1]，越小越好。
6. **calibration_k 公式**：MUST = 1 - ece（允许微调，但需 notes 说明）。
7. **异构要求**：模型池整体 MUST 满足 §四 异构要求（active 模型数 ≥ 3 / 供应商 ≥ 2 / 开源 ≥ 1 / 家族 ≥ 2）。
8. **API key 环境变量**：api_key_env 引用的环境变量 MUST 在运行时存在（active 模型）。
9. **status 取值受限**：仅 active / inactive。

## 十、命名规范

文件名固定为 `models.json`，存放于：
- 安装目录：`tri-true/templates/models.json`（默认模型池）
- 运行时：`.tribro/true/models.json`（用户自定义模型池，可覆盖默认）

加载顺序：用户自定义优先 > 默认。

## 十一、扩展规则

新增模型须经 `VERIFY_ADMIN models add` 命令，自动校验 schema 后入池。直接编辑 JSON 文件也允许，但下次加载时 MUST 重新校验。新增模型后 MUST 重新校验异构要求是否仍满足。
