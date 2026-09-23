---
name: tri-image-full-testcases
description: tri-image（tri-mm 图片类子SKILL）v2.0.0 七场景全栈生图引擎的端到端回归基线，覆盖 E1-E8 能力用例与 D1-D7 降级异常路径。
version: 2.0.0
---

# tri-image 端到端测试用例 v2.0.0

> 本文件是 `tri-image` 2.0.0（七场景全栈生图引擎）的能力回归基线。
> 每条用例对应一种「生图能力必须对等参考基准」的验证点：由 `tests/verify_tri_image.py` 做静态守恒校验，由人工/编排做端到端跑通。
> 版本号须与 SKILL.md / CHANGELOG.md / _meta.json 联动（当前 2.0.0）。

## 端到端能力回归（8 场景，每场景 ≥1 用例）

| 编号 | 场景 | 输入样例 | 通过判据 |
|---|---|---|---|
| E1 | 封面图（T1） | 一篇文章 + `--quick` | 落盘 `prompts/01-cover-*.md` **先于** 出图；产物在 `.tribro/multimedia/image/cover/<slug>/cover.png`；比例生效 |
| E2 | 信息图（T1） | Markdown 讲稿 | 产出 `structured-content.md`（数据未改写）+ `prompts/infographic.md`；21 布局中指定 1 种可命中 |
| E3 | 结构图 SVG（Track-V） | "画一个三层微服务架构图" | **不消耗任何生图额度**；产出单文件 `.svg`（含 `xmlns`、30px padding 的 viewBox、不设固定 width/height） |
| E4 | 结构图 @2x PNG | 同上 + `--scale 3` | 输出 3 倍图且宽高 = viewBox × 3 |
| E5 | 文章配图（批量） | 长文 + 默认批量 4 | 每图必有 `prompts/NN-*.md`；失败项单独重试不波及成功项；Markdown 回写插入路径正确 |
| E6 | 社媒卡组 | "小红书图片，AI 工具推荐" | **image-1 先行且不带 ref**，图 2+ 全部以图 1 为 ref；N 张产出且 N≤10 |
| E7 | 幻灯片 | 主题 + 16:9 | `outline.md` → N 张 prompt → N 张 PNG → `.pptx` + `.pdf` 均存在且页数 = N |
| E8 | 漫画 | 知识主题 + 4 页 | `characters/characters.png` 先行（多角色时），每页 ref 携带；最终 PDF 可合并 |

## 降级与异常路径（D1-D7）

| 编号 | 触发条件 | 期望行为 |
|---|---|---|
| D1 | 无任何 API Key 且 Tier-1 可用 | 走 Tier-1，仍可出全部 7 个光栅场景；结构图 Track-V 始终可用（**唯一零依赖场景，必须能单跑通**） |
| D2 | Tier-1 与 Tier-2 均不可用 | 明确告知 + 询问如何继续，**禁止**静默吐 SVG 敷衍 |
| D3 | 后端不支持 `--ref` | 自动走"角色/参考物描述内联"降级支路（comic / cover 决策表） |
| D4 | 参考图含人物 | 短硬身份话术生效，禁止长外貌描述 |
| D5 | 已出图文字错讹 | 只能重出（新 prompt 文件 + 新文件名），**禁止**用任何程序在 bitmap 上补字（P0 rule） |
| D6 | 压缩在无 cwebp/IM 的 Windows | 跨平台探测成功，或明确报缺少对应后端（非崩溃） |
| D7 | 批次 finishing 部分失败 | 汇报成功/失败计数 + 每图失败原因，只重试失败项 |

## 验证执行约定

- 静态守恒：`python tests/verify_tri_image.py`（门禁全绿为发布前置）。
- 端到端：按上表逐条构造最小输入，核对「通过判据」列；E3/E4（Track-V 零依赖）与 D1/D2 为最高优先级，必须率先验证。
- 所有生图产物默认落盘到 `references/common/output-contract.md` 约定的 `根路径/.tribro/multimedia/image/<scene>/<slug>/`，不污染源码树。
- 版本联动：本文件 `version: 2.0.0` 须与 SKILL.md / CHANGELOG.md / _meta.json 五处一致。
