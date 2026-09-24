# 协作编排（tri-orchestrate）

> 将规划文档拆分为多份独立 spec，分给多人/agent 并行执行，收集回执并自动回写总任务清单。

## 使用

```bash
# 1. 拆分
python tri-orchestrate/scripts/split-specs.py --input <requirements.md> --team 4

# 2. 分配（编辑 dispatch-plan.md 确认负责人）

# 3. 并行执行（每个 spec 在独立 AI 会话中运行 tri-coding）

# 4. 收集回执
python tri-orchestrate/scripts/collect-receipts.py --specs-dir .tribro/coding/<命名>/specs/ --dashboard
```
