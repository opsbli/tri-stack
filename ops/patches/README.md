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

## 实测踩过的三个坑（都会导致补丁层静默失效）

### 坑 1 · 行尾混用导致字节级匹配不命中

**本仓库行尾本就混用**：多数 `.md` 的 **git blob 本身就是 CRLF**
（实测 `README.md` blob 含 203 行 CR、`CONTRIBUTING.md` 含 133 行 CR，无 `.gitattributes`，
`core.autocrlf=true`——作者在 Windows 上开发）；而本补丁层新写入的 spec 是 LF。

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

## 当前补丁清单

| id | 类型 | 作用 |
|---|---|---|
| `spec-per-skill` | sync_spec | 为每个引用 `version-check-spec.md` 的 skill 部署校正版自带 spec（当前 33 个 = 顶层 24 + `children/*` 9） |
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
| `converge-version-stub` | converge_version_section | 顶层 skill 版本节统一为瘦指针 STUB（当前 **24** 个 = 顶层全部；含 `force_skills` 补齐的 9 个） |
| `converge-version-stub-children` | converge_version_section | `tri-sdlc/children/*` 9 个子阶段 skill 同款收敛（同缺陷类，scope 独立便于裁定） |
| `f7-contract-mode` | replace_text | 契约 §0：「连接 skillhub 校验 + `skillhub upgrade`」→ 自维护本地校验（22 处） |
| `f7b-contract-mode-intent` | replace_text | 契约 §0 变体（`tri-intent`）：远端校验/升级 + 端点内联 → 自维护口径 |
| `f8-install-hint-self-maintained` | replace_regex | 引导安装提示：`skillhub install <slug> [--dir <目标目录>]` → 自维护安装器（58 文件 / 66 处） |
| `f9-gate-script-rebuilt` | replace_text | `version-gate.md` §六：更正「脚本门禁当前缺失」→ 已重建为 `tri-forge/scripts/check_registry.py` |

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

> ⚠️ **测形态时必须先归一化行尾**：本仓库 `core.autocrlf=true` 且 `.gitattributes` 强制
> `*.md text eol=lf`，工作区字节可能是 `\r\r\n`（旧 CRLF blob 又被 smudge 一次）。
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
