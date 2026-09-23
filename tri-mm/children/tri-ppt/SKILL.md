---
name: 演示文稿全流程自动化
slug: tri-ppt
version: 1.2.0
displayName: 演示文稿全流程自动化
description: 演示文稿全流程自动化子SKILL。从 tri-mm 接收 I15·PPT 任务后，先「从全网采集文字/图片/图表素材」→ 提交素材审计 → 据已审计素材设计大纲与逐页动效方案 → 提交设计审计（可多轮迭代）→ 全部通过后生成精美 PPTX。当 tri-mm 路由建议指向本子SKILL时激活。作为 tri-mm 子SKILL随包安装，支持独立安装，含上游依赖检测两态逻辑（编排模式/引导安装）。
summary: 演示文稿端到端自动化：全网采集 → 双审计门 → 生成可直接下载的 PPTX。
tags: [ppt, presentation, slide, web-research, design-plan, animation, tri-mm-child]
license: MIT
---

# 演示文稿全流程自动化

> 本 skill 是 tri-mm 在 I15 多媒体生成下的**演示文稿类子 SKILL**，并升级为**端到端全自动流水线**：收到 PPT 任务后，先根据用户提问从全网采集文字/图片/图表素材 → 提交**素材审计** → 据已通过审计的素材设计每页大纲与逐页动效方案 → 提交**设计审计**（可多轮迭代）→ 全部通过后生成设计精美、可直接下载的 PPTX。
>
> 用户心智：把 AI 当"从选题到成片的全案幻灯片工作室"——你只给主题，它搜素材、出方案、过两道审计门、交付可下载的 PPTX，全程不黑箱。

## 强制执行契约（Execution Contract · 最高优先级）

> 本节定义 skill「被激活后必须做什么」，优先级高于 Agent 的通用默认行为。**tri-mm 依 I15 委派且媒体类型=PPT 即视为激活本子SKILL，不得仅当参考文档。**

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（见该章 STUB 指向的 `references/version-check-spec.md` 真源）；升级通道不可用则标注 C 态降级继续。版本检查完成前 NEVER 进入后续步骤。
1. **强制前置**：收到 tri-mm 转交任务 MUST 先读取快照 §三，校验 `intent.L2_核心意图 = I15` 且媒体类型 ∈ {PPT}；NEVER 跳过校验直接执行。独立使用 MUST 先走 §上游依赖检测。
2. **采集先于设计**：MUST 先完成 §全流程方法论 阶段一（全网素材采集 + 整理），产出 `materials.md` 素材库，NEVER 在素材审计通过前进入大纲设计。
3. **双审计门不可跳**：素材库 MUST 经**审计门①**通过后方可设计；大纲 + 动效方案 MUST 经**审计门②**通过后方可生成。任一未通过 NEVER 进入下一阶段。
4. **子类型识别**：MUST 识别演示场景（汇报/教学/路演/发布会），据此调整结构深度与采集广度。
5. **产物落盘**：生成演示文稿 MUST 落盘 `.tribro/multimedia/ppt/<命名>/` 并返回可访问路径（PPTX，必要时 PDF），NEVER 仅对话内联。
6. **参数可复现**：MUST 记录版式/配色/字体/动效等设计参数与素材来源，使产物可重生成。
7. **自检句**：作答前声明「本次意图=I15·PPT，已读取快照，场景=<...>，素材审计通过=<是/否>，设计审计通过=<是/否>」；与快照冲突 MUST 停止纠正。

## 触发时机

- tri-mm 媒体类型识别为「PPT」后路由至本子SKILL
- 意图范围：I15 多媒体生成 · 演示文稿类
- 关键词（任一）：PPT/幻灯片/演示/汇报/路演/课件/从零做 PPT

## 上游依赖检测（独立使用时）

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 编排模式** | 由 tri-mm 转交任务（含快照 §三 + 媒体类型=PPT） | 读取任务直接推进 |
| **B · 引导安装** | 未被 tri-mm 调用且未检测到 tri-mm / 快照 | MUST 提示依赖并引导安装 tri-mm |

**模式 B 提示语**：
> 本子SKILL 是 tri-mm 的演示文稿类专家，需由 tri-mm 路由媒体任务。请先安装：`skillhub install tri-mm --dir <目标目录>`。

## 输入契约

| 字段 | 用途 |
|---|---|
| `intent.L2_核心意图` | MUST = I15 |
| 媒体类型（tri-mm 标注） | MUST = PPT |
| `dimensions.D1_任务领域` | 演示主题/行业语境 |
| `dimensions.D2_输入形态` | 是否有素材/数据/参考 |
| `dimensions.D4_输出期望` | 格式（PPTX/PDF）、比例（默认 16:9） |
| `任务要点` | 产物硬约束（页数/风格/配色/受众） |
| `交付预期` | 用户期望交付物 |

> 若快照 `澄清门状态=待澄清`，不应激活。

## 职责边界

- **负责**：① 全网素材采集与整理；② 素材审计；③ 大纲 + 逐页动效方案设计；④ 设计审计；⑤ PPTX 生成与落盘。
- **不负责**：音乐（tri-music）、图片独立生成（tri-image）、视频（tri-video）、纯文本（tri-content）、业务代码（tri-coding）。
- 与 tri-mm：tri-mm 负责意图识别与媒体路由；本子SKILL 负责 PPT 全流程专业执行。
- **MECE 说明**：本 skill 仅增强 I15·PPT 既有子 SKILL 能力，不新增任何 L2/L3 意图认领，与家族路由零冲突。

## 全流程方法论（核心能力 · 可扩展）

> 五阶段串行 + 双审计门。每个阶段产物 MUST 落盘后再进入下一阶段。

### 阶段一 · 全网素材采集

根据用户提问/主题，从全网搜集三类素材并整理为 `materials.md` 素材库：

| 类型 | 采集方式 | 落点 |
|------|----------|------|
| 文字内容 | WebSearch/WebFetch 检索权威来源，提炼关键论点/数据/案例/金句 | `materials.md` 文字区 |
| 图表数据 | WebSearch 检索统计/对比数据；记录数值与来源，供阶段三原生图表使用 | `materials.md` 图表区 |
| 图片素材 | **优先 ImageGen 生成主题配图**（版权无忧、风格统一）；必要时 WebSearch 检索可商用图床 URL 并经用户确认后下载 | `materials.md` 图片区 + 本地图文件 |

- 素材 MUST 标注来源 URL 与用途（哪页用/做封面还是配图）。
- 版权安全：外采图片 MUST 为可商用授权；无授权则改用 ImageGen 生成。
- 素材库结构化：同步产出机器可读 `materials.json`（字段见 `references/materials-template.md`），供生成脚本消费。

### 审计门① · 素材审计（不可跳）

1. 呈现 `materials.md` + 缩略图，明确「请确认素材 / 指出需补充或剔除的项」。
2. 通过 → 阶段二；补充/剔除 → 修订素材库回本门；取消 → 终止。

### 阶段二 · 大纲 + 逐页动效方案设计

逐维度填充设计（主题受众/结构页数/每页大纲/版式/配色字体/图表图示/**动效转场**/交付格式），并把已审计素材映射到每页。产出 `design.md` 与机器可读 `design.json`（schema 见 `references/design-template.md`）。

- **动效方案**：逐页标注转场类型（fade/wipe/push/split/none，目录见 `references/design-template.md` 动效目录表）与可选强调点；生成脚本据此注入幻灯片切换效果。

### 审计门② · 设计审计（不可跳，可多轮）

1. 呈现 `design.md`（含每页大纲 + 动效方案），明确「请确认或提出修改意见」。
2. 通过 → 阶段三；修改 → 修订 `design.md` 回本门（支持多轮迭代直至通过）；取消 → 终止。

### 阶段三 · 生成 PPTX

1. 据 `design.json` + `materials.json` 构造版式/配色/字体/图片/图表/转场参数。
2. 运行 `python scripts/build_pptx.py --spec <dir>/design.json --materials <dir>/materials.json --out .tribro/multimedia/ppt/<命名>/<命名>.pptx`（脚本细则见 `references/design-template.md`）。
3. 若环境缺 `python-pptx`，脚本会给出 `pip install python-pptx` 提示；或委托 `pptx` skill 兜底生成。
4. 记录设计参数与素材来源，产物落盘 `.tribro/multimedia/ppt/<命名>/`。

### 可扩展性

1. 新增版式：在 `scripts/build_pptx.py` 布局函数表追加。
2. 新增场景：阶段一采集广度按场景调整。
3. 新增动效：动效目录表（references）与脚本转场映射同步追加。

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：`references/version-check-spec.md`。**可执行实现**：本 skill 自带 `scripts/check_update.py`（与 tri-intent 同源一致，按 `--slug` 自动适配）。
> **铁律**：版本比较/升级/回退/四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析 JSON + 按 state 处置」。

**执行方式（MUST）**：启动后运行 `python scripts/check_update.py --slug tri-ppt --json`；按 `state` 处置——`A/B/C/D` 一律放行（分别标注「校验通过 / 离线降级 / 通道降级 / 升级降级」），`BLOCK` 绝对禁止执行并按 `actions` 给恢复指引。退出码 `<20` 放行，`>=20` 阻断。

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 核心执行。版本检查未通过前 NEVER 进入以下任一执行步骤。

### 步骤 1：任务接收与校验
1. 读取 tri-mm 转交任务，校验 `L2=I15` 且媒体类型=PPT
2. 识别场景（汇报/教学/路演/发布会）
3. 声明自检句

### 步骤 2：阶段一 · 全网素材采集
1. WebSearch/WebFetch 检索文字与图表数据；ImageGen 生成主题配图
2. 整理 `materials.md` + 产出 `materials.json`
3. 落盘 `.tribro/multimedia/ppt/<命名>/`

### 步骤 3：审计门① · 素材审计
1. 呈现素材库，请确认/补充/剔除
2. 通过 → 步骤 4；否则修订回本步

### 步骤 4：阶段二 · 大纲 + 动效设计
1. 逐维度设计，素材映射每页
2. 产出 `design.md` + `design.json`
3. 落盘 `.tribro/multimedia/ppt/<命名>/`

### 步骤 5：审计门② · 设计审计（可多轮）
1. 呈现 design.md（大纲 + 动效），请确认/提修改
2. 通过 → 步骤 6；否则修订回本步

### 步骤 6：阶段三 · 生成与落盘
1. 运行 `scripts/build_pptx.py` 生成 PPTX
2. 落盘 `.tribro/multimedia/ppt/<命名>/`，返回可访问路径
3. 记录设计参数与素材来源

### 步骤 7：核对与交付
1. 逐项核对 `任务要点` 覆盖（页数/格式/配色/动效）
2. 落盘 `result.md`
3. 返回 tri-mm 汇总

## 交付产物机制

| 产物 | 说明 | 落盘位置 |
|---|---|---|
| materials.md / materials.json | 全网素材库（含来源） | `.tribro/multimedia/ppt/<命名>/` |
| design.md / design.json | 大纲 + 逐页动效方案 | `.tribro/multimedia/ppt/<命名>/` |
| 演示文稿文件 | PPTX（必要时 PDF） | 工作区（可访问路径） |
| result.md | 产物路径 + 参数 + 核对 | `.tribro/multimedia/ppt/<命名>/` |

## 质量标准

| 维度 | 标准 | 验证方式 |
|---|---|---|
| 素材完整 | 三类素材齐全且标注来源 | materials.md 无空类 |
| 双门到位 | 素材审计 + 设计审计均通过 | 两次确认记录存在 |
| 方案完整 | 设计 8 维 + 每页大纲 + 动效填充 | design.md 无空维度 |
| 产物可访问 | PPTX 落盘 | 路径可开 |
| 参数可复现 | 设计参数 + 素材来源完整 | 可重生成 |
| 格式合规 | 符合 `D4_输出期望` | 格式一致 |
| 版权安全 | 外采图片均可商用或改生成 | 来源可追溯 |
| 任务要点覆盖 | 满足全部条目 | 逐项核对 |

## 落盘规则

- 快照由 tri-intent 已落盘 `.tribro/snapshots/`（本 skill 只读，不重复产出）。
- 本子SKILL 链路文档落盘 `.tribro/multimedia/ppt/<命名>/`（materials/design/result）。
- 演示文稿产物落盘 `.tribro/multimedia/ppt/<命名>/` 并返回可访问路径。
- **NEVER 在生成物目录生成 `LICENSE` 或 `.gitignore`**——许可证仅由本 SKILL.md frontmatter `license: MIT` 声明。

## 目录结构

```
tri-mm/children/tri-ppt/
├── SKILL.md                       # 主入口：全流程流水线 + 双审计门 + python-pptx 生成
├── README.md                     # 特性/目录结构/安装/使用/设计原则
├── CHANGELOG.md                  # 版本变更历史（Keep a Changelog + SemVer）
├── scripts/
│   ├── build_pptx.py             # 确定性 PPTX 生成器（python-pptx）★新增
│   └── check_update.py           # 版本门脚本（与 tri-intent 同源）
├── references/
│   ├── materials-template.md     # 素材库模板 + materials.json schema ★新增
│   └── design-template.md        # 大纲+动效设计模板 + design.json schema + 动效目录表 ★新增
└── tests/
    └── tri-ppt-full-testcases.md # 全场景测试用例
```
