# Changelog

本文件记录 tri-cache skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.1.1] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手意图识别、业务作答产出、元操作信号处理与学习调优，转出/归属对应 skill 呼应家族 MECE。

## [2.1.0] - 2026-08-29

### 新增

- **CONTEXT_COMPACT 模式（上下文压缩 · L5 溢出治理）**：新增第五能力层，处理长会话/长审查撞上下文上限的问题。含四部分：① 模型感知预算（`scripts/token_budget.py`）；② 溢出信号识别（先排除 429/限流，避免误判为溢出而丢信息）；③ 压缩纪律六条（保留工具调用-结果配对 / 逐项枚举禁合并 / 关键值逐字保留 / 凭据仅留占位+指针 / 头部截断显式标注 / 不发明内容）；④ 压缩检查点产物（`.tribro/cache/compaction/<会话ID>_<序号>.md`，五段固定结构 + `complete` 标记）
- **`scripts/token_budget.py`**：模型感知 token 预算（context_window / output_limit / usable / count_tokens），**零新增依赖**——litellm 可用则用，否则回退 UTF-8 字节上界（保守上界，宁可早压缩也不静默溢出）；内置 `--self-test` 断言
- **`templates/compaction-checkpoint.md`**：压缩检查点模板（目标 / 已确认项 / 未决项 / 关键值原文 / 已尝试路径）
- **CACHE_ADMIN 新增 `budget` 命令**：输出模型上下文预算事实；`compact` 命令补注「归档日志 ≠ 对话压缩」避免语义撞名

### 变更

- 质量标准新增 3 行（预算降级可用 / 限流不误判 / 压缩无信息丢失）
- **容量治理（自举审计发现）**：SKILL.md 曾达 477 行逼近家族 500 行硬约束，已将「上下文压缩与预算」整节外移 `references/context-compaction.md`（含新增的七步执行流程 §五），SKILL.md 回落到 448 行；处理流程段改为指向单一事实源的指针，消除与参考文档的重复
- **行尾治理**：多处编辑导致 SKILL.md / CHANGELOG.md 出现 CRLF-LF 混合（会产生数百行假 diff），已统一恢复为文件原有约定（SKILL/README/CHANGELOG=CRLF，references/templates/tests=LF）
- frontmatter version `2.0.0` → `2.1.0`；description 增上下文压缩与 token 预算；目录结构同步

### 审计回填（tri-review v1.4.0 增量审计试运行）

- 补齐 CONTEXT_COMPACT 模式落地遗漏的六处：强制执行契约条目 1 的前置规则、条目 8 自检句枚举、输入契约新增「CONTEXT_COMPACT 模式输入」小节、职责边界纳入 L5、落盘规则登记 `.tribro/cache/compaction/`、压缩流程新增第 7 步「仍装不下」兜底分支（最多再压缩 2 轮，仍超则报错，NEVER 静默截断）

### 来源

- 上下文压缩与预算蒸馏自 strix `llm/compaction.py` + `llm/context_budget.py`（Apache-2.0），去产品化改写（剥离 overflow 判定中与特定 Provider 强绑定的表述，凭据处理改为与 tri-cache §隐私过滤 一致的占位+指针方案）

## [2.0.0] - 2026-08-15

### 新增

- **四层缓存架构**：从三层存储升级为四层架构，新增 L1 滑动窗口 和 L4 向量检索：
  - L1 滑动窗口：最近 N 轮「提问+回答」全文（默认 50 轮），FIFO 滑动，渐进注入（近 2 轮全文 + 其余仅摘要）
  - L4 向量检索：256 维确定性字符 n-gram 哈希嵌入 + 余弦相似度，语义召回，本地计算零 token 消耗
- **CACHE_INIT 模式**：新增项目初始化模式，`scripts/cache_init.py` 一键为指定项目建立四层缓存架构（默认当前项目）
- **L3 轻量摘要**：抽取式摘要（回答首句 ≤200 字）+ 关键词提取（拉丁单词优先 + CJK bigram），检索注入 token 降低约 90%
- **确定性算法库**：`scripts/cache_ops.py` 新增 `embed()` / `cosine_similarity()` / `generate_summary()` / `extract_tags()` / `manage_window()` 等函数
- **混合检索流程**：CACHE_LOOKUP 新增 L4 向量检索分支，支持语义描述检索，与 L2 结构化过滤结果合并去重
- **失效策略新增窗口滑动**：失效五策略组合（TTL + LRU + 窗口滑出 + 事件驱动 + 手动）
- **embeddings 表**：SQLite 新增 `embeddings` 表（cache_key + dim + ngram + vector），L4 向量存储
- **window_state 表**：SQLite 新增 `window_state` 表（session_id + seq + cache_key + question + answer + summary），L1 窗口持久化

### 变更

- frontmatter version `1.1.1` → `2.0.0`
- 核心方法论从「三层存储」升级为「四层架构」，更新全部说明文档、schema、模板
- `templates/meta.json` 新增窗口/向量/摘要配置项（config_window_size / config_embedding_dim / config_vector_top_k / config_summary_max_chars 等）
- `schemas/cache-entry.schema.md` 升级为 v2，新增 embeddings 表、window_state 表、8 索引（+1 窗口索引）
- 自检句新增 CACHE_INIT 模式声明
- 原文 frontmatter 新增 `summary` 字段与 `schema_version` 字段（=2）

### 修复

- **隐私脱敏修复**：`cache_ops.py::SECRET_PATTERN` 现连同 `=value` / `: value` 一并脱敏，修复 `password=abc123` 仅脱敏关键词、密钥值仍泄露的问题
- 测试用例版本从 v1.0.1 更新至 v2.0.0，对齐四层架构能力清单
- 新增自动化验证脚本 `tests/verify_architecture.py`（30 项断言覆盖四层架构全能力点）
- 新增 CI 集成 `.github/workflows/tri-cache-verify.yml`：push / PR 触及 `tri-cache/**` 时自动运行验证脚本，任一断言失败即阻断合并

## [1.1.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源 `tri-intent/references/version-gate.md`，消除各 skill 内的重复表述
- frontmatter version `1.1.0` → `1.1.1`

## [1.1.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.0.1` → `1.1.0`

## [1.0.1] - 2026-08-01

### 修复

#### 目录结构图清理（合规）
- 删除 SKILL.md「目录结构 / 配套文件」中列出的 `LICENSE` / `.gitignore` 条目，遵循《tri-skill-规范与生成指南》§4.1「禁止生成的文件」硬约束（许可证仅由 frontmatter `license` 字段声明，忽略策略由仓库统一管控）。
- 本版本无功能变更，仅文档合规修正（PATCH）。

## [1.0.0] - 2026-08-01

### 新增

- **初始版本**：tri-cache 横向基础设施型 skill，为 tri-xxx 家族全家族提供缓存与检索能力
- **三种工作模式**：CACHE_WRITE（被动写，hook 触发）/ CACHE_LOOKUP（主动检索）/ CACHE_ADMIN（管理命令）
- **三层存储架构**：内存热层（LRU dict，<1ms）/ SQLite 温层（WAL 索引，1-5ms）/ Markdown 冷层（按月分桶，5-20ms）
- **内容指纹去重**：提问归一化后 SHA-256 前 16 位作 cache_key，相同提问不重复写原文，仅更新 hit_count
- **差异化 TTL**：按意图 L2 设置不同 TTL（I01-I02 30 天 / I03-I05 7 天 / I06-I10 1 天 / I11-I12 与 I17-I20 与 M01-M04 不缓存）
- **命中复用策略**：按意图差异化复用（I01-I02 直接复用 / I03-I05 参考注入标注「请核实」/ I11-I12 不缓存）
- **失效四策略组合**：TTL 过期 + LRU 淘汰（容量超限至 80% 水位）+ 事件驱动失效（文件变更标记 stale）+ 手动失效（key/session/intent 批量）
- **隐私过滤**：写入前扫描密钥模式（password/token/secret/api_key/sk-/AKIA/PRIVATE KEY），命中脱敏 `***REDACTED***`，敏感度过高跳过缓存
- **双轨索引**：SQLite 主索引（7 索引覆盖组合查询）+ JSONL 增量日志（容灾，可重建 index.db）
- **上游依赖检测三态逻辑**：快照模式 / 引导安装 / 降级模式（退化为纯内存 LRU 缓存，声明降级精度低）
- **schema 与模板**：`schemas/cache-entry.schema.md` 定义 SQLite 表结构与 Markdown frontmatter；`templates/entry.md` 原文模板；`templates/meta.json` 配置模板
- **质量标准八维**：写入完整性 / 去重正确性 / 检索延迟 / 失效准确性 / 隐私安全 / 容量合规 / 索引一致性 / 复用建议准确