# 提示词文件先行规则（公共层 · 硬要求）

> 「先写提示词文件，再生图」是本 skill 的可复现性根基。任何后端、任何场景都适用。

## 规则

1. **每张图的完整终稿提示词 MUST 落盘**为独立文件后再调用后端；命名 `prompts/NN-{scene}-{slug}.md`（NN 两位序号）。
2. 该文件是**可复现记录**：换后端、重出、审计都读它。**NEVER** 用临时内联字符串直接调后端。
3. 文件 MUST 包含「完整终稿」而非片段——包括场景参数（风格/版式/调色板/比例/语言）、从源内容提取的真实数据、参考图约束、水印（若启用）。
4. 配 Frontier 元数据（YAML frontmatter）用于标注参考图用途：

```yaml
---
scene: cover
palette: elegant
rendering: flat-vector
references:
  - ref_id: 01
    filename: refs/ref-01-{slug}.png
    usage: direct | style | palette
---
```

5. **重写前的备份铁律**：目标提示词文件或图片文件若已存在，MUST 先改名为 `<name>-backup-YYYYMMDD-HHMMSS.<ext>`， NEVER 直接覆盖（保护用户手改内容并支持回滚）。
6. 「文本修正型重出」MUST 写**新提示词文件 + 新输出文件名**，保留有缺陷的候选以便对比。

## 各场景的提示词组装来源

| 场景 | 组装来源 |
|---|---|
| 封面图 | `../scenes/cover/prompt-template.md` + Gallery 词条 |
| 信息图 | `../scenes/infographic/base-prompt.md` + layouts/styles 词条 + structured-content |
| 结构图 | 不产生提示词文件（Track-V 直接产出 SVG），但 MUST 落 `prompts/{name}.md` 记录构造说明以便复现 |
| 文章配图 | `../scenes/illustration/prompt-construction.md` |
| 社媒卡片 | `../scenes/cards/prompt-assembly.md` |
| 幻灯片 | `../scenes/slides/outline-template.md` + `base-prompt.md` |
| 漫画 | `../scenes/comic/storyboard-template.md` + `character-template.md` |

## 反模式

| 反模式 | 后果 | 正解 |
|---|---|---|
| 内联字符串直接调后端 | 无法复现、无法换后端、无法审计 | 先落盘提示词文件 |
| 提示词里写「参见上文」 | 重跑时上下文已失 | 终稿 MUST 自包含 |
| 覆盖已有提示词 | 丢用户修订 | 备份改名 |
| 用代码修图上的字 | 违反 Track-R 红线 2 | 改提示词重出 |
