# tri-audio（tri-mm 音频类子SKILL）

tri-mm 在 I15 多媒体生成下派发的**音频类专家子 SKILL**（非音乐）。接收 tri-mm 转交的媒体任务，对配音/音效/配乐做 8 维详细设计，先产出 `design.md` 交用户确认，确认后再生成音频产物。音乐创作由 tri-music 处理。

## 特性

- **8 维专业设计**：脚本/音色/语速/情绪/时长/BGM音效/技术参数/多语言字幕
- **音乐隔离**：检测到音乐语义自动回退 tri-music
- **设计方案确认门**：先出方案再出声
- **参数可复现**：脚本/音色/语速/种子/采样率完整记录

## 目录结构

```
tri-audio/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-audio-full-testcases.md
```

## 安装

随 tri-mm 包分发，置于 `tri-mm/children/tri-audio/`。独立安装需先装 tri-mm。

## 使用

```
tri-mm 识别媒体类型=音频（非音乐）
      → 转交本子SKILL
      → 多维设计 → design.md
      → 用户确认（确认门）
      → 生成音频落盘工作区
      → result.md 审计
```

## 设计原则

- **先设计后生成**：8 维在 design.md 显式填充
- **确认门不可跳**：未确认不调用生成工具
- **音乐不越界**：音乐归 tri-music
