---
name: 多媒体生成路由编排
slug: tri-mm
version: 1.5.0
displayName: 多媒体生成路由编排
description: 多媒体生成下游路由编排 skill。读取 tri-intent 快照 §三，处理 I15（多媒体生成）意图，识别媒体大类（图片/音频/视频/PPT）并拍发至对应子SKILL（tri-image/tri-audio/tri-video/tri-ppt）执行；音乐创作委派 tri-music。每个子SKILL 先产出多维度设计方案交用户确认后再生成。当 tri-intent 快照下游路由建议指向本 skill 时激活。支持独立安装，含上游依赖检测两态逻辑（标准模式/引导安装）。
summary: I15 多媒体路由编排器，媒体类型识别后拍发 4 个子SKILL，子SKILL 各自做多维设计+确认门+生成；音乐委派 tri-music。
tags: [multimedia, router, orchestrator, design-plan, image, audio, video, ppt]
license: MIT
---

# 多媒体生成路由编排（下游路由 · I15）

> 本 skill 是 tri-intent 的下游执行 skill，依据快照 `snapshot.md` §三 结构化结论直接执行，不再重新识别意图。
> 用户心智：把 AI 当"多媒体制片人"——你给一句需求，它先判断要做图片/音频/视频/PPT，再交给对应专家子 SKILL 做专业设计，设计稿给你确认后才动手生成。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级；升级成功后继续，升级通道不可用则标注 D 态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：收到 tri-intent 快照且 `下游路由建议` 指向本 skill，MUST 先读取快照 §三，校验 `intent.L2_核心意图` = I15，NEVER 跳过校验直接拍发。若 L2 越界 → 停止并回退 tri-intent 重新路由。独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式。
2. **媒体类型识别（核心路由）**：MUST 先识别媒体大类（图片/音频/视频/PPT）；音乐创作语义 MUST 委派 tri-music。识别依据 `D4_输出期望` + `任务要点` + 用户原始请求关键词（见 §媒体类型识别与子SKILL路由）。NEVER 跳过类型识别直接调用任意子SKILL。
3. **拍发即转交，不自行生成**：MUST 将媒体任务（快照 §三 + 媒体类型标注）转交对应子SKILL，本 skill 不再自行构造生成参数或直接调用生成工具——专业设计与生成由子SKILL 负责。
4. **确认门编排**：MUST 要求子SKILL 先产出多维度 `design.md` 设计方案交用户确认，NEVER 允许子SKILL 在用户未确认前生成。用户确认 → 子SKILL 执行；修改 → 回到设计；取消 → 终止。
5. **子SKILL 可用性校验**：拍发前 MUST 确认目标子SKILL 目录存在（`children/tri-<type>/SKILL.md`）；缺失则提示该子SKILL 随 tri-mm 包分发、需确保目录完整。
6. **汇总与自检句**：作答前声明「本次意图=I15，已读取快照，媒体类型=<类型>，拍发子SKILL=<tri-xxx>，确认门=<待确认/已确认>」；与快照冲突 MUST 停止并纠正。

## 触发时机

- tri-intent 产出的快照中 `下游路由建议` 指向本 skill
- 意图编码范围：I15 多媒体生成

## 上游依赖检测（独立使用时）

> 本 skill 可独立安装。激活时 MUST 检测外部 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟） | 读取快照 §三，按工作流推进（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | MUST 提示用户「本次请求尚未经意图识别」，引导先经 tri-intent 产出快照；NEVER 按空上下文静默执行 |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |

> 本 skill 不支持降级模式——模式 B 为硬性阻断，MUST 安装 tri-intent 后方可使用。

**模式 B 提示语**：
> 本 skill 依赖 tri-intent 进行意图识别与输入校验。当前未检测到 tri-intent。
> 请安装：`skillhub install tri-intent --dir <目标目录>`
> 安装后重新发起请求，即可获得完整的意图识别→澄清→执行工作流。

## 输入契约

读取 `.tribro/snapshots/<命名>.md` 的 §三 结构化结论区：

| 字段 | 用途 |
|---|---|
| `intent.L2_核心意图` | 必须为 I15，否则不应激活本 skill |
| `dimensions.D1_任务领域` | 多媒体类型与风格语境 |
| `dimensions.D2_输入形态` | 是否有参考图/素材/脚本 |
| `dimensions.D4_输出期望` | 图片/音频/视频/PPT/音乐 |
| `任务要点` | 产物须满足的关键要求 |
| `交付预期` | 用户期望的最终交付物 |

> 若快照 `澄清门状态=待澄清`，不应激活。

## 职责边界

- **本 skill 负责**：I15 意图下的媒体类型识别、子SKILL 路由拍发、设计方案确认门编排、产物汇总核对
- **不负责**：意图识别（由 tri-intent）、纯文本成果物（由 tri-content）、编码开发（由 tri-coding）
- **专业设计与生成**：由子SKILL 负责——图片（tri-image）/ 非音乐音频（tri-audio）/ 视频（tri-video）/ PPT（tri-ppt）/ 音乐（tri-music）
- **对称检测**：子SKILL 内置上游依赖检测（编排模式/引导安装），与 tri-mm 构成双向校验
- **不触发场景（Not-Trigger）**：本 skill 不接手「图片/非音乐音频/视频/PPT/音乐的实际生成」（由对应子SKILL tri-image / tri-audio / tri-video / tri-ppt / tri-music 承接）；不接手「文本/技术内容生成」（属 tri-content / tri-coding）；不接手「识别用户意图」（由 tri-intent / 自身快照驱动）。

## 媒体类型识别与子SKILL路由

> 识别媒体大类 → 拍发对应子SKILL；音乐为独立委派分支。

| 媒体大类 | 识别信号（关键词/输出期望） | 拍发子SKILL | 子SKILL 职责 |
|----------|----------------------------|-------------|--------------|
| 图片 | 图片/插画/海报/图标/Logo/SVG/图表/流程图 | `children/tri-image/` | 位图/矢量图/图表 9 维设计 + 生成 |
| 音频（非音乐） | 配音/旁白/音效/配乐/BGM/朗读 | `children/tri-audio/` | 配音/音效/配乐 8 维设计 + 生成 |
| 视频 | 视频/短片/分镜/宣传片/口播 | `children/tri-video/` | 10 维分镜头设计 + 生成（协同 tri-audio/tri-music） |
| PPT | PPT/幻灯片/演示/汇报/路演 | `children/tri-ppt/` | 8 维大纲设计 + 生成 |
| 音乐 | 写歌/作词/AI音乐/海绵音乐/Suno/汽水音乐/抖音神曲 | `tri-music`（委派） | 歌曲创作全案（见 §子意图委派） |

> 音频与音乐的边界：含"歌曲/歌词/AI 音乐/具体音乐平台工具"语义 → 音乐 → tri-music；纯"配音/音效/配乐" → 音频 → tri-audio。

## 子意图委派（I15.music → tri-music）

> 音乐创作（歌曲/歌词/AI 音乐指令）是 I15 下的独立子分支，由专门的 tri-music 处理，本 skill 及 tri-audio 均不生成歌词或音乐工具指令。

- **委派条件**：快照 §三 `任务要点` 或用户原始请求含音乐创作语义（写歌/作词/作曲/AI 音乐/海绵音乐/Suno/汽水音乐/抖音神曲/国风音乐/DJ 改编 等关键词）。
- **委派动作**：本 skill MUST 将工作流移交给 tri-music——tri-music 复用同一份 tri-intent 快照（L2 = I15，L3 = I15.music）按 `tri-music/templates/hook-formula.md` 等契约推进（该模板位于 tri-music 包内，不在本包 children/ 下）。
- **对称检测**：tri-music 侧已内置上游依赖检测（tri-intent 快照模式 / 引导安装 / 降级模式），与 tri-mm 构成双向校验。若 tri-music 未安装，委派时提示 `skillhub install tri-music --dir <目标目录>`。
- **职责边界**：音乐全案（歌词 + AI 工具指令 + 音色定位 + 15 秒分镜 + 多平台发布矩阵）归 tri-music；本 skill 及 tri-audio 仅负责非音乐的多媒体。


## 核心能力方法论（路由编排 · 可扩展）

> 本 skill 的核心能力是**媒体类型识别与一跳委派**，而非自己产出媒体。

1. **类型识别**：据任务要点判定媒体大类（图片 / 音频 / 视频 / PPT），并下钻到具体产出形态
2. **子 SKILL 路由**：按大类委派对应 `children/` 子 SKILL（tri-image / tri-audio / tri-video / tri-ppt），一跳直达
3. **子意图二跳**：音乐创作子类（写歌 / 作词 / AI 音乐）由本 skill 转交 `tri-music`——保持「一个 L2 意图（I15）= 一个一跳下游」的 MECE 约束

**识别的唯一主键是「期望产出形态」**，不是素材类型：同一张图作为输入，产出修图走 tri-image、产出视频走 tri-video。

### 可扩展性

1. **新增媒体大类**：在 `children/` 建子 SKILL，并在 §子意图委派 表追加一行（大类 / 子 SKILL / 触发语义）——路由逻辑零改动
2. **新增子意图二跳**：在 §子意图委派 追加一行并声明二跳关系，MUST 在 `family-spec.md` §五 登记
3. **替换子 SKILL 实现**：只要子 SKILL 的输入输出契约不变，可整体替换，本 skill 不感知其内部方法论

## 核心能力方法论（路由编排 · 可扩展）

> 本 skill 的核心能力是**媒体类型识别与一跳委派**，而非自己产出媒体。

1. **类型识别**：据任务要点判定媒体大类（图片 / 音频 / 视频 / PPT），并下钻到具体产出形态
2. **子 SKILL 路由**：按大类委派对应 `children/` 子 SKILL（tri-image / tri-audio / tri-video / tri-ppt），一跳直达
3. **子意图二跳**：音乐创作子类（写歌 / 作词 / AI 音乐）由本 skill 转交 `tri-music`——保持「一个 L2 意图（I15）= 一个一跳下游」的 MECE 约束

**识别的唯一主键是「期望产出形态」**，不是素材类型：同一张图作为输入，产出修图走 tri-image、产出视频走 tri-video。

### 可扩展性

1. **新增媒体大类**：在 `children/` 建子 SKILL，并在 §子意图委派 表追加一行（大类 / 子 SKILL / 触发语义）——路由逻辑零改动
2. **新增子意图二跳**：在 §子意图委派 追加一行并声明二跳关系，MUST 在 `family-spec.md` §五 登记
3. **替换子 SKILL 实现**：只要子 SKILL 的输入输出契约不变，可整体替换，本 skill 不感知其内部方法论

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：`references/version-check-spec.md`。**可执行实现（single source of truth for logic）**：本 skill 自带 `scripts/check_update.py`（与 tri-intent 同源一致，按 `--slug` 自动适配）。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。修订规则只改真源一处，脚本与真源保持同步。

**执行方式（MUST）**

1. 任一执行入口启动后、核心执行前，运行脚本并取 JSON：
   ```bash
   python scripts/check_update.py --slug tri-mm --json
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
8. **阻断条件 P1–P4** 与四处版本同步点见真源；发布前 MUST 通过家族版本同步校验。

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 核心执行。版本检查未通过前 NEVER 进入以下任一执行步骤。

> 路由编排型工作流：识别 → 拍发 → 子SKILL 内设计+确认+生成 → 汇总。

### 步骤 1：快照校验与媒体类型识别

1. 读取快照 §三，校验 `intent.L2_核心意图` = I15
   - L2 越界 → 停止，回退 tri-intent 重新路由
2. 提取生成语境要素（D1/D2/D4/任务要点/交付预期）
3. 识别媒体大类（图片/音频/视频/PPT/音乐），参考 §媒体类型识别与子SKILL路由
4. 声明自检句：「本次意图=I15，已读取快照，媒体类型=<类型>，拍发子SKILL=<tri-xxx>」

### 步骤 2：拍发子SKILL（转交媒体任务）

1. 确认目标子SKILL 目录存在（`children/tri-<type>/SKILL.md` 或 `tri-music/`）；缺失则提示补全
2. 将媒体任务（快照 §三 + 媒体类型标注）转交对应子SKILL
3. 音乐 → 走 §子意图委派 转 tri-music

### 步骤 3：子SKILL 内「设计 → 确认 → 生成」（由子SKILL 执行）

> 此阶段由对应子SKILL 主导，tri-mm 负责确认门编排监督：

1. 子SKILL 完成多维度分析，产出 `design.md` 设计方案
2. **确认门**：将 design.md 呈现用户确认
   - 确认 → 子SKILL 生成产物
   - 修改 → 修订 design.md 回到确认
   - 取消 → 终止
3. 子SKILL 生成产物统一落盘 `.tribro/multimedia/<子类>/<命名>/`，落盘各自 `result.md`

### 步骤 4：汇总与核对

1. 收集子SKILL 返回的产物路径与 result.md
2. 逐项核对快照 `任务要点` 覆盖（跨子SKILL 协同项如视频旁白/BGM 一并核对）
3. 落盘 tri-mm 编排结果 `.tribro/multimedia/<命名>/result.md`
4. 返回用户：产物路径 + 设计方案摘要

## 交付产物

> tri-mm 作为编排器，本身不产出多媒体文件；其交付物为「编排结果 + 各子SKILL 产物汇总」。

### 一、产物清单

| 产物 | 说明 | 落盘位置 |
|---|---|---|
| 多媒体文件 | 由各子SKILL 生成（图片/音频/视频/PPT） | 工作区（可访问路径） |
| design.md | 各子SKILL 设计方案 | 子SKILL 各自 `.tribro/multimedia/<type>/<命名>/` |
| result.md | 子SKILL 执行结果 + tri-mm 编排结果 | 子SKILL 目录 / `.tribro/multimedia/<命名>/result.md` |

### 二、覆盖完整性

- 产物 MUST 满足 `任务要点` 中的关键要求
- 产物格式 MUST 符合 `D4_输出期望`
- 确认门 MUST 已通过（用户确认记录存在）方可生成

## 质量标准

| 维度 | 标准 | 验证方式 |
|---|---|---|
| 类型识别准确 | 媒体大类与子SKILL 一一对应 | 路由表匹配 |
| 拍发正确 | 任务转交对应子SKILL | 子SKILL 激活 |
| 确认门到位 | 生成前用户已确认 design.md | 确认记录存在 |
| 产物可访问 | 文件已落盘 | 路径可打开 |
| 协同正确 | 视频旁白→tri-audio、BGM→tri-music | 不越界 |
| 任务要点覆盖 | 满足任务要点全部条目 | 逐项核对 |

## 落盘规则

> 与 tri-intent（`.tribro/snapshots/`）、tri-action（`.tribro/actions/`）、tri-loop（`.tribro/loops/`）、tri-music（`.tribro/music/`）保持一致。

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- **tri-mm 编排结果**落盘于 `.tribro/multimedia/<命名>/result.md`
- **子SKILL 链路文档**各自落盘：
  - `.tribro/multimedia/image/<命名>/`（tri-image）
  - `.tribro/multimedia/audio/<命名>/`（tri-audio）
  - `.tribro/multimedia/video/<命名>/`（tri-video）
  - `.tribro/multimedia/ppt/<命名>/`（tri-ppt）
- **多媒体产物**（图片/音频/视频/PPT）落盘于工作区并返回可访问路径——这些是实际产物，不是 tri 链路文档；`.tribro/` 不存在时 MUST 先创建，交付时在 `.tribro/multimedia/<子类>/<命名>/` 落 `delivery-manifest.md` 记录交付物路径清单，保证产物可追溯

## 目录结构

> `children/` 下每个子SKILL 都是**自带 README/CHANGELOG/tests 的独立子包**，可随 tri-mm 整包分发，也可单独审计与版本演进。

```
tri-mm/
├── SKILL.md                     主入口：I15 路由编排 + 媒体类型识别 + 确认门编排
├── README.md
├── CHANGELOG.md
├── tests/
│   └── tri-mm-full-testcases.md 全场景测试用例
├── references/                  # 跨媒体通用参考（非流程逻辑）
│   ├── prompt-structure.md       # 跨媒体提示词结构：图像六段 / 视频八段 + 三锚复用 + 迭代纪律
│   └── version-check-spec.md       # 版本门细则（STUB 指针，NEVER 内联）
└── children/                    子SKILL（多维设计 + 确认门 + 生成）
    ├── tri-image/               图片（位图/矢量图/图表）
    │   ├── SKILL.md             9 维设计 + 生成
    │   ├── README.md
    │   ├── CHANGELOG.md
    │   └── tests/tri-image-full-testcases.md
    ├── tri-audio/               音频（配音/音效/配乐，非音乐）
    │   ├── SKILL.md             8 维设计 + 生成
    │   ├── README.md
    │   ├── CHANGELOG.md
    │   └── tests/tri-audio-full-testcases.md
    ├── tri-video/               视频（分镜头设计）
    │   ├── SKILL.md             10 维分镜头设计 + 生成
    │   ├── README.md
    │   ├── CHANGELOG.md
    │   └── tests/tri-video-full-testcases.md
    └── tri-ppt/                 演示文稿（大纲设计）
        ├── SKILL.md             8 维大纲设计 + 生成
        ├── README.md
        ├── CHANGELOG.md
        └── tests/tri-ppt-full-testcases.md
```

> 跨包引用：音乐分支的 6 维 Hook 公式模板位于 **tri-music 包**（`tri-music/templates/hook-formula.md`），不随 tri-mm 分发。
