---
name: tri-orchestrate
slug: tri-orchestrate
version: 1.0.0
displayName: 协作编排（tri-orchestrate）
description: "内部专用工具 skill（不注册为 tri-intent 下游路由项，由用户直接调用）。将 requirements.md 或 task-checklist.md 按功能点边界和依赖关系拆分为 N 份独立 spec，分配给多个人/agent 并行执行，收集结构化回执并自动回写 master-todo。含拆分器（split-specs.py）+ 回执收集器（collect-receipts.py）+ 进度看板生成器。支持独立安装，含上游依赖检测两态逻辑（独立模式 / 引导安装）。"
summary: 协作编排：拆分需求 → 分配 → 并行执行 → 回执收集 → master-todo 自动回写 → 进度看板。
tags: [orchestration, collaboration, split, dispatch, receipt, multi-person, internal-tool]
license: MIT
---

# 协作编排（内部专用工具）

> 本 skill 将规划文档拆分为多份独立 spec，分给多人/agent 并行执行，收集回执并自动回写总任务清单。
> **它解决的问题是**：一个人不可能做完所有事——需求要拆、活要分、进度要追、结果要汇总。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先运行 `python scripts/check_update.py --slug tri-orchestrate --json`，按 `references/version-check-spec.md` 处置。
1. **拆分 MECE 铁律**：spec 拆分 MUST 满足——每条功能点归属于恰好一个 spec（不重叠），所有功能点被覆盖（不遗漏）。**依赖关系决定拆分边界**——强耦合功能点（共享数据模型/API 接口）归入同一 spec。
2. **spec 独立性铁律**：每份 spec MUST 可被独立执行（一个人拿到 spec 就能开始工作，不需要等其他 spec 的中间产物）。跨 spec 依赖 MUST 显式声明在 spec 文件的「依赖的 Spec」字段中。
3. **回执驱动铁律**：master-todo 的复选框**NEVER 手动勾选**——只能由回执驱动自动更新。手动勾选会破坏「回执 = 完成」的一致性。
4. **回执格式强制**：回执 MUST 是 JSON，包含 `spec_id / status / assignee / files_changed / tests_passed / blockers / completed_at` 七个字段。缺失字段的回执视为无效。
5. **进度透明**：MUST 维护 master-todo.md 中的进度汇总表，每次回执到达后即时更新。
6. **冲突检测**：如果两个 spec 的 `files_changed` 有交集，MUST 在汇总时标注「潜在合并冲突」。
7. **最小化原则**：只编排用户指定的功能点范围，NEVER 擅自追加功能或扩大拆分粒度。
8. **自检**：作答前 MUST 声明「本次操作=&lt;拆分/分配/收集/汇总/全流程&gt;，spec 数=&lt;N&gt;，已分配=&lt;N&gt;，已完成=&lt;N&gt;，进度=&lt;N%&gt;」。

## 触发时机

| 触发分支 | 典型信号 |
|---|---|
| 拆分 | 「把 requirements 拆成 spec」「拆分任务」「分工」 |
| 收集 | 「Spec-1 做完了」「这是回执」「收集回执」 |
| 进度 | 「进度怎么样」「还剩多少」「看板」 |
| 全流程 | 「编排这个项目」「拆分并分配」 |

**不由本 skill 处理**：

| 信号 | 归属 |
|---|---|
| 产出 requirements.md | tri-prototype |
| 写业务代码 | tri-coding（由 spec 的执行者调用） |
| 审查代码 | tri-review |
| 记录 ADR / 术语表 | tri-domain |

## 上游依赖检测（独立使用时 · 两态）

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 独立模式**（默认） | 用户直接调用 | 自主完成编排 |
| **B · 引导安装** | 用户想接入 tri-intent | 提示安装 |

## 输入契约

| 字段 | 必填 | 说明 |
|---|---|---|
| 需求文档路径 | ✅ | requirements.md 或 task-checklist.md |
| 团队成员 | ✅ | 人员/agent 名单（至少 1 人） |
| 依赖关系 | ⬜ | spec 之间的依赖（自动检测 + 手动补充） |
| 产物目录 | ⬜ | spec 和回执的存储位置（默认 `.tribro/coding/<命名>/specs/`） |

## 职责边界

- **本 skill 负责**：拆分 spec → 生成 dispatch-plan → 收集回执 → 回写 master-todo → 生成进度看板
- **不负责**：写代码（tri-coding，由 spec 执行者调用）、审需求（tri-grill）、产出需求（tri-prototype）、审查代码（tri-review）

## 核心能力方法论（协作编排 · 可扩展）

### 五步编排流水线

```
requirements.md / task-checklist.md
     ↓
① 拆分（split-specs.py）
     │  按功能点边界 + 依赖关系 + 人员数
     │  产出：spec-01.md ~ spec-N.md + dispatch-plan.md
     ↓
② 分配（dispatch-plan.md 确认）
     │  每 spec 标注负责人 + 依赖
     │  用户确认分配 → spec 变为 READY
     ↓
③ 并行执行（由 AI 工具 / 人工执行）
     │  每 spec 在独立会话中运行 tri-coding
     │  完成后产出 receipt-<spec_id>.json
     ↓
④ 回执收集（collect-receipts.py）
     │  读取 receipt-*.json → 校验格式 → 更新 master-todo
     │  检测 files_changed 交集 → 标注潜在合并冲突
     ↓
⑤ 进度看板（master-todo.md 汇总表）
```

### 回执格式（强制）

```json
{
  "spec_id": "spec-01",
  "status": "completed",
  "assignee": "人员A",
  "files_changed": ["path/to/file.java", "path/to/file.vue"],
  "tests_passed": true,
  "blockers": [],
  "completed_at": "2026-09-24T14:41:00+08:00"
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| spec_id | string | ✅ | 关联的 spec 编号 |
| status | string | ✅ | `completed` / `blocked` / `partial` |
| assignee | string | ✅ | 执行人 |
| files_changed | string[] | ✅ | 变更的文件路径列表（用于冲突检测） |
| tests_passed | boolean | ✅ | 测试是否通过 |
| blockers | string[] | ✅ | 阻塞项（空数组 = 无阻塞） |
| completed_at | string | ✅ | 完成时间（ISO 8601） |

### 冲突检测

每次回执到达后，检查 `files_changed` 与已完成 spec 的交集：

```
files_changed(spec-01) ∩ files_changed(spec-02) ≠ ∅
  → 标注 ⚠ 潜在合并冲突
  → 列出冲突文件
  → 建议合并顺序
```

### 可扩展性

1. **新增回执字段**：在回执格式表追加字段（如 `code_review_passed`），收集器自动校验
2. **新增通知渠道**：在 collect-receipts.py 加 webhook（钉钉 / Slack 通知 spec 完成）
3. **新增进度维度**：在 master-todo 汇总表追加列（如「预计工时」「实际工时」）

## 处理流程

| 命令 | 脚本 | 说明 |
|---|---|---|
| 拆分 | `python scripts/split-specs.py --input <requirements.md> --team <人数>` | 产出 spec-*.md + dispatch-plan.md |
| 收集 | `python scripts/collect-receipts.py --specs-dir <specs目录>` | 读取 receipt-*.json → 回写 master-todo |
| 看板 | `python scripts/collect-receipts.py --dashboard` | 输出进度汇总表 |

## 交付产物

| 产物 | 位置 | 说明 |
|---|---|---|
| dispatch-plan.md | `.tribro/coding/<命名>/specs/` | 依赖图 + 分配矩阵 + 并行度分析 |
| master-todo.md | `.tribro/coding/<命名>/specs/` | 总任务清单（回执驱动自动勾选） |
| spec-01.md ~ spec-N.md | `.tribro/coding/<命名>/specs/` | 独立 spec 文件 |
| receipt-*.json | `.tribro/coding/<命名>/specs/` | 各 spec 的执行回执 |
| 进度看板 | master-todo.md §汇总 | 实时进度 |

### 兜底处理（NEVER 静默失败）

| 场景 | 处置 |
|---|---|
| 版本检查异常 | 放行（自维护模式），标注口径 |
| 需求文档解析失败 | 澄清；NEVER 凭想象拆分 |
| 回执 JSON 格式错误 | 跳过该回执；报警 |
| 回执的 spec_id 未知 | 跳过；报警 |
| files_changed 交集非空 | 标注潜在合并冲突；建议合并顺序 |
| 全部 spec 已完成 | 输出 100% 进度看板 |

### 落盘规则

- 所有文件落 **`.tribro/coding/<命名>/specs/`**（在目标项目根目录下的 `.tribro/` 中）
- spec 文件命名：`spec-{两位序号}.md`
- 回执文件命名：`receipt-{spec_id}.json`
- master-todo.md 是唯一进度事实源

## 版本检查与更新机制（强制技术约束 · 硬红线）

> **细则唯一真源**：`references/version-check-spec.md`（内部化持有）。
> **可执行实现**：`scripts/check_update.py`。

```bash
python scripts/check_update.py --slug tri-orchestrate --json
```

## 目录结构

```
tri-orchestrate/
├── SKILL.md                          主入口
├── README.md
├── CHANGELOG.md
├── references/
│   ├── version-check-spec.md         版本检查规范（内部化持有）
│   └── receipt-format.md             回执格式规范
├── scripts/
│   ├── check_update.py               版本门
│   ├── split-specs.py                拆分器
│   └── collect-receipts.py           回执收集器 + master-todo 回写
├── templates/
│   ├── master-todo.md                总任务清单模板
│   ├── dispatch-plan.md              分配计划模板
│   └── spec.md                       独立 spec 模板
└── tests/
    └── tri-orchestrate-full-testcases.md  测试用例
```
