# Proposal · `.tribro/` 链路文档目录命名收敛

- **状态**：`Approved: yes（方案 A）`
- **日期**：2026-09-24
- **范围**：tri-stack 全仓 37 个 `.tribro/<域>/` 目录 · 802 处引用 · 225 个文件
- **契约**：D30（proposal → 审批 → apply）。**本文件未把 `Approved` 翻为 `yes` 之前，不执行任何改动。**

## 1. 问题

`.tribro/` 下的链路文档目录，命名按 **4 套互不相干的口径**并存，且无任何文件定义过"应该用哪套"：

| 口径 | 数量 | 目录 |
|---|---|---|
| 动作 / 域名词 | 8 | `coding` `fixes` `reviews` `plans` `actions` `workflows` `loops` `sdlc` |
| skill 短名 | 21 | `content` `cost` `evolve` `guard` `humanize` `translate` `true` `god` `pm` `wiki` `learning` `music` `image` `forge` `code-analyzer` `cache` `pdf2md` `docx2md` `pptx2md` `xlsx2md` `html2md` |
| L3 子意图名 | 2 | `arch-viz`（← tri-html）、`audit-checklist`（← tri-checklist） |
| 全 slug | 3 | `tri-article` `tri-geo` `tri-jobhunt` |
| 共享契约 / 特例 | 3 | `snapshots`（← tri-intent）、`skills`（← tri-forge）、`multimedia`（← tri-mm）<br>（另：`specs` 嵌在 `coding/` 内，不占顶层，故不计入 37） |

**实际后果**：拿 skill 名去 `.tribro/` 里反查产物会踩空。最刺眼的是 `tri-html` → `arch-viz/`、`tri-checklist` → `audit-checklist/` —— 目录名既不是 skill 名也不是动作名，只有读过路由表的人才知道去哪找。

## 2. 判别标准（本 proposal 的核心主张）

不要先选"用哪套命名"，先选**可推导性**：

> **目录名能否从 skill slug 机械推导？**（去掉 `tri-` 前缀，允许常规名词化）
> - 能推导 → 通过
> - 不能推导 → 改名
> - 跨 skill 共享 → 登记豁免

这条标准的依据：`coding/` 同时装 `tri-coding` / `tri-prototype` / `tri-orchestrate` 三家产物，`sdlc/` 装 9 个 children，`skills/` 装所有 forge 生成物 —— **"一 skill 一目录"本来就不成立**。所以规则只能是"可从 skill 名推导"，不能是"目录名等于 skill 名"。

按此标准：**29 个通过**（`fixes` ← tri-fix、`plans` ← tri-plan、`loops` ← tri-loop 等常规名词化均可推导）、**5 个必须改**、**3 个豁免**。

## 3. 全量清单（37 个目录）

| 目录 | 口径 | 引用数 | 涉及文件 | 处置 |
|---|---|---|---|---|
| `snapshots` | 共享契约 / 特例 | 133 | 79 | 豁免（登记） |
| `sdlc` | 动作/域名词 | 75 | 39 | 通过（可推导） |
| `multimedia` | 共享契约 / 特例 | 61 | 16 | 豁免（登记） |
| `coding` | 动作/域名词 | 41 | 17 | 通过（可推导） |
| `skills` | 共享契约 / 特例 | 39 | 28 | 豁免（登记） |
| `loops` | 动作/域名词 | 31 | 12 | 通过（可推导） |
| `fixes` | 动作/域名词 | 27 | 11 | 通过（可推导） |
| `code-analyzer` | skill 短名 | 23 | 6 | 通过（可推导） |
| `tri-article` | 全 slug | 23 | 6 |  → `article/` |
| `wiki` | skill 短名 | 23 | 5 | 通过（可推导） |
| `cache` | skill 短名 | 22 | 7 | 通过（可推导） |
| `tri-geo` | 全 slug | 22 | 5 |  → `geo/` |
| `cost` | skill 短名 | 20 | 3 | 通过（可推导） |
| `god` | skill 短名 | 20 | 5 | 通过（可推导） |
| `actions` | 动作/域名词 | 17 | 13 | 通过（可推导） |
| `reviews` | 动作/域名词 | 17 | 6 | 通过（可推导） |
| `learning` | skill 短名 | 14 | 3 | 通过（可推导） |
| `translate` | skill 短名 | 14 | 8 | 通过（可推导） |
| `plans` | 动作/域名词 | 13 | 4 | 通过（可推导） |
| `true` | skill 短名 | 13 | 6 | 通过（可推导） |
| `docx2md` | skill 短名 | 11 | 2 | 通过（可推导） |
| `forge` | skill 短名 | 11 | 8 | 通过（可推导） |
| `html2md` | skill 短名 | 11 | 2 | 通过（可推导） |
| `pdf2md` | skill 短名 | 11 | 2 | 通过（可推导） |
| `pptx2md` | skill 短名 | 11 | 2 | 通过（可推导） |
| `workflows` | 动作/域名词 | 11 | 3 | 通过（可推导） |
| `xlsx2md` | skill 短名 | 11 | 2 | 通过（可推导） |
| `evolve` | skill 短名 | 10 | 3 | 通过（可推导） |
| `music` | skill 短名 | 10 | 5 | 通过（可推导） |
| `content` | skill 短名 | 9 | 4 | 通过（可推导） |
| `tri-jobhunt` | 全 slug | 9 | 7 |  → `jobhunt/` |
| `arch-viz` | L3 子意图名 | 8 | 2 |  → `html/` |
| `guard` | skill 短名 | 8 | 3 | 通过（可推导） |
| `audit-checklist` | L3 子意图名 | 7 | 2 |  → `checklist/` |
| `pm` | skill 短名 | 7 | 2 | 通过（可推导） |
| `humanize` | skill 短名 | 5 | 2 | 通过（可推导） |
| `image` | skill 短名 | 4 | 3 | 通过（可推导） |

## 4. 三个方案

### 方案 A（推荐）· 收敛 5 个不可推导项

- **改**：`arch-viz`→`html`、`audit-checklist`→`checklist`、`tri-article`→`article`、`tri-geo`→`geo`、`tri-jobhunt`→`jobhunt`
- **代价**：5 个目录 / **69 处引用** / 12 个文件 / **2 个脚本默认值**
- **收益**：口径从"4 套无定义"变为"**1 条规则（可推导）+ 4 个登记豁免**"，且全部有明文依据

### 方案 B（彻底）· A + 复数单数化

- **追加改**：`fixes`→`fix`、`reviews`→`review`、`plans`→`plan`、`actions`→`action`、`workflows`→`workflow`、`loops`→`loop`
- **追加代价**：**116 处引用**、4 组测试断言（tri-fix TC-06-05 / tri-review TC-08-02 / tri-plan TC-06-04 / tri-action TC-06-03）、tri-loop 门禁条目；**脚本影响为 0**
- **追加风险**：旧项目已存在的 `.tribro/fixes/` 等目录会"失联"（`.tribro/` 在 `.gitignore` 第 7 行，无版本控制、无法自动迁移）
- **收益**：形式更整齐；但按 §2 标准，复数形式**本就可推导**，属形式优化而非正确性修复

### 方案 C（最小）· 只登记不改名

- 把现状 4 套口径写进 `tri-forge/references/family-spec.md` + 合规清单第 10 项，**止住增量**
- **代价**：0 代码 / 2 个文档
- **收益**：新建 skill 不再产生第 5 套口径
- **不解决**：存量反查踩空

## 5. 兼容与回滚（通用）

- **不迁移历史产物**：`.tribro/` 已在 `.gitignore:7`，是无版本控制的本地目录。改名只对**新产生的产物**生效
- **新旧并存**：已存在旧目录的项目，下游 skill 按新路径找不到时会新建目录 —— 若不可接受，需额外一次性迁移脚本（`mv .tribro/arch-viz .tribro/html`）
- **回滚**：改动全部是纯文本替换，`git revert` 单个 commit 即可

## 6. Fix dependency order（方案 A 若批准）

1. **先立规则**：`tri-forge/references/family-spec.md` + `references/compliance-checklist.md` 第 10 项 —— 写入「可推导性」标准与 4 个豁免（单一事实源，必须在改名之前）
2. **改 skill 本体 + 脚本默认值**（5 个目录的落点声明）
3. **改测试断言**（对应 skill 的 `tests/*-full-testcases.md`）
4. **改路由/落盘约定**：`tri-intent/SKILL.md` 若含旧路径则同步
5. **改指南**：`WORKFLOW-GUIDE.html` §02 流转表 + §09 目录树 + 命名警告卡
6. **复跑校验**：全仓扫描确认旧名残留 = 0；`ops/version-lint.py` 五点一致性

### 第 2–3 步逐目录文件清单

### `arch-viz/` → `html/`（8 处，2 个文件）

- `tri-html\SKILL.md`
- `tri-html\tests\tri-html-full-testcases.md`

### `audit-checklist/` → `checklist/`（7 处，2 个文件）

- `tri-checklist\SKILL.md`
- `tri-checklist\tests\tri-checklist-full-testcases.md`

### `tri-article/` → `article/`（23 处，6 个文件）

- `tri-article\CHANGELOG.md`
- `tri-article\README.md`
- `tri-article\SKILL.md`
- `tri-article\hooks\index.py`
- `tri-article\templates\profile-skeleton.md`
- `tri-article\tests\tri-article-full-testcases.md`

### `tri-geo/` → `geo/`（22 处，5 个文件）

- `tri-geo\CHANGELOG.md`
- `tri-geo\README.md`
- `tri-geo\SKILL.md`
- `tri-geo\scripts\fetch_page.py`
- `tri-geo\tests\tri-geo-full-testcases.md`

### `tri-jobhunt/` → `jobhunt/`（9 处，7 个文件）

- `tri-jobhunt\SKILL.md`
- `tri-jobhunt\children\tri-docs\SKILL.md`
- `tri-jobhunt\children\tri-interview\SKILL.md`
- `tri-jobhunt\children\tri-jd\SKILL.md`
- `tri-jobhunt\children\tri-negotiate\SKILL.md`
- `tri-jobhunt\children\tri-resume-core\SKILL.md`
- `tri-jobhunt\children\tri-role\SKILL.md`

## 7. 附带发现（不在本 proposal 范围，另行处置）

- 🟠 **`tri-geo/.tribro/` 在 skill 包内留下 48 个本地文件**（`diag.py`、`exp-geo-20260917/`、`lessons.md`、`test-run/`）。已被 `.gitignore` 挡住、**未被版本控制**（`git ls-files` = 0），所以不进仓库；但 skill 经 junction 安装后这些文件会出现在安装位，打包时也会被收录。建议在合规清单加一条「skill 目录内禁建 `.tribro`」。
- 🔴 **`tri-frontend-design` 与 `tri-grill` 无固定 `.tribro/` 落点**，产物只随对话交付。纳入门禁审计时会因"定位不到固定产物"无法取证 —— 这是两个门禁空转的 skill，与本 proposal 的命名问题独立。

## 8. 审批

把下面这行翻成 `yes` 即视为批准对应方案（请在方案字母后标注）：

```
Approved: yes（方案 A）
```
