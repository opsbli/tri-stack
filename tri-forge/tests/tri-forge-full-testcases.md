# tri-forge 全场景测试用例

> 覆盖能力清单 + 三模式 + 五门流程 + 24 条硬约束自检 + 电池与门④.5 + 兜底场景。
> 判定口径：`PASS` = 行为与预期一致；`FAIL` = 偏离预期。

## 一、能力清单

| # | 能力 | 判定方式 |
|---|---|---|
| C1 | 三模式判定（A 规范顾问 / B 补全审计 / C 锻造生成） | 检查 SKILL.md §触发时机 四分支表 + §模式总览 |
| C2 | 五门流程（① 需求确认 ② 骨架生成 ③ 路由回流 ④ 合规自检 ⑤ 落盘交付） | 检查 §五门流程 区块 |
| C3 | 单一事实源（family-spec / compliance-checklist） | 检查 §强制执行契约 第 2 条 |
| C4 | 门④ 24 条自检 | 运行 `scripts/compliance_check.py --skill <slug>` |
| C5 | 门③ 路由回流 | 检查 `references/tri-intent-integration.md` 回填清单六项 |
| C6 | 五点版本一致性校验 | 运行 `scripts/check_registry.py --check` |
| C7 | 版本门（自维护模式） | 运行 `scripts/check_update.py --slug tri-forge --json` |
| C8 | 兜底处理（四类） | 检查 §兜底处理表 |
| C9 | 独立安装三态 | 检查 §上游依赖检测 三行表 |
| C10 | 与 tri-god / tri-guard（本分支未包含）的边界 | 检查 §不由本 skill 处理 表 |
| C11 | 门④.5 变更验收（案级条款集 diff） | 运行 `scripts/acceptance_diff.py --before <b> --after <a>` |
| C12 | case 电池（单一事实源 + search/eval 分离） | 运行 `scripts/battery_run.py --split search` / `--split eval --i-am-accepting` |

## 二、功能用例

| 用例 | 场景 | 预期结果 |
|---|---|---|
| T01 | 用户问「生成一个合规 skill 要满足哪些约束」 | 判为 **A 模式**；读 compliance-checklist 逐条说明；**不写任何文件** |
| T02 | 用户问「这条第 8 条约束怎么判」 | 判为 **A 模式**；给出判定方法（交叉比对 tri-intent 路由映射表）+ 示例；不落盘 |
| T03 | 用户说「按家族规范造一个 tri-xxx skill」 | 判为 **C 模式**；进入门①；先澄清 slug / 职责 / 是否下游 / 上游态数 |
| T04 | 用户说「给 tri-yyy 按规范审一遍」 | 判为 **B 模式**；产 `reports/tri-yyy-compliance.md`；24 条逐条判定 + 证据位置 |
| T05 | 用户说「补全这个 skill」且目标缺 `CHANGELOG.md` | 判为 **B 模式**；报 FAIL（第 1、11 条）；补全产物须用户确认后落盘 |
| T06 | 用户说「蒸馏这个人的方法论成一个 skill」 | **不激活本 skill**；指向 tri-god（I21） |
| T07 | 用户说「审一下这个第三方 skill 能不能装」 | **不激活本 skill**；指向 tri-guard（安全审计，本分支未包含） |
| T08 | 用户说「实现一个排序函数」 | **不激活本 skill**；指向 tri-coding（I11） |
| T09 | C 模式：生成的 skill 认领 L2=I13 默认落点，但 L2=I13 已被 tri-plan 认领 | 门③ → 门④ 第 8 条 **FAIL**；停止并提示改为 L3 子类或回炉门② |
| T10 | C 模式：生成物为横向型（不认领 L2） | 门③ **跳过**；门④ 第 8 条判 **N-A**（须附理由） |
| T11 | C 模式：门④ 第 17 条命中「19 个下游」硬编码计数 | 第 17 条 **FAIL**；回炉门② 改为描述性表述 |
| T12 | C 模式：目标目录不可写 | 第 21 条 **FAIL**；**不阻断交付**，但记录原因到交付摘要 |
| T13 | C 模式：同一条约束连续 3 轮 FAIL | **停止自动回炉**；向用户报告卡点并请求人工介入 |
| T14 | 独立使用（无 tri-intent）且用户拒绝安装 | 进入 **降级模式 C**；**先原样输出降级声明**；自构造等价输入并标注 `degraded` |
| T15 | 独立使用（无 tri-intent）未表态 | 输出**模式 B 提示语**并等待选择；NEVER 静默按空上下文执行 |

## 三、24 条硬约束自检用例

> 运行 `python scripts/compliance_check.py --skill <slug>` 验证判定正确性。
> 每条至少用一个「已知合规样本」验证 PASS、一个「已知缺陷样本」验证 FAIL。

| 用例 | 约束 | 构造 | 预期 |
|---|---|---|---|
| T16 | 1 目录结构 | 删除 `CHANGELOG.md` | FAIL，证据报核心文件 2/3 |
| T17 | 2 独立安装声明 | 把 description 中的「支持独立安装」删掉 | FAIL |
| T18 | 3 九章顺序 | 把「职责边界」移到「处理流程」之后 | FAIL，报章节顺序颠倒 |
| T19 | 4 frontmatter | 删 `tags` 字段 | FAIL，报缺字段 |
| T20 | 5 自检句 | 删掉自检句条目 | FAIL |
| T21 | 11 CHANGELOG | 把首条改成比 frontmatter 低一级的版本 | FAIL，报 P2≠P1 且非最大 |
| T22 | 17 硬编码计数 | 正文插入「共 19 个下游」 | FAIL，报命中计数 |
| T23 | 22 版本检查内部化 | 把指针改成其他 skill 的 `references/` | FAIL，报指向外部 |
| T24 | 8 MECE 交叉比对 | 认领与其他 skill 重叠的 L2 | 判 **MANUAL**（须人工比对真源） |

## 四、case 电池与门④.5 验收用例

> 运行 `scripts/battery_run.py --split all --i-am-accepting` 与
> `scripts/acceptance_diff.py --before <b> --after <a> [--ops <o>]`。
> 规范单一事实源：`references/case-battery-spec.md`；判据单一事实源：`references/change-acceptance-gate.md`。

| 用例 | 场景 | 预期 |
|---|---|---|
| T25 | 23 断链自引用指针 | 追加一个不存在的 `references/` 指针 | `#23` **FAIL**，报不可解析路径 |
| T26 | 23 跨 skill 指针 | 指针写成 `tri-forge/references/family-spec.md` | `#23` **PASS**（仓库根兜底可解析；仅按 skill 目录解析会误报） |
| T27 | 24 案级结构化（**必检**） | 评估产物 schema 缺结论字段（或案级键） | `#24` **FAIL** ⇒ **门④ 总判 FAIL**（v1.2.0 起由建议项升为必检，FAIL 即阻断、回炉门②） |
| T28 | 电池 split 纪律 | 不带 `--i-am-accepting` 跑 `--split eval` | **拒绝执行，退出码 2**，提示改用 `--split search` |
| T29 | 电池回归 | `--split all --i-am-accepting` | 19/19 与 `battery.json` / `_sealed` 期望一致，退出码 0 |
| T30 | 门④.5 检出建议项翻转 | before = 22 条脚本 / after = 24 条脚本，同一份电池 | 翻转 C-006 / C-008 / E-002，其余零误报，B1/B2/B3 全过 |
| T31 | 门④.5 干净 case 不作废 | 某 case 的 `clauses` 为 `[]` 且有结论变化 | **不得**判「字段缺失作废」，MUST 正常计入变更清单 |
| T32 | 门④.5 超范围记账 | 某 op 的变更不在电池覆盖内 | MUST 标 `out_of_scope` **并附 note**；未附 note 时 MUST 告警 |
| T33 | 门④.5 B1 负向 | 某 op 声称 `behavior_change` 但无 case 翻转 | **B1 FAIL**，退出码 1 |
| T34 | M7 负向测试（#23 有牙） | `tests/mutation-gate.py` 的 M7 注入断链指针 | 抓到 `#23` FAIL；且真实 skill md5 前后一致、**退出码 0** |
| T35 | **元级判据用例 · 正例**（M-24-a/b/c） | 分别注入 DDL schema（`case_id`+`verdict`）/ 英文案级键字段表（`test_id`+`status`）/ 中文「账本」字段表（`检查项`+`结论`） | `#24` **PASS**（三条均 PASS；任何一条误判 FAIL 即报错） |
| T36 | **元级判据用例 · 负例**（M-24-d/e） | ① 只在 `CHANGELOG.md` 提到 `signals.jsonl`；② 只说「台账」而不定义字段 | `#24` **N-A**（判定「提到 ≠ 定义」不会回归） |
| T37 | **元级判据用例 · 反例**（M-24-f） | 注入有案级键、**无结论字段**的产物字段表 | `#24` **FAIL**。token：v1.1.1（建议项期）= `PASS+adv24`；**v1.2.0 起（必检）= `FAIL:24`** —— 强度变更的可观测证据。**MUST NOT 因它翻红而改期望** |

> **T35–T37 的性质**：它们检验的不是被审计 skill，而是**第 24 条判据自身**。存在理由见 `references/compliance-checklist.md` §〇 校准记录 —— 仅凭「26 个对象变绿」无法区分「判据修对了」与「判据被调到刚好放过这 26 个对象」。
> **T27 的强度变更**：第 24 条升为必检后，「FAIL 不阻断」的旧表述不再成立——同一注入在 v1.1.1 是「建议改进项」，在 v1.2.0 是「阻断交付」。该差异由 `M-24-f` 的 token 形态变化机械承载（不需新增用例号）。

## 五、家族版本校验回归

| 用例 | 场景 | 预期 |
|---|---|---|
| T38 | 注入 P3 漂移（`_meta.json` 改错版本） | `check_registry.py --check` 报 P3≠P1，退出码 1 |
| T39 | 对 T38 执行 `--apply` | P3 被规则化回写为 P1 的值；**CHANGELOG 未被改动** |
| T40 | 注入 P5 漂移（README 徽章旧版本） | 报 P5≠P1；`--apply` 回写徽章 |
| T41 | 注入 P2 漂移（CHANGELOG 首条 ≠ frontmatter） | 报 P2≠P1；`--apply` **不回写**（属人工内容） |
| T42 | 全部一致 | `--check` 退出码 0，无漂移输出 |

## 六、测试结果记录

| 项 | 值 |
|---|---|
| 执行日期 | <YYYY-MM-DD> |
| 用例总数 | 42 |
| 通过 | <n> |
| 失败 | <n> |
| 备注 | <说明> |
