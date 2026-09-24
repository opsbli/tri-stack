# 回执格式规范

## 必填字段（7 个）

| 字段 | 类型 | 说明 |
|---|---|---|
| spec_id | string | 关联的 spec 编号 |
| status | string | completed / blocked / partial |
| assignee | string | 执行人 |
| files_changed | string[] | 变更的文件路径列表（用于冲突检测） |
| tests_passed | boolean | 测试是否通过 |
| blockers | string[] | 阻塞项（空数组 = 无阻塞） |
| completed_at | string | 完成时间（ISO 8601） |

## 冲突检测

每次回执到达后，检查 files_changed 与其他已完成 spec 的交集。
非空交集 → 标注潜在合并冲突。
