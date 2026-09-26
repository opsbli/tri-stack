# 变更日志

## [1.1.1] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.1.0] - 2026-09-25

### 新增

- **D9 对抗维（抗自证机制）**：在原有在场性判据之外新增对抗维——MUST 产出 ≥3 条可证伪错误场景，且 ≥1 条须落在其余维度判「通过」的条目上；报告**无「对抗式审查结论」小节即判违规**。理由：原有各维均为**在场性**判据（通过 = 确认存在），机制上无法自证「没有造假」。
- **`independence=` 独立性声明（报告必填）**：与 `delegation=` 并列的正交字段，取值 `same-agent` / `cross-context` / `cross-model`。同源时 MUST 写明「非独立第三方」且全文禁用「独立审核 / 独立第三方」字样。**安装市面 skill 不改变该取值**——委派是同一 agent 加载另一 skill 的 prompt，仍属同源。
- **跨轮单调性守卫 + `round-ledger.jsonl`**：新增第四件落盘产物（每轮追加 `{round, p0, p1, p2, new_evidence, changes, verdict}`）。门④ 读账本执行守卫：**P0 / P1 下降而 `new_evidence=0` ⇒ 判「收敛造假」嫌疑，强制升级人审**；任一 P 级降级 MUST 附新证据，否则驳回。
- **可复算证据（H5）**：每条 P0 / P1 MUST 附 `文件:行号` + 原文引文；无引文者降为 P2 并标 `evidence=unverifiable`。
- **机械守卫 `scripts/audit_gate.py`（新增）**：把 D9 / 独立性 / 可复算 / 单调性四条规则落成可执行判据（R1 / R2 / R3 / R4 / L2），附 `--self-test` 夹具（含「删掉对抗小节必判违规」反例），使上述规则**不可被形式化跳过**。
- **对抗层委派（可选增强）**：登记家族外 `metago-adversarial-review` 为对抗委派候选；未安装时降级为内置 D9 并如实登记 `delegation.adversarial=unavailable`。

### 变更

- 判据集口径由「八维」更新为「九维（D1–D9）」；`templates/req-audit-report.md` 增「对抗式审查结论」小节与 `independence=` 字段；`tri-forge/references/family-spec.md` §五 登记对抗委派二跳。
- **修订动因**：原判据集全为在场性检查、无对抗抵抗、跨轮无单调性守卫 —— 多轮迭代下 P0 可在零新证据时被收敛为 P2（「自审自过」）。取证与设计见 `reports/proposal-req-audit-adversarial-20260925.md`。

## [1.0.0] - 2026-09-25

### 新增

- **首版发布**：需求文档审核 skill——对 `tri-prototype` 产出的 `requirements.md` 做开工前审核
- **三阶段流水线**：前置本地校验（家族专有）→ 市面 skill 二跳委派 → 结论聚合与判定
- **三重前置校验**：结构完整性 / 证据溯源 / tri-coding 门② 可消费性
- **二跳委派**：中介 = 本 skill，被执行方 = 市面 PRD 审核 skill；调用契约与优先级见 `references/market-prd-review-skills.md`
- **八维自带规则**：D1 完整性 / D2 无歧义 / D3 可测性 / D4 边界异常 / D5 状态闭环 / D6 权限角色 / D7 数据字段 / D8 证据溯源
- **分级判定**：P0 阻断开工 / P1 有条件开工 / P2 可开工；反规避——NEVER 因催促下调级别
- **可执行实现**：`scripts/audit_precheck.py`（结构 / 溯源 / 可测性形态 / 待补充项定级的确定性判定）
- 上游依赖检测三态（快照模式 / 引导安装 / 降级模式）
- 版本门节采用家族 `version-stub v1` 瘦指针形态

### 设计边界

- **不改原文**：只产问题清单与修订建议，文档修订属 tri-prototype 回炉
- **不磨共识**：与 tri-grill 并列分工（tri-grill 对齐导向 / 本 skill 质量导向），非上下游
- **不注册 downstream**：内部专用工具，二跳形态登记于 `tri-forge/references/family-spec.md` §五
