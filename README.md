# tri-stack

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)
[![Skills](https://img.shields.io/badge/skills-26-6c5ce7.svg)](#技能目录)
[![Self-Maintained](https://img.shields.io/badge/status-self--maintained-00b894.svg)](#自维护声明)

**模块化、可组合的 AI 智能体技能集合 · 自维护 fork**

</div>

---

## 自维护声明

本仓库为 [TrisighT9527/tri-skills](https://github.com/TrisighT9527/tri-skills) 的 **自维护 fork**。

- **不再跟随上游更新**：版本号自主管理，不再与 skillhub 平台比对
- **远端比对已停用**：所有 skill 内置 `SELF_MAINTAINED = True`，完全跳过远端版本请求
- **自建基础设施**：`ops/` 目录包含版本校验器、补丁层、补装工具与版本线基线
- **自建 tri-forge**：技能锻造 skill（三模式 + 五门流程 + 22 条合规门禁）
- **自建 tri-prototype**：PM→Dev 桥接 skill（解析原型 + PRD → 产出 tri-coding 需求说明书）
- **补装缺失 skill（已废弃）**：曾从平台补装 11 个 tri-intent 路由引用的子类 skill（顶层 29 → 42）
- **平台取包工具已移除（2026-09-24）**：`ops/skills-install.py` 与「停用远端比对」裁定冲突，已删除；本地安装统一走 `ops/install-skills.py`（junction 方式）
- **分支收窄（2026-09-24）**：`main` 收窄为**编程工作流专线（22 个）+ 横向方法论（2 个），共 24 个 skill**；全量 46 个保存在归档分支 `archive-full-skills-20260924`（2026-09-25 新增内部工具型 `tri-req-audit` ⇒ 本分支 **25**；同日新增横向验证型 `tri-verify` ⇒ **26**）

> 上游作者将 tri-forge 私有化（`.gitignore` 显式排除 + 平台未发布），本仓库依据
> `tri-mece-audit/tri-mece-audit.html` 记录的规格自行重建。

---

## 简介

**tri-stack** 是一个面向 AI 智能体的技能集合。**本分支（`main`）为编程工作流专线，携带 26 个 skill（编程线 23 + 横向方法论 3）**，覆盖意图路由、编码、审查、修复、规划、代码洞察、全流程编排、项目接入与 skill 锻造。每个 skill 都是一个独立的功能单元，遵循统一的接口规范，可被任意 AI 工具按需加载和调用。

> **全量版（46 个 skill）** 保存在归档分支 **`archive-full-skills-20260924`**，额外包含内容生成、格式转换（PDF/Word/PPT/Excel/HTML → Markdown）、多模态生成、表达陪伴、领域单入口与横向方法论等 24 个 skill。

### 设计理念

- **模块化** — 每个 skill 职责单一，独立可部署，低耦合高内聚
- **可组合** — 通过 tri-intent 路由 + tri-workflow 编排，skill 可组合成复杂工作流
- **统一规范** — 所有 skill 遵循相同的接口契约、文档标准和版本管控
- **工具无关** — 不绑定特定 AI 工具，任何支持 skill 加载的系统均可使用
- **自维护** — 版本号自主管理，内置五点版本一致性校验，不依赖外部平台

---

## 分支说明：编程工作流专线

本分支面向**编程工作流的 skill 开发**，携带编程线 23 个 skill + 横向方法论 3 个（`tri-evolve` / `tri-true` / `tri-verify`），共 **26** 个（2026-09-25 新增 `tri-req-audit`，服务 tri-coding 门② 的需求文档审核）。

- 全量版 46 个 skill 保存在归档分支 **`archive-full-skills-20260924`**（已推送远端）
- 需要非编程能力的 skill 时，从归档分支取用或在该分支工作
- `tri-intent` 的 **27 落点分类体系完整保留**——未包含的落点（I01–I09 / I15 / I16 / I17–I20）在快照中被标注为「本分支未包含」，**不再触发安装询问**

---

## 技能目录（26 个）

### 控制面

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-intent](tri-intent/) | 1.14.4 | 意图识别总路由。第一层三分法（Asking/Doing/Expressing/Meta）→ 下钻二级意图 → 产出快照交接下游 |
| [tri-meta](tri-meta/) | 1.2.9 | 元操作处理（M01–M04）：纠错 / 追加细化 / 能力询问，并重路由回原 skill |

### 编程主干（写 → 修 → 审）

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-coding](tri-coding/) | 1.9.0 | 编码开发，三门流程：需求审批 → 设计审批 → 执行确认（I11） |
| [tri-fix](tri-fix/) | 1.5.4 | 调试修复：先造出一条能变红的反馈循环，再定位根因（I12） |
| [tri-review](tri-review/) | 1.8.0 | 代码审查：三模式 + Fowler 12 坏味 + 审查执行纪律八则（CR） |

### 编码子类（I11 一跳覆写）

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-frontend-design](tri-frontend-design/) | 1.1.7 | 前端设计方向：设计令牌 / 动效基线 / 多变体探索 |
| [tri-lottie](tri-lottie/) | 1.0.6 | 动效实现 / Lottie 集成 |
| [tri-prototype](tri-prototype/) | 1.1.3 | PM→Dev 桥接：解析原型 + PRD → tri-coding 需求说明书 |

### 代码洞察（I10 一跳覆写）

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-code-analyzer](tri-code-analyzer/) | 1.5.3 | 代码库深度剖析：五部分报告 + Mermaid 可视化 |
| [tri-html](tri-html/) | 1.3.8 | 架构可视化分析（高精度 viewer 引擎 + showcase 门禁） |
| [tri-checklist](tri-checklist/) | 1.1.6 | 审计清单生成：改动点 / 审查点 / 测试点 / 测试步骤四维 |

### 全流程 / 协作对齐

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-sdlc](tri-sdlc/) | 1.1.7 | SDLC 全生命周期编排：九阶段 + 68 必检项 + 三剖面 |
| [tri-orchestrate](tri-orchestrate/) | 1.0.3 | 协作编排：拆分需求 → 分配 → 并行执行 → 回执收集 → master-todo 回写 |
| [tri-grill](tri-grill/) | 1.0.4 | 质询对齐：六维质询（歧义/边界/反例/术语/依赖/优先级）直到共识 |
| [tri-req-audit](tri-req-audit/) | 1.1.1 | 需求文档审核：三重前置校验 + 二跳委派市面 PRD 审核 skill → P0/P1/P2 问题清单（自建） |
| [tri-domain](tri-domain/) | 1.0.2 | 领域建模：术语表（CONTEXT.md）+ ADR + 边界场景清单 |

### 内务 / 造物

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-init](tri-init/) | 1.1.0 | 项目初始化：扫描技术栈 → 生成 AGENTS.md + project-profile → 创建 .tribro/（自建） |
| [tri-forge](tri-forge/) | 1.2.0 | 技能锻造：三模式 + 五门流程 + 22 条合规门④ + 五点版本校验（自建） |
| [tri-god](tri-god/) | 1.2.5 | 蒸馏造物（I21）：把人 / 工作流 / 方法论蒸馏成可复用的新 skill |

### 相邻支撑

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-plan](tri-plan/) | 1.3.5 | 规划拆解：WBS + 依赖图 + 风险登记（I13） |
| [tri-action](tri-action/) | 1.2.6 | 操作执行（I14） |
| [tri-workflow](tri-workflow/) | 1.2.7 | 工作流设计引擎：7 阶段混合智能流水线（I13/I14 子类） |
| [tri-loop](tri-loop/) | 1.2.6 | 知识库 loop 启动（I14 子类） |

### 横向方法论

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-evolve](tri-evolve/) | 1.1.8 | 自进化 / 用户画像：OODA 闭环 + 经验条目库 + A/B 验证门 + 回滚（不认领 L2、不进路由） |
| [tri-true](tri-true/) | 1.1.7 | 四道防线消除幻觉：置信度 → 事实源（T1–T4）→ 多模型交叉 → 自反思修正（不认领 L2、不进路由） |
| [tri-verify](tri-verify/) | 1.1.0 | 运行中应用验证：V1–V5 触发 + 三类归因 + 有界循环 + 五态印章；引擎可插拔（本地 / TestSprite） |

---

## 自维护基础设施（`ops/`）

```
ops/
├── README.md                基础设施说明（工具 / 纪律 / 未完成项）
├── install-skills.py        junction 安装到 AI 工具（--target / --dry-run / --remove）
├── version-lint.py          版本一致性校验（P1–P5 + 文档层 D1–D4）
├── versions.json            自主版本线基线（35 skill 快照：顶层 26 + tri-sdlc 子 skill 9）
└── patches/                 本地补丁层（368 个 op，幂等重放）
    ├── README.md            机制说明 + 踩坑 + 校准记录
    ├── manifest.json        补丁清单（声明式唯一事实源）
    ├── apply.py             幂等重放器
    └── payload/             校正版版本检查规范（分发到各 skill）
```

**日常操作**：

```bash
# 安装 skill 到 AI 工具（junction，源始终在仓库，改仓库即生效）
python ops/install-skills.py --target ~/.workbuddy/skills --dry-run

# 重放补丁层（装完必做）
python ops/patches/apply.py

# 版本一致性校验（skill 包内 P1–P5 + 仓库级文档层 D1–D4）
python ops/version-lint.py

# 改了 skill 版本后同步文档层（幂等）
python ops/version-lint.py --apply-docs

# 版本一致性修复（P3/P5 自动）
python tri-forge/scripts/check_registry.py --apply
```

---

## 快速开始

### 前提条件

- 支持 AI 技能加载的 AI 工具（如 TRAE IDE、Cursor、Claude Code 等）
- 或支持 SkillHub 协议的工具环境

### 安装

```bash
git clone https://github.com/opsbli/tri-stack.git
cd tri-stack
```

### 使用

以 TRAE IDE 为例，安装后即可通过自然语言与 AI 交互，AI 会自动通过 tri-intent 识别意图并调度对应 skill：

```
用户：帮我看一下这段代码有什么问题...

→ tri-intent 分析意图 → 路由到 tri-review
→ tri-review 执行代码审查 → 输出结构化的审查报告
```

---

## 项目结构

```
tri-skills/
├── tri-*/                    # 26 个顶层 skill（见上方技能目录）
│   └── */children/           # 子 skill（tri-sdlc×9，随父包分发，非顶层 skill）
├── ops/                      # 自维护基础设施
│   ├── install-skills.py     # junction 安装到 AI 工具
│   ├── version-lint.py       # 版本一致性校验（P1–P5 + 文档层 D1–D4）
│   ├── versions.json         # 自主版本线基线
│   └── patches/              # 本地补丁层（76 op）
├── tri-mece-audit/           # MECE 审计报告（HTML）
├── WORKFLOW-GUIDE.html       # 使用手册
├── ops/README.md             # 基础设施说明
├── LICENSE                   # MIT
├── CONTRIBUTING.md           # 贡献指南
├── CHANGELOG.md              # 全局变更日志
└── .gitattributes            # 行尾统一
```

---

## 版本管控

本仓库为**自维护 fork**，版本号自主管理（自主版本线，见 `ops/versions.json`）。

- 每个 skill 包含独立的版本号、CHANGELOG 和内置版本检查机制（自维护模式：本地一致性校验）
- 全局版本变更记录见 [CHANGELOG.md](CHANGELOG.md)
- 各 skill 的详细变更记录见各自目录下的 `CHANGELOG.md`
- 版本一致性校验：`python ops/version-lint.py`（退出码 0 = 一致）

---

## 贡献指南

欢迎任何形式的贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解：

- 如何提交 Issue（Bug 报告 / 功能请求 / 新 skill 请求）
- 如何提交 PR
- 编码规范与 skill 开发标准

同时请遵守 [CODE\_OF\_CONDUCT.md](CODE_OF_CONDUCT.md)。

---

## 安全策略

发现安全漏洞？请参阅 [SECURITY.md](SECURITY.md) 了解如何报告。

---

## 许可证

本项目采用 MIT 许可证 — 详见 [LICENSE](LICENSE) 文件。

---

## 维护

- 仓库：<https://github.com/opsbli/tri-stack>
- 状态：自维护 fork（不再跟随上游更新）
- 上游：[TrisighT9527/tri-skills](https://github.com/TrisighT9527/tri-skills)（只读参考）
