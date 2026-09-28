# 锻造交付摘要 · `code-design-doc`（C 模式 · 详细设计说明书模板填充）

> 由 `tri-forge` 门⑤ 产出。**产物清单 + 门④ 24 条自检结果 + 门③ 路由登记记录 + 安装评估**。
> 本次输入来源：`direct`（用户直接触发；无 `.tribro/LATEST.md` 快照，未走快照链路）。
> 本报告为**时点快照，按仓库惯例冻结**。

## 一、输入确认（门①）

| 项 | 值 |
|---|---|
| skill 名 / slug | 详细设计说明书模板填充 / `code-design-doc` |
| 骨架来源 | `云南省财政厅集中运维体系建设项目（1标段）详细设计说明书-模板V1.0(1).docx` |
| 证据来源 | `D:\workspaces\{itom-base, itom-maintenance, tdma-monitor}`（Java + Maven） |
| 是否 tri-intent 下游 | **是**（认领 L2 = **I10 分析处理**；`L3_子意图 = design-doc`） |
| 上游检测态数 | 三态（快照模式 / 引导安装 / 降级模式） |
| 落盘位置 | **平台用户级** `~/.workbuddy/skills/code-design-doc/`（非本仓库源码树，故不入 `tri-*` 计数） |
| 门④ 判据版本 | `compliance-checklist.md` 24 条（12 家族硬约束 + 8 增强 + 1 安装 + 1 版本去重 + 2 证据驱动） |

### 模板解析实测（骨架事实源）

| 项 | 实测值 |
|---|---|
| 一级章 / 二级节 | **6** / **22** |
| 「补充：xxx」三级小节 | **15** |
| 设计表 | **6** 张（T-1 状态类别 / T-2 性能验证 / T-3 内部调用 / T-4 初始化 / T-5 错误类别 / T-6 检测点） |
| 六段式字段 | 模块定位 / 角色与前置 / 输入项 / 处理逻辑 / 输出项 / 模块特有规则·状态与审计 |
| 编号体系 | `SWU-*` / `MOD-*` / `COM-*` / `DATA-*` / `IF-*` / `INT-*` |

> ⚠️ **必须声明的口径修正**：初次口述为「8 张表」，直读 `word/document.xml` 实测后确认为 **6 张**。
> 产物 `references/template-structure.md` 已按实测值落盘。该模板另有两处**上游噪音**（8 个功能小节的
> 四段正文逐字重复且内容为无关的「账号管理」业务；`图4-3`/`表4-1` 号段与本章号冲突），
> 已作为「模板噪音三条」写入画像，要求在填充时**以本模板章号重编**并**不照抄重复正文**。

### 代码取证实测（证据源事实）

| 仓库 | 服务模块 | `*Controller.java` 实测数 | 顶层包 |
|---|---|---|---|
| `itom-base` | `itom-base-server` | **153** | base / cmdb / dict / door / message / user / websocket / zabbix |
| `itom-maintenance` | `itom-maintenance-server` | **142** | console(ansible/local·remote) / inspection / maintenance / monitor |
| `tdma-monitor` | `tdma-monitor-server` | **53** | grafana / monitor / prometheus / telegraf |

## 二、产物清单（门② 产出）

**12 个文件 / 1077 行**，落于 `~/.workbuddy/skills/code-design-doc/`：

| 文件 | 行数 | 内容 |
|---|---|---|
| `SKILL.md` | 233 | 五阶段链路 + 四门 + 证据锚强制 + 模板格式从属强制 |
| `README.md` | 85 | 特性 / 安装（junction）/ 用法（含链路图）/ 目录结构 / 设计原则 |
| `CHANGELOG.md` | 25 | 首条 `## [1.0.0] - 2026-09-28` |
| `_meta.json` | — | `ownerId / publishedAt / slug / version` |
| `references/version-check-spec.md` | 154 | 版本检查执行规范（内部化持有 → 满足第 22 条） |
| `references/template-structure.md` | 83 | **模板画像单一事实源**（6 章骨架 / 六段式 / 6 表列序 / 噪音三条 / 段落样式） |
| `references/code-evidence-rules.md` | 65 | **取证判据单一事实源**（S1/S2/S3/无锚四级 + 六段式取证锚点 + 编号反推 + 取证纪律 5 条） |
| `references/evidence-gate.md` | 81 | **门禁判据单一事实源**（G-2-1 锚覆盖率 / G-2-2 `[待确认]` 上限 0.5 / G-3-1·G-3-2 编号自洽 / G-4-1·G-4-2 回填保护） |
| `templates/outline.md` | 91 | 按章推进清单（6 章全节 checkbox）+ `outline.json` 字段结构 |
| `templates/section-skeleton.md` | 74 | 六段式骨架 + 6 表配合表 + 填写示例（3.1 补充：实时监控 片段） |
| `tests/code-design-doc-full-testcases.md` | 186 | A–H 八组能力清单 + ≥30 条用例（`T-A-1` … `T-H-4`） |
| `scripts/check_update.py` | — | 版本门（自维护模式，P1–P5 本地一致性） |

### 关键契约（SKILL.md 强制执行 8 条中的两条）

- **证据锚强制（第一性规则）**：产物中每一条陈述性断言 MUST 携带 `file:line` 级证据锚；
  采集不到证据的断言 MUST 标注 `[待确认]`；NEVER 编造证据、NEVER 因催促放宽本条。
- **模板格式从属强制**：填充 MUST 沿用模板**既有**章节层级、六段式字段名、表格列序与编号体系；
  NEVER 自行新增章节。模板自带的重复正文与冲突图号按「噪音三条」处置。

## 三、门④ 24 条自检结果

**门④ PASS —— FAIL 0 / MANUAL 1（已人工取证，见 §四）/ N-A 1（附理由）**

| # | 约束 | 判定 |
|---|---|---|
| 1 | 目录结构完整 | ✅ PASS |
| 2 | 独立安装声明 | ✅ PASS（含「上游依赖检测三态逻辑」） |
| 3 | SKILL.md 章节齐全且顺序正确 | ✅ PASS（九类齐全；版本节置后属家族 5 例既有变体，非缺陷） |
| 4 | frontmatter 完整 | ✅ PASS（八字段；`version: 1.0.0`） |
| 5 | 强制执行契约含自检句 | ✅ PASS |
| 6 | 上游检测态数与类型匹配 | ✅ PASS（检出：引导安装 / 降级模式 / 降级） |
| 7 | 职责边界明确 | ✅ PASS（13 行，含「不负责」） |
| 8 | 意图认领 MECE 不重叠 | 🔍 MANUAL → **已取证 PASS**（§四） |
| 9 | 核心能力方法论含可扩展性 | ✅ PASS |
| 10 | 交付产物含落盘规则 | ✅ PASS（写明 `.tribro/design-doc/`、`docs/`、就地更新三档） |
| 11 | CHANGELOG 规范 | ✅ PASS（首条=1.0.0=frontmatter=文件最大） |
| 12 | tests 全场景用例 | ✅ PASS（186 行；≥50 行且标题含「测试用例」） |
| 13 | 门禁/审批门明确 | ✅ PASS（四门） |
| 14 | 兜底处理覆盖 | ✅ PASS（专门章节 + NEVER；五类关键词 5/5） |
| 15 | 自检句格式与家族一致 | ✅ PASS |
| 16 | 反规避规则（建议项） | ✅ PASS |
| 17 | **禁止硬编码家族计数** | ✅ PASS（正则 `\d+\s*个(下游\|skill\|顶层目录\|tri-\*)` 未命中） |
| 18 | 可执行实现与 prompt 分离 | ✅ PASS（`scripts/check_update.py`） |
| 19 | 与相邻 skill 边界表（建议项） | ✅ PASS |
| 20 | 横向层自检句例外登记 | ⬜ N-A（角色=downstream，非横向型） |
| 21 | 安装评估 | ✅ PASS（目录可写=是） |
| 22 | 版本检查内部化 | ✅ PASS（自身指针=有；指向外部=否；节 19 行 ≤30 行 STUB） |
| 23 | 规范性判据单一事实源 | ✅ PASS（包内指针 5 个，不可解析 0） |
| 24 | **评估产物含案级结构化结论** | ✅ PASS（SKILL.md 内含 `\| 条目 ID \| 目标章节 \| 断言摘要 \| 证据锚（file:line） \| 判定 \|` 字段表） |

> 复跑命令：`python tri-forge/scripts/compliance_check.py --dir ~/.workbuddy/skills/code-design-doc`
> → `审计对象 1 个；门④ FAIL 0 个` · `门④ PASS（FAIL 0 · 需人工 1）`

## 四、门④ 第 8 条 `[需人工]` 人工取证（MECE 交叉比对）

判据要求「交由人类/Agent 交叉比对 `tri-intent/SKILL.md` §路由映射表」。本次不以散文断言，改用**可执行判据**取证
（脚本落 `%TEMP%/cdd_gate8.py`，退出码 0）：

| 检查 | 判据 | 结果 |
|---|---|---|
| ① 可执行映射键/值互异 | `hooks/intent-gate.py` 中 `SUBTYPE_SLUGS` 的 I10 条目 | **4 条**：`arch-viz→tri-html` / `audit-checklist→tri-checklist` / `code-analyzer→tri-code-analyzer` / `design-doc→code-design-doc`；键互异 True · 值互异 True |
| ② 下游 slug 认领唯一 | 全局反查 `code-design-doc` 的认领方 | 恰为 `[("I10","design-doc")]`，无第二认领方 |
| ③ 四处真源齐全 | SKILL.md §一路由行 / §一子类说明 / `doing/I10-analyze.md` 子类段 / `README.md` L3 表 | 各命中 1 ✅ |
| ④ 计数联动 | 四子类说明 / description / 路由型 17 / 引言四个 / MECE 四个 / hook 注释四个 | 6 项各命中 1 ✅ |
| ⑤ 旧口径残留 | 「现有三个 L3 子类」/「I10 三个子类说明」/「三个子类见下方」 | 活跃真源内**均为 0** ✅ |
| ⑥ 交付物形态互斥 | MECE 句中形态枚举 | `HTML 图表 / 复选框清单 / 深度剖析报告 / 模板化交付文档`，四元互异 ✅ |
| ⑦ 交付物落地 | 12 个必备文件存在性 | 缺失 0 ✅ |

**结论：PASS。** `design-doc` 与三个既有子类在**可执行映射层（键唯一）**、**产出物形态层（四元互斥）**、
**分析对象层（源码+模板 vs 项目架构 / 改动点 / 代码实现细节）** 三个维度均无重叠；
与 I10 默认（通用分析，本分支无下游）的边界亦有明文。

## 五、门③ 路由回填记录（**全部走 op 重放，未直改 skill 文件**）

`tri-intent` 版本 **1.14.3 → 1.14.4**。版本线由**既有 settle op `f94-ver-intent` 目标就地更新**（不占新 op 行）。

| op id | 目标 | 作用 |
|---|---|---|
| `cdd-ti-route-row` | `tri-intent/SKILL.md` | §一路由映射表 I10 行补 `code-design-doc` |
| `cdd-ti-note` | `tri-intent/SKILL.md` | §一 I10 子类说明 三子类→四子类（条目 / MECE / 依赖检测路径） |
| `cdd-ti-i10-section` | `tri-intent/doing/I10-analyze.md` | 子类判定真源新增 `design-doc` 子类段 |
| `cdd-ti-i10-mece` | `tri-intent/doing/I10-analyze.md` | MECE 论证表补行 + 该段「三个子类」→「四个子类」 |
| `cdd-ti-i10-intro` | `tri-intent/doing/I10-analyze.md` | 子类路由引言「现有三个 L3 子类」→「四个」（**批中补正**） |
| `cdd-ti-hook-comment` | `tri-intent/hooks/intent-gate.py` | `SUBTYPE_SLUGS` 上方注释「三个子类」→「四个」（**批中补正**） |
| `cdd-ti-hook` | `tri-intent/hooks/intent-gate.py` | `SUBTYPE_SLUGS` 补 `("I10","design-doc") → code-design-doc` |
| `cdd-ti-readme` | `tri-intent/README.md` | L3 子类路由表补 `design-doc` 行 |
| `cdd-ti-desc` | `tri-intent/SKILL.md` | frontmatter description「仅 I10 三子类」→「四子类」 |
| `cdd-ti-summary` | `tri-intent/SKILL.md` | frontmatter summary「16 个下游」→「17 个下游」 |
| `cdd-ti-counts` | `tri-intent/SKILL.md` | §四 计数口径：路由型 16 → 17 + 枚举补 slug + 非 `tri-*` 成员说明 |
| `cdd-ti-cl` | `tri-intent/CHANGELOG.md` | 追加 `## [1.14.4] - 2026-09-28` |
| `cdd-forge-fspec` | `tri-forge/references/family-spec.md` | §五 待登记项：登记「I10 第四 L3 子类 · design-doc」 |
| `cdd-doc-opsreadme-count` | `ops/README.md` | 目录树 op 计数 → 353（**settle 形式** `replace_regex`） |
| `cdd-doc-rootreadme-count` | `README.md` | 目录树 op 计数 → 353（**settle 形式**） |
| `cdd-doc-registry-rows` | `ops/patches/README.md` | §当前补丁清单补登 cdd 批 **17** 行 + `f94` 就地更新注记 |
| `cdd-doc-count-section` | `ops/patches/README.md` | 追加「计数（2026-09-28 · cdd 批增量）」小节 |

### 重放回执（干净基线）

| 轮 | 结果 |
|---|---|
| 构建期断言 | 17 个 cdd op 对回滚后干净目标：`replace_text` 全部 `old×1 / marker×0`；`replace_regex` 全部 `re_hits=1 / re_lines=1 / marker=0` |
| RUN 1 | 17/17 新建 op **「应用 1｜已应用 0」** + `f94-ver-intent`「应用 1」+ `sync-version-meta`「写入 1」（`_meta.json` 1.14.3 → 1.14.4） |
| RUN 2 / RUN 3 | `应用 1｜已应用 0` 计数 = **0**；17 个 cdd op 全部「应用 0｜已应用 1」→ **幂等成立** |

> 唯一 `not_found` 4 条（`f3-clause-inline` / `f3-clause-sentence` / `f3-standalone-line` / `dw-test-contract-fix`）
> 为**既有**登记项（目标文本已不存在于活跃树），与本批无关。

### 计数联动（当前态账本同批回写）

| 项 | 原值 | 现值 | 依据 |
|---|---|---|---|
| 补丁层 op 数 | 336 | **353** | +17（路由回填 13 + 文档计数 4）；`f94` 目标就地更新不占行 |
| 顶层 skill / 校验覆盖 | 26 / 35 | **26 / 35** | **不变**——`code-design-doc` 落平台用户级，不进源码树 |
| `tri-intent` §四 路由型下游 | 16 | **17** | 该集合**首次含非 `tri-*` 前缀成员** |

## 六、批中补正（同批内，未 commit）

门④ 复核发现两处**由本批引入**的残留计数，均已按仓库「未 commit 就地改 op」范式收口：

| # | 残留 | 成因 | 处置 |
|---|---|---|---|
| 1 | `doing/I10-analyze.md` 引言「现有三个 L3 子类」 | 原 `cdd-ti-i10-mece` 只覆盖 MECE 段同义句，漏了引言 | 补 op `cdd-ti-i10-intro`（**未新增纠错 op**） |
| 2 | `hooks/intent-gate.py` 注释「三个子类」 | 新增第 4 条 `SUBTYPE_SLUGS` 时未联动注释 | 补 op `cdd-ti-hook-comment` |
| 3 | 两处 op 计数 op 为字面 `replace_text`（`336→351`） | 批中 op 数再增 2 ⇒ 目标值过期，字面 op 会 `not_found` | **就地改为 settle 形式 `replace_regex`**（pattern `唯一事实源，当前 \d+ 个 op）` 等，收敛任意旧值）→ 消除「计数随 op 数联动」的链式追加，即 **f86/f97 同款永动的根治** |

> 另一处**早期纠偏**（同批）：首轮曾误新增 `cdd-ti-ver` 与既有 settle `f94-ver-intent` 同 glob 同 pattern，
> 两 op 互搏导致 `_meta.json` 停在 1.14.3。按「settle 目标就地更新、NEVER 追加链式 op」**回滚 + 就地改 `f94`**，
> 未保留任何纠错 op。

## 七、门④.5 判定：**N-A**

**理由**：门④.5 的适用对象是「**变更既有 skill 的规范性判据**」——即对本仓库既有 skill 的 SKILL.md / 判据
做改动时，须做变更前后的行为等价性与误报翻转验证（家族先例：`tri-forge` 第 24 条硬化时翻 5 条 / 未变 14 条 / 零误报）。
本次为**从零生成一个族外新 skill**（`code-design-doc` 不在本仓库源码树），不涉及任何既有 skill 的判据改动，
故门④.5 **不适用**。本批对仓库的改动全部是**路由登记 / 计数记账型**（不新增、不放宽任何判据），
按契约以「`compliance_check.py` FAIL 0 + 幂等重放零真应用」作为等价性判据。

## 八、版本与文档层一致性

| 项 | 结果 |
|---|---|
| 新 skill 版本门 | `check_update.py --slug code-design-doc` → **A 校验通过**（自维护模式；P1/P2/P3/P4/P5 五处一致；当前 1.0.0） |
| 仓库包内漂移 | `version-lint.py` 检查 35 个 skill → 漂移 **1**：`tri-forge`（P2 1.2.0 ≠ P1 1.0.5）——**非本轮引入**（`git diff HEAD -- tri-forge/` 仅 `family-spec.md`），见 §十 候选 ① |
| 文档层 D1–D4 | `--apply-docs` 幂等修正 **4** 处（`WORKFLOW-GUIDE.html` D2×2 + D1×1 / `README.md` D4×1，均为 `tri-intent` 1.14.3→1.14.4）；复跑 → **文档层无漂移** |

## 九、安装评估（第 21 条，三查）

| 查 | 结果 |
|---|---|
| slug 冲突 | 无同名 skill；`~/.workbuddy/skills/code-design-doc/` 为该 slug 唯一目录 |
| 目标目录可写 | 是（12 文件已实际落盘，1077 行） |
| 四平台路径可落地 | 下游依赖检测候选路径 ③ 覆盖 `~/.workbuddy` / `.trae` / `.cursor` / `.qcoder` 四个平台用户级目录；`check_downstream.py` 无需改造即可检出 |

## 十、遗留与候选（按优先级 + 编号）

| # | 级别 | 事项 | 说明 / 建议 |
|---|---|---|---|
| ① | 🟠 P1 | `tri-forge` P2≠P1 漂移（CHANGELOG 首条 **1.2.0** vs SKILL.md **1.0.5**） | **非本轮引入**。`dw2-tri-forge-version` 把 P1 settle 在 1.0.5，而 CHANGELOG 首条是 2026-09-27 的 1.2.0（来源 proposal `d24-promote-to-mandatory`，`Approved: yes`）——疑为 CHANGELOG 升版后遗漏 frontmatter 升版 op。**先取证「1.2.0 的变更是否真的在树内」再定方向**（就地更新 `dw2` 目标至 1.2.0，或回写 CHANGELOG 首条），建议独立 proposal 走 D30 |
| ② | 🟡 P2 | `WORKFLOW-GUIDE.html` G3 卡片（「G3 代码洞察 · I10 一跳覆写」）未收录 `code-design-doc`，正文仍写「按产出物形态**三选一**」 | 该指南自我限定为**仓库作用域**（「本仓库…26 个 skill」），而 `code-design-doc` 属平台用户级 ⇒ 不收录**在口径上自洽**、`cnt=3` 与 3 个 chip 也自洽。但它同时是路由地图，缺 I10 第四子类入口。**需裁定**：补一张标注「用户级安装」的 chip + 改「四选一」，或维持现状并在指南声明「仅列仓库成员」 |
| ③ | 🟢 P3 | 本报告与 skill 包**未 commit** | 12 个改动文件 + 本报告仍在工作区；是否落 commit 待放行（push 另行放行） |
| ④ | 🟢 P3 | 真实模板填充**尚未跑过端到端** | 本批只交付 skill 能力；建议用《云南省财政厅…详细设计说明书》+ 三个 `itom-*` 仓库跑一次 §五 五阶段链路，以校准 G-2-1 锚覆盖率阈值的实际可达区间 |
## 十一、端到端试点（新增类回归样例 · 2026-09-28）

> **本节为增量**。上文 §一–§十 是门⑤ 交付当日的**冻结快照**，按仓库惯例**不回改**；
> §十 中 ① / ③ / ④ 三项的状态在本节更新（见 §11.8）。

### 11.1 目的与依据

纪律依据（MEMORY 项目长期约定）：**「新增类 MUST 用新样本跑一次链路」**。
本批新增的 `code-design-doc` 属**族外新 skill**，须以「真实模板 + 真实代码库」跑通 §五 五阶段链路，
验证它在真实仓库上能产出**可交付产物**——而不是只在自造夹具上自洽。

### 11.2 输入与执行模式

| 项 | 值 |
|---|---|
| 模板 | `云南省财政厅集中运维体系建设项目（1标段）详细设计说明书-模板V1.0(1).docx` |
| 代码根 | `D:/workspaces/itom-base` · `D:/workspaces/itom-maintenance` · `D:/workspaces/tdma-monitor` |
| 分节清单（切片） | 2 节：`3.1.2 补充：实时监控`（六段式）· `3.4.3 补充：内部调用目录 › T-3 内部调用表` |
| 交付形态 | `markdown` |
| 上游依赖检测 | **模式 C · 降级模式**——`.tribro/` 存在但**无可用快照**（无 `LATEST.md`）⇒ 按 `SKILL.md §上游依赖检测` **原样声明降级**后推进 |

降级声明（照录 skill 契约原文，未改写）：

> 未检测到 tri-intent 快照，已进入降级模式：本次基于自构造输入执行，输入校验精度低于标准链路，
> 模板分节归属与编号体系的判定可能存在偏差，建议后续安装 tri-intent 以获得完整效果。

### 11.3 五阶段产物（实测落盘）

| 阶段 | 产出 | 落盘 / 结果 |
|---|---|---|
| ⓪ 版本检查 | 状态 **A · 一致** | `check_update.py --slug code-design-doc` → 退出码 **0** |
| ① 模板解析 | 骨架：6 章 / 22 节 / 15 个「补充：」/ 6 张表 + 六段式 slot + T-3 五列列序 | `.tribro/design-doc/outline.json` |
| ② 代码取证 | 证据台账 `EV-001…EV-019`（19 条） | `.tribro/design-doc/evidence-ledger.md` |
| ③ 分节填充 | 3.1.2 六段式 + T-3 三行表 | `.tribro/design-doc/pilot-20260928/…-20260928.md` |
| ④ 证据门禁 | 门①–门④ 逐条判定与回炉记录 | `.tribro/design-doc/gate-report.md` |
| ⑤ 回填交付 | 交付形态 `markdown` ⇒ **不写模板副本** | 本文件 §十一 |

### 11.4 阶段④ 门禁实测（禁手写，脚本输出）

```
断言=16 有锚=14 覆盖率=0.8750 [待确认]=2 占比=0.1250
T-3 数据行=3 裸编号=[]
```

| 门 | 判定 | 依据 |
|---|---|---|
| 门① 输入齐备 | ✅ PASS | 模板可解析；三代码根可读非空，实测 `*Controller.java` **348** · `*ServiceImpl.java` **441** · `/monitor/` 下 `.java` **1250**（监控域 Controller **95**）；分节清单非空 |
| 门② 证据完备 | ✅ PASS | **段级零锚 0 个**（模块定位 2/2 · 角色与前置 1/2 · 输入项 2/2 · 处理逻辑 4/4 · 输出项 2/3 · 第 6 段 3/3）；`U/T = 2/16 = 0.125 ≤ 0.5` |
| 门③ 编号一致 | ✅ PASS | 无上游编号来源 ⇒ `INT-001…003` 全部标 `[编号待校准]`，**零自造编号**；切片内无 `图/表 x-y` 引用，模板噪音号段 `图4-3`/`表4-1` **未沿用** |
| 门④ 回填确认 | ✅ PASS（自动放行） | 交付形态 `markdown` ⇒ G-4-1 不触发；G-4-2 范围纪律通过（产物章节集合 ⊆ 模板既有 ∪ 分节清单，字段名/列序原样） |

**回炉 0 轮** ⇒ 直接进入阶段⑤。

### 11.5 试点暴露的两条真发现（未美化）

| ID | 发现 | 证据锚 | 判定 |
|---|---|---|---|
| EV-008 | 告警状态定时任务 `MonitorAlertStatusTask` **整段被注释**（含 `@Scheduled(cron = "0/5 * * * * ?")`）⇒ 代码中存在的 **5 秒级状态刷新当前不生效** | `itom-maintenance/…/monitor/portal/task/MonitorAlertStatusTask.java:46` | `conflict`（设计存在 / 运行禁用） |
| EV-007 | `MonitorAlertRuleCheckSchedule` 的 `@Scheduled(fixedDelay = 5 * 60 * 1000)` **处于注释态**，改由 `interruptPause()` 供外部触发 | `itom-maintenance/…/monitor/MonitorAlertRuleCheckSchedule.java:29`、`:30` | `partial`（类已实现，调度未启用） |

> 两条均为「**按设计意图填**」与「**按代码实况填**」的典型分歧点。契约取后者：
> 交付文档描述**可运行系统的实况**；设计态与实况不一致记 `conflict` 并显式报告，
> `MUST NOT` 把注释态任务写成「每 5 秒刷新」。

### 11.6 试点暴露的台账缺陷（3 处，已收口）

首轮实测发现台账与文档**两侧数量不一致**（**文档侧无误，缺陷在台账侧**）：

| # | 缺陷 | 根因 | 修正 |
|---|---|---|---|
| 1 | 台账 §一 仅 15 行，漏「模块定位」第二条断言（范围排除项） | 采集时把「本模块**不含**巡检任务/计划调度、不含错误信息台账」并入 `EV-001` 摘要，未独立成行 | 补录 `EV-019`（锚 `InspectionItemController.java:39`，`confirmed`）；试点期不重编既有 EV 号，补录于 §一 表末并加注 |
| 2 | 台账 §一 **字面锚仅 12 处** < 判定锚 14 | `EV-014` 采回指写法「同 EV-006（`:65`、`:58`）」，可回溯但无显式 `file:line` | 展开为显式锚 `ApmRulesManageController.java:65`（`@PutMapping`）、`:58`（`@DeleteMapping`）；**语义不变，仅去回指** |
| 3 | 「取证纪律执行记录」总数过期（18 条 / 16 有锚） | 台账增行后未同步 | 改为 **`EV-001…EV-019` 共 19 条，其中 17 条有 `file:line` 锚，2 条无锚（EV-003 / EV-012）** |

**沉淀口径**：台账每行 MUST 至少携带**一个显式 `file:line` 锚**；跨行回指（`同 EV-xxx`）仅可作为**补充**。

### 11.7 阈值裁定：**不引入全局锚覆盖率阈值**（试点的核心产出）

本切片实测覆盖率 **87.5%**。G-2-1 维持「**段级零锚即 FAIL**」而**不**改成「全局覆盖率 ≥ X%」，理由由本次实跑给出：

- 真实仓库中「**使用角色定义**」（EV-003）「**界面刷新间隔**」（EV-012）一类断言**天然无后端锚点**（属配置 / 前端行为）；
- 若设全局阈值（如 ≥90%），会把**合规产物误判为 FAIL**；
- 段级判据（每段 ≥1 锚）恰好把「整段没证据」这一真实风险挡住，同时容忍段内个别无锚断言（按契约标 `[待确认]`）。

即：**本次端到端试跑的主要价值，是为「段级而非全局」这一判据设计提供了实测支撑，而非推翻它。**

### 11.8 §十 遗留状态更新

| §十 序号 | 原状态 | 现状态（2026-09-28 收尾） |
|---|---|---|
| ① 🟠 `tri-forge` P2≠P1 漂移 | 待取证 | **已闭环**。取证：1.0.6→1.2.0 四轮声明的变更**逐条在树内**——check-24 四处 `advisory=False`（`compliance_check.py:607/615/621/626`）、checklist `24/24` 与「两条均为必检」、battery `M-24-a…f`、`_sealed` 含 `FAIL:24`、`change-acceptance-gate.md` / `case-battery-spec.md` / `acceptance_diff.py` / `battery_run.py` / `mutation-gate.py` 均在 ⇒ 真值 = **1.2.0**。处置：**就地重定向** `dw2-tri-forge-version`（1.0.5 → 1.2.0），未新增纠错 op；`version-lint.py` → 检查 35 个 skill / **漂移 0** / EXIT=0 |
| ② 🟡 `WORKFLOW-GUIDE.html` G3 未收录 | 待裁定 | **维持现状**（口径自洽：指南自我限定「本仓库 26 个 skill」，而本 skill 属**平台用户级**）；如需补 I10 第四子类入口，另开提案 |
| ③ 🟢 未 commit | 待放行 | **已 commit** `ec9d094`（16 files changed，+489/−30；工作区干净）；**未 push**（push 单独放行） |
| ④ 🟢 未跑端到端 | 待跑 | **已完成** —— 即本节 §11.1–11.7 |

### 11.9 试点新登记的 skill 修订待办（下一批，尚未实施）

| # | 目标文件 | 内容 |
|---|---|---|
| 1 | `references/evidence-gate.md` | 追加台账锚口径：每行 MUST ≥1 **显式** `file:line` 锚，回指仅作补充 |
| 2 | `references/template-structure.md §1.4` | 模板噪音清单补一条：模板「补充：」小节的**示例业务正文（账号管理）与本章无关**，采集阶段 MUST 剥离 |
| 3 | （与 1 配套）`scripts/` | 后续若引入台账校验脚本，MUST 以**显式锚**计数，**不得**把回指计入 |

> 上述 3 条**尚未写入 `code-design-doc` 包**（该包为本批新增，改动需走下一批 patch 流程）。本节仅为登记。

## 十二、试点收尾：U3 归零 + U1 归因（2026-09-28 续）

> 承接 §11.9，试点执行完毕后的**收尾轮**。本节结论均为一手实测，产物回执见交付项目
> `.tribro/design-doc/gate-report.md`（§五 U3 收口回执 · §六 U1 归因）。

### 12.1 U3 裁定执行（清全文高亮）

| 步 | 动作 | 规模 | 回执 |
|---|---|---|---|
| U3-1 | `doc_update_text_property` 清正文 **run 级**黄高亮 | 54 段 | `update_text_property ok` |
| U3-2 | `doc_set_table_cells`（`common_cell_properties.text_format.highlight="none"`） | 6 张表 / 202 单元格 | `set_table_cells ok` ×6（version 2→7） |
| U3-3 | `save_file` | — | `File saved to: …-20260928.docx` |

**双通道终态**

| 通道 | 判据 | 结果 |
|---|---|---|
| editor_sdk | 6 表 202 单元格 `text_property.highlight` | **0** 非 none |
| editor_sdk | 309 结构节点 `text_format.highlight` | **0** 非 none |
| XML 直读 | 表格内含 **run 级** yellow 单元格 | 202（模板）→ **0** |
| XML 直读 | 全文 **run 级** yellow | 654（模板）→ **4**（模板自带图形占位 run，无 `<w:t>`） |
| XML 直读 | 全文 **pPr 级** yellow（¶ 不可见） | 313（模板固有） |

### 12.2 口径缺陷纠正（本轮最重要的方法论产出）

首轮复核曾报「201 个单元格仍带黄底 / run 级 yellow=4」，据此判定 U3 **未达标**。经查为**统计口径缺陷**：

1. **正则越层**：判据用 `<w:tc>.*?</w:tc>` 内是否出现 yellow 字符串 —— 该正则**同时命中单元格段落的
   `<w:pPr><w:rPr>` 段记层**（不可见），产生**假阳性**；
2. **互斥分支使对照不可比**：原件侧统计写成 `if run_hit: … elif ppr_hit: …`，run 级命中后永不进入 pPr 分支，
   得出「原件表格内 pPr = 0」的**假象**；非互斥重测后原件 = 201、现稿 = 201，**同一批、未增加**。

**正确口径**：按 `<w:r><w:rPr>`（**可见**，须归零）与 `<w:pPr><w:rPr>`（**不可见**，模板固有）
**分层且各自非互斥**统计。且 **表格是 `doc_resolve_document_structure` 的盲区**（其段落节点不展开单元格），
表格内高亮 MUST 另以 `doc_get_table_info` 或 XML `<w:tc>` 分层复核。

⇒ **U3 实为已完成** ——「未达标」是判据缺陷，非真实残留。此教训已固化为 skill 的 **W-9**。

### 12.3 U1 归因：**推翻「外部服务故障」定性**

首轮把 `doc_to_image` 失败定性为「外部服务故障，非文档问题」。本轮对照实验**推翻该定性**：

| 序 | 被转换文件 | 结果 |
|---|---|---|
| ① | **原模板**（未编辑，315579 B） | 服务侧**成功**写出 **31 页** PNG（仅 RPC 客户端读超时） |
| ② | **本稿**（354136 B），与①**背靠背同批** | `437009 DOC 转 PDF 失败` |
| ③ | **本稿**，独立重试 ×3 | `437009` ×3，稳定复现 |
| ④ | **未编辑副本**（pre-fill 备份，同源） | `50000 服务繁忙`（**限流闸门，未进入转换**） |
| ⑤ | **本稿**，紧随④ | `437009`（**已通过上传**，在转换阶段失败） |

**判读**：② 为同批背靠背 ⇒ 差异必来自文件；⑤ 中未编辑副本被挡在限流闸门、本稿获准入队**并进入转换阶段失败**
⇒ 服务对两者**区别对待**。累计 **6+ 次 `437009`**，跨两个时间窗稳定 ⇒ **排除偶发，本稿特异**。

**关键区分（skill 已固化）**：

| 失败码 | 阶段 | 性质 |
|---|---|---|
| `50000 服务繁忙` | `upload_credential` / 入队 | **服务侧限流**，与本文件无关 |
| `437009 DOC 转 PDF 失败` | `convert/doc_to_images` | **可能本文件特异** ⇒ MUST 做三文件对照实验再定性 |

### 12.4 根因线索：`save_file` 会**整包重写** docx（有损）

`editor_sdk` 保存**不是**原位替换 `document.xml`，而是用自有序列化器重建整个包。实测差异（模板 → 本稿）：

| 项 | 模板 | 本稿 |
|---|---|---|
| 部件数 | 36 | **31**（丢 `customXml/item1.xml` + `itemProps1.xml` + 其 rels、`docProps/custom.xml`、`word/webSettings.xml`） |
| `word/media/*` | image1=9705B … | image1 **丢失**、image4 **重复** ⇒ 重编号失真 |
| `word/header1.xml` / `footer1.xml` | 9160 / 2863 | **3171 / 473** |
| `word/endnotes.xml` / `footnotes.xml` | 3128 / 3018 | **666 / 572** |

**完整性校验**：`.rels` **无悬空目标**、`[Content_Types].xml` **无悬空 Override**、`document.xml` **良构**
（`ElementTree` 通过）⇒ 包结构**合法**，成因在**序列化语义构造**，非引用完整性。

**剩余风险（如实报告）**：页眉/页脚/尾注等**版式附属件**可能在重写后失真；
**正文内容**（六段式 / 编号 / 表格数据）已双通道核验**无残缺**。
**阻断**：进一步变异定位被限流（`50000`）阻断，待换时段重试。
**可选根治**：改走**原位 OOXML 改写**（保留原包结构）⇒ 属独立方案，需另立 proposal。

### 12.5 skill 侧修订（`code-design-doc` 1.1.0 → **1.2.0**）

| 文件 | 变更 |
|---|---|
| `references/docx-writeback.md` | **新增 W-9**（高亮分层 + 表格盲区 + 两个假判定陷阱）、**W-10**（整包重写有损 + 回填前转图留底纪律）；**重写 W-8**（删去「一律外部服务故障」的错误定性 → 两码区分 + 三文件对照实验规程） |
| `SKILL.md` | `version: 1.2.0`；§四速查表 **3 → 5** 条（补 W-9 / W-10） |
| `CHANGELOG.md` | 新增 `[1.2.0]` 条目（含实测证据表与口径纠正） |
| `README.md` / `_meta.json` | badge 与版本同步至 1.2.0 |

**版本门**：`scripts/check_update.py` → **A 校验通过 / 本地 P1–P5 五处一致 / RC=0**。

### 12.6 遗留（更新 §十 / §11.8）

| 项 | 状态 |
|---|---|
| §11.8 ③ 未 push | **仍未 push**（本地 2 个 commit：`ec9d094` + `bb3166f`；本节的 commit 追加为第 3 个）——push 由用户单独放行 |
| U3 范围外高亮 | 🟢 **已闭环**（按裁定执行，双通道归零） |
| U1 视觉转图 | 🟡 **重新定性为本稿特异转换器不兼容**；进一步定位待限流解除；根治（原位 OOXML）需 proposal |
| §11.9 三条 skill 待办 | 未变，仍待下一批
