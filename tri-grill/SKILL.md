---
name: tri-grill
slug: tri-grill
version: 1.0.0
displayName: 质询对齐（tri-grill）
description: "内部专用工具 skill（不注册为 tri-intent 下游路由项，由用户直接调用）。对 requirements.md / design.md / plan.md 等规划文档进行逐条质询，直到 PM 和 Dev 对每一句话有相同理解。质询过程产出的新决策由 tri-domain 记录为 ADR / 术语表条目。产出精化后的文档 + 对齐记录。NEVER 在仍有未解决歧义时宣布对齐完成。支持独立安装，含上游依赖检测两态逻辑（独立模式 / 引导安装）。"
summary: 逐条质询直到共识：挑战模糊术语 → 发明边界场景 → 记录 ADR → 精化文档 → 确认对齐完成。
tags: [grill, alignment, requirements, consensus, clarify, internal-tool]
license: MIT
---

# 质询对齐（内部专用工具）

> 本 skill 对规划文档进行**逐条质询**，直到 PM 和 Dev 对每一句话有相同理解。
> **它不是审阅**——审阅是看一遍说 OK；**质询是磨**——每一条都追问「这到底是什么意思」「如果…怎么办」「为什么不…」直到没有歧义。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先运行 `python scripts/check_update.py --slug tri-grill --json`，按 `references/version-check-spec.md` 处置。
1. **逐条质询铁律**：MUST 逐条（逐段 / 逐句）过文档，每条 MUST 至少提出一个挑战（歧义 / 边界场景 / 反例 / 术语不清晰）。**NEVER 跳过任何条目说「这条没问题」而不给出理由。**
2. **不放过铁律**：只要有一个未解决的歧义，MUST 继续质询。NEVER 在仍有「待确认」「待定」「大概」状态时宣布对齐完成。
3. **即时记录铁律**：质询过程中产生的决策 MUST **即时**调用 tri-domain 记录为 ADR / 术语表条目。NEVER 在质询结束后批量补写。
4. **文档精化铁律**：每解决一个歧义，MUST **立即更新原文档**（不是另建新文档），并在更新处标注 `[已对齐 YYYY-MM-DD]`。
5. **角色平等铁律**：质询过程中 PM 和 Dev 的意见**地位平等**。NEVER 默认「PM 说的就是对的」或「Dev 说的技术方案就是合理的」。
6. **结束条件**：对齐完成当且仅当满足以下全部条件：
   - 所有条目均已过质询（有质询记录，非空白）
   - 所有歧义均已解决（无「待确认」「待定」）
   - 术语表覆盖文档中所有领域概念
   - 用户确认「对齐完成」
7. **最小化原则**：只质询用户指定的文档 / 范围，NEVER 擅自扩展到其他文档或引入新话题。
8. **自检**：作答前 MUST 声明「本次文档=&lt;路径&gt;，条目数=&lt;N&gt;，已质询=&lt;N&gt;，已解决=&lt;N&gt;，待解决=&lt;N&gt;，新增ADR=&lt;N&gt;，新增术语=&lt;N&gt;」。

## 触发时机

| 触发分支 | 典型信号 |
|---|---|
| 直接触发 | 「帮我质询这个需求」「磨一下这个设计」「确保我们对齐了」「这个文档有什么歧义」 |
| 补全触发 | tri-prototype 产出 requirements.md 后，用户要求「确认我们对齐了再开始编码」 |

**不由本 skill 处理**：

| 信号 | 归属 |
|---|---|
| 记录 ADR / 术语表 | tri-domain（本 skill 调用 tri-domain 记录，但本体是 tri-domain） |
| 写业务代码 | tri-coding |
| 代码审查 | tri-review |

## 上游依赖检测（独立使用时 · 两态）

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 独立模式**（默认） | 用户直接调用 | 自主完成质询对齐 |
| **B · 引导安装** | 用户想接入 tri-intent / tri-domain | 提示安装 |

> 本 skill 依赖 `tri-domain`（用于记录 ADR / 术语表），但为**松耦合**——如果 tri-domain 不可用，本 skill 自行维护简单的 Markdown 术语表和决策列表（降级模式）。

## 输入契约

| 字段 | 必填 | 说明 |
|---|---|---|
| 文档路径 | ✅ | 要质询的文档（requirements.md / design.md / plan.md 等） |
| 质询范围 | ⬜ | 指定要质询的章节（缺省 = 全部） |
| 角色 | ⬜ | 当前用户角色（PM / Dev / Tech Lead），影响质询角度 |
| 领域模型路径 | ⬜ | CONTEXT.md 和 docs/adr/ 的路径（缺省 = 项目根目录） |

## 职责边界

- **本 skill 负责**：逐条质询 → 发明边界场景 → 挑战术语 → 调用 tri-domain 记录 → 精化文档 → 确认对齐完成
- **不负责**：生成 requirements.md（tri-prototype）、记录 ADR / 术语表（tri-domain）、写代码（tri-coding）、审查代码（tri-review）

## 核心能力方法论（质询 · 可扩展）

### 质询角度（六维，逐条过）

| 维度 | 挑战方式 | 示例 |
|---|---|---|
| **歧义** | 「这个词有两种理解，你指的是哪种？」 | 「提交」是提交表单还是提交审批？ |
| **边界场景** | 「如果…怎么办？」 | 如果数量为 0？如果两个人同时提交？ |
| **反例** | 「有没有不满足这条规则的情况？」 | 「所有资产必须有序列号」——租赁资产呢？ |
| **术语** | 「这个词你和我理解的一样吗？」 | 「入库」是物理入库还是系统录入？ |
| **依赖** | 「这条依赖于什么？谁先做？」 | 这需要物资分类先配置好 |
| **优先级** | 「这条是 P0 还是 P2？为什么？」 | 这个功能没有它系统能跑吗？ |

### 质询产出

| 产出 | 写入位置 | 格式 |
|---|---|---|
| 精化后的文档条目 | 原文档（就地更新） | 原文 + `[已对齐 YYYY-MM-DD]` 标注 |
| ADR | `<项目根>/docs/adr/` | tri-domain 的 ADR 格式 |
| 术语表条目 | `<项目根>/CONTEXT.md` | tri-domain 的术语表格式 |
| 边界场景 | CONTEXT.md §边界场景 | tri-domain 的边界场景格式 |
| 质询记录 | `reports/<slug>-grill.md` | 逐条质询过程 + 结论 |

### 可扩展性

1. **新增质询维度**：在 §质询角度 追加行（维度 / 挑战方式 / 示例）
2. **新增文档类型**：在 §输入契约 追加（如 ADR 质询、测试用例质询）
3. **新增角色视角**：在 §角色 追加（如 QA / Ops / Security）

## 处理流程

| 步骤 | 动作 |
|---|---|
| 1 | 读取文档，标记全部可质询条目 |
| 2 | 逐条质询（六维），每条至少一个挑战 |
| 3 | 调用 tri-domain 记录新决策 / 新术语 |
| 4 | 就地更新文档，标注 `[已对齐]` |
| 5 | 汇总：已解决 / 待解决 / 新增 ADR / 新增术语 |
| 6 | 用户确认「对齐完成」→ 交付精化后的文档 |

## 兜底处理（NEVER 静默失败）

| 场景 | 处置 |
|---|---|
| 文档不存在 | 澄清路径；NEVER 凭想象创建 |
| 用户拒绝回答某个问题 | 标注「用户选择不回答」；该条目保持原样；在汇总中列出 |
| 连续 3 轮同一条目仍未解决 | 停止该条目的质询；标注为「需升级讨论」；继续其他条目 |
| tri-domain 不可用 | 降级：自行维护简单的 Markdown 术语表和决策列表（不调用 tri-domain） |
| 文档无任何可质询条目 | 告知用户文档已足够清晰，无需质询 |

## 交付产物

| 产物 | 位置 | 说明 |
|---|---|---|
| 精化后的文档 | 原文档路径（就地更新） | 所有歧义已解决，标注 `[已对齐]` |
| 质询记录 | `reports/<slug>-grill.md` | 逐条质询过程 + 结论 + 新增 ADR / 术语列表 |

### 落盘规则

- 精化后的文档：**就地更新**（原文档路径不变），更新处标注 `[已对齐 YYYY-MM-DD]`
- 质询记录：`reports/<slug>-grill.md`
- ADR：`<项目根>/docs/adr/`（由 tri-domain 管理）
- 术语表：`<项目根>/CONTEXT.md`（由 tri-domain 管理）

## 版本检查与更新机制（强制技术约束 · 硬红线）

<!-- version-stub v1 · 瘦指针节点；细则唯一真源见 references/version-check-spec.md -->

> 任一执行入口启动后的**第零步**，先于核心执行阶段。细则唯一真源：`references/version-check-spec.md`；
> 可执行实现（逻辑唯一真源）：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、状态判定 MUST 由脚本完成；prompt 层 ONLY
> 「调用脚本 + 解析其 JSON 输出 + 按 `state` 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

```bash
python scripts/check_update.py --slug tri-grill --json
```

- 处置：按脚本输出放行或阻断（判据与 `block_code` 语义见真源）；NEVER 因版本门自身故障阻断 skill 启动。

## 目录结构

```
tri-grill/
├── SKILL.md                       主入口：六维质询 + 结束条件 + 兜底
├── README.md
├── CHANGELOG.md
├── references/
│   ├── version-check-spec.md      版本检查规范（内部化持有）
│   └── grill-techniques.md        质询技巧参考（六维展开 + 示例库）
├── scripts/
│   └── check_update.py            版本门
├── templates/
│   └── grill-report.md            质询记录模板
└── tests/
    └── tri-grill-full-testcases.md  测试用例
```
