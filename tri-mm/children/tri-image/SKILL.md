---
name: 图片生成
slug: tri-image
version: 2.0.0
displayName: 图片生成
description: 图片生成子SKILL。读取 tri-mm 转交的 I15 多媒体任务（快照§三 + 媒体类型=图片），对位图/矢量图/图表三类意图做多维度详细设计，产出设计方案交用户确认后生成；内置七场景全栈生图能力（封面图/结构图/信息图/文章配图/社媒卡片/幻灯片/知识漫画）与三轨管线（矢量确定性轨 + 原生光栅轨 + 引擎光栅轨）。当 tri-mm 路由建议指向本子SKILL时激活。作为 tri-mm 子SKILL随包安装，支持独立安装，含上游依赖检测两态逻辑（编排模式/引导安装）。
summary: 图片类多维设计专家 + 七场景生图执行引擎，覆盖 9 维设计、21 版式×22 风格、23 配图风格、12 卡片预设、17 幻灯片风格与确定性 SVG 结构图，先出设计方案确认再生成。
tags: [image, design-plan, multimodal, tri-mm-child, cover, infographic, diagram, illustration, slide-deck, comic]
license: MIT
---

# 图片生成（tri-mm 子SKILL · 图片）

> 本 skill 是 tri-mm 在 I15 多媒体生成下的**图片类子 SKILL**，依据 tri-mm 转交的媒体任务（快照 `snapshot.md` §三 + 媒体类型=图片）做多维度详细设计，先产出**设计方案**交用户确认，再生成图片产物。
>
> 用户心智：把 AI 当「懂构图、懂色彩的专业美术指导」——先给清晰方案再出图，而不是先吐一堆不对味的图再返工。
>
> 本次升级把原本只有「设计问卷」的空壳，补成「设计 → 场景路由 → 提示词构建 → 生图 → 合并 → 落盘」的完整执行引擎（详见 CHANGELOG 2.0.0）。

## 强制执行契约（Execution Contract · 最高优先级）

0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级；升级通道不可用则标注 D 态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。

1. **强制前置**：收到 tri-mm 转交任务 MUST 先读取快照 §三，校验 `intent.L2_核心意图 = I15` 且媒体类型 ∈ {图片}；NEVER 跳过校验直接生成。独立使用（未经 tri-mm 路由）MUST 先走 §上游依赖检测 判定模式。
2. **多维设计先于生成**：MUST 先完成 §图片设计方法论 的全部维度分析，产出 `design.md` 设计方案，NEVER 在未经用户确认前直接调用生成工具。
3. **确认门不可跳**：`design.md` MUST 呈现给用户确认；用户未确认前 NEVER 进入生成。用户要求修改 → 修订 design.md 回到确认；用户取消 → 终止。跳过开关见 `references/common/confirmation-policy.md`。
4. **子类型与场景双判定**：MUST 先识别图片子类型（位图/矢量图/图表），再路由到七场景之一与对应轨道（Track-V / Track-R·T1 / Track-R·T2）；路由表见 §场景路由。**NEVER** 用位图轨道产出结构图，也 NEVER 用矢量轨道顶替需要位图的场景。
5. **提示词文件先行（硬）**：每张图的完整终稿提示词 MUST 先落盘 `prompts/NN-{scene}-{slug}.md`，再调用任何后端。详见 `references/common/prompt-file-rules.md`。
6. **产物落盘**：生成产物 MUST 落盘至 `.tribro/multimedia/image/<scene>-<slug>/` 并返回可访问路径，NEVER 只在对话中内联展示不落盘；`result.md` MUST 落盘（完成判据载体）。
7. **参数可复现**：MUST 记录生成参数（提示词/负向/种子/尺寸/后端），便于复现。
8. **结论置信标注（用户硬要求）**：本 skill 产出的每一个结论性表达/判断/推荐 MUST 附三要素——① 置信度（高/中/低）；② 依据类型（`事实 known`/`计算 computed`/`推断 inferred`/`常识 common`/`框架 iframe`/`猜测 guess`）；③ 可验证事实源（有外部来源附 URL，无外部来源附本地证据锚 `file:line` 或标注「无外部来源」）。格式：`结论……（置信度：高；依据：框架 iframe；来源：references/common/image-backend-rules.md）`。**`猜测 guess` 类结论 MUST 标低置信度并提示人工验证。**
9. **自检**：作答前声明「本次意图=I15·图片，已读取快照，子类型=<位图/矢量图/图表>，场景=<七场景之一>，轨道=<Track-V/T1/T2>，设计方案已交付确认=<是/否>，已读教训=<N 条/无文件>」；与快照冲突 MUST 停止并纠正。

## 触发时机

- tri-mm 媒体类型识别为「图片」后路由至本子SKILL
- 意图范围：I15 多媒体生成 · 图片类（位图/矢量图/图表）
- 用户原始意图关键词（任一）：图片/插画/海报/封面/图标/Logo/SVG/图表/流程图/信息图/配图/小红书图片/PPT/幻灯片/漫画

## 上游依赖检测（独立使用时）

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 编排模式** | 由 tri-mm 转交任务（含快照 §三 + 媒体类型=图片） | 读取任务直接推进（标准模式） |
| **B · 引导安装** | 未被 tri-mm 调用且未检测到 tri-mm / 快照 | MUST 提示依赖并引导安装 tri-mm（本子SKILL 不独立做意图识别） |

**模式 B 提示语**：
> 本子SKILL 是 tri-mm 的图片类专家，需由 tri-mm 路由媒体任务。请先安装：`skillhub install tri-mm --dir <目标目录>`。安装后重新发起请求即可获得「意图识别 → 媒体路由 → 图片设计 → 确认 → 生成」完整工作流。

## 输入契约

读取 tri-mm 转交任务中携带的快照 §三 结构化结论区：

| 字段 | 用途 |
|---|---|
| `intent.L2_核心意图` | MUST = I15 |
| 媒体类型（tri-mm 标注） | MUST = 图片 |
| `dimensions.D1_任务领域` | 图片主题/行业语境 |
| `dimensions.D2_输入形态` | 是否有参考图/素材（图生图） |
| `dimensions.D4_输出期望` | 格式（PNG/SVG/JPG/PPTX/PDF） |
| `任务要点` | 产物硬约束（风格/尺寸/元素） |
| `交付预期` | 用户期望交付物 |

> 若快照 `澄清门状态` = 待澄清，不应激活——先由 tri-intent 的 clarify-gate 完成澄清。

## 职责边界

- **负责**：图片类（位图/矢量图/图表）的多维设计 + 七场景生图执行 + 后处理（压缩/格式转换）
- **不负责**：音乐（tri-music）、视频（tri-video）、演示文稿大纲以外的内容（与 tri-ppt 协同）、纯文本成果物（tri-content）、编码开发（tri-coding）
- **与 tri-mm**：tri-mm 负责意图识别与媒体路由；本子SKILL 负责图片专业设计与执行

## 场景路由（本次升级新增 · 核心能力）

> 先判轨道，再进场景。轨道决定「用不用模型、用不用额度、是不是位图」。

| 场景 | scene id | 默认轨道 | 判定信号 | 规范入口 |
|---|---|---|---|---|
| 结构图 | `diagram` | **Track-V**（矢量确定性，零额度） | 架构图/流程图/时序图/ER/组织图/状态机/脑图/时间线/数据流、「画个图」 | `references/scenes/diagram/README.md` |
| 封面图 | `cover` | Track-R | 封面/头图/cover/文章配封面 | `references/scenes/cover/README.md` |
| 信息图 | `infographic` | Track-R | 信息图/信息大图/可视化总结 | `references/scenes/infographic/README.md` |
| 文章配图/视觉素材 | `illustration` | Track-R | 为文章配图/加插图/生成素材 | `references/scenes/illustration/README.md` |
| 社媒图片卡片 | `cards` | Track-R | 小红书图片/图片卡片/微信贴图 | `references/scenes/cards/README.md` |
| 幻灯片 | `slides` | Track-R | PPT/幻灯片/演示/汇报（图片流 + 合并） | `references/scenes/slides/README.md` |
| 知识漫画 | `comic` | Track-R | 知识漫画/教育漫画/传记漫画 | `references/scenes/comic/README.md` |

**轨道定义与切换**

| 轨道 | 实现 | 依赖 | 升降轨条件 |
|---|---|---|---|
| **Track-V** | 手工构造 SVG（含设计系统：8 色语义板、组件模式、分层顺序）+ `scripts/svg_to_png.py` 导出 @Nx PNG | 仅 PNG 导出需渲染器（缺失则只交付 SVG，能力不丢） | 结构图默认不升轨；用户明确要位图质感「概念图」时可升 T1 |
| **Track-R · T1** | 运行环境原生生图工具（如 `ImageGen`） | **零第三方依赖** | 位图场景默认首选 |
| **Track-R · T2** | `scripts/engine/main.ts`（12 provider，批处理并行） | Bun（或 `npx -y bun`）+ 对应 API Key | 需指定 provider/模型、批处理、精确比例（2.35:1）、4K 时升轨 |

> 完整后端解析顺序、两条硬红线、首图锚链、coderef 契约见 `references/common/image-backend-rules.md`（grep 模式：`Track-R` / `⛔` / `首图锚链`）。

## 图片设计方法论（核心能力 · 向后兼容保留）

> 先设计、再生成。每个维度 MUST 在 design.md 中显式填充，避免「凭感觉出图」。

### 多维设计维度

| # | 维度 | 说明 | 常见取值 |
|---|------|------|----------|
| 1 | 主题与语义 | 主体对象、场景、数量、关键元素 | 人物/产品/风景/抽象概念 |
| 2 | 风格与流派 | 视觉风格与参考 | 写实/插画/扁平/3D/像素/水彩/国风/赛博朋克 |
| 3 | 构图与景别 | 主体位置、前景背景、景别 | 三分法/居中/留白/特写/中景/全景 |
| 4 | 色彩与色调 | 主色板、明暗调性、情绪 | 暖调/冷调/高对比/莫兰迪 |
| 5 | 光影 | 光源方向与质感 | 自然光/棚拍/霓虹/逆光/柔光 |
| 6 | 细节与质感 | 材质、清晰度、细节密度 | 金属/毛发/磨砂/高清 |
| 7 | 画幅与分辨率 | 比例、分辨率、格式 | 1:1/16:9/9:16/3:4；PNG/SVG |
| 8 | 参考输入 | 图生图参考 | 有/无；参考图路径 |
| 9 | 负向约束 | 不想要的元素 | 畸变/水印/多余文字 |

### 子类型差异

- **位图**（插画/照片/海报）：重风格+光影+质感；参数含提示词/尺寸/风格/负向/种子
- **矢量图**（图标/Logo/SVG）：重简洁+配色+用途；参数含描述/配色/尺寸
- **图表**（数据/流程）：重数据准确+类型+标注；参数含数据/图表类型/标题/标签

### 场景化维度扩展（本次升级新增）

> 9 维是通用底座；命中具体场景后 MUST 叠加该场景的专属维度，取值来自对应 Gallery。

| scene | 追加维度 | Gallery 条目数（合订本） |
|---|---|---|
| `cover` | Type(6) × Palette(11) × Rendering(7) × Text(4) × Mood(3) × Font(4) | 11+7+3 |
| `infographic` | Layout(21) × Style(22) + 版式×风格推荐组合 | 21+22 |
| `illustration` | Type × Style(23) × Palette(4) + 密度 | 23+4 |
| `cards` | Style(12) × Layout(8) × Palette(3) + 卡片数 | 12+3+4 |
| `slides` | Style(17) + density/mood/texture/typography + 页数启发 | 17+5 |
| `comic` | Art-style(6) × Layout(7) × Tone(7) × Preset(5) + 角色表 | 6+7+5+7 |
| `diagram` | 图类型(9) + 8 色语义板 + 组件模式 | 4（类型细则） |

### design.md 模板

```markdown
# 图片设计方案 · <命名>

- 子类型：<位图/矢量图/图表>
- 场景：<七场景之一> | 轨道：<Track-V / T1 / T2>
- 一句话目标：<...>

| 维度 | 设计决策 |
|------|----------|
| 主题与语义 | <...> |
| 风格与流派 | <...> |
| 构图与景别 | <...> |
| 色彩与色调 | <...> |
| 光影 | <...> |
| 细节与质感 | <...> |
| 画幅与分辨率 | <比例 / 分辨率 / 格式> |
| 参考输入 | <有/无 + 路径> |
| 负向约束 | <...> |
| 场景专属维度 | <style / layout / palette / 页数 等> |

## 生成参数（待确认后执行）
- 正向提示词：<...>
- 负向提示词：<...>
- 尺寸/种子：<...>
- 提示词文件：prompts/NN-{scene}-{slug}.md
```

### 可扩展性

1. 新增风格：在维度 2 取值表追加一行
2. 新增子类型：在子类型差异表追加一段，处理流程自动适配
3. 新增维度：在设计维度表追加一行
4. **新增场景（本次升级新增）**：在 `references/scenes/` 下新增目录 + README.md，并在 §场景路由 表追加一行（同步七处：路由表/契约/输入契约/职责边界/落盘规则/产物清单/自检句）

## 知识装配顺序（分层加载 · 去重与覆盖）

> `references/` 下文件较多，MUST 按层加载，NEVER 一次性全读。

| 层 | 内容 | 何时加载 | grep 模式 |
|---|---|---|---|
| ① 常驻层 | `references/common/user-input-rules.md`、`prompt-file-rules.md`、`confirmation-policy.md` | 每次必读 | `MUST 优先`、`提示词文件先行`、`确认门` |
| ② 场景层 | `references/scenes/<scene>/README.md` + 该场景 Gallery | 命中场景后读 | `## <条目名>`（如 `## bento-grid`） |
| ③ 后端层 | `references/common/image-backend-rules.md`、`references/engine/README.md` | Track-R 命中 T2 时读 | `provider`、`--batchfile` |
| ④ 参考图层 | `references/common/reference-images.md`、`watermark-guide.md` | 有参考图 / 启用水印时读 | `usage:`、`footnote` |
| ⑤ 外部覆盖层 | 用户工作区自定义 Gallery（同名文件） | 用户显式提供时 | — |

**去重与优先级**：同名条目只加载一次；优先级 = ⑤ 外部覆盖层 > ② 场景层 > ① 常驻层。Gallery 采用合订本（一个文件含 N 个 `##` 锚点），读取时 MUST 按命中条目名定位小节，**NEVER 通篇加载**。

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 核心执行。版本检查未通过前 NEVER 进入以下任一执行步骤。

> 含**设计方案确认门**：设计 → 确认 → 生成 → 落盘。

### 步骤 0：偏好加载（⛔ BLOCKING）

首次运行 MUST 完成偏好配置（路径与键空间见 `references/common/preferences-schema.md`）；未完成前 NEVER 进入步骤 1。合并后为**单一命名空间**，七场景共用，NEVER 重复追问。

### 步骤 1：任务接收与校验

1. 读取 tri-mm 转交任务，校验 `L2=I15` 且媒体类型=图片
2. 识别图片子类型（位图/矢量图/图表）+ 场景（§场景路由）+ 轨道
3. 声明自检句

### 步骤 2：多维设计 → 产出 design.md

1. 逐维度填充 §图片设计方法论 表格（结合 `任务要点`/`D1`/`D4`）
2. 追加场景专属维度（从对应 Gallery 取候选与推荐组合）
3. 落盘 `design.md` 至 `.tribro/multimedia/image/<scene>-<slug>/design.md`

### 步骤 3：确认门（不可跳）

1. 向用户呈现 design.md，明确「请确认或提出修改」
2. 确认 → 进入步骤 4；修改 → 修订 design.md 回到本步；取消 → 终止
3. 显式跳过（`--quick` 等）时 MUST 在下一条用户可见输出中声明本次采用的参数

### 步骤 4：构建提示词并落盘（硬要求）

1. 按场景组装终稿提示词（来源见 `prompt-file-rules.md` 组装表）
2. 落盘 `prompts/NN-{scene}-{slug}.md`；已存在则先备份改名
3. 处理参考图（direct/style/palette）、水印（若启用）

### 步骤 5：生成（分轨执行）

- **Track-V**：按 `references/scenes/diagram/README.md` 构造 SVG → 落盘 `.svg` → `python scripts/svg_to_png.py <svg> -s 2`
- **Track-R**：解析后端（`image-backend-rules.md`）→ 比例换算（`python scripts/aspect.py 16:9`，仅 T1 需要）→ 按 `batch-policy.md` 分批 → 生成 → 失败项单独重试一次
- **合并**（slides / comic）：全部图片产出后调用合并脚本（可选依赖，见 §可选依赖）

### 步骤 6：核对与交付

1. 逐项核对 `任务要点` 覆盖（含比例、语言、参考要素是否可见、文字是否错讹）
2. 落盘 `result.md`（产物路径 + 参数 + 核对结果）
3. 返回 tri-mm 汇总；按需跑后处理 `python scripts/compress_image.py <path> -f webp`

## 完成判据（外化 · 可机械校验）

> 「何时算完成」由以下可校验项决定，NEVER 依赖模型自述「已完成」。

| 判据 | 机械校验方式 |
|---|---|
| P-1 设计方案已落盘 | 文件存在：`.tribro/multimedia/image/<scene>-<slug>/design.md` |
| P-2 确认门已通过 | design.md 同级含确认标记，或用户显式跳过（记录于 result.md） |
| P-3 提示词文件完整 | `prompts/NN-*.md` 数量 == 计划生成图数（Track-V 为 1 个构造说明） |
| P-4 产物已落盘 | 每张图对应文件存在且非空 |
| P-5 结果已记录 | `result.md` 存在且含「产物路径 / 参数 / 核对」三段 |
| P-6 自检查通过 | `python tests/verify_tri_image.py` 退出码 0 |

**停车态 vs 结束态**：停在步骤 3（等用户确认）是**停车**，NEVER 判为结束；只有 P-1…P-5 全满足才标记为**结束**。中途交还控制权 MUST 明确写「停车：等待用户确认 design.md」。

## 交付产物

| 产物 | 说明 | 落盘位置 |
|---|---|---|
| design.md | 设计方案（9 维 + 场景维度填充） | `.tribro/multimedia/image/<scene>-<slug>/` |
| prompts/NN-*.md | 每张图的终稿提示词（可复现记录） | 同上 |
| refs/ | 参考图 + 描述文件（按需） | 同上 |
| 图片文件 | PNG / SVG / JPG（按 D4） | 同上，并返回可访问路径 |
| 合并产物 | `{slug}.pdf` / `{slug}.pptx`（slides、comic） | 同上 |
| result.md | 产物路径 + 参数 + 核对结果 | 同上 |

## 质量标准

| 维度 | 标准 | 验证方式 |
|---|---|---|
| 方案完整 | 9 维 + 场景维度全部填充 | design.md 无空维度 |
| 轨道正确 | 结构图走 Track-V、位图走 Track-R | 路由表匹配 + 产物格式 |
| 提示词先行 | 每张图有对应 prompts 文件 | 文件计数比对 |
| 确认到位 | 用户确认后生成 | 确认记录存在 |
| 产物可访问 | 文件已落盘 | 路径可打开 |
| 参数可复现 | 生成参数完整 | 据参数可重生成 |
| 格式合规 | 符合 `D4_输出期望` | 格式一致 |
| 任务要点覆盖 | 满足任务要点全部条目 | 逐项核对 |
| 无标识残留 | 无第三方归属信息 | `tests/verify_tri_image.py` 去标识检查 |

## 进化契约

> 本 skill 如何接收反馈、沉淀经验、自我修订。

1. **反馈接收点**：用户对设计方案/出图结果的任何修正意见即反馈输入（含「风格不对」「文字错讹」「比例错」等）。
2. **经验沉淀位**：`.tribro/image/lessons.md`。启动时（版本检查第零步后）MUST 优先读取该文件；目录或文件不存在时**静默跳过**——NEVER 报错、NEVER 阻断、NEVER 追问。每次执行结束 MUST 追加本次经验教训（含日期、场景、问题、可操作规避动作；空泛内容 NEVER 写入；无新增写「无新增」占位）。写入失败 MUST 提示用户但不阻断交付。
3. **自我修订触发条件**：同一类修正意见在 lessons.md 中累计 ≥3 次 → 修订对应场景的 Gallery 或公共规则（补充负向约束、调整推荐组合），并按版本联动铁律同步 SKILL/CHANGELOG/README/tests 五处版本。

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：`references/version-check-spec.md`。NEVER 在此内联四态判定/升级流程/版本比较算法/节流缓存等细则。

**执行要点**

1. 运行 `python scripts/check_update.py --slug tri-image --json`，解析 `state`：`A`/`B`/`C`/`D` 一律放行并标注口径；`BLOCK` 绝对禁止执行。退出码 `<20` 放行，`>=20` 阻断。
2. 检出陈旧 MUST 自动执行 `skillhub upgrade tri-image` → `skillhub verify tri-image`；失败或通道不可用落 D 态降级继续。
3. 以 junction 指向源码树的 `source: local` 安装跳过自动更新，改为提示维护者手动同步。

## 落盘规则

- 快照由 tri-intent 已落盘 `.tribro/snapshots/`
- 本子SKILL 链路文档落盘于 `.tribro/multimedia/image/<scene>-<slug>/`（design.md + prompts/ + refs/ + result.md）
- 图片产物落盘同目录并返回可访问路径——这些是实际产物，不是 tri 链路文档
- **教训文件**：`.tribro/image/lessons.md`（见 §进化契约）
- design.md 在确认前可覆盖更新；result.md 落盘后不修改（审计完整性）

## 可选依赖（按需启用，缺省不影响主链路）

| 能力 | 依赖 | 缺失时降级 |
|---|---|---|
| Track-V 的 PNG 导出 | resvg / rsvg-convert / inkscape / ImageMagick / cairosvg | 仅交付 SVG（主要产物，能力不丢） |
| Track-R · T2 引擎 | Bun（或 `npx -y bun`）+ 对应 API Key | 走 T1 原生轨 |
| 幻灯片/漫画合并 | Bun + `pdf-lib` / `pptxgenjs` | 交付 PNG 序列，不合并 |
| 压缩转码 | cwebp / ImageMagick / Pillow | 跳过压缩，交付原图 |

## 目录结构

```
tri-mm/children/tri-image/
├── SKILL.md                        主入口：9维设计 + 七场景路由 + 三轨管线 + 完成判据
├── README.md                       特性/目录/用法/测试/设计原则
├── CHANGELOG.md                    版本变更历史
├── _meta.json                      版本与元信息（五处版本联动之一）
├── references/
│   ├── common/                     公共层（去重后单一命名空间）
│   │   ├── user-input-rules.md     用户输入工具约定
│   │   ├── image-backend-rules.md  后端选择 + 双红线 + 首图锚链 + coderef 契约
│   │   ├── prompt-file-rules.md    提示词文件先行 + 组装来源表
│   │   ├── batch-policy.md         批处理优先序与 n=1 特例
│   │   ├── confirmation-policy.md  确认门 + 开关别名表
│   │   ├── reference-images.md     参考图处理与身份保持话术
│   │   ├── watermark-guide.md      水印注入
│   │   ├── preferences-schema.md   合并后的偏好键空间
│   │   └── output-contract.md      统一输出契约与备份铁律
│   ├── engine/                     引擎层（Track-R · T2）
│   │   ├── README.md               CLI 选项/环境变量/provider 优先级
│   │   ├── usage-examples.md       分 provider 调用示例
│   │   ├── oauth-vs-api-key.md     订阅凭证 ≠ API Key 的边界
│   │   ├── image-fallback.md       免密降级路径
│   │   └── providers/              7 份 provider 专档
│   ├── scenes/                     场景层（每场景 README + Gallery 合订本）
│   │   ├── cover/ · infographic/ · illustration/ · cards/ · slides/ · comic/ · diagram/
│   └── postprocess/                后处理说明
├── scripts/
│   ├── engine/                     生图引擎（TS，零第三方依赖）+ providers/ + coderef/
│   ├── aspect.py                   宽高比 → 像素尺寸（T1 必需）
│   ├── svg_to_png.py               SVG → @Nx PNG（跨平台探测 + 同名命令身份校验）
│   ├── compress_image.py           压缩/转码（跨平台探测 + 防覆盖）
│   ├── merge-to-pdf.ts · merge-to-pptx.ts · merge-to-pdf-comic.ts   合并（可选依赖）
│   └── check_update.py             版本门（与家族同源）
└── tests/
    ├── verify_tri_image.py         静态门禁自检（退出码 0/2/3）
    └── tri-image-full-testcases.md 全场景测试用例
```
