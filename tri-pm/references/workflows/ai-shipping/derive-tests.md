---
name: derive-tests
description: 把成文意图转成测试覆盖映射——清点今天已存在的测试、从系统文档派生用例、把现有覆盖与提议测试及未验证缺口分开、逐条标注 unit / integration / guarded-live / manual，并建议一道「绿灯才可合入」的 CI 门。
source: pm-skills-main/pm-ai-shipping/commands/derive-tests.md
domain: AI 交付
---

# /derive-tests → 把意图变成测试

> 蒸馏自命令 `derive-tests`｜域：AI 交付｜源词数：1222
> **语法翻译**：源项目以 `/derive-tests` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤。源文对 `/document-app`、`/security-audit-static`、`/ship-check` 的斜杠引用一律理解为**编排到对应工作流文件**。
> 源 1222 词，**按规格拆为两部分**；步骤 4–6、输出模板、CI 门与 Notes 见 `derive-tests-part2.md`。**测试类型四分法、状态三态、证据来源格式（doc + code / `file:line`）绝不拆丢**。

## 用途

文档说系统**应该**做什么；审计找出代码**没做到**的地方；**测试是让那个缺口在下一次 AI 编辑后不会重开的东西**。本流程读取成文意图，把每一条承重规则变成一个具体测试用例，分类成「该自动化的 / 需要受控实跑的 / 只能人工的」，然后建议那道让 `main` 保持诚实的 CI 门。

它产出的是一张**覆盖映射（`tests.md`）+ 具体测试用例，不是一套写完的测试**——确定性的那些由你或下一个 agent 去实现。

## 参数提示

`<repo path or area; defaults to the whole repository>`（仓库路径或某个区域；缺省为整个仓库）

## 调用示例（翻译为对话形态）

- 源：`/derive-tests` → 「为整个仓库派生一张测试覆盖映射」
- 源：`/derive-tests the checkout flow` → 「为 checkout 流程派生测试覆盖映射」
- 源：`/derive-tests supabase/functions` → 「为 supabase/functions 派生测试覆盖映射」

## 前提：成文意图（Prerequisite）

测试是**从文档派生**的，所以**文档先行**。若 `documentation/*.md` 缺失或过薄，先走 `document-app` 流程（本流程**最重度依赖** `flows.md`、`permissions.md`、`automation.md`）。**你无法为从未写下来的规则做覆盖映射——意图缺席之处，就说它缺席，而不是发明规则去测。**

## 工作流步骤（1–3）

1. **读意图 —— 以及已经存在的测试**
   - 读适用的系统文档（architecture、flows、permissions、variables，以及 emails / cron / seo / automation 中已存在的那些）。用 **shipping-artifacts** 技能判断每篇文档该有什么；用 **intended-vs-implemented** 技能守住那条纪律：**把文档当作待验证的声明，不是当作证明**。〔引用技能：`**shipping-artifacts**`、`**intended-vs-implemented**`〕
   - 然后**清点既有测试套件**：有哪些测试文件、它们**实际断言了什么**、今天在 CI 里跑的是什么。**你产出的映射必须把「现在就存在的覆盖」与「你正在提议的覆盖」区分开**；跳过这一步会得到一张**假绿的映射**——声称规则被锚定，实则无人检查。**如果没有测试，就明说——这本身就是一条发现。**

2. **抽出值得测的规则** — 挑出**承重且确定性**的规则，即那些一旦被违反就**跨越信任、数据、金钱、租户或隐私边界**的规则（逐条照抄）：
   - 授权的 **allow 与 deny 两种**情形（尤其是 `flows.md` 里的边界穿越与 `permissions.md` 里的矩阵）；
   - 每个 sink 上的输入校验与输出编码；
   - 作业的幂等性与去重键（idempotency and dedup keys）；
   - **fail-closed 默认值**（error / timeout / cache-miss / flag 这些**必须拒绝而不是放行**的路径）；
   - 副作用触发条件（一封邮件到底何时发出、一次写入何时提交、一个付费动作何时触发）；
   - 公开或 bot 路由上的 **public-data-only** 约束；
   - `automation.md` 里任何 agent 的 **output-contract 与 tool-surface 限制**。

   **跳过装饰性行为。一条规则值得一个测试，是因为搞错它会伤到行为者以外的人。**

3. **搭覆盖映射** — 一行一个 use case：**rule → expected behavior（含 negative case）→ evidence source（doc + code）→ test type → status（existing / proposed / none）**。**status 列是这张映射保持诚实的关键——只有当仓库里真有一个测试今天就断言它，才可以标 `existing`。**
   - **测试类型四分法（照抄）**：
     - **unit** — 纯粹且确定性，无外部服务。
     - **integration（deterministic）** — 针对本地或内存依赖（测试 DB、mock 的 provider）行使真实接线，**每次跑法一致**。
     - **guarded live** — 需要真实的外部 DB、邮件服务、LLM 或第三方。**只在显式 flag 后面跑，绝不进默认 CI 运行**。
     - **manual** — UI/视觉或判断题。是**评审者检查表条目**，不是自动化测试。
   - **CI 必须要求什么**：**确定性本地集** = unit + 确定性 integration，即那些**无实时依赖、每次跑法一致**的测试。决策逻辑能被隔离时**优先 unit**；规则住在接线里（middleware、RLS、auth guards）、只有「真实但本地」的依赖才能行使它时**才上 integration**。**guarded-live 与 manual 行永远不为默认运行设门。**
   - **policy shadow 警告**：见 part2「policy shadow 警告」一节（逐条照抄）——把只能实跑的规则抽成纯函数 helper**只能作为补充、不能作为替代**。

（policy shadow 警告全文、Checkpoint、步骤 4–6、输出模板、CI 门建议、保存指令与 Notes 见 `derive-tests-part2.md`。）

## Further Reading

（源未提供 Further Reading）
