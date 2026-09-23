# tri-image（tri-mm 图片类子SKILL）

tri-mm 在 I15 多媒体生成下派发的**图片类专家子 SKILL**。接收 tri-mm 转交的媒体任务（快照 §三 + 媒体类型=图片），对位图/矢量图/图表三类意图做 9 维详细设计，先产出 `design.md` 设计方案交用户确认，确认后按**七场景 × 三轨管线**生成图片产物。

> v2.0.0 起从「设计问卷」升级为「设计 + 执行引擎」：补齐七场景 Gallery、生图引擎、确定性结构图轨与后处理，全部对外接口向后兼容。

## 特性

- **9 维专业设计**：主题/风格/构图/色彩/光影/质感/画幅/参考/负向，逐维度可解释
- **子类型自适应**：位图（插画/海报）、矢量图（图标/Logo/SVG）、图表（数据/流程）差异参数
- **七场景全覆盖**：封面图 / 结构图 / 信息图 / 文章配图 / 社媒卡片 / 幻灯片 / 知识漫画
- **三轨管线**：
  - **Track-V 矢量确定性**——结构图手绘 SVG，零额度、可编辑、不依赖模型
  - **Track-R · T1 原生光栅**——运行时原生生图能力，**零第三方依赖**
  - **Track-R · T2 引擎光栅**——12 provider、批处理并行、精确比例与 4K（需 Bun + Key）
- **Gallery 规模**：21 信息图版式 × 22 风格、23 配图风格、12 卡片预设、17 幻灯片风格、11 封面调色板 × 7 渲染、漫画 6 画风 × 7 版式 × 7 基调 × 5 体裁
- **提示词文件先行**：每张图终稿提示词先落盘，可复现、可换后端、可审计
- **完成判据外化**：P-1…P-6 可机械校验，区分停车态与结束态
- **经验教训闭环**：`.tribro/image/lessons.md` 启动读取、结束追加

## 目录结构

```
tri-image/
├── SKILL.md                        主入口：9维设计 + 七场景路由 + 三轨管线 + 完成判据
├── README.md
├── CHANGELOG.md
├── _meta.json                      版本与元信息
├── references/
│   ├── common/                     公共层（8 份，去重后单一命名空间）
│   ├── engine/                     引擎层文档 + 7 份 provider 专档
│   ├── scenes/                     七场景（cover/infographic/illustration/cards/slides/comic/diagram）
│   └── postprocess/compress.md     压缩与格式转换
├── scripts/
│   ├── engine/                     生图引擎（TS，零第三方依赖）
│   ├── aspect.py                   宽高比 → 像素尺寸
│   ├── svg_to_png.py               SVG → @Nx PNG
│   ├── compress_image.py           压缩/转码
│   ├── merge-to-pdf.ts 等          合并（可选依赖）
│   └── check_update.py             版本门
└── tests/
    ├── verify_tri_image.py         静态门禁自检（退出码 0/2/3）
    └── tri-image-full-testcases.md 全场景测试用例
```

## 安装

本子SKILL 随 tri-mm 包分发，置于 `tri-mm/children/tri-image/`。独立安装时需先装 tri-mm：

```
skillhub install tri-mm --dir <目标目录>
```

## 使用

由 tri-mm 自动路由；用户亦可直接点名。标准流程：

```
tri-mm 识别媒体类型=图片
      → 转交本子SKILL（携带快照 §三）
      → 场景路由（七场景之一）+ 轨道判定（Track-V / T1 / T2）
      → 多维设计（9 维 + 场景维度）→ 产出 design.md
      → 用户确认（确认门）
      → 提示词落盘 prompts/NN-{scene}-{slug}.md
      → 分轨生成（必要时合并 PPTX/PDF）
      → result.md 落盘 + 交付
```

### 脚本速查

```bash
python scripts/aspect.py 16:9 --quality 2k --json     # 比例换算（T1 必用）
python scripts/svg_to_png.py a.svg -s 2               # 结构图 @2x 导出
python scripts/compress_image.py out.png -f webp -q 80
python scripts/check_update.py --slug tri-image --json
python tests/verify_tri_image.py                      # 门禁自检，退出码 0 为通过
```

## 测试

`tests/tri-image-full-testcases.md` 覆盖：静态门禁（去标识残留、版本一致、行数、文件数、引用越界、Gallery 计数）、七场景端到端、降级路径（无 Key、无渲染器、参考图不支持、文字错讹）与向后兼容项。

## 设计原则

- **先设计后生成**：9 维 + 场景维度在 design.md 显式填充，不凭感觉出图
- **确认门不可跳**：未确认不调用生成工具
- **轨道不串用**：结构图走矢量轨、位图走光栅轨，互不顶替
- **提示词先行**：终稿提示词必落盘，是可复现记录
- **产物必落盘**：图片 MUST 落盘工作区并返回可访问路径
- **零依赖优先**：主链路不依赖任何第三方包，重型能力一律降级可选
