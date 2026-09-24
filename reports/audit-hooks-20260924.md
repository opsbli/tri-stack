# 审计报告：hook 层普查（声明 vs 实现）

- **日期**：2026-09-24
- **基线**：`main @ 1ab5196`（24 skill）＋归档分支 `archive-full-skills-20260924`（46 skill）
- **范围**：全家族对 hook 的**声明**、仓库内 hook 的**真实实现**、以及两者的差集
- **结论**：🔴 **真 hook 依赖 4 个，宿主 hook 的真实实现数为 0**。唯一的 `hooks/` 目录里放的**不是 hook**。

> ⚠️ **方法学更正**：首版用「token 以 `-hook` 结尾」朴素匹配，产出 2 个**假阳性**，已剔除（见 §1.2）。
> 教训：**命名后缀不等于语义依赖** —— 必须回读上下文确认它是「触发源」还是「标签 / 外部术语」。

---

## 一、生产现状（实测）

### 1.1 真 hook 依赖（4 个，均在「触发时机」表里作为触发源 + 注明入参）

| hook | 归属 | 触发模式 | 入参（原文） | main 上是否存在 |
|---|---|---|---|---|
| `evolve-hook` | `tri-evolve` | `EVOLVE_OBSERVE` | 作答事件 + 用户行为 | ✅ 存在该 skill |
| `cache-hook` | `tri-cache` | `CACHE_WRITE` | `{快照§三, 作答内容, source_skill}` | ❌ 已移除 |
| `cost-hook` | `tri-cost` | `COST_TRACK` | `{node_id, input/output_tokens, source_skill}` | ❌ 已移除 |
| `guard-hook` | `tri-guard` | 安装前前哨审计 | 待审 skill 的路径 / URL / 目录 / 源码 | ❌ 已移除 |

> 四者共性是：hook 是该模式的**唯一自动触发源**，缺失即只能靠用户显式调用（其余模式都另有显式入口）。

### 1.2 假阳性（2 个，已剔除，不是 hook 依赖）

| 标识符 | 实际是什么 | 证据 |
|---|---|---|
| `commit-hook` | `tri-sdlc/children/tri-devenv` 的 **frontmatter `tags` 标签**（描述其产出的「钩子配置」） | `tri-devenv/SKILL.md:8` |
| `shell-hook` | `tri-code-analyzer/references/tech-stacks/` 中描述的**外部平台术语**（Claude Code/Cursor 的 hook 形态 A） | `agent-skills-plugin.md:22` |

### 1.3 仓库内 `hooks/` 目录的真实内容

| 文件 | 所在 | 它其实是什么 |
|---|---|---|
| `tri-intent/hooks/intent-gate.py`（+`.md`） | main | **「识别结果呈现器」**（SKILL.md 原文：「定位为识别结果呈现器**而非**执行前闸门」，**可选调用**）→ **不是宿主 hook** |
| `tri-article/hooks/index.py` | 归档分支 | **文章索引与去重 CLI**（走 `.tribro/article/articles`）→ **也不是 hook** |

> 即：**`hooks/` 这个目录名在家族里名不副实**，装的是「与某 skill 配套的辅助脚本」，不是宿主回调。

---

## 二、问题

| ID | 严重度 | 问题 | 证据 |
|---|---|---|---|
| H-1 | 🔴 P0 | **4 个 hook 声明，0 个实现**。依赖 hook 的模式能否自动触发，完全取决于宿主（WorkBuddy 等）是否**另行**配置了同名 hook —— 而仓库从未交付、也从未说明如何注册 | §1.1 + §1.3 |
| H-2 | 🟠 P1 | hook 被写成「触发源之一」，但**无任何降级声明**。无 hook 时这些模式**静默退化**，用户无法从文档判断自己拿到的是完整模式还是残缺模式 | `tri-evolve` / `tri-cache` / `tri-cost` / `tri-guard` §触发时机表 |
| H-3 | 🟡 P2 | 仓库**无 hook 注册/配置文档**：没说清归谁实现、入参契约、注册在哪。想补也无契约可依 | 全仓无 hooks 配置/说明文件 |
| H-4 | 🟡 P2 | `hooks/` 目录名误导：调研者会以为「hook 已实现」，实际是配套脚本 | §1.3 |

**根因**：hook 在家族里是**隐性外部依赖** —— 被当作「已存在的基础设施」引用，但从未列入交付物清单，
也没有对应合规检查项（已核实：`compliance-checklist.md` 22 条中 **`hook` 出现 0 次**）。

---

## 三、影响面（对当前 main）

**只有 `tri-evolve` 受影响**（另 3 个 hook 的归属 skill 不在 main）：

- `evolve-hook` 缺失 → `EVOLVE_OBSERVE` 不可用 → `EVOLVE_LEARN` 无信号原料 → **「每晚自己学」断在第一环**
- 目前可用路径仅剩 `EVOLVE_APPLY`（下游请求画像 / 经验）

`tri-sdlc` / `tri-code-analyzer` **不受影响**（首版曾误判，见 §1.2 更正）。

---

## 四、优化方向（三选一或组合）

| 方案 | 内容 | 代价 | 适用 |
|---|---|---|---|
| **A · 补实现** | 在 `ops/hooks/` 下建 hook 契约与实现（先 `evolve-hook`，因它是 main 上唯一有真实需求的），并写注册说明 | 高：需确定宿主 hook 接入方式 | 真要「每晚进化」 |
| **B · 补降级声明** | 在每个依赖 hook 的 skill 的 §触发时机 表里，为 hook 触发源标注「无 hook 时的替代触发方式」（通常 = 显式命令） | 低：纯文档 | 立即做，治 H-2 |
| **C · 去 hook 化** | 把「显式命令触发」改为默认，hook 降为可选加速 | 中：改触发语义 | 要在零宿主配置下也能用 |

**建议顺序**：先 **B**（让现状可读可判断），再决定 **A**（确需自动化）或 **C**（要零外部依赖）。

---

## 五、Fix dependency order

1. **定义 hook 契约**（治 H-3）：名字 / 入参 / 触发时机 / 由谁注册 —— 单一事实源，落在 `tri-forge/references/family-spec.md`
2. **补合规检查项**：`compliance-checklist.md` 增一条「若声明 hook 触发源，MUST 同时声明无 hook 时的降级路径」（治 H-2、防复发）
3. **补降级声明**（方案 B）：改 4 个 skill 的 §触发时机
4. **实现或去化**（方案 A / C）：视第 1 步契约决定
5. **更名 `hooks/` 目录**（治 H-4）：`tri-intent/hooks/` → `tri-intent/scripts/`（与家族惯例一致），同步 SKILL.md 引用

---

## 六、评分

| 维度 | 评分 | 说明 |
|---|---|---|
| 声明完整性 | 🟢 | 4 个 hook 在触发时机表里位置明确、入参清楚 |
| 实现完整性 | 🔴 | 4 声明 / 0 实现 |
| 可判断性 | 🔴 | 无降级声明，用户无法自辨完整/残缺模式 |
| 契约可依性 | 🟠 | 无 hook 契约文档，想补也无从下手 |
| 审计方法可靠性 | 🟠 | 首版朴素匹配错 2 个；**hook 类审计必须回读上下文** |
| **综合** | 🔴 **P0** | 一个**从未交付、却被 4 个 skill 依赖**的层 |
