---
name: tri-workflow
slug: tri-workflow
version: 1.1.1
displayName: 工作流设计引擎（tri-workflow）
summary: 依据 tri-intent 快照或独立对话，通过 7 阶段混合智能流水线设计企业级工作流，产出多形态可执行产物。融合模板驱动、状态机校验、编译器多目标后端三种架构范式。
tags: [workflow, orchestration, pipeline, ci-cd, approval, automation, state-machine, dsl, enterprise]
license: MIT
---

# 工作流设计引擎（tri-workflow）

企业级 AI 工作流设计 skill。通过 **7 阶段混合智能流水线**（环境感知 → 模板匹配 → 对话补全 → 编译优化 → 校验验证 → 多目标输出 → 迭代反馈）将用户需求或 tri-intent 快照转化为可执行的工作流产物，支持 5 种交付形态：SKILL.md、设计文档、CI/CD 配置、审批流模板、DAG 配置。

## 特性

- **双入口**：下游执行（读取 tri-intent 快照 §三）或独立使用（对话提取需求），完整闭环。
- **上游依赖检测三态**：
  - **A · 快照模式**：定位到可用快照，按工作流推进（标准模式）。
  - **A0 · 待识别**：有 tri-intent 但无可用快照 → 提示先经意图识别，绝不静默执行。
  - **B · 独立降级模式**：跳过快照读取，直接从对话提取需求，环境感知降级为仅扫描本地 Skills/MCP。
- **渐进式交付**：每阶段产出可独立确认的中间产物，用户可随时调整/终止。
- **多目标后端**：按工作流类型选择交付形态，统一编译为可版本管理的声明式 DSL（`workflows/<name>.wf.yml`）。
- **质量门禁**：9 维度质量标准，🔴 阻断项 = 0 方可进入阶段 6。
- **Node Registry**：可复用节点注册表，积累高频节点覆盖代码工程/协作沟通/审批/数据/监控/条件分支。

## 安装

### 作为 tri-intent 下游 skill（推荐）

随 tri-intent 家族一并安装即可，由快照路由激活。

### 独立安装

```bash
skillhub install tri-workflow --dir <目标目录>
```

独立安装时仍可检测上游 tri-intent：若可用则进入 A/A0 模式，否则自动降级为 B 模式（不依赖 tri-intent 也可使用）。

## 用法

### 下游执行（经 tri-intent 路由）

tri-intent 产出的快照 `下游路由建议` 指向本 skill（I13 规划拆解 / I14 操作执行的工作流子类）时，直接激活，读取快照 §三 推进。

### 独立使用

直接对 Agent 说：「帮我设计一个 <CI/CD 流水线 / 审批流 / 数据处理流>」，本 skill 将：

1. 进入模式 B，从对话提取必填字段（工作流类型、业务领域、触发方式、核心节点、交付形态、技术栈约束）。
2. 按阶段 1→7 顺序产出中间产物与最终工作流产物。
3. 作答前声明：「本次意图=<I13/I14>，已读取快照=<是/否>，模式=<快照/待识别/降级>，当前阶段=<1-7>」。

## 目录结构

```
tri-workflow/
├── SKILL.md                              # 主入口：7 阶段流水线 + 执行契约 + 质量标准
├── README.md                             # 本文件
├── CHANGELOG.md                          # 版本变更记录
├── tests/
│   └── tri-workflow-full-testcases.md    # 全场景测试用例
├── templates/
│   ├── node-registry.md                  # 可复用节点注册表
│   ├── workflow-templates/               # 7 个预置工作流模板
│   └── output-backends/                  # 多目标输出后端规范
├── schemas/
│   ├── env-profile.schema.md             # 环境感知 schema
│   ├── workflow-model.schema.md          # 工作流模型 schema
│   └── workflow-dsl.schema.md            # 工作流 DSL schema
└── validators/
    ├── dependency-checker.md             # 依赖校验规则（8 规则）
    └── executability-validator.md        # 可执行性验证规则（8 规则）
```

## 相关

- 上游意图识别：tri-intent
- 协作链路：tri-coding（节点实现）、tri-fix（调试修复）、tri-review（代码审查）、tri-action（动作编排）、tri-loop（复盘迭代）
