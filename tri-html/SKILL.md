---
name: 架构可视化分析
slug: tri-html
version: 1.3.7
displayName: 架构可视化分析
description: 项目架构可视化分析下游执行 skill。以系统架构设计师视角对指定项目（默认当前项目）进行全面深度架构分析，涵盖架构设计/目录结构/技术栈选型/代码设计/功能设计/特殊设计（安全/性能等）六维，双引擎生成可视化产物：高精度 viewer 引擎（Typed JSON IR → 确定性校验 showcase 门禁 → 单文件交互 HTML：架构图/工作流/时序图/数据流/生命周期五类，深浅主题、聚焦、路径探查、角色透镜、故事播放、PNG/SVG/WebM 导出）+ Mermaid 兼容模式（目录树/类图/ER/旅程图）。当 tri-intent 快照下游路由建议指向本 skill（L2=I10、L3=arch-viz）时激活。支持独立安装，含上游依赖检测三态逻辑与渲染引擎 Node 探测降级链。
summary: 六维架构分析方法论 + 双渲染引擎（viewer 确定性高精引擎 / Mermaid 兼容）+ showcase 客观门禁 + 结构化诊断修复回执（2 轮上限）+ 单文件 HTML 交付，含双审批门与 §代码版权与许可证合规。
tags: [architecture-analysis, visualization, html, mermaid, single-file, arch-viz, typed-ir, viewer-engine]
license: MIT
---

# 架构可视化分析（下游路由 · I10 arch-viz 子类）

> 本 skill 是 tri-intent 的下游执行 skill，依据快照 `snapshot.md` §三 结构化结论直接执行，不再重新识别意图。
> 用户心智：把 AI 当系统架构设计师，期望拿到一份能双击打开、多维度看清项目全貌的可视化 HTML 报告，而非一长串文字描述。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（运行 `scripts/check_update.py` 做本地版本一致性校验，本仓库为自维护 fork、不做远端比对；按脚本输出与退出码处置）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：激活后 MUST 先读取快照 §三，校验 `intent.L2_核心意图` = I10 且 `L3_子意图` = arch-viz；越界（非 I10 或 L3 不匹配）MUST 停止并回退 tri-intent 重路由，NEVER 静默按空上下文执行。独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式。
2. **六维分析铁律**：MUST 完整覆盖六维分析（架构设计/目录结构/技术栈选型/代码设计/功能设计/特殊设计），任一维度缺失 = 半成品，NEVER 落盘交付。维度定义详见 `references/analysis-dimensions.md`。
3. **双审批门 + 单文件铁律**：
   - **门①（分析范围确认）**：扫描项目结构后，MUST 向用户复述分析范围（项目路径/根目录文件清单/识别到的技术栈/六维分析计划/图表引擎模式），用户确认通过方可进入分析。**禁跳门抢跑**。
   - **分析执行**：逐维分析，每维产出结论 + 对应图表（按 §渲染引擎双模 决策表分流：五类技术图走 viewer 引擎高精模式，其余走 Mermaid）。
   - **门②（HTML 交付确认）**：HTML 落盘后 MUST 向用户呈现文件路径 + 图表清单与文件大小 + 六维结论摘要 + **viewer 图表 deliver 客观回执**（checksPassed/errors/warnings/SHA-256），用户确认通过方为交付完成。
   - **单文件铁律**：主报告 MUST 为单个 `.html` 文件（CSS/JS/Mermaid 全内联，离线可打开）；每张 viewer 图表为**独立单文件**交互 HTML（各自零依赖）。NEVER 让主报告依赖外部 CDN，NEVER 产出散装多文件（viewer 图表与可选 analysis.json 除外）。
4. **职责边界**：本 skill 负责「读快照 → 扫描项目 → 六维分析 → 双引擎图表生成 → 组装单文件 HTML → 落盘交付」。意图识别（由 tri-intent）、编码开发（由 tri-coding）、代码审查（由 tri-review）、调试修复（由 tri-fix）不属于本 skill。**关键边界**：本 skill 只分析不改代码——发现问题记录于 HTML 报告的「架构观察」章节，修复由 tri-coding/tri-fix 执行。
5. **自检**：作答前用一句话声明「本次意图=I10，L3=arch-viz，已读取快照，当前阶段=<扫描/门①/分析/HTML组装/门②>，六维覆盖=<已覆盖/缺失X维>，引擎模式=<viewer高精/Mermaid兼容/降级>，单文件=<是/否>，落盘=<路径/未落盘>」，若与上述规则冲突则停止并纠正。

## 触发时机

- tri-intent 产出的快照中 `下游路由建议` 指向本 skill（L2=I10、L3=arch-viz）
- 用户直接说「分析这个项目的架构」「生成项目架构可视化 HTML」「画一张项目架构图」「项目全貌报告」等 arch-viz 语义
- 用户要求可视化系统架构/基础设施/云/安全/网络拓扑、技术工作流、API 调用时序、请求生命周期、数据管线/血缘、状态机，或要求「交互式架构图」「可导出的架构图（PNG/SVG）」「对比两版架构差异」时——若落在 I10 arch-viz 语义内同样路由本 skill，由 §渲染引擎双模 承接

## 上游依赖检测（独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测外部 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟）且 `下游路由建议` 指向本 skill | 读取快照 §三，按工作流推进（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | MUST 提示用户「本次请求尚未经意图识别」，引导先经 tri-intent 产出快照；NEVER 按空上下文静默执行 |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户明确拒绝安装 | 从用户请求自构造等价输入（意图判定默认 I10/L3=arch-viz + 任务要点 + 交付预期 + 项目路径），声明「当前为降级模式，意图识别精度低于完整工作流，生成的 HTML 仍需人工复核分析结论」 |

**模式 B 提示语**：
> 本 skill 依赖 tri-intent 进行意图识别与输入校验。当前未检测到 tri-intent。
> 请安装：`python ops/install-skills.py --target <目标目录>`
> 安装后重新发起请求，即可获得完整的意图识别→澄清→执行工作流。

**模式 C 降级声明**：以表格 **C · 降级模式** 行为单一真源（自构造等价输入 + 声明降级口径），NEVER 另行维护第二份重复文本。

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
- **不触发场景（Not-Trigger）**：本 skill 不接手「架构问题的直接修复」（转 tri-coding / tri-fix，本 skill 只分析不改码）；不接手「审计清单生成」（属 tri-checklist，为 I10 audit-checklist）；不接手「代码级深度剖析报告」（属 tri-code-analyzer）；不接手「识别用户意图」（由 tri-intent / 自身快照驱动）。

## tri-html 方法论（核心能力 · 可扩展）

> 六维架构分析 + 双引擎图表（viewer 高精 / Mermaid 兼容）+ 单文件 HTML 组装，形成「扫描 → 分析 → 图表 → 组装 → 客观门禁」的完整方法论。

### 核心理念

> **架构是项目的骨架，可视化是理解的放大器；确定性校验是可视化的可信度来源。** 文字描述架构容易失真，图表能让架构一目了然；单文件 HTML 让可视化可分享、可离线、可归档；showcase 客观门禁（9 项检查 + 结构化诊断）让「图好看」从主观感受变成可验证事实。

### 渲染引擎双模（viewer 高精引擎 + Mermaid 兼容）

> 双模机制是本 skill 的核心集成：Agent 分析层产出的图表按类型分流到两个渲染通道，任一通道故障都不阻断交付。

**引擎探测（分析前执行一次，结果带入门①）**：

```bash
python scripts/build_html.py --check-engine   # 退出码 0=viewer 可用 / 3=回落 Mermaid
```

**图表类型分流决策表**：

| 图表类型 | 引擎 | 产出 |
|---|---|---|
| 架构图（组件/服务/边界） | viewer `architecture` | 独立单文件交互 HTML |
| 工作流/流程（CI/CD/审批/Runbook） | viewer `workflow` | 独立单文件交互 HTML |
| 时序图（API 调用链/缓存回源） | viewer `sequence` | 独立单文件交互 HTML |
| 数据流/血缘 | viewer `dataflow` | 独立单文件交互 HTML |
| 生命周期/状态机 | viewer `lifecycle` | 独立单文件交互 HTML |
| 目录树/技术栈矩阵/类图/ER 图/用户旅程图 | Mermaid 兼容 | 内联进主报告 |

**降级链（绝不阻断交付）**：

| 检测结果 | 模式 | 行为 |
|---|---|---|
| Node ≥ 18 且引擎文件齐备 | viewer 高精 | 五类技术图经 `scripts/viewer` 引擎 deliver（showcase 门禁），主报告嵌入链接卡片 |
| Node 缺失 / 版本不足 / 引擎文件缺失 | Mermaid 兼容（降级） | `build_html.py` 自动回落，报告「高精度交互图表」节标注降级原因；**声明降级口径后继续** |

**高精度模式工作流（细则唯一真源：`references/viewer-authoring.md`）**：

1. 按类型路由表选型；只读对应 schema + 一个同类型示例（示例学字段形态，事实必须新写）；
2. 先写候选 IR（一条主路径、≤12 主节点、`meta.quality_profile: "showcase"`），**首个候选前禁读渲染器源码**；
3. `node scripts/viewer/bin/viewer.mjs validate <type> <ir.json> --quality showcase --json` 校验；读 `diagnostics[]` → 只改 `subject` 指向对象 → 用 `supportedFixes` → 重跑；**修复上限 2 轮**，未收敛则如实报告；
4. `deliver` 原子提交成品（SHA-256 回执）；通过校验的候选即冻结，永不再改；
5. 通过的图表在 analysis.json 顶层 `viewer_diagrams[]` 登记（type/title/ir），由 `build_html.py` 在组装时统一渲染并嵌入报告链接卡片。

**Mermaid 兼容模式**：流程与模板不变（`references/mermaid-templates.md`），Mermaid 转换为 viewer IR 时只取拓扑与语义、重新创作（`references/viewer-authoring.md` §三）。

**能力边界铁律**：作者契约（`viewer-authoring.md`）只承诺 vendored 引擎真实具备的能力；引擎尚不具备的外部演进能力（登记于 `references/engine-evolution-notes.md`）MUST NOT 进入创作路径或对用户承诺。

### 六维分析框架

| 维度 | 核心问题 | 产出图表 | 详见 |
|---|---|---|---|
| 1. 架构设计 | 整体架构是什么模式？（单体/微服务/Serverless/事件驱动…） | viewer 架构图（优先）或 Mermaid C4 Context/Container | `references/analysis-dimensions.md` §1 |
| 2. 目录结构设计 | 目录如何组织？分层是否清晰？ | Mermaid 目录树 + 文件统计 | `references/analysis-dimensions.md` §2 |
| 3. 技术栈选型 | 用了哪些技术？版本？依赖关系？ | Mermaid 技术栈矩阵 + 依赖图 | `references/analysis-dimensions.md` §3 |
| 4. 代码设计 | 模块划分/接口设计/数据模型？ | Mermaid 类图/ER 图 + 模块依赖图 | `references/analysis-dimensions.md` §4 |
| 5. 功能设计 | 实现了哪些功能？功能模块关系？ | viewer 工作流图（流程类）或 Mermaid 功能模块图 + 用户旅程图 | `references/analysis-dimensions.md` §5 |
| 6. 特殊设计 | 安全/性能/可观测性/扩展性策略？ | viewer 数据流/生命周期图（按语义匹配）或 Mermaid 特殊设计图 | `references/analysis-dimensions.md` §6 |

> 每维度的检查项清单、数据采集命令、输出图表模板详见 `references/analysis-dimensions.md`；Mermaid 图表语法模板详见 `references/mermaid-templates.md`；viewer 引擎创作契约详见 `references/viewer-authoring.md`。

### 单文件 HTML 组装策略

| 组成部分 | 实现 | 指针 |
|---|---|---|
| HTML 骨架 | HTML5 语义化标签，内联 `<style>` + `<script>` | `scripts/build_html.py` §骨架生成 |
| 样式 | 内联 CSS，深色/浅色主题切换（localStorage 记忆） | `scripts/build_html.py` §样式注入 |
| Mermaid 渲染 | 内联 mermaid.min.js（v10+，离线可用） | `scripts/build_html.py` §mermaid 注入 |
| 交互 | 折叠/展开维度、图表全屏、复制代码块 | `scripts/build_html.py` §交互注入 |
| viewer 图表卡片 | 探测引擎 → `viewer_diagrams[]` 逐张 deliver → 报告嵌入链接卡片（校验摘要 + 相对链接） | `scripts/build_html.py` §viewer 引擎集成 |
| 组装入口 | `python scripts/build_html.py --analysis <analysis.json> --out <output.html>` | 确定性组装逻辑 |
| 引擎探测入口 | `python scripts/build_html.py --check-engine` | 退出码 0=viewer 可用 / 3=回落 Mermaid |

> HTML 组装与 viewer 引擎集成的确定性逻辑（骨架/样式/Mermaid/交互注入/引擎探测/deliver 调用）下沉 `scripts/build_html.py`，SKILL.md 仅留指针；分析结论以 JSON 输入，脚本输出主报告单文件 + viewer 独立成品。

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

<!-- version-stub v1 · 瘦指针节点；细则唯一真源见 references/version-check-spec.md -->

> 任一执行入口启动后的**第零步**，先于核心执行阶段。细则唯一真源：`references/version-check-spec.md`；
> 可执行实现（逻辑唯一真源）：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、状态判定 MUST 由脚本完成；prompt 层 ONLY
> 「调用脚本 + 解析其 JSON 输出 + 按 `state` 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

```bash
python scripts/check_update.py --slug tri-html --json
```

- 处置：按脚本输出放行或阻断（判据与 `block_code` 语义见真源）；NEVER 因版本门自身故障阻断 skill 启动。

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
引擎探测（python scripts/build_html.py --check-engine → viewer高精 / Mermaid兼容降级）
  │
  ▼
门①·分析范围确认 ──不通过──→ 调整范围 → 再门①
  │（向用户复述：项目路径/根目录文件清单/识别到的技术栈/六维分析计划/图表引擎模式/输出文件名）
  │通过
  ▼
六维分析（逐维执行，每维产出结论 + 图表；按 §渲染引擎双模 决策表分流）
  │  1. 架构设计分析 → viewer 架构图 或 Mermaid C4 图
  │  2. 目录结构分析 → 目录树 + 文件统计（Mermaid）
  │  3. 技术栈选型分析 → 技术栈矩阵 + 依赖图（Mermaid）
  │  4. 代码设计分析 → 类图/ER 图 + 模块依赖图（Mermaid）
  │  5. 功能设计分析 → 功能模块图 + 用户旅程图（Mermaid / 流程类走 viewer）
  │  6. 特殊设计分析 → 安全/性能/可观测性图（按语义分流）
  ▼
viewer 高精图表（若有）：写候选 IR → validate showcase → 修复循环(≤2轮) → deliver 冻结
  │
  ▼
组装 analysis.json（六维结论 + Mermaid 源码 + viewer_diagrams[] + 元数据）
  │
  ▼
调 scripts/build_html.py：deliver viewer 图表 → 组装主报告单文件 HTML（嵌入链接卡片）
  │
  ▼
落盘至 `.tribro/html/<命名>/`（主报告 + viewer 独立成品 + 可选 analysis.json；用户指定交付目录时同步落一份）
  │
  ▼
门②·HTML 交付确认 ──不通过──→ 携反馈补充分析/调整图表 → 再门②
  │（向用户呈现：文件路径 + 六维结论摘要 + 图表清单 + deliver 客观回执 + 文件大小）
  │通过
  ▼
交付完成（主报告 HTML + viewer 独立图表 + 可选 analysis.json 供二次定制）
```

## 兜底处理（NEVER 静默失败）

本 skill 在下列五类异常下 MUST 走显式降级路径并**在交付回执中标注实际降级与未通过的门**，NEVER 静默失败、NEVER 把未过闸门的产物描述为成功：

| 异常类 | 触发 | 兜底路径 |
|---|---|---|
| ① 版本检查异常 | `scripts/check_update.py` 返回非 A/D 或退出码 ≥20（BLOCK） | 按 §版本检查与更新机制 处置；BLOCK 时停止产出并报告 |
| ② 门禁不过 | viewer / showcase 的 validate → deliver → visual-check 任一非零退出，或容器化闸门（`scrollHeight ≤ 视口`）不达标 | 按诊断给出的修复项（`labelAt` / viewBox 高度等）迭代；重试仍不达标 → **如实报告未通过的门与实测值**，NEVER 把非零退出描述为成功 |
| ③ 上游缺失 | 无 tri-intent 快照 / 无目标项目路径 | 走 §上游依赖检测 的降级模式，向用户确认待可视化的项目与图类型 |
| ④ hook 缺失 | 本 skill 以快照路由 / 用户直呼为触发源，**不以 hook 为触发源** | 无 hook 环境功能完整；NEVER 假设自动触发 |
| ⑤ 异常场景 | 技术栈无法解析 / 生成器依赖缺失 / 图规模超出单屏 | 依赖缺失 → 走双引擎的降级引擎并登记；规模超限 → 拆图或降低细节层级，**在报告中登记实际采用的视口与缩放**，NEVER 用缩小字号蒙混 |

## 🔴 检查点与红灯清单（STOP · NEVER）

### 🔴 用户确认检查点（STOP）
- 🔴 **STOP**：门①（分析范围确认）——扫描项目后向用户复述项目路径/根目录文件清单/技术栈/六维分析计划/图表引擎模式，未获用户确认 NEVER 进入分析。
- 🔴 **STOP**：门②（HTML 交付确认）——HTML 落盘后向用户呈现文件路径+六维结论摘要+viewer deliver 客观回执，未获用户确认 NEVER 视为交付完成。

### 🚫 红灯清单（NEVER）
- NEVER 跳门抢跑，任一门未通过携反馈回炉（§强制执行契约）
- NEVER 六维分析任一维度缺失仍落盘交付（§强制执行契约）
- NEVER 越界（非 I10 或 L3 不匹配）时静默按空上下文执行（§强制执行契约）
- NEVER 让主报告依赖外部 CDN 或产出散装多文件（§强制执行契约）
- NEVER 把未过闸门/非零退出的产物描述为成功（§兜底处理）
- NEVER 直接修复架构问题，只分析不改代码（§职责边界）

## 交付产物机制

### 一、文件命名规范

沿用 tri-intent 快照命名：`<问题类型>_<日期>_<时间>_<会话ID>`

- 主报告 HTML：`<项目名>-arch-viz_<日期>_<时间>.html`（如 `myapp-arch-viz_20260802_202348.html`）
- viewer 图表成品：`<主报告stem>-view-<序号>-<类型>.html`（如 `myapp-arch-viz_20260802_202348-view-1-architecture.html`，由 build_html.py 自动生成）
- analysis.json（可选）：`<项目名>-arch-viz_<日期>_<时间>.json`

### 二、存放目录

```
.tribro/                                     # 若不存在则先创建
├── snapshots/                               tri-intent 产出（已存在）
│   └── <命名>.md
└── html/<命名>/                              # 默认落盘：主报告 + viewer 成品 + 链路文档
    ├── <项目名>-arch-viz_<日期>_<时间>.html   # 主报告（单文件，可双击打开）
    ├── <主报告stem>-view-<n>-<类型>.html      # viewer 独立成品（每张单文件交互 HTML）
    ├── scope-confirmation.md                 # 门①载体（分析范围确认，含引擎模式）
    ├── analysis.json                         # 六维分析结论（可选，供二次定制）
    └── .viewer-ir/                           # viewer 候选 IR 中间产物（deliver 由 build_html.py 托管）
```

> 最终交付物（主报告 + viewer 成品）默认落盘 `.tribro/html/<命名>/`；用户显式指定交付目录时落用户指定位置（项目根目录），但 MUST 同时在 `.tribro/html/<命名>/` 保留副本；副本 MUST 包含主报告 + 全部 viewer 独立成品（保持相对链接结构，防图表卡片链接断裂）。

### 三、产物清单

| 产物 | 文件名 | 内容 | 审批门 |
|---|---|---|---|
| 分析范围确认 | `scope-confirmation.md` | 项目路径/根目录文件清单/技术栈/六维分析计划/引擎模式/输出文件名 | 门① |
| 主报告单文件 HTML | `<项目名>-arch-viz_<日期>_<时间>.html` | 六维分析结论 + Mermaid 图表 + viewer 图表链接卡片 + 交互组件，零依赖可双击打开 | 门② |
| viewer 独立成品（可选） | `<主报告stem>-view-<n>-<类型>.html` | 经 showcase 门禁的单文件交互图表（深浅主题/聚焦/路径探查/导出），deliver 回执校验 9/9 | 门② |
| 分析数据 | `analysis.json`（可选） | 六维结论结构化数据 + Mermaid 源码 + viewer_diagrams[]，供二次定制 | — |

## 质量标准

> 每条标准都可被独立验证。交付前逐行核对，任一不达标则回到对应门。

**产出前自检清单**（交付前逐项核对，任一不达标 → 回到对应门；重试仍失败 → §兜底处理 ②：如实报告未通过的门与实测值）：
- [ ] 结构：产物含渲染/诊断章节与清单，无缺失与占位符。
- [ ] 合规：未用禁用措辞，未越出「职责边界/Not-Trigger」。
- [ ] 溯源：关键结论附来源标注（结论标注铁律：事实/计算/推断/常识/猜测）。
- [ ] 可验证：命中内容可按下表「验证方式」复验。

| 维度 | 标准 | 验证方式 |
|---|---|---|
| 六维覆盖 | 六维分析全部覆盖，无缺失维度 | 检查 analysis.json 含六个维度键 |
| 图表完整 | 每维至少 1 张图表，图表源码语法正确 | Mermaid 语法校验（build_html.py 内置校验）+ viewer validate showcase |
| viewer 门禁 | 每张 viewer 图表 showcase 校验 9/9、0 error、0 warning，deliver 回执含 SHA-256 | `deliver --json` 回执字段核对 |
| 引擎降级诚实 | 引擎不可用时报告标注降级原因，NEVER 静默丢失 viewer_diagrams | 报告「高精度交互图表」节含降级说明 |
| 单文件零依赖 | 主报告与每张 viewer 成品均无外部 CDN/资源引用，可离线打开 | grep `<link rel=` / `<script src=http` 应为空 |
| 修复循环上限 | viewer 校验失败聚焦修复 ≤ 2 轮，未收敛如实报告 | 修复过程记录 |
| 双审批门 | 门①范围确认 + 门②交付确认 100% 执行，无跳门 | 链路文档含两门确认记录 |
| 可双击打开 | HTML 文件双击在浏览器正常渲染，Mermaid/viewer 图表正常显示 | 人工浏览器验证 |
| 架构观察 | 发现的架构问题记录于「架构观察」章节，含严重程度与建议 | HTML 报告含「架构观察」段 |

## 落盘规则

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- 本 skill 链路文档落盘于 `.tribro/html/<命名>/`（可覆盖更新）
- **最终成果物（主报告 + viewer 独立成品）默认落盘 `.tribro/html/<命名>/`**；用户显式指定交付目录时落用户指定位置（MUST 同步保留 `.tribro/html/<命名>/` 副本，口径见 §交付产物机制 · 二）
- analysis.json 与 viewer 候选 IR 作为可选中间产物落盘 `.tribro/html/<命名>/`
- NEVER 在用户工作区生成散装多文件（CSS/JS/Mermaid 必须内联进单 HTML；viewer 图表每张为独立单文件成品，属交付物而非散装文件）

## 目录结构

```
tri-html/
├── SKILL.md                          # 主入口：六维分析 + 双引擎图表 + 单文件 HTML 组装 + 双审批门 + §代码版权与许可证合规
├── README.md                         # 特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      # 版本变更记录（Keep a Changelog + SemVer）
├── _meta.json                        # 安装元数据（ownerId/publishedAt/slug/version，家族内部工具 安装时生成）
├── references/
│   ├── analysis-dimensions.md        # 六维分析维度详细参考（检查项/采集命令/输出图表）
│   ├── mermaid-templates.md          # Mermaid 图表语法模板（架构图/目录树/类图/ER图/旅程图）
│   ├── viewer-authoring.md           # viewer 引擎作者契约（类型路由/创作不变量/修复循环/deliver 验收）
│   ├── engine-evolution-notes.md     # 外部引擎演进对照登记（vendored 基线能力边界 + 同步评估要点）
│   └── version-check-spec.md       # 版本门细则（STUB 指针，NEVER 内联）
├── scripts/
│   ├── build_html.py                 # 单文件 HTML 组装器（骨架/样式/Mermaid/交互注入 + viewer 引擎集成）
│   └── viewer/                       # 内置高精度图表引擎（vendored MIT 组件，零运行时 npm 依赖，Node>=18）
│       ├── bin/viewer.mjs            # CLI：render/validate/deliver/compare/preview/visual-check/guide/brands/doctor/demo
│       ├── renderers/                # 五类渲染器 + shared（validator/geometry/diagnostics/i18n）
│       ├── schemas/                  # Typed JSON IR Schema（5 类 + common）
│       ├── delta/                    # architecture compare（Before/Delta/After）
│       ├── assets/template.html      # Viewer Runtime 模板（单文件交互成品模板）
│       ├── references/               # authoring-contract / delivery-contract / viewer-runtime
│       ├── examples/                 # 各类型 IR 示例（结构参照）
│       └── recipes/                  # 场景配方（guide 命令数据源）
└── tests/
    ├── run_exec_tests.py             # 可执行面自动化测试（31 用例真实执行 + 硬性断言）
    └── tri-html-full-testcases.md    # 全场景测试用例
```

> **引擎内部纪律（外层适配、内层不动）**：`scripts/viewer/` 为 vendored 第三方组件，tri-html 集成层只通过 CLI 调用（`node scripts/viewer/bin/viewer.mjs <command>`），**NEVER 直接修改 `scripts/viewer/` 内部实现**；引擎演进对照登记于 `references/engine-evolution-notes.md`（vendored 基线能力边界 + 同步评估要点）。

## 代码版权与许可证合规（硬红线）

> 本 skill 生成单文件 HTML，含内联 CSS/JS、Mermaid.js 库代码与 vendored 图表引擎，属生成代码类，MUST 遵循 §代码版权与许可证合规 硬红线。

### 四类风险

| 风险 | 本 skill 场景 | 规避措施 |
|---|---|---|
| 许可证冲突 | HTML 产物若被商用，依赖库许可证须兼容 MIT | 仅使用 MIT 许可的库（Mermaid.js = MIT；viewer 引擎 = MIT）；NEVER 内联 GPL/AGPL 库 |
| 依赖供应链 | Mermaid.js 版本须固定且校验完整性；viewer 引擎零运行时 npm 依赖（Node 标准库 only） | build_html.py 锁定 mermaid.min.js 版本 + SHA256 校验；viewer 引擎不引入任何运行时依赖 |
| 标识披露 | HTML 报告含项目结构信息，可能泄露敏感路径 | 门①扫描时识别 .gitignore / .env / 密钥文件，在报告中脱敏或提示用户；报告「关于」章节披露 Mermaid.js 与 viewer 引擎及其许可证 |

### 提交前六项自检

1. **原创不照搬**：六维分析结论与图表源码 MUST 基于实际项目扫描生成，NEVER 照搬模板示例
2. **许可证兼容**：内联库均为 MIT 兼容；NEVER 内联 GPL/AGPL/SSPL 库
3. **依赖已授权**：Mermaid.js、viewer 引擎等 MIT 组件的使用符合其许可证条款（保留版权声明与 NOTICE）
4. **披露到位**：HTML 报告「关于」章节列明内联库、viewer 引擎及其许可证
5. **license 字段已声明**：本 skill frontmatter `license: MIT` 已声明
6. **敏感信息脱敏**：项目结构中的密钥/凭证/敏感路径已脱敏

### 底线

**原创不照搬、许可证兼容、依赖已授权、披露到位、license 字段已声明、敏感信息脱敏——六条全过才可交付。**
