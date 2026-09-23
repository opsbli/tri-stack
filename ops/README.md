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
├── skills-install.py           平台取包 / 补装 / 缺失检测
├── version-lint.py            四处版本一致性校验（§六 + 本仓库补充的 P5）
├── versions.json              自主版本线基线（40 个 skill 的版本快照）
└── patches/                    本地补丁层（对上游 skill 的本地修正）
    ├── README.md               机制说明、补丁清单、每项依据、踩坑
    ├── manifest.json           补丁清单（声明式，唯一事实源，当前 12 个 op）
    ├── apply.py                幂等重放器
    └── payload/
        └── version-check-spec.md   校正版版本检查规范（分发到各 skill 的 references/）
```

## 三个工具

### `version-lint.py` —— 四处（实为五处）版本一致性校验

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

### `skills-install.py` —— 平台取包与补装

```bash
python ops/skills-install.py --detect              # 只报告缺失集（只读）
python ops/skills-install.py --detect --install     # 检出缺失并全部补装
python ops/skills-install.py --slugs tri-pm,tri-wiki --install
python ops/skills-install.py --detect --dry-run     # 预演，不写盘
```

「缺失集」= **被引用 − 本地已有 − 不可得**：从总路由 skill（`tri-intent`）全文抽取
`tri-*` slug，剔除子技能名 / 文件名 / 日期标签，再减去显式黑名单（当前仅 `tri-forge`）。

当前状态：**检出 0 个缺失**（11 个曾被引用的子类 skill 已补装；`tri-forge` 在
任何可达源都不存在，且上游 `.gitignore` 显式排除了 `tri-forge/`，属作者有意私有）。

### `patches/apply.py` —— 补丁层重放器

```bash
python ops/patches/apply.py             # 应用（幂等，可反复跑）
python ops/patches/apply.py --dry-run   # 只报告将发生什么
python ops/patches/apply.py --json      # 机器可读输出
```

## 纪律（重要）

1. **凡新增 / 同步 skill，装完立刻重放补丁层**
   ```bash
   python ops/skills-install.py --detect --install && python ops/patches/apply.py
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

## 相关档案（在 gitignore 目录内，仅本机留存）

`.workbuddy/` 保存一次性勘察与决策留档，**不进版本控制**：
`memory/`（逐日工作日志与硬事实）、`proposals/`（提案与裁定记录）、
`step*.py` / `step*-report.md`（各阶段勘察脚本与报告）、`_upstream/`、`_kit/`。

> 若希望这些决策记录也随 fork 分发，需另行迁入版本化路径。**待裁决。**

## 已知未完成项

| 项 | 说明 |
|---|---|
| 四处版本一致性校验 | `tri-intent/references/version-gate.md` §六 要求 4 处版本号一致，原由 tri-forge 的 `sync_registry.py` 校验，现**缺脚本门禁**（`ops/` 尚无对应校验器）。计划由自建的 tri-forge 承接 |
| 远端版本比对停用 | 自维护后「与平台比版本」失去意义，计划停用 `check_update.py` 的远端比对 |
| ~~版本号漂移清理~~ | ✅ **已完成**：真实漂移在 **P5（README 版本声明）×4**（`tri-god` / `tri-humanize` / `tri-music` / `tri-workflow`）。P1–P4 一直一致。校验器 `ops/version-lint.py`，修复 op `sync_readme_version` |
