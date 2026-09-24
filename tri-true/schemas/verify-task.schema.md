---
name: verify-task-schema
description: tri-true 验证任务数据模型 schema。定义 5 表结构（verify_tasks / confidence_assessments / source_verifications / multi_model_checks / reflection_revisions）+ 字段语义 + 状态机，供实现与校验对齐。
---

# tri-true 验证任务 Schema

> 本文件定义 tri-true 验证任务的数据模型，是 verify-index.db 与 verify-index.jsonl 的唯一权威定义。
> 实现时 MUST 严格对齐本 schema，NEVER 私自增删字段；扩展须经 SKILL.md §可扩展性 声明。

## 一、整体架构（5 表结构）

```
┌─────────────────┐     ┌──────────────────────┐
│  verify_tasks   │1───*│ confidence_assessments│
│  (主表)          │     │  (防线一)              │
└────────┬────────┘     └──────────────────────┘
         │1
         │
         │*              ┌──────────────────────┐
         ├──────────────>│ source_verifications  │
         │               │  (防线二)              │
         │               └──────────────────────┘
         │1
         │
         │*              ┌──────────────────────┐
         ├──────────────>│ multi_model_checks    │
         │               │  (防线三)              │
         │               └──────────────────────┘
         │1
         │
         │*              ┌──────────────────────┐
         └──────────────>│ reflection_revisions  │
                         │  (防线四)              │
                         └──────────────────────┘
```

主表 `verify_tasks` 一对多关联 4 张子表，分别对应四道防线产物。

## 二、表 1：verify_tasks（验证任务主表）

### 2.1 字段定义

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `verify_id` | string (UUID) | PK, 非空 | 验证任务唯一 ID |
| `task_name` | string | 非空 | 任务命名（`VERIFY_<日期>_<时间>_<会话ID>`） |
| `source_skill` | string | 非空 | 来源 skill（如 tri-ask / tri-content / user_direct） |
| `source_text` | text | 非空 | 待验证原文 |
| `source_text_hash` | string (sha256) | 非空 | 原文哈希（用于去重与查询） |
| `risk_level` | enum | 非空 | low / medium / high / critical |
| `domain` | enum | 非空 | medical / financial / legal / technical / general |
| `upstream_mode` | enum | 非空 | A_snapshot / B_install_prompt / C_degraded |
| `snapshot_ref` | string | 可选 | 关联快照路径（若 A 模式） |
| `hallucination_type` | enum | 非空 | factuality / faithfulness / mixed |
| `final_confidence` | float | 非空, [0,1] | 最终综合置信度 |
| `knowledge_type` | enum | 非空 | known / computed / inferred / iframe / common / guess（与置信度同层级并行属性） |
| `final_status` | enum | 非空 | verified / rejected / uncertain / human_review |
| `防线触发` | int | 非空, 1-4 | 触发到的最深防线 |
| `修订次数` | int | 非空, 0-3 | 防线四修订轮次 |
| `created_at` | ISO8601 | 非空 | 创建时间 |
| `updated_at` | ISO8601 | 非空 | 更新时间 |
| `schema_version` | int | 非空, 默认 1 | schema 版本 |

### 2.2 状态机

```
                        ┌─────────────────┐
        创建 ───────────>│   in_progress   │
                        └────────┬────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
        ┌───────────┐    ┌───────────┐    ┌───────────┐
        │ verified  │    │ uncertain │    │ rejected  │
        └───────────┘    └─────┬─────┘    └───────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ human_review │
                        └──────────────┘
```

| 状态 | 含义 | 触发条件 |
|------|------|----------|
| in_progress | 验证中 | 任务创建 |
| verified | 已验证通过 | 防线放行 + 置信度 ≥ 阈值 |
| uncertain | 不确定 | 置信度边界 + 无 T1/T2 支撑 |
| rejected | 已拒绝 | 置信度 < 0.5 且无 T1/T2，拒答 |
| human_review | 待人审 | critical 风险 + 置信 < 0.8 |

### 2.3 risk_level 语义

| 等级 | 含义 | 触发条件 | 处理 |
|------|------|----------|------|
| low | 低风险 | 一般信息查询 | 防线一即可放行 |
| medium | 中风险 | 技术文档、一般事实 | 防线一 + 防线二 |
| high | 高风险 | 医疗、法律、金融建议 | 四道防线全走 |
| critical | 关键风险 | YMYL、删除/发布/资金 | 四道防线 + 强制人审 |

## 三、表 2：confidence_assessments（防线一·置信度评估）

### 3.1 字段定义

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `assessment_id` | string (UUID) | PK | 评估 ID |
| `verify_id` | string (UUID) | FK, 非空 | 关联 verify_tasks |
| `paragraph_index` | int | 非空 | 段落索引（段级评估） |
| `paragraph_text` | text | 非空 | 段落原文 |
| `vc_score` | float | 非空, [0,1] | Verbalized Confidence（LLM 自评把握度 / 100） |
| `sc_score` | float | 非空, [0,1] | Self-Consistency（N 次采样 top-k 一致度） |
| `sc_samples` | int | 非空 | 采样次数 N（默认 5） |
| `cc_score` | float | 非空, [0,1] | Calibrated Confidence（VC × 校准系数 k） |
| `calibration_model` | string | 非空 | 校准所用模型名 |
| `ece_value` | float | 非空, [0,1] | 该模型 ECE（期望校准误差） |
| `composite_confidence` | float | 非空, [0,1] | 综合置信 `0.4×VC + 0.3×SC + 0.3×CC` |
| `knowledge_type` | enum | 非空 | known / computed / inferred / iframe / common / guess（与置信度同层级并行属性，决定验证路由） |
| `threshold` | float | 非空, [0,1] | 当前段落阈值（按 risk_level） |
| `verdict` | enum | 非空 | pass（≥阈值且知识类型允许放行）/ fail（<阈值或 guess 类型需进一步验证） |
| `created_at` | ISO8601 | 非空 | 创建时间 |

### 3.2 阈值矩阵（按 risk_level）

| risk_level | 高置信阈值（放行） | 低置信阈值（触发防线二） |
|------------|-------------------|--------------------------|
| low | ≥ 0.7 | < 0.7 |
| medium | ≥ 0.75 | < 0.75 |
| high | ≥ 0.85 | < 0.85 |
| critical | ≥ 0.9 | < 0.9 |

### 3.3 综合置信度公式

```
composite_confidence = 0.4 × vc_score + 0.3 × sc_score + 0.3 × cc_score
```

- VC：LLM 直接自评「我对这段的把握度（0-100）」/ 100
- SC：N 次采样（默认 5），top-k 答案一致度 = max_count / N
- CC：VC × k，其中 k = 1 - ECE（ECE 越大，k 越小，置信度越被压低）

### 3.4 知识类型分类（与置信度同层级并行属性）

> 每个段落 MUST 在置信度评估的**同时**标注知识类型。知识类型与置信度是**同级并行属性**——置信度回答"多确信"，知识类型回答"确信的依据是什么"。二者共同决定验证路由与放行策略。

| knowledge_type | 名称 | 含义 | 验证路由 | 放行条件 |
|----------------|------|------|----------|----------|
| `known` | 事实 | 可从权威信源直接检索的既定事实 | 防线二（RAG 检索 T1/T2） | T1/T2 支撑即可 |
| `computed` | 计算 | 通过数学/逻辑运算得出 | 重算验证（独立计算复核） | 重算结果一致 |
| `inferred` | 推断 | 基于已知前提逻辑推导 | 防线三（多模型）+ 防线四（自反思） | 强共识或修订达标 |
| `iframe` | 框架 | 基于特定框架/范式/结构推导 | 框架一致性验证 + 防线三 | 框架内自洽 + 多模型一致 |
| `common` | 常识 | 广泛认可的通识，无需信源 | 常识校验（轻量，防线一即可） | 置信度 ≥ 阈值 |
| `guess` | 猜测 | 无确凿依据的推断 | 四道防线全走 + 人审兜底 | NEVER 仅凭置信度放行 |

### 3.5 知识类型与置信度联合判定矩阵

| knowledge_type | 高置信（≥阈值） | 中置信 | 低置信（<阈值） |
|----------------|-----------------|--------|------------------|
| `known` | 防线一放行 | 防线二验证 | 防线二验证 |
| `computed` | 重算验证 | 重算验证 | 重算验证 |
| `inferred` | 防线三验证 | 防线三 + 防线四 | 防线四 + 兜底 |
| `iframe` | 框架验证 | 框架验证 + 防线三 | 防线三 + 防线四 |
| `common` | 防线一放行 | 防线一放行 | 防线二验证 |
| `guess` | 防线三 + 人审 | 防线四 + 人审 | 兜底（拒答/多答案） |

> **铁律**：`guess` 类型 NEVER 仅凭置信度单独放行，MUST 经多模型交叉验证 + 人审兜底。

## 四、表 3：source_verifications（防线二·事实源验证）

### 4.1 字段定义

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `verification_id` | string (UUID) | PK | 验证 ID |
| `verify_id` | string (UUID) | FK, 非空 | 关联 verify_tasks |
| `paragraph_index` | int | 非空 | 段落索引 |
| `claim_text` | text | 非空 | 待验证主张（句级） |
| `citation_marker` | string | 非空 | 引用标记（如 [1], [2]） |
| `source_url` | string | 非空 | 信源 URL |
| `source_title` | string | 非空 | 信源标题 |
| `source_tier` | enum | 非空 | T1 / T2 / T3 / T4 |
| `relevance_score` | float | 非空, [0,1] | 相关性分 |
| `credibility_score` | float | 非空, [0,1] | 可信度分（按 tier） |
| `freshness_score` | float | 非空, [0,1] | 时效分 |
| `weighted_score` | float | 非空, [0,1] | 加权得分 |
| `supporting_excerpt` | text | 非空 | 支撑片段 |
| `verification_status` | enum | 非空 | supported / refuted / partial / no_source |
| `created_at` | ISO8601 | 非空 | 创建时间 |

### 4.2 可信度加权公式

```
weighted_score = α × relevance_score + β × credibility_score + γ × freshness_score
```

- 默认 α=0.4, β=0.4, γ=0.2
- credibility_score 按 tier：T1=1.0, T2=0.8, T3=0.5, T4=0.2

### 4.3 verification_status 语义

| 状态 | 含义 | 处理 |
|------|------|------|
| supported | 信源支撑该主张 | T1/T2 支撑 → verified |
| refuted | 信源反驳该主张 | 标记 hallucination |
| partial | 部分支撑 | 触发防线三 |
| no_source | 无信源 | 触发防线三 |

## 五、表 4：multi_model_checks（防线三·多模型交叉验证）

### 5.1 字段定义

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `check_id` | string (UUID) | PK | 检查 ID |
| `verify_id` | string (UUID) | FK, 非空 | 关联 verify_tasks |
| `paragraph_index` | int | 非空 | 段落索引 |
| `claim_text` | text | 非空 | 待验证主张 |
| `model_name` | string | 非空 | 模型名 |
| `model_family` | string | 非空 | 架构家族（GPT / Claude / Llama / Qwen / 等） |
| `is_open_source` | bool | 非空 | 是否开源 |
| `model_answer` | text | 非空 | 模型回答 |
| `model_confidence` | float | 非空, [0,1] | 模型自评置信 |
| `historical_accuracy` | float | 非空, [0,1] | 历史准确度 |
| `self_assessment_ability` | float | 非空, [0,1] | 自评能力（ECE 反向） |
| `uaf_weight` | float | 非空, [0,1] | UAF 权重 = historical_accuracy × self_assessment_ability |
| `agreement_score` | float | 非空, [0,1] | 与多数派一致度 |
| `created_at` | ISO8601 | 非空 | 创建时间 |

### 5.2 UAF 加权融合公式

```
final_answer = argmax(Σ uaf_weight_i × model_confidence_i × agreement_score_i)
```

### 5.3 共识阈值判定

| 共识类型 | 条件 | 判定 |
|----------|------|------|
| 强共识 | 所有模型一致 + 均 ≥ 0.7 | verified |
| 弱共识 | ≥ 2/3 模型一致 | verified + 标注 "N 模型验证" |
| 分歧 | < 2/3 一致 | 触发防线四 |

### 5.4 异构要求校验

- 参与模型 MUST ≥ 3 个
- 供应商 MUST ≥ 2 家
- 开源模型 MUST ≥ 1 个
- 架构家族 MUST ≥ 2 种

## 六、表 5：reflection_revisions（防线四·自我反思修正）

### 6.1 字段定义

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `revision_id` | string (UUID) | PK | 修订 ID |
| `verify_id` | string (UUID) | FK, 非空 | 关联 verify_tasks |
| `paragraph_index` | int | 非空 | 段落索引 |
| `round` | int | 非空, 1-3 | 修订轮次 |
| `method` | enum | 非空 | cove / reflexion / critique_refine |
| `extracted_claims` | text[] | 非空 | 提取的主张列表（CoVe 阶段） |
| `verification_queries` | text[] | 非空 | 验证查询列表 |
| `evidence_found` | text | 非空 | 检索到的证据 |
| `original_answer` | text | 非空 | 原始回答 |
| `revised_answer` | text | 非空 | 修订后回答 |
| `original_confidence` | float | 非空, [0,1] | 原始置信度 |
| `revised_confidence` | float | 非空, [0,1] | 修订后置信度 |
| `reflection_notes` | text | 可选 | 反思笔记（Reflexion thought） |
| `critique_notes` | text | 可选 | 核查员评语（Critique 阶段） |
| `verdict` | enum | 非空 | pass（≥阈值）/ fail（<阈值，下一轮或兜底） |
| `created_at` | ISO8601 | 非空 | 创建时间 |

### 6.2 修订轮次状态机

```
轮次 1 (CoVe) ──pass──> 交付
        │
        fail
        ▼
轮次 2 (Reflexion) ──pass──> 交付
        │
        fail
        ▼
轮次 3 (Critique-Refine) ──pass──> 交付
        │
        fail
        ▼
兜底（拒答 / 多答案 / 人审）
```

## 七、校验规则

1. **verify_id 一致性**：5 表的 verify_id MUST 与主表 verify_tasks.verify_id 一致。
2. **段落索引连续**：同一 verify_id 下的 paragraph_index MUST 从 0 连续递增。
3. **防线触发顺序**：防线触发 MUST 按顺序 1→2→3→4，不可跳过（除非高置信 + common/known 类型直接放行）。
4. **置信度范围**：所有 *_confidence / *_score 字段 MUST ∈ [0, 1]。
5. **knowledge_type 取值受限**：仅 known / computed / inferred / iframe / common / guess。
6. **knowledge_type 必填**：verify_tasks 和 confidence_assessments 的 knowledge_type MUST 非空，与 composite_confidence 同级并行。
7. **guess 放行限制**：knowledge_type=guess 时，NEVER 仅凭 composite_confidence ≥ 阈值放行，MUST 经多模型交叉验证 + 人审兜底。
8. **tier 取值受限**：source_tier 仅 T1/T2/T3/T4。
9. **method 取值受限**：method 仅 cove / reflexion / critique_refine，且轮次与 method 对应（1→cove, 2→reflexion, 3→critique_refine）。
10. **异构要求**：multi_model_checks 同一 verify_id 下 MUST 满足异构要求（≥3 模型 / ≥2 供应商 / ≥1 开源 / ≥2 架构家族）。
11. **修订轮次上限**：reflection_revisions 同一 verify_id 下最多 3 条记录。
12. **人审触发**：risk_level=critical 且 final_confidence < 0.8 时，final_status MUST 为 human_review；knowledge_type=guess 且 risk_level≥high 时，final_status MUST 为 human_review。

## 八、命名规范

- 索引文件：`verify-index.db`（SQLite 主索引）+ `verify-index.jsonl`（JSONL 增量日志）
- 存放目录：`.tribro/true/verify-index.db` + `.tribro/true/verify-index.jsonl`
- 双轨容灾：每次写入 MUST 同时写 SQLite 和 JSONL，任一失败 MUST 告警

## 九、扩展规则

新增字段或表须经 `VERIFY_ADMIN` 命令，自动校验 schema 后入库。直接编辑 JSONL 文件也允许，但下次加载时 MUST 重新校验。schema_version 升级时 MUST 提供迁移脚本。
