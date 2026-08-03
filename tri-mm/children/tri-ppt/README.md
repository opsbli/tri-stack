# tri-ppt（tri-mm 演示文稿类子SKILL）

tri-mm 在 I15 多媒体生成下派发的**演示文稿类专家子 SKILL**。接收 tri-mm 转交的媒体任务，对演示文稿意图做 8 维详细设计（主题受众/结构页数/每页大纲/版式/配色字体/图表图示/动画转场/交付格式），先产出大纲 `design.md` 交用户确认，确认后再生成 PPTX。

## 特性

- **8 维专业设计**：结构/版式/配色/图表/动画全覆盖
- **大纲确认门**：先出每页大纲再生成，排版一次定准
- **参数可复现**：版式/配色/字体完整记录

## 目录结构

```
tri-ppt/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-ppt-full-testcases.md
```

## 安装

随 tri-mm 包分发，置于 `tri-mm/children/tri-ppt/`。独立安装需先装 tri-mm。

## 使用

```
tri-mm 识别媒体类型=PPT
      → 转交本子SKILL
      → 8 维设计 → 大纲 design.md
      → 用户确认（确认门）
      → 生成 PPTX 落盘工作区
      → result.md 审计
```

## 设计原则

- **先设计后生成**：8 维 + 每页大纲显式填充
- **确认门不可跳**：未确认不调用生成工具
- **产物必落盘**：PPTX MUST 落盘工作区
