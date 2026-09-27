# iteration 1 报告 · tri-forge-envelope-01（eval-harness 训练循环首跑）

> **日期**：2026-09-27 ｜ **基线 run**：`btier2-20260927`（24 执行 23 过）｜ **终态 run**：`iter1-final-20260927`（25 执行 24 过，96.0%）
> **流程**：optimizer-contract §三（val 基线 → 独立优化器 → op candidate → paired 3-judge → 处置）

## 一、独立优化器（reasoning 档，冷启动，只给路径）

- **结论**：`no-op`（op-candidates/20260927-iter1.json）
- **诊断**：复现 FAIL:#11；`git show HEAD` 证实**已提交态版本线一致**（1.0.5=1.0.5，门禁本应 PASS）——失败纯系脏工作区：并行在途批次新增 1.2.0 CHANGELOG 条目而 frontmatter 未 settle，评估测到中途在途态；optimizer 介入会与在途批次双重记账。
- **改进建议（超出主会话归因的增量）**：门禁型 case 宜在**干净 worktree** 跑，防脏树污染判定。

## 二、paired 3-judge 盲评（lite 档 ×3，顺序轮换消位置偏差）

| judge | 盲票 | 实际指向 |
|---|---|---|
| judge-1 | A（A=优化器） | 优化器 |
| judge-2 | B（B=优化器） | 优化器 |
| judge-3 | A（A=优化器） | 优化器 |

**3/3 多数：优化器诊断 keep**。共性理由：有 git HEAD 证据链 + 两个低风险动作（补 settle / 干净 worktree）；主会话版本「无证据仅断言、动作被动」。

## 三、处置

1. **no-op keep**：tri-forge #11 维持登记，等在途批次落地后复测转 pass。
2. **采纳 harness 改进**（列入后续项）：门禁型 case 的干净 worktree 运行模式。
3. **迭代产出**：tri-code-analyzer 新增 stack-02（Flutter fixture，hit=true 主信号必中分支覆盖），val 台账 24→25 case。

## 四、iteration 级复盘

- 同源禁令机制有效：独立优化器产出了主会话未有的证据链（git show HEAD）与改进项。
- 盲评协议有效：judge 在不知来源情况下 3/3 收敛，且给出一致的质量区分理由。
- 成本：优化器 1 agent（reasoning）+ 3 judge（lite）≈ 4 次子代理调用/iteration。
