# 生命周期状态机与增量同步规范（tri-wiki 治理层 · 唯一真源）

> grep 模式：`seedling|budding|evergreen|stale|deprecated|archive|生命周期|状态机|增量|mtime|rebuild|同步`
> 可执行实现：`scripts/lifecycle_govern.py`、`scripts/sync_incremental.py`。本文件是规范唯一真源。

---

## 1. 生命周期：为什么 v1 不够

v1 入库笔记的 `status` 恒为 `seedling`，没有演进路径、没有衰减机制、没有复核提醒。一次建库很漂亮，半年后就是一堆没人敢信的旧文档。

治理层引入**双轨状态机**：成长轨往上走，衰减轨往下走，两条轨道都不允许跳级。

```
成长轨：  seedling ──► budding ──► evergreen
                          │
                          │ 超过 stale_days 未复核
                          ▼
衰减轨：  stale ──► deprecated ──► archive
```

## 2. 状态定义

| 状态 | 轨 | 语义 | 谁判定 |
|---|---|---|---|
| `seedling` | 成长 | 刚入库，元数据或内容未达标 | 默认初值 |
| `budding` | 成长 | 元数据完整 +（内容达标 或 有链接） | 脚本建议 |
| `evergreen` | 成长 | 元数据完整 + 内容达标 + 有链接 | 脚本建议 |
| `stale` | 衰减 | 长期未复核，可信度存疑 | 脚本建议 |
| `deprecated` | 衰减 | 已过时，不建议引用 | **人工仲裁** |
| `archive` | 衰减 | 归档保留，不参与检索 | **人工仲裁** |

## 3. 推进判据（全部确定性，NEVER 目测）

输入：`frontmatter` 五必填字段完整度、正文有效字符数、反向链接数、最近更新日期。

| 判定 | 条件（默认参数） |
|---|---|
| → `evergreen` | 元数据完整 **且** 正文 ≥ 800 字符 **且** 反向链接 ≥ 2 |
| → `budding` | 元数据完整 **且**（正文 ≥ 800 字符 **或** 反向链接 ≥ 2） |
| → 保持 `seedling` | 其余 |
| → `stale` | 已达 evergreen/budding 且超过 `--stale-days`（默认 180）未复核 |
| → `deprecated` | 已 `stale` 且再超过 `2 × stale_days` 未处置 |
| → `archive` | 已 `deprecated` 且再超过 `2 × stale_days` 未处置 |

**硬规则**：脚本只**建议**（`--plan`），写入必须显式 `--apply`；衰减轨的 `deprecated` / `archive` 终态 MUST 经人工确认——机器可以提示「这篇该退了」，NEVER 替用户决定「这篇废了」。

阈值常量位于 `scripts/lifecycle_govern.py` 顶部（`DEFAULT_STALE_DAYS` / `MIN_LINKS` / `MIN_CHARS`），中文语料下 800 字符约等于一篇成型笔记。

## 4. 新增字段

| 字段 | 必填 | 说明 |
|---|:--:|---|
| `status` | 否（默认 `seedling`） | 取值为上表六状态之一 |
| `reviewed` | 否 | 最近一次人工/脚本复核日期，`--apply` 自动写入 |
| `dup_group` | 否 | 由 `dedup_content.py --apply` 写入的近重复簇号 |

字段注入由 `organize.py`（初次入库）与 `lifecycle_govern.py --apply`（后续治理）共同完成，规范见 `frontmatter-spec.md`。

---

## 5. 增量同步：索引是缓存

### 5.1 核心原则

> **markdown 是真相，索引状态是缓存。**

`.wiki-meta/sync-state.json` 可以在任何时刻删除，用 `--mode rebuild` 从 markdown 全量重建，语义完全等价。因此：
- 用户不装本 skill 也能读自己的知识库；
- 索引损坏 NEVER 导致数据丢失；
- 派生数据（可信度 / 转载簇 / lint 结果）NEVER 写回笔记正文（写入 `dup_group` / `status` 除外，那属于治理标记）。

### 5.2 双判据变更检测

```
mtime 差值 > 0.001s ?  ──否──►  未变更
        │ 是
        ▼
   sha256 与状态文件比对  ──相同──►  未变更（时钟抖动/复制导致）
        │ 不同
        ▼
      已修改
```

单一 mtime 判据在文件复制、时区切换、挂载盘同步时会大量误报；单 hash 判据在大库上每次全量重算代价高。先 mtime 粗筛、再 hash 确认，兼顾准确性与成本。

### 5.3 三种模式

| 模式 | 行为 | 落盘 |
|---|---|---|
| `plan` | 只输出 added/modified/unchanged/deleted 清单 | 否 |
| `apply` | 计算并刷新状态文件 | 是（原子替换 `.json.tmp` → `.json`） |
| `rebuild` | 忽略旧状态，全量重建 | 是 |

### 5.4 与 v1 全量构建的关系

v1 的六阶段管道不变；增量同步是**管道之外的治理动作**：

- 源数据有更新 → 仍走完整六阶段重建（v1 契约第 13 条保留）；
- 只是想看「哪些笔记变了 / 索引是否最新」→ 用 `sync_incremental.py --mode plan`；
- 索引状态丢失或怀疑损坏 → `--mode rebuild`。

**NEVER 静默合并新旧产物**——增量同步只管「检测与重建索引」，不管「合并新旧笔记」，后者仍是全量重建。
