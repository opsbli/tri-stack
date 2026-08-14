# 素材库模板与 materials.json Schema（references）

> 本文件供阶段一产出使用。SKILL.md §全流程方法论 阶段一与审计门① 引用本模板。大块参考表集中此处，正文仅留指针（满足家族约束：大块参考表移 references/）。

## 一、materials.md（人读版，提交审计用）

```markdown
# 素材库 · <命名>

## 文字内容
- [论点/数据] <内容摘要> —— 来源：<URL> —— 用途：<第N页/封面>
- ...

## 图表数据
- [图表] <描述> —— 数值：<类别=值, ...> —— 来源：<URL> —— 用途：<第N页 data_chart>

## 图片素材
- [配图] <提示词/主题> —— 方式：ImageGen / 外采(<URL>) —— 本地：assets/xxx.png —— 用途：<封面/第N页>
- ...

> 版权声明：外采图片均确认可商用授权；无授权项已用 ImageGen 替代生成。
```

## 二、materials.json（机读版，供生成脚本消费）

```json
{
  "text": [
    {"content": "内容摘要", "source": "https://...", "use": "p3"}
  ],
  "charts": [
    {"desc": "季度营收", "data": {"categories": ["Q1","Q2","Q3"], "series": [{"name":"营收","values":[120,150,180]}]}, "source": "https://..."}
  ],
  "images": [
    {"path": "assets/cover.png", "prompt": "科技蓝抽象商务封面", "source": "imagegen", "use": "cover"}
  ]
}
```

字段说明：
- `text[].use` / `images[].use`：与 design.json 中 slide 的 `image_use` 或页码对应，生成时按 `use` 自动匹配图片。
- `images[].path`：相对于 design.json 所在目录的本地图片路径（生成脚本自动拼接绝对路径）。
- `charts[]`：仅作审计留痕；实际图表数据在 design.json 的 `slide.chart` 中结构化给出。

## 三、采集规范（grep 指引）

- 检索文字/数据：`WebSearch "<主题> 数据/报告/白皮书"` → 优先权威站（政府/智库/官方文档）。
- 生成配图：`ImageGen "<主题> 风格=商务/科技/扁平 比例=16:9"`。
- 外采图：`WebSearch "<主题> site:unsplash.com OR site:pexels.com"` → 确认 license 后下载到 `assets/`。

> grep 模式：`素材库` / `materials.json` / `use=` / `ImageGen`
