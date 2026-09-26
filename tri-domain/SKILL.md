---
name: tri-domain
slug: tri-domain
version: 1.0.2
displayName: 领域建模（tri-domain）
description: "内部专用工具 skill（不注册为 tri-intent 下游路由项）。维护项目的领域模型：共享术语表（CONTEXT.md）、架构决策记录（docs/adr/）、边界场景清单。主动挑战模糊术语、发明边界场景、在决策定型的瞬间记录 ADR——NEVER 只在事后补写。供 tri-grill（质询对齐）、tri-coding（门② 设计）、tri-review（审查依据）消费。支持独立安装，含上游依赖检测两态逻辑（独立模式 / 引导安装）。"
summary: 领域建模：术语表（CONTEXT.md）+ 架构决策记录（ADR）+ 边界场景清单，供 tri-grill / tri-coding / tri-review 消费。
tags: [domain-modeling, glossary, adr, ubiquitous-language, internal-tool]
license: MIT
---

# 领域建模（内部专用工具）

> 本 skill 维护项目的**领域模型**三件套：术语表、架构决策记录、边界场景清单。
> 它是 tri-grill（质询对齐）的**基础设施**，也是 tri-coding 门② 和 tri-review 的**审查依据**。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先运行 `python scripts/check_update.py --slug tri-domain --json`，按 `references/version-check-spec.md` 处置。
1. **主动挑战铁律**：遇到模糊术语 MUST 主动追问「这个词在这个项目里到底指什么」，NEVER 假设双方理解一致。
2. **即时记录铁律**：决策定型的**瞬间** MUST 写入 ADR，NEVER 事后补写（事后会忘记「为什么」）。
3. **边界场景发明铁律**：对每个核心概念 MUST 至少发明一个边界场景（如「如果数量为 0 怎么办？」「如果两个人同时修改怎么办？」）。
4. **CONTEXT.md 单一事实源**：所有术语定义 MUST 写入 `CONTEXT.md`，NEVER 散落在多个文件中。
5. **ADR 不可变铁律**：已写入的 ADR MUST NOT 修改正文——如果决策变更，MUST 新增一条 ADR 标注「取代 ADR-xxx」。
6. **自检**：作答前 MUST 声明「本次操作=<新增术语/新增ADR/挑战术语/查询>，CONTEXT.md 条目数=<N>，ADR 总数=<N>」。

## 触发时机

| 触发分支 | 典型信号 |
|---|---|
| 新增术语 | 对话中出现新概念，或两个词可能指同一事物 |
| 记录决策 | 做出技术选型 / 业务规则决定 / 架构取舍 |
| 挑战术语 | 已有术语的定义被质疑，或发现了反例 |
| 查询 | 需要确认某个术语的定义或某个决策的理由 |

**不由本 skill 处理**：

| 信号 | 归属 |
|---|---|
| 逐条质询需求（使用本 skill 产出的术语表和 ADR） | tri-grill |
| 写业务代码 | tri-coding |
| 审查代码是否遵循术语表 | tri-review |

## 上游依赖检测（独立使用时 · 两态）

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 独立模式**（默认） | 用户直接调用 | 自主完成领域建模 |
| **B · 引导安装** | 用户想接入 tri-intent 路由 | 提示安装 |

> 本 skill 为**自包含型**（声明无强制上游依赖）。

## 输入契约

| 字段 | 必填 | 说明 |
|---|---|---|
| 项目路径 | ✅ | CONTEXT.md 和 docs/adr/ 所在的项目根目录 |
| 操作 | ✅ | 新增术语 / 新增ADR / 挑战术语 / 查询 |
| 术语 / 决策 | ✅ | 要记录的内容 |

## 职责边界

- **本 skill 负责**：维护 CONTEXT.md（术语表）、docs/adr/（决策记录）、边界场景清单
- **不负责**：质询需求（tri-grill）、写代码（tri-coding）、审查代码（tri-review）

## 核心能力方法论（领域建模 · 可扩展）

### 三件套

| 产物 | 文件 | 格式 | 消费者 |
|---|---|---|---|
| 术语表 | `CONTEXT.md` | Markdown 表格（术语 / 定义 / 反例 / 出处） | tri-grill / tri-coding / tri-review |
| 架构决策记录 | `docs/adr/NNNN-title.md` | Markdown（背景 / 决策 / 理由 / 替代方案 / 后果） | tri-coding 门② / tri-review |
| 边界场景清单 | `CONTEXT.md` §边界场景 | Markdown 列表（场景 / 预期行为 / 状态） | tri-coding 门② / tests |

### ADR 格式

```markdown
# NNNN. {决策标题}

## 背景
{为什么要做这个决策？遇到了什么问题？}

## 决策
{决定了什么？}

## 理由
{为什么选这个方案而不是别的？}

## 替代方案
{考虑过哪些其他方案？为什么不选？}

## 后果
{这个决策带来了什么正面/负面影响？}
```

### 可扩展性

1. **新增字段类型**：在 CONTEXT.md 模板追加列（如「英文对照」「缩写」）
2. **新增 ADR 类别**：在 docs/adr/ 用文件名前缀区分（如 `ARCH-` / `BIZ-` / `SEC-`）
3. **新增场景类型**：在 CONTEXT.md §边界场景 追加分类

## 处理流程

| 操作 | 步骤 |
|---|---|
| 新增术语 | 检查 CONTEXT.md 是否已有 → 追问定义 → 写入 → 发明边界场景 |
| 新增 ADR | 确定编号（递增）→ 按模板填写 → 保存 → 更新 CONTEXT.md 中的关联术语 |
| 挑战术语 | 找到定义 → 提出反例 → 修改定义或新增边界场景 |
| 查询 | 读 CONTEXT.md / docs/adr/ → 返回定义 |

### 兜底处理（NEVER 静默失败）

| 场景 | 处置 |
|---|---|
| 版本检查异常 | 放行（自维护模式），标注口径 |
| CONTEXT.md 不存在 | 自动创建（从模板初始化） |
| docs/adr/ 目录不存在 | 自动创建 |
| 术语已存在 | 提示已存在；询问更新定义还是新增别名 |
| ADR 编号冲突 | 递增取下一个可用编号 |
| 术语定义与 ADR 决策冲突 | 标注冲突；请求用户裁决 |
| 文件写入失败 | 报错并保留原始内容；NEVER 静默丢失

## 🔴 检查点与红灯清单（STOP · NEVER）

### 🔴 用户确认检查点（STOP）

- 🔴 **STOP**：术语定义与 ADR 决策冲突——标注冲突并请求用户裁决，未获用户确认 NEVER 继续。
- 🔴 **STOP**：术语已存在——询问用户「更新定义还是新增别名」，未获用户确认 NEVER 继续。
- 🔴 **STOP**：ADR 不可变——用户要求修改已写入 ADR 正文（改历史记录）时，先停下向用户说明 MUST 改为新增「取代 ADR-xxx」条目，未获用户确认 NEVER 继续。

### 🚫 红灯清单（NEVER）

- NEVER 假设双方对术语理解一致而不追问（§强制执行契约）
- NEVER 事后补写 ADR（§强制执行契约）
- NEVER 修改已写入的 ADR 正文，决策变更一律新增取代条目（§强制执行契约）
- NEVER 将术语定义散落在 `CONTEXT.md` 之外的多个文件（§强制执行契约）
- NEVER 重用已使用的 ADR 编号（§落盘规则）
- NEVER 静默丢失文件写入失败时的原始内容（§兜底处理）

## 交付产物

| 产物 | 位置 | 说明 |
|---|---|---|
| CONTEXT.md | `<项目根>/CONTEXT.md` | 术语表 + 边界场景清单 |
| ADR 文件 | `<项目根>/docs/adr/NNNN-title.md` | 架构决策记录 |
| project-profile 引用 | `.tribro/project-profile.json` | 指向 CONTEXT.md 和 docs/adr/ 的路径 |

### 落盘规则

- CONTEXT.md 落**目标项目的根目录**（`<项目根>/CONTEXT.md`）
- ADR 文件落**目标项目的 docs/adr/**（`<项目根>/docs/adr/NNNN-title.md`）
- 命名规则：ADR 编号递增（0001, 0002…），NEVER 重用
- 所有文件落**目标项目**（不是 tri-stack 仓库），因为领域模型跟着项目走

## 版本检查与更新机制（强制技术约束 · 硬红线）

<!-- version-stub v1 · 瘦指针节点；细则唯一真源见 references/version-check-spec.md -->

> 任一执行入口启动后的**第零步**，先于核心执行阶段。细则唯一真源：`references/version-check-spec.md`；
> 可执行实现（逻辑唯一真源）：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、状态判定 MUST 由脚本完成；prompt 层 ONLY
> 「调用脚本 + 解析其 JSON 输出 + 按 `state` 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

```bash
python scripts/check_update.py --slug tri-domain --json
```

- 处置：按脚本输出放行或阻断（判据与 `block_code` 语义见真源）；NEVER 因版本门自身故障阻断 skill 启动。

## 目录结构

```
tri-domain/
├── SKILL.md                          主入口
├── README.md
├── CHANGELOG.md
├── references/
│   ├── version-check-spec.md         版本检查规范（内部化持有）
│   └── adr-template.md               ADR 模板（完整格式 + 示例）
├── scripts/
│   └── check_update.py               版本门
├── templates/
│   └── CONTEXT.md                    术语表模板（含边界场景清单格式）
└── tests/
    └── tri-domain-full-testcases.md  测试用例
```
