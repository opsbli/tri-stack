# ops/ —— 自维护 fork 的运维基础设施

## 为什么这个目录在 git 里

本仓库已转为**自维护 fork**（不再依赖上游更新，版本号另起自主线）。
`ops/` 存放自维护所必需的工具与不变量定义。

**它必须进版本控制**，因为：

| 场景 | 若工具在 gitignore 目录（如 `.workbuddy/`） | 在 `ops/`（本目录） |
|---|---|---|
| `skillhub upgrade` 整树替换 skill 目录 | ✅ 存活（不在 skill 目录内） | ✅ 存活 |
| **重新 clone 仓库** | ❌ **丢失** | ✅ **存活** |
| 他人拉取本 fork | ❌ 拿不到 | ✅ 拿得到 |

> 本目录是从 `.workbuddy/patches/` 迁移而来的。迁移前补丁层虽能扛住升级替换，
> 但 `git clone` 后就不存在了 —— 对一个自维护 fork 而言这是硬伤。

## 目录结构

```
ops/
├── README.md                   本文件
├── install-skills.py            junction 安装到 AI 工具（--target / --dry-run / --remove）
├── version-lint.py            版本一致性校验（skill 包内 P1–P5 + 仓库级文档层 D1–D4）
├── versions.json              自主版本线基线（35 个 skill 的版本快照：顶层 26 + tri-sdlc 子 skill 9）
└── patches/                    本地补丁层（对上游 skill 的本地修正）
    ├── README.md               机制说明、补丁清单、每项依据、踩坑
    ├── manifest.json           补丁清单（声明式，唯一事实源，当前 368 个 op）
    ├── apply.py                幂等重放器
    ├── payload/
    │   └── version-check-spec.md   校正版版本检查规范（分发到各 skill 的 references/）
    └── assets/
        └── check_update.py     去耦版脚本（f10 分发到 tri-sdlc 子 skill 的 scripts/）
```

## 安装到 AI 工具（junction 方式）

```bash
# 安装全部 26 个 skill 到 WorkBuddy（推荐先 --dry-run）
python ops/install-skills.py --target ~/.workbuddy/skills

# 安装到其他 AI 工具（改 target 路径即可）
python ops/install-skills.py --target ~/.trae/skills
python ops/install-skills.py --target ~/.cursor/skills

# 卸载
python ops/install-skills.py --target ~/.workbuddy/skills --remove
```

> 使用 Windows junction（`mklink /J`），源始终在仓库（单源），改仓库即生效。
> 安装后通过 junction 运行版本门、compliance_check 等脚本均可正常工作。

## 三个工具

### `version-lint.py` —— 版本一致性校验（skill 包内 P1–P5 + 仓库级文档层 D1–D4）

```bash
python ops/version-lint.py                   # 人类可读报告（退出码 0=无漂移 / 1=有漂移）
python ops/version-lint.py --json            # 机器可读
python ops/version-lint.py --emit-baseline   # 重新生成 ops/versions.json
python ops/version-lint.py --skill tri-coding
```

校验 `tri-intent/references/version-gate.md` §六 定义的一致性，并**补上 §六 漏掉的第 5 处**：

| 点 | 位置 | 说明 |
|---|---|---|
| P1 | `<skill>/SKILL.md` frontmatter `version:` | **唯一真源（基准）** |
| P2 | `<skill>/CHANGELOG.md` 首个 `## [x.y.z]` | 须 = P1，且为全文件最大 |
| P3 | `<skill>/_meta.json` `version` | 平台识别可斜杠激活所需 |
| P4 | `~/.workbuddy/skills/.skills_store_lock.json` | 平台注册表（自维护环境通常不存在） |
| **P5** | **`<skill>/README.md` 的版本声明** | **§六 未列，实测存在的第 5 处**（本仓库补充） |

**P5 只认两种声明形式**：shields.io 徽章 `badge/version-<v>-`，或 README 顶部 frontmatter。
**不认**散文提及（「基于 xxx v1.4.4」）与历史升级记录（「当前版本：2.1.1」）——
改动那些是篡改历史。实测该规则把 12 个「README 含版本号」的 skill 收敛为 4 个真漂移，避开 8 个误报。

### ~~`skills-install.py`~~ —— 平台取包与补装（**已于 2026-09-24 移除**）

该脚本从 `api.skillhub.cn` 下载 skill 包，用于补装「被 tri-intent 路由表引用、但仓库未纳入」
的 skill。**已删除**，理由：它与「停用远端比对」裁定（见 §版本门：自维护模式）**直接冲突**——
既然不再请求平台，就不该保留一个以平台为唯一数据源的工具。

分支收窄为 24 个 skill（编程线 22 + 横向 2）后，全部 skill 均在本仓库内，**无「缺失集」需补装**。（2026-09-25 新增内部工具型 `tri-req-audit` ⇒ 顶层 **25**；同日新增横向验证型 `tri-verify` ⇒ 顶层 **26**）
本地安装统一由 `install-skills.py` 的 junction 方式承担（见 §安装到 AI 工具）。

> **历史**：曾用它从平台补装 11 个被 tri-intent 引用的子类 skill（顶层 29 → 42）。
> 该记录保留于各 skill 的 `CHANGELOG.md`，属追加型历史、不改写。

### `patches/apply.py` —— 补丁层重放器

```bash
python ops/patches/apply.py             # 应用（幂等，可反复跑）
python ops/patches/apply.py --dry-run   # 只报告将发生什么
python ops/patches/apply.py --json      # 机器可读输出
```

## 纪律（重要）

1. **凡新增 / 同步 skill，装完立刻重放补丁层**
   ```bash
   python ops/install-skills.py --target ~/.workbuddy/skills && python ops/patches/apply.py

   # 改了任一 skill 的版本号后，同步仓库级文档层（幂等，只写文档）
   python ops/version-lint.py --apply-docs
   ```
   实证：补装 11 个 skill 时，它们自带 **11 个缺 spec、8 个 tri-forge 断链指针**，
   全部由一次重放自动修好，零手工介入。

2. **任何对 skill 文件的本地修正，都必须表达为 `manifest.json` 里的 op 并重放**
   ——否则下次 `skillhub upgrade` 整树替换后即丢。**不要**直接编辑 skill 文件。
   优先写成**规则化 op**（按语义值比对，如 `sync_version_meta` / `sync_readme_version`），
   而不是字面量替换——规则化 op 对新增/同步的 skill 自动生效。

3. **改完自查幂等**：连续跑两次 `apply.py`，第二次应报 `写入 0｜跳过 N`。
   若每次都报「写入 N」，说明比对逻辑失效（常见原因：行尾差异、字段切错）。

4. **版本一致性用 `version-lint.py` 验，不用肉眼**。退出码 0 才算过。

5. **本目录的改动要随 skill 变更一起提交**，不要在 skill 改动后单独忘记提交 `ops/`。

## 踩坑：bash heredoc 会吃掉正则转义（高危）

**实测**：把 Python 脚本通过 `python - <<'PY' ... PY` 传入时，正则里的 `\s` / `\S`
会被**静默转换成 `/s` / `/S`**，得到永不匹配的模式，而脚本**不报错、只返回 `None`**。

```
pat='^version:/s*(/S+)'   -> None     ← 被吃掉，且无任何报错
pat='^version: *(\\S+)'   -> 匹配
```

⇒ **凡含正则转义的 Python，一律写成文件再执行**，不要用 heredoc / `python -c`。
本次因这个坑，一个交叉校验脚本对 40 个 skill 全部返回 `None`，差点据此误判。

## 踩坑：悬空 junction 会让安装器「看不见」自己的产物（已修）

**事故（2026-09-24）**：`~/.workbuddy/skills/` 下 46 个 `tri-*` 入口**全部悬空**
（都指向已改名的 `codes/tri-skills/<slug>`，而实际源码树是 `codes/tri-stack/<slug>`），
斜杠激活全线失效。而 `install-skills.py` 跑起来报「✅ 新建 24」，并未修复。

**根因**：判定用了跟随链接的 API。对**悬空 junction**：

| 判据 | 悬空 junction 的返回值 | 后果 |
|---|---|---|
| `Path.exists()` | **False** | 走「新建」分支 → `mklink` 报「已存在」而失败 |
| `Path.is_symlink()` | **False** | 同上；**junction 不是 symlink**，Windows 上这条永远不成立 |
| `Path.is_dir()` | False | 同上 |
| `os.path.lexists()` | **True** ✅ | 唯一能同时覆盖「有效链接 / 悬空链接 / 真实目录」的判据 |

⇒ 依次踩了两次：第一版修成 `exists() or is_symlink()`，**仍不生效**——因为 junction 的
`is_symlink()` 也是 False。最终改用 `lexists` + `lstat` 的
`FILE_ATTRIBUTE_REPARSE_POINT (0x400)`。

**另一处**：`is_junction()` 原本以 `if not p.exists(): return False` 开头，
对悬空链接直接短路返回 False ⇒ 连删除都判不出来。已改为不依赖 `exists()`。

**删除方式**：junction 用 `os.rmdir()`（`RemoveDirectory` 语义，只摘重解析点、**不删源**），
不再 `cmd /c rmdir`——少一层 shell 依赖，也避开中文 Windows 的编码问题。

**验证**：修复后重放 → `🔄 重建 24 · 🔴 失败 0`；再跑一次 → `⏭ 跳过 24`（幂等）；
经 junction 运行版本门，`dangling_link` 由 `true` → `false`、`warnings` 清空。

> 复现要点：**凡对链接/重解析点做「存在性」判断，一律用 `os.path.lexists`**，
> 不要用 `Path.exists()`。

## 待裁决项 → 已执行（2026-09-24）

| 项 | 处置 |
|---|---|
| **22 个孤儿入口** | ✅ **已移除**（`已移除 22｜失败 0`）。现 `~/.workbuddy/skills/` 下 `tri-*` 入口 = **24**，`仍悬空 0`、`指向别处 0`。需要时重放 `ops/install-skills.py` 即可重建 |
| `codes/tri-skills/` 空目录 | ✅ **已迁移**至 `%TEMP%\tri-skills-moved-20260924`。实测其内仅 `.idea` 工程元数据（8 项），**非 git 跟踪路径**。采用「移动」而非硬删——`rm -rf` 被安全策略拦在非 Temp 路径；确认无用后可直接删除 |
| 版本节形态未统一 | ✅ **已统一**：33 个版本节**全部**为 `version-stub v1`。按 git 归一化口径（`.gitattributes` 的 `*.md text eol=lf`）实测仅 **2 种形态** —— **32** 个完全一致（14 行，仅 `{slug}` 不同）+ `tri-forge` **26** 行（STUB + 保留的「家族承接职能」专属段）。收敛范围：顶层 **24**（含经 `force_skills` 补齐的 9 个）+ `children/*` **9** |
| 引导安装提示残留 | ✅ **已收敛**：`f8-install-hint-self-maintained`（`replace_regex`）改 **58 文件 / 66 处** `skillhub install … --dir <目标目录>` → 自维护安装器 |

## 相关档案（在 gitignore 目录内，仅本机留存）

`.workbuddy/` 保存一次性勘察与决策留档，**不进版本控制**：
`memory/`（逐日工作日志与硬事实）、`proposals/`（提案与裁定记录）、
`step*.py` / `step*-report.md`（各阶段勘察脚本与报告）、`_upstream/`、`_kit/`。

> 若希望这些决策记录也随 fork 分发，需另行迁入版本化路径。**待裁决。**

### 版本门：自维护模式（已启用）

每个 skill 自带的 `scripts/check_update.py` 内置 `SELF_MAINTAINED = True`：

- **不再请求平台**（裁定 1「停用远端比对」已落地）
- 改为校验本 skill 的 **5 处版本声明**是否一致：P1 `SKILL.md` / P2 `CHANGELOG.md` 首条 /
  P3 `_meta.json` / P4 `lock.json`（存在时）/ **P5 `README.md` 版本声明**
- 状态：`A`（一致，exit 0）/ `D`（存在漂移，exit 12，附修订动作）
- 逃生舱：`TRI_ALLOW_REMOTE=1` 可临时恢复远端比对（仅排障）
- 负向测试已通过：注入 P3/P5 漂移 → 均正确地报 `D` 并给出精确的漂移描述

## 已知未完成项

| 项 | 说明 |
|---|---|
| ~~四处版本一致性校验~~ | ✅ **已完成**：`ops/version-lint.py`（仓库侧）+ `tri-forge/scripts/check_registry.py`（独立安装侧），五点校验（P1–P5） |
| ~~远端版本比对停用~~ | ✅ **已完成**：43+1 份 `check_update.py` 注入 `SELF_MAINTAINED = True`，完全跳过远端请求；tri-sdlc 子 skill 的 9 份于 2026-09-25 随 `f10` 部署时即已内置 |
| ~~版本号漂移清理~~ | ✅ **已完成**：P5 漂移 ×4（tri-god / tri-humanize / tri-music / tri-workflow）已由 `sync_readme_version` op 修复 |
| ~~引导安装提示残留~~ | ✅ **已完成**：`f8-install-hint-self-maintained`（`replace_regex`）收敛 58 文件 / 66 处；CHANGELOG 历史与 `version-gate.md` 纠错注记按「整行守卫」豁免 |
| ~~版本节远端口径~~ | ✅ **已完成**：`converge-version-stub{,-children}` 收敛 33 个版本节（顶层 24 + 子 skill 9）为瘦指针 STUB；`f7-*` 修正契约 §0 的 23 处 |
| ~~版本线升版链~~ | ✅ **已完成**：15 个 skill 升 patch + `--apply-docs` 幂等修正 45 处文档层漂移 + `--emit-baseline` 重写基线（24 skill） |
| ~~children 版本线治理缺口~~ | ✅ **已完成（2026-09-25）**：① 校验覆盖 **24 → 33**（两校验器补扫 `tri-sdlc/children/*`，此前 9 个子 skill 无任何版本守卫）；② `f10`（新 op 类型 `sync_script`）为 9 个子 skill 部署自带 `scripts/check_update.py`（取去耦形态，STUB 命令不再悬空、独立安装成立）；③ 9 个子 skill 升 patch `1.1.1 → 1.1.2` 并记 CHANGELOG（`b80cfa9` 的实质变更此前未升版未记）+ `f11` 同步 tests 描述；④ `f12` 补 README 目录树（漏列 `references/` + 新增 `scripts/`） |
| ~~check_update.py 形态分裂（B5）~~ | ✅ **已完成（2026-09-25）**：顶层 22 份主形态（带 `DEFAULT_SLUG="tri-intent"` 硬编码）经**行为等价双证明**（正向 JSON 全等 / 负向 mutation 注入 P5 漂移双抓、归一后 JSON 全等）后由 `f13` 统一覆盖为去耦形态。终态：**34 份（33 skill + 1 payload）hash 全等**，仅存 1 种形态（2026-09-25 新增 `tri-req-audit` ⇒ **35 份 = 34 skill + 1 payload**，仍全等；同日新增 `tri-verify` ⇒ **36 份 = 35 skill + 1 payload**，仍全等） |
| ~~tri-forge 自建~~ | ✅ **已完成**：`tri-forge/`（15 文件；`tests/mutation-gate.py` 迁入后为 **16** 文件），三模式 + 五门流程 + 22 条门④ + 门③ 路由回流 + 五点版本校验 |
| ~~tri-forge 门④ 负向验证~~ | ✅ **已完成**：mutation testing **6/6** 项注入全部被抓到（见下表） |
| ~~自建 tri-forge 走一次**生成型**实战（门①→⑤）~~ | ✅ **已完成**：`tri-init`（1.0.0 首发 2026-09-24）即该实战产物。① **落盘位置**合规：`tri-forge/SKILL.md` 规定模式 C 产物默认落仓库根 `<slug>/`，`tri-init/` 正合；② **功能证据**：门④ `python tri-forge/scripts/compliance_check.py --skill tri-init` → **FAIL 0 · 需人工 0**（22 条全 PASS/N-A）；③ **包结构**齐备 `references/`+`templates/`+`scripts/`+`tests/`（`templates/` 为 family-spec 的「产出落盘型 skill 必须」项）；④ 时间线：`tri-forge` 1.0.0（2026-09-23）→ `tri-init` 1.0.0（2026-09-24）。⚠️ **判据说明**：仓内**无**门①→⑤ 的逐门执行日志（设计决策留痕在 `.workbuddy/proposals/PROPOSAL-tri-init-20260923.md`，属 D30 契约、未入版本控制），故本项依据 = 用户确认 + 上述功能证据 |

## 门④ 负向测试结果（mutation testing）

| 用例 | 约束 | 门④ 判定 |
|---|---|---|
| M1 版本检查全部指向外部 | #22 | FAIL ✅（抓到） |
| M2 删独立安装声明 | #2 | FAIL ✅ |
| M3 CHANGELOG 首条≠frontmatter | #11 | FAIL ✅ |
| M4 插入硬编码家族计数 | #17 | FAIL ✅ |
| M5 删自检句 | #5 | FAIL ✅ |
| M6 删除 CHANGELOG.md | #1 | FAIL ✅ |
| **还原后终态** | — | **PASS** ✅ |

⇒ 门④ **有牙**：6/6 项典型合规缺陷全部被对应条目精确拦截，还原后恢复 PASS。
测试脚本原在 `.workbuddy/_mutation-gate.py`（gitignore 目录内）；**已迁入版本控制** → `tri-forge/tests/mutation-gate.py`（`git ls-files` 已跟踪）。

## 计数增量（2026-09-25）

新增内部工具型 skill **`tri-req-audit`**（需求文档审核）后，下列**当前态**计数已就地更新。
上文**带日期的历史条目**（「待裁决项 → 已执行（2026-09-24）」表内数字、`🔄 重建 24` 等**实测输出引文**、
`--emit-baseline 重写基线（24 skill）`）为**时点快照，一律不改写** —— 改写它们等于伪造当时的结论。

| 计数 | 原值 | 现值 | 佐证 |
|---|---|---|---|
| 顶层 skill | 24 | **25** | `compliance_check.py --all` 审计对象数 |
| 校验覆盖（顶层 + `tri-sdlc/children/*`） | 33 | **34** | `tri-forge/scripts/check_registry.py --check` 报「检查 34 个 skill；漂移 0」 |
| `version-check-spec.md` 份数 | 33 | **34** | `spec-per-skill` op 实测 `跳过 34` |
| `check_update.py` 份数 | 34（33 skill + 1 payload） | **35（34 skill + 1 payload）** | 34 份 skill 副本 + `ops/patches/assets/` 1 份，hash 仍全等 |
| 补丁层 op 数 | 23 | **122** | `ops/patches/manifest.json` |
| `converge-version-stub` 覆盖顶层节 | 24 | **25** | 该 op 实测 `跳过 25` |
| `f13` 覆盖 | 24 | **25** | 该 op 实测 `跳过 25` |

> 快照口径（P4 已刷新）：`ops/versions.json` 条目由 **33 → 34**。

### 计数增量（2026-09-25 · 第二轮）

修复 `compliance_check.py` **角色识别盲区**（补丁 op `f20-role-detection`）后：
补丁层 op 数 **30 → 31**。skill 数 / 校验覆盖 / `check_update.py` 份数**均不变**
（该 op 只改 `tri-forge/scripts/compliance_check.py`，不动 skill 集合）。

| 受影响位置 | 处置 |
|---|---|
| 上方目录树 `当前 30 个 op`、§计数对账表 `补丁层 op 数` 行 | ✅ 已改当前值 |
| 根 `README.md` 目录树 `30 个 op` | ✅ 已改当前值 |
| 本文件 §计数增量（第一轮）与上表其余行 | ⬜ **冻结** —— 当时实测快照 |

> 本轮同时给 `ops/patches/README.md` 的「踩坑」小节补了**坑 4**（纯删除型修正无可用
> `already_marker`）与**坑 5**（工作区 `\r\r\n` 使多行 `old` 静默不命中）。

### 计数增量（2026-09-25 · 第三轮）

`tri-frontend-design` 路由自述更正（补丁 op `f21`–`f25`，口径修正、无行为变更）后：
补丁层 op 数 **31 → 36**。skill 数 / 校验覆盖 / `check_update.py` 份数**均不变**；
`ops/versions.json` 中该 skill 由 **1.1.3 → 1.1.4**（`--emit-baseline` 已刷新）。

| 受影响位置 | 处置 |
|---|---|
| 上方目录树与 §计数对账表 `补丁层 op 数` | ✅ 已改当前值 |
| `WORKFLOW-GUIDE.html`（D1 chip）与根 `README.md`（D4 表行）的该 skill 版本 | ✅ 已由 `version-lint.py --apply-docs` 幂等修正 |
| `ops/version-lint.py` 内 `# 顶层 24 个 tri-*` 注释 | ✅ 更正为 25（上轮改数遗漏的注释层） |
| 前两轮增量小节 | ⬜ **冻结** —— 当时实测快照 |

### 计数增量（2026-09-25 · 第四轮）

新增横向验证型 skill **`tri-verify`**（运行中应用的功能验证）后，下列**当前态**计数已就地更新。

| 计数 | 原值 | 现值 | 佐证 |
|---|---|---|---|
| 顶层 skill | 25 | **26** | `compliance_check.py --all` 审计对象数 |
| 校验覆盖（顶层 + `tri-sdlc/children/*`） | 34 | **35** | `ops/version-lint.py` 报「检查 35 个 skill；存在漂移 0 个」 |
| `version-check-spec.md` 份数 | 34 | **35** | `spec-per-skill` op 实测 `跳过 35` |
| `check_update.py` 份数 | 35（34 skill + 1 payload） | **36（35 skill + 1 payload）** | 35 份 skill 副本 + `ops/patches/assets/` 1 份，36/36 同 hash |
| 补丁层 op 数 | 36 | **45** | `ops/patches/manifest.json`（新增 `f26`–`f34`） |
| `ops/versions.json` 条目 | 34 | **35** | 已含 `tri-verify` 1.0.0 |
| `converge-version-stub` 覆盖顶层节 | 25 | **26** | 该 op 实测 `跳过 26` |
| `f13` 覆盖 | 25 | **26** | 该 op 实测 `跳过 26` |

| 受影响位置 | 处置 |
|---|---|
| 上方目录树 `versions.json` / `当前 45 个 op` 两行、§安装命令示例 `25 个 skill` | ✅ 已改当前值 |
| 上方 §计数对账表 `补丁层 op 数` 行 | ✅ 已改当前值（该表其余行系 tri-req-audit 冻结快照，不刷新） |
| 根 `README.md` 技能目录标题、目录树 `versions.json` 与 `patches/` 两行 | ✅ 已改当前值 |
| `WORKFLOW-GUIDE.html` §04「第零步」正文（`34 个 skill（顶层 25 + 9）`） | ✅ 已改当前值 |
| `ops/version-lint.py` 内 `# 顶层 25 个 tri-*` 注释 | ✅ 更正为 26 |
| `ops/patches/manifest.json` 的 `converge-version-stub` / `f13` 两条 label | ✅ 已改当前值（25 → 26） |
| 前三轮增量小节 | ⬜ **冻结** —— 当时实测快照 |

> 本轮为**纯新增**（新增 1 个 skill + 9 个 op），未改动既有 skill 的版本号。
> 复核判据：`version-lint.py` 退出码 0（存在漂移 0 个）；`apply.py` 连跑两次，第二次 `应用 0｜写入 0`。

### 计数增量（2026-09-25 · 第五轮 · `tri-req-audit` 对抗层硬化）

`tri-req-audit` 的**审核对抗层硬化**（补丁 op `f35`–`f50d` 系列 + 插序的 `f43` / `f46a` / `f46b` / `f47a`，
共 **22** 个）后：补丁层 op 数 **45 → 76**。本轮**纯改既有 skill 内容**，
skill 集合与版本线覆盖面均未变（`tri-req-audit` 自身由 1.0.0 → 1.1.0）。

| 计数 | 原值 | 现值 | 佐证 |
|---|---|---|---|
| 顶层 skill | 26 | **26** | 不变（本轮无新增 skill） |
| 校验覆盖（顶层 + `tri-sdlc/children/*`） | 35 | **35** | 不变 |
| `version-check-spec.md` 份数 | 35 | **35** | 不变 |
| `check_update.py` 份数 | 36 | **36** | 不变 |
| 补丁层 op 数 | 45 | **76** | `ops/patches/manifest.json`（本轮 22 + 并发会话 9） |
| `ops/versions.json` 中 `tri-req-audit` | 1.0.0 | **1.1.0** | `--emit-baseline` 已刷新 |

| 受影响位置 | 处置 |
|---|---|
| 上方目录树 `当前 45 个 op` | ✅ 已改当前值（76） |
| 上方 §计数对账表（第一轮）`补丁层 op 数` 行 | ✅ 已改当前值（沿用第四轮先例：该行按「当前态账本」就地刷新，该表其余行冻结） |
| 根 `README.md` 徽章 `skills-24`、目录树两处 op 数 | ✅ 已改当前值（26 / 76） |
| `WORKFLOW-GUIDE.html`（D1 徽章 chip / D2 正文）与根 `README.md`（D4 表行）的该 skill 版本 | ✅ 已由 `version-lint.py --apply-docs` 幂等修正（3 处） |
| 前四轮增量小节与全部冻结段落 | ⬜ **冻结** —— 当时实测快照 |

> ⚠️ **并发来源说明**：本轮执行期间，另有会话向 `manifest.json` 追加 **9** 个 op
> （`f60-action-fallback` … `f68-workflow-fallback`，涉 9 个 skill 的 fallback 分支），
> 故 45 + 22 + **9** = **76**。本小节「现值」一律取**实测总数**；那 9 个 op 的清单行由该会话自行补记
> （见 `ops/patches/README.md` §当前补丁清单尾注），本文件**不代填**，避免双方重复追加。

> 复核判据：`ops/version-lint.py` 退出码 0（漂移 0，文档层无漂移）；`apply.py` 连跑两次，
> 第二次 `应用 0｜写入 0`；`tri-req-audit/scripts/audit_gate.py --self-test` 全绿。


### 计数增量（2026-09-25 · 第六轮 · 门④ #14 判据硬化 + 版本纪律 + 回溯补版）

补丁层 op 数 **76 → 122**（+47 新增 −1 退役）；顶层 skill **26** / 校验覆盖 **35** / `check_update.py` **36** 份
**均不变**；18 个 skill PATCH 升版（`ops/versions.json` 已 `--emit-baseline` 刷新）。

| 载体 | 处置 |
|---|---|
| 上方目录树 `当前 76 个 op`、§计数对账表（第一轮）`补丁层 op 数` 行 | ✅ 已改当前值（122） |
| 根 `README.md` 目录树 `76 个 op` | ✅ 已改当前值（122） |
| `ops/patches/README.md` §当前补丁清单 | ✅ 补 `f60`–`f68` 9 行 + 本轮 47 行；`f24` 改为划除行 |
| 前五轮 §计数增量 与全部带日期快照 | ⬜ **冻结** —— 当时实测快照，不改写 |

> 本轮由**单会话**完成（无并发写入）。新增约定「版本线 op 用 `replace_regex` settle 形式」详见
> `ops/patches/README.md` 同名小节。
