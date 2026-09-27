# optimizer-contract —— 独立优化器模型契约（SkillOpt reflection 阶段）

> 生成：2026-09-27，SkillOpt 落地批 item 5。
> 论文依据（arXiv 2605.23904）：优化器与目标模型**同源**时自诊断偏差显著；
> 独立强优化器跨模型可恢复 56%–74% 增益。darwin-skill 黑名单 #1 已自认同会话自诊偏差。

## 一、角色定义

| 角色 | 承担者 | 职责 | 禁止 |
|---|---|---|---|
| **Rollout 执行者** | 通用子 agent（同会话可） | 带 skill 跑 golden case，产出 trace | 解释失败原因 |
| **Reflection / Optimizer** | **独立子 agent，换模型档**（reasoning 档），冷启动 | 读 trace 路径 → 现场诊断 → 产出 op candidate | 直接改文件、直接落 manifest、跑 apply.py |
| **Gate** | `apply.py --dry-run` + `version-lint.py` + `run_eval --split val` | 三门全过才 keep | 跳过任一门 |
| **裁定** | paired 3-judge（同-judge 配对，多数决） | op candidate 的 keep/revert | 用绝对分裁定 |

**同源禁令（本契约的核心）**：reflection 子 agent MUST 与 rollout 会话不同实例、
不同模型档、无共享对话上下文。同会话自诊 = 论文实证的偏差源 = 违反本契约。

## 二、输入输出契约

**输入**（只给地图，不给正文 —— Meta-Harness 消融：Full traces 50.0 vs Scores-only 34.6）：

```
trace_store.py map --run-id <R> --json        # 只回传路径
# optimizer 自行按需：
trace_store.py show --run-id <R> --case-id <C> # 走到现场
gate_adapter.py run --skill <S> --json          # 复跑门禁取证
```

**输出**（op candidate，**不落 manifest**）——写入
`ops/eval-harness/op-candidates/<date>-<slug>.json`：

```json
{
  "candidate_id": "cand-20260927-tri-lottie-t3",
  "trigger_cases": ["tri-lottie-envelope-01"],
  "diagnosis": "版本四件套 tests=1.0.2 滞后（skill/changelog=1.0.5）",
  "ops": [ { "type": "settle…", "target": "…", "…": "…" } ],
  "expected_effect": "tri-lottie-envelope-01 → pass（val 分数 0.8→1.0）",
  "risk": "……"
}
```

## 三、流程（一次迭代 = 一个 iteration）

```
1. run_eval.py --split val --run-id iter-<N>          # 基线分数
2. spawn 独立 optimizer（换模型档，冷启动）
   输入：trace 路径 + coverage.md（ROI 边界）+ 本契约
   输出：op candidate JSON
3. paired 评审：candidate 的 ops 生成 → 3-judge 多数决 keep/revert
4. keep ⇒ 由人（D30 proposal → AskUserQuestion → flip yes）放行入 manifest 批
5. 重放补丁层 → version-lint → run_eval --split val 复测
6. 分数不升反降 ⇒ revert（回滚 + 就地改 op，勿新增纠错 op）
```

## 四、禁止事项（黑名单，照搬论文会踩的坑）

1. ❌ optimizer 直改 SKILL.md —— 违反铁律 1；一切修正走 op 重放。
2. ❌ 同会话 / 同模型自诊 —— 本契约 §一 同源禁令。
3. ❌ 用 LLM judge 绝对分当 val 分数 —— 只认 command / gate_envelope 的确定性判定。
4. ❌ 一次改多个维度 —— 归因不可分；一个 candidate 只对一个 trigger_cases 集合负责。
5. ❌ 用 test split 调 skill —— test 仅终局跑一次（防过拟合）。
6. ❌ 无预算全量重写 —— 论文实测低 2–3 分；小步 op 优先。
7. ❌ 漏版本线 —— 版本 settle op 在 `sync-*` 前 + `sync_version_meta` 同批 + version-lint 0。
8. ❌ 优化 C 档 skill —— coverage.md C 档 31 份无 pass/fail，显式排除。

## 五、成本口径

论文复杂轨迹类 benchmark 每涨 1 分需 37.9–46.4M token。本仓约束：
只在 A 档 4 skill（coverage.md §二）开训练循环；B 档须先补任务级 scorer；
单 iteration 的 val 复测 ≤ 13 case（2026-09-27 pilot 规模），超预算先收缩 case 集。
