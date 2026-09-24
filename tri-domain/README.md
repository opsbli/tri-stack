# 领域建模（tri-domain）

> 维护项目的领域模型：术语表（CONTEXT.md）+ ADR + 边界场景清单。

## 使用

```
用户：「记录一个决策：我们选了 PostgreSQL 而不是 MongoDB，因为事务一致性要求」
     → tri-domain 写入 docs/adr/0001-postgres-for-write-model.md

用户：「『提交』在这个项目里到底是什么意思？」
     → tri-domain 在 CONTEXT.md 中创建术语条目
```

## 消费者

- tri-grill（质询对齐时引用术语表和 ADR）
- tri-coding 门②（设计时遵循 ADR）
- tri-review（审查时检查是否遵循术语表）
