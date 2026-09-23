# tri-cache

缓存管理横向基础设施型 skill。为 tri-xxx 家族全家族提供用户上下文的高质量缓存与检索能力。CACHE_WRITE 模式读取 tri-intent 快照 §三 元数据缓存下游 skill 作答；CACHE_LOOKUP 模式混合检索历史；CACHE_INIT 模式为指定项目初始化四层缓存架构。hook 或显式请求激活。

本 skill **不认领任何 L2 意图编码**，是家族的横切关注点（cross-cutting concern），不破坏下游执行 skill 的 MECE 划分。核心理念：**缓存不是垃圾桶——存的要能找到，找到的要敢用，用过的要会过期，注入的要省 token。**

## 特性

- **四层缓存架构（分层设计）**：
  - **L1 滑动窗口**：最近 N 轮「提问+回答」全文（默认 50 轮），FIFO 滑动，渐进注入（近 2 轮全文 + 其余仅摘要），<1ms
  - **L2 结构化存储**：SQLite `index.db`（WAL）全量元数据 + 摘要 + 标签，精确组合查询零 token，1-5ms
  - **L3 轻量摘要**：≤200 字抽取式摘要，检索预览与上下文注入，token 消耗较全文降低约 90%
  - **L4 向量检索**：256 维确定性字符 n-gram 哈希嵌入 + 余弦相似度，语义召回，本地计算零 token
- **设计哲学**：用检索解决该检索的问题（L4 向量），用结构化解决该结构化的问题（L2 SQLite），即时上下文归 L1 窗口，低成本注入归 L3 摘要
- **内容指纹去重**：提问归一化后 SHA-256 前 16 位作 cache_key，相同提问 NEVER 重复写原文，仅更新 hit_count
- **差异化 TTL**：按意图 L2 设置不同 TTL——I01-I02 事实/概念 30 天、I03-I05 建议/决策/推理 7 天、I06-I10 内容处理 1 天；I11/I12 编码调试、I17-I20 表达陪伴、M01-M04 元操作 NEVER 缓存
- **命中复用策略**：按意图差异化复用——I01-I02 直接复用（TTL 内）、I03-I05 参考注入（标注「请核实」）、I11/I12 NEVER 直接复用（文件可能已变更）
- **失效五策略组合**：TTL 过期 + LRU 淘汰（容量超限至 80% 水位）+ 窗口滑动（FIFO 滑出降级）+ 事件驱动失效（文件变更标记 stale）+ 手动失效（key/session/intent 批量）
- **隐私过滤**：写入前扫描密钥模式（password/token/secret/api_key/sk-/AKIA/PRIVATE KEY），命中脱敏 `***REDACTED***`，敏感度过高则跳过缓存
- **双轨索引**：SQLite 主索引（结构化组合查询）+ JSONL 增量日志（容灾，可重建 index.db）
- **项目初始化**：`scripts/cache_init.py` 一键为指定项目建立四层缓存架构（默认当前项目）
- **独立安装三态依赖检测**：快照模式 / 引导安装 / 降级模式（退化为纯内存滑动窗口缓存）

## 目录结构

```
tri-cache/
├── SKILL.md                          主入口：缓存管理契约 + 四层架构 + 差异化TTL + 失效策略
├── README.md                         特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      Keep a Changelog + SemVer
├── _meta.json                        平台元数据（slug/version）
├── schemas/
│   └── cache-entry.schema.md        缓存条目 schema v2（四表 + 8 索引 + frontmatter）
├── scripts/
│   ├── cache_ops.py                  归一化/指纹/脱敏/向量嵌入/摘要/标签/滑动窗口（确定性逻辑）
│   ├── cache_init.py                 项目四层缓存架构初始化
│   └── check_update.py               版本检查与更新（家族同源）
├── templates/
│   ├── entry.md                      缓存原文 Markdown 模板
│   └── meta.json                     配置模板（容量/TTL/窗口/向量/摘要/隐私）
└── tests/
    ├── tri-cache-full-testcases.md   全场景全能力测试用例（四层架构审计版）
    └── verify_architecture.py        四层架构自动化验证脚本（30 项断言）
```

运行时落盘结构（`.tribro/cache/`）：

```
.tribro/cache/
├── index.db                          SQLite 主索引（WAL，四表：cache_entries/embeddings/window_state/cache_meta）
├── index.jsonl                       JSONL 增量日志（容灾）
├── meta.json                          缓存元信息（统计 + 配置）
├── window_state.json                  滑动窗口持久化镜像（L1）
├── entries/                           缓存条目原文（L2）
│   └── <YYYY-MM>/                     按月分桶
│       └── <问题类型>_<日期>_<时间>_<会话ID>_<hash8>.md
└── summaries/                         摘要快查（L3）
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
| C · 降级模式 | 用户拒绝安装 | 退化为纯内存滑动窗口缓存（无元数据、无持久化），声明降级精度低 |

> 三态逻辑：本 skill 为基础设施型，支持降级——降级模式退化为内存缓存，仍可工作但精度低。

## 使用

### 四种工作模式

| 模式 | 触发源 | 输入 | 输出 |
|------|--------|------|------|
| CACHE_INIT（项目初始化） | 用户显式「为项目建立缓存」 | 目标项目根目录（默认当前项目） | 四层缓存架构就绪 |
| CACHE_WRITE（被动写） | 下游 skill 执行完毕后 cache-hook 触发 | 快照 §三 + skill 作答产物 | 四层同步落位 + 索引更新 |
| CACHE_LOOKUP（主动检索） | 用户显式「回忆/检索历史」请求 | 检索查询（关键词/语义/意图/时间/会话） | 命中条目列表（摘要级）+ 复用建议 |
| CACHE_ADMIN（管理） | 用户显式管理命令 | stats/cleanup/invalidate/rebuild | 管理结果 |

### CACHE_INIT 流程

```
用户指定目标项目（默认当前项目）
        │
        ▼
  运行 python scripts/cache_init.py --root <项目根目录>
        │
        ▼
  创建 .tribro/cache/（index.db 四表 + meta.json + window_state.json + entries/ + summaries/）
        │
        ▼
  校验四层架构就绪 → 返回初始化结果
```

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
  L3 摘要生成 + 差异化 TTL → L1 入窗（全文）
        │
        ▼
  L2 写原文 entries/<YYYY-MM>/ + 写 SQLite + 追加 JSONL
        │
        ▼
  L4 向量生成写 embeddings 表
```

### CACHE_LOOKUP 流程（混合检索）

```
用户检索请求 {关键词?, 语义描述?, 意图?, 时间?, 会话?, top_k?}
        │
        ▼
  L1 查滑动窗口（命中则渐进注入返回）
        │
        ▼
  L2 结构化过滤（意图/会话/时间/状态精确查询）
        │
        ▼
  L4 向量检索（语义描述 → embed → 余弦 Top-K，合并去重）
        │
        ▼
  L3 摘要级注入（token 高效；需全文再读冷层）
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
tri-cache stats                        # 查看统计（条目数、大小、命中率、窗口占用）
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
- 本 skill 缓存产物落盘于 `.tribro/cache/`（含 index.db / index.jsonl / entries/ / summaries/ / meta.json / window_state.json，可覆盖更新）
- 缓存原文落盘于 `.tribro/cache/entries/<YYYY-MM>/`（按月分桶）
- 检索结果为即时对话回应，不落盘
- 降级模式（模式 C）全程不落盘，仅内存滑动窗口

## 测试

- 完整测试用例见 `tests/tri-cache-full-testcases.md`，覆盖元数据、强制执行契约、输入契约、四层架构方法论、自检声明、交付产物、职责边界、质量标准等全部能力点。
- 自动化验证脚本 `tests/verify_architecture.py`：30 项断言逐项验证四层架构（L1 滑动窗口 / L2 结构化 / L3 摘要 / L4 向量）及指纹去重、隐私过滤、写入/检索链路，运行 `python tests/verify_architecture.py`，退出码 0 即全部通过。
- CI 集成：`.github/workflows/tri-cache-verify.yml` 在 push / PR 触及 `tri-cache/**` 时自动运行验证脚本（Python 3.12），任一断言失败即阻断合并；支持 `workflow_dispatch` 手动触发。

## 设计原则

- **横向基础设施**：不认领 L2 意图编码，不破坏家族 MECE 划分，是横切关注点
- **四层各司其职**：检索问题归 L4 向量、结构化问题归 L2 SQLite、即时上下文归 L1 窗口、低成本注入归 L3 摘要
- **token 优先**：摘要注入、渐进窗口、SQL 过滤、本地向量——四层协同把 token 消耗降到最低
- **存的要能找到**：双轨索引（SQLite 结构化查询 + JSONL 容灾重建）+ 向量语义召回
- **找到的要敢用**：差异化 TTL + 隐私过滤 + 命中复用策略，标注「请核实」而非盲返回
- **用过的要会过期**：TTL + LRU + 窗口滑动 + 事件驱动 + 手动失效五策略组合
- **可独立运行**：三态依赖检测，无 tri-intent 时降级为内存窗口缓存仍可工作
