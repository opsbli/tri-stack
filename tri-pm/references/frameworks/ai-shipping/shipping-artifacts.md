---
name: shipping-artifacts
description: 让 AI 生成（vibe-coded）应用在上线前可被评审的那套长效文档集——「核心集」（架构、用户/权限流、权限、变量与密钥、测试覆盖映射）+「条件集」（邮件、定时任务、SEO、嵌入式 agent/自动化，仅在该能力存在时才产）；规定每篇文档必须捕获什么、评审者怎么用它。
source: pm-skills-main/pm-ai-shipping/skills/shipping-artifacts/SKILL.md
domain: AI 交付
---

# 交付文档集（shipping-artifacts）

> 蒸馏自 `shipping-artifacts`｜域：AI 交付｜源词数：1359
> 源文件 1359 词，单文件超 900 上限，**按规格拆为三部分**，只切分说明性散文的落点，**成员清单、触发条件、必须捕获项逐条完整保留**：
> - 本文件（part1）：集合总览 + 核心集/条件集**成员清单** + 组织方式 + 输出模板与命名
> - `shipping-artifacts-part2.md`：**核心集 5 篇**逐条明细（必须捕获什么 / 评审者怎么用）
> - `shipping-artifacts-part3.md`：**条件集 4 篇**逐条明细 + 关键规则（源 Notes）

## Purpose（用途）

AI agent 写代码很快，但不留下任何关于**意图**的长效记录——系统应该做什么、谁被允许做什么、密钥住在哪、哪些规则真的被验证过。没有这份记录，没有任何人（也没有任何审计 agent）能判断代码是否可以安全上线。本技能定义那一小组恢复「可评审性」的文档。

这些文档住在仓库根目录的 `documentation/`，写给**两类读者**：人类评审者，和下一个 AI 编码 agent。它们是后续每一次审计的**「应然状态」那一半**——一次安全或性能评审的质量上限，就是它能拿来跟代码比对的那份意图的质量。

## 必含章节清单（MUST-SECTIONS）

即**核心集（Core docs）**——每个可评审的应用都有这些面，所以**始终产出**：

- [ ] `architecture.md` — 架构：系统是什么、怎么拼起来的
- [ ] `flows.md` — 用户/权限流：权限与副作用真正被行使的那些旅程
- [ ] `permissions.md` — 权限：谁被允许做什么
- [ ] `variables.md` — 变量与密钥：配置与密钥，映射到风险
- [ ] `tests.md` — 测试覆盖映射：哪些成文规则真的被检查了

> 源 SKILL.md 自身的章节结构为：Purpose / How the set is organized / Core documents / Conditional documents（include only when the capability exists）/ Notes。

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

即**条件集（Conditional docs）**——**仅当该能力确实存在时才纳入**；能力存在则必产，能力不存在则在 `architecture.md` 里一行说明，**绝不发明空文档**。触发条件逐条：

- [ ] `emails.md` — 邮件：**仅当**应用发送事务性或自动化邮件
- [ ] `cron.md` — 定时任务：**仅当**存在定时或后台作业
- [ ] `seo.md` — SEO：**仅当**存在公开/可索引或面向 bot 的路由
- [ ] `automation.md` — 自动化：**仅当**应用嵌入了 AI agent、LLM 工作流、tool-calling、webhook 或外部自动化

## 逐段引导问题

### How the set is organized（这套集合怎么组织）

这套集合**不是**一份固定清单，而是**一个小的 core（核心）+ 若干 conditional（条件）**，条件文档只在该能力存在时才加。

- **Core docs**：每个可评审的应用都有这些面，所以**始终产出**。
- **Conditional docs**：只在应用确实有该能力时纳入一篇。**如果没有，就在 `architecture.md` 里写一行**（源例句：「No scheduled work — no `cron.md`.」）**而不是发明一篇空文档**。可评审性来自一张**诚实的地图**，而「我们不做 X」本身就是地图的一部分。
- 大多数文档由 `document-app` **从代码逆向**得到。**唯一的例外是 `tests.md`**，它由 `derive-tests` **从其他文档派生**——它是**验证映射**，不是对某个子系统的描述。

对当前状态要**残酷地诚实，但不要疑神疑鬼**（brutally honest without being paranoid）。任务是一张准确的地图，不是一张健康证明。每篇文档都要短、**以表格与要点为主**、跳过泛泛的理论。

（核心集 5 篇的逐条明细见 part2；条件集 4 篇的逐条明细见 part3。）

## 输出模板

```markdown
（源文件未给出单篇文档的输出骨架，规定的是产物集合的落盘形态：）

documentation/
  architecture.md   # 核心 · 含 Related Documents 索引
  flows.md          # 核心
  permissions.md    # 核心
  variables.md      # 核心
  tests.md          # 核心 · 由 derive-tests 派生
  emails.md         # 条件
  cron.md           # 条件
  seo.md            # 条件
  automation.md     # 条件
```

## 输出命名规则

固定文件名（如上），统一落在**仓库根目录的 `documentation/`** 下。**不写「updated date」行**——文件自身的历史才是事实源。

## 关键规则

见 part3 的「关键规则（源 Notes，逐条）」——源 Notes 共 6 条。

## Checkpoint

（源未设 checkpoint）

## Further Reading

（源未提供 Further Reading）
