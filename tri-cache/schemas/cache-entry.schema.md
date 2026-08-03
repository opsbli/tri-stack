---
name: cache-entry-schema
description: tri-cache 缓存条目数据模型 schema。定义 SQLite 主索引表结构、字段语义、索引规约与 Markdown 原文 frontmatter 格式，供实现与校验对齐。
---

# tri-cache 缓存条目 Schema

> 本文件定义 tri-cache 缓存条目的数据模型，是 SQLite 主索引与 Markdown 原文的唯一权威定义。
> 实现时 MUST 严格对齐本 schema，NEVER 私自增删字段；扩展须经 SKILL.md §可扩展性 声明。

## 一、SQLite 主索引表结构

### 1.1 cache_entries 表（缓存条目主表）

```sql
CREATE TABLE cache_entries (
  cache_key      TEXT PRIMARY KEY,        -- 内容指纹 SHA-256 前16位
  question       TEXT NOT NULL,           -- 用户原始提问（归一化前）
  answer         TEXT NOT NULL,           -- AI 完整回答
  summary        TEXT NOT NULL,           -- 摘要 ≤200字
  intent_l1      TEXT,                    -- A.Asking / B.Doing / C.Expressing / Meta
  intent_l2      TEXT,                    -- I08 等编码
  aux_intents    TEXT,                    -- 辅助意图 JSON 数组，如 ["I09","I10"]
  d1_domain      TEXT,                    -- 任务领域（办公/学习/编程/生活/创作/商业/情感/科研/未指定）
  d2_input_form  TEXT,                    -- 输入形态（文本/代码/图片/文档/表格/音视频/链接/无）
  d3_rounds      TEXT,                    -- 交互轮次（单轮/多轮/长程Agent）
  d4_output      TEXT,                    -- 输出期望（简答/长文/结构化数据/可执行代码/文件产物/分步指引）
  d5_certainty   TEXT,                    -- 确定性（明确/模糊/开放）
  session_id     TEXT NOT NULL,           -- 会话ID（快照命名含）
  user_id        TEXT DEFAULT 'default',  -- 用户ID（单用户默认 default）
  source_skill   TEXT,                    -- 产出作答的 skill（如 tri-ask/tri-content）
  created_at     INTEGER NOT NULL,        -- 创建时间戳（Unix 秒）
  last_accessed  INTEGER NOT NULL,        -- 最近访问时间戳（Unix 秒）
  hit_count      INTEGER DEFAULT 0,       -- 命中次数
  ttl_seconds    INTEGER,                 -- TTL（秒，null=永久，0=不缓存）
  expires_at     INTEGER,                 -- 过期时间戳（Unix 秒，null=永久）
  content_size   INTEGER,                 -- 内容字节数（question+answer）
  tags           TEXT,                    -- 关键词 JSON 数组，如 ["翻译","中英"]
  status         TEXT DEFAULT 'active',   -- active / stale / expired / archived
  entry_path     TEXT,                    -- 原文文件相对路径（相对 .tribro/cache/）
  schema_version INTEGER DEFAULT 1        -- schema 版本号
);
```

### 1.2 索引规约

```sql
CREATE INDEX idx_intent_l2   ON cache_entries(intent_l2);
CREATE INDEX idx_session     ON cache_entries(session_id);
CREATE INDEX idx_user        ON cache_entries(user_id);
CREATE INDEX idx_created     ON cache_entries(created_at);
CREATE INDEX idx_last_access ON cache_entries(last_accessed);
CREATE INDEX idx_expires     ON cache_entries(expires_at);
CREATE INDEX idx_status      ON cache_entries(status);
```

| 索引 | 用途 |
|------|------|
| idx_intent_l2 | 按意图检索 |
| idx_session | 按会话检索 |
| idx_user | 按用户检索 |
| idx_created | 按时间范围检索 |
| idx_last_access | LRU 淘汰排序 |
| idx_expires | TTL 过期批量标记 |
| idx_status | 状态过滤（active/stale/expired/archived） |

### 1.3 cache_meta 表（统计与配置）

```sql
CREATE TABLE cache_meta (
  key   TEXT PRIMARY KEY,
  value TEXT
);
```

**预置键**：

| key | 含义 | 示例值 |
|-----|------|--------|
| total_entries | 总条目数 | 1024 |
| total_size_bytes | 总字节数 | 52428800 |
| total_hits | 累计命中数 | 356 |
| total_misses | 累计未命中数 | 210 |
| total_evictions | 累计淘汰数 | 18 |
| last_cleanup_at | 上次清理时间戳 | 1722497400 |
| config_max_size_mb | 容量上限 MB | 100 |
| config_default_ttl | 默认 TTL 秒 | 2592000 |
| config_hot_layer_size | 热层容量 | 256 |
| schema_version | schema 版本 | 1 |

## 二、字段语义规约

### 2.1 cache_key 生成规则

1. 取用户原始提问
2. 归一化：去首尾空白 → 转小写 → 去标点（`[^\w\s]`）→ 压缩多余空格
3. SHA-256 哈希
4. 取前 16 位作 `cache_key`

### 2.2 status 状态机

```
active ──TTL过期──> expired ──清理──> (删除)
  │                    │
  │文件变更            │恢复（手动）
  ▼                    ▼
stale ──手动失效──> archived
```

| 状态 | 含义 | 检索可见性 |
|------|------|------------|
| active | 有效 | 返回 |
| stale | 可能过时 | 返回但标注「请核实」 |
| expired | 已过期 | 不返回（保留可恢复） |
| archived | 已归档（LRU 淘汰） | 不返回 |

### 2.3 ttl_seconds 与 expires_at 关系

- `ttl_seconds = 0` 或 L2 ∈ `no_cache_intents` → 不缓存
- `ttl_seconds = null` → 永不过期（`expires_at = null`）
- `ttl_seconds > 0` → `expires_at = created_at + ttl_seconds`

## 三、PRAGMA 配置（每连接一次）

```sql
PRAGMA journal_mode=WAL;          -- 读写并发
PRAGMA synchronous=NORMAL;        -- 平衡持久性与速度
PRAGMA temp_store=MEMORY;
PRAGMA cache_size=-20000;         -- ~20MB
PRAGMA foreign_keys=ON;
```

## 四、JSONL 增量日志格式

每行一条事件 JSON：

```json
{"event":"write","cache_key":"a1b2c3d4e5f6a7b8","ts":1722497400,"entry":{"intent_l2":"I08","session_id":"6a5c037d","summary":"...","entry_path":"entries/2026-08/I08_20260801_143022_6a5c037d_a1b2c3d4.md"}}
{"event":"hit","cache_key":"a1b2c3d4e5f6a7b8","ts":1722497500}
{"event":"invalidate","cache_key":"a1b2c3d4e5f6a7b8","ts":1722497600,"reason":"file_changed"}
{"event":"evict","cache_key":"a1b2c3d4e5f6a7b8","ts":1722497700,"reason":"lru"}
```

| event 类型 | 含义 |
|-----------|------|
| write | 写入新条目 |
| hit | 命中（更新 hit_count） |
| invalidate | 失效（标记 stale/expired/archived） |
| evict | LRU 淘汰 |

## 五、Markdown 原文 frontmatter 格式

```yaml
---
cache_key: <hash16>
intent:
  l1: <L1>
  l2: <L2>
  aux: [<辅助意图>]
dimensions:
  d1: <领域>
  d2: <输入形态>
  d3: <轮次>
  d4: <输出期望>
  d5: <确定性>
session_id: <会话ID>
user_id: default
source_skill: <来源skill>
created_at: <ISO8601>
ttl_seconds: <秒>
expires_at: <ISO8601>
tags: [<关键词>]
status: active
schema_version: 1
---
```

## 六、命名规范

缓存原文文件命名沿用家族规范并追加内容指纹：

```
<问题类型>_<日期>_<时间>_<会话ID>_<hash8>.md
例：I08_20260801_143022_6a5c037d_a1b2c3d4.md
```

- `<问题类型>`：快照 §三 的 L2 编码（如 I08）
- `<日期>`：YYYYMMDD
- `<时间>`：HHMMSS
- `<会话ID>`：chat_session_id 前 8 位
- `<hash8>`：cache_key 前 8 位

## 七、隐私脱敏规则

密钥模式正则（命中即脱敏 `***REDACTED***`）：

```
(?i)(password|passwd|secret|api[_-]?key|token|sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN.*PRIVATE KEY-----)
```

- 命中行替换为 `***REDACTED***`
- 整条回答敏感度高（命中 ≥3 处）则跳过缓存并记日志
