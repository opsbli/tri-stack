---
name: shipping-artifacts-part3
description: shipping-artifacts 续篇（part3）——条件集 4 篇文档（emails / cron / seo / automation）的触发条件、必须捕获内容与评审用法，以及全集合的关键规则（源 Notes）。
source: pm-skills-main/pm-ai-shipping/skills/shipping-artifacts/SKILL.md
domain: AI 交付
---

# 交付文档集 · 条件集与关键规则（shipping-artifacts-part3）

> 蒸馏自 `shipping-artifacts`｜域：AI 交付｜源词数：1359
> **本文件是 `shipping-artifacts.md` 的续篇（part3）**，因单文件超 900 词上限而拆出。总览与成员清单见 part1，核心集 5 篇明细见 part2。
> 拆分只切分了说明性散文的落点，**触发条件、必须捕获清单、评审用法逐条完整保留**。

## Conditional documents（条件文档 · 仅当该能力存在时才纳入）

条件集的门槛是**能力是否真的存在**，不是「想不想写」。**能力存在 → 该篇必产；能力不存在 → 在 `architecture.md` 里写一行说明，绝不发明空文档。**

6. **`emails.md`** — 系统发出的每一种通知。*触发条件：**仅当**应用发送事务性（transactional）或自动化邮件。*
   - **必须捕获**：**queue → processor → provider** 这条路径；模板以及它们接受的变量；retry/backoff（重试与退避）行为；发送失败时该去哪里看。
   - **评审者怎么用**：发现未经校验的模板输入，以及 PII 暴露边界。

7. **`cron.md`** — 所有定时工作以及如何安全运维它们。*触发条件：**仅当**存在定时或后台作业（scheduled or background jobs）。*
   - **必须捕获**：一张清单表（**job → schedule → function → secrets → limits → retry**）；每个作业如何保持**幂等（idempotent）**；内部调用如何鉴权；到哪里看上次运行记录。
   - **评审者怎么用**：找出**可伪造的触发器（forgeable triggers）**和无界的后台作业。

8. **`seo.md`** — 单页应用（SPA）如何处理 SEO 与社交预览。*触发条件：**仅当**存在公开/可索引（public/indexable）或面向 bot 的路由。*
   - **必须捕获**：预览方案（**static meta / prerender / edge HTML**）；一张 **route → needs-SEO → public-data-only** 表；动态元数据如何被消毒（sanitized）；bot-vs-human 路由分流。
   - **评审者怎么用**：抓住 **public-data-only 违规**，以及 bot 路由上的**元数据注入（metadata injection）**。

9. **`automation.md`** — 嵌入式 agent 与其他自动化路径。*触发条件：**仅当**应用嵌入了 AI agent、LLM 工作流、tool-calling、webhook 或外部自动化。*
   - **必须逐个 automation/agent 捕获**：
     - **trigger + owner**，以及它是**自动运行**还是**仅在批准后运行**；
     - 它可以读取的 inputs，以及它**可以调用的确切 tools/APIs**（**tool surface 本身就是一道硬护栏**）；
     - **steering（引导）住在哪里（即 prompt）** vs. **non-prompt hard guardrails（非 prompt 的硬护栏）**；
     - 回给应用的 **output contract（输出契约）**：schema、校验、失败处理；
     - **app-owned side effects（应用拥有的副作用）vs. agent-owned suggestions（agent 拥有的建议）**；
     - 控制项：approval gates（批准闸门）、audit/timeline logging（审计与时间线日志）、rate limits（限流）、retries（重试）、kill switch（急停开关）。
   - **评审者怎么用**：让**隐藏的自动化路径变可见**，并划清 agent **提议（proposes）**什么与应用**执行（enforces）**什么之间的界线——**这是现代 AI 生成应用中风险最高的一个面**。

## 关键规则（源 Notes，逐条）

- 每一篇产出的文档都要在 `architecture.md` 的 "Related Documents" 段里加一条指向自己的引用，让整套集合保持**可发现**。
- **跳过任何不适用的条件文档，并用一行说明这件事**，而不是发明内容。
- **把示例和成品模板排除在这些文档之外**——它们描述的是**这个**系统，不是通用方法。
- Agent 运行上下文文件（`CLAUDE.md` / `AGENTS.md`）是**另一种产物**：它是从这些文档**派生出来的指令**，不是系统文档。它在交接（handoff）步骤由 `ship-check` 产出，**不在这里产**。
- `tests.md` 由 `derive-tests` 产出；其余全部由 `document-app` 产出。
- **不要写「updated date」行**——文件自身的历史才是事实源。

## 与 intended-vs-implemented 的关系

本集合是**「应然」的那一半**；`intended-vs-implemented` 负责拿它去比对代码的**「实然」**，且**缺口两侧都必须有 `file:line` 级引用**。因此：

- 文档缺失或过期 → 这本身就是审计的第一条发现，先补文档再审计。
- 文档里写了但代码没执行 → 独立成立的一条发现，按「跨过缺口暴露什么」定级。

## Checkpoint

（源未设 checkpoint）

## Further Reading

（源未提供 Further Reading）
