---
name: I21-distill
description: 【Doing·I21 蒸馏造物】用户要求把人/工作流/专业技能/事物/书籍等对象蒸馏、提炼、萃取、复刻为一个可复用的新 skill 时触发。核心产物是可独立调用的 skill，而非业务代码或普通文档。
---

# I21 蒸馏造物（Doing）

> 本项是 Doing 大类下 I21 的独立二级意图。核心动作是「把某个值得复用的存在蒸馏成一个新 skill」，产出物是一个可被 Agent 独立调用的 skill（含方法论/人格/流程的可复用封装），与编码开发（产业务代码）、内容生成（产文档）严格区分。

## 识别特征

- 核心动词为 **蒸馏 / 提炼 / 萃取 / distill / 复刻 / 造一个 skill / 把 XX 做成 skill / 沉淀成能力**
- 期望产出 = **一个新 skill**（可被 Agent 独立加载执行，非一次性答复、非业务代码）
- 蒸馏对象可为以下类型之一：
  - 人类（human）：某个人的思维/表达/决策方式（如「把张三的编程风格蒸馏成一个 skill」）
  - 工作流（workflow）：一套可复用的流程/步骤序列（如「把这套发布流程做成 skill」）
  - 专业技能（skill）：一门可操作的专业方法/手艺（如「把 TDD 方法论沉淀成 skill」）
  - 事物（thing）：书/视频/课程/文档等长内容中的知识框架（如「复刻这本书的方法论为 skill」）
  - 其它/通用（general）：跨类型混合或无法归入上述类型
- 典型语料：
  - 「把张三的编程风格蒸馏成一个 skill」→ I21，对象=人类
  - 「把这套发布流程做成 skill」→ I21，对象=工作流
  - 「复刻这本书的方法论为 skill」→ I21，对象=事物
  - 「造一个能复刻某人代码风格的 skill」→ I21，对象=人类
  - 「把这套评审流程沉淀成可复用的 skill」→ I21，对象=工作流

## 与邻近意图边界

- vs **I11 编码开发（tri-coding）**：I11 产出业务代码/程序，I21 产出可独立调用的 skill（含方法论蒸馏与 frontmatter 规范封装）。判定关键看用户最终期望——是「一段可运行的程序」还是「一个可复用的 skill 能力包」。
- vs **I13 规划拆解（tri-plan）**：I13 产出计划/步骤文档，I21 产出可执行的 skill 产物。规划是「拆解怎么做」，蒸馏是「把能力固化成 skill」。
- vs **I06 内容生成（tri-content）**：I06 产出文章/文档等文本内容，I21 产出结构化 skill（含 SKILL.md + 方法论 + registry 注册）。文档是内容，skill 是可调用的能力封装。
- vs **I16 头脑风暴（tri-bs）**：I16 产出发散性想法清单，I21 产出确定性的 skill 产物。头脑风暴是开放发散，蒸馏是收敛固化。

## 路由规则

| 字段 | 取值 |
|---|---|
| L1_交互类型 | B.Doing |
| L2_核心意图 | I21 蒸馏造物 |
| 下游路由建议 | tri-god（默认） |
| 落盘 | 快照（snapshot.md） |

> tri-god 内部再按蒸馏对象类型（human / workflow / skill / thing / general）从 `methodologies/registry.md` 驱动加载对应方法论，严格按该方法论阶段串行执行。tri-intent 仅负责识别 L2=I21 并路由到 tri-god，对象类型判定由 tri-god 在执行阶段完成。
>
> **关于「按家族规范生成 / 补全 / 审计 skill」**：此类任务由 **tri-forge**（内部专用工具 skill，不注册为 tri-intent 下游）承接，用户可直接调用 tri-forge，无需经意图路由。tri-forge 产出的 skill 若具备「tri-intent 下游」身份，则按 tri-forge 包内 `references/tri-intent-integration.md` 的同步规则回填 tri-intent（路由映射表 / L3 子类表 / 检测路径 / 计数 / README）。

## 路由判定流程

1. **核心动作判定**：识别用户核心动词是否为「蒸馏/提炼/萃取/distill/复刻/造一个 skill/把 XX 做成 skill/沉淀成能力」
2. **产出判定**：确认期望产出是「一个可复用的新 skill」而非业务代码或普通文档
3. **L2 判定**：动作 + 产出均命中 → L2 = **I21 蒸馏造物**
4. **下游路由**：`下游路由建议` = tri-god
5. **快照标注**：在快照 §三 `任务要点` 中保留蒸馏对象与聚焦方向关键词，供下游 skill 激活时校验对象类型 / 子类

## tri-god 激活条件（下游 skill 侧）

> tri-god 收到快照后，按以下条件校验是否激活：

- 快照 §三 `intent.L2_核心意图` = I21
- `下游路由建议` 指向 tri-god
- 两者同时满足即激活 tri-god 的蒸馏流程（识别对象类型 → 加载方法论 → 双审批门 + 执行前确认 → 执行 → 报告）

若 L2 越界（非 I21），tri-god 将停止并回退 tri-intent 重新路由。

## 与 tri-god 上游依赖检测的对称关系

- tri-intent 侧：产出快照后检测 `tri-god/` 目录是否存在，未安装时提示 `skillhub install tri-god --dir <目标目录>`
- tri-god 侧：激活时检测上游 tri-intent 是否可用（模式 A 快照模式 / 模式 B 引导安装 / 模式 C 降级模式）
- 双向检测确保：无论用户先安装哪一端，缺失的另一端都会被检测到并给出安装引导

## 与 tri-forge 的协作关系（内部工具，非下游）

> tri-forge 是**内部专用工具 skill**，不注册为 tri-intent 下游路由项（用户直接调用，不经意图识别）。其产出物若具备「tri-intent 下游」身份，则需同步回填 tri-intent。

- **tri-intent 侧**：不路由到 tri-forge；检测路径仍包含 `.tribro/skills/`，用于发现 tri-forge 机器生成的下游 skill 并自动接通路由。
- **tri-forge 侧**：激活时检测上游 tri-intent 是否可用（模式 A 快照模式 / 模式 B 引导安装 / 模式 C 降级模式），确保生成的下游 skill 能正确接回快照契约。
- **下游同步约束（用户硬要求）**：tri-forge 生成「作为 tri-intent 下游」的 skill 时，MUST 在门③同步回填 tri-intent（路由映射表 / L3 子类表 / 检测路径 / 计数 / README），详见 tri-forge 包内 `references/tri-intent-integration.md`。即 tri-forge 是「下游的制造者」——其产出物若有下游身份，路由由 tri-forge 自动接通。