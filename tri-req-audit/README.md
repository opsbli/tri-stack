# 需求文档审核（tri-req-audit）

![version](https://img.shields.io/badge/version-1.1.0-blue) ![license](https://img.shields.io/badge/license-MIT-green)

> 面向 tri-xxx 家族的**内部专用工具**：对 `tri-prototype` 产出的 `requirements.md` 做**开工前审核**——
> 先做家族专有的三重前置本地校验，再**二跳委派**市面 PRD 审核 skill，最后聚合为 P0/P1/P2 问题清单与修订清单。
> **只出问题，不改原文。**

## 特性

- **三阶段流水线**：前置本地校验（家族专有）→ 市面 skill 二跳委派 → 结论聚合与判定
- **三重前置校验**：结构完整性 / 证据溯源 / tri-coding 门② 可消费性——市面通用 skill **不知道门② 要消费什么**，故这一层只能本地做
- **二跳委派**：按注册表优先级委派市面 PRD 审核 skill（`prd-review` → `requirement-testability-review` → `bg-requirement-review`），调用契约与可用性探测均以 `references/market-prd-review-skills.md` 为单一事实源
- **降级有兜底**：市面 skill 全部不可用时改用自带 **D1–D9 九维规则**，分级标准与委派审核完全一致，**NEVER 因降级而放宽**
- **两级门禁 + 分级判定**：P0 阻断开工 / P1 有条件开工 / P2 可开工；反规避——**NEVER 因用户催促而下调级别**
- **门禁有牙**：三重校验的可机器判定部分由 `scripts/audit_precheck.py` 承担，语义维明确标注「须 Agent 复核」

## 与 tri-grill 的分工（并列，非上下游）

| | tri-grill | **tri-req-audit** |
|---|---|---|
| 导向 | **对齐**（问人） | **质量**（评文档） |
| 动作 | 逐条质询 → 就地改文档 → 产 ADR | 三重校验 + 委派 → 产问题清单（**不改原文**） |
| 产出 | 精化后的 `requirements.md` + 质询记录 | 审核报告 + 修订清单 |
| 一句话 | 磨共识 | 验质量 |

两者都在 `tri-prototype` 之后、`tri-coding` 门② 之前调用，**顺序不限**。

## 安装

```bash
python ops/install-skills.py --target <目标目录>
```

独立安装后本 skill 自包含（自带 `references/version-check-spec.md` 与 `scripts/check_update.py`），
不依赖仓库内其他 skill 的文件。

## 用法

```
用户：「审一下这份 requirements.md，能开工吗」
     ↓
门① 锁定路径 + 范围 + 视角
     ↓
门② 前置三重校验（脚本出逐条 JSON + Agent 复核语义维）
     ↓
门③ 探测市面 skill 可用性 → 按优先级委派 → 登记回执
     ↓
门④ 去重 → 冲突裁决（本地可消费性判据优先）→ 分级 → 判定
     ↓
门⑤ 落盘：审核报告 + 修订清单 + 委派回执台账
```

**产物**（全部落 `.tribro/req-audit/<命名>/`）：

| 产物 | 文件 |
|---|---|
| 审核报告 | `req-audit-report.md` |
| 修订清单 | `req-audit-fixes.md` |
| 委派回执台账 | `delegation-receipts.json` |

> `requirements.md` 本身属 `tri-prototype` 的产物区（`.tribro/coding/<命名>/`），本 skill **只读不改**。

## 目录结构

```
tri-req-audit/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── _meta.json
├── references/
│   ├── version-check-spec.md          版本检查执行规范（内部化持有）
│   ├── market-prd-review-skills.md    市面 PRD 审核 skill 注册表（委派契约真源）
│   └── audit-dimensions.md            九维审核规则 + 分级判据（本地判据真源）
├── scripts/
│   ├── check_update.py                版本门（与家族同源）
│   └── audit_precheck.py              前置三重校验（结构 / 溯源 / 可消费性）
├── templates/
│   └── req-audit-report.md            审核报告模板
└── tests/
    └── tri-req-audit-full-testcases.md
```

## 设计原则

1. **本地前置 + 外部借力，缺一不可**：市面 skill 强在通用产品视角，家族专有的「可消费性」判据只能本地做
2. **二跳形态显式登记**：本 skill 是中介，市面 skill 是被执行方——被执行方**不注册**为 tri-intent 下游，二跳形态登记于 `tri-forge/references/family-spec.md` §五
3. **委派诚实**：实际调用了谁、结果如何、解析是否成功，**三位一并登记**；NEVER 声称调用了而实际未调用
4. **不越界**：不改原文（→ tri-prototype）、不磨共识（→ tri-grill）、不审代码（→ tri-review）、不审 skill（→ tri-forge）
5. **降级不放水**：兜底审核与委派审核共用同一份分级判据
