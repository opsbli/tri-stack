---
name: evolve-schema
description: tri-evolve 进化数据模型 schema。定义经验条目库、用户画像、调优建议、质量基线四张表的 SQLite 结构、字段语义、状态机与信号事件格式，供实现与校验对齐。
---

# tri-evolve 进化数据 Schema

> 本文件定义 tri-evolve 进化产物的数据模型，是 lessons / profile / proposals / baseline 四库的唯一权威定义。
> 实现时 MUST 严格对齐本 schema，NEVER 私自增删字段；扩展须经 SKILL.md §可扩展性 声明。

## 一、经验条目库（lessons.db）

```sql
CREATE TABLE lessons (
  lesson_id        TEXT PRIMARY KEY,        -- UUID
  scenario         TEXT NOT NULL,           -- 场景描述（什么情况下）
  attribution      TEXT NOT NULL,           -- 归因（哪个 skill/意图的什么缺陷）
  proposal         TEXT NOT NULL,           -- 改进建议
  confidence       REAL NOT NULL,           -- 置信度 0-1
  status           TEXT DEFAULT 'pending',  -- pending/validating/verified/rejected/rolled_back
  ab_result        TEXT,                    -- A/B 结果 JSON {lift, sample, p_value}
  embedding        BLOB,                   -- 场景描述 embedding（语义检索）
  source_channels  TEXT,                    -- 信号来源 JSON 数组
  target_skill     TEXT,                    -- 目标 skill
  target_intent    TEXT,                    -- 目标意图 L2
  rollback_reason  TEXT,                    -- 回滚原因（被回滚时填）
  created_at       INTEGER NOT NULL,        -- 创建时间戳
  verified_at      INTEGER,                 -- 验证时间戳
  rolled_back_at   INTEGER,                 -- 回滚时间戳
  schema_version   INTEGER DEFAULT 1
);
CREATE INDEX idx_lesson_status ON lessons(status);
CREATE INDEX idx_lesson_skill  ON lessons(target_skill);
CREATE INDEX idx_lesson_intent ON lessons(target_intent);
```

### 状态机

```
pending ──提议生成──> validating ──A/B通过──> verified ──应用──> applied
                         │                      │
                         │A/B失败               │回滚
                         ▼                      ▼
                      rejected              rolled_back
```

| 状态 | 含义 | 可注入下游 |
|------|------|------------|
| pending | 待验证 | ❌ |
| validating | A/B 进行中 | ❌ |
| verified | 验证通过 | ✅ |
| applied | 已应用配置覆盖 | ✅ |
| rejected | 验证失败 | ❌ |
| rolled_back | 被回滚 | ❌ |

## 二、用户画像（profile.db）

```sql
CREATE TABLE user_profile (
  user_id        TEXT PRIMARY KEY,
  static_attrs  TEXT,                    -- 静态属性 JSON {age?, profession?, region?, tech_stack?}
  style_prefs    TEXT,                   -- 风格偏好 JSON {tone, length, format} + 衰减权重
  topic_prefs    TEXT,                   -- 主题偏好 JSON {domain, topics, terms} + 频次时间衰减
  interaction    TEXT,                   -- 交互习惯 JSON {query_style, intent_dist, active_hours}
  prefs_history  TEXT,                    -- 偏好演变历史 JSON [{ts, field, old, new}]
  created_at    INTEGER NOT NULL,
  updated_at    INTEGER NOT NULL,
  schema_version INTEGER DEFAULT 1
);
```

### 静态属性 JSON 示例

```json
{
  "profession": "backend_developer",
  "region": "Asia/Shanghai",
  "tech_stack": ["Node.js", "TypeScript", "Koa"]
}
```

> 敏感属性（health / political / religious / sexual）NEVER 写入。

### 风格偏好 JSON 示例（带衰减权重）

```json
{
  "tone": {"value": "formal", "weight": 0.82, "samples": 15},
  "length": {"value": "concise", "weight": 0.75, "samples": 12},
  "format": {"value": "list", "weight": 0.68, "samples": 9}
}
```

## 三、调优建议（proposals.db）

```sql
CREATE TABLE proposals (
  proposal_id    TEXT PRIMARY KEY,
  target_skill   TEXT NOT NULL,
  target_intent  TEXT,
  config_override TEXT,                  -- 配置覆盖 JSON
  status         TEXT DEFAULT 'pending',  -- pending/validating/verified/applied/rejected
  ab_lift        REAL,                    -- A/B 提升幅度
  ab_p_value     REAL,                    -- 显著性 p 值
  ab_sample      INTEGER,                 -- 样本数
  lesson_id      TEXT,                    -- 关联经验条目
  risk_level     TEXT DEFAULT 'medium',  -- low/medium/high
  approval_status TEXT,                  -- 高风险人工审批状态
  created_at     INTEGER NOT NULL,
  applied_at     INTEGER,
  schema_version INTEGER DEFAULT 1
);
CREATE INDEX idx_proposal_status ON proposals(status);
CREATE INDEX idx_proposal_skill  ON proposals(target_skill);
```

## 四、质量基线（baseline.db）

```sql
CREATE TABLE baseline (
  skill_name    TEXT,
  intent_l2     TEXT,
  metric        TEXT,                    -- hit_rate/satisfaction/reuse_rate/feedback_ratio
  value         REAL,
  ts            INTEGER NOT NULL,
  PRIMARY KEY (skill_name, intent_l2, metric, ts)
);
```

## 五、信号事件流格式（signals.jsonl）

每行一信号事件 JSON：

```json
{"event":"explicit_feedback","ts":1722497400,"user_id":"u1","session_id":"s1","skill":"tri-ask","intent_l2":"I01","signal":"thumbs_up","text":"回答很准确"}
{"event":"implicit_behavior","ts":1722497500,"user_id":"u1","session_id":"s1","skill":"tri-content","intent_l2":"I08","behavior":"retry"}
{"event":"cache_hit","ts":1722497600,"hit":true,"intent_l2":"I01","cache_key":"a1b2c3d4"}
{"event":"correction","ts":1722497700,"source":"tri-meta","skill":"tri-coding","intent_l2":"I11","correction":"..."}
{"event":"snapshot_dist","ts":1722497800,"intent_l2":"I08","count":12,"clarify_gate_triggered":false}
```

| event 类型 | 含义 | 渠道 |
|-----------|------|------|
| explicit_feedback | 用户显式反馈 | ① |
| implicit_behavior | 用户隐式行为 | ② |
| cache_hit | 缓存命中 | ③ |
| correction | 纠偏记录 | ④ |
| snapshot_dist | 快照分布 | ⑤ |
| session_trace | 会话轨迹 | ⑥ |

## 六、PRAGMA 配置（每连接一次）

```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA temp_store=MEMORY;
PRAGMA cache_size=-20000;
```

## 七、时间衰减加权公式

```python
# 动态偏好更新（半衰期 30 天）
import math
age_days = (now - last_update) / 86400
weight = math.exp(-math.log(2) * age_days / 30)
new_value = (old_value * weight * old_samples + new_signal) / (weight * old_samples + 1)
```

## 八、A/B 验证判定

```
通过条件：lift >= 0.05 AND p_value < 0.05 AND sample >= 30
- lift = 实验组质量分均值 - 对照组质量分均值
- p_value：单尾 t 检验
- sample：实验组与对照组各 ≥30
```
