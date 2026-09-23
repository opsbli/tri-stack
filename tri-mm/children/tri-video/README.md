# tri-video（tri-mm 视频类子SKILL）

tri-mm 在 I15 多媒体生成下派发的**视频类专家子 SKILL**。接收 tri-mm 转交的媒体任务，对视频意图做 10 维详细设计（时长/分镜头/运镜/转场/画面/旁白/字幕/节奏/画幅/平台），先产出分镜头 `design.md` 交用户确认，确认后再生成视频。旁白协同 tri-audio、BGM 协同 tri-music。

支持**双制作路线**：AI 生成工具路线（默认）与代码渲染精确路线（程序化逐帧渲染，八阶段流水线 + 镜头配方卡体系 + 判例式审美准则 + BGM 卡点 + 声音设计 + 独立终检）。

## 特性

- **10 维专业设计**：含分镜头脚本、运镜、转场、字幕、平台适配（双路线通用）
- **双路线判定**：按输入信号选择 AI 生成或代码渲染路线，均可行时对比交用户选择
- **分镜头确认门**：先出分镜头表再生成，节奏/字幕一次定准
- **代码渲染方法论知识包**（`references/`，5 文件）：
  - `production-pipeline.md` — 八阶段制作流水线 + 三推进模式 + 品牌→动效参数预设表
  - `aesthetic-rules.md` — 判例式审美准则 26 条（节奏 R / 质感 Q / 声音 S / 文案 C / 流程 P）
  - `shot-card-system.md` — 镜头配方卡 schema / 十类分类学 / 三读法则 / 能量弧段位模板
  - `capture-and-camera.md` — 素材采集三件套 + 2.5D 页面相机 + 高清栅格化技法
  - `beat-sync-sound.md` — BGM 卡点方法论（网格拟合/鼓点分类/渲后回测）+ 声音设计 + 音画对齐
- **确定性算法下沉**：`scripts/beat_grid_fit.py` 节拍网格拟合与半倍/双倍歧义裁决
- **子任务协同**：旁白→tri-audio，BGM→tri-music，不越界；代码渲染路线的节奏分析/钉帧/验收归本 skill
- **参数可复现**：分镜头 + 生成/渲染参数完整记录；确定性渲染铁律（固定种子、逐帧可复现）

## 目录结构

```
tri-video/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── references/
│   ├── production-pipeline.md
│   ├── aesthetic-rules.md
│   ├── shot-card-system.md
│   ├── capture-and-camera.md
│   ├── beat-sync-sound.md
│   └── version-check-spec.md
├── scripts/
│   ├── beat_grid_fit.py
│   └── check_update.py
└── tests/
    └── tri-video-full-testcases.md
```

## 安装

随 tri-mm 包分发，置于 `tri-mm/children/tri-video/`。独立安装需先装 tri-mm。

## 使用

```
tri-mm 识别媒体类型=视频
      → 转交本子SKILL
      → 制作路线判定（AI 生成 / 代码渲染）
      → 10 维设计 → 分镜头 design.md
      → 用户确认（确认门）
      → AI 生成路线：协同 tri-audio/tri-music → 生成落盘
      → 代码渲染路线：八阶段流水线（采集→逐镜头实现→声音设计）→ 独立终检 → 双版本交付
      → result.md 审计
```

## 设计原则

- **先设计后生成**：10 维 + 分镜头表显式填充
- **确认门不可跳**：未确认不调用生成工具、不开始渲染
- **协同不越界**：音频生成归 tri-audio/tri-music；音频设计与验收归代码渲染路线
- **验收贯穿全程**：代码渲染路线每镜头静帧验收 + 交付前独立终检，不把首检交给用户
