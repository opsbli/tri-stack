# Proposal · tri-meta 深度重写（全场最低分的结构弱项 · D30 契约）

- **Date**: 2026-09-26
- **Author**: agent（darwin 轮后续）
- **Approved**: yes (2026-09-26, AskUserQuestion「按 proposal 执行」)
- **Scope**: 仅 `tri-meta/SKILL.md`（68.3→76.9 后仍为 35 skill 最低；本提案只动 d5/d7 两个弱项，dim2/3/4 相关簇已达 8/8/9 不碰）

## 一、证据（post2-20260926.tsv 盲评 + 原文定位）

| 弱项 | 证据 | 位置 |
|---|---|---|
| d5=7 可执行具体性 | M02/M03 重路由映射四处含糊：`（本分支未包含，原 tri-ask）`×3、`对应下游 skill（本分支有下游者）`——软化/悬空措辞，无明确处置动作 | L106–110 |
| d7=7 整体架构 | M05 不认领声明全文 **9 处**（L6/7/25/27/32/60/70/95/235），其中 ≥5 处为整句重复 | 全文 grep 实测 |
| d8=7 实测 | 结构性弱项已由 ①② 覆盖大半，剩余为 dry_run 口径波动，本批不动 | — |

## 二、提案动作（零发明：只删重复 + 把悬空措辞替换为该 skill 已有的显式语义）

1. **M05 声明收敛**：保留 3 处权威位（契约 L25、frontmatter L6/7、红灯清单 L195），其余 4 处整句重复（L32/L60/L95/L235）删除或缩为短指针`（M05 不认领，见契约 5）`；L27「家族决策」blockquote 与 L149/187（越界处置）为功能性出现，保留。
2. **重路由映射精确化**：L106–110 四行替换为显式语义——`→ 停止并交还 tri-intent 按快照路由派发（本分支不持下游映射；tri-ask/tri-mm/tri-bs 已归档至 archive 分支）`，如实反映 main 分支收窄态，NEVER 编造下游清单。
3. **验收**：paired 3 judge（keep/revert 权威）；预期 d5 7→9、d7 7→8。

## 三、执行方式（补丁层铁律）

- op 前缀 `dw4-*`；tri-meta settle op 就地更新 1.2.8→1.2.9；CHANGELOG 追加条目；`version-lint --apply-docs`；apply 连跑幂等。

## 四、审批

- [ ] AskUserQuestion 通过
- [ ] Approved 翻 yes（注明日期）
- [ ] apply + 幂等回执 + paired 评审
