# 提案 · 第三方 skill 门禁：补两个失败分类（silent-bypass / 不可修 case）

- **日期**：2026-09-27
- **状态**：`Approved:no` ← 待批（未 apply；未编辑 `external_skill_gate.py`）
- **关联**：`reports/proposal-third-party-gate-20260926.md`（该门禁的上一轮）

## 一、缘起

外部框架评估（SkillEvolver / arXiv 2605.10500）暴露了两个**本仓门禁目前不覆盖**的失败模式：

1. **silent-bypass**：skill 内容看起来合法，但**运行时从不被调用** —— 静态齐备性检查对它零区分度。
2. **不可修 case**：GT 本身有争议时，怎么改 skill 都过不了；正确处置是**标记并移入回归集做防护**，而不是反复重试。

## 二、归属裁定（两类失败不在同一个地方）

| 失败分类 | 正确落点 | 理由 |
|---|---|---|
| silent-bypass | `tri-forge/scripts/external_skill_gate.py`（静态**风险**判据 S5） | 门禁只看静态产物；真正的「没被调用」需要运行时调用日志 |
| 不可修 case | **eval harness 侧**（不在门禁） | 它是「用例」的属性，不是「skill」的属性 |

> **其中「不可修 case」已在本次落地**（见 §五），因为它落在 P1 的新建物里，无需动受治理文件。

## 三、现状核查

`tri-forge/scripts/external_skill_gate.py`（276 行）：

| 组 | 判据 | 位置 |
|---|---|---|
| 结构组 | S1 frontmatter 最小集 · S2 description 触发信息 · S3 本地引用可达 · S4 目录卫生 | `:110-134` |
| 安全组 | X1 密钥字面量(🔴) · X2 动态执行 · X3 危险删除 · X4 下载安装 · X5 代码内硬编码外联 | `:136-158` |
| 质量组 | Q1 软化措辞 · Q2 AI 腔 · Q3 反例清单存在性 | `:160-166` |

**无 silent-bypass 判据**；`grep -i "silent\|bypass"` 零命中。豁免机制已存在
（`load_registry()` `:65-78`，豁免 MUST 登记于 `references/external-gate-registry.md`，NEVER 静默豁免）。

> 注：`external_skill_gate.py` 当前有**未提交改动（1 行）**。本提案改动点在
> **质量组尾部**，与之不重叠，可安全叠加。

**`lint-skills` 在本机不存在**：`find` 全仓 + 全部 `~/.workbuddy/skills/` 均未命中。
本提案因此**不包含** lint-skills 侧改动（见 §六 待裁定）。

## 四、拟增判据 S5 · 触发面缺失（silent-bypass 风险）

**定义**：`description` 与正文均**无触发条件表述** ⇒ 该 skill 有「运行时从不被选中」的风险。

**判据（三条任一命中 ⇒ `MANUAL`，detail 带 `silent-bypass-risk`）**：

| # | 检查 | 判据 |
|---|---|---|
| a | description 触发结构 | 不含「当…时 / 用于 / 触发 / 适用于 / When to use / Use when」任一 |
| b | 正文触发章节 | 无 `## 触发时机` / `## 何时` / `Triggers` 章节标题 |
| c | 被引用性（**可选增强**） | 全量扫描时，无任何其他 skill 的 SKILL.md 提及本 skill 名 |

**误报控制**：一律判 `MANUAL` 而非 `FAIL`（静态无法证明「没被调用」）；
豁免 MUST 登记 `references/external-gate-registry.md`（沿用现有机制，不新增通道）。

**实现片段**（追加于 Q3 之后）：

```python
RE_TRIG = re.compile(r"(当[^\n。]{0,20}(时|场景)|用于|触发|适用于|Use when|When to use)", re.I)
RE_TRIG_SECT = re.compile(r"^#{2,4}[ \t]*(触发时机|何时|Triggers?)\b", re.M)
...
    t_hit = bool(RE_TRIG.search(desc)) or bool(RE_TRIG_SECT.search(text))
    add("S5", "MANUAL" if not t_hit else "PASS",
        "silent-bypass-risk: description 与正文均无触发条件表述" if not t_hit
        else "触发面存在")
```

同步在文件头判据清单（`:10-13`）结构组追加 `S5`。

## 五、已落地的另一半：不可修 case 出口（eval harness 侧）

落在本次新建的 `ops/eval-harness/trace_store.py`（纯增量，未动任何现有文件）：

- 新增 `status=unrepairable` 取值；**必须**附 `--meta '{"note":"<GT 争议点>"}'`，
  否则退出码 2 拒绝写入。
- 用途：把「GT 有争议、改 skill 也过不了」的用例显式标记，用于**移入回归集做防护**，
  而不是反复重试。
- 已实测：无 note → 报错拒绝；带 note → `results.tsv` 记为 `unrepairable` 行。

## 六、验收判据（S5 部分）

| 项 | 判据 |
|---|---|
| 生效 | 对一份「description 无触发词且无触发章节」的 skill → `S5=MANUAL` 且 detail 含 `silent-bypass-risk` |
| 不误伤 | 现有合规 skill → `S5=PASS`；`--all` 总评分不应因 S5 整体劣化 |
| 自检 | `python tri-forge/scripts/external_skill_gate.py --self-test` 退出码 0 |
| 回执 | 22 个第三方 skill 的三组判据计数与 `reports/`/`external-gate-registry.md` 口径一致 |

## 七、待裁定

1. **`lint-skills` 归属**：本机未找到该组件（记忆中的「6-gate 归档系统」成员）。
   请指路其真实位置，或确认本轮**跳过**该项。
2. **落地载体**：走补丁层新增 op，还是判定 `tri-forge/scripts/` 属自维护主线后直接改。
3. **S5 判据 c（被引用性）**：需要全量扫描、且可能对「独立安装型 skill」误报，
   建议**暂不做**，仅登记为可选增强。
