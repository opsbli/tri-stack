# case 电池规范 · 判据单一事实源

> **本文件是「case 电池」的判据唯一真源。** 其它位置（`compliance-checklist.md` / `SKILL.md`）
> ONLY 允许**瘦指针引用**，NEVER 重述本文件的判据 —— 这是硬约束第 23 条（规范单一事实源）的自我约束。
>
> **定位**：电池是**门④.5（变更验收）的输入真源**。门④.5 判「一次变更是否改变了行为」，
> 但它需要一份「case → 期望裁决」的清单才能跑；本规范定义那份清单怎么建、怎么分集、怎么封存。
> 三者关系：**门④（静态合规）→ 门④.5（动态行为）→ 电池（门④.5 的输入）**。

---

## 一、要解决的问题

在没有电池之前，门④.5 的输入只能临时拼——**同一批用例既用于开发调试又用于验收**，
这正是 Meta-Harness 论文自认栽过的坑（TerminalBench-2 的 search 与 final eval 用同一批 89 个任务，
要靠 regex 审计查泄漏）。实测依据（三轮 pilot，2026-09-26 ～ 09-27）：

| 实测项 | 数字 | 出处 |
|---|---|---|
| 「聚合分 + 散文摘要」的诊断 recall | 2/5 = 40%，46% 弃权 | pilot2 |
| 「案级结构化台账」的诊断 recall | 5/5 = 100%，0 误报 | pilot2b |
| 两份台账的输入成本 | ≈3.8 KB/轮（对比全量原始 trace 65 KB） | pilot2b |
| 归档规模 ×5 后实际读取量变化 | **不变**（26 文件 / 65,039 B） | pilot2b |

→ 电池把「case → 案级结论」固定成单一事实源，且**成本与归档规模解耦**。

---

## 二、电池 schema（单一事实源）

文件：`tests/battery/battery.json`。**case 是追加一行**，不需要改任何脚本（零改动路径）。

```json
{
  "case_id": "C-001",
  "kind": "real",                      // real（真实 skill 包）| fixture（基准包 + 单点 op）
  "target": "tri-coding",              // real → 仓库内 slug；fixture → fixtures.json 里的夹具名
  "split": "search",                   // search | eval
  "expected": {
    "verdict_token": "PASS",           // 翻转判据主键
    "clauses": ["#8"]                  // 该 case 的非 PASS 条款集（解释用）
  },
  "ratification": "baseline-frozen",   // by-design | baseline-frozen
  "basis": "……"                        // 期望的依据（一句话）
}
```

| 字段 | 必需 | 口径 |
|---|---|---|
| `case_id` | ✅ | 两侧对齐的键；MUST 稳定，NEVER 复用 |
| `kind` | ✅ | `real` = 仓库内真实 skill 包；`fixture` = 由 `fixtures.json` 的「基准包 + op」物化 |
| `split` | ✅ | 见 §三；**MUST 显式声明**，无默认值 |
| `expected.verdict_token` | ✅ | 见 §四 |
| `expected.clauses` | ✅ | **允许空列表**（全 PASS 的干净 case 本来就没有非 PASS 条款）；缺该**键**才作废 |
| `ratification` | ✅ | `by-design`（有独立于脚本的 ground truth）｜`baseline-frozen`（基线快照，仅用于变更检测） |
| `basis` | ✅ | 一句话说明期望的依据；`baseline-frozen` MUST NOT 被当作「判据正确性」的证据 |

### 夹具的 delta 形式（`tests/battery/fixtures.json`）

夹具**不落盘为目录**，而定义为「基准包 + op 列表」，运行期物化到临时目录。原因有两条：

1. **体积恒定** —— 夹具体积不随基准包增长（差分而非全量）。
2. **不污染 skills 树** —— 夹具含 `SKILL.md`，若落盘在 skills 目录下会被 skill 发现机制当成真实 skill 加载。

op 语言：`append` / `prepend` / `regex_replace` / `delete_file` / `add_file`。
**每个夹具 MUST 只做一处语义 op** —— 这样其期望与基线只差一处，可直接充当 by-design 断言。

---

## 三、split 纪律（硬性）

| 集 | 用途 | 运行时机 | 约束 |
|---|---|---|---|
| `search` | 开发调试 / 定位问题 | 随时可跑 | 期望可读、可反复跑 |
| `eval` | **只在变更验收（门④.5）时跑** | 仅验收 | 期望封存于 `_sealed/eval-expect.json` |

**机械强制**：`battery_run.py --split eval|all` **必须**与 `--i-am-accepting` 同时出现，否则拒绝执行（退出码 2）。
这条防的不是疏漏，而是**过拟合形态本身**：只要允许对着 eval 组调参，就一定会发生。

**封存**：`_sealed/` 下的期望对**执行体（被优化的对象）禁读**；
只有门④.5 的验收动作可以读。这条与 pilot 系列实验对 `_sealed/ground-truth.json` 的处置一致。

---

## 四、裁决 token 口径

**`verdict_token` 是翻转判据的唯一主键**；`clauses` 只用于解释「因为哪条改了」。

```
token = "PASS" | "FAIL:<必检失败条目号,升序>"     +   "+adv<建议项失败条目号>"（若有）
```

口径理由（均由实测确定）：

1. **token MUST 带条目号，不能只编码总判。**
   实测（2026-09-27）：新增**建议项**条目**不改变** PASS/FAIL 总判，只改变条目集。
   若 token 只编码总判，这类变更会被判为「未翻转任何 case」，B1 直接 FAIL —— 而这恰恰是
   pilot2b 指出的关键单位：**可机械比对的最小粒度是「案级条款集」，不是分数、也不是总判**。
2. **`MANUAL` 项 NEVER 入 token**（它是待人工项，不是结论），只留在 `clauses`。
3. **`clauses` 的字符串 NEVER 用作翻转判据**（同一节在两版常被引成不同粒度，字符串比对会系统性误报）；
   但**条目号**（`#23` 这类稳定标识）是安全的，故可以进 token。

---

## 五、与门④.5 的接口

```bash
# 1) 改前 / 改后各产一次台账（--gate 指向对应版本的门禁脚本）
python scripts/battery_run.py --split all --i-am-accepting \
    --gate <改前脚本> --stamp-version 1.0.6 --ledger before.json --attribute "op-01=23"
python scripts/battery_run.py --split all --i-am-accepting \
    --ledger after.json --attribute "op-01=23"

# 2) 进门④.5
python scripts/acceptance_diff.py --before before.json --after after.json --ops ops.json
```

台账即门④.5 的输入契约（`case_id` / `verdict` / `verdict_token` / `clauses` / `evidence` / `changed_by`），
**不需要任何转换层**。

`--attribute "op-01=23"` 的归因口径：某 op 引入条目号 `#23`，则条款集含 `#23` 的 case 记为 `changed_by=op-01`。
**局限（随用随声明）**：若该条目号在变更前**已存在**于该 case 的条款集，本口径会误归因；
故它只适用于「op 引入的条目号此前不存在于该 case 条款集」的情形。

---

## 六、新增 case 的零改动路径

1. **真实包**：在 `battery.json` 的 `cases` 追加一行（`kind:"real"` + `target:<slug>` + `split` + `expected` + `ratification` + `basis`）。
2. **反例夹具**：在 `fixtures.json` 的 `fixtures` 追加一条（`base` + **单点** op），再在 `battery.json` 追加一行（`kind:"fixture"`）。
3. 重算期望：`python scripts/battery_run.py --split all --i-am-accepting --emit-expect <out.json>`
   —— 该输出是**候选**，MUST 经人工核定后再写入 `expected` / `_sealed`，并据实标注 `ratification`。

**NEVER** 让 `--emit-expect` 的输出**未经核定**直接成为期望——那是把脚本现状当成判据正确性。

---

## 七、已知边界（诚实声明）

1. **电池只覆盖它声明的那个门禁。** 本次电池的覆盖对象是 `compliance_check.py`；
   改 `tests/mutation-gate.py` 这类**不在覆盖范围内**的变更，门④.5 应记 `out_of_scope`（MUST 附理由），
   NEVER 假装「无 case 翻转」。
2. **`baseline-frozen` 的期望不是正确性断言**，它只保证「不会再悄悄变」——即变更检测与防回归。
3. **存在已知盲区，且已被显式固化为 case**：`E-005-criteria-redefinition` 注入一次「判据被重述且自称真源」，
   期望**与基线完全相同**（当前机械层面检不出它）。MUST NOT 因它未翻而修改其期望 ——
   它的作用正是把盲区变成可回归的断言。
4. **电池会随包演进**：`#24` 从建议项升为必检、或 `_sealed` 被重写，都属变更，MUST 走门④.5 自验收。
5. **本规范本身尚未被真实评测系统验证**：三轮 pilot 验证的是**诊断接口**，不是采集管道；
   要关闭此局限需一次「真实 skill × 真实评估」的试点。
