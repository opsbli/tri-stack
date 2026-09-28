---
name: I10-analyze
description: 【Doing·I10 分析处理】用户提供数据/文本/现象，要求分析、洞察、找规律、评估、诊断时触发，如数据分析、SWOT、情感分析、趋势判断。核心是从材料中挖掘洞察并给出解读。
---

> **分支范围提示（编程工作流专线）**：本文件描述的是**分类识别逻辑**，该逻辑完整保留；
> 但其中提到的部分下游 skill **未包含在本分支**。路由真源以 `SKILL.md` §一 路由映射表为准；
> 未包含的落点在快照中标注「本分支未包含」，全量实现见归档分支 `archive-full-skills-20260924`。


# I10 分析处理（Doing）

## 识别特征

- 动词为 **分析 / 评估 / 解读 / 找规律 / 看看有什么问题 / 诊断**
- 输入是待剖析的材料（数据表/文本/日志/现象），输出是**洞察与断**
- 典型语料：「分析这份销售数据的趋势」「这段用户评论做情感分析」「评估这个方案的可行性」

## 与邻近意图边界

- vs **I09 总结提炼**：I09 压缩事实，I10 产出评判与洞察
- vs **I04 决策辅助**：I10 呈现分析不强制选择，I04 收敛到选哪个
- vs **I05 推理计算**：I10 面向开放数据/无唯一解，I05 求确定正解

## 子类路由

> I10 分析处理现有四个 L3 子类，均**直接覆写下游 slug**（一跳，无需中介 skill），与 I06 article 子类设计一致。

### arch-viz（架构可视化分析）

- **触发语义**：任务要点含项目架构可视化语义（分析项目架构/生成架构可视化 HTML/画项目架构图/项目全貌报告/架构师视角分析项目；v1.2.0 起扩展：拓扑/时序/数据流/状态机可视化、交互式架构图、架构差异对比）
- **L3 子意图**：`arch-viz`
- **下游覆写**：默认 I10 → **`tri-html`**（I10 默认通用分析在本分支无下游，原 tri-content）
- **下游职责**：以系统架构设计师视角对项目进行六维架构分析（架构设计/目录结构/技术栈/代码设计/功能设计/特殊设计），生成主报告单文件 HTML + viewer 高精度交互图表（内置确定性渲染引擎，Node≥18 可用时启用，缺失自动回落 Mermaid 兼容模式）
- **下游依赖检测**：仅需检测源码树 `tri-html/`，缺失即提示安装

### audit-checklist（审计清单生成）

- **触发语义**：任务要点含项目审计清单语义（生成审计 checklist/项目自检清单/改动审查测试清单/质量保障 checklist/commit 提交前检查清单）
- **L3 子意图**：`audit-checklist`
- **下游覆写**：默认 I10 → **`tri-checklist`**（I10 默认通用分析在本分支无下游，原 tri-content）
- **下游职责**：对项目进行全面审计，覆盖改动点/审查点/测试点/测试步骤四维，支持 Git 暂存区/工作区/commit id 三种输入模式，产出 Markdown 复选框 checklist
- **下游依赖检测**：仅需检测源码树 `tri-checklist/`，缺失即提示安装

### code-analyzer（代码库深度剖析）

- **触发语义**：任务要点含代码库深度剖析语义（剖析代码库/帮我读懂这个项目/接手项目全维度分析/代码级深度剖析/吃透代码库/代码库 onboarding）
- **L3 子意图**：`code-analyzer`
- **下游覆写**：默认 I10 → **`tri-code-analyzer`**（I10 默认通用分析在本分支无下游，原 tri-content）
- **下游职责**：以架构师+程序员双视角对代码库执行七阶段剖析管道（定位→识别→拓扑→穿透→横切→对照→交付），产出五部分 Markdown 报告（架构拓扑/工程实现/风格审计/Mermaid 四图/上手指南），每条结论强制附 file:line 证据锚，对照内置技术栈知识库（arkts/electron/flutter/qt/react-native/taro/uni-app/通用后端）校准，未覆盖栈经官方文档联网建卡
- **下游依赖检测**：检测源码树 `tri-code-analyzer/` 或 `.tribro/skills/tri-code-analyzer/`，缺失即提示安装

### design-doc（详细设计说明书模板填充）

- **触发语义**：任务要点含「按既有模板填写设计文档」语义（按这个模板填设计文档 / 把详细设计说明书写了 / 补充：xxx 按模板格式填写 / 照着模板把每一节补全）
- **L3 子意图**：`design-doc`
- **下游覆写**：默认 I10 → **`code-design-doc`**（I10 默认通用分析在本分支无下游，原 tri-content）；该 skill **安装于平台用户级** `~/.workbuddy/skills/code-design-doc/`，非本仓库源码树成员
- **下游职责**：以甲方《详细设计说明书》模板为骨架、以真实源码为唯一证据源，逐节填充「补充：xxx」小节与设计表格；五阶段串行（模板解析 → 代码取证 → 六段式填充 → 证据门禁 → 回填交付），每条断言强制 `file:line` 证据锚，无证据标 `[待确认]`，产出案级证据台账
- **下游依赖检测**：检测 `code-design-doc/`（本仓库源码树 / `.tribro/skills/` / **平台用户级** `~/.workbuddy|.trae|.cursor|.qcoder/skills/` / 注册表），缺失即提示安装

### 子类 MECE 论证

| 子类 | 分析对象 | 产出 | 与 I10 默认的边界 |
|---|---|---|---|
| arch-viz | 项目整体架构 | 单文件 HTML 可视化 | I10 默认（原 tri-content）是通用分析，arch-viz 专司架构可视化 |
| audit-checklist | 项目改动/审查/测试点 | Markdown checklist | I10 默认（原 tri-content）是通用分析，audit-checklist 专司审计清单 |
| code-analyzer | 代码库工程实现细节 | 五部分深度剖析报告（Markdown + 内嵌 Mermaid） | I10 默认（原 tri-content）是通用分析，code-analyzer 专司代码级剖析（证据锚定+上手指南） |
| design-doc | 源码 + 甲方设计说明书模板 | 按模板格式填满的交付文档（六段式分节 + 设计表） | I10 默认（原 tri-content）是通用分析，design-doc 专司**受模板逐节约束**的设计文档产出（证据锚定 + 案级台账） |

四个子类交付物形态互斥（HTML 图表 / 复选框清单 / 深度剖析报告 / 模板化交付文档），分析对象与深度不同，MECE 成立。默认 I10（无子类语义）在本分支无下游（原 tri-content 未包含）。

### 冲突消解（code-analyzer × arch-viz）

- 「画架构图/生成可视化 HTML/交互式架构图」→ arch-viz（tri-html）。
- 「剖析/读懂/接手项目/代码级深度分析」→ code-analyzer（tri-code-analyzer）。
- 同时命中（如「深度分析项目并画图」）→ 按**用户指定输出物形态**判定：要 HTML 交互图表 → arch-viz；要深度报告 → code-analyzer。code-analyzer 报告内嵌 Mermaid 四图已覆盖基础图形需求；用户需交互式可视化时由 code-analyzer 提示续接 tri-html。

### 对称检测说明

tri-intent 的下游依赖检测已扩展为同时扫描 `skills/<slug>/`（hand-authored 源树）与 `.tribro/skills/<slug>/`（tri-forge 机器生成物），故 arch-viz/audit-checklist 子类落盘 `.tribro/skills/` 后即可被检测到。