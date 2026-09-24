# tri-stack

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)
[![Skills](https://img.shields.io/badge/skills-42-6c5ce7.svg)](#技能目录)
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
- **补装缺失 skill**：从平台补装 11 个 tri-intent 路由引用的子类 skill（顶层 29 → 42）

> 上游作者将 tri-forge 私有化（`.gitignore` 显式排除 + 平台未发布），本仓库依据
> `tri-mece-audit/tri-mece-audit.html` 记录的规格自行重建。

---

## 简介

**tri-stack** 是一个面向 AI 智能体的技能集合，提供 **42 个模块化、可组合的 skill**，覆盖意图路由、编码、审查、修复、规划、内容生成、翻译、工作流编排、原型解析、PM→Dev 桥接等多个领域。每个 skill 都是一个独立的功能单元，遵循统一的接口规范，可被任意 AI 工具按需加载和调用。

### 设计理念

- **模块化** — 每个 skill 职责单一，独立可部署，低耦合高内聚
- **可组合** — 通过 tri-intent 路由 + tri-workflow 编排，skill 可组合成复杂工作流
- **统一规范** — 所有 skill 遵循相同的接口契约、文档标准和版本管控
- **工具无关** — 不绑定特定 AI 工具，任何支持 skill 加载的系统均可使用
- **自维护** — 版本号自主管理，内置五点版本一致性校验，不依赖外部平台

---

## 技能目录（42 个）

### 入口层

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-intent](tri-intent/) | 1.13.1 | 意图识别总路由。第一层三分法（Asking/Doing/Expressing/Meta）→ 下钻二级意图 → 产出快照交接下游 |

### 执行层（按意图分派）

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-ask](tri-ask/) | 1.2.2 | 咨询作答（I01–I05） |
| [tri-content](tri-content/) | 1.2.4 | 通用内容处理（I06–I10） |
| [tri-article](tri-article/) | 1.4.1 | 去 AI 化技术文章生成（I06 子类） |
| [tri-coding](tri-coding/) | 1.7.0 | 编码开发，三门流程：需求审批 → 设计审批 → 执行确认（I11） |
| [tri-fix](tri-fix/) | 1.4.0 | 调试修复：先造红再定位根因（I12） |
| [tri-review](tri-review/) | 1.6.0 | 代码审查：三模式 + Fowler 12 坏味 + 审查执行纪律八则（CR） |
| [tri-plan](tri-plan/) | 1.3.0 | 规划拆解：WBS + 依赖图 + 风险登记（I13） |
| [tri-action](tri-action/) | 1.2.2 | 操作执行（I14） |
| [tri-bs](tri-bs/) | 1.2.2 | 头脑风暴（I16） |
| [tri-mm](tri-mm/) | 1.5.0 | 多媒体生成路由编排（I15） |
| [tri-music](tri-music/) | 2.2.3 | 爆款音乐生成器（I15 音乐子类） |
| [tri-express](tri-express/) | 1.2.2 | 表达陪伴（I17–I20，不落盘） |
| [tri-meta](tri-meta/) | 1.2.2 | 元操作处理（M01–M04） |
| [tri-god](tri-god/) | 1.2.1 | 蒸馏造物（I21） |
| [tri-html](tri-html/) | 1.3.0 | 架构可视化分析（I10 子类） |
| [tri-checklist](tri-checklist/) | 1.1.2 | 审计清单生成（I10 子类） |
| [tri-frontend-design](tri-frontend-design/) | 1.1.1 | 前端设计方向（I11 子类） |
| [tri-lottie](tri-lottie/) | 1.0.2 | 动效实现 / Lottie 集成（I11 子类） |
| [tri-code-analyzer](tri-code-analyzer/) | 1.4.0 | 代码深度剖析（I10 子类） |
| [tri-pdf2md](tri-pdf2md/) | 1.4.5 | PDF → Markdown（I08 子类） |
| [tri-docx2md](tri-docx2md/) | 1.4.5 | Word → Markdown（I08 x2md 族） |
| [tri-pptx2md](tri-pptx2md/) | 1.4.5 | PPT → Markdown（I08 x2md 族） |
| [tri-xlsx2md](tri-xlsx2md/) | 1.3.5 | Excel → Markdown（I08 x2md 族） |
| [tri-html2md](tri-html2md/) | 1.3.5 | HTML → Markdown（I08 x2md 族） |
| [tri-wiki](tri-wiki/) | 1.1.0 | 知识库搭建（I08 子类） |
| [tri-prototype](tri-prototype/) | 1.1.0 | PM→Dev 桥接：解析原型 + PRD → tri-coding 需求说明书（I11 子类） |

### 编排层

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-workflow](tri-workflow/) | 1.2.3 | 工作流设计引擎：7 阶段混合智能流水线（I13/I14 子类） |
| [tri-sdlc](tri-sdlc/) | 1.1.3 | SDLC 全生命周期编排：九阶段 + 68 必检项 + 三剖面（I11/I13/I14 子类） |
| [tri-loop](tri-loop/) | 1.2.2 | 知识库 loop 启动（I14 子类） |

### 横向方法论层

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-cache](tri-cache/) | 2.1.1 | 四层缓存 + 上下文压缩 |
| [tri-cost](tri-cost/) | 1.3.0 | token 成本审计 + 预算闸门 |
| [tri-evolve](tri-evolve/) | 1.1.2 | 自进化学习 + 用户画像 |
| [tri-guard](tri-guard/) | 1.0.1 | skill 安全审计（skillspector 确定性扫描） |
| [tri-humanize](tri-humanize/) | 1.1.1 | 去 AI 化改写（35 种 AI 写作模式） |
| [tri-translate](tri-translate/) | 1.1.2 | 三策略分层翻译 |
| [tri-true](tri-true/) | 1.1.2 | 四道防线消除幻觉 |

### 领域层

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-learn](tri-learn/) | 1.0.2 | 一对一学习教练（掌握学习 + 间隔重复 + 错题追踪） |
| [tri-jobhunt](tri-jobhunt/) | 1.0.3 | 求职全流程（ATS 简历 + 面试 + 谈判），含 6 个 children |
| [tri-pm](tri-pm/) | 1.1.1 | PM 领域产物与工作流（9 域 / 68 框架 / 42 工作流） |

### 内部工具层

| 名称 | 版本 | 描述 |
|---|---|---|
| [tri-forge](tri-forge/) | 1.0.0 | 技能锻造：三模式 + 五门流程 + 22 条合规门④ + 五点版本校验（自建） |

---

## 自维护基础设施（`ops/`）

```
ops/
├── README.md                基础设施说明（工具 / 纪律 / 未完成项）
├── skills-install.py        平台取包 / 补装 / 缺失检测
├── version-lint.py          五点版本一致性校验（P1–P5）
├── versions.json            自主版本线基线（42 skill 快照）
└── patches/                 本地补丁层（14 个 op，幂等重放）
    ├── README.md            机制说明 + 踩坑 + 校准记录
    ├── manifest.json        补丁清单（声明式唯一事实源）
    ├── apply.py             幂等重放器
    └── payload/             校正版版本检查规范（分发到各 skill）
```

**日常操作**：

```bash
# 补装缺失 skill
python ops/skills-install.py --detect --install

# 重放补丁层（装完必做）
python ops/patches/apply.py

# 版本一致性校验
python ops/version-lint.py

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
├── tri-*/                    # 42 个顶层 skill（见上方技能目录）
│   └── */children/           # 子 skill（tri-mm×4 + tri-sdlc×9 + tri-jobhunt×6）
├── ops/                      # 自维护基础设施
│   ├── skills-install.py     # 平台取包 / 补装
│   ├── version-lint.py       # 五点版本一致性校验
│   ├── versions.json         # 自主版本线基线
│   └── patches/              # 本地补丁层（14 op）
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
