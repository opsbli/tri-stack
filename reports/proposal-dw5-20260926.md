# Proposal · dw5 批（children 兜底章节 + tri-release 降级路径 + versions.json 重建）

- **Date**: 2026-09-26
- **Author**: agent
- **Approved**: yes (2026-09-26, AskUserQuestion「全部执行」；范围以本文件 §二 为准——children 兜底为执行中新发现的 #14 硬门禁缺口，属同批既有模式 f67–f74 的补齐)
- **Scope**: tri-sdlc/children ×9 + tri-release 维度 4 + ops/versions.json

## 一、证据（一手实测）

| 项 | 证据 |
|---|---|
| children 兜底缺口 | `compliance_check.py --dir` 实测 9/9 全部 `#14 兜底处理覆盖 = 🔴 FAIL`（无专门章节）；父级 tri-sdlc 有（f67 补）；顶层 26 全有（f67–f74 补）——P1 批只覆盖了顶层，children 层级漏扫 |
| tri-release d8 | 维度 3 有「无 CI → 本地等价流程」先例（L124），维度 4 预发布冒烟无任何降级路径；契约第 5 条（L28）无条件 MUST，存在「无预发布环境即死锁」的失败模式未编码 |
| versions.json | 机械对账：26 顶层全部落后 1–3 个 PATCH（停在 P1 批前）+ 9 children 完全缺席；WORKFLOW-GUIDE 已含 req-audit（先前 MEMORY 注记过期） |
| tri-cr 试点（取消） | 一手核对：所谓「三处重复」实为契约→红灯的带 §出处聚合（设计模式）+ 干净的验证维度表，无逐字冗余可去——指针化收益低于风险，**取消** |

## 二、执行内容

1. **children ×9 新增 `## 兜底处理（NEVER 静默失败）`**（插于「🔴 检查点与红灯清单」之前）：①版本检查异常 ②门禁不过→退回 tri-sdlc ③上游缺失→§上游依赖检测 ④hook 缺失（非触发源）——四行统一聚合既有语义；⑤**每份定制**（charter 立项材料不可判定澄清 / cr 静态工具不可用手工替代 / design Must 不可落点退回门② / devenv 环境不可搭登记阻塞 / impl 任务阻塞不跳任务 / ops 指标无法采手工巡检 / release 无预发布环境本地等价冒烟 / require AC 不可判定升级人审 / test 环境不可用最小子集+如实声明）。
2. **tri-release 维度 4 降级行** + 契约第 5 条加降级指针（消解「无预发布环境死锁」）。
3. **ops/versions.json 机械重建**：脚本从全部 SKILL.md frontmatter 取版本（26 顶层 + 9 children），保留 purpose/source_note 并更新 generated。
4. **归档** `reports/proposal-tri-verify-20260925.md`（用户裁定提交存档，Approved: no 维持）。
5. **验收**：#14 9/9 PASS、apply 幂等、version-lint EXIT=0、paired 评审。

## 三、执行方式

- op 前缀 `dw5-*`（20 op：章节 9 + release 2 + CHANGELOG 9）；settle 就地更新（6 份 1.1.4→1.1.5、3 份 1.1.5→1.1.6）。
- 模板四行为聚合既有语义（有 §出处），第⑤行为各 skill 契约内已有语义的显式化——禁止 blind 套用，逐份核对。
