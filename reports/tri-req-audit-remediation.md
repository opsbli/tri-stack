# tri-req-audit · 遗留 5 项整改闭环报告

> **性质**：`reports/tri-req-audit-forge.md`（2026-09-25 锻造交付摘要，**时点快照、已冻结**）的**跟进整改**记录。
> 因锻造报告属时点结论，本报告**不改写它**，而是另立一份对账。
> 触发：用户「遗留 5 项怎么整改？」→「按此顺序修」（批准 P0→P4 依赖序）。

---

## 一、结论（先行）

| 项 | 结果 |
|---|---|
| 原遗留 5 项 | **全部闭环**（🟠 2 → 0；🟡 3 → 0） |
| 终局回归 | `apply.py` ×2 幂等 ｜ `version-lint` / `check_registry` **EXIT=0** ｜ 门④ 25 对象 **9 FAIL（与改前同一集合）** ｜ `tri-req-audit` 门④ **FAIL 0**、版本门 `state=A` |
| 补丁层 | op **28 → 30**（新增 `f18` / `f19`），两 op 均已收敛为「已应用」 |
| 新发现 | **2 项**（🟠 1 / 🟡 1），**本轮未修**，见 §七 |
| 待放行 | **1 项**：`tri-req-audit` 尚未 junction 安装（工作区外全局状态） |

**执行序（未倒置）**：

```
P0 固化工作区（并行写入探测 + 备份 + 指纹索引）
 └─→ P1 项5（脚本去重）+ 项2（family-spec 规则）      ← op 28 → 30
      └─→ apply.py ×2（幂等）+ 行为等价双证明
           └─→ P2 项1（计数对账）                    ← 依赖 P1 后的最终 op 数 30
                └─→ P3 项3（GUIDE 收录）             ← chip 版本须先定稿
                     └─→ P4 项4（--emit-baseline）   ← 最后快照全部版本
```

---

## 二、原遗留 5 项对账

| # | 原报告项 | 原严重度 | 处置 | 判据 / 证据 | 状态 |
|---|---|---|---|---|---|
| 3 | 补丁层自述中的计数在语义上失真 | 🟠 | **P2**：当前态账本 11 处改数；带日期记录**冻结**并加增量注记 | manifest 内已无残留过期计数（`顶层 24 / 当前 33 / 34 份 / 23 个 op` 全零命中） | ✅ |
| 4 | `family-spec.md` §1.4 未登记 `coding/` | 🟠 | **P1**：op `f18`。⚠️**结论反转**，见 §三 | §1.4 连跑三次 `应用 1 → 已应用 1 → 已应用 1` | ✅（改用另一种口径） |
| 1 | `WORKFLOW-GUIDE.html` 未收录新 skill | 🟡 | **P3**：15 处（计数 7 + 收录 7 + 命名卡同步 1） | `version-lint --apply-docs` 两次 **0 处修正 / EXIT=0** | ✅ |
| 2 | `ops/versions.json` 基线未含新 skill | 🟡 | **P4**：`--emit-baseline` | 33 → **34** 条目；`tri-req-audit=1.0.0`；**顺带修掉既有漂移** `tri-review` 1.6.2 → 1.7.0 | ✅ |
| 5 | `compliance_check.py` 重复代码块 | 🟡 | **P1**：op `f19` 删重复块 | `old` 命中**恰好 1 次**；保留处注释加注使 marker 成立；行为等价双证明见 §六 | ✅ |

> 原报告 §五「安装评估」另有一条现状记录（用户级落点尚未创建），**不在 5 项之内**，见 §八。

---

## 三、关键自我纠正：原报告 #4 的建议被否（重要）

### 3.1 原建议与我的首版实现

原报告 #4 的判断是：§1.4 判据为「可推导」，但 `coding/` 由三 skill 共写而豁免清单未登记 → **建议「补充登记 `coding/`」**。
我首版照此实现为规则：**「共享性优先 —— 任一目录由 ≥2 skill 写入即落入豁免行，MUST 登记」**，并登记 `coding/`。

### 3.2 为什么这是错的（级联）

| 目录 | 写方 | 首版规则下的后果 |
|---|---|---|
| `coding/` | `tri-coding` / `tri-prototype` / `tri-orchestrate` | 已登记 |
| `sdlc/` | `tri-sdlc` + 9 个子 skill | **也须登记**，但原清单没有 |
| `forge/` | `tri-forge` + `tri-lottie` | **也须登记**，但原清单没有 |

⇒ 该规则要求**新增 2 处登记**，而原清单只有 2 行 —— 修正引入的**不一致比原缺口更大**。

### 3.3 正确判读的线索（在下游文档里）

| 证据 | 内容 |
|---|---|
| 原豁免清单两例 | `snapshots/`（← `tri-intent`）、`skills/`（← `tri-forge`）—— **恰恰都不可推导** |
| GUIDE 的「通过」清单 | `coding/` 本就列在「可按 skill 名推导」一行 |
| §1.4 首句 | 「**判据只有一条**：目录名能否从 skill slug 机械推导」—— 共享性从未被定义为判据 |

⇒ 语义应为：**可推导性优先**；豁免只是「**共享 ∩ 不可推导**」这一交叉情形的处置（因改名要动多个调用方，故须登记留痕）。

### 3.4 纠正后口径

| 情形 | 处置 |
|---|---|
| 可从 skill 名推导（**任一写方**即可） | ✅ **通过** —— 共享但可推导者同此，**无需登记**（`coding/` / `sdlc/` / `forge/`） |
| 由多个 skill 共享 **且不可推导** | ✅ 豁免（须在下表登记）—— `snapshots/` / `skills/` |
| 不可推导 **且单一写方** | ❌ MUST 改名 |

- 豁免清单**仍为 2 行**，各行补「**不可**由 X 推导」依据（防止再次被判为遗漏）。
- 判定顺序写明：`① 先判可推导性 → ② 仅当不可推导时再看共享性`。

### 3.5 落地手法（为何不留孤儿纠正 op）

错误版本**从未 commit**（仅存在于工作区）。因此采用：

1. 把 §1.4 **还原到 `f18` 之前**；
2. 就地改正 `f18` 的 `new` / `already_marker` / `label`。

⇒ 当前树与「全新 clone / 升级整树替换后」的树，**由同一个 op 正确产出**，不需要额外纠正 op。

---

## 四、P2 计数对账：实测真值

> 口径：一律以**本仓工具回执**为准（`compliance_check --all` 对象数 / `check_registry --check` 报数 / op 自身 `跳过 N`），不采信文档自述。

| 计数 | 文档旧值 | 实测值 | 佐证 |
|---|---|---|---|
| 顶层 skill | 24 | **25** | `compliance_check.py --all` → 审计对象 25 |
| 校验覆盖（顶层 + `tri-sdlc/children/*`） | 33 | **34** | `check_registry.py --check` → 「检查 **34** 个 skill」 |
| `version-check-spec.md` 份数 | 33 | **34** | `spec-per-skill` op 实测 `跳过 34` |
| `check_update.py` 份数 | 34（33 + 1 payload） | **35（34 + 1 payload）** | 34 份 skill 副本 + `assets/` 1 份，hash 仍全等 |
| 补丁层 op 数 | 23 | **30** | `manifest.json` |
| `converge-version-stub` 顶层覆盖 | 24 | **25** | 该 op 实测 `跳过 25` |
| `f13-check-update-decouple` 顶层覆盖 | 24 | **25** | 该 op 实测 `跳过 25` |

### 4.1 处置三分法

| 类别 | 判据 | 处置 | 处数 |
|---|---|---|---|
| **当前态账本** | 描述「此刻仓库/工具形态」：目录树注释、命令示例、当前清单表、label、章节计数 | **改数** | **11** |
| **时点记录** | 落在带日期标题下、或本身是**实测输出引文**（`🔄 重建 24`、`写入 22｜跳过 2`）、事故记录 | **冻结**，只加日期增量注记 | 6 处引用 + 2 个增量小节 |
| **事实性失真（顺带发现）** | 陈述与实测矛盾，非计数问题 | **更正** | 1 |

### 4.2 改动的 11 处当前态

| 文件 | 处数 | 内容 |
|---|---|---|
| `ops/README.md` | 3 | 目录树（`versions.json` 33/24→34/25、`manifest.json` 23→30 op）、安装命令注释 24→25 |
| `ops/patches/README.md` | 3 | 「当前补丁清单」表：`spec-per-skill` 33/24→34/25、`converge-version-stub` 24→25、`f13` 24→25（并标注「首轮 22+2」保留原始回执） |
| `README.md`（根） | 6 | 分支说明、简介总数与分解（22+2 → **23+2**）、技能目录标题、`ops/` 树 2 处 |
| `ops/patches/manifest.json` | 2 | `f13` 与 `converge-version-stub` 的 label |

### 4.3 冻结的处数（**未改原数字**，仅加日期增量注记）

| 文件 | 位置 | 冻结理由 |
|---|---|---|
| `ops/README.md` | L85 分支收窄、L161 安装回执引文、L171 入口数、L173 版本节形态、L203 版本节远端口径、L204 基线重写 | 带日期条目 / 实测输出引文 |
| `ops/patches/README.md` | §锚点型注入事故（`43 份 ×3`、`覆盖 24 份`）、§自维护模式（`当前 24 份` / `2 种形态`）、§源形态取「去耦版」、§后续 f13 | 事故记录 / 当时实测快照 |

两文件各追加「**计数增量（2026-09-25）**」小节，集中列出现值 + 佐证，并显式声明上述条目为时点快照。
（理由：把「24」改成「25」或反过来，等于**伪造当时的结论**。）

### 4.4 顺带发现的事实性失真

| 位置 | 原文 | 实测 | 处置 |
|---|---|---|---|
| `ops/README.md` L224 | 「测试脚本在 `.workbuddy/_mutation-gate.py`（gitignore 目录内），**如需**纳入版本控制须迁到 `ops/` 或 `tri-forge/tests/`」 | `git ls-files` 确认 **`tri-forge/tests/mutation-gate.py` 已被跟踪** | 已改为「**已迁入版本控制**」；同页 L207 的 `tri-forge/`（15 文件）补注「迁入后为 **16** 文件」 |

---

## 五、P3：GUIDE 收录（分层定位与最小充分集）

**分层定位判据**：`tri-req-audit` 是**内部工具型**（`tri-intent` 全库**零引用**，非注册下游）+ **用户直调** + 服务 tri-coding **门②** → 归 **G4 全流程 / 协作对齐**（与 `tri-orchestrate` / `tri-grill` / `tri-domain` 同层，标 `直调`）。

| # | 位置 | 内容 |
|---|---|---|
| 1 | 头部 chip | `需求审核 tri-req-audit v1.0.0` |
| 2 | §02 **G4 分层** | cnt 4 → 5；chip `<b>tri-req-audit</b> <span class="v">1.0.0</span> <span class="v">直调</span>`；描述补职责 + 「先对齐、**再审核**、再拆解、后编码」 |
| 3 | 产物落点总表 | 「15 个编程资产」→ **16**；新增行（`G2 · 审核` → `req-audit/&lt;命名&gt;/`：report / fixes / delegation-receipts.json ｜ 真实成果物：无（只读不改）） |
| 4 | 关键衔接点 | 「五个」→ **六个**；新增 `tri-prototype → tri-req-audit → tri-coding 门②` |
| 5 | 命名基准卡 | 豁免补限定「共享**且不可推导**；可推导者即使共享也归通过 —— 如 `coding/` / `sdlc/` / `forge/`」（与 §1.4 纠正后口径对齐） |
| 6 | 轨道选择决策表 | 新增「这份需求文档 / PRD 能不能开工」→ `tri-req-audit`（直调） |
| 7 | `.tribro` 目录地图 | 新增 `req-audit/&lt;命名&gt;/` 行 |

另有**计数 7 处**（kicker / 副标题 / 2 个 chip / TOC / §02 标题 / 分支说明 / 版本门段）。

**验收**：`version-lint --apply-docs` 连跑两次均 **「无漂移」/ EXIT=0**（0 处修正）。
D1 检查天然覆盖新 chip —— 若 chip 版本写错，`--apply-docs` 会报漂移，故这是**有牙的验收点**。

**行尾**：byte 级探测确认 GUIDE 本就是 **CRLF**（此前用 `read_text()` 探得 `CRLF=0` 是**假象** —— text 模式会归一化）。
改后 CRLF 979 → **985**（+6 行），**无裸 CR**。

---

## 六、P1 判据有牙证明

### 6.1 `f19` 的两处机制性坑（本轮新发现）

| # | 坑 | 后果 | 修法 |
|---|---|---|---|
| 1 | `op_replace_text` **先判 marker 再判 old**（`if marker and marker in txt: already+=1; continue`） | 我原计划用 `role = "unknown"` 作 marker，该串**改前已出现 2 次** ⇒ op 被误判「已应用」而**永不生效** | 换标记策略 |
| 2 | **纯删除型修正不存在可用 marker**（已证明 post-fix 文本的**每个连续子串都已在 pre-fix 中**，含跨删除边界的接缝 `role = "unknown"\n\n    r = []` —— 改前 L169-171 本就存在） | 任何 marker 要么改前已存在、要么改后不存在 ⇒ **永不幂等** | 让 `new` **引入新文本**：保留处注释加注「单次赋值（去重后仅保留一处，勿再复制）」，兼作幂等标记 |

### 6.2 行为等价双证明

| 方向 | 方法 | 结果 |
|---|---|---|
| **正向** | `compliance_check.py --all --json` 改前 / 改后归一化比对；25 个审计对象覆盖全部角色分支 | **JSON 全等** ✅ |
| **负向** | 4 个定向 fixture：`fx-internal`（内部工具）/ `fx-unknown`（无关键词）/ `fx-downstream`（下游）/ `fx-noskill`（无 SKILL.md → error 路径）；改前脚本取自 `git show HEAD:tri-forge/scripts/compliance_check.py` | 逐目录 **JSON 全等**、退出码全同 ✅ |

### 6.3 幂等

| 轮次 | `f18` | `f19` |
|---|---|---|
| run1 | `应用 1｜已应用 0` | `应用 1｜已应用 0` |
| run2 | `应用 0｜已应用 1` | `应用 0｜已应用 1` |
| run3（终局） | 30 op、**两轮 applied 均为 0**、error 0 | — |

`not_found` 仅 `f3-clause-inline` / `f3-clause-sentence` / `f3-standalone-line` **3 个常驻项**（已知正常态）。

---

## 七、新发现（本轮未修，附证据与严重度）

| # | 项 | 证据 | 影响 | 建议动作 | 严重度 |
|---|---|---|---|---|---|
| 1 | **`compliance_check.py` 角色识别覆盖盲区** | 25 个顶层 skill 按仓内检测逻辑分类：root 1 / internal 6 / lateral 2 / downstream 8 / **unknown 8** | 角色决定 **#8（MECE）/ #20** 是否适用 ⇒ 这 8 个的判定建立在 `unknown` 分支上 | 复核 `tri-checklist` / `tri-code-analyzer` / `tri-fix` / `tri-frontend-design` / `tri-god` / `tri-html` / `tri-lottie` / `tri-review` 的描述关键词，放宽或补规则 | 🟠 |
| 2 | **`tri-req-audit` 尚未 junction 安装** | `os.path.lexists("~/.workbuddy/skills/tri-req-audit")` = **False**；`install-skills.py --dry-run` → `✅ 1 · ⏭ 跳过 24 · 🔴 失败 0` | 词表/斜杠激活不可用（不影响仓库内校验） | `python ops/install-skills.py --target ~/.workbuddy/skills` | 🟡 |

> `tri-req-audit` 的安装不在获批的 P0–P4 范围内，且属**工作区外全局状态变更** → 未擅自执行，列为待放行项。

---

## 八、终局回归矩阵

| 校验 | 命令 | 结果 | 与改前对比 |
|---|---|---|---|
| 补丁层幂等 | `python ops/patches/apply.py --json` ×2 | 30 op ｜ applied **0 / 0** ｜ error 0 | ✅ |
| 版本一致性（仓库侧） | `python ops/version-lint.py` | **EXIT=0** | ✅ |
| 版本一致性（独立安装侧） | `python tri-forge/scripts/check_registry.py --check` | 「检查 **34** 个 skill；漂移 **0**」 | ✅ |
| 门④ 全仓 | `python tri-forge/scripts/compliance_check.py --all` | 25 对象 ｜ FAIL **9** | **与改前同一集合**（`tri-action` / `tri-checklist` / `tri-evolve` / `tri-fix` / `tri-loop` / `tri-lottie` / `tri-meta` / `tri-sdlc` / `tri-workflow`）→ 行为等价 |
| 门④ 本 skill | `... --skill tri-req-audit` | 1 对象 ｜ **FAIL 0** | ✅ |
| 版本门 本 skill | `python tri-req-audit/scripts/check_update.py --slug tri-req-audit --json` | `state="A"` ｜ `self_check="已通过"` | ✅ |

---

## 九、改动文件清单

| 文件 | 性质 | 说明 |
|---|---|---|
| `ops/patches/manifest.json` | 补丁层源 | +`f18-familyspec-shared-domain` / +`f19-compliance-dedup`（28→30）；2 条 label 计数修正 |
| `ops/patches/README.md` | 文档 | 当前清单表 3 计数 + 新增 f18/f19 两行 + f18 描述 + 「计数增量」小节 |
| `ops/README.md` | 文档 | 目录树/命令 3 计数 + 3 处增量注记 + L224 事实更正 + 「计数增量」小节 |
| `README.md`（根） | 文档 | 6 处计数 |
| `WORKFLOW-GUIDE.html` | 文档 | 15 处（计数 7 + 收录 7 + 命名卡 1） |
| `ops/versions.json` | 基线 | `--emit-baseline` 33 → 34 |
| `tri-forge/scripts/compliance_check.py` | skill 文件 | **经 op `f19` 产出**（未直改） |
| `tri-forge/references/family-spec.md` | skill 文件 | **经 op `f18` 产出**（未直改） |
| `.workbuddy/memory/2026-09-25.md` / `MEMORY.md` | 记忆 | 原子写（写 temp + `os.replace`） |

**并行会话文件**：`WORKFLOW-GUIDE.html`（tri-init 1.0.2→1.0.3 四处）、`ops/patches/README.md`（f14–f17 五行）、`tri-init/*` 5 文件、`README.md` tri-init 行 —— 来自**另一会话**，本轮**未单方提交**，提交切分留待裁定。

---

## 十、评分

| 维度 | 评分 | 依据 |
|---|---|---|
| 遗留项闭环度 | 🟢 **5/5** | 全部有 op / 判据 / 证据 |
| 判据有牙度 | 🟢 | 行为等价**双证明**（正向全仓 JSON 全等 + 负向 4 fixture）；幂等三轮一致 |
| 诚实度 | 🟢 | 主动反转原报告 #4 的建议并给出反证；冻结 6 处时点记录不改写；2 项未修如实列出 |
| 文档一致性 | 🟢 | 4 处计数四层（op 数 / spec 份数 / check_update 份数 / skill 总数）全部对账；`version-lint` 双校验器 EXIT=0 |
| 残余风险 | 🟡 | 角色识别 `unknown` 8 个（🟠，影响 #8/#20）；安装未执行（🟡）；并行会话未提交（🟡） |

**门④ 判定**：本 skill `FAIL 0`；仓库级 9 个 FAIL 为**既有存量**，与本次改动无因果关系（已由改前基线证明）。
