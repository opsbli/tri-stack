# 变更日志

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
