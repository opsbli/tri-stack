# tri-cache

缓存管理横向基础设施型 skill。为 tri-xxx 家族全家族提供提问-作答产物的缓存与检索能力。CACHE_WRITE 模式读取 tri-intent 快照 §三 元数据缓存下游 skill 作答；CACHE_LOOKUP 模式读取缓存索引检索历史。hook 或显式请求激活。

本 skill **不认领任何 L2 意图编码**，是家族的横切关注点（cross-cutting concern），不破坏 21 个下游执行 skill（数量见 family-spec §1.3）的 MECE 划分。核心理念：**缓存不是垃圾桶——存的要能找到，找到的要敢用，用过的要会过期。**

## 特性

- **三层存储架构**：内存热层（LRU dict，<1ms）/ SQLite 温层（WAL 索引，1-5ms）/ Markdown 冷层（按月分桶归档，5-20ms），逐层降级延迟
- **内容指纹去重**：提问归一化后 SHA-256 前 16 位作 cache_key，相同提问 NEVER 重复写原文，仅更新 hit_count
- **差异化 TTL**：按意图 L2 设置不同 TTL——I01-I02 事实/概念 30 天、I03-I05 建议/决策/推理 7 天、I06-I10 内容处理 1 天；I11/I12 编码调试、I17-I20 表达陪伴、M01-M04 元操作 NEVER 缓存
- **命中复用策略**：按意图差异化复用——I01-I02 直接复用（TTL 内）、I03-I05 参考注入（标注「请核实」）、I11/I12 NEVER 直接复用（文件可能已变更）
- **失效四策略组合**：TTL 过期 + LRU 淘汰（容量超限至 80% 水位）+ 事件驱动失效（文件变更标记 stale）+ 手动失效（key/session/intent 批量）
- **隐私过滤**：写入前扫描密钥模式（password/token/secret/api_key/sk-/AKIA/PRIVATE KEY），命中脱敏 `***REDACTED***`，敏感度过高则跳过缓存
- **双轨索引**：SQLite 主索引（结构化组合查询）+ JSONL 增量日志（容灾，可重建 index.db）
- **独立安装三态依赖检测**：快照模式 / 引导安装 / 降级模式（退化为纯内存 LRU 缓存）

## 目录结构

```
tri-cache/
├── SKILL.md                          主入口：缓存管理契约 + 三层架构 + 差异化TTL + 失效策略
├── README.md                         特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      Keep a Changelog + SemVer
├── LICENSE                           MIT
├── .gitignore
├── schemas/
│   └── cache-entry.schema.md        缓存条目 schema（SQLite 表结构 + Markdown frontmatter）
└── templates/
    ├── entry.md                      缓存原文 Markdown 模板
    └── meta.json                     配置模板（容量/TTL/热层/隐私）
```

运行时落盘结构（`.tribro/cache/`）：

```
.tribro/cache/
├── index.db                          SQLite 主索引（WAL）
├── index.jsonl                       JSONL 增量日志（容灾）
├── meta.json                          缓存元信息（统计 + 配置）
├── entries/                           缓存条目原文
│   └── <YYYY-MM>/                     按月分桶
│       └── <问题类型>_<日期>_<时间>_<会话ID>_<hash8>.md
└── summaries/                         摘要快查（可选）
    └── <YYYY-MM>.jsonl
```

## 安装

将 `tri-cache/` 目录放入你的 skills 目录即可：

```bash
cp -r tri-cache/ /path/to/your/skills/
```

本 skill 可独立安装。激活时检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| A · 快照模式 | `.tribro/snapshots/` 有快照 或 skills 目录有 `tri-intent/` | CACHE_WRITE 读取快照 §三 元数据缓存；CACHE_LOOKUP 读 index.db 检索 |
| B · 引导安装 | 以上均不满足 | 向用户提示依赖并引导安装 `skillhub install tri-intent` |
| C · 降级模式 | 用户拒绝安装 | 退化为纯内存 LRU 缓存（无元数据、无持久化），声明降级精度低 |

> 三态逻辑：本 skill 为基础设施型，支持降级——降级模式退化为内存缓存，仍可工作但精度低。

## 使用

### 三种工作模式

| 模式 | 触发源 | 输入 | 输出 |
|------|--------|------|------|
| CACHE_WRITE（被动写） | 下游 skill 执行完毕后 cache-hook 触发 | 快照 §三 + skill 作答产物 | 缓存条目 + 索引更新 |
| CACHE_LOOKUP（主动检索） | 用户显式「回忆/检索历史」请求 | 检索查询（关键词/意图/时间/会话） | 命中条目列表 + 复用建议 |
| CACHE_ADMIN（管理） | 用户显式管理命令 | stats/cleanup/invalidate/rebuild | 管理结果 |

### CACHE_WRITE 流程

```
cache-hook 传入 {快照§三, 作答内容, source_skill}
        │
        ▼
  声明自检句 + 提问归一化 → SHA-256 → cache_key
        │
        ▼
  查 SQLite 去重（已存在则 hit_count++ 返回）
        │
        ▼
  意图过滤（no_cache_intents 跳过）+ 隐私过滤（脱敏）
        │
        ▼
  生成摘要 ≤200字 + 按意图差异化 TTL
        │
        ▼
  写原文 entries/<YYYY-MM>/ + 写 SQLite + 追加 JSONL + 更新热层
```

### CACHE_LOOKUP 流程

```
用户检索请求 {关键词?, 意图?, 时间?, 会话?, top_k?}
        │
        ▼
  声明自检句 + 查内存热层（命中则返回）
        │
        ▼
  查 SQLite 组合查询（过滤 active + 校验 expires_at）
        │
        ▼
  加载原文 Markdown 冷层 + 更新 hit_count/last_accessed
        │
        ▼
  按意图标注复用建议（直接复用 / 参考注入 / 请核实）
```

### 差异化 TTL 表

| 意图 L2 | TTL | 是否缓存 | 复用策略 |
|----------|-----|----------|----------|
| I01-I02 信息/概念 | 30 天 | 是 | 直接复用 |
| I03-I05 建议/决策/推理 | 7 天 | 是 | 参考注入 |
| I06-I10 内容处理 | 1 天 | 是 | 参考注入 |
| I11-I12 编码/调试 | — | 否 | — |
| I13-I14 规划/操作 | 7 天 | 是 | 参考注入 |
| I15-I16 多媒体/头脑风暴 | 1 天 | 是 | 参考注入 |
| I17-I20 表达陪伴 | — | 否 | — |
| M01-M04 元操作 | — | 否 | — |

### 管理命令

```bash
tri-cache stats                        # 查看统计（条目数、大小、命中率）
tri-cache cleanup                      # 触发清理（过期标记 + LRU 淘汰）
tri-cache invalidate --key <hash>      # 失效单条
tri-cache invalidate --session <id>     # 失效整会话
tri-cache invalidate --intent <L2>      # 按意图失效
tri-cache rebuild                      # 从 JSONL 重建 index.db
tri-cache export --out <path>          # 导出全部缓存
tri-cache compact                      # 压缩 index.jsonl
```

### 落盘规则

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- 本 skill 缓存产物落盘于 `.tribro/cache/`（含 index.db / index.jsonl / entries/ / meta.json，可覆盖更新）
- 缓存原文落盘于 `.tribro/cache/entries/<YYYY-MM>/`（按月分桶）
- 检索结果为即时对话回应，不落盘
- 降级模式（模式 C）全程不落盘，仅内存 LRU

## 测试

完整测试用例见 `tests/tri-cache-full-testcases.md`，覆盖元数据、强制执行契约、输入契约、缓存管理方法论、自检声明、交付产物、职责边界、质量标准等全部能力点，含 50 条用例。

## 设计原则

- **横向基础设施**：不认领 L2 意图编码，不破坏家族 MECE 划分，是横切关注点
- **三层降级**：热层未命中降级温层，温层无原文降级冷层，逐层延迟递增
- **存的要能找到**：双轨索引（SQLite 结构化查询 + JSONL 容灾重建），组合查询走索引
- **找到的要敢用**：差异化 TTL + 隐私过滤 + 命中复用策略，标注「请核实」而非盲返回
- **用过的要会过期**：TTL + LRU + 事件驱动 + 手动失效四策略组合
- **可独立运行**：三态依赖检测，无 tri-intent 时降级为内存缓存仍可工作
