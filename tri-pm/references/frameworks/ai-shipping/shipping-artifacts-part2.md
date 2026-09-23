---
name: shipping-artifacts-part2
description: shipping-artifacts 续篇（part2）——核心集 5 篇文档（architecture / flows / permissions / variables / tests）逐条的「必须捕获什么 · 评审者怎么用」。
source: pm-skills-main/pm-ai-shipping/skills/shipping-artifacts/SKILL.md
domain: AI 交付
---

# 交付文档集 · 核心集明细（shipping-artifacts-part2）

> 蒸馏自 `shipping-artifacts`｜域：AI 交付｜源词数：1359
> 本文件是 `shipping-artifacts.md` 的续篇。总览与成员清单见 part1，条件集明细与 Notes 见 part3。

## Core documents（核心文档）

每条格式：**文件 · 一句话用途 · 必须捕获什么 · 评审者怎么用**。

### 1. `architecture.md` — 系统是什么、怎么拼起来的

- **必须捕获**：产品概览 + 关键假设；技术栈；auth/session/claims 端到端怎么流转；**信任边界**（例：service-role vs. client）；一份简短的 **Known risks / assumptions**（已知风险与假设）清单——**每条都要有它在代码中现身之处作为支撑，不能是一份泛泛的检查表**；以及一份索引所有其他已产出文档的 "Related Documents" 段。
- **评审者怎么用**：根文档——其余一切都从这里交叉引用出去。

### 2. `flows.md` — 权限与副作用真正被行使的那些旅程

- **必须捕获**：
  - 每一条承重流程（load-bearing flow）写成 **actor + precondition + success outcome**；
  - 跨 **UI → server → data → jobs → providers → agents** 的逐步序列；
  - **每一个受保护步骤上的 authz 检查**——哪个 claim/role/scope、作用在哪个 resource 上、以及**预期的 deny 情形**；
  - **信任边界穿越**（trust-boundary crossings）：browser→server、server→provider、job→app、agent→tool、webhook→app；
  - 每一步造成的状态变更与副作用：写入、入队的邮件、被触发的作业、对外调用。
- **评审者怎么用**：静态的 `permissions.md` 矩阵展示不出的**运行时视图**——授权在**哪里**、以**什么顺序**被执行，以及**它在哪里可以被跳过**。
- **Anti-PRD rule（反 PRD 规则）**：一条**不触及权限、数据完整性、外部副作用、金钱、隐私或运维安全**的流程**不属于这里**。这是一张安全/运维地图，不是一份功能规格。

### 3. `permissions.md` — 谁被允许做什么

- **必须捕获**：roles/claims；scope 从哪里推导（**token vs. DB**）；一张 **resource × operation × role** 矩阵；哪些表有 row-level security（RLS，行级安全）、哪些依赖代码里执行的检查。
- **评审者怎么用**：访问控制审计拿来跟代码比对的**基线**。`flows.md` 展示它运动中的样子，这里是**静态参照**。

### 4. `variables.md` — 配置与密钥，映射到风险

- **必须捕获**：一张 **Name · used-by · scope（server/client）· source · rotation · risk** 的表；**明确确认没有任何密钥被打包进客户端**（no secret is bundled client-side）；一份上线前检查表（pre-go-live checklist）。
- **评审者怎么用**：密钥/PII 泄露面，以及事故响应期间的轮换方案。

### 5. `tests.md` — 验证映射

一句话用途：哪些成文规则**真的被检查了**、哪些**只是被提议**、哪些**什么都没检查**。

- **必须捕获——分成三个清晰分隔的小节，让这张映射不可能读出「假绿」（can't read falsely green）**：
  - **Existing coverage（现有覆盖）**：**今天**就在仓库里的测试，每条绑定它所锚定的规则——让映射反映现实，不是愿望清单。
  - **Proposed tests（提议的测试）**：建议但尚未写的用例，**按测试类型标注**：automated unit/integration · guarded live · manual review。
  - **Gaps（缺口）**：完全没有任何验证的成文规则，**按跨过它会暴露什么来排序**。
- **每一行携带**：use-case → rule → expected behavior（**含 deny/negative 情形**）→ evidence source（**doc + code**）→ status（existing / proposed / none）。同时注明**哪些检查是 CI 必需的、并对合入 `main` 设门**。
- **评审者怎么用**：「documented == implemented」的**可操作形态**——显示其他文档声称的每条规则，今天是**真被测试锚定**、**只是被提议**、还是**未经验证**。
- **产出方**：由 `derive-tests` 产出（**不是** `document-app`），因为它是从其他文档与既有测试套件**派生**的，而不是从某个子系统读出来的。

## Checkpoint

（源未设 checkpoint）

## Further Reading

（源未提供 Further Reading）
