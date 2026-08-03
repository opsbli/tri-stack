# tri-skills

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)

**模块化、可组合的 AI 智能体技能集合**

</div>

---

## 简介

**tri-skills** 是一个面向 AI 智能体的技能集合，提供 **24 个模块化、可组合的 skill**，覆盖意图路由、编码、审查、修复、规划、内容生成、翻译、工作流编排等多个领域。每个 skill 都是一个独立的功能单元，遵循统一的接口规范，可被任意 AI 工具按需加载和调用。

### 设计理念

- **模块化** — 每个 skill 职责单一，独立可部署，低耦合高内聚
- **可组合** — 通过 tri-intent 路由 + tri-workflow 编排，skill 可组合成复杂工作流
- **统一规范** — 所有 skill 遵循相同的接口契约、文档标准和版本管控
- **工具无关** — 不绑定特定 AI 工具，任何支持 skill 加载的系统均可使用

---

## 技能目录

### 核心

| 名称 | 描述 |
|------|------|
| [tri-intent](tri-intent/) | 意图识别与路由。分析用户需求，确定最佳执行路径，调度下游 skill |

### 编码

| 名称 | 描述 |
|------|------|
| [tri-coding](tri-coding/) | 按任务要点执行代码编写，遵循最小化原则 |
| [tri-review](tri-review/) | 代码审查与质量评估，覆盖正确性、安全、性能、可维护性 |
| [tri-fix](tri-fix/) | 定位并修复问题，精准修改根因 |
| [tri-plan](tri-plan/) | 需求分析、风险评估与分步实施规划 |

### 内容

| 名称 | 描述 |
|------|------|
| [tri-content](tri-content/) | 通用内容生成，按任务要点输出结构化内容 |
| [tri-article](tri-article/) | 文章撰写与编辑，支持多种文体和风格 |
| [tri-translate](tri-translate/) | 翻译，遵循信达雅原则 |
| [tri-html](tri-html/) | 可视化图表，HTML 生成，支持现代 CSS 和响应式设计 |

### 交互

| 名称 | 描述 |
|------|------|
| [tri-ask](tri-ask/) | 苏格拉底式反问与需求澄清，通过结构化提问明确需求 |
| [tri-bs](tri-bs/) | 头脑风暴与创意生成，多角度发散思考 |
| [tri-express](tri-express/) | 表达与呈现，将信息转换为清晰优雅的表达 |

### 流程

| 名称 | 描述 |
|------|------|
| [tri-loop](tri-loop/) | 迭代循环控制，管理与执行重复性任务 |
| [tri-workflow](tri-workflow/) | 工作流编排，将多个 skill 编排为 DAG 工作流 |
| [tri-sdlc](tri-sdlc/) | SDLC 全流程管理，覆盖 12 阶段项目生命周期 |
| [tri-action](tri-action/) | 操作执行，在限定范围内执行指定操作 |

### 工具

| 名称 | 描述 |
|------|------|
| [tri-checklist](tri-checklist/) | 检查清单生成，确保过程完整可追溯 |
| [tri-cache](tri-cache/) | 缓存复用，指纹去重 + 新鲜度标记 |
| [tri-evolve](tri-evolve/) | 自我进化，从交互中提取模式并沉淀为 skill |
| [tri-god](tri-god/) | 全视角综合评估，多维度分析评审 |
| [tri-meta](tri-meta/) | 元技能管理，管理 skill 自身的生命周期 |
| [tri-mm](tri-mm/) | 多媒体生成 |
| [tri-music](tri-music/) | 音乐生成，AI 驱动的音乐创作 |
| [tri-true](tri-true/) | 真值验证与断言，验证事实与逻辑一致性 |

---

## 快速开始

### 前提条件

- 支持 AI 技能加载的 AI 工具（如 TRAE IDE、Cursor、Claude Code 等）
- 或支持 SkillHub 协议的工具环境

### 安装

#### 方式一：克隆仓库

```bash
git clone https://github.com/your-username/tri-skills.git
cd tri-skills
```

#### 方式二：SkillHub 安装（如环境支持）

```bash
# 安装全部 skill
skillhub install tri-skills

# 安装单个 skill
skillhub install tri-skills/tri-coding
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
├── tri-intent/              # 核心：意图识别与路由
├── tri-coding/              # 编码
├── tri-review/              # 审查
├── tri-fix/                 # 修复
├── tri-plan/                # 规划
├── tri-content/             # 内容生成
├── tri-article/             # 文章撰写
├── tri-translate/           # 翻译
├── tri-html/                # HTML 生成
├── tri-ask/                 # 需求澄清
├── tri-bs/                  # 头脑风暴
├── tri-express/             # 表达呈现
├── tri-loop/                # 迭代控制
├── tri-workflow/            # 工作流编排
├── tri-sdlc/                # SDLC 管理
├── tri-action/              # 操作执行
├── tri-checklist/           # 检查清单
├── tri-cache/               # 缓存复用
├── tri-evolve/              # 自我进化
├── tri-god/                 # 综合评估
├── tri-meta/                # 元技能管理
├── tri-mm/                  # 思维导图
├── tri-music/               # 音乐生成
├── tri-true/                # 真值验证
├── LICENSE                  # MIT 许可证
├── README.md                # 本文件
├── CONTRIBUTING.md          # 贡献指南
├── CODE_OF_CONDUCT.md       # 行为准则
├── SECURITY.md              # 安全策略
├── CHANGELOG.md             # 变更日志
└── .gitignore               # Git 忽略规则
```

---

## 版本管控

每个 skill 都包含独立的版本号、CHANGELOG 和内置版本检查机制，确保在运行时可自动检测并更新到最新版本。

全局版本变更记录见 [CHANGELOG.md](CHANGELOG.md)，各 skill 的详细变更记录见各自目录下的 `CHANGELOG.md`。

---

## 贡献指南

欢迎任何形式的贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解：

- 如何提交 Issue（Bug 报告 / 功能请求 / 新 skill 请求）
- 如何提交 PR
- 编码规范与 skill 开发标准

同时请遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

---

## 安全策略

发现安全漏洞？请参阅 [SECURITY.md](SECURITY.md) 了解如何报告。

---

## 许可证

本项目采用 MIT 许可证 — 详见 [LICENSE](LICENSE) 文件。

---

## 联系

- 项目主页：https://github.com/your-username/tri-skills
- 作者：tribro-agent

---

<div align="center">
  <sub>Built with ❤️ by tribro-agent</sub>
</div>