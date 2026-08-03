# tri-video（tri-mm 视频类子SKILL）

tri-mm 在 I15 多媒体生成下派发的**视频类专家子 SKILL**。接收 tri-mm 转交的媒体任务，对视频意图做 10 维详细设计（时长/分镜头/运镜/转场/画面/旁白/字幕/节奏/画幅/平台），先产出分镜头 `design.md` 交用户确认，确认后再生成视频。旁白协同 tri-audio、BGM 协同 tri-music。

## 特性

- **10 维专业设计**：含分镜头脚本、运镜、转场、字幕、平台适配
- **分镜头确认门**：先出分镜头表再生成，节奏/字幕一次定准
- **子任务协同**：旁白→tri-audio，BGM→tri-music，不越界
- **参数可复现**：分镜头 + 生成参数完整记录

## 目录结构

```
tri-video/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-video-full-testcases.md
```

## 安装

随 tri-mm 包分发，置于 `tri-mm/children/tri-video/`。独立安装需先装 tri-mm。

## 使用

```
tri-mm 识别媒体类型=视频
      → 转交本子SKILL
      → 10 维设计 → 分镜头 design.md
      → 用户确认（确认门）
      → 协同 tri-audio/tri-music → 生成视频落盘
      → result.md 审计
```

## 设计原则

- **先设计后生成**：10 维 + 分镜头表显式填充
- **确认门不可跳**：未确认不调用生成工具
- **协同不越界**：音频归 tri-audio/tri-music
