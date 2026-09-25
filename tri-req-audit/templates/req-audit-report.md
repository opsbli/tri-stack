# 需求文档审核报告（req-audit-report.md）

> 由 `tri-req-audit` 产出。落盘位置：`.tribro/req-audit/<命名>/req-audit-report.md`。
> 本模板由 `scripts/audit_precheck.py` 的输出 + Agent 的语义维复核填充。**NEVER 省略「结论可信度」区**。

---

## 一、输入来源

| 项 | 值 |
|---|---|
| 审核对象 | `{{requirements_path}}` |
| 审核范围 | {{scope}}（缺省 = 全量九章 + 八维 D1–D8） |
| 审核视角 | {{perspective}}（缺省 = 全岗位就绪度矩阵） |
| 上游态 | {{upstream_state}}（A 快照 / B 引导安装 / C 降级） |
| 输入来源标注 | {{input_source}}（`snapshot` / `direct` / `degraded`） |
| 结构形态 | {{structure_mode}}（standard / non-standard） |

## 二、门② 前置三重校验结果

> 可机器判定部分来自 `scripts/audit_precheck.py`（附其 JSON 摘要）；语义部分由 Agent 逐条给出证据。

### 2.1 结构完整性

| 检查 | 结果 | 证据 |
|---|---|---|
| 九章齐备 | {{chapters_ok}} | 缺：{{missing_chapters}} |
| 关键字段非空 | {{fields_ok}} | {{empty_fields}} |
| 占位符残留 | {{placeholder_ok}} | {{placeholders}} |

### 2.2 证据溯源（D8）

| 检查 | 结果 | 证据 |
|---|---|---|
| 业务规则有 PRD 出处 | {{rule_source_ok}} | {{rules_without_source}} |
| 交互规则有原型出处 | {{interaction_source_ok}} | {{interactions_without_source}} |
| 冲突项标「PRD 优先」 | {{conflict_marked_ok}} | {{conflicts_unmarked}} |
| 保真度如实 | {{fidelity_ok}} | {{fidelity_note}} |

### 2.3 下游可消费性（tri-coding 门②）

| 检查 | 结果 | 证据 |
|---|---|---|
| 验收标准可判定（D3） | {{acceptance_testable_ok}} | {{untestable_acceptance}} |
| 技术约束齐备 | {{tech_ok}} | {{tech_gaps}} |
| 待补充项已定级并说明影响 | {{pending_ok}} | {{pending_gaps}} |

## 三、市面 skill 委派记录（门③）

| 优先级 | 候选 slug | 探测结果 | 是否调用 | 调用结果 | 解析状态 |
|---|---|---|---|---|---|
| 1 | `prd-review` | {{p1_probe}} | {{p1_called}} | {{p1_result}} | {{p1_parse}} |
| 2 | `requirement-testability-review` | {{p2_probe}} | {{p2_called}} | {{p2_result}} | {{p2_parse}} |
| 3 | `bg-requirement-review` | {{p3_probe}} | {{p3_called}} | {{p3_result}} | {{p3_parse}} |

**委派结论**：`delegation={{delegation}}`（`delegated` / `unavailable`）
**原始回执**：见同目录 `delegation-receipts.json`

## 四、问题清单（聚合后 · 去重 + 冲突已裁决）

| # | 级别 | 维度 | 问题 | 证据位置 | 来源 | 修订建议 |
|---|---|---|---|---|---|---|
| 1 | {{level}} | {{dim}} | {{issue}} | {{evidence}} | {{origin}} | {{suggestion}} |
| 2 | | | | | | |

> **来源**列取值：`local`（本地校验）/ `<slug>`（市面 skill 回执）/ `both`（双来源指认，已去重）。
> **冲突分歧**（本地「可消费性」判据与市面 skill 结论不一致）单列于 §五。

## 五、分歧与裁决记录

| # | 分歧点 | 本地判据结论 | 市面 skill 结论 | 裁决 | 理由 |
|---|---|---|---|---|---|
| 1 | {{divergence}} | {{local_view}} | {{external_view}} | {{ruling}} | 家族下游契约优先 |

> 无分歧时写「无」。

## 六、岗位就绪度矩阵

| 岗位 | 就绪度 | 阻塞项 |
|---|---|---|
| 产品 | {{ready_pm}} | {{block_pm}} |
| UX | {{ready_ux}} | {{block_ux}} |
| 前端 | {{ready_fe}} | {{block_fe}} |
| 后端 | {{ready_be}} | {{block_be}} |
| 测试 | {{ready_qa}} | {{block_qa}} |

> 就绪度取值：`可开工` / `待澄清` / `不可开工`。兜底审核（未委派）时本矩阵由本地八维判据推导，
> MUST 在 §七 声明其覆盖弱于委派模式。

## 七、结论可信度（**必填，NEVER 省略**）

| 项 | 内容 |
|---|---|
| 审核模式 | {{audit_mode}}（委派审核 / 兜底审核） |
| 覆盖说明 | {{coverage_note}} |
| 未覆盖 | {{uncovered}} |

## 八、开工判定

> **判定 = {{verdict}}**（`阻断开工` / `有条件开工` / `可开工`）

| 判据 | 计数 |
|---|---|
| P0 阻断 | {{count_p0}} |
| P1 需澄清 | {{count_p1}} |
| P2 建议改进 | {{count_p2}} |

- `阻断开工` ⟺ P0 ≥ 1 → **回炉 `tri-prototype`**，修订后重审
- `有条件开工` ⟺ P0 = 0 且 P1 ≥ 1 → 列入修订清单，建议 `tri-grill` 对齐后进 tri-coding 门②
- `可开工` ⟺ 仅 P2

## 九、后续建议

| 项 | 建议 |
|---|---|
| 回炉对象 | {{rework_target}} |
| 对齐建议 | {{align_suggestion}}（建议转 `tri-grill` 的条目清单） |
| 市面 skill 安装建议 | {{install_hint}}（兜底审核时必填：建议安装的首个候选 + 安装命令） |

---

## 审核元数据

| 项 | 值 |
|---|---|
| 审核时间 | {{audited_at}} |
| 审核对象版本 | {{requirements_rev}}（文件 mtime / git rev） |
| 审核模式 | {{audit_mode}} |
| 委派状态 | `delegation={{delegation}}` |
| 问题总数 | {{total_issues}}（P0 {{count_p0}} / P1 {{count_p1}} / P2 {{count_p2}}） |
