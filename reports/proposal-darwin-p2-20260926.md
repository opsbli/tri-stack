# Proposal · darwin P2 批（结构性重写类 · D30 契约）

- **Date**: 2026-09-26
- **Author**: agent (darwin-skill 轮)
- **Approved**: yes (2026-09-26, AskUserQuestion「全批执行」)
- **Status**: pending review
- **Scope**: tri-stack 全仓 35 skill（26 顶层 + 9 children），结构性/重写类缺陷，与已完成的 P0（fb5f540）/ P1（631e066）互不重叠

## 一、背景

darwin 轮 P0+P1 已合 main（fast-forward 49049b1→631e066）。复评（`post-20260926.tsv`）均值 82.7→86.1，沉淀出以下结构性弱项。本批均为**章节级重写/去重/纠偏**（非 P1 的纯增章），故按裁定单独走 D30 proposal，不并入已关闭的 darwin 轮。

## 二、候选清单（证据 + 提案动作）

| # | 目标 | 证据（复评实测） | 提案动作 |
|---|------|------------------|----------|
| 1 | tri-ops | 第 24 条契约仍有 `&**:` 同款损坏（P0 全仓清零时漏网，复评发现） | 契约修复 op + PATCH 升版。**严重度最高，排序第一**（P0 级缺陷混入本批） |
| 2 | tri-plan | 「处理流程」+速查表整段重复（P0 去重批未覆盖此文件形态）；d7=5 | 重复节去重 op |
| 3 | tri-meta | 复评 68.3 全场最低：d2/d5/d7 弱；兜底③与「不支持降级」契约矛盾 | 兜底③口径对齐重写；d2/d5/d7 弱项视重写后的 paired 评审决定是否二次迭代 |
| 4 | tri-grill | 工作流仅 6 行表、无每步输入/输出（d2 弱） | 工作流节扩写（每步输入/输出/闸门），仅聚合既有语义 |
| 5 | children ×9 | d6=7：目录结构节漏 `references/` 与 `scripts/`（与 audit_gate.py 实际扫描面不符） | 9 份目录结构节纠偏（同一 op 模板批量） |
| 6 | tri-fix | 双「第 8 条」编号冲突（P1 时仅登记未修） | 编号重排 op |
| 7 | tri-html | 截断句 + 幽灵 §3.13 引用 | 残句补全/删除 + 幽灵引用清理 |

## 三、执行方式（补丁层铁律）

- 全部落成 `ops/patches/manifest.json` op（id 前缀 `dw3-*`），重放 `apply.py`；回执判据 = 连跑两次第二次零写入。
- 涉及 SKILL.md 章节增/删/重写 ⇒ 各目标 PATCH 升版 + CHANGELOG 条目 + `_meta.json` 同步 + `version-lint --apply-docs`。
- **新增版本批前先 grep 同 glob 同 pattern 的旧 settle op**（f86/f97 永动教训）。
- 重写类 op 起草时逐 skill 核对契约原文，禁止模板字段 blind 套用（P1 四处文本漂移教训）。
- 验收：改后跑一轮 paired 评审（3 judge，keep/revert 依据）；结果追加至 darwin 轮记录。

## 四、风险

- tri-meta 兜底③重写触及契约语义，须与 `tri-intent` M05 路由原文对齐，防止二次漂移。
- children 批量纠偏为 9 份同模板， AnchOR 断言须逐份验证（P1 批曾现 8 份 ANCHOR_FAIL）。
- item 1（tri-ops）为 P0 级，若用户希望提前可单独先行，不等本批整体裁决。

## 五、执行顺序（依赖序）

1 → 2 → 6 → 7（独立修复，无依赖）→ 5（批量模板）→ 4 → 3（重写量最大、风险最高，放最后单独 paired 评审）。

## 六、审批

- [ ] AskUserQuestion 通过
- [ ] 本文件 Approved 翻 yes（注明日期）
- [ ] apply + 双跑零写入回执
- [ ] paired 评审 ≥ 2:1 better
