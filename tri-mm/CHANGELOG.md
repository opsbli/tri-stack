# Changelog

本文件记录 tri-mm skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。


## [1.5.0] - 2026-09-22

### 新增

- **子SKILL tri-video 双制作路线增强**（`children/tri-video`，随包分发，子包版本维持 1.1.1 至发布）：
  - 新增「制作路线判定」：AI 生成工具路线（默认）与代码渲染精确路线（程序化逐帧渲染）双路线，判定结果写入 design.md 与自检句；双路线均可行时对比交用户选择
  - 子包新增 `references/` 知识包 6 文件：production-pipeline.md（八阶段流水线+三推进模式+动效参数预设）、aesthetic-rules.md（判例式审美准则 26 条 R/Q/S/C/P）、shot-card-system.md（镜头配方卡 schema/十类/三读法则/能量弧）、capture-and-camera.md（采集三件套+2.5D 页面相机+高清栅格化）、beat-sync-sound.md（BGM 卡点+声音设计+音画对齐）、version-check-spec.md（版本门瘦指针）
  - 子包新增 `scripts/`：beat_grid_fit.py（节拍网格拟合确定性算法）、check_update.py（版本门确定性入口，与家族同源）
  - 子包 tests 增补至 28 用例（路线判定/知识包装载/准则过检/独立终检/卡点/独立运行 J 组）
  - 与父包划界不变：tri-mm 仍只做路由编排与媒体类型识别，专业设计与生成归子包；BGM 曲目生成归 tri-music、旁白归 tri-audio，代码渲染路线的节奏分析/钉帧/验收归 tri-video
- **新增** `references/prompt-structure.md`（增强项 E8）：跨媒体生成提示词结构骨架（图像六段 / 视频八段，含运动与时长节奏强制段）、一致性锚三块复用规则、迭代纪律（单变量 / 先补段后调词 / 可复现参数落盘）、反模式清单。与子包划界：场景级提示词构建与落盘归 `children/tri-image`、`children/tri-video`，冲突以子包为准。
- `references/` 目录首次建立。

## [1.4.4] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手各类媒体实际生成（由子SKILL tri-image/tri-audio/tri-video/tri-ppt/tri-music 承接）、文本/技术内容生成（tri-content / tri-coding）与意图识别（tri-intent），强化「编排路由、不亲自生成」边界。

## [1.4.3] - 2026-09-18

### 变更

- **版本联动 bump**：本次未改动 tri-mm 自身的路由/编排逻辑，仅因随包分发的子 SKILL `tri-image` 升级至 2.0.0（七场景全栈生图引擎：封面图/结构图/信息图/文章配图/社媒卡片/幻灯片/知识漫画，三轨管线 Track-V/T1/T2，12 provider 引擎，纯 Python 零依赖工具）而提升父包版本，避免与 skillhub 上已发布的 1.4.2 同版本重发（409）并真实分发新内容。
- frontmatter version `1.4.2` → `1.4.3`

## [1.4.2] - 2026-09-02

### 修复
- SKILL.md `name`/`displayName` 去除全角括号 slug 后缀；4 个 children SKILL.md 同步去除。
- `版本检查` 引用从 `version-gate.md` 统一回指 `version-check-spec.md`；产物落盘目录收敛为 `.tribro/multimedia/`。
- frontmatter version `1.4.1` -> `1.4.2`

## [1.4.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源 `tri-intent/references/version-gate.md`，消除各 skill 内的重复表述
- frontmatter version `1.4.0` → `1.4.1`

## [1.4.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.3.1` → `1.4.0`

## [1.3.1] - 2026-08-02

### 修复

- **跨包路径引用错误**：§子意图委派 中 `templates/hook-formula.md` 修正为 `tri-music/templates/hook-formula.md`——该模板位于 tri-music 包内，本包 `templates/` 目录并不存在，原路径会导致读取失败

### 变更

- **目录结构树补全**：`## 目录结构` 展开 `children/` 四个子包（tri-image/tri-audio/tri-video/tri-ppt），明确各子包自带 README/CHANGELOG/tests，可独立审计与版本演进；并补注跨包引用说明
- **测试用例扩充**：`tests/tri-mm-full-testcases.md` 从 14 例扩至 52 例，新增「媒体类型路由决策」（14 例，含音频/音乐边界与复合请求拆分）、「音乐委派路径」（7 例）、「质量标准六维」（12 例，每维度含正例+反例）、「落盘与子包结构」（5 例）四组

## [1.3.0] - 2026-08-02

### 新增（架构升级：路由编排 + 子SKILL）

- **定位升级为「多媒体生成路由编排 skill」**：从「直接生成」改为「媒体类型识别 → 子SKILL 路由拍发 → 确认门编排 → 产物汇总」
- **媒体类型识别与子SKILL 路由**：识别图片/音频（非音乐）/视频/PPT 四大类，拍发至 4 个新建子SKILL（`children/tri-image` `children/tri-audio` `children/tri-video` `children/tri-ppt`）；音乐创作仍委派 tri-music
- **设计方案确认门**：每个子SKILL MUST 先产出多维度 `design.md` 设计方案交用户确认，确认后才生成，避免反复返工
- **4 个子SKILL（均 v1.0.0）**：
  - tri-image：位图/矢量图/图表，9 维设计（主题/风格/构图/色彩/光影/质感/画幅/参考/负向）
  - tri-audio：配音/音效/配乐，8 维设计（脚本/音色/语速/情绪/时长/BGM音效/技术/字幕）；音乐语义回退 tri-music
  - tri-video：10 维分镜头设计（时长/分镜/运镜/转场/画面/旁白/字幕/节奏/画幅/平台），协同 tri-audio/tri-music
  - tri-ppt：8 维大纲设计（主题受众/结构页数/大纲/版式/配色字体/图表/动画/格式）
- **落盘规则扩展**：子SKILL 链路文档分别落盘 `.tribro/multimedia/{image,audio,video,ppt}/<命名>/`

### 变更

- 强制执行契约从「直接构造生成参数」改为「媒体类型识别 + 拍发 + 确认门编排」
- 处理流程从单链路生成改为「识别 → 拍发 → 子SKILL 内 设计/确认/生成 → 汇总」
- 职责边界明确：tri-mm 只路由编排，专业设计与生成由子SKILL 负责

## [1.2.0] - 2026-07-30

### 新增

- **`.tribro/multimedia/` 链路文档落盘**：与 tri-intent（`.tribro/snapshots/`）、tri-action（`.tribro/actions/`）、tri-loop（`.tribro/loops/`）保持一致
- **执行结果落盘**：tri-mm 执行结果落盘于 `.tribro/multimedia/<命名>/result.md`，含产物路径 + 生成参数 + 覆盖核对 + 引用
- **落盘规则 section 增强**：明确区分 tri 链路文档（result.md）与多媒体产物（工作区），路径分离不混淆

## [1.1.0] - 2026-07-26

### 新增

- **上游依赖检测两态逻辑**：支持快照模式 / 引导安装两种执行模式
  - A · 快照模式：检测到 `.tribro/snapshots/` 快照或 `tri-intent/` 目录时，按标准工作流推进
  - B · 引导安装：未检测到外部依赖时，向用户提示并引导安装 `skillhub install tri-intent`
- 明确本 skill 不支持降级模式——模式 B 为硬性阻断，MUST 安装 tri-intent 后方可使用

### 变更

- 上游依赖检测从隐式依赖改为显式两态判定，独立安装场景下未检测到依赖时硬性阻断
- 强制执行契约明确独立使用时 MUST 先走上游依赖检测判定模式

## [1.0.0] - 2026-07-24

### 新增

- 初始版本：多媒体生成下游执行 skill，处理 I15（多媒体生成）意图，产出图片/图表/音视频/PPT 等非文本成果物
- 产物类型识别方法论：5 种产物类型（位图/矢量图/图表/音视频/演示文稿）据识别信号映射到对应生成能力
- 生成参数构造方法论：按产物类型构造完整生成参数（必备参数 + 可选参数），确保可复现
  - 参数构造原则：从 `任务要点` 提取硬约束，从 `D4_输出期望` 确定产物格式，若有参考素材作为图生图/参考输入
- 能力匹配调用：按产物类型匹配生成能力，无匹配能力时显式说明并回退建议替代方案
- 任务要点覆盖核对：逐项核对清单，能力限制无法满足的条目显式标注原因
- 产物落盘与路径返回：生成产物 MUST 落盘至工作区并返回可访问路径，生成参数记录随产物交付
- 质量标准六维：产物可访问 / 参数可复现 / 格式合规 / 约束满足 / 能力匹配 / 任务要点覆盖
- 轻量无审批门：单轮生成即交付，无审批门、无链路文档，多媒体文件 + 生成参数记录即交付物
