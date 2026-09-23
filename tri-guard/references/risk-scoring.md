---
name: risk-scoring
description: tri-guard 的风险评分数值规则——严重级别点数 / 置信度缩放 / 同级递减权重 / 可执行文件乘数 / 严重带推荐映射 / 输出与退出码契约。确定性计算由 scripts/risk_score.py 完成。
---

# 风险评分与推荐契约（tri-guard）

> 单一事实源。grep 模式：`点数`、`严重带`、`推荐`、`退出码`。
> 确定性计算公式由 `scripts/risk_score.py` 落地（见 §五），prompt 层 NEVER 用散文重构公式，只调用脚本。

---

## 一、严重级别点数

| 严重级别 | 点数 |
|----------|------|
| CRITICAL | 50 |
| HIGH | 25 |
| MEDIUM | 10 |
| LOW | 5 |

## 二、评分计算

```text
score = Σ (每类每个发现的贡献值)
contribution = base_points × diminishing_weight × confidence × executable_multiplier
final_score = min(100, max(score_floor, round(score)))
```

解释：
- **置信度缩放**：clamp 到 `[0,1]`，置信度 0 的发现跳过计分（仍保留在结果）。
- **同级递减权重**：同一 `rule_id` 下第 1 次×1.0、第 2 次×0.5、第 3 次×0.25、第 4 次起忽略。
- **可执行文件乘数**：发现来自可执行脚本文件 ×1.3；纯文档文件不乘。
- **风险下限**：存在可信 SC8（携字节码）发现时分数至少为 51。
- **封顶**：最终分数在 `[0,100]`。
- **阈值**：`RISK_THRESHOLD = 50`。

## 三、严重带与推荐映射

| 分数 | 严重级别 | 推荐 |
|------|----------|------|
| 0–20 | LOW | SAFE |
| 21–50 | MEDIUM | CAUTION |
| 51–80 | HIGH | DO_NOT_INSTALL |
| 81–100 | CRITICAL | DO_NOT_INSTALL |

> 数值分数是**风险姿态**，不是裁决本身；最终裁决（APPROVE/CAUTION/REJECT）由 `references/semantic-review.md` §三 rubric 结合语义复核得出。

## 四、输出契约（供集成方/退出码对齐）

| 项 | 契约 |
|----|------|
| 严重级别集合 | `LOW / MEDIUM / HIGH / CRITICAL` |
| 推荐集合 | `SAFE / CAUTION / DO_NOT_INSTALL` |
| 裁决集合（tri-guard） | `APPROVE / CAUTION / REJECT` |
| CLI 退出码 | `0`=分数≤50（SAFE/CAUTION）；`1`=分数>50（DO_NOT_INSTALL）；`2`=错误 |
| SARIF 级别 | CRITICAL/HIGH→`error`；MEDIUM→`warning`；LOW→`note` |

## 五、确定性实现

score、带、推荐、退出码的确定性计算由 `scripts/risk_score.py` 完成，用法：

```bash
python scripts/risk_score.py findings.json      # 输出 {score, severity, recommendation, exit_code}
python scripts/risk_score.py findings.json --json
```

输入：OK 形状为引擎 finding 列表（或本 skill 降级轨自构造的 `{severity, rule_id, confidence, executable}` 列表）。输出保持此 reference 契约一致。