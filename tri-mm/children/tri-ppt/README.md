# tri-ppt（tri-mm 演示文稿类子SKILL · 全流程自动化）

tri-mm 在 I15 多媒体生成下派发的**演示文稿类专家子 SKILL**，并升级为**端到端全自动流水线**：接收 PPT 任务后，先「从全网采集文字/图片/图表素材」→ 提交**素材审计** → 据已审计素材设计大纲与逐页动效方案 → 提交**设计审计**（可多轮迭代）→ 全部通过后生成设计精美、可直接下载的 PPTX。

## 特性

- **全网素材采集**：WebSearch/WebFetch 取文字与图表数据，ImageGen 生成主题配图（版权无忧）
- **双审计门**：素材审计 + 设计审计，全程不黑箱，可多轮迭代
- **大纲 + 逐页动效方案**：8 维设计 + 逐页转场/强调方案，先确认再生成
- **确定性生成**：`scripts/build_pptx.py`（python-pptx）按 design.json 产出高质量 PPTX
- **参数可复现**：版式/配色/字体/动效/素材来源完整记录

## 目录结构

```
tri-ppt/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── scripts/
│   ├── build_pptx.py             # 确定性 PPTX 生成器
│   └── check_update.py           # 版本门脚本（与 tri-intent 同源）
├── references/
│   ├── materials-template.md     # 素材库模板 + materials.json schema
│   └── design-template.md        # 大纲+动效模板 + design.json schema + 动效目录表
└── tests/
    └── tri-ppt-full-testcases.md
```

## 安装

随 tri-mm 包分发，置于 `tri-mm/children/tri-ppt/`。独立安装需先装 tri-mm。

## 使用

```
tri-mm 识别媒体类型=PPT
      → 转交本子SKILL
      → 阶段一：全网采集 → materials.md/materials.json
      → 审计门①：素材审计（通过/补充/剔除）
      → 阶段二：大纲 + 逐页动效设计 → design.md/design.json
      → 审计门②：设计审计（可多轮迭代）
      → 阶段三：build_pptx.py 生成 PPTX 落盘工作区
      → result.md 审计
```

## 设计原则

- **采集先于设计**：素材审计通过前不进入大纲设计
- **双门不可跳**：素材审计 + 设计审计均通过方可生成
- **产物必落盘**：PPTX MUST 落盘工作区并返回可访问路径
- **确定性生成**：版式/配色/图表/转场由 `build_pptx.py` 算法落地，不靠模型自律复现
