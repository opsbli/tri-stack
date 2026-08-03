---
name: I10-analyze
description: 【Doing·I10 分析处理】用户提供数据/文本/现象，要求分析、洞察、找规律、评估、诊断时触发，如数据分析、SWOT、情感分析、趋势判断。核心是从材料中挖掘洞察并给出解读。
---

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

> I10 分析处理现有两个 L3 子类，均**直接覆写下游 slug**（一跳，无需中介 skill），与 I06 article 子类设计一致。

### arch-viz（架构可视化分析）

- **触发语义**：任务要点含项目架构可视化语义（分析项目架构/生成架构可视化 HTML/画项目架构图/项目全貌报告/架构师视角分析项目）
- **L3 子意图**：`arch-viz`
- **下游覆写**：`tri-content` → **`tri-html`**
- **下游职责**：以系统架构设计师视角对项目进行六维架构分析（架构设计/目录结构/技术栈/代码设计/功能设计/特殊设计），生成单文件 HTML 可视化报告
- **下游依赖检测**：仅需检测 `tri-html/`（含 `.tribro/skills/tri-html/`），缺失即提示安装

### audit-checklist（审计清单生成）

- **触发语义**：任务要点含项目审计清单语义（生成审计 checklist/项目自检清单/改动审查测试清单/质量保障 checklist/commit 提交前检查清单）
- **L3 子意图**：`audit-checklist`
- **下游覆写**：`tri-content` → **`tri-checklist`**
- **下游职责**：对项目进行全面审计，覆盖改动点/审查点/测试点/测试步骤四维，支持 Git 暂存区/工作区/commit id 三种输入模式，产出 Markdown 复选框 checklist
- **下游依赖检测**：仅需检测 `tri-checklist/`（含 `.tribro/skills/tri-checklist/`），缺失即提示安装

### 子类 MECE 论证

| 子类 | 分析对象 | 产出 | 与 tri-content 边界 |
|---|---|---|---|
| arch-viz | 项目整体架构 | 单文件 HTML 可视化 | tri-content 是通用分析，arch-viz 专司架构可视化 |
| audit-checklist | 项目改动/审查/测试点 | Markdown checklist | tri-content 是通用分析，audit-checklist 专司审计清单 |

两个子类分析对象不同（架构 vs 改动点）、产出不同（HTML vs checklist），MECE 成立。默认 I10（无子类语义）仍路由 tri-content。

### 对称检测说明

tri-intent 的下游依赖检测已扩展为同时扫描 `skills/<slug>/`（hand-authored 源树）与 `.tribro/skills/<slug>/`（tri-forge 机器生成物），故 arch-viz/audit-checklist 子类落盘 `.tribro/skills/` 后即可被检测到。