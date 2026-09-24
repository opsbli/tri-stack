# 质询对齐（tri-grill）

> 逐条质询直到共识：挑战模糊术语 → 发明边界场景 → 记录 ADR → 精化文档 → 确认对齐完成。

## 使用

```
用户：「帮我质询这个 requirements.md，确保我们对齐了再开始编码」
     ↓
tri-grill 逐条过文档（六维：歧义/边界/反例/术语/依赖/优先级）
     ↓
调用 tri-domain 记录新决策（ADR）和术语
     ↓
就地精化文档（标注 [已对齐]）
     ↓
产出精化后的 requirements.md + 质询记录
```

## 消费者

- tri-coding 门②（消费精化后的 requirements.md）
- 团队成员（通过 CONTEXT.md 术语表对齐理解）
