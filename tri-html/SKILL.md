---
name: tri-html
slug: tri-html
version: 1.1.1
displayName: 架构可视化分析（tri-html）
description: 项目架构可视化分析下游执行 skill。以系统架构设计师视角对指定项目（默认当前项目）进行全面深度架构分析，涵盖架构设计/目录结构/技术栈选型/代码设计/功能设计/特殊设计（安全/性能等）六维，生成单文件 HTML（内联 CSS/JS + Mermaid 图表）多维度可视化展示。当 tri-intent 快照下游路由建议指向本 skill（L2=I10、L3=arch-viz）时激活。支持独立安装，含上游依赖检测三态逻辑（快照模式/待识别/引导安装/降级模式）。
summary: 六维架构分析方法论 + 单文件 HTML 可视化组装（Mermaid 架构图/依赖图/目录树/技术栈矩阵），零依赖可双击打开，含双审批门与 §3.13 代码版权合规。
tags: [architecture-analysis, visualization, html, mermaid, single-file, arch-viz]
license: MIT
---

# 架构可视化分析（下游路由 · I10 arch-viz 子类）

> 本 skill 是 tri-intent 的下游执行 skill，依据快照 `snapshot.md` §三 结构化结论直接执行，不再重新识别意图。
> 用户心智：把 AI 当系统架构设计师，期望拿到一份能双击打开、多维度看清项目全貌的可视化 HTML 报告，而非一长串文字描述。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级；升级成功后继续，升级通道不可用则标注 D 态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：激活后 MUST 先读取快照 §三，校验 `intent.L2_核心意图` = I10 且 `L3_子意图` = arch-viz；越界（非 I10 或 L3 不匹配）MUST 停止并回退 tri-intent 重路由，NEVER 静默按空上下文执行。独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式。
2. **六维分析铁律**：MUST 完整覆盖六维分析（架构设计/目录结构/技术栈选型/代码设计/功能设计/特殊设计），任一维度缺失 = 半成品，NEVER 落盘交付。维度定义详见 `references/analysis-dimensions.md`。
3. **双审批门 + 单文件铁律**：
   - **门①（分析范围确认）**：扫描项目结构后，MUST 向用户复述分析范围（项目路径/根目录文件清单/识别到的技术栈/六维分析计划），用户确认通过方可进入分析。**禁跳门抢跑**。
   - **分析执行**：逐维分析，每维产出结论 + 对应 Mermaid 图表（架构图/依赖图/目录树/技术栈矩阵/功能模块图/特殊设计图）。
   - **门②（HTML 交付确认）**：HTML 落盘后 MUST 向用户呈现文件路径 + 截图预览描述 + 六维结论摘要，用户确认通过方为交付完成。
   - **单文件铁律**：产出 MUST 为单个 `.html` 文件，所有 CSS/JS 内联，Mermaid 图表内联，NEVER 产出多文件或依赖外部 CDN（离线可打开）。
4. **职责边界**：本 skill 负责「读快照 → 扫描项目 → 六维分析 → 生成 Mermaid 图表 → 组装单文件 HTML → 落盘交付」。意图识别（由 tri-intent）、编码开发（由 tri-coding）、代码审查（由 tri-review）、调试修复（由 tri-fix）不属于本 skill。**关键边界**：本 skill 只分析不改代码——发现问题记录于 HTML 报告的「架构观察」章节，修复由 tri-coding/tri-fix 执行。
5. **自检**：作答前用一句话声明「本次意图=I10，L3=arch-viz，已读取快照，当前阶段=<扫描/门①/分析/HTML组装/门②>，六维覆盖=<已覆盖/缺失X维>，单文件=<是/否>，落盘=<路径/未落盘>」，若与上述规则冲突则停止并纠正。

## 触发时机

- tri-intent 产出的快照中 `下游路由建议` 指向本 skill（L2=I10、L3=arch-viz）
- 用户直接说「分析这个项目的架构」「生成项目架构可视化 HTML」「画一张项目架构图」「项目全貌报告」等 arch-viz 语义

## 上游依赖检测（独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟）且 `下游路由建议` 指向本 skill | 读取快照 §三，按工作流推进（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | MUST 提示用户「本次请求尚未经意图识别」，引导先经 tri-intent 产出快照；NEVER 按空上下文静默执行 |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户明确拒绝安装 | 从用户请求自构造等价输入（意图判定默认 I10/L3=arch-viz + 任务要点 + 交付预期 + 项目路径），声明「当前为降级模式，意图识别精度低于完整工作流，生成的 HTML 仍需人工复核分析结论」 |

**模式 B 提示语**：
> 本 skill 依赖 tri-intent 进行意图识别与输入校验。当前未检测到 tri-intent。
> 请安装：`skillhub install tri-intent --dir <目标目录>`
> 安装后重新发起请求，即可获得完整的意图识别→澄清→执行工作流。

**模式 C 降级声明**：
> 用户明确拒绝安装后，从用户请求自构造等价输入（意图判定默认 I10/L3=arch-viz + 任务要点 + 交付预期 + 项目路径），声明「当前为降级模式，意图识别精度低于完整工作流，生成的 HTML 仍需人工复核分析结论」。

## 输入契约

读取 `.tribro/snapshots/<命名>.md` 的 §三 结构化结论区：

| 字段 | 用途 |
|---|---|
| `intent.L2_核心意图` | 确认为 I10，否则不应激活本 skill |
| `intent.L3_子意图` | 确认为 arch-viz，否则不应激活本 skill |
| `dimensions.D1_任务领域` | 决定技术栈语境（应为「软件工程/架构」） |
| `dimensions.D2_输入形态` | 项目路径 / 仓库根目录（默认当前项目） |
| `dimensions.D4_输出期望` | 应为「单文件 HTML」或「可视化报告」 |
| `任务要点` | 项目路径（默认当前项目）+ 关注维度 + 输出文件名 |
| `交付预期` | 用户期望的可视化形态与深度 |

> 若快照 `澄清门状态` = 待澄清，不应激活本 skill——先由 tri-intent 的 clarify-gate 完成澄清。

> **模式 C 降级输入**：从用户原始请求提取项目路径（默认当前项目）+ 关注维度（默认六维全覆盖）+ 输出文件名（默认 `<项目名>-arch-viz.html`）。

## 职责边界

- **本 skill 负责**：依据快照或用户直接请求，扫描项目 → 六维架构分析 → 生成 Mermaid 图表 → 组装单文件 HTML → 落盘交付
- **不负责**：意图识别（由 tri-intent）、编码开发（由 tri-coding）、代码审查（由 tri-review）、调试修复（由 tri-fix）、生成多文件网站或带后端的可视化应用（由 tri-coding）
- **关键边界**：本 skill「只分析不改代码」——架构问题记录于 HTML 报告「架构观察」章节，修复动作由 tri-coding/tri-fix 执行
- **与 tri-checklist 的边界**：tri-html 是「项目整体架构可视化分析」（I10 arch-viz），tri-checklist 是「项目审计清单生成」（I10 audit-checklist）；前者产出 HTML 全貌报告，后者产出 Markdown 自检清单，互不重叠

## tri-html 方法论（核心能力 · 可扩展）

> 六维架构分析 + Mermaid 可视化 + 单文件 HTML 组装，形成「扫描 → 分析 → 图表 → 组装」的完整方法论。

### 核心理念

> **架构是项目的骨架，可视化是理解的放大器。** 文字描述架构容易失真，图表能让架构一目了然；单文件 HTML 让可视化可分享、可离线、可归档。

### 六维分析框架

| 维度 | 核心问题 | 产出图表 | 详见 |
|---|---|---|---|
| 1. 架构设计 | 整体架构是什么模式？（单体/微服务/Serverless/事件驱动…） | Mermaid 架构图（C4 Context/Container） | `references/analysis-dimensions.md` §1 |
| 2. 目录结构设计 | 目录如何组织？分层是否清晰？ | Mermaid 目录树 + 文件统计 | `references/analysis-dimensions.md` §2 |
| 3. 技术栈选型 | 用了哪些技术？版本？依赖关系？ | Mermaid 技术栈矩阵 + 依赖图 | `references/analysis-dimensions.md` §3 |
| 4. 代码设计 | 模块划分/接口设计/数据模型？ | Mermaid 类图/ER 图 + 模块依赖图 | `references/analysis-dimensions.md` §4 |
| 5. 功能设计 | 实现了哪些功能？功能模块关系？ | Mermaid 功能模块图 + 用户旅程图 | `references/analysis-dimensions.md` §5 |
| 6. 特殊设计 | 安全/性能/可观测性/扩展性策略？ | Mermaid 特殊设计图（按实际） | `references/analysis-dimensions.md` §6 |

> 每维度的检查项清单、数据采集命令、输出图表模板详见 `references/analysis-dimensions.md`；Mermaid 图表语法模板详见 `references/mermaid-templates.md`。

### 单文件 HTML 组装策略

| 组成部分 | 实现 | 指针 |
|---|---|---|
| HTML 骨架 | HTML5 语义化标签，内联 `<style>` + `<script>` | `scripts/build_html.py` §骨架生成 |
| 样式 | 内联 CSS，深色/浅色主题切换（localStorage 记忆） | `scripts/build_html.py` §样式注入 |
| Mermaid 渲染 | 内联 mermaid.min.js（v10+，离线可用） | `scripts/build_html.py` §mermaid 注入 |
| 交互 | 折叠/展开维度、图表全屏、复制代码块 | `scripts/build_html.py` §交互注入 |
| 组装入口 | `python scripts/build_html.py --analysis <analysis.json> --out <output.html>` | 确定性组装逻辑 |

> HTML 组装的确定性逻辑（骨架/样式/Mermaid/交互注入）下沉 `scripts/build_html.py`，SKILL.md 仅留指针；分析结论以 JSON 输入，脚本输出单文件 HTML。

### 可扩展性

> 以下扩展点均为**追加维度/图表模板**，不改核心工作流：

| 扩展点 | 零改动扩展方式 |
|---|---|
| 新增分析维度 | 在 `references/analysis-dimensions.md` 追加一维（如「DevOps 设计」），脚本自动支持 |
| 新增图表类型 | 在 `references/mermaid-templates.md` 追加模板，build_html.py 自动渲染 |
| 新增交互组件 | 在 `scripts/build_html.py` §交互注入 追加 JS 片段 |
| 主题定制 | 在 `scripts/build_html.py` §样式注入 追加主题变量 |
| 技术栈识别规则 | 在 `references/analysis-dimensions.md` §3 追加识别规则（如检测 bun.lockb → Bun） |


## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：`tri-intent/references/version-gate.md`。**可执行实现（single source of truth for logic）**：本 skill 自带 `scripts/check_update.py`（与 tri-intent 同源一致，按 `--slug` 自动适配）。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。修订规则只改真源一处，脚本与真源保持同步。

**执行方式（MUST）**

1. 任一执行入口启动后、核心执行前，运行脚本并取 JSON：
   ```bash
   python scripts/check_update.py --slug tri-html --json
   ```
   - 节流：结果持久化缓存（默认 1440 分钟 / 24h 仅校验一次），`--force` 强制重查，`--dry-run` 只判定不真升级。
   - 脚本自动定位 skill 目录（默认脚本上级目录），`--slug` 显式指定自身 slug（如上）。
2. 解析 JSON 的 `state` 字段，按态处置：
   - `A` 校验通过 / `B` 离线降级 / `C` 通道降级 / `D` 升级降级 → **一律放行**，进入后续阶段；并据 `warnings` / `notes` / `actions` 在交付物或日志标注对应口径（如「版本校验未完成（离线）」「版本陈旧·自动升级失败」）。
   - `BLOCK` → **绝对禁止执行**，按 `block_code`（P2/P3/P4）输出结构化恢复指引（手动命令见 `actions` 字段）。
3. 退出码语义（供 shell 编排）：`0`=A 放行；`10`=B；`11`=C；`12`=D；`20`=阻断。判定规则：`<20` 放行，`>=20` 阻断。脚本自身异常时兜底降级放行（退出码 11），NEVER 因版本门自身故障导致 skill 无法启动。

**执行要点**

1. **端点取自配置**：API 主机 MUST 读自 `~/.skillhub/metadata.json`，NEVER 硬编码域名。营销官网 `skillhub.cn` 与 API 主机 `api.skillhub.cn` 是两个站点——官网对任意路径都返回 `200 + HTML` 兜底页，绝不可作校验端点。读不到配置即判通道不可用。
2. **校验请求**：`GET {api_host}/api/v1/skills/{slug}`，超时 ≤ 5s，失败重试 1 次，会话内仅校验一次。
3. **最新版取值**：`latestVersion.version`，缺失时回退 `skill.tags.latest`。平台**不提供** `min_compatible` / `deprecated` / `checksum_sha256` / `signature`，NEVER 依赖这些字段。
4. **响应有效性**（三条件同时成立）：HTTP 200 **且** `Content-Type` 含 `application/json` **且** 能解析出版本字段。仅看状态码会被 SPA 兜底页击穿。
5. **版本比较**：按 [SemVer](https://semver.org/lang/zh-CN/) 逐段整数比较，NEVER 字符串比较。
6. **四态判定**：
   - **A 校验通过**（响应有效且 `current >= latest`）→ 放行。
   - **B 离线降级**（网络不可达）→ 标注「版本校验未完成（离线）」后以当前版本继续。
   - **C 通道降级**（可达但响应无效 / 404 / 405 / 读不到配置）→ 标注「版本校验未完成（通道不可用）」+ 输出通道异常告警后继续。
   - **D 升级降级**（陈旧且已真实尝试自动升级但未完成）→ 标注「版本陈旧·自动升级失败」+ 输出手动升级指引后继续。
   - 四态 NEVER 用于绕过「已检出陈旧却不尝试升级」——MUST 先真实执行一次自动升级，失败方可落 D 态。
7. **更新通道（自动执行）**：检出陈旧 MUST 自动执行 `skillhub upgrade <slug>` → `skillhub verify <slug>`，升级前备份、签名明确不一致则回滚。CLI 不在 PATH 时回退 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`；CLI 缺失或升级失败 → 落 D 态降级继续，NEVER 阻断。以 junction 指向源码树的 `source: local` skill 跳过自动更新，改为提示维护者手动同步。命令细则、CLI 定位顺序与已知陷阱见真源。
8. **阻断条件 P1–P4** 与四处版本同步点见真源；发布前 MUST 通过 `python tri-forge/scripts/sync_registry.py --check`。

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 核心执行。版本检查未通过前 NEVER 进入以下任一执行步骤。

```
[模式判定: 快照模式 / 降级模式]
  │
  ▼
读取快照 §三 或 用户直接请求（提取项目路径/关注维度/输出文件名）
  │
  ▼
项目扫描（ls/find/cat package.json/识别技术栈/统计文件数）
  │
  ▼
门①·分析范围确认 ──不通过──→ 调整范围 → 再门①
  │（向用户复述：项目路径/根目录文件清单/识别到的技术栈/六维分析计划/输出文件名）
  │通过
  ▼
六维分析（逐维执行，每维产出结论 + Mermaid 图表源码）
  │  1. 架构设计分析 → 架构图
  │  2. 目录结构分析 → 目录树 + 文件统计
  │  3. 技术栈选型分析 → 技术栈矩阵 + 依赖图
  │  4. 代码设计分析 → 类图/ER 图 + 模块依赖图
  │  5. 功能设计分析 → 功能模块图 + 用户旅程图
  │  6. 特殊设计分析 → 安全/性能/可观测性图
  ▼
组装 analysis.json（六维结论 + Mermaid 源码 + 元数据）
  │
  ▼
调 scripts/build_html.py 生成单文件 HTML
  │
  ▼
落盘 HTML 至用户工作区（默认 <项目名>-arch-viz.html）
  │
  ▼
门②·HTML 交付确认 ──不通过──→ 携反馈补充分析/调整图表 → 再门②
  │（向用户呈现：文件路径 + 六维结论摘要 + 图表清单 + 文件大小）
  │通过
  ▼
交付完成（HTML 文件 + 可选 analysis.json 供二次定制）
```

## 交付产物机制

### 一、文件命名规范

沿用 tri-intent 快照命名：`<问题类型>_<日期>_<时间>_<会话ID>`

- HTML 文件名：`<项目名>-arch-viz_<日期>_<时间>.html`（如 `myapp-arch-viz_20260802_202348.html`）
- analysis.json（可选）：`<项目名>-arch-viz_<日期>_<时间>.json`

### 二、存放目录

```
用户工作区（项目根目录或用户指定目录）
└── <项目名>-arch-viz_<日期>_<时间>.html    # 最终交付物（单文件，可双击打开）

.tribro/                                     # 若不存在则先创建
├── snapshots/                               tri-intent 产出（已存在）
│   └── <命名>.md
└── arch-viz/                                本 skill 链路文档
    └── <命名>/
        ├── scope-confirmation.md            # 门①载体（分析范围确认）
        └── analysis.json                    # 六维分析结论（可选，供二次定制）
```

### 三、产物清单

| 产物 | 文件名 | 内容 | 审批门 |
|---|---|---|---|
| 分析范围确认 | `scope-confirmation.md` | 项目路径/根目录文件清单/技术栈/六维分析计划/输出文件名 | 门① |
| 单文件 HTML | `<项目名>-arch-viz_<日期>_<时间>.html` | 六维分析结论 + Mermaid 图表 + 交互组件，零依赖可双击打开 | 门② |
| 分析数据 | `analysis.json`（可选） | 六维结论结构化数据 + Mermaid 源码，供二次定制 | — |

## 质量标准

> 每条标准都可被独立验证。交付前逐行核对，任一不达标则回到对应门。

| 维度 | 标准 | 验证方式 |
|---|---|---|
| 六维覆盖 | 六维分析全部覆盖，无缺失维度 | 检查 analysis.json 含六个维度键 |
| 图表完整 | 每维至少 1 张 Mermaid 图表，图表源码语法正确 | Mermaid 语法校验（build_html.py 内置校验） |
| 单文件零依赖 | HTML 文件无外部 CDN/资源引用，可离线打开 | grep `<link rel=` / `<script src=http` 应为空 |
| 双审批门 | 门①范围确认 + 门②交付确认 100% 执行，无跳门 | 链路文档含两门确认记录 |
| 可双击打开 | HTML 文件双击在浏览器正常渲染，Mermaid 图表正常显示 | 人工浏览器验证 |
| 架构观察 | 发现的架构问题记录于「架构观察」章节，含严重程度与建议 | HTML 报告含「架构观察」段 |

## 落盘规则

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- 本 skill 链路文档落盘于 `.tribro/arch-viz/<命名>/`（可覆盖更新）
- **最终成果物（单文件 HTML）落盘至用户工作区**（项目根目录或用户指定目录，非 `.tribro/`）
- analysis.json 作为可选中间产物落盘 `.tribro/arch-viz/<命名>/`
- NEVER 在用户工作区生成多文件（CSS/JS/Mermaid 必须内联进单 HTML）

## 目录结构

```
tri-html/
├── SKILL.md                          # 主入口：六维分析 + 单文件 HTML 组装 + 双审批门 + §3.13 代码版权
├── README.md                         # 特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      # 版本变更记录（Keep a Changelog + SemVer）
├── _meta.json                        # 安装元数据（ownerId/publishedAt/slug/version，tri-forge 安装时生成）
├── references/
│   ├── analysis-dimensions.md        # 六维分析维度详细参考（检查项/采集命令/输出图表）
│   └── mermaid-templates.md          # Mermaid 图表语法模板（架构图/目录树/类图/ER图/旅程图）
├── scripts/
│   └── build_html.py                 # 单文件 HTML 组装器（骨架/样式/Mermaid/交互注入）
└── tests/
    └── tri-html-full-testcases.md    # 全场景测试用例
```

## 代码版权与许可证合规（硬红线）

> 本 skill 生成单文件 HTML，含内联 CSS/JS 与 Mermaid.js 库代码，属生成代码类，MUST 遵循 §3.13 硬红线。

### 四类风险

| 风险 | 本 skill 场景 | 规避措施 |
|---|---|---|
| 版权署名 | 内联 Mermaid.js（MIT 许可）MUST 保留版权声明 | build_html.py 注入 mermaid.min.js 时保留头部版权注释 |
| 许可证冲突 | HTML 产物若被商用，依赖库许可证须兼容 MIT | 仅内联 MIT 许可的库（Mermaid.js = MIT）；NEVER 内联 GPL/AGPL 库 |
| 依赖供应链 | Mermaid.js 版本须固定且校验完整性 | build_html.py 锁定 mermaid.min.js 版本 + SHA256 校验 |
| 标识披露 | HTML 报告含项目结构信息，可能泄露敏感路径 | 门①扫描时识别 .gitignore / .env / 密钥文件，在报告中脱敏或提示用户 |

### 提交前六项自检

1. **原创不照搬**：六维分析结论与图表源码 MUST 基于实际项目扫描生成，NEVER 照搬模板示例
2. **许可证兼容**：内联库均为 MIT 兼容；NEVER 内联 GPL/AGPL/SSPL 库
3. **依赖已授权**：Mermaid.js 等 MIT 库的使用符合其许可证条款（保留版权声明）
4. **披露到位**：HTML 报告「关于」章节列明内联库及其许可证
5. **license 字段已声明**：本 skill frontmatter `license: MIT` 已声明
6. **敏感信息脱敏**：项目结构中的密钥/凭证/敏感路径已脱敏

### 底线

**原创不照搬、许可证兼容、依赖已授权、披露到位、license 字段已声明、敏感信息脱敏——六条全过才可交付。**
