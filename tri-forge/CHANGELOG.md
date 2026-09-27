# 变更日志

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

> **一致性硬约束**：本文件首个 `## [x.y.z]` MUST 与 `SKILL.md` frontmatter 的 `version` 相等，
> 且 MUST 为本文件的最大版本。违反即触发门④ 第 11 条 FAIL。

## [1.2.0] - 2026-09-27

> 来源：用户裁定 T3=A「修完即升，作守门员」。proposal：工作区 `tri-forge-handoff/PROPOSAL-d24-promote-to-mandatory.md`（`Approved: yes`）。
> **前置（阶段 1 · v1.1.1）全部满足**：元级用例 `M-24-a…f` 6/6；全家族第 24 条 **5 PASS / 21 N-A / 0 FAIL**；第 23 条 26/26 不回归；门④.5 翻转 5 条 / 未变 14 条零误报 / B1·B2·B3 全过。

### 变更（判据强度）

- **门④ 第 24 条「评估产物含案级结构化结论」由建议项升为必检**（`scripts/compliance_check.py` 四处 `add(24, …)` 的 `advisory` 由 `True` 改 `False`，条目标题去掉「（建议项）」）。
  效果：#24 FAIL 由「计入建议改进项、不阻断」变为 **门④ 总判 FAIL ⇒ 回炉门②**。
- `references/compliance-checklist.md`：第 24 条去掉〔建议项〕标记；§五 强度说明改为「两条均为必检」；判定记录格式的汇总口径 `23/23` → **`24/24`**，删去「建议项不阻断」括注。

### ⚠️ 性质变化（已随判据正文入库，MUST 与「已淘汰候选判据」区分）

- 修正后本条**存量 0 FAIL**，作用变为**守门员**——只在**未来新增** skill / 新增评估产物时生效。
- 与 v1.1.0 淘汰的两个候选判据（「真源声明标注」82% FAIL、「阈值扩散」45% FAIL）**性质不同**：那是「**判据测不出差异**」⇒ 无效；本条是「**标准已被家族达成**」⇒ 有效，但只在增量上生效。
- **升必检的正当理由不是「能抓出 5 个坏包」（那 5 个已取证证明是误报），而是「把一条已被普遍满足的标准固化为不可回退的下限」。**

### 测试

- `tests/battery/battery.json` + `_sealed/eval-expect.json`：**M-24-f 期望重戳** `PASS+adv24` → **`FAIL:24`**（强度变更的可观测证据）。
- `tests/tri-forge-full-testcases.md`：T27 由「建议项不阻断」改为「必检 ⇒ 阻断」；T37 补记 token 两态。**未新增用例号**（同一注入的强度差异已由 M-24-f 的 token 形态机械承载，避免无谓重编号）。

### 验收

- 门④ 全家族：必检项 FAIL **0**；第 24 条 5 PASS / 21 N-A。
- 第 24 条**阻断态实证**：M-24-f 夹具下 `#24` FAIL ⇒ 门④ 总判 FAIL。
- 电池 19/19 与（已重戳的）期望一致；`check_registry --check` 漂移 0；`tests/mutation-gate.py` 7/7 且真实文件 md5 未变。
- 门④.5（1.1.1 → 1.2.0）：机械检出 M-24-f 的 token 形态变化。

## [1.1.1] - 2026-09-27


> 来源：用户裁定「先修判据再谈升必检」（T1=A）。
> 上游审计：工作区 `tri-forge-handoff/D24-PRECONDITION-AUDIT.md`；proposal：`tri-forge-handoff/PROPOSAL-d24-criterion-fix.md`（`Approved: yes`）。
> **动机**：v1.1.0 把第 24 条定为建议项时，26 对象实测 5 个 FAIL；本轮对 5 例做逐包 `file:line` 取证，
> 结论是 **5 例全部不可信**（3 例误报 + 1 例双向误判 + 1 例设计取舍），**无一存在实质缺口** —— 不得为此改 5 个生产 skill。

### 修复

- **第 24 条判据三层缺陷**（`scripts/compliance_check.py` check-24）：
  - **F-a 适用性闸门过松**：文件级「提到即算」，`CHANGELOG.md` / `tests/` / README 目录树 / frontmatter 全被当作「schema 定义」（`tri-evolve` 7 处命中里 6 处是噪音）→ 改为**只认结构化产物定义区块**（SQL DDL / 真表头字段表 / 内联字段枚举）+ 排除清单 + **产物语境白名单**。
  - **F-b 共现粒度错**：文件级 AND 不要求同区块（`tri-review` 的 frontmatter `ledger` 与相隔 77 行的输入表仍被判命中）→ 改为**同区块共现**。
  - **F-c 词表过窄 + 口径/实现不一致**：不认 `spec_id` / `testId` / `lesson_id` / `proposal_id` / `检查项`；`EVAL_PRODUCT` 只写「台账」漏「**账本**」→ tri-review 真 schema（`references/review-checklists.md` §5）**整体漏检**。已补同义形态。
  - **F-d 假表头**（修正过程中新发现）：数据行因含「检查项」被当成字段表表头 ⇒ 误报 `tri-sdlc` → 字段表 MUST 从其**真表头**（后随分隔行 `|---|`）开始。
- **第 24 条 N-A 新增一态**：账本**仅按聚合维度**（轮/批次/时间）落账且包内声明了守卫/单调性用途 ⇒ `N-A` 并附理由（`tri-req-audit` 的 `round-ledger.jsonl` 属此列：按轮聚合是**守卫型账本**的刻意设计，案级维度在报告侧）。

### 新增

- **元级判据用例 `M-24-a…f`**（`tests/battery/`，`split=eval`，期望封存于 `_sealed/eval-expect.json`）：
  正例 3（DDL `case_id`+`verdict` / 英文案级键 `test_id`+`status` / 中文「账本」`检查项`+`结论`）、
  负例 2（`CHANGELOG` 噪音 / 提及≠定义）、反例 1（有案级键、**无结论字段** ⇒ MUST `FAIL`）。
  **存在理由**：仅凭「26 个对象变绿」无法区分「判据修对了」与「判据被调到刚好放过这 26 个对象」——
  这是 `case-battery-spec.md` 的 `search/eval split` 纪律在**判据自身**上的应用。**新增 6 条用例（电池 13 → 19）。**

### 变更

- `references/compliance-checklist.md`：第 24 条判定口径全文重写；§〇 追加**校准记录（2026-09-27 · 第 24 条二次校准）**，含 5 例裁定表、三层根因、修正后结果与**已知边界（诚实声明：适用性系文本启发式推定，残余误判方向以漏判为主）**。
- `tests/battery/battery.json`：**C-006 / C-007 / C-008 期望重戳**（`baseline-frozen`）——三者的 `+adv24` 收敛为 `PASS`，正是本次修正的直接效果。
- `tests/tri-forge-full-testcases.md`：**章节号与用例号修复**（v1.1.0 插入电池章节时造成的 §四/§五 重号与 T26–T29 重复）；新增 T35–T37（元级判据用例）。用例总数 → 42。

### 验收

- 门④ 全家族 26 对象：第 24 条 **5 PASS / 21 N-A / 0 FAIL**（逐条人工复核全部为真命中）；必检项 FAIL 0。
- 元级判据用例 **6/6** 与 `_sealed` 期望一致。
- 电池回归 19/19；第 23 条不回归（26/26 PASS）；`check_registry --check` 五处版本位点漂移 0。
- 门④.5：v1.1.0 判据脚本（快照）与 v1.1.1 对同一份 19 条电池各产一次台账 → 机械判定。

## [1.1.0] - 2026-09-27

> 来源：用户裁定「①②③ 全批 + 第 23 条必检 / 第 24 条建议项 + 电池试点取 tri-forge 自身门禁」。
> proposal 存工作区 `tri-forge-handoff/PROPOSAL-v1.1.0-batch-gate-battery-deffix.md`（`Approved: yes`）。

### 新增

- **case 电池子系统**（门④.5 的输入真源）：
  - `references/case-battery-spec.md`：电池判据单一事实源 —— case schema、**search / eval split 纪律**、`_sealed` 封存、与门④.5 的接口契约、裁决 token 口径、新增 case 的零改动路径、5 条已知边界。
  - `tests/battery/battery.json`：电池单一事实源，**13 条 case**（search 8 条真实家族包 + eval 5 条反例夹具），每条带 `expected` / `ratification`（`by-design` 或 `baseline-frozen`）/ `basis`。
  - `tests/battery/fixtures.json`：夹具以「基准包 + **单点 op**」的 delta 形式定义，运行期物化到临时目录 —— 体积恒定，且**不在 skills 树内落 `SKILL.md`**（避免被 skill 发现机制误加载）。
  - `tests/battery/_sealed/eval-expect.json`：eval 组期望封存，**仅在变更验收时读**，执行体禁读。
  - `scripts/battery_run.py`：跑电池 → 产**案级台账**，直接喂 `acceptance_diff.py`，无需转换层。`--split eval|all` **必须**与 `--i-am-accepting` 同时出现，否则拒绝执行。
- **门④ 判据 22 → 24 条**（两条均为三轮 pilot 的实测产物，非上游条文，也非凭实测共性推定）：
  - **第 23 条 · 规范性判据单一事实源**（**必检**）：包内自引用指针 MUST 可解析，解析顺序为「skill 目录 → **仓库根兜底**」（跨 skill 引用属合法形态）。证据：pilot1 —— A/B 验证门被重述在 **7 个**文件/产物（含 `scripts/` 代码硬编码），文本变异无法撼动行为。
  - **第 24 条 · 评估产物含案级结构化结论**（**建议项**）：评估产物 schema MUST 同时含**案级键**与**结论字段**。证据：pilot2b —— 保住「案级」这个结构单位时诊断 recall **40% → 100%**，成本仅 1/17（~3.8 KB vs 65 KB）。
  - 上线前对 **26 个家族对象 + 23 个第三方对象**做只读实测校准；**淘汰两个零区分度的候选判据**：「指针段落须含真源声明词」（34 个适用对象中 28 FAIL，**82%**）与「同一阈值字面量出现于 ≥3 个文件」（33 个中 15 FAIL，**45%**，命中物多为 CHANGELOG 记录与测试断言）。

### 修复

- **`tests/mutation-gate.py` D1（计数不对称致退出码恒为 1）**：`caught` 把**基线行**计入（基线 verdict 恰为 `✅ PASS`），而 `total` 显式排除基线 ⇒ `caught=7 ≠ total=6` ⇒ `sys.exit` **恒为 1**，脚本永远报失败。改为**只对注入用例计数**，基线单独断言。
- **`tests/mutation-gate.py` D2（穿透 junction 实际改写真实 skill）**：`find_repo_root` 经 `Path.resolve()` 穿透 junction 落到真实仓库，脚本**直接写** `tri-coding/SKILL.md` 与 `CHANGELOG.md` ⇒ 跑 tri-forge 的测试会静默改动兄弟 skill，**中途中断会留下注入态**。改为：① 变异只在 `tempfile` 副本上进行（`compliance_check.py --dir <副本>`）；② 运行前后对真实 skill 关键文件做 **md5 自证**，不一致即判 FAIL；③ `find_repo_root` 加前置守卫（须同时存在 `.git` 与 `tri-forge/scripts/compliance_check.py`），定位失败退出 `2` 并**永不回退到「就地变异」**。同时新增 M7 用例（制造断链自引用指针 → `#23` 应翻）。
- **`scripts/acceptance_diff.py`（干净 case 被误判作废）**：`clauses` 为空被当「字段缺失整条作废」，误伤**全 PASS 的干净 case** —— 实测使 C-007（由干净变为带建议项失败）这条**真实翻转被漏记**，且错报为「两侧不齐」。改为：`clauses` 键 MUST 存在但**允许空列表**；防虚假填写改判「**token 声称 FAIL 而条款集为空**」（自相矛盾）才作废。

### 变更

- `scripts/acceptance_diff.py` 新增 `out_of_scope` claim（不参与 B1/B2，**MUST 附理由**）—— 用于「变更不在电池覆盖范围内」的诚实记账，NEVER 假装「无 case 翻转」；对未知 claim 值改报**告警**而非静默忽略。
- `scripts/battery_run.py` 台账新增 `skill` / `version` / `battery_version` / `gate` 字段，报告标题可显示「前版 → 后版」；新增 `--gate`（对比改前/改后两版门禁）与 `--attribute`（把 case 的结论变化机械归因到引入该条目的 op）。
- `scripts/compliance_check.py` 头部与输出文案 22 → 24；新增 `#23`（必检）与 `#24`（advisory）判定；被淘汰的候选判据的实测数据在位留档。
- `references/compliance-checklist.md` 22 → **24 条**：新增 §五（证据驱动约束 23–24），原 §五/§六 顺延为 §六/§七；§〇 补本次实测校准记录；§七（变更验收）中「本节不是第 23 条」的措辞随第 23 条设立而更新 —— 该节即第 23 条的**首个自证实例**。
- `references/family-spec.md` §二 登记「按需资产：变更验收电池」（**不强制**普通生成物）；§三 引用数与 §六 交付摘要计数同步。
- `SKILL.md` / `README.md` / `tests/tri-forge-full-testcases.md` 计数、结构树与门④.5 输入来源同步；五处版本位点 → `1.1.0`。

### 验收（本变更自身即门④.5 的首个真实用例）

`before`（v1.0.6 判据脚本，快照存 `%TEMP%/tf-v110/`）与 `after`（v1.1.0）对**同一份 13 条电池**各产一次台账 → 门④.5 机械判定：**翻转 3 条**（C-006 / C-008 / E-002）、未变 8 条**零误报**、B1/B2/B3 全过、`op-03`（mutation-gate 修复，超出电池覆盖）记 `out_of_scope` 并附理由。
完整报告：工作区 `tri-forge-handoff/v110-gate-report.md`；两份台账 `ledger-before.json` / `ledger-after.json`。

## [1.0.6] - 2026-09-26

### 新增

- **新增门④.5「变更验收」**（仅变更既有 skill 时触发；从零生成 / A 模式 / 纯字形调整判 `N-A`）：变更前后用同一套 case 电池跑**案级台账**，产出 `case_id | 前版条款集 | 后版条款集 | 翻转? | 方向 | 条款差` 表，可直接充当 changeset 的「哪些行为变了、因为哪条改了」一节。
  - **判据单一事实源**：`references/change-acceptance-gate.md`（新增）
  - **可执行实现**：`scripts/acceptance_diff.py`（新增；台账比对 + 三条硬门判定，退出码 `0` 全过 / `1` 阻断 / `2` 输入错误）
  - **三条硬门**：B1 声称行为变更的 op MUST 至少翻转 1 条 case；B2 标 `cosmetic` 的 op MUST NOT 翻转任何 case；B3 结论无差异的 case MUST NOT 入变更清单（结构性保证 0 误报）
  - **判定态**：`PASS` / `FAIL`（阻断）/ `INCOMPLETE`（判定不完整，**同样阻断**）/ `N-A`（不阻断，须声明理由）
  - **两条由实测确定的口径**：① 翻转判据 MUST 是结论本身（`verdict_token`），NEVER 是 `clauses` 字符串比对（同一节在两版常被引成不同粒度，会系统性误报）；② `evidence` 回验未命中只标 `unverified` 待复核，NEVER 因此作废整条。

### 变更

- `references/compliance-checklist.md` 新增「六、变更验收（另见）」节，**仅为瘦指针、不重述判据**；**22 条条目本身未改动**，本节不是第 23 条。
- `SKILL.md` §处理流程 增补门④.5 节点与说明；§模式总览 / §兜底处理 / §可扩展性 / §目录结构 同步更新。
- 门④.5 的**设计边界**已随判据文件一并声明：只判「行为有没有变」、不判「变好还是变坏」；依赖一份 case 电池且其 search / eval 两集 MUST 分离；**首选落地为「提示」而非「阻断」**，待电池成熟后再升级。

## [1.0.5] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.0.4] - 2026-09-24

### 变更

- **版本门节收敛为瘦指针 STUB**：`## 版本检查与更新机制` 由 35 行全量版收敛为 14 行（执行方式 + 真源指针），移除已失效的**远端 skillhub 内联细则**（端点解析 / 四态判定 / 升级流程 / SemVer 比较算法）。依据 `references/version-check-spec.md` §六（该节须 ≤30 行、禁内联细则）；本仓库已转自维护 fork（`scripts/check_update.py` 内置 `SELF_MAINTAINED = True`，完全跳过远端请求），原节描述的行为**永不执行**。
- **强制执行契约 §0 同步修正**：版本门措辞由「连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级」改为「运行 `scripts/check_update.py` 做本地版本一致性校验，本仓库为自维护 fork、不做远端比对」，消除 prompt 层与脚本实际行为的直接矛盾。
- 节内 **skill 专属职能**（`scripts/check_registry.py` 家族级 P1–P5 校验）原样保留，未被本次收敛影响。
- 非功能性变更（文档口径），无行为变更。

## [1.0.3] - 2026-09-24

### 变更

- **§1.5 登记表更新**：`evolve-hook` 实现状态由「❌ 未交付」改为「✅ pi（形态 B）已交付 · ❌ 形态 A/C 未交付」，并登记其入参契约。

## [1.0.2] - 2026-09-24

### 变更

- **新增 hook 依赖契约 `family-spec.md` §1.5**：声明即须给降级路径 + 登记 + 命名 + `hooks/` 目录名纪律；登记 4 个 hook（实现数 0）。`compliance-checklist.md` 第 14 条由「四类」扩为「五类」（含 hook 缺失）。

## [1.0.1] - 2026-09-24

### 变更

- **分支收窄为编程工作流专线（22 skill）**：清理对已移除 skill 的交叉引用——职责边界表 / 不由本 skill 处理表的对应行改为「本分支未包含（原 tri-xxx）」或删除；已删的委派关系与相邻边界说明同步失效。非功能性变更（文档）。

## [1.0.0] - 2026-09-23

### 新增

- **首版发布**：三模式技能锻造工具（A 规范顾问 / B 补全审计 / C 锻造生成）
- **五门流程**：门① 需求确认 → 门② 骨架生成 → 门③ 路由回流 → 门④ 合规自检 → 门⑤ 落盘交付
- **家族硬规范单源**：`references/family-spec.md`（骨架清单 + 12 条家族硬约束 + 章序表 + 待登记项）
- **22 条合规核对清单**：`references/compliance-checklist.md`（12 家族 + 8 增强 + 1 安装 + 1 版本检查去重）
- **门④ 可执行实现**：`scripts/compliance_check.py`，逐条判定并明确标出 `MANUAL` 项
- **门③ 路由回填规则单源**：`references/tri-intent-integration.md`（含回填顺序与优先级仲裁）
- **五点版本一致性校验**：`scripts/check_registry.py`（`--check` / `--apply`）
- **三方模板**：`templates/skill-md.md` / `readme.md` / `changelog.md`
- **测试用例**：`tests/tri-forge-full-testcases.md`（含 22 条硬约束自检用例）

### 设计取舍

- **不注册为 tri-intent 下游**：定位为内部专用工具，由用户直接调用（与原上游设计一致）
- **承接而非重建版本校验**：五点校验规则与 `ops/version-lint.py` 同源，但保留自有副本以保证独立安装
- **P2 不代写**：`CHANGELOG.md` 首条属人工内容，`--apply` 只规则化回写 P3 / P5

### 来源说明

本 skill 系**自维护 fork 自行重建**。上游作者将其私有化：上游 `.gitignore` 显式排除 `tri-forge/`，
平台 `/api/v1/skills/tri-forge` 与 `/api/v1/download?slug=tri-forge` 均 404，
作者名下全量 skill 枚举中亦无此 slug。重建依据为仓库内 `tri-mece-audit/tri-mece-audit.html`
记录的规格（定位、职责边界表、四分支触发、三模式、五门流程、门④ 22 条约束来源、自检句格式）。
