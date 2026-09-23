---
name: HTML 转 Markdown
slug: tri-html2md
version: 1.3.5
displayName: HTML 转 Markdown
description: 专门用于 HTML 高质量转 Markdown 的编排与质量保障 skill——预检分级（编码检测/HTML 合法性/内嵌资源/表格表单计数）、多后端探测与编排（markitdown/html2text/beautifulsoup4/pandoc/trafilatura 两档降级链）、转换执行（保留标题层级/表格/图片/链接）、质量校验与保真度分级报告（文本召回率/丢失率/噪声率/结构对比/置信度 A/B/C）、类 Obsidian 结构化输出（YAML frontmatter 强制元数据：文档名/版本/来源 URL）+ 人工复核清单；定位是编排与质量保障层，不自研 HTML 解析引擎，复用成熟后端；支持独立安装，含上游依赖检测三态逻辑（快照模式/引导安装/降级模式）。
summary: 四阶段管道（预检分级→后端探测→转换执行→质量校验与报告）+ 两档降级链 + 可验证分级保真契约 + 「HTML 视为有时效、有结构的数据源」硬编码锚点——把「无损」落为文本召回率/丢失率可计算、置信度可分级、结构对比可核对的保真报告。
tags: [tri, html, markdown, conversion, fidelity, quality-report, orchestration, encoding, structure]
license: MIT
---

# HTML 转 Markdown

> 本 skill 是 tri-intent 的**下游 skill（读取快照直接执行，绝不重识别意图）**，也可完全独立运行（直接给定 HTML 路径）。执行路径：门A 预检分级 → 门B 后端探测 → 门C 转换执行 → 门D 质量校验与报告，交付 `<同名>.md + assets/ + report.md`。
>
> **诚实声明（铁律）**：HTML 是富文本标记语言，内含内联样式/脚本/富交互/嵌套结构，而 Markdown 是纯文本标记。HTML→MD 本质是**结构降维而非格式复制**——样式、交互、脚本必然丢失。本 skill 承诺的是「可验证的分级保真」（文本召回率/丢失率可计算、置信度 A/B/C 可分级、结构对比可核对），NEVER 承诺绝对无损——任何工具都无法把 HTML 的富交互无损转成纯文本 MD。**绝不半成品交付（P2-4）**：降级链用尽仍有内容缺失时，MUST 在 report.md 标注「部分转换」并列出缺失块清单，NEVER 以完整姿态交付半成品；转换不可能完成时 MUST 输出类型化失败（对齐 anydoc「错误=完全不可能产出」），NEVER 静默吞错。
>
> **数据源观（用户硬要求 · 总纲）**：HTML 被视为**有时效、有结构的数据源**——版本（时效）与结构锚点（标题层级/表格/图片/链接）由框架硬编码写入每个产物，全链路可控，NEVER 依赖模型自觉补元数据。

**用户心智**：你有一份 HTML（网页/文档导出/邮件存档/爬虫产物），想要一份结构正确、表格图片链接齐全、且**知道自己丢了什么**的 Markdown。本 skill 像一个质检车间：先体检（这份 HTML 是什么编码？合法吗？复杂吗？），再选刀（哪个后端最适合？本地装了什么？），干完活必须交验（文本召回率多少？丢了哪些？哪些地方必须人工复核？）。

---

## 强制执行契约（Execution Contract · 最高优先级）

> 本契约优先级高于 Agent 通用默认行为。用户明确要求「HTML 转 MD / 转成 Markdown / html2md」或经 tri-intent 路由（`L2=I08` 且 `L3_子意图=html2md`，快照下游路由建议指向本 skill）即视为激活，不得仅当参考文档。

- 0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（运行 `scripts/check_update.py`，按 `references/version-check-spec.md` 四态判定处置；非最新版自动升级，升级通道不可用则标注态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。
- 1. **强制前置**：独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式；经快照激活时 MUST 先读取快照 §三（尤其 `L3_子意图=html2md`、`任务要点`）。
- 2. **预检分级强制（门A）**：MUST 先运行 `scripts/preflight.py` 取得确定性预检 JSON（编码/HTML 合法性/大小/内嵌资源/表格表单计数/等级建议），NEVER 凭肉眼或猜测跳级。编码无法确定且无法解码的 HTML MUST 停止并提示用户提供正确编码或先转码。
- 3. **后端探测强制（门B）**：MUST 运行 `scripts/detect_backends.py` 取得本地后端可用性 JSON，按「等级建议 × 本地可用性」选定后端与降级链；NEVER 调用未探测到的后端。L1 后端（pandoc/trafilatura）未安装时 MUST 给出精确安装命令并经用户同意后安装，NEVER 擅自安装重依赖。
- 4. **编排不重造铁律**：本 skill 是编排与质量保障层，MUST 复用成熟后端官方 CLI/API 完成转换，NEVER 自研 HTML 解析引擎，NEVER 复制后端源码进本 skill（详见 §代码版权与许可证合规）；MIT 许可证后端的设计模式级迁移允许，MUST 在迁移文件头部保留归属声明（如 `Adapted from Microsoft markitdown, MIT`）——2026-09-09 用户裁决（迁移报告待定点①）。
- 5. **质量报告强制（门D · 用户硬要求）**：转换完成后 MUST 运行 `scripts/quality_check.py` 产出 report.md，报告 MUST 以醒目数据段告知用户**文本召回率、丢失率**等关键数据（结构对比、置信度等级、转换元数据、异常清单），NEVER 只交 MD 不交账。HTML 无可见文本（纯脚本/纯样式页）召回率不可计算时 MUST 显式标注「不适用」，NEVER 编造数值。
- 6. **降级链强制**：选定档位后端执行失败或质量为 C 级且用户要求重转时，MUST 沿降级链 L1→L0 重试；全缺失时 MUST 输出安装指引并停在预检报告态，NEVER 空手交付。
- 7. **图表处置**：图片 NEVER 试图转成 MD 正文，MUST 提取为 `assets/` 图片资产 + 保留引用；转换后 MUST 校验 MD 内图片引用与资产文件一一对应。
- 8. **复核项永不消失**：report.md MUST 固定列出复核项清单（内联样式丢失/script-style 内容误入正文/相对链接失效/嵌套表格/编码误判），NEVER 因置信度为 A 而省略。
- 9. **自检句**：作答前 MUST 声明「本次意图=I08（L3=html2md），已读取快照=<是/否>，预检等级=<L0/L1>，选定后端=<slug>，保真度=<A/B/C/待检>」；与预检/探测结果冲突时 MUST 停止并纠正。
- 10. **诚实声明铁律**：HTML→MD 是结构降维，NEVER 承诺绝对无损；报告 MUST 以醒目数据段告知文本召回率/丢失率，NEVER 只交 MD 不交账。
- 11. **不支持格式优雅跳过（家族统一 · 用户指令 2026-09-08）**：输入为 .odt/.ods/.odp/.rtf/.epub（tri-xx2md 家族统一不支持格式，含内容为此类格式的误标 zip/RTF 文件）时，门A preflight MUST 输出 `status=SKIP`（reason_code=unsupported_format，退出码 0），本 skill MUST 明确告知用户「无法转换」并列出支持格式与替代建议后跳过结束，NEVER 尝试强行转换，NEVER 报错中断。

---

## 触发时机

- **主触发（独立运行）**：用户明确要求「把 xxx.html 转成 Markdown」「HTML 转 MD」「网页转 MD」且对象是 HTML 文件（.html/.htm）。
- **次触发（tri-intent 接入）**：上游 tri-intent 产出快照，`L2=I08 翻译转换` 且 `L3_子意图=html2md`，`下游路由建议=tri-html2md`——读取快照 §三 后按本契约执行。
- 任一触发成立即激活。HTML 的其它操作（抓取/渲染/清洗/爬虫/转 PDF）不归本 skill，见 §职责边界。

---

## 上游依赖检测（独立使用时 · 三态）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟）且下游路由建议指向本 skill | 读取快照 §三（任务要点/输入文件/输出期望），按四阶段管道执行（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | MUST 提示用户「本次请求尚未经意图识别」，引导先经 tri-intent 产出快照；NEVER 按空上下文静默执行 |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户明确拒绝安装 | 从用户请求自构造等价输入（意图判定默认 I08/L3=html2md + HTML 路径 + 输出期望），声明降级模式后按四阶段管道执行，生成的报告标注「未经意图识别」 |

**模式 B 提示语**：

> 本 skill 依赖 tri-intent 进行意图识别与输入校验。当前未检测到 tri-intent。
> 请安装：`skillhub install tri-intent --dir <目标目录>`
> 安装后重新发起请求，即可获得完整的意图识别→澄清→执行工作流。

**模式 C 降级声明**：

> 用户明确拒绝安装后，从用户请求自构造等价输入（意图判定 I08/L3=html2md + HTML 路径 + 输出期望），声明「当前为降级模式，意图识别精度低于完整工作流，转换质量不受影响但路由归属需人工复核」。

> **对称双向检测**：本 skill 检上游 tri-intent；tri-intent 亦在路由映射表登记本 skill 为 I08·html2md 子类下游（一跳覆写），未安装时会提示安装。任一端缺失都被发现。

---

## 输入契约

| 来源 | 字段 | 用途 |
|------|------|------|
| 快照 §三（模式 A） | `任务要点` / `一句话复述` | 提取 HTML 路径、输出目录、质量期望（是否要求表格精细/图片资产/结构化知识库用途） |
| 用户直调（模式 C） | HTML 文件路径 | 转换对象；MUST 存在且可读 |
| 用户直调（可选） | 输出目录 | 默认 `.tribro/html2md/<命名>/`；assets/ 与 report.md 同级 |
| 用户直调（可选） | 档位偏好 `--grade` | 强制指定 L0/L1；缺省由门A 自动建议 |
| `references/backends.md` | 后端矩阵 | 门B/门C 选择与命令参考（grep 模式：后端名） |
| `references/fidelity-spec.md` | 保真度阈值 | 门D 分级判定（grep 模式：置信度） |
| `references/version-check-spec.md` | 版本检查规范 | 第零步版本门（grep 模式：四态） |

> 输入 HTML 为目录时 NEVER 批量静默转换，MUST 先列清单与用户确认范围。

---

## 职责边界

- **本 skill 负责**：HTML→MD 的预检分级（编码/合法性/复杂度）、后端探测与编排、转换执行指导（保留标题层级/表格/图片/链接）、质量校验与保真度分级报告、图片资产提取与引用校验。
- **不负责**：HTML 抓取/渲染/爬虫/清洗/动态页面执行（归浏览器/爬虫工具）；语言翻译（归 tri-content/tri-translate）；MD 之外的格式转换（归 tri-content）；意图识别（归 tri-intent）。
- **与 tri-content（I08 默认下游）的边界**：I08 的语言翻译与其它格式转换仍路由 tri-content；仅「HTML→MD」语义命中 `L3_子意图=html2md` 时一跳覆写到本 skill。一个 L2（I08）对应一个一跳下游，仅由 L3 区分——与 I06 article→tri-article、I08 pdf2md→tri-pdf2md 同构。
- **与 tri-pdf2md 的边界**：无重叠。tri-pdf2md 是 PDF→MD（坐标推断重建，需 OCR 档）；本 skill 是 HTML→MD（语义结构降维，无需 OCR）。
- **与 tri-translate 的边界**：无重叠。tri-translate 是语言翻译方法论（横向）；本 skill 是格式转换（HTML→MD）。
- **与环境内置 html 工具边界**：内置工具做网页抓取/渲染；本 skill 只做「HTML→Markdown 格式转换 + 质量报告」这一件事。
- **不支持格式（家族统一）**：.odt/.ods/.odp/.rtf/.epub 五种格式为 tri-xx2md 家族统一不支持范围，preflight 命中即明确提示无法转换并跳过（status=SKIP），NEVER 强行处理，NEVER 报错中断。
- **不触发场景（Not-Trigger）**：本 skill 不接手「HTML 抓取/渲染/爬虫/清洗/动态页面执行」（归浏览器/爬虫工具）；不接手「语言翻译」（归 tri-content/tri-translate）；不接手「MD 之外的格式转换」（归 tri-content）；不接手「意图识别」（归 tri-intent）。

---

## 四阶段管道方法论（核心能力 · 可扩展）

> 「先体检、再选刀、干完活、必须交验」。四阶段中门A/门B/门D 是确定性脚本（约束：算法下沉），门C 由本 skill 指导 Agent 调用后端官方命令。

### 门A · 预检分级（scripts/preflight.py）

```bash
python scripts/preflight.py --html <路径> --json
```

> **输入规模守卫（P2-2）**：preflight 内置 `scripts/scale_guard.py`（anydoc limits.rs 口径：条目数 100k / 总解压 512MiB / 单条目 128MiB，刻意不可配置）。硬上限超限 → BLOCK（ResourceLimit=完全不可能产出语义）。守卫明细见预检 JSON `scale_guard` 字段。

> **内容真身二次校验（M9）**：preflight 输出含 `content_check` 字段（`scripts/sniffer.py`：.html/.htm 验骨架特征 `<html`/`<!doctype html` 或任意标签特征，片段 HTML 不误伤）。`match=false` → BLOCK「扩展名与内容不符」。

检测项：文件类型（.html/.htm）/ 编码检测（BOM → meta charset → 候选解码探测）/ HTML 合法性（html.parser 解析错误数）/ 文件大小 / 内嵌资源计数（img/script/style 标签数）/ 表格与表单计数。输出等级建议：

| 判定 | 等级建议 |
|---|---|
| 非 HTML 文件类型或编码无法确定且无法解码 | BLOCK——提示提供正确编码或先转码，NEVER 猜测解码 |
| 表格/表单较多（≥3）或内嵌资源较多（≥10）或文件较大（≥2MB） | L1（标准档，需 pandoc/trafilatura 精细结构） |
| 其余（简单 HTML，以标题/段落为主） | L0（快速档） |

### 门B · 后端探测与选择（scripts/detect_backends.py）

```bash
python scripts/detect_backends.py --grade <L0|L1> --json
```

探测五后端本地可用性（import 与 CLI 双探测）：`markitdown / html2text / beautifulsoup4 / pandoc / trafilatura`。决策规则：等级建议 × 本地可用性 → 选定后端 + 降级链；全缺失 → 输出安装指引并停在预检报告态。

**两档分级策略**（完整矩阵含安装命令/许可证/已验证命令见 `references/backends.md`，grep 模式：`L0|L1`）：

| 档位 | 适用 | 首选 | 降级 | 预期质量 |
|---|---|---|---|---|
| L0 快速 | 简单 HTML、大批量 | markitdown | html2text → beautifulsoup4 | 文本优，表格/结构有限 |
| L1 标准 | 复杂 HTML、表格/嵌套结构、学术/文档导出 | pandoc | trafilatura → L0 链 | 结构优，表格/标题层级完整 |

> **无 L2/L3 档**：HTML 本身含语义结构（标题/表格/链接标签），不需要 OCR 档（L2）或 LLM 兜底（L3）——这是与 tri-pdf2md 的关键差异。

### 门C · 转换执行（本 skill 指导，后端干活）

1. 按选定后端的官方命令执行（命令模板见 `references/backends.md` §已验证命令，grep 模式：`命令`）；优先开启后端保留结构的能力（pandoc `-f html -t gfm`、markitdown 默认结构保留、trafilatura 提取正文）。
2. 产出 `<同名>.md` + `assets/` 图片资产；后端输出含图片时 MUST 保留相对引用并校验资产落盘。
3. 后处理：清理 script/style 残留、统一图片相对路径、校验 MD 语法（表格列对齐/代码块闭合）、保留标题层级树（NEVER 压平为纯段落）。
4. 失败或超时 → **MUST 调用 `python scripts/convert_pipeline.py --doc <路径> --md <同名>.md --chain "<selected>,<fallback_chain>" --json` 一次性代码化执行降级链（M1，NEVER Agent 手工逐后端重试）**；输出 JSON 的 `backend_used`/`attempts`（逐后端异常聚合）MUST 写入门D 报告「降级轨迹」字段；退出码 3（全后端失败）时向用户输出聚合诊断并停止。
5. **深嵌套爆栈降级（M4）**：markitdown/html2text/bs4 runner 遇 `RecursionError` → 自动平文本提取兜底（弃结构保内容），输出 JSON `meta.fallback="get_text_plain"`；该字段 MUST 写入门D 报告且**产物置信度强制 ≤B**，复核项必列「HTML 过深，仅保文本结构丢失」。
6. **编码探测留痕（M9）**：文本后端统一经 `scripts/sniffer.py` detect_charset 解码，输出 JSON `meta.charset_detected` 记录探测编码，MUST 写入门D 报告转换元数据。

### 门D · 质量校验与报告（scripts/quality_check.py · 用户硬要求）

```bash
python scripts/quality_check.py --html <路径> --md <路径> [--report-dir <目录>] --json
```

**校验指标**（全部确定性计算，NEVER 目测）：

| 指标 | 定义 | 算法 |
|---|---|---|
| **文本召回率** | HTML 可见文本被 MD 覆盖的比例 | 归一化后字符 bigram 集合覆盖率（中文/英文自适应） |
| **丢失率** | 1 − 文本召回率 | 同上 |
| 噪声率 | MD 有而 HTML 无的比例（脚本残留/幻觉信号） | 反向 bigram 覆盖率 |
| 结构对比 | 标题 h1-h6/表格/图片/链接：HTML 侧计数 vs MD 侧计数 | html.parser 计数 vs MD 语法计数 |
| 异常清单 | 乱码（U+FFFD）/脚本内容误入正文/空输出/代码块围栏不成对 | 正则 + 启发式 |

**质量四维 LLM 抽评（可选 · 默认关闭 · P2-1）**：completeness / structure / formatting / cleanliness 四维盲评（LLM-judge 双 swap），方法论唯一真源 `references/fidelity-spec.md` §质量四维抽评。启用属付费确认场景（总则②）：MUST 用户二次确认，NEVER 默认或自动调用；基准引用一律标注来源。默认仅交付确定性指标。

**置信度分级**（阈值唯一真源 `references/fidelity-spec.md`，grep 模式：`置信度`）：

| 置信度 | 判定 | 处置 |
|---|---|---|
| **A 直接可用** | 文本召回率 ≥95% 且结构计数吻合 | 交付，报告标注 |
| **B 抽查复核** | 文本召回率 85–95% 或结构部分缺失 | 交付 + 列出复核项 |
| **C 强制人工复核** | 文本召回率 <85%，或检出乱码/脚本误入正文/空输出，或召回率无法计算 | 交付 + 醒目警示 + 建议升级档位重转 |

**report.md 关键数据段（固定结构，NEVER 省略）**：文本召回率、丢失率、噪声率、结构对比表、置信度等级与原因、转换元数据（后端/档位/文件大小/耗时/资产数/降级轨迹）、异常清单、固定复核项清单。HTML 无可见文本时召回率标注「不适用（无可见文本）」并降为 C 级口径。

### 可扩展性

1. **新增后端**：在 `references/backends.md` 矩阵追加一行 + `detect_backends.py` 的 `BACKENDS` 表追加探测项，零改流程。
2. **调整档位阈值**：只改 `preflight.py` 顶部常量（表格/资源/大小阈值等）。
3. **调整保真度阈值**：只改 `references/fidelity-spec.md`（单一事实源）。
4. **新增质量指标**：在 `quality_check.py` 追加计算函数 + 报告模板加一行。

---

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：本 skill 内部 `references/version-check-spec.md`（不依赖任何外部上游 skill）。**可执行实现**：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

**执行方式（MUST）**：运行 `python scripts/check_update.py --slug tri-html2md --json`，解析 `state` 字段——`A`/`B`/`C`/`D` 一律放行并标注口径，`BLOCK`（退出码 ≥20）绝对禁止执行并按 `block_code` 输出恢复指引。退出码 `<20` 放行；脚本自身异常兜底降级放行，NEVER 因版本门故障阻断启动。四态判定、升级流程、节流缓存细则均在 `references/version-check-spec.md`，本章节 NEVER 内联。

---

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 门A → 门B → 门C → 门D → 交付。版本检查未通过前 NEVER 进入以下任一步骤。

1. **入口分流**：声明自检句 → 模式 A 读快照 §三 / 模式 C 自构造输入；提取 HTML 路径、输出期望。
2. **门A 预检**：运行 `preflight.py`；BLOCK（编码不可解/非 HTML）则停止并提示；取得等级建议与风险项。
3. **门B 探测**：运行 `detect_backends.py`；向用户报告「等级建议 + 本地可用后端 + 选定方案」；L1 后端缺失且需要 L1 时给出安装命令，经同意后安装并复测。
4. **门C 转换执行**：按选定后端官方命令执行 → 产出 MD + assets → 后处理（script/style 残留/图片路径/MD 语法/保留标题树）→ 失败经 scripts/convert_pipeline.py 代码化执行降级链（M1）。
5. **门D 校验**：运行 `quality_check.py` → 产出 report.md（含文本召回率/丢失率等关键数据段）；C 级时向用户醒目警示并给出升级重转选项。
6. **交付**：`<同名>.md + assets/ + report.md` 落输出目录（默认 `.tribro/html2md/<命名>/`）；回显产物路径与置信度结论。
7. **链路落盘**：本次转换的过程数据（预检 JSON/探测 JSON/质量 JSON）落 `.tribro/html2md/<命名>/` 供追溯。

---

## 交付产物

| 产物 | 文件名 | 内容 | 审批门 |
|------|--------|------|--------|
| Markdown 正文 | `<同名>.md` | 转换结果（含图片相对引用、保留标题树） | 门D 校验后 |
| 图片资产 | `assets/` | 提取的图片 + 引用对应 | 与正文同步 |
| 质量报告 | `report.md` | 文本召回率/丢失率/结构对比/置信度/复核项/异常清单 | 门D（MUST，NEVER 省略） |
| 过程数据 | `.tribro/html2md/<命名>/*.json` | 预检/探测/质量三份 JSON（追溯用） | 自动 |

---

## 质量标准

| 维度 | 标准 | 验证方式 |
|------|------|----------|
| 报告完整性 | report.md 含文本召回率/丢失率/结构对比/置信度/元数据/异常/复核项全段 | `quality_check.py` 输出核对 |
| 保真度诚实 | 召回率不可计算时显式「不适用」，NEVER 编造数值 | 报告字段校验 |
| 图片引用一致 | MD 图片引用与 assets/ 文件一一对应 | 计数比对 |
| 降级完整 | 后端失败必留降级轨迹，全缺失停在预检态 | 过程 JSON 核对 |
| 结构保留 | 标题层级非空、表格语法闭合、代码块闭合、script/style 无残留 | MD 语法检查 |
| 编码正确 | 中文无乱码（U+FFFD/锟斤拷 计数为 0） | `quality_check.py` 异常清单 |
| 边界恪守 | 不猜测解码、不擅自装重依赖、不擅自调付费 API | 流程审查 |
| 版本联动 | SKILL.md / CHANGELOG / tests 三处版本一致 | 发布前核对 |

---

## 落盘规则

- 本 skill 为 tri-forge 生成物，包落盘于 `.tribro/skills/tri-html2md/`（安装后经 junction 同步平台）。
- 用户成果物（`<同名>.md + assets/ + report.md`）落 `.tribro/html2md/<命名>/`——全部产物统一落盘至 `.tribro/`。
- 过程数据（预检/探测/质量 JSON）落 `.tribro/html2md/<命名>/`（命名沿用家族规范 `HTML2MD_<日期>_<时间>_<会话ID>`）。
- 全程不生成 LICENSE / .gitignore。

---

## 目录结构

```
tri-html2md/
├── SKILL.md                       主入口：契约 + 四阶段管道 + 保真度契约 + 代码版权合规
├── README.md                      特性/目录/安装/使用/测试/设计原则
├── CHANGELOG.md                   Keep a Changelog + SemVer
├── _meta.json                     平台元数据
├── references/
│   ├── backends.md                后端矩阵（能力/安装/许可证/已验证命令 · grep 索引）
│   ├── fidelity-spec.md           保真度分级规范（阈值唯一真源 + 复核项清单）
│   └── version-check-spec.md      版本检查与更新规范（内部唯一真源）
├── scripts/
│   ├── preflight.py               门A：预检分级（编码/合法性/复杂度/等级建议 + 输入规模守卫）
│   ├── detect_backends.py         门B：五后端探测与档位决策（含降级链）
│   ├── postprocess.py             门C：转换后处理（两遍锚点保护/实体解码/围栏感知清理）
│   ├── convert_pipeline.py        门C：降级链执行器（M1：逐后端 attempts 异常聚合 + 聚合诊断 + M4 降级/meta 钩子，自包含副本）
│   ├── md_table.py                M8：自产表转义（竖线转义/换行折空格/列对齐，家族同源副本）
│   ├── sniffer.py                 M9：内容真身二次校验 + charset 嗅探（家族同源副本）
│   ├── _io_safe.py                输出编码兜底（M2：GBK 控制台 safe_print，家族同源副本）
│   ├── quality_check.py           门D：文本召回率/丢失率/结构对比/异常/报告生成
│   ├── scale_guard.py             门A 输入规模守卫（anydoc limits.rs 口径 · P2-2）
│   └── check_update.py            版本检查与更新（家族同源）
└── tests/
    ├── tri-html2md-full-testcases.md  全场景全能力测试用例（审计版）
    ├── mutation_smoke.py          变异冒烟测试（确定性变异 × N 轮 · P2-3）
    └── samples/                   真实格式样本 ×1（综合真实格式样本）
```

### 运行时落盘结构（`.tribro/html2md/`）

```
.tribro/html2md/<命名>/
├── preflight.json     门A 预检输出（等级建议 + 风险项）
├── backends.json      门B 探测输出（可用后端 + 降级链）
└── quality.json       门D 质量输出（指标 + 置信度）
```

---

## 进化契约

> 本 skill 生成物自带进化契约（compliance #23）——如何接收反馈、沉淀经验、自我修订：

- **反馈接收点**：用户对 report.md 复核项的回填与投诉（「这页表格丢了」「这个链接失效了」「中文乱码了」）写入 `.tribro/html2md/feedback/`；每次 C 级报告自动视为一条改进信号。
- **经验沉淀位**：后端版本漂移（CLI 参数变更）、新后端出现、编码探测失败案例沉淀入 `.tribro/html2md/lessons.md`；规范修订回写 `references/backends.md` 与 `references/fidelity-spec.md`。
- **自我修订触发条件**：① 同类 HTML 连续 ≥3 次 C 级 → 修订档位判定阈值或首选后端；② 后端能力排名显著变化 → 修订 `references/backends.md` 矩阵；③ 新高质量开源后端出现（社区 Stars/维护活跃双高）→ 评估纳入矩阵并更新 `detect_backends.py` 的 `BACKENDS` 表；④ 编码探测连续失败（同一编码误判）→ 修订 `preflight.py` 候选编码表。
- **质量闭环归属**：本 skill 负责「转换 + 度量 + 报告」，复核与采信由用户执行；report.md 的复核项回填是下一次转换阈值调优的输入。

---

## 代码版权与许可证合规（硬红线）

- 本 skill 只**编排调用**后端官方 CLI / Python API，NEVER 复制、改写或内嵌任何后端源码。
- 后端许可证口径（MIT：markitdown/html2text/beautifulsoup4；GPL-2.0：pandoc（CLI）；Apache-2.0：trafilatura）见 `references/backends.md` §许可证——GPL 后端（pandoc）以「外部 CLI 调用、不分发其代码」方式使用；用户对许可证敏感时引导改用 MIT/Apache 后端（markitdown/html2text/beautifulsoup4/trafilatura）。
- 报告与文档引用基准数据 MUST 标注来源与版本，NEVER 混用口径。
