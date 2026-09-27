# 提案 · tri-req-audit：补全 `cross-context` 的子会话隔离边界（+ R6 机械守卫）

- **日期**：2026-09-27
- **状态**：`Approved:no` ← 待批（未 apply，未编辑任何 skill 文件）
- **关联**：`reports/proposal-req-audit-adversarial-20260925.md`（上一轮对抗层硬化）

## 一、缘起

外部框架评估（SkillEvolver / arXiv 2605.10500）中有一条机制值得借鉴：
其 **auditor 的隔离设计**明确规定审计者只能接收
`candidate skill + 任务说明 + 训练数据 + 带标签 trace`，
**显式排除验证集与优化器自身上下文**。

本仓 `tri-req-audit` 的对抗层已实现大部分同类机制（见下），仅 `cross-context`
一档的**隔离边界缺少可验证的内容契约**——本提案只补这一处。

## 二、现状核查（不凭记忆，逐条附证据）

| 机制 | 状态 | 证据 |
|---|---|---|
| D9 对抗维（≥3 条可证伪场景，≥1 条须落在其余维度判「通过」处） | ✅ 已实现 | `references/audit-dimensions.md` §二 D9；`SKILL.md:35` 第 12 条 |
| `independence=` 三态（`same-agent` / `cross-context` / `cross-model`） | ✅ 已实现 | `references/audit-dimensions.md:164-174` |
| 「委派 ≠ 独立」的反伪装规则 | ✅ 已实现（严于外部框架） | `references/audit-dimensions.md:172-174`；`CHANGELOG.md:14` |
| 机械守卫 R1/R2/R3/R4/L2 + 自检夹具 | ✅ 已实现 | `scripts/audit_gate.py:17-22`，`--self-test` |
| mutation 反例（删对抗小节必判违规 / 同源自称独立必被判） | ✅ 已实现 | `tests/tri-req-audit-full-testcases.md` TC-D06 / TC-D08 |
| **`cross-context` 的隔离内容契约** | ❌ **缺失** | `references/audit-dimensions.md:169` 附加要求**仅有**「记录子会话标识」 |

> 结论：本提案**不是**从无到有，而是补最后一格。现状已覆盖抗自证的主体。

## 三、唯一缺口

`cross-context`（审核在独立子会话执行）当前只要求「记录子会话标识」。
但**「子会话」是形式条件**——若该子会话仍能看到生成方的推理过程、自评结论或
期望值，它实质退化回 `same-agent`，「独立」就变成一句标签。

外部框架的做法是给出**可验证的排除清单**；本仓缺的正是这一清单。

## 四、拟改条文（精确 old → new）

### 4.1 `references/audit-dimensions.md` §五 表格行

**old**（`:169`）：

```
| `cross-context` | 审核在**独立子会话**执行（生成方 context 未参与） | 记录子会话标识 |
```

**new**：

```
| `cross-context` | 审核在**独立子会话**执行（生成方 context 未参与） | 记录子会话标识 + `isolation_scope=` 声明（见下「子会话隔离边界」） |
```

### 4.2 `references/audit-dimensions.md` §五 新增小节（置于独立性声明表之后）

```
**子会话隔离边界（`cross-context` 的可验证定义）**：

允许接收：候审文档本体、任务说明、训练数据、带标签的执行 trace。

MUST NOT 接收（任一未排除即**不得**写 `cross-context`）：
  ① 生成方（被审文档作者）的推理过程 / 自评结论 / 会话上下文；
  ② 验证集或任何未脱敏的对照材料；
  ③ 审核结论的期望值（防锚定）。

理由：子会话若可见上述任一项，独立审核退化为**形式标签**——与
`same-agent` 无实质差别。`isolation_scope=` MUST 显式列出排除项。
```

### 4.3 `scripts/audit_gate.py` 新增 R6

规则：`independence=cross-context` 时，报告 MUST 含 `isolation_scope=`，且其值
MUST 显式声明排除生成方上下文（关键词：`生成方` / `context` / `上下文` / `验证集`）。
其余取值不适用。

```python
ISO = re.compile(r"isolation_scope[ \t]*=[ \t]*`?([^\n`]+)`?")
...
    elif vals[0] == "cross-context":
        m = ISO.search(txt)
        if not m:
            bad.append("R6 independence=cross-context 但缺 `isolation_scope=` 声明"
                       "（MUST 列出子会话 MUST NOT 接收的内容，见 audit-dimensions.md §五）")
        elif not any(k in m.group(1) for k in ("生成方", "context", "上下文", "验证集")):
            bad.append(f"R6 `isolation_scope=` 未声明排除项（收到：{m.group(1)!r}）"
                       "—— MUST 至少显式排除生成方上下文")
```

同步文件头判据清单增一行：

```
    R6  H2 隔离边界     —— independence=cross-context 时 MUST 含 `isolation_scope=` 且声明排除项
```

### 4.4 配套两处

| 文件 | 改动 |
|---|---|
| `templates/req-audit-report.md` | 在 `independence=` 行旁增 `isolation_scope=` 行（`f49b` 已加过 `independence` 行，此处照办） |
| `tests/tri-req-audit-full-testcases.md` | 新增反例用例：`independence=cross-context` 但缺 `isolation_scope=` ⇒ 判 FAIL；`audit_gate.py --self-test` 增对应夹具 |

## 五、验收判据

| 项 | 判据 |
|---|---|
| R6 生效 | 造一份 `cross-context` 且无 `isolation_scope=` 的报告 → `audit_gate.py` 退出码 1 并列出 R6 |
| 不误伤 | `same-agent` / `cross-model` 报告 → R6 不触发（其余判据结果不变） |
| 自检 | `audit_gate.py --self-test` 退出码 0，且新增夹具确在跑 |

## 六、幂等判据（若走补丁层）

`python ops/patches/apply.py --dry-run` 连跑两次，第二次必须为
**「写入 0｜应用 0」**；`already_marker` 取 §4.1 新行整行文本（含 `isolation_scope`），
避免锚点型重复注入。

## 七、不动的部分 / 待裁定

- **不动**：D9 判据、`independence=` 三态取值、`same-agent` 反伪装规则、R1–R5/L2。
- **不动**：`delegation=unavailable ⇒ MUST same-agent` 这条如实原则。
- **待裁定**：落地载体——① 走补丁层新增 op（`replace_text` ×3 + 测试）；② 判定
  `tri-req-audit` 属自维护主线后直接改（本仓 `tri-*` 为自维护 fork）。
  两者对 skill 产物的最终状态等价，差别只在升级后的可重放性。
