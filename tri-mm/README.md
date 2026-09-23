# tri-mm

多媒体生成下游**路由编排** skill。读取 tri-intent 快照 §三，处理 I15（多媒体生成）意图，识别媒体大类（图片/音频/视频/PPT）并拍发至对应子 SKILL 执行；音乐创作委派 tri-music。每个子 SKILL 先产出多维度设计方案交用户确认后再生成。当 tri-intent 快照下游路由建议指向本 skill 时激活。

本 skill **只负责意图识别后的「媒体类型识别 + 子SKILL 路由拍发 + 设计方案确认门编排 + 产物汇总」**，不再自行构造生成参数或直接生成——专业设计与生成由各子 SKILL 负责。核心理念：**先识别媒体类型，再拍发给对应专家，专家先出设计方案确认后再生成**。

## 特性

- **媒体类型识别**：图片 / 音频（非音乐）/ 视频 / PPT 四大类，据 `D4_输出期望` + `任务要点` 关键词匹配；音乐语义委派 tri-music
- **子SKILL 路由拍发**：`children/tri-image` `children/tri-audio` `children/tri-video` `children/tri-ppt`，每个子SKILL 是独立的多维设计专家
- **设计方案确认门**：子SKILL MUST 先产出 `design.md` 设计方案交用户确认，确认后才生成——避免反复返工
- **多维专业设计**：图片 9 维 / 音频 8 维 / 视频 10 维 / PPT 8 维，每维可解释、可扩展
- **协同不越界**：视频旁白→tri-audio、BGM→tri-music；音乐全案→tri-music
- **轻量编排 + 独立安装两态依赖检测**：不支持降级模式（模式 B 硬性阻断）
- **跨媒体提示词结构**：新增 `references/prompt-structure.md`——图像六段 / 视频八段骨架、角色·场景·风格三锚复用、单变量迭代与可复现参数记录；场景级构建仍归各子 SKILL。

## 目录结构

```
tri-mm/
├── SKILL.md                     主入口：I15 路由编排 + 媒体类型识别 + 确认门编排
├── README.md
├── CHANGELOG.md
├── tests/
│   └── tri-mm-full-testcases.md 全场景测试用例
└── children/                    子SKILL（多维设计 + 确认门 + 生成）
    ├── tri-image/               图片（位图/矢量图/图表）
    ├── tri-audio/               音频（配音/音效/配乐，非音乐）
    ├── tri-video/               视频（分镜头设计）
    └── tri-ppt/                 演示文稿（大纲设计）
```

## 安装

将 `tri-mm/` 目录（含 `children/`）放入你的 skills 目录即可：

```bash
cp -r tri-mm/ /path/to/your/skills/
```

本 skill 可独立安装。激活时检测外部 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|---|---|---|
| A · 快照模式 | `.tribro/snapshots/` 有快照 或 skills 目录有 `tri-intent/` | 读取快照 §三，按工作流推进（标准模式） |
| B · 引导安装 | 以上均不满足 | 向用户提示依赖并引导安装 `skillhub install tri-intent` |

> 本 skill 不支持降级模式——模式 B 为硬性阻断，MUST 安装 tri-intent 后方可使用。

## 使用

### 核心流程

收到 tri-intent 快照且 `下游路由建议` 指向本 skill 后，按以下链路推进：

```
读取快照 §三 (L2 = I15)
        │
        ▼
  媒体类型识别（图片/音频/视频/PPT/音乐）
        │
        ├── 音乐 → 委派 tri-music（歌曲创作全案）
        │
        ▼（非音乐）
  拍发对应子SKILL（携带快照 §三 + 媒体类型标注）
        │
        ▼
  子SKILL 多维设计 → 产出 design.md
        │
        ▼
  确认门：用户确认 / 修改 / 取消
        │（确认）
        ▼
  子SKILL 生成产物落盘工作区
        │
        ▼
  tri-mm 汇总核对 → result.md
```

### 媒体类型 → 子SKILL 路由表

| 媒体大类 | 拍发子SKILL | 子SKILL 设计维度 |
|----------|-------------|------------------|
| 图片 | children/tri-image | 主题/风格/构图/色彩/光影/质感/画幅/参考/负向（9 维） |
| 音频（非音乐） | children/tri-audio | 脚本/音色/语速/情绪/时长/BGM音效/技术/字幕（8 维） |
| 视频 | children/tri-video | 时长/分镜/运镜/转场/画面/旁白/字幕/节奏/画幅/平台（10 维） |
| PPT | children/tri-ppt | 主题受众/结构页数/大纲/版式/配色字体/图表/动画/格式（8 维） |
| 音乐 | tri-music（委派） | 歌曲创作全案 |

## 测试

完整测试用例见 `tests/tri-mm-full-testcases.md`，覆盖媒体类型识别、子SKILL 路由拍发、确认门编排、音乐委派 tri-music、产物汇总核对、上游依赖检测两态逻辑等能力点。

## 设计原则

- **类型识别前置**：MUST 先识别媒体大类再拍发子SKILL，跳过识别直接调用必失配
- **拍发不代做**：tri-mm 只路由编排，专业设计与生成由子SKILL 负责
- **确认门不可跳**：子SKILL 未获用户确认 design.md 前不得生成
- **协同不越界**：音频/音乐归 tri-audio/tri-music，图片/视频/PPT 各归其位
