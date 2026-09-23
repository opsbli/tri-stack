---
name: cache-entry-schema
description: tri-cache 缓存条目数据模型 schema v2。定义四层架构（L1 滑动窗口 / L2 结构化 / L3 摘要 / L4 向量）的 SQLite 表结构、字段语义、索引规约与 Markdown 原文 frontmatter 格式，供实现与校验对齐。
---

# tri-cache 缓存条目 Schema（v2 · 四层架构）

> 本文件定义 tri-cache 缓存条目的数据模型，是 SQLite 主索引、向量嵌入表、滑动窗口表与 Markdown 原文的唯一权威定义。
> 实现时 MUST 严格对齐本 schema，NEVER 私自增删字段；扩展须经 SKILL.md §可扩展性 声明。
> 本 schema 由 `scripts/cache_init.py` 落地为可执行 DDL（single source of truth for logic）。

## 一、四层架构数据模型总览

| 层 | 载体 | 表 / 文件 | 职责 |
|----|------|-----------|------|
| L1 滑动窗口 | 内存 + 持久化 | `window_state` 表 + `window_state.json` | 最近 N 轮「提问+回答」全文，即时上下文注入 |
| L2 结构化存储 | SQLite | `cache_entries` 表 | 全量条目结构化元数据，精确查询/过滤/统计/失效 |
| L3 轻量摘要 | SQLite + JSONL | `cache_entries.summary` + `summaries/<YYYY-MM>.jsonl` | ≤200 字摘要，检索预览与低成本上下文注入 |
| L4 向量检索 | SQLite | `embeddings` 表 | 确定性字符 n-gram 哈希嵌入，语义相似检索 |

## 二、SQLite 表结构

### 2.1 cache_entries 表（L2 结构化存储 · 主表）

```sql
CREATE TABLE cache_entries (
  cache_key      TEXT PRIMARY KEY,        -- 内容指纹 SHA-256 前16位
  question       TEXT NOT NULL,           -- 用户原始提问（归一化前）
  answer         TEXT NOT NULL,           -- AI 完整回答
  summary        TEXT NOT NULL,           -- 轻量摘要 ≤200字（L3）
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
  tags           TEXT,                    -- 关键词 JSON 数组，如 ["闭包","JavaScript"]
  status         TEXT DEFAULT 'active',   -- active / stale / expired / archived
  entry_path     TEXT,                    -- 原文文件相对路径（相对 .tribro/cache/）
  schema_version INTEGER DEFAULT 2        -- schema 版本号
);
```

### 2.2 embeddings 表（L4 向量检索）

```sql
CREATE TABLE embeddings (
  cache_key   TEXT PRIMARY KEY REFERENCES cache_entries(cache_key) ON DELETE CASCADE,
  dim         INTEGER NOT NULL,           -- 向量维度（默认 256）
  ngram_min   INTEGER NOT NULL,           -- n-gram 最小长度（默认 1）
  ngram_max   INTEGER NOT NULL,           -- n-gram 最大长度（默认 2）
  vector      TEXT NOT NULL,              -- 向量 JSON 数组（L2 归一化）
  created_at  INTEGER NOT NULL            -- 生成时间戳（Unix 秒）
);
```

- 向量由 `scripts/cache_ops.py::embed()` 生成：字符 n-gram 哈希嵌入（语言无关、确定性、零外部依赖）。
- 检索时对 query 计算同参数嵌入，与全表向量做余弦相似度（`cosine_similarity`），取 Top-K。
- `cache_key` 级联删除：条目失效删除时向量自动清理。

### 2.3 window_state 表（L1 滑动窗口）

```sql
CREATE TABLE window_state (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id  TEXT NOT NULL,              -- 会话ID
  seq         INTEGER NOT NULL,           -- 窗口内序号（FIFO，0 起递增）
  cache_key   TEXT NOT NULL REFERENCES cache_entries(cache_key),
  question    TEXT NOT NULL,              -- 提问全文（窗口内高保真）
  answer      TEXT NOT NULL,              -- 回答全文
  summary     TEXT,                       -- 轻量摘要（渐进注入用）
  created_at  INTEGER NOT NULL            -- 入窗时间戳（Unix 秒）
);
CREATE INDEX idx_window_session ON window_state(session_id, seq);
```

- 窗口容量默认 50 轮（`config_window_size`），FIFO 滑动：超容量滑出最旧条目。
- 滑出条目已落 L2/L3/L4（结构化/摘要/向量），故窗口只保「即时」，不保「全量」。
- `window_state.json` 为窗口的跨会话持久化镜像（`{"windows": {session_id: [...]}}`），重启可恢复。

### 2.4 cache_meta 表（统计与配置）

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
| config_window_size | 滑动窗口容量（轮） | 50 |
| config_window_inject_full | 窗口内全文注入轮数 | 2 |
| config_embedding_dim | 向量维度 | 256 |
| config_vector_top_k | 向量检索 Top-K | 10 |
| config_vector_min_score | 向量检索最低相似度 | 0.5 |
| config_summary_max_chars | 摘要最大字数 | 200 |
| schema_version | schema 版本 | 2 |

## 三、索引规约

```sql
CREATE INDEX idx_intent_l2   ON cache_entries(intent_l2);
CREATE INDEX idx_session     ON cache_entries(session_id);
CREATE INDEX idx_user        ON cache_entries(user_id);
CREATE INDEX idx_created     ON cache_entries(created_at);
CREATE INDEX idx_last_access ON cache_entries(last_accessed);
CREATE INDEX idx_expires     ON cache_entries(expires_at);
CREATE INDEX idx_status      ON cache_entries(status);
CREATE INDEX idx_window_session ON window_state(session_id, seq);
```

| 索引 | 用途 |
|------|------|
| idx_intent_l2 | 按意图检索（L2 结构化过滤） |
| idx_session | 按会话检索 |
| idx_user | 按用户检索 |
| idx_created | 按时间范围检索 |
| idx_last_access | LRU 淘汰排序 |
| idx_expires | TTL 过期批量标记 |
| idx_status | 状态过滤（active/stale/expired/archived） |
| idx_window_session | 滑动窗口按会话 FIFO 排序 |

## 四、字段语义规约

### 4.1 cache_key 生成规则

1. 取用户原始提问
2. 归一化：去首尾空白 → 转小写 → 去标点（`[^\w\s]`）→ 压缩多余空格
3. SHA-256 哈希
4. 取前 16 位作 `cache_key`

### 4.2 status 状态机

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

### 4.3 ttl_seconds 与 expires_at 关系

- `ttl_seconds = 0` 或 L2 ∈ `no_cache_intents` → 不缓存
- `ttl_seconds = null` → 永不过期（`expires_at = null`）
- `ttl_seconds > 0` → `expires_at = created_at + ttl_seconds`

### 4.4 向量嵌入规约（L4）

- 算法：`embed(text, dim=256, ngram=(1,2))`——归一化文本 → 滑动 n-gram → 带符号 MD5 哈希累加 → L2 归一化。
- 确定性：同文本同参数 MUST 产出同向量（零外部依赖、离线可用）。
- 存储：向量 JSON 数组存 `embeddings.vector`；检索时内存加载全量向量做余弦相似度。
- 相似度：`cosine_similarity(a, b)` = L2 归一化向量点积；低于 `config_vector_min_score` 不返回。

### 4.5 轻量摘要规约（L3）

- 算法：`generate_summary(question, answer, max_chars=200)`——回答首句，截断 ≤200 字。
- 用途：检索结果预览 + 上下文注入（只注入摘要，token 消耗较全文大幅降低）。
- 标签：`extract_tags(text, top_n=5)`——拉丁单词优先 + CJK 字符 bigram，存 `cache_entries.tags`。

### 4.6 滑动窗口规约（L1）

- 容量：`config_window_size`（默认 50 轮）；FIFO 滑动，超容量滑出最旧。
- 注入：`config_window_inject_full`（默认 2）——最近 2 轮注入全文，其余轮次仅注入摘要（渐进式上下文，token 高效）。
- 持久化：`window_state.json` 镜像 + `window_state` 表双写，重启可恢复。

## 五、PRAGMA 配置（每连接一次）

```sql
PRAGMA journal_mode=WAL;          -- 读写并发
PRAGMA synchronous=NORMAL;        -- 平衡持久性与速度
PRAGMA temp_store=MEMORY;
PRAGMA cache_size=-20000;         -- ~20MB
PRAGMA foreign_keys=ON;
```

## 六、JSONL 增量日志格式

每行一条事件 JSON：

```json
{"event":"write","cache_key":"a1b2c3d4e5f6a7b8","ts":1722497400,"entry":{"intent_l2":"I08","session_id":"6a5c037d","summary":"...","entry_path":"entries/2026-08/I08_20260801_143022_6a5c037d_a1b2c3d4.md"}}
{"event":"hit","cache_key":"a1b2c3d4e5f6a7b8","ts":1722497500}
{"event":"invalidate","cache_key":"a1b2c3d4e5f6a7b8","ts":1722497600,"reason":"file_changed"}
{"event":"evict","cache_key":"a1b2c3d4e5f6a7b8","ts":1722497700,"reason":"lru"}
{"event":"embed","cache_key":"a1b2c3d4e5f6a7b8","ts":1722497800,"dim":256}
```

| event 类型 | 含义 |
|-----------|------|
| write | 写入新条目（含摘要） |
| hit | 命中（更新 hit_count） |
| invalidate | 失效（标记 stale/expired/archived） |
| evict | LRU 淘汰 |
| embed | 向量生成（L4） |

## 七、Markdown 原文 frontmatter 格式

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
summary: <≤200 字摘要>
status: active
schema_version: 2
---
```

## 八、命名规范

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

## 九、隐私脱敏规则

密钥模式正则（命中即脱敏 `***REDACTED***`，由 `scripts/cache_ops.py::SECRET_PATTERN` 单一持有）：

```
(?i)(password|passwd|secret|api[_-]?key|token|sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN.*PRIVATE KEY-----)
```

- 命中行替换为 `***REDACTED***`
- 整条回答敏感度高（命中 ≥3 处）则跳过缓存并记日志
