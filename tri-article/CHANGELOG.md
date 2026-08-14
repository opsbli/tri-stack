# Changelog

本文件所有记录遵循 [Keep a Changelog](https://keepachangelog.com/) 格式，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.2.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源 `tri-intent/references/version-gate.md`，消除各 skill 内的重复表述
- frontmatter version `1.2.0` → `1.2.1`

## [1.2.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.1.2` → `1.2.0`

## [1.1.2] - 2026-08-02

### 新增

- `references/de-ai-rules.md`：去 AI 化引擎完整参考（禁用词分类表 / 视角库维度表 / 结构自由化细则 / 模式 A·B 适配表 / 13 项质量门禁自查清单）
- `tests/` 新增 TC-S01~S14 脚本调用用例，覆盖 `hooks/index.py` 的 `add`（index.json 11 字段完整性、slug 自动派生、同 (slug,domain) 覆盖不追加）、`dedup`（hard/soft/none 三档与退出码）、`search`（按 tag/domain/keyword 及多条件与逻辑）、`edit_distance` 边界

### 变更

- 自检句改为家族标准形式：「本次意图=I06（L3=article），已读取快照=<是/否>，profile 已加载=<是/否>」
- 首段措辞由「可选下游」改为「下游 skill（读取快照直接执行，绝不重识别意图）」，消除与家族原则的冲突
- SKILL.md §2 去 AI 化核心要求、§4 质量门禁 由内联长清单收敛为摘要 + `references/de-ai-rules.md` 指针
- §目录结构（SKILL.md 与 README.md）补齐 `hooks/`、`references/`，与磁盘实际一致

### 移除

- 清理 git 脏文件：`hooks/__pycache__/index.cpython-313.pyc` 及空目录 `hooks/_reg_articles`、`hooks/_t_articles`（家族禁止 .gitignore，故直接删除）

## [1.1.1] - 2026-08-01

### 修复

- **`hooks/index.py` dedup 输出新增 `level` 字段**：返回 `hard` / `soft` / `none` 明确区分硬重复（标题哈希命中）、软重复（同领域 slug 编辑距离≤2）、无重复，便于上游「三选一」逻辑快速消费（此前仅有 `hard`/`soft` 数组，无单一层级字段）
- **`hooks/index.py` add 改为覆盖更新**：同 `(slug, domain)` 视为同一篇文章的覆盖更新，原地替换索引记录而非追加，避免索引随文章覆盖重复增长

## [1.1.0] - 2026-08-01

### Changed

- **文章存储重构到 `.tribro`**：原 `OUTPUT_DIR` / `HISTORY_DIR` 合并为单一 `ARTICLES_ROOT`（默认 `.tribro/tri-article/articles`），按「领域分桶 `<domain-slug>/` + `index.json` 全量索引」组织，专为**便于搜索与去重**设计。
- 新增 §1.5「文章存储与检索」：定义领域分桶、时间排序文件名 `<YYYYMMDD>-<slug>.md`、`index.json` 记录字段、去重算法（标题归一化哈希硬重复 + 同领域 slug 编辑距离≤2 软重复）、检索方式。
- 新增辅助脚本 `hooks/index.py`（纯标准库）：`dedup` / `add` / `search` / `list` 四个子命令，维护 `index.json` 单一事实源。
- **对齐 tri-intent 路由**：次触发精确为 `L2=I06 内容生成` 且 `L3_子意图=article`；输入契约新增快照 `L3_子意图`、`DOMAIN_POOL` 兼作领域分桶名。
- `profile-skeleton.md`：`OUTPUT_DIR` / `HISTORY_DIR` 合并为 `ARTICLES_ROOT`，反问示例同步更新。

### Added

- 生成后 MUST 维护 `index.json` 与文件一致（新增/覆盖同步更新索引）。

## [1.0.0] - 2026-08-01

### Added

- 通用「去 AI 化」技术文章生成 skill（tri-article）。
- 占位符 + profile 机制：具体数据（`AUTHOR_PROFILE` / `PRODUCT_*` / `OUTPUT_DIR` / `HISTORY_DIR` / `DOMAIN_POOL` / `LICENSE_STMT` / `DISABLED_WORDS`）全部参数化，首次运行反问用户后落盘 `.tribro/tri-article/profile.md`，每次生成先替换再执行。
- 去 AI 化写作引擎：日期哈希选题轮转、文章类型轮换、去重检查、禁用词表、口语化风格、个性化视角库、结构自由化、随机化机制（人称/节奏）、结构模式 A/B、质量门禁 12 项自查。
- 可选产品自然植入（三层约束 + 一票否决），由 `PRODUCT_ENABLED` 开关控制。
- 上游依赖检测两态逻辑（独立运行 / 可选接入 tri-intent）。
- 首次初始化流程与 `templates/profile-skeleton.md` 骨架。
- 配套 README.md、tests/tri-article-full-testcases.md。
