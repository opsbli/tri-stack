# 大纲 + 动效设计模板与 design.json Schema（references）

> 本文件供阶段二产出与阶段三生成使用。SKILL.md §全流程方法论 阶段二/阶段三引用本模板。大块模板/目录表集中此处，正文仅留指针。

## 一、design.md（人读版，提交审计门②用）

```markdown
# 演示文稿大纲 + 动效方案 · <命名>

- 场景：<汇报/教学/路演/发布会>
- 总页数：<...>
- 配色：主色<...> / 辅助色<...> / 强调色<...>
- 字体：标题<...> / 正文<...>
- 交付格式：<PPTX · 16:9>

| 页码 | 版式 | 标题 | 要点/图示 | 动效(转场) |
|------|------|------|-----------|-------------|
| 1 | cover | <封面标题> | <副标题> | none |
| 2 | section | 目录/章节 | <...> | fade |
| 3 | bullets | <...> | <要点> | fade |
| 4 | data_chart | <...> | 柱状图 | wipe |
| 5 | two_column | <...> | 左文右图 | push |
| ... | | | | |
| N | closing | 谢谢 | <...> | split |

## 动效方案说明
- 转场节奏：封面 none（停留）→ 章节 fade → 内容页 fade/wipe 交替 → 结尾 split。
- 强调点（可选）：关键数据页可在备注标注「强调该数字」。
```

## 二、design.json（机读版，供 build_pptx.py 消费）

```json
{
  "meta": {"title": "演示标题", "subtitle": "副标题", "author": "作者", "date": "2026-08-11"},
  "theme": {
    "aspect": "16:9",
    "colors": {"primary":"#1F4E79","secondary":"#2E75B6","accent":"#ED7D31","bg":"#FFFFFF","text":"#222222","muted":"#666666"},
    "fonts": {"title":"Microsoft YaHei","body":"Microsoft YaHei"}
  },
  "slides": [
    {"layout":"cover","title":"演示标题","subtitle":"副标题","transition":"none"},
    {"layout":"section","section_no":1,"title":"第一章 背景","subtitle":"...","transition":"fade"},
    {"layout":"bullets","title":"核心要点","bullets":["要点一","要点二"],"transition":"fade"},
    {"layout":"data_chart","title":"营收增长","chart":{"type":"bar","title":"季度营收(万)","categories":["Q1","Q2","Q3"],"series":[{"name":"营收","values":[120,150,180]}]},"transition":"wipe"},
    {"layout":"two_column","title":"方案对比","left":{"heading":"方案A","bullets":["..."]},"right":{"heading":"方案B","image_use":"compare","bullets":["..."]},"transition":"push"},
    {"layout":"image_focus","title":"产品展示","image_use":"showcase","caption":"图：产品架构","transition":"fade"},
    {"layout":"comparison","title":"优劣对比","compare":[{"heading":"优势","bullets":["..."]},{"heading":"劣势","bullets":["..."]}],"transition":"wipe"},
    {"layout":"quote","quote":"金句内容","author":"出处","transition":"fade"},
    {"layout":"closing","title":"谢谢观看","subtitle":"联系方式","transition":"split"}
  ]
}
```

### 字段说明
- `meta`：封面/结尾自动套用 title/subtitle/author/date。
- `theme.colors`：六色主题；`theme.fonts`：中英文字体（中文建议 Microsoft YaHei / 思源黑体）。
- `slides[].layout`：cover | section | bullets | two_column | image_focus | data_chart | comparison | quote | closing。
- `slides[].image`：直接给本地图片路径；或 `image_use`：按 materials.json 的 `images[].use` 自动匹配。
- `slides[].chart`：原生图表数据（bar/column/pie/line）。
- `slides[].transition`：逐页转场，取值见下方动效目录表。
- `slides[].notes`：演讲者备注（可选）。

## 三、动效目录表（grep 指引）

| transition 值 | 效果 | 适用 |
|---------------|------|------|
| `none` | 无切换（封面/结尾停留） | cover / closing |
| `fade` | 淡入 | 章节/通用 |
| `wipe` | 擦除 | 数据/内容页 |
| `push` | 推入 | 对比/转折 |
| `split` | 分割 | 结尾 |

> build_pptx.py 据 `transition` 注入 `<p:transition>`（python-pptx 无原生 API，走 oxml）。未知值按 `none` 处理。
> grep 模式：`design.json` / `layout:` / `transition:` / `image_use`
