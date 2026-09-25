# 锻造交付摘要 · `tri-req-audit`（C 模式）

> 由 `tri-forge` 门⑤ 产出。**产物清单 + 门④ 22 条自检结果 + 门③ 路由登记记录 + 安装评估**。
> 本次输入来源：`direct`（用户直接触发；`.tribro/LATEST.md` 不存在，无可用快照，未走快照链路）。

## 一、输入确认（门①）

| 项 | 值 |
|---|---|
| skill 名 / slug | 需求文档审核 / `tri-req-audit` |
| 一句话职责 | 对 `tri-prototype` 产出的 `requirements.md` 做开工前审核：三重前置本地校验 → 二跳委派市面 PRD 审核 skill → 聚合为 P0/P1/P2 问题清单与修订清单；**只出问题，不改原文** |
| 是否 tri-intent 下游 | **否**（内部工具型，不注册下游路由项） |
| 上游检测态数 | 三态（快照模式 / 引导安装 / 降级模式）——委派编排型，含降级声明 |
| 与 tri-grill 关系 | **并列分工**（tri-grill 对齐导向 / 本 skill 质量导向），非上下游 |
| 落盘位置 | `<repo>/tri-req-audit/` |

## 二、产物清单（门② 产出）

| 文件 | 行数 | 内容 |
|---|---|---|
| `tri-req-audit/SKILL.md` | 九章 | 三阶段流水线 + 五门 + 二跳委派 + 八维兜底 |
| `tri-req-audit/README.md` | — | 特性 / 与 tri-grill 分工表 / 安装 / 用法 / 目录结构 / 设计原则 |
| `tri-req-audit/CHANGELOG.md` | — | 首条 `## [1.0.0] - 2026-09-25` |
| `tri-req-audit/_meta.json` | — | ownerId / publishedAt / slug / version |
| `tri-req-audit/references/version-check-spec.md` | — | 版本检查执行规范（内部化持有，满足第 22 条） |
| `tri-req-audit/references/market-prd-review-skills.md` | — | **市面 skill 注册表 + 委派契约单一事实源** |
| `tri-req-audit/references/audit-dimensions.md` | — | **八维审核规则 + 分级判据单一事实源** |
| `tri-req-audit/scripts/check_update.py` | 40731 B | 版本门（与 `ops/patches/assets/check_update.py` **hash 全等**：`5f06729b8404`） |
| `tri-req-audit/scripts/audit_precheck.py` | — | 前置三重校验确定性判定（结构 / 溯源 / 可测性形态 / 定级） |
| `tri-req-audit/templates/req-audit-report.md` | — | 审核报告模板（九区 + 元数据） |
| `tri-req-audit/tests/tri-req-audit-full-testcases.md` | 230 行 | 31 条用例（能力 12 / 委派降级 7 / 边界 7 / 负向 mutation 5） |

## 三、门④ 22 条自检结果

**门④ PASS —— 必检项 FAIL 0 / N-A 2（均附理由）**

| # | 约束 | 判定 |
|---|---|---|
| 1 | 目录结构完整 | ✅ PASS（核心 3/3；子目录 4/4） |
| 2 | 独立安装声明 | ✅ PASS（命中「支持独立安装，含上游依赖检测三态逻辑」） |
| 3 | SKILL.md 章节齐全且顺序正确 | ✅ PASS（九类齐全；版本节置于交付产物之后，家族已登记变体） |
| 4 | frontmatter 完整 | ✅ PASS（八字段；version=1.0.0） |
| 5 | 强制执行契约含自检句 | ✅ PASS（18 行；自检句 `本次模式=`） |
| 6 | 上游检测态数与类型匹配 | ✅ PASS（检出：引导安装 / 降级模式 / 降级） |
| 7 | 职责边界明确 | ✅ PASS（含「不负责」+ 相邻边界表六行） |
| 8 | 意图认领 MECE 不重叠 | ⬜ N-A（内部工具型，不认领 L2/L3）→ **已按契约 §5 补做人工跨真源比对，见 §四** |
| 9 | 核心能力方法论含可扩展性 | ✅ PASS |
| 10 | 交付产物含落盘规则 | ✅ PASS（`.tribro/req-audit/<命名>/`，由 slug 去前缀机械推导） |
| 11 | CHANGELOG 规范 | ✅ PASS（首条=1.0.0=frontmatter=文件最大） |
| 12 | tests 全场景用例 | ✅ PASS（230 行；标题含「测试用例」） |
| 13 | 门禁 / 审批门明确 | ✅ PASS（门①–门⑤，逐门通过条件与回炉方向） |
| 14 | 兜底处理覆盖 | ✅ PASS（八类场景，明确 NEVER 静默失败） |
| 15 | 自检句格式与家族一致 | ✅ PASS（内部工具型标准形 `本次模式=`） |
| 16 | 反规避规则〔建议项〕 | ✅ PASS |
| 17 | 禁止硬编码家族计数 | ✅ PASS（全文无 `\d+ 个(下游\|skill\|顶层目录)` 命中） |
| 18 | 可执行实现与 prompt 分离 | ✅ PASS（`scripts/` 两脚本） |
| 19 | 与相邻 skill 边界表〔建议项〕 | ✅ PASS |
| 20 | 横向层自检句例外登记 | ⬜ N-A（非横向型） |
| 21 | 安装评估 | ✅ PASS（见 §五） |
| 22 | 版本检查内部化 | ✅ PASS（自身指针有；无外部指向；15 行 ≤30） |

命令：`python tri-forge/scripts/compliance_check.py --skill tri-req-audit` → **EXIT=0**

## 四、门③ 路由登记记录

本 skill 为**内部工具型**，按 `references/tri-intent-integration.md` §一 **不执行**常规路由回填（无 L2/L3 编码）。
但因其采用**二跳形态**，按该文件 §五 与 `family-spec.md` §五 要求，**必须登记二跳例外**。

### 4.1 二跳登记（已落地）

| 项 | 内容 |
|---|---|
| 登记位置 | `tri-forge/references/family-spec.md` §五 待登记项表**新增一行**（原文第 187 行下方，现第 188 行） |
| 落地方式 | 补丁 op `f14-req-audit-two-hop`（`replace_text`）+ `python ops/patches/apply.py` 重放 —— **未直改 skill 文件**（遵守项目铁律 #1） |
| 中介 | `tri-req-audit`（需求文档审核） |
| 被执行方 | 市面 PRD 审核 skill：`prd-review` / `requirement-testability-review` / `bg-requirement-review` —— **不注册**为 tri-intent 下游 |
| 契约真源 | `tri-req-audit/references/market-prd-review-skills.md` |

### 4.2 MECE 跨真源人工比对（补做第 8 条）

以**路由真源** `tri-intent/SKILL.md` §一 路由映射表为基准：

| 检查 | 证据 | 结论 |
|---|---|---|
| 真源中是否存在「需求审核 / 需求文档审核 / PRD 审核」落点 | `grep -nE "需求审核\|需求文档审核\|req-audit\|PRD 审核" tri-intent/SKILL.md tri-intent/doing/*.md` → **无命中** | 无既有落点被占用 |
| 全仓是否另有 skill 声称同一职能 | `grep -lE "审核需求\|审查需求文档\|需求文档审核" tri-*/SKILL.md` → 仅 `tri-req-audit/SKILL.md` | 无重叠 |
| 是否被错误登记为下游 | `grep -n "tri-req-audit" tri-intent/SKILL.md` → **无命中** | 符合「内部工具型不注册下游」 |
| 与四个近邻的职能边界 | `tri-prototype`（产文档）/ `tri-grill`（磨共识）/ `tri-review`（审代码，独占 CR）/ `tri-forge`（审 skill 包） | 对象两两不同 |

### 4.3 未回填项（有意）

| 项 | 为什么不做 |
|---|---|
| `tri-intent` 路由映射表 / L3 子类说明 | 内部工具型不认领 L2/L3，登记反而违反「一跳路由」约束 |
| `check_downstream.py` 检测清单 | 同上；探测落点已由 `market-prd-review-skills.md` §四 自持 |
| 家族计数表述 | 全文无硬编码计数（第 17 条 PASS） |

## 五、安装评估（第 21 条）

| 检查 | 结果 |
|---|---|
| slug 冲突 | ✅ 无 —— 四平台落点均无 `tri-req-audit` |
| 目标目录可写 | ✅ `~/.workbuddy/skills` 可写（写探针已清理） |
| 四平台可落地 | ⚠️ `.trae` / `.cursor` / `.qcoder` 三处目录本机不存在 → **仅记录，不阻断交付** |
| 当前安装态 | 用户级落点尚未创建（`check_update.py` 报 `is_link=false`）。安装命令：`python ops/install-skills.py --target <目标目录>` |

## 六、判据有牙证明（mutation testing）

`scripts/audit_precheck.py` 经**六组注入验证**，判据非文字装饰：

| 注入 | 期望 | 实测 |
|---|---|---|
| 正向（合法九章文档） | `ok` / 无缺陷 | ✅ EXIT=0，仅 INFO 结论 |
| mut1 删除「八、验收标准」整章 | `blocked` | ✅ EXIT=1，D1 P0「整章缺失：验收标准」 |
| mut2 验收标准写「界面友好，操作流畅」 | `blocked` | ✅ EXIT=1，D3 P0「验收标准不可判定」 |
| mut3 业务规则「出处」列留空 | `blocked` | ✅ EXIT=1，D8 P0「条目缺出处」 |
| mut4 技术约束留 `{{tech_stack}}` | `blocked` | ✅ EXIT=1，D1 P0「模板占位符未替换」 |
| mut5 待补充项「影响」列留空 | `conditional` | ✅ EXIT=0 但 D1 P1（P0=0） |

**过程中修正两处判据缺陷**（均为首版实测暴露，非推测）：

1. **假阳性**：解析元数据的「冲突项数量｜0」触发「未标注 PRD 优先」告警 → 扫描范围收窄到业务规则 / 功能需求 / 页面三章。
2. **mutation 逃逸（严重）**：`cells()` 用 `strip("|")` 把**外层**管道也剥掉，导致行尾空单元格被吞（`| a | b |  |` 变 3 格而非 4 格），mut5 漏检。同时列定位靠 `c[-2]` 硬编码，对列数不同的表会取错列。已重写为**表头驱动**列定位（`col_index`）。

## 七、版本一致性校验

| 校验器 | 结果 |
|---|---|
| `python ops/version-lint.py` | **EXIT=0**；覆盖 **34** 个 skill（顶层 25 + `children/*` 9），漂移 0；`tri-req-audit` 行：P1 1.0.0 / P2 1.0.0 / P3 1.0.0 / P5 1.0.0(badge) ✅；D1–D4 文档层无漂移 |
| `python tri-forge/scripts/check_registry.py --check` | **EXIT=0**；检查 34 个 skill，存在漂移 **0** 个 |
| `python tri-req-audit/scripts/check_update.py --slug tri-req-audit --json` | `state=A`，退出码 0，5 处版本声明一致 |
| `python ops/patches/apply.py`（连跑两次） | 第二次全 op **写入 0 / 应用 0**（幂等达标）；`spec-per-skill` 跳过数 33 → **34**（新 skill 已纳入）；`f14` 应用 1 → 已应用 1 |

## 八、遗留项（**本次刻意未做**，附理由与建议动作）

> 以下均为**「新增 skill 后被影响但超出锻造范围」**的项，按最小化原则不擅自扩展。**均带证据**。

| # | 项 | 证据 / 现状 | 建议动作 | 严重度 |
|---|---|---|---|---|
| 1 | `WORKFLOW-GUIDE.html` 未收录新 skill | 该文档会枚举 skill（`tri-grill` 出现 12 次、`tri-forge` 15 次），但 `version-lint` 的 D1–D3 **只校验已存在的条目**，故**不报错也不提示缺漏** | 人工决定分层图位置后增补 chip（D1 格式 `<b>tri-x</b> <span class="v">1.0.0</span>`） | 🟡 |
| 2 | `ops/versions.json` 基线未含新 skill | 该文件为 `--emit-baseline` 生成物，当前尚缺 `tri-req-audit`；且 `tri-review` 已 1.7.0 而基线仍记 1.6.2（**既有漂移，非本次引入**） | 跑 `python ops/version-lint.py --emit-baseline` 整体刷新（会一并修正 tri-review） | 🟡 |
| 3 | 补丁层自述中的计数已在语义上失真 | `ops/patches/manifest.json:231` 与 `ops/patches/README.md:73,87,96,222,436,457,474,476` 写「顶层 24」「当前 33 个」「34 份 hash 全等」；现实测应为 **顶层 25 / 覆盖 34 / 35 份** | **不宜直接改**——其中多数是**带时点的实测记录与追加型历史**（家族口径：冻结不改写）。正确做法是追加一条**带日期的增量注记**说明 2026-09-25 新增 `tri-req-audit` 后计数 +1 | 🟠 |
| 4 | `family-spec.md` §1.4 豁免清单未登记 `coding/` | §1.4 判据为「`.tribro/<域>/` 目录名可从 skill slug 机械推导」，但 `tri-prototype` / `tri-coding` / `tri-orchestrate` 三家实际共写 `.tribro/coding/`，而豁免清单只登记了 `snapshots/` 与 `skills/` | 补充登记 `coding/` 等共享域目录（本 skill **已主动规避**：产物落 `.tribro/req-audit/`，可推导，零争议） | 🟠 |
| 5 | `tri-forge/scripts/compliance_check.py` 存在**重复代码块** | 角色识别块（`if "总路由" in desc and ...` 起的五行 if/elif 链 + 上方注释）在 **L143–155 与 L157–169 完全重复**。因两次赋值结果相同，**行为无差异**（本次 22 条判定不受影响），属可维护性缺陷 | 删除 L157–169 的重复块。⚠️ **必须走补丁 op**（项目铁律 #1：skill 文件不得直改），且须做行为等价验证（对全部 skill 跑 `--all --json` 前后 JSON 全等） | 🟡 |

## 九、结论

- 门①→门⑤ **全流程走通**；门④ **22/22 PASS**（2 N-A 附理由）
- 产物 **11 个文件**落 `tri-req-audit/`；门③ 二跳登记经补丁 op `f14` 落地且**幂等**（连跑两次零写入）
- 版本一致性 **两个校验器均 EXIT=0**
- 判据有牙：六组 mutation 验证通过，并修正了 1 处假阳性 + 1 处**mutation 逃逸**
- 遗留 5 项（🟠 2 / 🟡 3）已在 §八 逐项给出证据与建议动作
