# 变更日志

## [1.0.0] - 2026-09-24

### 新增

- **首版发布**：协作编排 skill——拆分需求 → 分配 → 并行执行 → 回执收集 → master-todo 自动回写
- split-specs.py：spec 拆分器（按功能点边界 + 依赖关系 + 人数）
- collect-receipts.py：回执收集器 + master-todo 回写 + 冲突检测
- 回执格式规范（7 字段 JSON）
- 模板：master-todo / dispatch-plan / spec
