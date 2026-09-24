---
name: tri-init
slug: tri-init
version: 1.0.0
displayName: 项目初始化（tri-init）
description: "内部专用工具 skill（不注册为 tri-intent 下游路由项，由用户直接调用）。用于将任意项目接入 tri-stack 开发流程：扫描项目目录检测技术栈（Java/Maven/RuoYi、TS/Vite、Go、Python 等），生成 AGENTS.md（AI 协作编码规范）、project-profile.json（机器可读项目元数据）与 .tribro/ 产物目录结构。如果检测到代码生成器（如 RuoYi generator），严格遵循其规范（租户字段 / 审计字段 / 编码规范）生成 project-profile。已有 AGENTS.md 时提示用户确认是否覆盖重新生成。支持独立安装，两态上游依赖检测。"
summary: 项目初始化：扫描技术栈 → 生成 AGENTS.md + project-profile → 创建 .tribro/ → 无缝衔接 tri-coding / tri-review。
tags: [init, project-setup, tech-stack, agents-md, project-profile, internal-tool]
license: MIT
---

# 项目初始化（内部专用工具）

> 本 skill 是 tri-stack 家族的**内部专用工具**，**不注册为 tri-intent 的下游路由项**——用户直接调用。
> 用户心智：**「我有一个项目（新或旧），帮我接入 tri-stack 开发流程」**——扫一遍项目，告诉 AI 这个项目用什么技术栈、遵循什么规范，然后就可以开始用 tri-coding / tri-review 了。

## 强制执行契约（Execution Contract · 最高优先级）

> 本节定义 skill「被激活后必须做什么」，优先级高于 Agent 的通用默认行为。**用户要求初始化项目或指定项目路径即视为激活本工作流**，MUST NOT 仅将其当作参考文档。

0. **版本检查前置硬门（第零步）**：任一执行入口启动后、核心执行前，MUST 先运行 `python scripts/check_update.py --slug tri-init --json`，按 `references/version-check-spec.md` 处置。版本检查完成前 NEVER 进入后续步骤。
1. **两模式强制**：激活后 MUST 先判定**单项目模式**还是**多项目模式**（前后端分离），再读取对应路径。NEVER 在未确认项目路径的情况下开始扫描。
2. **扫描诚实铁律**：技术栈检测 MUST 基于项目特征文件的**实际存在**，NEVER 猜测。检测不到的技术栈标注「未检测到」，NEVER 编造。
3. **AGENTS.md 保护铁律**：如果目标项目已有 AGENTS.md，MUST 展示现有内容摘要并询问用户「覆盖重新生成 / 保留合并 / 跳过」，NEVER 静默覆盖。
4. **代码生成器规范铁律**：如果检测到代码生成器模块（如 RuoYi generator），MUST 严格遵循其规范生成 project-profile——特别是数据库设计的**租户字段**（`tenant_id`）和**审计字段**（`create_dept / create_by / create_time / update_by / update_time`）与**逻辑删除字段**（`del_flag`）。NEVER 遗漏这些字段。
5. **project-profile 双格式**：MUST 同时产出 `project-profile.json`（机器可读，tri-coding 门② 消费）和 AGENTS.md 中嵌入的 project-profile 摘要（人可读）。两者数据 MUST 一致。
6. **幂等性**：重复运行 MUST 产生相同结果（幂等），NEVER 重复创建已存在的目录或文件。
7. **自检**：作答前 MUST 声明「本次模式=&lt;单项目/多项目&gt;，目标路径=&lt;路径&gt;，已扫描，技术栈=&lt;检测结果&gt;，AGENTS.md=&lt;新建/覆盖/保留&gt;，.tribro=&lt;已创建/已存在&gt;」。

## 触发时机

| 触发分支 | 典型信号 |
|---|---|
| 直接触发 | 「初始化这个项目」「把 ops-pilot 接入 tri-stack」「帮我生成 AGENTS.md」「初始化 .tribro」 |
| 补全触发 | 项目缺少 AGENTS.md 或 project-profile，tri-coding 门② 提示「建议先运行 tri-init」 |

**不由本 skill 处理**：

| 信号 | 归属 |
|---|---|
| 生成 skill 本身 | tri-forge |
| 写业务代码 | tri-coding |
| 安装 skill 到 AI 工具 | ops/install-skills.py |
| 审查代码 | tri-review |

## 上游依赖检测（独立使用时 · 两态）

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 独立模式**（默认） | 用户直接调用，无需 tri-intent | 自主完成扫描与生成 |
| **B · 引导安装** | 用户想通过 tri-intent 路由使用（可选） | 提示安装 tri-intent |

> 本 skill 为**自包含型**（声明无强制上游依赖），不依赖 tri-intent 即可完成全部功能。tri-intent 仅提供可选的路由统计能力。

## 输入契约

| 字段 | 必填 | 说明 |
|---|---|---|
| 项目路径 | ✅ | 后端项目根目录（含 `pom.xml` / `go.mod` / `package.json` 等特征文件） |
| 前端项目路径 | ⬜ | 前端项目根目录（前后端分离时提供） |
| 项目名称 | ✅ | 用于 AGENTS.md 标题和 project-profile |
| 技术栈偏好 | ⬜ | 如果自动检测不准确，用户可手动指定 |
| 代码生成器规范 | ⬜ | 如果项目使用代码生成器（RuoYi generator 等），指定规范来源 |

## 职责边界

- **本 skill 负责**：扫描项目 → 检测技术栈 → 生成 AGENTS.md → 生成 project-profile → 创建 `.tribro/`
- **不负责**：写业务代码（tri-coding）、生成 skill（tri-forge）、安装 skill（ops/install-skills.py）、版本管理（ops/version-lint.py）、审查代码（tri-review）
- **相邻边界**：

| 相邻 skill | 边界判据 |
|---|---|
| tri-forge | tri-forge 生成 **skill 包**；tri-init 初始化**项目环境**（让项目能用 tri-stack） |
| tri-coding | tri-coding 消费 project-profile **写代码**；tri-init 生成 project-profile 供 tri-coding 消费 |
| tri-review | tri-review 消费 project-profile **审查代码**；tri-init 生成 project-profile 供 tri-review 消费 |
| ops/install-skills.py | install-skills 安装 **skill 到 AI 工具**；tri-init 初始化**项目以使用 skill** |

## 核心能力方法论（项目扫描 · 可扩展）

### 技术栈检测规则

| 检测目标 | 特征文件 | 检测内容 |
|---|---|---|
| Java / Maven | `pom.xml` | `<java.version>`、`<groupId>`、`<artifactId>`、`<modules>` |
| Java / Gradle | `build.gradle` | `sourceCompatibility`、`dependencies` |
| Spring Boot | `pom.xml` 含 `spring-boot-starter` | Boot 版本、已启用 starter |
| RuoYi 框架 | 目录含 `ruoyi-*` 模块 | RuoYi 版本、代码生成器规范、租户/审计字段 |
| TypeScript / Vite | `tsconfig.json` + `vite.config.ts` | TS 版本、Vite 插件 |
| Vue | `package.json` 含 `vue` | Vue 版本、UI 库（Element Plus / Ant Design Vue） |
| React | `package.json` 含 `react` | React 版本、UI 库 |
| Go | `go.mod` | Go 版本、框架（Gin / Echo） |
| Python | `requirements.txt` / `pyproject.toml` | Python 版本、框架（Django / FastAPI） |
| 前后端分离 | 后端 + 前端分别检测 | API 前缀、端口、跨域配置 |

### 代码生成器规范提取

| 检测目标 | 特征 | 提取内容 |
|---|---|---|
| RuoYi generator | `ruoyi-generator/` 模块 | 模板位置、生成规则、标准字段 |
| 租户字段 | `TenantEntity.java` 或 `tenant_id` 列 | `tenant_id` 类型与命名 |
| 审计字段 | `BaseEntity.java` 或 `create_by/create_time` 列 | 审计字段名与类型 |
| 逻辑删除 | `del_flag` 列或 `@TableLogic` 注解 | 删除标志字段名与值 |

### 五步初始化流水线

```
项目路径
     ↓
① 技术栈扫描（特征文件检测 + 框架识别 + 代码生成器检测）
     ↓
② AGENTS.md 生成（AI 协作编码规范，基于扫描结果 + 用户确认）
     ↓
③ project-profile 生成（JSON + 嵌入 AGENTS.md 摘要）
     ↓
④ .tribro/ 目录结构创建
     ↓
⑤ 交付确认（输出初始化摘要 + 后续操作指引）
```

### 兜底处理（NEVER 静默失败）

| 场景 | 处置 |
|---|---|
| 版本检查异常 | 放行（自维护模式），标注口径 |
| 项目路径不存在 | 澄清，NEVER 创建不存在的目录 |
| AGENTS.md 已存在 | 展示摘要 + 三选一（覆盖/合并/跳过），NEVER 静默覆盖 |
| 技术栈无法检测 | 标注「未检测到」+ 请用户手动指定 |
| 代码生成器规范无法提取 | 标注「未检测到代码生成器」+ 使用通用规范 |

### 可扩展性

1. **新增技术栈检测规则**：在 `references/tech-stack-detection.md` 追加行（特征文件 / 检测内容），扫描逻辑自动适用
2. **新增代码生成器规范**：在 `references/db-conventions.md` 追加规范条目，profile 生成自动覆盖
3. **新增输出格式**：在 `templates/` 追加模板，初始化流程自动使用

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 判定模式 → 扫描 → 生成 → 交付。

| 步骤 | 动作 | 产出 |
|---|---|---|
| 1 | 确认项目路径（单项目 / 多项目） | 路径列表 |
| 2 | 技术栈扫描（每个项目路径） | 技术栈检测结果 |
| 3 | 代码生成器检测（如有） | 规范提取结果（租户字段 / 审计字段 / 逻辑删除） |
| 4 | AGENTS.md 生成或确认覆盖 | AGENTS.md |
| 5 | project-profile.json + 嵌入摘要 | project-profile.json |
| 6 | .tribro/ 目录创建 | .tribro/ 目录树 |
| 7 | 交付确认 | 初始化摘要 + 后续操作指引 |

## 交付产物

| 产物 | 位置 | 说明 |
|---|---|---|
| AGENTS.md | `<项目根>/AGENTS.md` | AI 协作编码规范（含 project-profile 摘要） |
| project-profile.json | `<项目根>/.tribro/project-profile.json` | 机器可读项目元数据（tri-coding 门② 消费） |
| .tribro/ | `<项目根>/.tribro/` | 产物目录结构（coding / fixes / reviews / sdlc 等子目录） |

## 版本检查与更新机制（强制技术约束 · 硬红线）

> **细则唯一真源**：`references/version-check-spec.md`（内部化持有）。
> **可执行实现**：`scripts/check_update.py`。

```bash
python scripts/check_update.py --slug tri-init --json
```

- `0` A · 一致 → 放行
- `12` D · 存在漂移 → 放行但告警
- 退出码 `<20` 放行，`>=20` 阻断

## 目录结构

```
tri-init/
├── SKILL.md                          主入口
├── README.md
├── CHANGELOG.md
├── references/
│   ├── version-check-spec.md         版本检查规范（内部化持有）
│   ├── tech-stack-detection.md       技术栈检测规则表
│   └── db-conventions.md             数据库规范（租户 / 审计 / 逻辑删除字段）
├── scripts/
│   ├── check_update.py               版本门
│   └── project-scan.py               项目扫描脚本（确定性逻辑）
├── templates/
│   ├── AGENTS.md                     AGENTS.md 模板
│   └── project-profile.json          project-profile 模板
└── tests/
    └── tri-init-full-testcases.md    测试用例
```
