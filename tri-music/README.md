---
name: tri-music
slug: tri-music
version: 2.2.1
displayName: 爆款音乐创作（tri-music）
description: 多平台爆款音乐创作下游执行 skill。读取 tri-intent 快照 §三，处理 I15.music（音乐/多媒体创作）意图，覆盖抖音/汽水音乐/网易云/QQ 音乐/酷狗/酷我五大平台发行 + 海绵音乐/Suno/Udio/Melo/音潮五套 AI 工具适配。支持独立安装，含上游依赖检测三态逻辑（快照模式/引导安装/降级模式）。
summary: 抖音+汽水音乐+网易云+QQ 音乐+酷狗+酷我的爆款音乐创作 skill，含 6 维 Hook 公式、微情绪意象库、反 AI 罐头基底、多 AI 工具适配与发行 SOP。
tags: [music, hit-music, hook-engineering, multi-platform, ai-music, douyin, qishui, netease-cloud, qq-music, kugou, kuwo, suno, udio, haimian, melo, yinchao, lyrics]
license: MIT
---

# 爆款音乐创作（下游路由 · I15.music）

> 本 skill 是 tri-intent 的下游执行 skill，依据快照 `snapshot.md` §三 结构化结论直接执行多平台爆款音乐创作。
> 用户心智：把 AI 当音乐制作人，期望拿到可在抖音/汽水音乐等平台引爆的完整音乐作品（含歌词、Prompt 模板、发行策略）。

## 强制执行契约（Execution Contract · 最高优先级）

1. **强制前置**：收到 tri-intent 快照且 `下游路由建议` 指向本 skill，MUST 先读取快照 §三（含 `核心文化元素/主题`、`核心情绪基调`、`目标受众`、`目标平台` 四个核心字段），再按工作流串行推进，NEVER 跳过直接产出歌词。
2. **子意图路由 + 输入依赖校验**：I15.music 属委托执行类文本+多媒体复合意图，MUST 校验核心文化元素/主题、情绪基调、目标受众、目标平台四个必填字段。
3. **6 维 Hook 公式强制应用**：所有歌词创作 MUST 经过 `templates/hook-formula.md` 校验，6 个维度（旋律/节奏/歌词/编曲/结构/情绪）至少覆盖 5 个维度。
4. **微情绪意象库强制引用**：歌词创作 MUST 优先从 `templates/lyrics-micros-emotion.md` 选取具体意象，NEVER 使用"孤独/爱/梦想"等抽象词汇作为副歌核心。
5. **多 AI 工具适配层（可扩展）**：根据用户指定的 AI 工具，从 `prompts/` 目录加载对应提示词模板。**默认启用** `prompts/anti-can.md`（反 AI 罐头）作为所有工具的通用基底。
6. **多平台发行策略强制套用**：发行前 MUST 通过 `templates/platform-matrix.md` 校验 5 平台差异化策略，并参考 `templates/release-sop.md` 执行 5 阶段发行 SOP。
7. **最小化原则（门禁规则）**：执行范围以 `任务要点` 为准，不擅自扩大（如不擅自修改已确定的主题/曲风/平台）。若发现需扩大，NEVER 默默操作，必须向用户说明并确认。
8. **反 AI 罐头检查清单（硬性）**：歌词/曲风/编曲/混音/封面/标题/发行每个环节 MUST 通过 `checklists/anti-can-music.md` 校验。

## 触发时机

- tri-intent 产出的快照中 `下游路由建议` 指向本 skill
- 意图编码范围：I15.music（音乐/多媒体创作子意图）

## 上游依赖检测（独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 快照模式** | `.tribro/snapshots/` 有快照 或 skills 目录有 `tri-intent/` | 读取快照 §三，按工作流推进（标准模式） |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户明确拒绝安装 | 从用户请求自构造等价输入，声明降级模式 |

**模式 B 提示语**：
> 本 skill 依赖 tri-intent 进行意图识别与输入校验。当前未检测到 tri-intent。
> 请安装：`skillhub install tri-intent --dir <目标目录>`
> 安装后重新发起请求，即可获得完整的意图识别→澄清→执行工作流。

**模式 C 降级声明**：
> 用户明确拒绝安装后，从用户请求自构造等价输入（核心文化元素/主题 + 情绪基调 + 目标受众 + 目标平台），声明「当前为降级模式，意图识别精度低于完整工作流」。

## 输入契约

读取 `.tribro/snapshots/<命名>.md` 的 §三 结构化结论区：

| 字段 | 用途 |
|---|---|
| `intent.L2_核心意图` | 必须为 I15.music，否则不应激活本 skill |
| `核心文化元素/主题` | 决定歌词意象与文化锚点 |
| `核心情绪基调` | 决定曲风与编曲走向 |
| `目标受众` | 决定发行平台优先级与歌词语态 |
| `目标平台` | 决定发行 SOP 起点（抖音/汽水/网易云/QQ 音乐/酷狗/酷我） |
| `任务要点` | 创作须覆盖的功能点（如"创作国风电音 + 副歌含 1 个具体意象"） |
| `交付预期` | 用户期望的最终交付物（如"完整歌词 + 海绵音乐 Prompt + 抖音发行清单"） |

> **模式 C 降级模式输入**：当用户拒绝安装 tri-intent 时（见 §上游依赖检测 模式 C），从用户原始请求自构造等价输入——核心文化元素/主题 + 情绪基调 + 目标受众 + 目标平台 + 任务要点，声明降级模式后按工作流推进。

## 职责边界

- **本 skill 负责**：依据快照结论，对 I15.music 意图产出多平台爆款音乐创作成果物（歌词 + AI 工具 Prompt + 发行 SOP + 反 AI 罐头自检）
- **不负责**：意图识别（由 tri-intent）、非音乐类多媒体（由 tri-mm 视频/动画等）、纯文本内容（由 tri-content）、商业包装（由其他 skill 协同）

## 核心能力（可扩展）

### 核心理念

> **没有 6 维 Hook 校验过的副歌，就不能进 AI 工具生成；没有反 AI 罐头基底提示词的 Prompt，就不能保证出片质量。**

音乐创作是文本创作 + 多媒体生成 + 多平台发行的复合任务。本 skill 通过 6 维 Hook 公式、微情绪意象库、反 AI 罐头基底、多 AI 工具适配与发行 SOP 五个核心方法论，差异化解决「AI 音乐容易撞稿、用户不会写 Prompt、不懂平台规则」三大痛点。

### 方法论概览

| 方法论 | 作用 | 文件 | 适用环节 |
|---|---|---|---|
| 6 维 Hook 公式 | 副歌记忆点设计（旋律/节奏/歌词/编曲/结构/情绪） | `templates/hook-formula.md` | 歌词创作后必须校验 |
| 微情绪意象库 | 副歌意象选词（含 6 大情绪场景） | `templates/lyrics-micros-emotion.md` | 歌词创作时强制引用 |
| 平台发行矩阵 | 5 平台差异化策略 | `templates/platform-matrix.md` | 发行前必须校验 |
| 5 阶段发行 SOP | 预热→首发→加投→维护→复盘 | `templates/release-sop.md` | 发行全程必须遵循 |
| 反 AI 罐头清单 | 8 维度防同质化自检 | `checklists/anti-can-music.md` | 创作/AI 生成/封面/标题各环节必检 |
| 多 AI 工具适配 | 海绵音乐/Suno/Udio/Melo/音潮差异化 Prompt | `prompts/*.md` | 创作时按用户指定工具加载 |

### 输入依赖校验细则

| 必填字段 | 来源 | 缺失处理 |
|---|---|---|
| 核心文化元素/主题 | 快照 D1_任务领域 | 缺失则回退 tri-intent clarify-gate |
| 核心情绪基调 | 快照 D4_输出期望 | 缺失则回退 tri-intent clarify-gate |
| 目标受众 | 快照 D1_任务领域 | 缺失则回退 tri-intent clarify-gate |
| 目标平台 | 快照 D4_输出期望 | 缺失则回退 tri-intent clarify-gate |
| AI 工具选择 | 用户指定 | 缺失则默认推荐海绵音乐 |

> **回退规则**：必填字段缺失时 MUST 回退 tri-intent 的 clarify-gate，NEVER 凭空生成主题或臆测平台。

### 可扩展性

> 新增方法论/AI 工具/平台无需修改核心工作流：

1. **新增 AI 工具 Prompt**：在 `prompts/` 目录创建 `<tool>.md`（遵循 `haimian.md` 格式），用户指定时自动加载
2. **新增平台发行策略**：在 `templates/platform-matrix.md` 追加平台行 + 在 `templates/release-sop.md` 追加阶段适配
3. **新增 Hook 维度**：在 `templates/hook-formula.md` 追加维度行 + 自检清单
4. **新增反 AI 罐头指令**：在 `prompts/anti-can.md` 追加指令段，所有 Prompt 自动追加

## 创作工作流（I15.music 委托执行链路）

```
tri-intent 快照 §三
        │
        ▼
  输入依赖校验（4 必填字段）
        │
     缺失 ──→ 回退 tri-intent clarify-gate
        │满足
        ▼
  歌词创作（含微情绪意象库）
        │
        ▼
  6 维 Hook 公式校验（templates/hook-formula.md）
        │
     <18 维 ──→ 返工歌词
        │≥18 维
        ▼
  AI 工具 Prompt 拼装（prompts/anti-can.md 基底 + prompts/<tool>.md）
        │
        ▼
  反 AI 罐头自检（checklists/anti-can-music.md · 8 维度）
        │
     不达标 ──→ 修正后重检
        │达标
        ▼
  平台发行策略套用（templates/platform-matrix.md + release-sop.md）
        │
        ▼
  交付（歌词 + Prompt + 发行清单 + 自检报告）
```

### 阶段速查表

| 阶段 | 关键动作 | 产出 |
|---|---|---|
| 1 | 读取快照 §三，校验 4 必填字段 | — |
| 2 | 歌词创作（参考微情绪意象库） | 歌词草稿 |
| 3 | 6 维 Hook 公式校验 | 自检结果（≥18 维优秀） |
| 4 | 拼装 AI 工具 Prompt | 完整 Prompt（已含反 AI 罐头基底） |
| 5 | 反 AI 罐头 8 维度自检 | 自检报告 |
| 6 | 平台发行策略套用 | 5 平台发行清单 + SOP 起点 |
| 7 | 交付完整音乐创作包 | 歌词 + Prompt + 发行清单 + 自检报告 |

## 交付产物

### 一、文件命名规范

沿用 tri-intent 快照命名：`<问题类型>_<日期>_<时间>_<会话ID>`

- 示例：`I15_music_20260226_143022_6a5c037d`

### 二、存放目录

```
.tribro/                    # 若不存在则先创建
├── snapshots/              tri-intent 产出（已存在）
│   └── <命名>.md
└── music/                  tri-music 链路文档
    └── <命名>/
        ├── lyrics.md         # 完整歌词（含 6 维 Hook 校验）
        ├── prompt.md         # AI 工具完整 Prompt（含反 AI 罐头基底）
        ├── release.md        # 5 平台发行清单 + SOP 起点
        └── selfcheck.md      # 反 AI 罐头自检报告
```

### 三、产物清单

| 产物 | 文件名 | 内容 |
|---|---|---|
| 完整歌词 | `lyrics.md` | 主歌/副歌/桥段 + 6 维 Hook 自检 |
| AI 工具 Prompt | `prompt.md` | 海绵音乐/Suno/Udio/Melo/音潮完整 Prompt |
| 发行清单 | `release.md` | 5 平台差异化策略 + 5 阶段 SOP 起点 |
| 自检报告 | `selfcheck.md` | 反 AI 罐头 8 维度自检结果 |

## 目录结构

```
tri-music/
├── SKILL.md                          # 主入口：爆款音乐创作工作流 + 核心方法论
├── README.md                         # 本文件：使用说明与扩展指南
├── CHANGELOG.md                      # 变更日志
├── tests/
│   └── tri-music-full-testcases.md   # 全场景全能力测试用例
├── templates/
│   ├── hook-formula.md               # 6 维 Hook 公式模板
│   ├── lyrics-micros-emotion.md      # 微情绪意象库
│   ├── platform-matrix.md            # 5 平台发行策略矩阵
│   └── release-sop.md                # 5 阶段发行 SOP
├── checklists/
│   └── anti-can-music.md             # 反 AI 罐头 8 维度自检清单
├── prompts/
│   ├── anti-can.md                   # 反 AI 罐头通用基底（必加）
│   ├── haimian.md                    # 海绵音乐 Prompt（中文为主）
│   ├── suno.md                       # Suno Prompt（英文为主）
│   ├── udio.md                       # Udio Prompt
│   ├── melo.md                       # Melo Prompt
│   └── yinchao.md                    # 音潮 Prompt
```

## 快速开始

### 场景一：抖音 + 海绵音乐（默认推荐）

1. 用户提供：核心文化元素/主题 + 情绪基调 + 目标受众 + 目标平台（抖音）
2. 读取 `templates/lyrics-micros-emotion.md` 选取意象
3. 按 6 维 Hook 公式（`templates/hook-formula.md`）创作歌词
4. 拼装 `prompts/anti-can.md` + `prompts/haimian.md` → 生成完整 Prompt
5. 执行 `checklists/anti-can-music.md` 自检
6. 套用 `templates/platform-matrix.md` 抖音策略 + `templates/release-sop.md` 5 阶段
7. 交付：歌词 + Prompt + 发行清单

### 场景二：全平台发行（5 平台同步）

1. 同场景一产出歌词 + Prompt
2. 套用 `templates/platform-matrix.md` 5 平台差异化策略
3. 套用 `templates/release-sop.md` 5 阶段 SOP（按平台优先级排序）
4. 交付：歌词 + Prompt + 5 平台发行清单 + 跨平台数据观察计划

### 场景三：AI 工具替换（Suno/Udio/Melo/音潮）

1. 同场景一/二产出歌词
2. 加载对应工具的 `prompts/<tool>.md`（如 `prompts/suno.md`）
3. 拼装 `prompts/anti-can.md` 基底 + 工具特定 Prompt
4. 交付：歌词 + 对应工具 Prompt

## 质量保证

| 维度 | 标准 | 校验方式 |
|---|---|---|
| Hook 命中维度 | ≥18 维（21 维满分） | `templates/hook-formula.md` 自检 |
| 反 AI 罐头 | 8 维度全过 | `checklists/anti-can-music.md` 自检 |
| 平台合规 | 5 平台差异化策略不冲突 | `templates/platform-matrix.md` 校验 |
| 发行 SOP | 5 阶段齐备 | `templates/release-sop.md` 校验 |
| 微情绪意象 | 副歌含 1 个具体意象 | `templates/lyrics-micros-emotion.md` 引用 |

## 版本信息

- 当前版本：2.1.1
- 上一版本：2.1.0
- 升级日期：2026-08-02
- 升级依据：v2.1.0 新增 `.tribro/music/` 链路文档落盘；v2.1.1 补齐 `## 质量标准` 三维、`tests/` 全量用例与目录结构对齐（详见 CHANGELOG.md）

## 关联资源

- 调研报告：《2025-2026 全网爆款音乐深度解析报告》—— 12 项优化建议的依据来源，结论已融入本 skill 各章节
- 版权合规：遵循本 skill「版权红线」要求，生成内容须原创、可合规发布
