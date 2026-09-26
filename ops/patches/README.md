# 本地补丁层（tri-stack）

## 为什么需要它

本仓库的 skill 是从 **skillhub 平台**同步来的（作者 `TrisighT` / `user_989eb8f0`，平台共 92 个 skill）。
同步方式有两种，**两者都会整树替换 skill 目录**：

| 方式 | 命令 | 影响 |
|---|---|---|
| 版本门自动升级 | `python <skill>/scripts/check_update.py`（D 态触发） | 整树替换该 skill 目录 |
| 手动升级 | `skillhub upgrade <slug>` | 同上 |

> ⚠️ **本仓库当前已自维护**：所有 `check_update.py` 均内置 `SELF_MAINTAINED = True`，
> 版本门**不再请求平台、也不再自动升级**（D 态只报告漂移，不改文件）。
> 上表描述的是「整树替换**仍可能发生**」的前提——设 `TRI_ALLOW_REMOTE=1` 恢复远端模式即成立，
> 手动 `skillhub upgrade` 亦属此列。**故补丁层仍需按此设计保持可重放**，而非可以省去。

⇒ **直接改仓库里的 skill 文件，下次同步就会丢。** 所以本地修正必须表达成
「记录 + 可重放」，而不是一次性编辑。本目录就是那个记录。

## 目录结构

```
ops/patches/
├── README.md                       本文件
├── manifest.json                   补丁清单（声明式，唯一事实源）
├── payload/
│   └── version-check-spec.md       校正版版本检查规范（分发到各 skill 的 references/）
└── apply.py                        幂等重放器
```

## 用法

```bash
python ops/patches/apply.py             # 应用（幂等，可反复跑）
python ops/patches/apply.py --dry-run   # 只报告将发生什么
python ops/patches/apply.py --json      # 机器可读输出
```

**推荐时机**：每次 `skillhub upgrade` 之后立即重放一次。

## 实测踩过的六个坑（都会导致补丁层静默失效）

### 坑 1 · 行尾混用导致字节级匹配不命中

**本仓库行尾本就混用**（**2026-09-23 诊断时的状态**）：多数 `.md` 的 **git blob 本身就是 CRLF**
（当时实测 `README.md` blob 含 203 行 CR、`CONTRIBUTING.md` 含 133 行 CR，无 `.gitattributes`，
`core.autocrlf=true`——作者在 Windows 上开发）；而本补丁层新写入的 spec 是 LF。

> **现状已变（2026-09-25 实测）**：`.gitattributes` 已引入（`* text=auto eol=lf` +
> `*.md` / `*.py` / `*.json` / `*.html` … `text eol=lf`）、`core.autocrlf` 在 `.git/config`
> 中置为 **false**，`README.md` 的 blob **已为 LF（0 CR）**。但 `tri-intent/SKILL.md` 等
> **blob 仍为 CRLF**（386 行全 CRLF，未被 renormalize 覆盖），工作区还出现 `\r\r\n`（见坑 5）
> ⇒ **坑 1 的处置（行尾无关匹配）依然必要**；其「不充分」之处（多行 `old` 在 `\r\r\n` 上
> 静默不命中）已由 2026-09-25 的 `norm_lf` 修掉（见坑 5）。

⇒ 若按**字节**匹配 `old`/`new`（LF 书写），遇到 CRLF 文件会**静默不命中**，表现为
`应用 0｜已应用 0`（`f6-gate-fill-empty-block` 首次就是这样失败的）。

**处置**：`op_replace_text` 改为**行尾无关**——匹配前归一化为 LF，写回时恢复原行尾风格。
`op_sync_spec` 亦改为按**归一化文本**比对，避免在 CRLF 检出上反复产生无意义改写。

> 早期版本的 README 把根因写成「`write_text` 在 Windows 下把 `\n` 翻成 `\r\n`」——
> **该归因有误**，CRLF 是仓库原生状态。真实问题是「仓库行尾混用 + 字节级匹配」的组合。

### 坑 2 · 「已应用」标记不能用短串

早期版本拿 `new`（如「。」或空串）当已应用标记，结果把 **515 个无关文件**误计为「已应用」，
产出虚高数字。**必须用专属长标记**（`already_marker`），否则计数不可信。

### 坑 3 · 幂等性必须实测

`sync_spec` 首版用字节哈希比对，因行尾差异永不相等，**每次运行都报「写入 42」**，
幂等形同虚设。判据：**连续运行两次，第二次应报 `写入 0｜跳过 N`**。

### 坑 4 · 纯**删除型**修正没有可用的 `already_marker`

**场景**：修正的实质是**把一段文本删掉一部分**（而非插入或改写语义），期望 `old`（改前文本）
命中一次、替换为 `new`（改后文本）。

**根因**：`op_replace_text` 的判定顺序是「**先判 marker、再判 old**」：

```python
if marker and marker in txt:
    already += 1
    continue          # ← 命中即判「已应用」，old 根本不看
n_old = txt.count(old_lf)
```

而**纯删除型修正的改后文本，其每一个连续子串都必然已在改前文本中出现过**——包括跨被删边界的
「接缝」。于是两条路都堵死：

- 若拿 `new` 的某个子串当 marker（`new` 缺省即作 marker）⇒ marker 在**改前**就命中
  ⇒ op 被判「已应用」而**永不生效**；
- 若改用改前文本里的短串当 marker ⇒ 同样在改前命中（即坑 2）。

**实测案例（`f19-compliance-dedup`）**：原计划 `already_marker = 'role = "unknown"'`，
但该串在改前文件里**已出现 2 次** ⇒ op 永不生效。曾试图为「接缝」找一个改前不含的子串，
结果证明**不存在** —— 把改后文本按所有可能边界切分，每个片段都能在改前文本里找到
（例如 `role = "unknown"\n\n    r = []`，改前 L169-171 本就是这个形态）。

**修复范式**：`new` **必须引入改前不存在的新文本**，并以此充当 marker。`f19` 的做法是在保留处
加注「——单次赋值（去重后仅保留一处，勿再复制）」，取其中一段作 `already_marker`。

**判据**：写 op 前**先断言** `marker not in pre_fix_text`，写后断言 `marker in post_fix_text`
（`f20` 已把这两条固化成构建脚本里的 `assert`）；随后连跑两次 `apply.py`，
第二次应为 `应用 0｜已应用 1`。

### 坑 5 · 工作区 `\r\r\n` 会让多行 `old` **静默不命中**

> ✅ **已修复（2026-09-25）**：`apply.py` 新增 `norm_lf()`，`read_norm` 改为走它
> （去掉**全部** `\r`）；`op_sync_spec` / `op_sync_script` 的字节比对一并修正
> （原写法会让 `\r\r\n` 目标**每次判「不一致」而反复重写**，属坑 3 的同类）。
> **验收**：旧 / 新 `apply.py --json` 输出**逐字相同**（当前树零行为变化，因为下列
> 16 个文件对现有 op 本就零命中）；合成复测 `t_crcrlf.txt` 由 `count=0` → **`count=1`**。
> **坑位保留**：同类写法在别处仍极易复现（任何自己读仓库文件的脚本）——判据见文末。

**背景**：坑 1 解决的是「CRLF 检出 + 字节级匹配」。本仓库还有更刁的一种：**`\r\r\n`**。
实测归因（2026-09-25）：`core.autocrlf` 为 **`false`**（`.git/config`）、`.gitattributes` 目标是 LF，
而 `tri-intent/SKILL.md` 等 **blob 仍是 CRLF**（386 行全 CRLF）⇒ `\r\r\n` **不是** autocrlf 造成，
而是检出/写入链在已有 CRLF 之上**再补一个 CR**。（**别照抄原因**——2026-09-23 的诊断曾把同类
现象归给 `core.autocrlf=true`，该归因现已不成立。）

**修复前**，`read_norm` 只做 `.replace("\r\n", "\n")` —— 对 `\r\r\n` 只会吃掉后一个 `\r`，
**留下一个裸 `\r`**：

| 文件字节 | `read_norm` 归一后 | 多行 `old`（LF 书写）命中 |
|---|---|---|
| `AAA\nBBB\n` | `AAA\nBBB\n` | ✅ |
| `AAA\r\nBBB\r\n` | `AAA\nBBB\n` | ✅ |
| `AAA\r\r\nBBB\r\r\n` | `AAA\r\nBBB\r\n` | ❌ **`count == 0`** |

⇒ 多行 `old` 在 `\r\r\n` 文件上**永不命中**，op 报 `应用 0｜已应用 0`（= `not_found`），
**且没有任何报错**。写回本身是**保形**的（`write_keep` 会把 `\n` 还原为 `\r\n`，往返无损），
所以问题**只在匹配**，不在写回。

**实测**（2026-09-25，`f20` 轮，直接调用 `apply.read_norm` / `write_keep`）：

```
t_lf.txt       count(old_lf)=1   ✅
t_crlf.txt     count(old_lf)=1   ✅
t_crcrlf.txt   count(old_lf)=0   ❌  ← 归一后为 'AAA\r\nBBB\r\nCCC\r\n'
```

全仓扫描**16 个文件**为 `\r\r\n`：`tri-intent` / `tri-checklist` / `tri-evolve` / `tri-html` 的
`SKILL.md`，加 12 个 `CHANGELOG.md`（`tri-action` / `coding` / `evolve` / `fix` / `html` /
`intent` / `loop` / `meta` / `plan` / `sdlc` / `true` / `workflow`）。

**修复前的暴露面**：当时的 31 个 op 中，只有 `f3-standalone-line` / `f3-gate-cmd-check` /
`f3-gate-cmd-apply` 满足「glob `**/*.md` **且** 多行 `old`」⇒ 理论上可受影响；实测这三者的
`old` 在那 16 个 `\r\r\n` 文件中以及**全仓活跃树**内均**零命中**，故当时读数没变。
**它是「上游整树替换后重放」这一设计场景里的定时炸弹** —— 上游若带回含该文本的文件，
命中会被静默吞掉，而补丁层只会安静地报 `not_found`。

**写法纪律**（`apply.py` 已修，但**自己写脚本读仓库文件时同样适用**）：

- **单行 `old` 天然免疫**；多行 `old` 经 2026-09-25 的修复后**已可正常使用**，
  但若你自己写脚本做 `old`/`new` 匹配或内容解析，仍须自行**去尽 `\r`**；
- 需要**读文件内容做解析**时，先去掉**全部** `\r`：`re.sub(r"\r", "", raw)`。
  ⚠️ 「先替 `\r\n` 再替 `\r`」是**错的**（`\r\r\n` 会被拆成两次匹配 ⇒ 仍得 `\n\n`）；
  `read_text()` 的通用换行同样把 `\r\r\n` 译成 `\n\n` 并**插入空行**
  （`f20` 解析 `tri-intent` 路由表时因此**两次**返回空集，循环在首行后即 `break`）。

**判据**：按 **byte** 统计 `raw.count(b"\r\n")` 与 `raw.count(b"\r")`；两者不等即存在裸 `\r`
（`\r\r\n` 的特征是 `\r` 数 ≈ `2 ×` `\r\n` 数）。**不要用 `read_text()` 数** —— 它会归一化，
`\r` 恒为 0，给出假象。

### 坑 6 · `--dry-run` 下依赖前序 op 产物的锚点必然 `not_found`

`apply.py --dry-run` **不落盘**。若某 op 的锚点文本**由前序 op 的 `new` 生成**（典型：为前序
改名 / 新增的段落再补一行），dry-run 时前序 op 的产物还不存在 ⇒ 该 op 报 `not_found`，**属正常态**。

| 实证 | 锚点来源 | dry-run | 真实 `apply.py` |
|---|---|---|---|
| `f50a-req-audit-tests-cap-row3` | `| 3 \| 九维判定（D1–D9） \| … TC-A02 – TC-A09 \|`，由 `f46a` / `f46b` 改名（`八维`→`九维`、`D1–D8`→`D1–D9`）产生 | `not_found`（虚警） | **`应用 1`** |
| `f47b-req-audit-rename-dimrange-py` | `.py` 里的 `D1–D8` | `not_found` | `not_found` ⇒ **真多余** |

⇒ **判据**：删「锚点不存在」的 op 前，必须以**真实 `apply.py`（非 dry-run）**的读数为准；
dry-run 的 `not_found` 只能证明「此刻树上没有」，**不能**证明「op 冗余」。
二者混同会把 `f50a` 这类**正常态虚警**误删（该 op 删了就会让能力清单第 3 行版本号漏改）。

## 当前补丁清单

| id | 类型 | 作用 |
|---|---|---|
| `spec-per-skill` | sync_spec | 为每个引用 `version-check-spec.md` 的 skill 部署校正版自带 spec（当前 35 个 = 顶层 26 + `children/*` 9；实测 `跳过 35`） |
| `f2-pointer` | replace_text | 版本门真源指针 `tri-forge/references/version-check-spec.md` → `references/version-check-spec.md` |
| `f3-clause-inline` | replace_text | 移除「；发布前 MUST 通过 python tri-forge/scripts/sync_registry.py --check。」 |
| `f3-clause-sentence` | replace_text | 移除「。发布前 MUST 通过 …」句首变体 |
| `f3-standalone-line` | replace_text | 移除独立的「- 发布前 MUST 通过 …」行 |
| `f3-gate-cmd-check` | replace_text | 移除 version-gate.md 的 `sync_registry.py --check` 命令行 |
| `f3-gate-cmd-apply` | replace_text | 移除 version-gate.md 的 `sync_registry.py --apply` 命令行 |
| `f5-gate-charter` | replace_text | `tri-intent/references/version-gate.md`：「唯一真源」→「家族设计总纲」 |
| ~~`f5-humanize-wording`~~ | replace_text | （已移除：原 `tri-humanize` 未包含在本分支，对应 op 已从 `manifest.json` 删除） |
| `f6-gate-fill-empty-block` | replace_text | `version-gate.md` §六：填补被清空的发布前门禁代码块 |
| `sync-version-meta` | sync_version_meta | P1↔P3：`_meta.json` 版本 = SKILL.md 版本（规则化） |
| `sync-readme-version` | sync_readme_version | P1↔P5：README 版本声明 = SKILL.md 版本（规则化） |
| `self-maintained-const-func` | replace_text | 版本门：注入 `SELF_MAINTAINED` 常量与 `self_consistent_check()` |
| `self-maintained-branch` | replace_text | 版本门：在节流检查前插入自维护分支（跳过远端比对） |
| `converge-version-stub` | converge_version_section | 顶层 skill 版本节统一为瘦指针 STUB（当前 **26** 个 = 顶层全部；含 `force_skills` 补齐的 9 个） |
| `converge-version-stub-children` | converge_version_section | `tri-sdlc/children/*` 9 个子阶段 skill 同款收敛（同缺陷类，scope 独立便于裁定） |
| `f7-contract-mode` | replace_text | 契约 §0：「连接 skillhub 校验 + `skillhub upgrade`」→ 自维护本地校验（22 处） |
| `f7b-contract-mode-intent` | replace_text | 契约 §0 变体（`tri-intent`）：远端校验/升级 + 端点内联 → 自维护口径 |
| `f8-install-hint-self-maintained` | replace_regex | 引导安装提示：`skillhub install <slug> [--dir <目标目录>]` → 自维护安装器（58 文件 / 66 处） |
| `f9-gate-script-rebuilt` | replace_text | `version-gate.md` §六：更正「脚本门禁当前缺失」→ 已重建为 `tri-forge/scripts/check_registry.py` |
| `f10-children-check-update` | sync_script | 为 `tri-sdlc/children/*` 的 9 个子 skill 各部署自带 `scripts/check_update.py`（对齐顶层；STUB 命令不再悬空） |
| `f11-children-tests-version` | replace_regex | 子 skill 的 tests 描述版本引用 `v1.1.1` → `v1.1.2`（随版本线补升同步） |
| `f12-children-readme-tree` | replace_text | 子 skill README 目录树：补列实际存在的 `references/` 与新增的 `scripts/check_update.py` |
| `f13-check-update-decouple` | sync_script | 顶层 26 份 `check_update.py` 统一为去耦形态（清除 `tri-intent` 硬编码耦合；首轮 2026-09-25 实际 `写入 22｜跳过 2`，跳过的即已去耦的 `tri-code-analyzer` / `tri-lottie`；后续新增 `tri-req-audit` / `tri-verify` 均已自带去耦版 ⇒ 现 **全量跳过**） |
| `f14-req-audit-two-hop` | replace_text | family-spec §五：登记 `tri-req-audit` 二跳路由例外（2026-09-25 补记，op 于 2026-09-25 随 tri-req-audit 锻造加入） |
| `f15-agents-md-coding-rules` | replace_text | `tri-init` AGENTS.md 模板：新增「通用编码行为规则（8 条）」章节——写码纪律（最简实现 / 分层成长 / 先用已有依赖等），与项目特定编码规范正交；第 1 条采用兼容安全版（2026-09-25） |
| `f15b-tests-t31` | replace_text | `tri-init` 测试用例：AGENTS.md 内容验证节追加 T31（该文件第六/七节本有历史性重复，`replace_text` 全量命中使两份同步获得 T31）（2026-09-25） |
| `f16-tri-init-version` | replace_regex | `tri-init` 版本线 1.0.2 → 1.0.3（SKILL.md frontmatter；**必须排在 `sync-version-meta` 之前**，P3 才能同轮跟随）（2026-09-25）；改用 **settle 形式**（`^version: \d+\.\d+\.\d+$` → 目标；任意旧版本收敛至目标，目标就地更新） |
| `f17-tri-init-changelog` | replace_text | `tri-init` CHANGELOG：追加 `[1.0.3]` 条目（P2 属人工内容，由 op 表达而非手改文件）（2026-09-25） |
| `f18-familyspec-shared-domain` | replace_text | `family-spec.md` §1.4：补「**判定顺序**」（**可推导优先** —— 共享但可推导者仍属「通过」，豁免只收「共享 ∩ 不可推导」）+ 给豁免清单两行补「不可推导」依据；消除 `coding/` 两行同时命中的歧义（2026-09-25） |
| `f19-compliance-dedup` | replace_text | `compliance_check.py`：删去重复的「角色识别」if/elif 链（原 L143-155 与 L157-169 逐字重复、二次赋值同值、行为无差异）；保留处加注「单次赋值」作幂等标记（2026-09-25） |
| `f20-role-detection` | replace_text | `compliance_check.py`：修复**角色识别盲区** —— ① 按 `tri-intent/SKILL.md` §一 路由映射表（`family-spec` §1.1 真源）收 slug 集合，**收录即判下游**；② 下游判据由「下游 ∩ 认领」改为「`下游执行` 写法 ∪ 真源收录」；③ `children` 判定**前移**并用目录结构作主判据；④ 读真源先 `re.sub(r"\r","")` 去尽 CR。效果：`unknown` **8 → 0**、`downstream` **8 → 16**、#8 由 N-A 转 MANUAL，**verdict 无变化**（2026-09-25） |
| `f21-fed-route-declaration` | replace_text | `tri-frontend-design/SKILL.md`：§触发时机 补「**tri-intent 路由（一跳覆写）**」触发行 + **路由归属**注记（原文自称「独立工具 skill，不注册为 tri-intent 下游路由项」属**滞后口径**，与 `tri-intent/SKILL.md` §一 路由映射表 / `doing/I11-coding.md` / `hooks/intent-gate.py` 可执行映射冲突）；旧文本内嵌「⚠️ 已废弃」防回流（2026-09-25） |
| `f22-fed-boundary-mece` | replace_text | 同上：§职责边界 —— 「不认领任何 L2/L3 编码」→ 只认领 `I11` 的 `L3=frontend-design` 子类；「MECE：不认领下游路由，作为独立工具存在」→ **参与**路由并与同层五落点（tri-coding / tri-lottie / tri-prototype / tri-html / tri-sdlc）按**产出物形态**划分；Not-Trigger 末项改为「L1 识别 / L2 分流由 tri-intent 负责」（2026-09-25） |
| `f23-fed-selfcheck-line` | replace_text | 同上：契约 §6 自检句 `下游=<否>` → `路由=<I11/frontend-design 子类｜用户直调>`（原字段编码的正是「不位于下游」这一滞后口径）（2026-09-25） |
| ~~`f24-fed-version-1-1-4`~~ | replace_text | （已移除：版本线 op 改 settle 形式后，该 op 的 `old`（1.1.3）被后序版本 op `f91` 销毁 ⇒ 值型 marker 永久失配；其目标（1.1.4 → 1.1.5）由 `f91-ver-frontend-design` 的 settle 形式承接，故从 `manifest.json` 删除） |
| `f25-fed-changelog-1-1-4` | replace_text | `tri-frontend-design` CHANGELOG：追加 `[1.1.4]` 条目（P2 属人工内容，由 op 表达而非手改文件）（2026-09-25） |
| `f26-coding-verify-gate-contract` | replace_text | `tri-coding` 契约新增 **§7 交付前功能验证自动门**（tri-verify 委派），原 §7 风险预筛顺延为 §8 —— 建立强制力来源（2026-09-25） |
| `f27-coding-verify-workflow-ascii` | replace_text | `tri-coding` §编码工作流 ASCII 链路图：在 `implements.md` 与「§交付前风险预筛」之间插入**功能验证门**（含失败回流支线）（2026-09-25） |
| `f28-coding-verify-gate-section` | replace_text | `tri-coding` 新增 **§交付前功能验证自动门** 章节（时机 / V1–V5 触发规则 / 五态消费表 / 强制规则），插入「§交付前风险预筛自动门」之前（2026-09-25） |
| `f29-coding-verify-stage-row` | replace_text | `tri-coding` §阶段速查表追加**阶段 9**（功能验证自动门 + `verdict.md` 载体）（2026-09-25） |
| `f30-coding-verify-quality-row` | replace_text | `tri-coding` §质量标准追加「**功能验证**」维度（五态区分 + 已升级人审不得自动交付 + 可执行判据）（2026-09-25） |
| `f31-coding-verify-boundary` | replace_text | `tri-coding` §职责边界「不负责」清单补入 `tri-verify`（功能验证由 tri-verify 委派执行，本 skill 只消费判据）（2026-09-25） |
| `f32-fix-reverify-contract` | replace_text | `tri-fix` 契约新增 **§8 修复后复验**（tri-verify 委派 · 防回归硬门），原 §8 风险预筛顺延为 §9 —— 补上「修好 A 破坏 B」的机械判据（2026-09-25） |
| `f33-fix-reverify-quality-row` | replace_text | `tri-fix` §质量标准追加「**修复后复验**」维度（前后运行对比无回归）（2026-09-25） |
| `f34-family-spec-tri-verify-reg` | replace_text | `family-spec` §五 登记 `tri-verify` 两项：① **横向型委派契约**（含「自检句采用标准格式、无例外」的 #20 核实结论）② **引擎抽象与判据印章四概念**的单一事实源位置（2026-09-25） |

| `f43-req-audit-version-1-1-0` | replace_regex | `tri-req-audit` 版本线 1.0.0 → **1.1.0**（对抗层硬化属 minor）。**必须排在 `sync-version-meta` / `sync-readme-version` 之前**，P3/P5 才能同轮跟随 —— 该 op 由 `manifest.json` **插序**实现（2026-09-25）；改用 **settle 形式**（`^version: \d+\.\d+\.\d+$` → 目标；任意旧版本收敛至目标，目标就地更新） |
| `f46a-req-audit-rename-nine-md` | replace_regex | `tri-req-audit/**/*.md`（skip `CHANGELOG.md`）：「八维」→「九维」（D9 对抗维落地后的口径同步；CHANGELOG 属追加型历史，禁用 `skip_names` 豁免）（2026-09-25） |
| `f46b-req-audit-rename-dimrange-md` | replace_regex | 同上：`D1–D8` → `D1–D9`（维数区间随 D9 扩容；`en-dash` 逐字，勿写成普通连字符）（2026-09-25） |
| `f47a-req-audit-rename-nine-py` | replace_regex | `tri-req-audit/scripts/*.py`：「八维」→「九维」（脚本内提示文案同步）（2026-09-25） |
| `f35-req-audit-d9-dimension` | replace_text | `references/audit-dimensions.md` 新增 **§二 D9 对抗维**：≥3 条可证伪场景、≥1 条须落其余维度判「通过」处、构造不出须列 ≥3 个尝试过的攻击入口、与 D4 的 MECE 区分（在场 vs 可证伪）、「无对抗小节 = 违规」（2026-09-25） |
| `f36-req-audit-evidence-rule` | replace_text | 同上 **§四 H5 可复算证据**：P0/P1 必附 `文件:行号` + 引文；无引文一律降 P2 并标 `evidence=unverifiable`（2026-09-25） |
| `f37-req-audit-independence-field` | replace_text | 同上 **§五 `independence=`**：三取值（`same-agent` / `independent-agent` / `external-tool`）+ 同源禁用字样（同源时禁写「独立审核」「独立第三方」）+「委派 ≠ 独立」（2026-09-25） |
| `f38-req-audit-contract-rules` | replace_text | `tri-req-audit/SKILL.md`：契约自检句增 `对抗=` / `独立性=`；新增**铁律 12**（对抗结论必填，无该小节 = 不合规，门④判不通过）与**铁律 13**（跨轮单调性）（2026-09-25） |
| `f39b-req-audit-dim-table-d9` | replace_text | `SKILL.md` §审核维度速查表增 **D9** 行（与 `audit-dimensions.md` 对表）（2026-09-25） |
| `f40-req-audit-aggregate-monotonic` | replace_text | `SKILL.md` §阶段三增**单调性守卫**行（P0/P1 结论下降须有新证据；零新证据下降 ⇒ 强制升级人审）（2026-09-25） |
| `f41-req-audit-gate4-guard` | replace_text | `SKILL.md` 门④ 行升级为「+ 单调性守卫 + 机械守卫自检（`audit_gate.py` 非 0 ⇒ **不得落盘交付**）」（2026-09-25） |
| `f42a-req-audit-deliverable-ledger-row` | replace_text | `SKILL.md` 交付产物表增 `round-ledger.jsonl` 行（跨轮账本，单调性守卫的数据源）（2026-09-25） |
| `f42b-req-audit-deliverable-rules` | replace_text | `SKILL.md` 落盘规则「三件套」→「**四件套**」（补入账本）（2026-09-25） |
| `f44-req-audit-changelog-1-1-0` | replace_text | `tri-req-audit/CHANGELOG.md`：追加 `[1.1.0]` 条目（P2 属人工内容，由 op 表达而非手改文件）（2026-09-25） |
| `f45-familyspec-adversarial-delegation` | replace_text | `tri-forge/references/family-spec.md` §五：登记「**对抗委派二跳 · `tri-req-audit`**」（被执行方 = 家族外 `metago-adversarial-review`；未装即降级为内置 D9）（2026-09-25） |
| `f48-req-audit-gate-script` | sync_script | `sync_script`：把 `ops/patches/assets/audit_gate.py` 部署为 `tri-req-audit/scripts/audit_gate.py` —— **门④ 的牙**（R1–R4 + L2 五条机械判据 + `--self-test` 反例夹具）（2026-09-25） |
| `f49a-req-audit-template-adversarial-section` | replace_text | `templates/req-audit-report.md`：新增「**十、对抗式审查结论（D9 · 必填）**」小节（3 条占位）（2026-09-25） |
| `f49b-req-audit-template-independence-row` | replace_text | 同上 §七：增 `independence=` 行（与 SKILL.md 自检句对表）（2026-09-25） |
| `f50a-req-audit-tests-cap-row3` | replace_text | `tests/tri-req-audit-full-testcases.md` 能力清单增第 **13** 行（D9 对抗维）（2026-09-25） |
| `f50b-req-audit-tests-cap-rows` | replace_text | 同上：增第 **14–15** 行（独立性声明 / 跨轮单调性）（2026-09-25） |
| `f50c-req-audit-tests-case-a13` | replace_text | 同上：新增用例 **TC-A13**（DC 类校验同步）（2026-09-25） |
| `f50d-req-audit-tests-cases-d06-08` | replace_text | 同上：新增用例 **TC-D06–D08**（对抗 / 独立性 / 单调性）；§六 用例数 TC-A 12→13、TC-D 5→8（2026-09-25） |
| `f60-action-fallback` | replace_text | `tri-action` 补 §兜底处理（五类异常覆盖 + NEVER 静默失败）—— 门④ #14 收口 |
| `f61-checklist-fallback` | replace_text | `tri-checklist` 补 §兜底处理（五类异常覆盖 + NEVER 静默失败）—— 门④ #14 收口 |
| `f62-evolve-fallback` | replace_text | `tri-evolve` 补 §兜底处理（五类异常覆盖 + NEVER 静默失败）—— 门④ #14 收口 |
| `f63-fix-fallback` | replace_text | `tri-fix` 补 §兜底处理（五类异常覆盖 + NEVER 静默失败）—— 门④ #14 收口 |
| `f64-loop-fallback` | replace_text | `tri-loop` 补 §兜底处理（五类异常覆盖 + NEVER 静默失败）—— 门④ #14 收口 |
| `f65-lottie-fallback` | replace_text | `tri-lottie` 补 §兜底处理（五类异常覆盖 + NEVER 静默失败）—— 门④ #14 收口 |
| `f66-meta-fallback` | replace_text | `tri-meta` 补 §兜底处理（五类异常覆盖 + NEVER 静默失败）—— 门④ #14 收口 |
| `f67-sdlc-fallback` | replace_text | `tri-sdlc` 补 §兜底处理（五类异常覆盖 + NEVER 静默失败）—— 门④ #14 收口 |
| `f68-workflow-fallback` | replace_text | `tri-workflow` 补 §兜底处理（五类异常覆盖 + NEVER 静默失败）—— 门④ #14 收口 |
| `f69-14-structural` | replace_text | compliance_check.py 第 14 条判据硬化：由「正文出现兜底+NEVER」的存在性代理，改为「须存在专门的 `##/### 兜底处理` 章节且含 NEVER」的结构判定；五类关键词命中数作为建议项写入回执（非硬门槛），并如实报告是否命中专门章节 |
| `f70-code-analyzer-fallback` | replace_text | tri-code-analyzer：新增「兜底处理（NEVER 静默失败）」章节（门④ 第 14 条须有专门章节）——按本 skill 触发源与既有机制定制五类异常降级路径 |
| `f71-coding-fallback` | replace_text | tri-coding：新增「兜底处理（NEVER 静默失败）」章节（门④ 第 14 条须有专门章节）——按本 skill 触发源与既有机制定制五类异常降级路径 |
| `f72-frontend-design-fallback` | replace_text | tri-frontend-design：新增「兜底处理（NEVER 静默失败）」章节（门④ 第 14 条须有专门章节）——按本 skill 触发源与既有机制定制五类异常降级路径 |
| `f73-god-fallback` | replace_text | tri-god：新增「兜底处理（NEVER 静默失败）」章节（门④ 第 14 条须有专门章节）——按本 skill 触发源与既有机制定制五类异常降级路径 |
| `f74-html-fallback` | replace_text | tri-html：新增「兜底处理（NEVER 静默失败）」章节（门④ 第 14 条须有专门章节）——按本 skill 触发源与既有机制定制五类异常降级路径 |
| `f75-intent-fallback` | replace_text | tri-intent：新增「兜底处理（NEVER 静默失败）」章节（门④ 第 14 条须有专门章节）——按本 skill 触发源与既有机制定制五类异常降级路径 |
| `f76-plan-fallback` | replace_text | tri-plan：新增「兜底处理（NEVER 静默失败）」章节（门④ 第 14 条须有专门章节）——按本 skill 触发源与既有机制定制五类异常降级路径 |
| `f77-review-fallback` | replace_text | tri-review：新增「兜底处理（NEVER 静默失败）」章节（门④ 第 14 条须有专门章节）——按本 skill 触发源与既有机制定制五类异常降级路径 |
| `f78-true-fallback` | replace_text | tri-true：新增「兜底处理（NEVER 静默失败）」章节（门④ 第 14 条须有专门章节）——按本 skill 触发源与既有机制定制五类异常降级路径 |
| `f79-version-discipline` | replace_text | family-spec §六：新增步骤 6「变更时（版本纪律 · MUST）」——SKILL.md 正文章节级增删改 MUST 至少 PATCH 升版 + CHANGELOG 条目（此前无 MUST 条文，本轮实测 f15→f16→f17 三件套已是事实惯例，本次成文） |
| `f80-ver-action` | replace_regex | tri-action 版本线 1.2.4 → 1.2.5（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f81-ver-checklist` | replace_regex | tri-checklist 版本线 1.1.4 → 1.1.5（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f82-ver-evolve` | replace_regex | tri-evolve 版本线 1.1.6 → 1.1.7（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f83-ver-fix` | replace_regex | tri-fix 版本线 1.5.1 → 1.5.2（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f84-ver-loop` | replace_regex | tri-loop 版本线 1.2.4 → 1.2.5（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f85-ver-lottie` | replace_regex | tri-lottie 版本线 1.0.3 → 1.0.4（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f86-ver-meta` | replace_regex | tri-meta 版本线 1.2.4 → 1.2.5（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f87-ver-sdlc` | replace_regex | tri-sdlc 版本线 1.1.5 → 1.1.6（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f88-ver-workflow` | replace_regex | tri-workflow 版本线 1.2.5 → 1.2.6（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f89-ver-code-analyzer` | replace_regex | tri-code-analyzer 版本线 1.5.1 → 1.5.2（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f90-ver-coding` | replace_regex | tri-coding 版本线 1.8.1 → 1.8.2（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f91-ver-frontend-design` | replace_regex | tri-frontend-design 版本线 1.1.4 → 1.1.5（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f92-ver-god` | replace_regex | tri-god 版本线 1.2.3 → 1.2.4（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f93-ver-html` | replace_regex | tri-html 版本线 1.3.3 → 1.3.4（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f94-ver-intent` | replace_regex | tri-intent 版本线 1.14.1 → 1.14.2（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f95-ver-plan` | replace_regex | tri-plan 版本线 1.3.2 → 1.3.3（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f96-ver-review` | replace_regex | tri-review 版本线 1.7.0 → 1.7.1（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f97-ver-true` | replace_regex | tri-true 版本线 1.1.4 → 1.1.5（SKILL.md frontmatter；P3/P5 由 sync op 同轮跟随）（**settle 形式**：任意旧版本收敛至该目标；目标就地更新，NEVER 追加链式 op） |
| `f98-cl-action` | replace_text | tri-action CHANGELOG：追加 [1.2.5] 条目（兜底章节补齐；P2 属人工内容） |
| `f99-cl-checklist` | replace_text | tri-checklist CHANGELOG：追加 [1.1.5] 条目（兜底章节补齐；P2 属人工内容） |
| `f100-cl-evolve` | replace_text | tri-evolve CHANGELOG：追加 [1.1.7] 条目（兜底章节补齐；P2 属人工内容） |
| `f101-cl-fix` | replace_text | tri-fix CHANGELOG：追加 [1.5.2] 条目（兜底章节补齐；P2 属人工内容） |
| `f102-cl-loop` | replace_text | tri-loop CHANGELOG：追加 [1.2.5] 条目（兜底章节补齐；P2 属人工内容） |
| `f103-cl-lottie` | replace_text | tri-lottie CHANGELOG：追加 [1.0.4] 条目（兜底章节补齐；P2 属人工内容） |
| `f104-cl-meta` | replace_text | tri-meta CHANGELOG：追加 [1.2.5] 条目（兜底章节补齐；P2 属人工内容） |
| `f105-cl-sdlc` | replace_text | tri-sdlc CHANGELOG：追加 [1.1.6] 条目（兜底章节补齐；P2 属人工内容） |
| `f106-cl-workflow` | replace_text | tri-workflow CHANGELOG：追加 [1.2.6] 条目（兜底章节补齐；P2 属人工内容） |
| `f107-cl-code-analyzer` | replace_text | tri-code-analyzer CHANGELOG：追加 [1.5.2] 条目（兜底章节补齐；P2 属人工内容） |
| `f108-cl-coding` | replace_text | tri-coding CHANGELOG：追加 [1.8.2] 条目（兜底章节补齐；P2 属人工内容） |
| `f109-cl-frontend-design` | replace_text | tri-frontend-design CHANGELOG：追加 [1.1.5] 条目（兜底章节补齐；P2 属人工内容） |
| `f110-cl-god` | replace_text | tri-god CHANGELOG：追加 [1.2.4] 条目（兜底章节补齐；P2 属人工内容） |
| `f111-cl-html` | replace_text | tri-html CHANGELOG：追加 [1.3.4] 条目（兜底章节补齐；P2 属人工内容） |
| `f112-cl-intent` | replace_text | tri-intent CHANGELOG：追加 [1.14.2] 条目（兜底章节补齐；P2 属人工内容） |
| `f113-cl-plan` | replace_text | tri-plan CHANGELOG：追加 [1.3.3] 条目（兜底章节补齐；P2 属人工内容） |
| `f114-cl-review` | replace_text | tri-review CHANGELOG：追加 [1.7.1] 条目（兜底章节补齐；P2 属人工内容） |
| `f115-cl-true` | replace_text | tri-true CHANGELOG：追加 [1.1.5] 条目（兜底章节补齐；P2 属人工内容） |
| `dw-true-contract-fix` | replace_text | tri-true 契约第 1 条修复：`&**：` → `1. **强制前置（按模式分流）**：`（模板复制事故；darwin P0 批） |
| `dw-true-dedupe-runtime` | replace_text | tri-true 去重：与 §交付产物·二 重复的「运行时落盘结构」目录树收敛为指针 |
| `dw-true-changelog` | replace_text | tri-true CHANGELOG：追加 [1.1.6] 条目（契约修复 + 去重） |
| `dw-orchestrate-dedupe` | replace_text | tri-orchestrate 去重：删除「交付产物」下逐字重复的第二份「兜底处理」表 |
| `dw-tri-orchestrate-version` | replace_regex | tri-orchestrate 版本线 settle → 1.0.2（darwin P0 批） |
| `dw-orchestrate-changelog` | replace_text | tri-orchestrate CHANGELOG：追加 [1.0.2] 条目（兜底表去重） |
| `dw-meta-dirtree` | replace_text | tri-meta 目录结构节纠偏：补登实际存在的 `references/version-check-spec.md` 与 `scripts/check_update.py` |
| `dw-meta-changelog` | replace_text | tri-meta CHANGELOG：追加 [1.2.6] 条目（目录结构节纠偏） |
| `dw-design-contract-fix` | replace_text | tri-design 契约第 1 条修复：`&**：` → `1. **强制前置**：` |
| `dw-tri-design-version` | replace_regex | tri-design 版本线 settle → 1.1.3（darwin P0 批） |
| `dw-design-changelog` | replace_text | tri-design CHANGELOG：追加 [1.1.3] 条目（契约第 1 条修复） |
| `dw-impl-contract-fix` | replace_text | tri-impl 契约第 1 条修复：`&**：` → `1. **强制前置**：` |
| `dw-tri-impl-version` | replace_regex | tri-impl 版本线 settle → 1.1.3（darwin P0 批） |
| `dw-impl-changelog` | replace_text | tri-impl CHANGELOG：追加 [1.1.3] 条目（契约第 1 条修复） |
| `dw-test-contract-fix` | replace_text | tri-test 契约第 1 条修复：`&**：` → `1. **强制前置**：` |
| `dw-tri-test-version` | replace_regex | tri-test 版本线 settle → 1.1.3（darwin P0 批） |
| `dw-test-changelog` | replace_text | tri-test CHANGELOG：追加 [1.1.3] 条目（契约第 1 条修复） |

| `dw2-tri-action-p1-section` | replace_text | `tri-action` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-checklist-p1-section` | replace_text | `tri-checklist` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-code-analyzer-p1-section` | replace_text | `tri-code-analyzer` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-coding-p1-section` | replace_text | `tri-coding` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-domain-p1-section` | replace_text | `tri-domain` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-evolve-p1-section` | replace_text | `tri-evolve` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-fix-p1-section` | replace_text | `tri-fix` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-forge-p1-section` | replace_text | `tri-forge` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-frontend-design-p1-section` | replace_text | `tri-frontend-design` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-god-p1-section` | replace_text | `tri-god` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-grill-p1-section` | replace_text | `tri-grill` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-html-p1-section` | replace_text | `tri-html` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-init-p1-section` | replace_text | `tri-init` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-intent-p1-section` | replace_text | `tri-intent` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-loop-p1-section` | replace_text | `tri-loop` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-lottie-p1-section` | replace_text | `tri-lottie` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-meta-p1-section` | replace_text | `tri-meta` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-orchestrate-p1-section` | replace_text | `tri-orchestrate` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-plan-p1-section` | replace_text | `tri-plan` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-prototype-p1-section` | replace_text | `tri-prototype` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-req-audit-p1-section` | replace_text | `tri-req-audit` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-review-p1-section` | replace_text | `tri-review` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-sdlc-p1-section` | replace_text | `tri-sdlc` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-true-p1-section` | replace_text | `tri-true` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-verify-p1-section` | replace_text | `tri-verify` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-workflow-p1-section` | replace_text | `tri-workflow` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-charter-p1-section` | replace_text | `tri-charter` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-cr-p1-section` | replace_text | `tri-cr` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-devenv-p1-section` | replace_text | `tri-devenv` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-impl-p1-section` | replace_text | `tri-impl` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-ops-p1-section` | replace_text | `tri-ops` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-release-p1-section` | replace_text | `tri-release` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-require-p1-section` | replace_text | `tri-require` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-test-p1-section` | replace_text | `tri-test` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-design-p1-section` | replace_text | `tri-design` 新增「🔴 检查点与红灯清单」章节（dim4 显性 STOP + dim9 红灯聚合；仅聚合既有语义。darwin P1 批） |
| `dw2-tri-cr-contract-fix` | replace_text | `tri-cr` 契约第 1 条修复：`&**：` 损坏行恢复为 `1. **强制前置**：`（模板复制事故；darwin P0 补遗） |
| `dw2-tri-devenv-contract-fix` | replace_text | `tri-devenv` 契约第 1 条修复：`&**：` 损坏行恢复为 `1. **强制前置**：`（模板复制事故；darwin P0 补遗） |
| `dw2-tri-release-contract-fix` | replace_text | `tri-release` 契约第 1 条修复：`&**：` 损坏行恢复为 `1. **强制前置**：`（模板复制事故；darwin P0 补遗） |
| `dw2-tri-action-changelog` | replace_text | `tri-action` CHANGELOG：追加 [1.2.6] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-checklist-changelog` | replace_text | `tri-checklist` CHANGELOG：追加 [1.1.6] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-code-analyzer-changelog` | replace_text | `tri-code-analyzer` CHANGELOG：追加 [1.5.3] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-coding-changelog` | replace_text | `tri-coding` CHANGELOG：追加 [1.8.3] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-domain-changelog` | replace_text | `tri-domain` CHANGELOG：追加 [1.0.2] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-evolve-changelog` | replace_text | `tri-evolve` CHANGELOG：追加 [1.1.8] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-fix-changelog` | replace_text | `tri-fix` CHANGELOG：追加 [1.5.3] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-forge-changelog` | replace_text | `tri-forge` CHANGELOG：追加 [1.0.5] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-frontend-design-changelog` | replace_text | `tri-frontend-design` CHANGELOG：追加 [1.1.6] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-god-changelog` | replace_text | `tri-god` CHANGELOG：追加 [1.2.5] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-grill-changelog` | replace_text | `tri-grill` CHANGELOG：追加 [1.0.2] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-html-changelog` | replace_text | `tri-html` CHANGELOG：追加 [1.3.5] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-init-changelog` | replace_text | `tri-init` CHANGELOG：追加 [1.0.4] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-intent-changelog` | replace_text | `tri-intent` CHANGELOG：追加 [1.14.3] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-loop-changelog` | replace_text | `tri-loop` CHANGELOG：追加 [1.2.6] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-lottie-changelog` | replace_text | `tri-lottie` CHANGELOG：追加 [1.0.5] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-meta-changelog` | replace_text | `tri-meta` CHANGELOG：追加 [1.2.7] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-orchestrate-changelog` | replace_text | `tri-orchestrate` CHANGELOG：追加 [1.0.3] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-plan-changelog` | replace_text | `tri-plan` CHANGELOG：追加 [1.3.4] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-prototype-changelog` | replace_text | `tri-prototype` CHANGELOG：追加 [1.1.3] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-req-audit-changelog` | replace_text | `tri-req-audit` CHANGELOG：追加 [1.1.1] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-review-changelog` | replace_text | `tri-review` CHANGELOG：追加 [1.7.2] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-sdlc-changelog` | replace_text | `tri-sdlc` CHANGELOG：追加 [1.1.7] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-true-changelog` | replace_text | `tri-true` CHANGELOG：追加 [1.1.7] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-verify-changelog` | replace_text | `tri-verify` CHANGELOG：追加 [1.0.1] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-workflow-changelog` | replace_text | `tri-workflow` CHANGELOG：追加 [1.2.7] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-charter-changelog` | replace_text | `tri-charter` CHANGELOG：追加 [1.1.3] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-cr-changelog` | replace_text | `tri-cr` CHANGELOG：追加 [1.1.3] 条目（P1 章节 + 契约修复；P2 属人工内容） |
| `dw2-tri-devenv-changelog` | replace_text | `tri-devenv` CHANGELOG：追加 [1.1.3] 条目（P1 章节 + 契约修复；P2 属人工内容） |
| `dw2-tri-impl-changelog` | replace_text | `tri-impl` CHANGELOG：追加 [1.1.4] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-ops-changelog` | replace_text | `tri-ops` CHANGELOG：追加 [1.1.3] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-release-changelog` | replace_text | `tri-release` CHANGELOG：追加 [1.1.3] 条目（P1 章节 + 契约修复；P2 属人工内容） |
| `dw2-tri-require-changelog` | replace_text | `tri-require` CHANGELOG：追加 [1.1.3] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-test-changelog` | replace_text | `tri-test` CHANGELOG：追加 [1.1.4] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-design-changelog` | replace_text | `tri-design` CHANGELOG：追加 [1.1.4] 条目（P1 章节；P2 属人工内容） |
| `dw2-tri-domain-version` | replace_regex | `tri-domain` 版本线 settle → 1.0.2（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-forge-version` | replace_regex | `tri-forge` 版本线 settle → 1.0.5（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-grill-version` | replace_regex | `tri-grill` 版本线 settle → 1.0.2（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-prototype-version` | replace_regex | `tri-prototype` 版本线 settle → 1.1.3（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-verify-version` | replace_regex | `tri-verify` 版本线 settle → 1.0.1（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-charter-version` | replace_regex | `tri-charter` 版本线 settle → 1.1.3（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-cr-version` | replace_regex | `tri-cr` 版本线 settle → 1.1.3（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-devenv-version` | replace_regex | `tri-devenv` 版本线 settle → 1.1.3（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-ops-version` | replace_regex | `tri-ops` 版本线 settle → 1.1.3（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-release-version` | replace_regex | `tri-release` 版本线 settle → 1.1.3（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw2-tri-require-version` | replace_regex | `tri-require` 版本线 settle → 1.1.3（darwin P1 批；settle 形式，任意旧版收敛） |
| `dw3-ops-contract-fix` | replace_text | `tri-ops` 契约第 1 条修复：`&**：` 损坏行恢复为 `1. **强制前置**：`（P0/P1 批同款清零时因 children 层级漏扫。darwin P2 批） |
| `dw3-plan-dedup` | replace_text | `tri-plan` 去重：删除逐字重复的第二份「处理流程」节（含 7 行表。darwin P2 批） |
| `dw3-meta-fallback3` | replace_text | `tri-meta` 兜底③口径对齐：移除对不存在的「降级模式」的引用，对齐「不支持降级」硬性阻断语义（darwin P2 批） |
| `dw3-grill-workflow` | replace_text | `tri-grill` 处理流程扩写：6 行表 → 含每步输入/产出/闸门的 7 步表（语义仅聚合既有章节。darwin P2 批） |
| `dw3-fix-renumber` | replace_text | `tri-fix` 契约编号修正：第 2 个「8.」→「9.」（双「第8条」冲突。darwin P2 批） |
| `dw3-html-ghost-ref-summary` | replace_text | `tri-html` 幽灵引用清理（summary 行）：§3.13 代码版权合规 → §代码版权与许可证合规（darwin P2 批） |
| `dw3-html-ghost-ref-tree` | replace_text | `tri-html` 幽灵引用清理（目录注释行）：+ §3.13 代码版权 → + §代码版权与许可证合规（darwin P2 批） |
| `dw3-html-ghost-ref-hardline` | replace_text | `tri-html` 幽灵引用清理（硬红线行）：遵循 §3.13 硬红线 → 遵循 §代码版权与许可证合规 硬红线（darwin P2 批） |
| `dw3-html-truncation` | replace_text | `tri-html` 残句补全：「引擎内部纪律」行悬空逗号截断，补全「内层不动」语义（语义源自本节标题与 engine-evolution-notes.md。darwin P2 批） |
| `dw3-children-dirtree` | replace_text | tri-sdlc 子 skill SKILL.md 目录结构节补登 `references/` 与 `scripts/check_update.py`（wildcard ×9；与 f12 README 树对齐。darwin P2 批） |
| `dw3-tri-ops-changelog` | replace_text | `tri-ops` CHANGELOG：追加 [1.1.4] 条目（契约修复 + 目录树。darwin P2 批） |
| `dw3-tri-charter-changelog` | replace_text | `tri-charter` CHANGELOG：追加 [1.1.4] 条目（目录树。darwin P2 批） |
| `dw3-tri-cr-changelog` | replace_text | `tri-cr` CHANGELOG：追加 [1.1.4] 条目（目录树。darwin P2 批） |
| `dw3-tri-devenv-changelog` | replace_text | `tri-devenv` CHANGELOG：追加 [1.1.4] 条目（目录树。darwin P2 批） |
| `dw3-tri-release-changelog` | replace_text | `tri-release` CHANGELOG：追加 [1.1.4] 条目（目录树。darwin P2 批） |
| `dw3-tri-require-changelog` | replace_text | `tri-require` CHANGELOG：追加 [1.1.4] 条目（目录树。darwin P2 批） |
| `dw3-tri-design-changelog` | replace_text | `tri-design` CHANGELOG：追加 [1.1.5] 条目（目录树。darwin P2 批） |
| `dw3-tri-impl-changelog` | replace_text | `tri-impl` CHANGELOG：追加 [1.1.5] 条目（目录树。darwin P2 批） |
| `dw3-tri-test-changelog` | replace_text | `tri-test` CHANGELOG：追加 [1.1.5] 条目（目录树。darwin P2 批） |
| `dw3-tri-grill-changelog` | replace_text | `tri-grill` CHANGELOG：追加 [1.0.3] 条目（工作流扩写。darwin P2 批） |
| `dw3-tri-plan-changelog` | replace_text | `tri-plan` CHANGELOG：追加 [1.3.5] 条目（去重。darwin P2 批） |
| `dw3-tri-meta-changelog` | replace_text | `tri-meta` CHANGELOG：追加 [1.2.8] 条目（兜底③对齐。darwin P2 批） |
| `dw3-tri-fix-changelog` | replace_text | `tri-fix` CHANGELOG：追加 [1.5.4] 条目（编号修正。darwin P2 批） |
| `dw3-tri-html-changelog` | replace_text | `tri-html` CHANGELOG：追加 [1.3.6] 条目（幽灵引用 + 残句补全。darwin P2 批） |
| `dw4-meta-m05-trigger` | replace_text | `tri-meta` M05 声明收敛（触发时机）：整句重复 → 短指针（darwin 后续批） |
| `dw4-meta-m05-table` | replace_text | `tri-meta` M05 声明收敛（响应策略表）：整句重复 → 短指针（darwin 后续批） |
| `dw4-meta-m05-disk` | replace_text | `tri-meta` M05 声明收敛（落盘规则）：整句重复 → 短指针（darwin 后续批） |
| `dw4-meta-reroute` | replace_text | `tri-meta` 重路由映射精确化：4 行悬空措辞 → 显式处置语义（darwin 后续批） |
| `dw4-meta-changelog` | replace_text | `tri-meta` CHANGELOG：追加 [1.2.9] 条目（darwin 后续批） |
| `dw5-tri-charter-fallback` | replace_text | `tri-charter` 新增兜底章节（#14 children 补齐；⑤ 立项材料不可判定。dw5 批） |
| `dw5-tri-cr-fallback` | replace_text | `tri-cr` 新增兜底章节（⑤ 静态检查工具不可用→手工替代。dw5 批） |
| `dw5-tri-design-fallback` | replace_text | `tri-design` 新增兜底章节（⑤ Must 不可落点→退回门②。dw5 批） |
| `dw5-tri-devenv-fallback` | replace_text | `tri-devenv` 新增兜底章节（⑤ 环境不可搭建→登记阻塞。dw5 批） |
| `dw5-tri-impl-fallback` | replace_text | `tri-impl` 新增兜底章节（⑤ 任务阻塞→不跳任务。dw5 批） |
| `dw5-tri-ops-fallback` | replace_text | `tri-ops` 新增兜底章节（⑤ 指标无法采集→手工巡检替代。dw5 批） |
| `dw5-tri-release-fallback` | replace_text | `tri-release` 新增兜底章节（⑤ 无预发布环境→本地等价冒烟。dw5 批） |
| `dw5-tri-require-fallback` | replace_text | `tri-require` 新增兜底章节（⑤ AC 不可判定→升级人审。dw5 批） |
| `dw5-tri-test-fallback` | replace_text | `tri-test` 新增兜底章节（⑤ 环境不可用→最小核心链路验证子集。dw5 批） |
| `dw5-release-contract-degrade` | replace_text | `tri-release` 契约第 5 条补降级指针（**须排在 release-fallback 之前**——其 marker 会被兜底⑤行注入；dw5 批） |
| `dw5-release-dim4-degrade` | replace_text | `tri-release` 维度 4 补「无预发布环境」降级行（对齐维度 3 无 CI 先例；dw5 批） |
| `dw5-tri-charter-changelog` | replace_text | `tri-charter` CHANGELOG：追加 [1.1.5] 条目（dw5 批） |
| `dw5-tri-cr-changelog` | replace_text | `tri-cr` CHANGELOG：追加 [1.1.5] 条目（dw5 批） |
| `dw5-tri-design-changelog` | replace_text | `tri-design` CHANGELOG：追加 [1.1.6] 条目（dw5 批） |
| `dw5-tri-devenv-changelog` | replace_text | `tri-devenv` CHANGELOG：追加 [1.1.5] 条目（dw5 批） |
| `dw5-tri-impl-changelog` | replace_text | `tri-impl` CHANGELOG：追加 [1.1.6] 条目（dw5 批） |
| `dw5-tri-ops-changelog` | replace_text | `tri-ops` CHANGELOG：追加 [1.1.5] 条目（dw5 批） |
| `dw5-tri-release-changelog` | replace_text | `tri-release` CHANGELOG：追加 [1.1.5] 条目（dw5 批） |
| `dw5-tri-require-changelog` | replace_text | `tri-require` CHANGELOG：追加 [1.1.5] 条目（dw5 批） |
| `dw5-tri-test-changelog` | replace_text | `tri-test` CHANGELOG：追加 [1.1.6] 条目（dw5 批） |
| `dw6-grill-selfcheck-entity` | replace_text | `tri-grill` 自检声明 `&lt;路径&gt;` HTML 实体恢复原生尖括号（复评微批） |
| `dw6-grill-output-row` | replace_text | `tri-grill` 质询产出表：路径定源 `<项目根>/reports/<文档stem>-grill.md` + 挂接 `templates/grill-report.md`（复评微批） |
| `dw6-grill-flow-row` | replace_text | `tri-grill` 处理流程步骤 2 质询记录路径口径统一（复评微批） |
| `dw6-grill-deliver-row` | replace_text | `tri-grill` 交付产物表路径口径统一（复评微批） |
| `dw6-grill-diskrule` | replace_text | `tri-grill` 落盘规则路径定源 + 格式模板指针（复评微批） |
| `dw6-grill-fallback-stop` | replace_text | `tri-grill` 兜底表补「用户在 🔴 STOP 拒绝确认 / 中止」分支（复评微批） |
| `dw6-grill-role-note` | replace_text | `tri-grill` 输入契约表下补角色侧重注（复评微批） |
| `dw6-grill-changelog` | replace_text | `tri-grill` CHANGELOG：追加 [1.0.4] 条目（复评微批） |
| `dw6-html-gate2-scope` | replace_text | `tri-html` 契约门②「截图预览描述」→「图表清单与文件大小」（与流程图口径一致；复评微批） |
| `dw6-html-modec-dedup` | replace_text | `tri-html` 模式 C 降级声明去重（与表 C 行逐字重复且无 §出处，非有意聚合；复评微批） |
| `dw6-html-copy-relnote` | replace_text | `tri-html` 交付副本 MUST 含主报告 + 全部 viewer 成品（保相对链接可达；复评微批） |
| `dw6-html-diskrule-fix` | replace_text | `tri-html` 落盘规则矛盾修复（统一为默认 `.tribro/html/<命名>/` + 用户指定时双写；复评微批） |
| `dw6-html-tri-true-ref` | replace_text | `tri-html` 质量标准「原 tri-true 兜底机制」悬空引用 → §兜底处理 ②（复评微批） |
| `dw6-html-changelog` | replace_text | `tri-html` CHANGELOG：追加 [1.3.7] 条目（复评微批） |

## 每项补丁的依据

### spec-per-skill + f2-pointer（真源形态）

**事实**：
- 上游 29 个顶层 SKILL.md 有 22 个指向 `tri-forge/references/version-check-spec.md`（**断链**），
  另 7 个用相对路径 `references/version-check-spec.md`（可用）
- `tri-forge` 在**任何可达源**都不存在（**当时结论，2026-09-23 之前**）：本地磁盘 / git 全历史 /
  原作者 GitHub（与本地同 commit `71e44af`）/ 平台 `/api/v1/skills` 与 `/api/v1/download` 双 404；
  **作者名下 92/92 个 skill 全量枚举，`forge` 零命中**
- 上游自身对真源形态**三向矛盾**：4437B spec 写「不依赖任何外部 skill」（支持自带）；
  `tri-humanize/SKILL.md:219` 写「家族级单一事实源，NEVER 内联/自带 fork」（反对自带）；8 个 skill 实际各带一份

> **后续（2026-09-23）**：本仓库已**自行重建 `tri-forge/`**（见 `.gitignore` 注记与
> `tri-forge/CHANGELOG.md`），其中 `tri-forge/scripts/check_registry.py` 承接上游
> `sync_registry.py` 的五点校验职能。⇒ 上文「不存在」的结论**仅属决策沿革**，不再是现状；
> 后果之一见 §f9：`version-gate.md` §六 曾据此注入「脚本门禁当前缺失」的兜底清单，已更正。

**裁定（用户 2026-09-23）**：**自带为主 + 总纲定位**
- 每个 skill 自带 `references/version-check-spec.md` → 满足家族「支持独立安装」要求
- `tri-intent/references/version-gate.md` 重定位为**家族设计总纲**（设计原则、端点配置真源、
  四处版本同步点、junction 单源例外、P1–P4 阻断定义）
- 两份文件互相注明管辖范围；`scripts/check_update.py` 为**可执行真源**

### payload 的校正内容

`payload/version-check-spec.md` 以上游 4437B 变体为底本（无错字、来自最新一批 skill），
按**与 `scripts/check_update.py` 实际行为的逐条比对**校正：

| 上游 spec 原述 | 实际实现 | 校正 |
|---|---|---|
| `--platform <平台>`，取值 `trae\|workbuddy\|qwen\|codex` | **无此参数** | 删除，改为实际存在的 `--skill-dir` / `--json` / `--dry-run` / `--ttl-min` |
| 退出码 `20` / `21` / `22` 三种 BLOCK | **只有 20**，P2/P3/P4 通过 `block_code` 区分 | 合并为单一的 `20` + `block_code` 说明 |
| 未提 `64` | 存在 `64`（参数/环境错误） | 补充 |
| 缓存文件 `<cache-dir>/.version_cache.json` | `~/.cache/<slug>/update-state.json` | 修正 |
| 「本文件是 **tri-forge 家族** …唯一事实源」 | 家族名不是 tri-forge | 改为「本 skill 自带」+ 总纲指引 |
| 未提端点解析 | 读 `~/.skillhub/metadata.json` 取 origin | 补充第 3、5 条 |
| `--simulate-*` 表把预期退出码与场景错位配对 | 4 类注入参数各自独立 | 改为「参数 / 取值 / 场景」三列，不断言退出码 |

## 关于 `tri-forge` 提及（F4 · 已重估，不再是待办）

> **立论前提已变**：F4 形成时，`tri-forge` 在**任何可达源都不存在**
> （本地磁盘 / git 全历史 / 原作者 GitHub / 平台 92/92 全量枚举均无命中），
> 故当时把对它的引用一律视作「断链残留」。
> **2026-09-23 已在本仓库重建 `tri-forge/`**（见 `.gitignore` 注记与 `tri-forge/CHANGELOG.md`），
> 它现在是本仓库的一等 skill —— 在 `ops/version-lint.py` 与 `ops/versions.json` 覆盖内。
> ⇒ 对 `tri-forge` 的引用**不再是断链**，本节从「待办」降级为「口径备忘」。

实测（2026-09-24，排除 `.workbuddy/`）：**37 个 .md / 99 处**提及 `tri-forge`，按文件归类：

| 类别 | 文件数 | 处理 |
|---|---|---|
| SKILL.md / README.md / `doing/**` 等 | 18 | 正当引用（真源指针、协作关系） |
| `CHANGELOG.md` 历史 | 10 | **不改**（追加型历史） |
| `tri-forge/**` 自身 | 5 | 自指 |
| `tests/*.md` | 2 | 正当引用 |
| `ops/**` | 2 | 机制自述（本文件 + 补丁清单） |

> 早期版本的表格把这 37/99 记作 **19 个 / 42 处**——那是 `tri-forge` 尚未重建、
> 且未计入 spec 副本与 CHANGELOG 时的口径，现已按实测更正。

## 本目录已纳入 git（此前不在，已迁移）

本补丁层原位于 `.workbuddy/patches/` —— 该路径被 `.gitignore:6` 命中，**故当时不进 git**。
**已迁至 `ops/patches/` 并纳入版本控制**（同批迁移理由见 `ops/README.md` §为什么这个目录在 git 里）。

| 场景 | 迁移前（`.workbuddy/patches/`） | 现在（`ops/patches/`） |
|---|---|---|
| `skillhub upgrade` 整树替换 skill 目录 | ✅ 存活 | ✅ 存活 |
| **重新 clone 本仓库** | ❌ **丢失** | ✅ **存活** |
| 他人拉取本 fork | ❌ 拿不到 | ✅ 拿得到 |

⇒ 原先写的「若希望重新 clone 也存活…**待裁决**」**已落地**：对自维护 fork 而言，
补丁层丢失 = 全部本地修正丢失，与 `ops/` 其余工具的取舍一致。


---

## 锚点型注入的幂等陷阱（实测事故，必读）

**事故**：新增「把 SELF_MAINTAINED 常量与函数注入 `check_update.py`」两个 op 时，
第一次重放就把代码**重复注入 43 份 ×3**（事故发生在全量 43 份时期；分支收窄后该 op 覆盖 **24** 份）。

**根因**：这类 op 的 `old` 是**锚点**（插入位置），而 `new = 注入内容 + 锚点` ——
锚点在插入后**依然存在**。原判定逻辑是「`old` 未命中时才看 `already_marker`」，
于是每次重放都再插一遍。

**修复**：`op_replace_text` 改为**先判标记、命中即跳过**：

```python
if marker and marker in txt:
    already += 1
    continue          # ← 标记在，说明结果已存在，绝不再插
n_old = txt.count(old_lf)
...
```

**更重要的教训 —— 幂等必须用「内容指纹」验证，不能只比输出**：

当时的幂等测试比较的是**两次运行的输出文本**，两次输出完全相同，于是判定「✅ 幂等」——
但文件其实在持续增长（1 份 → 2 份 → 3 份）。输出文本相同不代表文件相同。

正确做法：

```python
# 重放前后统计目标特征串的出现次数，必须恒为 1
Counter(p.read_text().count("def self_consistent_check(") for p in files)
# → 应为 {1: 24}；若为 {2: 24}、{3: 24} 即发生重复注入
```

**现已固化为验证方式**：凡新增**锚点型注入** op，重放后必须按内容指纹确认
「每个目标文件恰好含 1 份」。

---

## 自维护模式（`SELF_MAINTAINED`）

本仓库为自维护 fork。两个 `self-maintained-*` op 把这一状态**注入到每个 skill 自带的**
`check_update.py`，使其：

- **完全跳过远端请求**（不再解析 `~/.skillhub/metadata.json`、不请求平台）
- 改为校验**本 skill 自身的 5 处版本声明**是否一致（P1–P5），返回 A（一致）/ D（漂移）
- 排障逃生舱：`TRI_ALLOW_REMOTE=1` 临时恢复远端比对

实现要点（为什么可行）：当前 **24 份** `check_update.py` 实测只有 **2 种形态**
（`tri-code-analyzer` / `tri-lottie` 与其余 22 份），差异**仅在模块 docstring
与两个额外 helper**，`decide()` 主体完全一致 ⇒ 一个字面锚点即可覆盖全部。
锚点选在 `    state = load_state()` **之前**——必须在节流检查之前，
否则旧的远端缓存态会先命中并 early return，自维护校验永不执行。

---

## 版本节收敛为瘦指针 STUB（`converge_version_section`）

### 依据：自维护已落地，但 prompt 层口径没跟上

`self-maintained-*` 两个 op 只改了**脚本**（`check_update.py` 不再请求平台）。
但 SKILL.md **正文**仍是上游同步来的「远端 skillhub 口径」全量版，实测三处直接矛盾：

| 位置 | 上游残留文本 | 实际行为 |
|---|---|---|
| 强制执行契约 §0 | 「MUST 先通过 §版本检查与更新机制（连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级…）」 | 脚本自维护模式下**不发任何请求**；`skillhub upgrade` 在本 fork 无意义 |
| §版本检查与更新机制 | 端点读自 `~/.skillhub/metadata.json`、四态 A/B/C/D 细则、SemVer 逐段比较算法 | 全部被 `SELF_MAINTAINED` 短路，永不执行 |
| 同上（节长） | 35 行 | 家族规范 `references/version-check-spec.md` §六 要求 **≤30 行**且**禁内联**四态/升级流程/比较算法 |

### 判据（为什么是规则化而不是 13 份字面量）

`converge_version_section` 按**语义**收敛，不写字面量：

- `already_marker`（`<!-- version-stub v1`）命中 → 已收敛，跳过
- 节内含 `legacy_markers`（`skillhub upgrade` / `~/.skillhub`）任一 → 收敛为 STUB
- 两者皆无 → **不碰**（已合规的 9 行 STUB，或节内含 skill 专属内容者）
- `{slug}` 占位由目录名填充 ⇒ 新增 / 同步 skill 后自动生效

实测命中（分两阶段）：
- **阶段一**：顶层 **15** 个（14 个含远端标记 + `tri-forge` 经 `force_skills` 强制）
  + `tri-sdlc/children/*` **9** 个 = **24** 个版本节；
- **阶段二（形态统一）**：再经 `force_skills` 补齐剩余 **9** 个顶层节 —— 其中 **6** 个原为
  **违规**形态（内联四态判定 / 退出码语义：`tri-god` 16 行、`tri-prototype` 15、
  `tri-init` 12、`tri-frontend-design` 11、`tri-code-analyzer` 8、`tri-lottie` 4），
  **3** 个已是合规纯指针（`tri-domain` / `tri-grill` / `tri-orchestrate`，各 8 行）；
  统一为同一 STUB。
- **终态**：**33** 个版本节全部为 `version-stub v1`；按 git 归一化口径
  （`.gitattributes` 的 `*.md text eol=lf`，即去掉全部 CR）实测仅 **2 种形态** ——
  **32** 个完全一致（14 行，仅 `{slug}` 不同）+ `tri-forge` **26** 行（保留专属段）。

> ⚠️ **测形态时必须先归一化行尾**：`.gitattributes` 虽已强制 `*.md text eol=lf`，但
> **`core.autocrlf` 实测为 `false`（写在 `.git/config`）**，且部分 `*.md` 的 **blob 仍是 CRLF**
> （如 `tri-intent/SKILL.md`）⇒ 工作区字节可能落成 `\r\r\n`。**该现象不是 autocrlf 造成的**
> ——是检出/写入链在已有 CRLF 之上又补了一个 CR（2026-09-25 实测；归因不确定时以 byte 统计为准）。
> 直接按字节数行会把同一形态误判为多一种（曾因此把 4 个 `\r\r\n` 文件误读为「15 行」）。
> **判据应以 `git hash-object` 与 HEAD blob 比对为准**。

契约 §0 由 `f7-*` 两个 op 覆盖 **23** 处（22 处同文 + `tri-intent` 的变体）。

### `tri-forge` 为什么需要 `preserve`

它的版本节里混有 **skill 专属职能**（`scripts/check_registry.py` 家族级 P1–P5 校验），
一刀切会丢内容。故 `preserve: {"tri-forge": "**家族承接职能"}` —— STUB 之后的专属段原样保留。

### 幂等判据

连续跑两次 `apply.py`，第二次三个 op 均报 `写入 0｜跳过 N`（N = 24 / 9 / 23）。
**不要只比输出文本**（见上文「锚点型注入的幂等陷阱」）——本次判据是「标注为已收敛的文件数」。

### F4 残留（本次刻意不动）

| 类别 | 位置 | 为什么不动 |
|---|---|---|
| 逃生舱文档 | 各 skill `references/version-check-spec.md`（×4 处/份）、`tri-intent/references/version-gate.md` | 远端模式仍由 `TRI_ALLOW_REMOTE=1` 保留，属**正确记载**而非漂移 |
| 补丁层自述 | `ops/README.md`、`ops/patches/README.md`、`payload/version-check-spec.md` | 机制说明 |
| 历史 | 各 skill `CHANGELOG.md` | 追加型历史，**不改写** |
| 上游镜像 | `.workbuddy/_upstream/**` | 在 `exclude_paths` 内，非分发树 |

---

## 引导安装提示回归自维护口径（`replace_regex` + `f8`）

### 缘起：修 9 个 children 时发现的是 66 处

用户批准的原始范围是「`tri-sdlc/children/*` 的 9 个 `SKILL.md` 各有一行
`skillhub install tri-sdlc --dir <目标目录>`」。但**全仓扫描后**同一缺陷类是 **58 文件 / 66 处**：

| 位置类别 | 命中 | 说明 |
|---|---|---|
| 顶层 `SKILL.md` 「模式 B · 引导安装」提示 | 20 | `> 请安装：\`skillhub install tri-intent --dir <目标目录>\`` |
| `children/*/SKILL.md` | 9 | `> 请先安装：\`skillhub install tri-sdlc --dir <目标目录>\`` |
| `README.md` 安装段 | 24 | 含各 skill 自身安装命令 |
| `tri-intent/doing/*.md`（下游路由说明） | 4 | |
| `references/snapshot-contract.md` + `validators/dependency-checker.md` | 3 | 契约与验证器给用户的安装命令 |
| `tests/*.md` 期望输出断言 | 8 | **必须同步改**，否则测试描述的是不可达字符串 |

⇒ 与 `converge_version_section` 同一类问题：**脚本已自维护，但 prompt / 文档层口径没跟上**。
拖到后面做会留下跨文件口径不一致，故一并收敛。

### 为什么新增 op 类型而不是复用 `replace_text`

`replace_text` 是**字面量**匹配，本场景有两个硬需求它满足不了：

1. **slug 不同**：`tri-intent` / `tri-sdlc` / `tri-god` / `<slug>` 各不相同，
   字面量方案需要十余条 op 且新增 skill 后失效；
2. **必须与历史/纠错文本区分**：`CHANGELOG.md` 里
   `\`skillhub install <slug> --upgrade\``（历史 bug 记录）与
   `version-gate.md:110` 的纠错注记，**与主路径提示共享 `skillhub install` 前缀**，
   只有「整行守卫」能分开——误改它们等于篡改历史/删掉正确的实测结论。

故新增 `replace_regex`（与 `replace_text` 共用 `read_norm` / `write_keep`，行尾无关）：

| 字段 | 作用 |
|---|---|
| `pattern` | 正则，逐行 `subn` 全局替换（一行可多处） |
| `replacement` | 替换串 |
| `already_marker` | 命中即整文件判「已应用」（幂等靠**内容指纹**，不靠输出比对） |
| `skip_line_containing` | 命中任一子串的行**整行不动** → 本次用 `--upgrade` 排除历史与纠错注记 |
| `skip_names` | 按文件名整文件跳过 → `CHANGELOG.md` |
| `skip_prefixes` | 按相对路径前缀整文件跳过 → `ops/`（本目录自述，不应被自己的 op 改） |

匹配模式（钉在 `--dir <目标目录>` 形态上，天然避开 `--upgrade`）：

```
skillhub[ \t]+install[ \t]+(?:<[^>]*>|[-A-Za-z0-9_]+)(?:[ \t]+--dir[ \t]+(?:<[^>]*>|[^\s`]+))?
```

⇒ 替换为 `python ops/install-skills.py --target <目标目录>`。
本仓库的安装模型是 **junction 链入整个家族**（`ops/install-skills.py` 无按 slug 选择的能力），
故「请安装 tri-intent」这类单 slug 提示统一改为家族安装器命令，语义上仍满足原意。

### 幂等判据

连续跑两次 `apply.py`，`f8` 第二次必须报 `应用 0｜已应用 60`（58 个被迁移 + 2 个本就含新指引：
根 `README.md`、`tri-init/templates/AGENTS.md`）。首次为 `应用 66｜已应用 2`。

### 本次刻意不动

| 类别 | 位置 | 为什么不动 |
|---|---|---|
| 历史 | 各 `CHANGELOG.md` 的 `skillhub install <slug> --upgrade` | 追加型历史 |
| 纠错注记 | `tri-intent/references/version-gate.md:110` | 记载「`install --upgrade` 不存在」的正确结论 |
| 机制自述 | `ops/**`（`skip_prefixes` 排除） | 本目录的说明文本 |
| 历史快照 | `tri-mece-audit/tri-mece-audit.html` | `.html` 不在 glob 内；38 处版本引用属 46-skill 时代快照，且不在 `version-lint` D1–D4 覆盖范围 |

---

## §六 门禁叙述回归现状（`f9` · 一并修正 `f6` 的注入源）

### 缘起：`f6` 注入的兜底文案随 `tri-forge` 重建而失真

`f6-gate-fill-empty-block` 当年在填补上游清空的代码块时，注入了这样一段兜底说明：

> ⚠️ **脚本门禁当前缺失**：原本由 `tri-forge/scripts/sync_registry.py` 提供，但 `tri-forge`
> 未随任何可达源分发……在本仓库自行实现等效校验器之前，按下列清单逐条手工核对

**但 2026-09-23 本仓库已重建 `tri-forge/`**，其中 `tri-forge/scripts/check_registry.py`
就是那道门禁（P1–P5，`--check` / `--apply`）。⇒ 该段「缺失 + 只能手工」的叙述**与现状相反**，
且它已由 `f6` **写进了 skill 文件** `tri-intent/references/version-gate.md`。
按铁律，修正必须走补丁层，不能直接改文件。

### 两步处置

| 步 | op | 作用 |
|---|---|---|
| 1 | `f9-gate-script-rebuilt` | 把**已注入**的失真段替换为现状叙述（`old` = 旧 ⚠️ 段，`new` = 新 ✅ 段） |
| 2 | `f6-gate-fill-empty-block`（改 `new` + `already_marker`） | 让**未来上游同步**在填补空块时**直接写入正确文本**，不再需要 f9 二次纠正 |

新叙述同时给出两条真实路径（都保留手工清单作最后兜底）：
- **家族侧**：`python tri-forge/scripts/check_registry.py --check`
- **单 skill 独立安装侧**：该 skill 自带的 `scripts/check_update.py`（自维护模式下已内置 P1–P5 自洽校验）

### 幂等判据

`f6` 在**首次运行**会报 `not_found`——因为当前树既无上游空块（`old`）、也无新标记
（`already_marker` 已改为 `脚本门禁已就位`）。这是**一次性**的：`f9` 随后完成替换，
第二次起 `f6` 报 `已应用 1`。判据 = 连跑三次，`f6` / `f9` 均稳定在 `应用 0｜已应用 1`。

---

## `f3-*` 三个 op 为何**常驻** `not_found`（正常态，非缺陷）

`apply.py` 汇总里有三行长期显示 ⬜ `应用 0｜已应用 0`，易被误读为「3 个 op 坏了」：

```
| `f3-clause-inline` | 移除发布前校验子句（行内分号引出版） | ⬜ 应用 0｜已应用 0 |
| `f3-clause-sentence` | 移除发布前校验子句（句号引出版） | ⬜ 应用 0｜已应用 0 |
| `f3-standalone-line` | 移除发布前校验独立行 | ⬜ 应用 0｜已应用 0 |
```

**这是预期终态**，原因是两层叠加：

1. **目标文本已不存在于活跃树**。三者移除的都是 `；发布前 MUST 通过 \`python
   tri-forge/scripts/sync_registry.py --check\`。` 家族子句；该子句在 F3 轮批量清除，
   此后 §六 版本节又统一收敛为瘦指针 STUB（`converge-version-stub`），更不会重新出现。
2. **残余出现处全部落在补丁层作用域之外**。实测全仓仍含该字面串的文件只有三类：
   - `.workbuddy/memory/*.md`、`.workbuddy/proposals/*.md` —— 历史日志与提案；
   - `.workbuddy/_upstream/**/SKILL.md` —— 上游快照（只读参照）。

   而 `manifest.json` 顶层 `exclude_paths = [".workbuddy", ".git"]` 把整个 `.workbuddy/`
   排除在外 ⇒ 即使 op 的 `glob` 写的是 `**/*.md`，也扫不到这些文件。
   （另一处历史残留 `tri-article/CHANGELOG.md` 不在本分支——本分支为编程专线 24 skill。）

**为何保留而不删除**：op 是「上游整树替换后不丢修正」的可重放账本，属**追加型历史**。
若上游某次同步把旧子句带回来，这三个 op 会立即从 `not_found` 变为 `应用 N` 生效；
删掉它们等于放弃该防御。故保留，仅在此说明其 ⬜ 为正常态。

**判据**（可复验）：`grep -rn '发布前 MUST 通过' --include='*.md' .` 的命中应**全部**位于
`.workbuddy/` 之下；`manifest.json` 的 `exclude_paths` 含 `.workbuddy`。两者同时成立即正常。

---

## `sync_script` 新 op 类型与「children 对等化」（`f10`–`f12` · 2026-09-25）

### 为什么必须新增 op

铁律要求：对 skill 文件的任何修正 MUST 落成 op。而 `tri-sdlc` 的 9 个子 skill
（`tri-sdlc/children/*`）此前**不带 `scripts/`**，其版本节 STUB 却写着
`python scripts/check_update.py --slug <child> --json` ⇒ **悬空引用**：

- child **独立安装**（junction 到 child 目录）时，该相对路径不存在；
- 即便 cwd 落在 `tri-sdlc/` 根使路径成立，`--skill-dir` 默认 = 脚本上级目录 = `tri-sdlc`，
  与 `--slug <child>` **校验对象错位**。

顶层 24 个 skill 的 `scripts/check_update.py` 是 **24/24 齐备**，故正确修法是给 child **补件**，
而不是把命令改成「指父脚本」——后者违反 `references/version-check-spec.md` 明写的
「每个 tri-* skill 各带一份…以保证单个 skill 可独立安装、不依赖其他 skill 的文件」。

### op 定义

```json
{
  "id": "f10-children-check-update",
  "type": "sync_script",
  "glob": "tri-sdlc/children/*/SKILL.md",   // 命中即取其父目录为目标 skill 目录
  "payload": "assets/check_update.py",      // 源文件，相对 ops/patches/
  "dest": "scripts/check_update.py"         // 目标 skill 目录下的落点
}
```

实现与 `sync_spec` 同法：**归一化文本（LF）比对 + 字节写入**，一致即跳过；目标不存在时
创建父目录并新增。故连跑两次为 `写入 9｜跳过 0` → `写入 0｜跳过 9`。

### 源形态取「去耦版」，不是 22 份主形态

24 份脚本有两种形态，差异在 `DEFAULT_SLUG`（`"tri-intent"` vs `None`）、
`CACHE_DIR`（`~/.cache/tri-intent` vs `~/.cache/tri-skills`）与若干注释文案。
给 child 部署时取 `DEFAULT_SLUG = None` 的去耦版——**child 的默认 slug 不可能是 `tri-intent`**，
硬编码默认值对它是错的。

### 后续（`f13` · 同日）：顶层 22 份主形态一并统一去耦

主形态与去耦形态的 40 行差异中，功能性仅 3 处：`DEFAULT_SLUG="tri-intent"` → `None`
（去耦版**新增** slug 空值 BLOCK 防御）、`CACHE_DIR` 模块级默认值（实测 `decide()` 总会
按 slug 重设为 `~/.cache/<slug>` ⇒ 默认值从不生效，无行为差异）、User-Agent 串
（自维护模式不发网络，仅远端逃生舱用）。其余全是注释/docstring 文案。

**行为等价双证明后才覆盖**：
- 正向：同一 skill（tri-action）分别用两形态跑 `--json`，归一 `skill_dir` 后 **JSON 全等**、均 exit 0 / `state=A`
- 负向（mutation）：复制 tri-god 注入 P5 漂移（badge `1.2.3→1.2.4`），两形态各校验同一副本，
  **均 EXIT=12 / `state=D` / 归一后 JSON 全等**

据此新增 `f13`（`sync_script`，`glob: tri-*/SKILL.md`）：顶层 24 份统一覆盖为 payload 去耦版，
实测 `写入 22｜跳过 2`（跳过的即内容已一致的 `tri-code-analyzer` / `tri-lottie`）。
**终态：33 份 skill 副本 + 1 份 payload = 34 份 hash 全等**（`98315f6c…`），
全仓 `check_update.py` 仅存 1 种形态。

### 同一轮补齐的三处

| # | 现象 | op | 判据 |
|---|---|---|---|
| 1 | child 无 `scripts/`，STUB 命令悬空 | `f10` | 9 份 hash 全等且 = payload |
| 2 | child 内容于 `b80cfa9` 名义变更但版本未升（P2 首条仍停在 2026-08-05） | 运维直接 bump 到 `1.1.2` + `f11` 同步 tests 描述 | `version-lint` 报 `1.1.2` 且 P1==P2 |
| 3 | child README 目录树漏列实际存在的 `references/` | `f12` | 树中同时含 `references/` 与 `scripts/` |

### 幂等判据

`f10`：`写入 9｜跳过 0` → `写入 0｜跳过 9`；`f11` / `f12`：各
`应用 9｜已应用 0` → `应用 0｜已应用 9`。即第二次重放**零写入**。
`f10` 的源文件入库于 `ops/patches/assets/check_update.py`。

### 配套：两个校验器的覆盖范围同步扩展

`ops/version-lint.py` 与 `tri-forge/scripts/check_registry.py` 原先都用
`REPO.glob("tri-*")` 发现 skill，而 children 位于 `tri-sdlc/children/` ⇒ **9 个子 skill
从未被任何版本校验覆盖**（这是上述三处欠账长期未被发现的根因）。
两者现均已追加 `REPO.glob("tri-sdlc/children/*")`，覆盖数由 **24 → 33**。

## 计数增量（2026-09-25）

新增内部工具型 skill **`tri-req-audit`** 后：顶层 **24 → 25**、补丁层 op **28 → 30**（新增 `f18`/`f19`）、
校验覆盖 **33 → 34**、`check_update.py` **34 → 35 份**（34 skill + 1 payload，hash 仍全等）。

| 受影响位置 | 处置 |
|---|---|
| 「当前补丁清单」表 `spec-per-skill` / `converge-version-stub` / `f13` 三行 | ✅ 已改为当前值 |
| 「当前补丁清单」表新增 `f18` / `f19` 两行 | ✅ 已补 |
| §锚点型注入事故（`43 份 ×3`、`覆盖 24 份`）、§自维护模式（`当前 24 份`/`2 种形态`）、 |
| §源形态取「去耦版」（`24 份脚本有两种形态`）、§后续 f13（`顶层 24 份`/`终态 33+1=34`） | ⬜ **冻结** —— 均为当时实测快照，改写即伪造 |

> 冻结段落的现状读数：`check_update.py` **34 份 skill 副本 + 1 payload**、**仅 1 种形态**（`f13` 后全等）。

### 计数增量（2026-09-25 · 第二轮）

修复 `compliance_check.py` 角色识别盲区后：补丁层 op **30 → 31**（新增 `f20-role-detection`）。
skill 数、校验覆盖、`check_update.py` 份数**均无变化**（本 op 只改脚本，不动 skill 集合）。

| 受影响位置 | 处置 |
|---|---|
| 「当前补丁清单」表新增 `f20` 一行 | ✅ 已补 |
| 本文件 §「实测踩过的坑」标题 `三个坑` → `五个坑`，新增坑 4 / 坑 5 | ✅ 已补 |
| `ops/README.md` 目录树 `当前 30 个 op`、§计数对账表 `补丁层 op 数` 行 | ✅ 已改当前值 |
| 根 `README.md` 目录树 `30 个 op` | ✅ 已改当前值 |
| §计数增量（2026-09-25，第一轮）`op 28 → 30` | ⬜ **冻结** —— 当时实测快照 |
| `reports/tri-req-audit-remediation.md`（`op 28 → 30` ×2、`补丁层 op 数 23 → 30`） | ⬜ **冻结** —— 带日期的整改报告，改写即伪造结论 |

### 计数增量（2026-09-25 · 第三轮）

`tri-frontend-design` **路由自述更正**（口径修正，无行为变更）后：补丁层 op **31 → 36**
（新增 `f21`–`f25`）。skill 数 / 校验覆盖 / `check_update.py` 份数**均不变**。

| 受影响位置 | 处置 |
|---|---|
| 「当前补丁清单」表新增 `f21`–`f25` 五行 | ✅ 已补 |
| `ops/README.md` 目录树 `当前 31 个 op`、§计数对账表 `补丁层 op 数` 行 | ✅ 已改当前值 |
| 根 `README.md` 目录树 `31 个 op` | ✅ 已改当前值 |
| `WORKFLOW-GUIDE.html`（D1 chip L194）与根 `README.md`（D4 表行）的该 skill 版本 | ✅ 已由 `version-lint.py --apply-docs` 幂等修正为 **1.1.4** |
| `ops/versions.json` 中该 skill | ✅ 已由 `--emit-baseline` 刷新为 **1.1.4** |
| 前两轮增量小节 | ⬜ **冻结** —— 当时实测快照 |

> ⚠️ **新增版本线 op 时必须考虑顺序**：`f24`（P1）**插在 `sync-version-meta` / `sync-readme-version` 之前**。
> 若追加到末尾，该 op 会先用**旧版本**写 `_meta.json`，要等第二轮才被纠正
> ⇒ 判据「连跑两次，第二次 `写入 0`」当场失败。**`manifest.json` 的 op 顺序即执行顺序。**
> 实测回执：本轮首跑 `f24 = 应用 1` 且 `sync-version-meta = 写入 1`（同轮跟随 ✅），
> 二/三跑均 `应用 0｜已应用 1` 与 `写入 0｜跳过 25`。

### 计数增量（2026-09-25 · 第四轮）

新增横向验证型 skill **`tri-verify`**（运行中应用的功能验证）后：顶层 **25 → 26**、补丁层 op **36 → 45**
（新增 `f26`–`f34`）、校验覆盖 **34 → 35**、`version-check-spec.md` **34 → 35 份**、
`check_update.py` **35 → 36 份**（35 skill + 1 payload，hash 仍全等）、`ops/versions.json` **34 → 35**。

| 受影响位置 | 处置 |
|---|---|
| 「当前补丁清单」表新增 `f26`–`f34` 九行 | ✅ 已补 |
| 「当前补丁清单」表 `spec-per-skill` / `converge-version-stub` / `f13` 三行 | ✅ 已改为当前值（35 / 26 / 26） |
| `ops/README.md` 目录树 `当前 36 个 op`、§计数对账表 `补丁层 op 数` 行 | ✅ 已改当前值（45） |
| 根 `README.md` 目录树 `36 个 op`、技能目录标题、`versions.json` 行 | ✅ 已改当前值 |
| `WORKFLOW-GUIDE.html` §04「第零步」正文（`34 个 skill（顶层 25 + 9）`） | ✅ 已改当前值 |
| `ops/version-lint.py` 内 `# 顶层 25 个 tri-*` 注释；`manifest.json` 的 `converge-version-stub` / `f13` 两条 label | ✅ 已改当前值 |
| §计数增量（2026-09-25，第一至三轮）与全部冻结段落 | ⬜ **冻结** —— 当时实测快照 |

> **幂等复核**：本轮 `apply.py` 连跑两次，第二次全表为 `应用 0｜已应用 N` / `写入 0｜跳过 N`，
> 无任何 `应用 N>0` 或 `写入 N>0`；`f3-clause-*` 三行仍常驻 `not_found`（目标子句已清，属正常态，
> 见 §`f3-*` 三个 op 为何常驻 `not_found`）。`version-lint.py` 退出码 0（存在漂移 0 个）。

---

## 计数增量（2026-09-25 · 第五轮 · `tri-req-audit` 对抗层硬化）

本轮新增 **22** 个 op（详见 §当前补丁清单末 22 行），补丁层 op 数 **45 → 76**。

| 计数 | 原值 | 现值 | 佐证 |
|---|---|---|---|
| 补丁层 op 数（`manifest.json`） | 45 | **76** | 本轮 22 + 并发会话 9（`f60`–`f68`） |
| §当前补丁清单 数据行数 | 46 | **68** | 本轮补 22 行；68 行 = manifest 中 **67** 个 op + 1 行划除行（`f5-humanize-wording`，已移除） |
| skill 集合 / 版本覆盖 | — | **不变** | 本轮纯改既有 skill 内容 |

| 受影响位置 | 处置 |
|---|---|
| §当前补丁清单：`f34` 行后补入本轮 22 行 | ✅ |
| §实测踩过的**五个**坑 → **六个**坑（新增坑 6） | ✅ |
| `ops/README.md` 目录树 `当前 45 个 op`、§计数对账表 `补丁层 op 数` 行 | ✅ 已改当前值（76） |
| 前四轮增量小节与全部冻结段落 | ⬜ **冻结** —— 当时实测快照 |

### 本轮的 op 顺序约束（两条，顺序即执行顺序）

1. **版本线插序**：`f43-req-audit-version-1-1-0` 改 P1（`SKILL.md` frontmatter），
   **MUST 排在 `sync-version-meta` / `sync-readme-version` 之前**；否则首轮用**旧值**写 `_meta.json`，
   第二轮才纠正 ⇒ 幂等判据当场失败。
2. **改名插序（更隐蔽）**：`f46a` / `f46b` / `f47a` 把「八维 / D1–D8」改成「九维 / D1–D9」，
   **MUST 排在内容 op（`f35`–`f42b`）之前**。因为内容 op 会往 `SKILL.md` 新插入 `D1–D9` 字样，
   若改名 op 在其后，`already_marker` 会命中而**整文件跳过** ⇒ 同一份文件里「九维」与「D1–D8」并存。

> ⚠️ **并发来源说明**：本轮执行期间，另有会话向 `manifest.json` 追加 **9** 个 op
> （`f60-action-fallback` … `f68-workflow-fallback`，涉 9 个 skill 的 fallback 分支）。
> 为免双方重复追加，本表**不代填**其行；其清单行由该会话补记。
> 故 `manifest.json` 实测 **76** 个 op，而本表当前 **68** 行，差额 **8** = 上述并发 op 9 个
> − 表内 1 行划除行（`f5-humanize-wording` 不在 manifest 中）。对账判据：
> `manifest ids − 表内 ids` 应恰为那 9 个 `f6x-*-fallback`。

> **幂等复核**：连跑两次 `apply.py`，第二次全表 `应用 0｜已应用 N` / `写入 0｜跳过 N`；
> 常驻 `not_found` 仅 `f3-clause-inline` / `f3-clause-sentence` / `f3-standalone-line` 三行
> （目标子句已清，属正常态，见前文）。`ops/version-lint.py` 退出码 0。


## 计数增量（2026-09-25 · 第六轮 · 门④ #14 判据硬化 + 版本纪律成文 + 回溯补版）

### 本轮三件事

1. **门④ 第 14 条判据硬化**（`f69-14-structural`）：由「正文出现 `兜底` + `NEVER`」的**存在性代理**，
   改为**结构判定** —— 须存在专门的 `##` / `### 兜底处理` 章节且该章节含 `NEVER`。五类关键词的命中数
   写入回执作为**建议项**（非硬门槛，避免误伤以「场景兜底表」呈现的既有章节：`tri-grill` 命中 0/5 仍合规）。
2. **9 个缺口 skill 补章**（`f70`–`f78`）：`tri-code-analyzer` / `tri-coding` / `tri-frontend-design` /
   `tri-god` / `tri-html` / `tri-intent` / `tri-plan` / `tri-review` / `tri-true` 各补一节定制「兜底处理」。
   各按其触发源与既有机制填五类异常（如 `tri-intent` 明写「不以 hook 为触发源，缺 hook 时照常执行并登记
   「未做 hook 校验」」；`tri-true` 显式区分「执行环境层兜底」与既有的「结论层 §兜底机制」）。
3. **版本纪律成文 + 回溯补版**（`f79` + `f80`–`f115`）：`family-spec` §六 新增步骤 6（MUST：`SKILL.md`
   正文增改章节 ⇒ 至少 PATCH 升版 + CHANGELOG 条目）；18 个 skill（本轮 9 + 上轮 9）各升 PATCH 并补 CHANGELOG。

### 版本线 op 改用 settle 形式（本轮新约定）

**缺陷实证**：`f24`（`tri-frontend-design` 1.1.3 → 1.1.4，`replace_text`，`already_marker = "version: 1.1.4"`）
在本轮 `f91`（1.1.4 → 1.1.5）生效后，`old`（1.1.3）与 marker（1.1.4）**双双不在树上** ⇒ 永久 `not_found`。
根因：版本线 op 是**就地破坏型**（后序 op 覆盖同一行 ⇒ 销毁前序 op 的 `old`），与 CHANGELOG op 的
**前置插入型**（`old` 保留在下方）不同。

**新约定**：版本线 op 一律用 `replace_regex` —— `pattern = ^version: \d+\.\d+\.\d+$`、
`replacement = version: <目标>`、`already_marker = version: <目标>`。**任意旧版本收敛至目标**（settle），
目标**就地更新**、**NEVER 追加链式 op**。本轮已把 `f16` / `f43` 与 `f80`–`f97` 共 **20** 个 op 转为该形式。

### 计数（本轮）

| 项 | 原值 | 现值 | 依据 |
|---|---|---|---|
| 补丁层 op 数（`manifest.json`） | 76 | **122** | 本轮 +47（判据 1 + 补章 9 + 规则 1 + 版本线 18 + CHANGELOG 18）− 退役 1（`f24`） |
| 顶层 skill 数 | 26 | **26** | 不变 |
| 校验覆盖（顶层 + `children`） | 35 | **35** | 不变 |
| §当前补丁清单 数据行数 | 68 | **124** | +9（`f60`–`f68` 补记）+47（本轮）= 124 行 = manifest **122** + 划除行 **2**（`f5-humanize-wording` / `f24-fed-version-1-1-4`） |

> 回执：`apply.py` 二次跑**零真写入 / 零真应用**；`version-lint` 退出 0（漂移 0）；
> `compliance_check --all` = 审计 **26** · **FAIL 0**。本轮由**单会话**完成，无并发写入。

### 计数（2026-09-25 · darwin-skill P0 批增量）

> darwin-skill 全仓基线评估（35 skill）后的 P0 硬伤修复批。上节「计数（本轮）」为第六轮时点表，**冻结**。

| 项 | 原值 | 现值 | 依据 |
|---|---|---|---|
| 补丁层 op 数（`manifest.json`） | 122 | **139** | +17（`dw-*`：契约修复 4 + 去重 2 + 目录纠偏 1 + 版本线 4 + CHANGELOG 6）。`f86`/`f97` settle 目标**就地更新**（1.2.5→1.2.6 / 1.1.5→1.1.6，不占新行）；曾误追加 2 个重复版本 op（与 `f86`/`f97` 同 glob 同 pattern），按「settle 目标就地更新、NEVER 链式追加」约定删除 |
| §当前补丁清单 数据行数 | 124 | **141** | +17；对账恒等式：141 − 划除 2 = manifest **139** ✅ |

回执：`apply.py` 连跑两次**零真写入 / 零真应用**（`dw-*` 与 `f86`/`f97` 均 `应用 0｜已应用 1`）；
`version-lint` 包内漂移 0、`--apply-docs` 修文档层 6 处（WORKFLOW-GUIDE D1 ×3 + README D4 ×3）后 EXIT=0。
涉及 skill：`tri-true` 1.1.6 / `tri-orchestrate` 1.0.2 / `tri-meta` 1.2.6 / `tri-design`·`tri-impl`·`tri-test` 1.1.3。

### 计数（2026-09-26 · darwin-skill P1 批增量）

> 上两节计数表为时点快照，**冻结**。本批 = P1 章节（dim4 显性 STOP 检查点 + dim9 红灯清单聚合，35 skill）+ P0 补遗（tri-cr / tri-devenv / tri-release 契约第 1 条 `&**：` 损坏修复）。

| 项 | 原值 | 现值 | 依据 |
|---|---|---|---|
| 补丁层 op 数（`manifest.json`） | 139 | **223** | +84（`dw2-*`：章节 35 + 契约修复 3 + CHANGELOG 35 + settle 新增 11）；既有 24 个 settle op 目标**就地更新**（不占新行） |
| §当前补丁清单 数据行数 | 141 | **225** | +84；对账恒等式：225 − 划除 2 = manifest **223** ✅ |

回执：`apply.py` 第二次跑零真写入/零真应用（`dw2-*` 全部 `应用 0｜已应用 1`）；
`version-lint` 包内漂移 0、`--apply-docs` 修文档层 74 处后 EXIT=0。
全部 35 skill 升 PATCH（章节级新增，family-spec §六 步骤 6）。

### 计数（2026-09-26 · darwin-skill P2 批增量）

> 上两节计数为时点快照，**冻结**。本批 = 结构性重写类 7 项
> （proposal `reports/proposal-darwin-p2-20260926.md`，Approved: yes 2026-09-26；
> paired 评审 3 judge 全 better 15/15，含可回溯性核验）。

| 项 | 原值 | 现值 | 依据 |
|---|---|---|---|
| 补丁层 op 数（`manifest.json`） | 223 | **247** | +24（`dw3-*`：内容修复 9 + children 目录树 wildcard 1 + CHANGELOG 14）；**14 个既有 settle op 目标就地更新**（不占新行：ops/charter/cr/devenv/release/require→1.1.4，design/impl/test→1.1.5，grill→1.0.3，plan→1.3.5，meta→1.2.8，fix→1.5.4，html→1.3.6） |
| §当前补丁清单 数据行数 | 225 | **249** | +24；对账恒等式：249 − 划除 2 = manifest **247** ✅ |

回执：`apply.py` 连跑幂等（`dw3-*` 全部 `应用 0｜已应用 N`）；`version-lint --apply-docs` EXIT=0。
14 skill PATCH 升版（fix/meta/html/plan/grill 为结构性修复；children 9 份为目录结构节补登，d6 失真消除）。
四处计数中 skill 总数（26/35/35/36）不变——本批无新增 skill。
曾发现的机械替换残留（`§3.13 代码版权(合规)` 整替换产生重复短语）已按「未 commit 范式」就地拆分修正：
ghost regex op 拆为 3 个上下文精确的 replace_text op（-1/+3），回滚 `tri-html/SKILL.md` 后重放。

### 计数（2026-09-26 · tri-meta 重写批增量）

> 上节计数为时点快照，**冻结**。本批 = proposal `reports/proposal-tri-meta-rewrite-20260926.md`（Approved: yes 2026-09-26）；
> paired 评审 3 judge 全 better（2 clear + 1 slight）。

| 项 | 原值 | 现值 | 依据 |
|---|---|---|---|
| 补丁层 op 数（`manifest.json`） | 247 | **252** | +5（`dw4-*`：M05 收敛 3 + 重路由精确化 1 + CHANGELOG 1）；settle 就地更新 1.2.8→1.2.9（不占新行） |
| §当前补丁清单 数据行数 | 249 | **254** | +5；对账恒等式：254 − 划除 2 = manifest **252** ✅ |

回执：`apply.py` 二轮全部 `应用 0｜已应用 1`；`version-lint --apply-docs` EXIT=0。tri-meta PATCH 1.2.9。

### 计数（2026-09-26 · dw5 批增量）

> 上节计数为时点快照，**冻结**。本批 = proposal `reports/proposal-dw5-20260926.md`（Approved: yes 2026-09-26）：
> children 兜底章节 ×9（#14 由 9/9 🔴 FAIL → 0 FAIL）+ tri-release 无预发布环境降级路径（契约第 5 条 + 维度 4）+ CHANGELOG ×9。
> tri-cr 冗余试点经一手核对**取消**（「重复」实为带 §出处的有意聚合设计）。versions.json 机械重建（26 顶层漂移归零 + 补 9 children，直写非 op）。

| 项 | 原值 | 现值 | 依据 |
|---|---|---|---|
| 补丁层 op 数（`manifest.json`） | 252 | **272** | +20（`dw5-*`：兜底章节 9 + release 降级 2 + CHANGELOG 9）；9 个 settle op 目标就地更新（6 份 1.1.4→1.1.5、3 份 1.1.5→1.1.6，不占新行） |
| §当前补丁清单 数据行数 | 254 | **274** | +20；对账恒等式：274 − 划除 2 = manifest **272** ✅ |

回执：`apply.py` 二轮 0 真应用；`version-lint` EXIT=0；`--dir` 实测 #14 children 9/9 PASS。
**新教训（marker 毒化）**：同批前序 op 可向后序 op 的 already_marker 文本注入（本批 release 兜底⑤行含契约 op 的 marker）⇒ 契约 op 首轮被误判已应用而跳过。
**op 顺序约束再 +1**：引用型/指针型 op 必须排在会注入其 marker 的章节 op **之前**。judges 抓出后按未 commit 范式修正（回滚 + 调序 + 重放）。

### 计数（2026-09-26 · 复评微批增量）

> 上节计数为时点快照，**冻结**。本批 = 3 judge 盲评共识短板微批（≥2/3 采信，1 条否决：
> tri-html `name:` 中文名实为家族惯例 6/7，judge 参照系错误）。
> tri-grill PATCH 1.0.3→1.0.4 / tri-html PATCH 1.3.6→1.3.7（settle 就地更新 2 个，不占新行）。

| 项 | 原值 | 现值 | 依据 |
|---|---|---|---|
| 补丁层 op 数（`manifest.json`） | 272 | **286** | +14（`dw6-*`：grill 8 + html 6） |
| §当前补丁清单 数据行数 | 274 | **288** | +14；对账恒等式：288 − 划除 2 = manifest **286** ✅ |
| `ops/README.md` 目录树 op 计数 | 122（过期） | **286** | darwin P0–dw5 各批均未回写该行，本批一并修正 |
| 根 `README.md` 目录树 op 计数 | 122（过期） | **286** | 同上 |

回执：`apply.py` 首轮 14/14「应用 1」（无 marker 毒化）、二轮 0 真应用；`version-lint` EXIT=0。
判定依据：post2 复评 tri-grill 81.8 / tri-html 84.6 为当日最低档，judge 明细未落盘 → 按纪律一手实测
（3 judge 独立盲评当前文件）重建短板证据。
