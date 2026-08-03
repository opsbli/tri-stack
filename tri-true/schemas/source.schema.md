---
name: source-schema
description: tri-true 信源数据模型 schema。定义 T1-T4 四级分级 + 可信度权重 + 加权公式字段，供 sources.json 与实现校验对齐。
---

# tri-true 信源 Schema

> 本文件定义 tri-true 信源库的数据模型，是 sources.json 的唯一权威定义。
> 实现时 MUST 严格对齐本 schema，NEVER 私自增删字段；扩展须经 SKILL.md §可扩展性 声明。

## 一、JSON 整体结构

```json
{
  "schema_version": 1,
  "sources": [
    {
      "url": "<信源 URL，必填，唯一>",
      "title": "<信源标题，必填>",
      "tier": "<T1|T2|T3|T4，必填>",
      "domain": "<medical|financial|legal|technical|general|all，必填>",
      "credibility_score": "<可信度分 0-1，必填>",
      "freshness_score": "<时效分 0-1，默认 1.0>",
      "last_verified_at": "<ISO8601，最后验证时间>",
      "description": "<信源描述，可选>",
      "access_method": "<api|crawl|static，默认 crawl>",
      "access_config": {
        "api_key_env": "<环境变量名，可选>",
        "rate_limit": "<QPS 限制，可选>",
        "headers": {}
      },
      "status": "<active|inactive|deprecated，默认 active>",
      "notes": "<备注，可选>"
    }
  ]
}
```

## 二、字段语义规约

### 2.1 必填字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `url` | string (URL) | 非空，唯一 | 信源 URL（含协议） |
| `title` | string | 非空 | 信源标题（人类可读） |
| `tier` | enum | "T1"\|"T2"\|"T3"\|"T4" | 信源分级（详见 §三） |
| `domain` | enum | medical\|financial\|legal\|technical\|general\|all | 适用领域 |
| `credibility_score` | float | [0,1] | 可信度分（默认按 tier，可手动调整） |

### 2.2 可选字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `freshness_score` | float | 1.0 | 时效分（1.0=最新，递减） |
| `last_verified_at` | ISO8601 | null | 最后验证时间 |
| `description` | string | "" | 信源描述 |
| `access_method` | enum | "crawl" | api / crawl / static |
| `access_config` | object | {} | 访问配置（API key 环境变量/QPS/headers） |
| `status` | enum | "active" | active / inactive / deprecated |
| `notes` | string | "" | 备注 |

## 三、四级信源分级语义

| Tier | 类型 | 默认 credibility_score | 信源特征 | 示例 |
|------|------|------------------------|----------|------|
| **T1** | 权威事实类 | 1.0 | 不可辩驳的事实源头：法律法规、政府公报、官方 API 文档、ISO/IEEE 标准 | https://www.iso.org/standard.html |
| **T2** | 权威观点类 | 0.8 | 经同行评议或权威机构背书：研究机构报告、同行评议论文、内部审核方案 | https://arxiv.org/abs/2024.xxxxx |
| **T3** | 一般参考类 | 0.5 | 公开发布但未严格评议：媒体报道、行业文章、技术博客 | https://medium.com/@xxx/article |
| **T4** | 待验证类 | 0.2 | 匿名或营销驱动：论坛帖子、营销内容、匿名贡献 | https://forum.xxx.com/t/123 |

### 3.1 tier 升降规则

- **T3→T2 升级**：一般参考类经同行评议或权威机构背书后，可升级为 T2。
- **T2→T1 升级**：权威观点类经时间检验成为事实标准后，可升级为 T1。
- **T3→T4 降级**：一般参考类被发现有利益冲突或营销驱动，降级为 T4。
- **任何 tier → deprecated**：信源失效（404）或内容被撤回，status 标 deprecated，不再用于验证。

## 四、可信度加权公式

防线二对每个信源的加权得分：

```
weighted_score = α × relevance_score + β × credibility_score + γ × freshness_score
```

- 默认权重：α=0.4（相关性）, β=0.4（可信度）, γ=0.2（时效）
- `relevance_score`：RAG 检索的相关性分（cosine similarity 或 BM25 分，归一化到 [0,1]）
- `credibility_score`：取本 schema 的字段值（默认按 tier）
- `freshness_score`：取本 schema 的字段值，或按 last_verified_at 计算（越久越低）

### 4.1 verification_status 判定

| 条件 | verification_status | 处理 |
|------|---------------------|------|
| 有 T1/T2 信源 + supported | supported | verified（附引用） |
| 有 T1/T2 信源 + refuted | refuted | 标记 hallucination |
| 仅 T3/T4 信源 + supported | partial | 触发防线三 |
| 无信源 | no_source | 触发防线三 |

## 五、句级引用归因（ReClaim 模式）

每个被验证的句级主张 MUST 生成 inline citation `[N]`，回溯到具体信源 chunk：

```json
{
  "claim_text": "OpenAI 发布了 GPT-4 于 2023 年 3 月",
  "citations": [
    {
      "marker": "[1]",
      "source_url": "https://openai.com/research/gpt-4",
      "source_tier": "T1",
      "supporting_excerpt": "GPT-4 was released on March 14, 2023.",
      "weighted_score": 0.96
    }
  ]
}
```

## 六、状态机

```
active ──失效──> inactive ──确认撤回──> deprecated
   ↑                                    │
   └────────恢复────────────────────────┘
```

| 状态 | 含义 | 处理 |
|------|------|------|
| active | 活跃 | 可用于验证 |
| inactive | 失效 | 临时不可用（如 404），不用于验证 |
| deprecated | 已弃用 | 永不再用（内容被撤回） |

## 七、校验规则

1. **url 唯一性**：同一 url 在 sources 数组中 MUST 唯一。
2. **tier 取值受限**：仅 "T1" / "T2" / "T3" / "T4"。
3. **credibility_score 范围**：MUST ∈ [0,1]，且与 tier 默认值一致（除非手动调整，需 notes 说明）。
4. **domain 取值受限**：仅 medical / financial / legal / technical / general / all。
5. **access_method 取值受限**：仅 api / crawl / static。
6. **status 取值受限**：仅 active / inactive / deprecated。
7. **active 信源可用性**：status=active 的信源 MUST 可访问（定期 health check）。
8. **API key 环境变量**：access_config.api_key_env 引用的环境变量 MUST 在运行时存在。

## 八、命名规范

文件名固定为 `sources.json`，存放于：
- 安装目录：`tri-true/templates/sources.json`（默认信源库）
- 运行时：`.tribro/true/sources.json`（用户自定义信源库，可覆盖默认）

加载顺序：用户自定义优先 > 默认。

## 九、扩展规则

新增信源须经 `VERIFY_ADMIN sources add` 命令，自动校验 schema 后入库。直接编辑 JSON 文件也允许，但下次加载时 MUST 重新校验。tier 升降须经管理员确认并记录 notes。
