---
name: PPT 转 Markdown
slug: tri-pptx2md
version: 1.4.5
displayName: PPT 转 Markdown
description: 专门用于 PowerPoint/WPS 演示文稿（.pptx/.pptm/.pps/.pot/.ppsx/.ppsm/.ppt 同族七扩展名）高质量转 Markdown 的编排与质量保障 skill——预检分级（文件类型魔数判定/页数/备注/图片计数/旧格式标记）、多后端探测与编排（anydoc 全族直读首选 + python-pptx/markitdown/pandoc/LibreOffice 降级链）、结构降维转换（每页 Slide 块 + 标题/正文/备注/图片引用）、质量校验与保真度分级报告（页覆盖率/文本召回率/丢失率/结构对比/置信度 A/B/C）；定位是编排与质量保障层，不自研 PPT 解析/渲染引擎，复用成熟后端；支持独立安装，含上游依赖检测三态逻辑（快照模式/引导安装/降级模式）。
summary: 四门管道（预检分级→后端探测→结构降维转换→质量校验）+ 四档降级链 + 可验证分级保真契约 + 「PPT 视为有时效、有结构的数据源」硬编码锚点——把「无损」落为页覆盖率/文本召回率可计算、置信度可分级、每页 Slide 块可追溯的质量报告。
tags: [tri, ppt, pptx, pptm, pps, pot, ppsx, ppsm, markdown, conversion, fidelity, quality-report, orchestration, wps, anydoc]
license: MIT
---

# PPT 转 Markdown

> 本 skill 是 tri-intent 的**下游 skill（读取快照直接执行，绝不重识别意图）**，也可完全独立运行（直接给定 PPT 路径）。执行路径：门A 预检分级 → 门B 后端探测 → 门C 结构降维转换 → 门D 质量校验与报告，交付 `<同名>.md + assets/ + report.md`。
>
> **诚实声明（铁律）**：PPT 是面向演示的排版容器，动画/过渡/母版/精确排版是「表现层」，转 MD 时**必然丢失**；图表/SmartArt 只能以图片资产保留，不能转成正文。PPT→MD 本质是**结构降维而非格式复制**。本 skill 承诺的是「可验证的分级保真」（页覆盖率/文本召回率可计算、置信度 A/B/C 可分级），NEVER 承诺绝对无损。**绝不半成品交付（P2-4）**：降级链用尽仍有内容缺失时，MUST 在 report.md 标注「部分转换」并列出缺失页清单，NEVER 以完整姿态交付半成品；转换不可能完成时 MUST 输出类型化失败（对齐 anydoc「错误=完全不可能产出」），NEVER 静默吞错。
>
> **数据源观（用户硬要求 · 总纲）**：PPT 被视为**有时效、有结构的数据源**——版本（时效）与页序（空间）锚点由框架硬编码写入每个产物，全链路可控，NEVER 依赖模型自觉补元数据。

**用户心智**：你有一份 PPT（汇报/培训/方案/课件，可能是 .pptx 也可能是老 .ppt，可能是 WPS 生成的），想要一份结构正确、图片备注齐全、且**知道自己丢了什么**的 Markdown。本 skill 像一个质检车间：先体检（这是什么格式？多少页？有备注吗？图多吗？），再选刀（哪个后端最适合？本地装了什么？），干完活必须交验（页覆盖多少？文本召回多少？丢了哪些？哪些地方必须人工复核？）。

---

## 强制执行契约（Execution Contract · 最高优先级）

> 本契约优先级高于 Agent 通用默认行为。用户明确要求「PPT 转 MD / 转成 Markdown / pptx2md / 把这份 PPT 转成 md」或经 tri-intent 路由（`L2=I08` 且 `L3_子意图=pptx2md`，快照下游路由建议指向本 skill）即视为激活，不得仅当参考文档。

- 0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（运行 `scripts/check_update.py`，按 `references/version-check-spec.md` 四态判定处置；非最新版自动升级，升级通道不可用则标注态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。
- 1. **强制前置**：独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式；经快照激活时 MUST 先读取快照 §三（尤其 `L3_子意图=pptx2md`、`任务要点`）。
- 2. **预检分级强制（门A）**：MUST 先运行 `scripts/preflight.py` 取得确定性预检 JSON（文件类型/页数/备注/图片计数/旧格式标记/等级建议），NEVER 凭肉眼或猜测跳级。非 PPT 文件（魔数不匹配）MUST 停止并提示。
- 3. **后端探测强制（门B）**：MUST 运行 `scripts/detect_backends.py` 取得本地后端可用性 JSON，按「等级建议 × 本地可用性」选定后端与降级链；NEVER 调用未探测到的后端。缺失后端 MUST 给出精确安装命令并经用户同意后安装，NEVER 擅自安装依赖。
- 4. **编排不重造铁律**：本 skill 是编排与质量保障层，MUST 复用成熟后端官方 CLI/API 完成转换，NEVER 自研 PPT 解析/渲染引擎，NEVER 复制后端源码进本 skill（详见 §代码版权与许可证合规）；MIT 许可证后端的设计模式级迁移允许，MUST 在迁移文件头部保留归属声明（如 `Adapted from Microsoft markitdown, MIT`）——2026-09-09 用户裁决（迁移报告待定点①）。
- 5. **质量报告强制（门D · 用户硬要求）**：转换完成后 MUST 运行 `scripts/quality_check.py` 产出 report.md，报告 MUST 以醒目数据段告知用户**页覆盖率、文本召回率、丢失率**等关键数据（结构对比、置信度等级、转换元数据、异常清单），NEVER 只交 MD 不交账。
- 6. **降级链强制**：选定档位后端执行失败或质量为 C 级且用户要求重转时，MUST 沿降级链重试（.pptx：L1→L0；.ppt/.pps/.pot：anydoc 直读首选，anydoc 缺失时 LibreOffice 转换后走标准链）；全缺失时 MUST 输出安装指引并停在预检报告态，NEVER 空手交付。
- 7. **L3 LLM 兜底须确认**：涉及付费 LLM 视觉 API 或商业 API 时，MUST 先向用户说明成本与数据外发风险并取得确认，NEVER 未经确认调用。
- 8. **图表处置（2026-09-08 MUST 化，P1-4）**：门B 探测 anydoc 可用且格式命中 → MUST 文本化提取（题注加粗段 + 类别×系列缓存数据表；SmartArt 文本点），图片资产并行保留；anydoc 不可用 → MUST 回退图片资产提取（`assets/` + 页内引用）并记录降级轨迹。NEVER 由 Agent 现场裁量二选一——模式由探测 JSON + 本契约决定。转换后 MUST 校验 MD 内图片引用与资产文件一一对应（anydoc 主链经 dump_assets.py 资产清单段对应）。
- 9. **复核项永不消失**：report.md MUST 固定列出复核项清单（演讲者备注丢失/SmartArt 与图表转图片/母版占位符/.ppt 旧格式兼容/页内多文本框阅读顺序），NEVER 因置信度为 A 而省略。
- 10. **自检句**：作答前 MUST 声明「本次意图=I08（L3=pptx2md），已读取快照=<是/否>，预检等级=<L0/L1/PPT>，选定后端=<slug>，保真度=<A/B/C/待检>」；与预检/探测结果冲突时 MUST 停止并纠正。
- 11. **旧格式路径（2026-09-08 定案）**：anydoc 可用时 `.ppt/.pps/.pot` MUST 直读（自研二进制记录流解析器，NEVER 强制中转）；anydoc 缺失时才降级 LibreOffice headless 转中间 `.pptx` 再走标准链，NEVER 直接尝试用 python-pptx 解析 `.ppt`（不支持）。模式由 `detect_backends.py` 探测 JSON 决定，NEVER Agent 现场裁量。
- 12. **页序锚点铁律（用户硬要求）**：每个 Slide 块 MUST 带页序锚点（`## Slide N`），文档级 MUST 带版本元数据（缺省取 PPT 修改时间 + 页数指纹，可 `--doc-version` 覆盖）——PPT 是**有时效、有结构的数据源**，锚点由框架硬编码写入，NEVER 依赖模型自觉补全。
- 13. **不支持格式优雅跳过（家族统一 · 用户指令 2026-09-08）**：输入为 .odt/.ods/.odp/.rtf/.epub（tri-xx2md 家族统一不支持格式，含内容为此类格式的误标 zip/RTF 文件）时，门A preflight MUST 输出 `status=SKIP`（reason_code=unsupported_format，退出码 0），本 skill MUST 明确告知用户「无法转换」并列出支持格式与替代建议后跳过结束，NEVER 尝试强行转换，NEVER 报错中断。

---

## 触发时机

- **主触发（独立运行）**：用户明确要求「把 xxx.pptx/.ppt 转成 Markdown」「PPT 转 MD」「pptx2md」且对象是演示文稿文件（.pptx/.ppt，含 WPS 生成）。
- **次触发（tri-intent 接入）**：上游 tri-intent 产出快照，`L2=I08 翻译转换` 且 `L3_子意图=pptx2md`，`下游路由建议=tri-pptx2md`——读取快照 §三 后按本契约执行。
- 任一触发成立即激活。PPT 的其它操作（合并/拆分/模板编辑/放映）不归本 skill，见 §职责边界。

---

## 上游依赖检测（独立使用时 · 三态）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟）且下游路由建议指向本 skill | 读取快照 §三（任务要点/输入文件/输出期望），按四门管道执行（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | MUST 提示用户「本次请求尚未经意图识别」，引导先经 tri-intent 产出快照；NEVER 按空上下文静默执行 |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户明确拒绝安装 | 从用户请求自构造等价输入（意图判定默认 I08/L3=pptx2md + PPT 路径 + 输出期望），声明降级模式后按四门管道执行，生成的报告标注「未经意图识别」 |

**模式 B 提示语**：

> 本 skill 依赖 tri-intent 进行意图识别与输入校验。当前未检测到 tri-intent。
> 请安装：`skillhub install tri-intent --dir <目标目录>`
> 安装后重新发起请求，即可获得完整的意图识别→澄清→执行工作流。

**模式 C 降级声明**：

> 用户明确拒绝安装后，从用户请求自构造等价输入（意图判定 I08/L3=pptx2md + PPT 路径 + 输出期望），声明「当前为降级模式，意图识别精度低于完整工作流，转换质量不受影响但路由归属需人工复核」。

> **对称双向检测**：本 skill 检上游 tri-intent；tri-intent 亦在路由映射表登记本 skill 为 I08·pptx2md 子类下游（一跳覆写），未安装时会提示安装。任一端缺失都被发现。

---

## 输入契约

| 来源 | 字段 | 用途 |
|------|------|------|
| 快照 §三（模式 A） | `任务要点` / `一句话复述` | 提取 PPT 路径、输出目录、质量期望（是否要求备注/图片精细） |
| 用户直调（模式 C） | PPT 文件路径 | 转换对象；MUST 存在且可读 |
| 用户直调（可选） | 输出目录 | 默认 `.tribro/pptx2md/<命名>/`；assets/ 与 report.md 同级 |
| 用户直调（可选） | 档位偏好 `--grade` | 强制指定 L0/L1/PPT；缺省由门A 自动建议 |
| 用户直调（可选） | 文档版本标识 `--doc-version` | 时效元数据（缺省：PPT 修改时间 + 页数指纹自动生成） |
| `references/backends.md` | 后端矩阵 | 门B/门C 选择与命令参考（grep 模式：后端名） |
| `references/fidelity-spec.md` | 保真度阈值 | 门D 分级判定（grep 模式：置信度） |

> 输入 PPT 为目录时 NEVER 批量静默转换，MUST 先列清单与用户确认范围。

---

## 职责边界

- **本 skill 负责**：PPT→MD 的预检分级、后端探测与编排、结构降维转换指导（每页 Slide 块 + 标题/正文/备注/图片引用）、质量校验与保真度分级报告、图片资产提取与引用校验。
- **不负责**：PPT 合并/拆分/模板编辑/放映/加密（归环境内置 pptx skill）；语言翻译（归 tri-content/tri-translate）；MD 之外的格式转换（归 tri-content）；意图识别（归 tri-intent）。
- **与 tri-content（I08 默认下游）的边界**：I08 的语言翻译与其它格式转换仍路由 tri-content；仅「PPT→MD」语义命中 `L3_子意图=pptx2md` 时一跳覆写到本 skill。一个 L2（I08）对应一个一跳下游，仅由 L3 区分——与 I06 article→tri-article、I08 pdf2md→tri-pdf2md 同构。
- **与 tri-pdf2md 的边界**：无重叠。tri-pdf2md 处理 PDF→MD；本 skill 处理 PPT→MD。两者同为 I08 的 L3 子类下游，互不冲突。
- **与环境内置 pptx skill 的边界**：内置 pptx skill 做 PPT 文档操作（创建/编辑/模板）；本 skill 只做「PPT→Markdown 格式转换 + 质量报告」这一件事。
- **不支持格式（家族统一）**：.odt/.ods/.odp/.rtf/.epub 五种格式为 tri-xx2md 家族统一不支持范围，preflight 命中即明确提示无法转换并跳过（status=SKIP），NEVER 强行处理，NEVER 报错中断。
- **不触发场景（Not-Trigger）**：本 skill 不接手「PPT 合并/拆分/模板编辑/放映/加密」（归环境内置 pptx skill）；不接手「语言翻译」（归 tri-content/tri-translate）；不接手「MD 之外的格式转换」（归 tri-content）；不接手「意图识别」（归 tri-intent）。

---

## 四门管道方法论（核心能力 · 可扩展）

> 「先体检、再选刀、干完活、必须交验」。四门中门A/门B/门D 是确定性脚本（约束：算法下沉），门C 由本 skill 指导 Agent 调用后端官方命令。

### 门A · 预检分级（scripts/preflight.py）

```bash
python scripts/preflight.py --ppt <路径> --json
```

> **输入规模守卫（P2-2）**：preflight 内置 `scripts/scale_guard.py`（anydoc limits.rs 口径：条目数 100k / 总解压 512MiB / 单条目 128MiB，刻意不可配置）。硬上限超限 → BLOCK（ResourceLimit=完全不可能产出语义）。守卫明细见预检 JSON `scale_guard` 字段。

> **内容真身二次校验（M9）**：preflight 输出含 `content_check` 字段（`scripts/sniffer.py` 按扩展名映射校验族：.pptx/.pptm/.ppsx/.ppsm 验 zip 内 `ppt/presentation.xml`、.ppt/.pps/.pot 验 OLE CFB 签名∪OPC 并集）。`match=false` → BLOCK「扩展名与内容不符」。

检测项：文件类型魔数判定（.pptx=PK zip 头 / .ppt=OLE 复合文档头 D0CF11E0）/ 页数（slide 数，zipfile 探测 ppt/slides/*.xml）/ 备注存在性（ppt/notesSlides/）/ 图片计数（ppt/media/）/ 旧格式标记。输出等级建议：

| 判定 | 等级建议 |
|---|---|
| 魔数既非 PK 也非 D0CF11E0 | BLOCK——非 PPT 文件，提示后停止 |
| .pptx + 版式简单（纯文本为主） | L0（快速档） |
| .pptx + 复杂版式（图表/大量图片/备注密集） | L1（标准档） |
| .ppt/.pps/.pot（OLE 旧格式） | PPT（anydoc 直读首选；anydoc 缺失时 LibreOffice 转中间 .pptx 再走标准链） |

### 门B · 后端探测与选择（scripts/detect_backends.py）

```bash
python scripts/detect_backends.py --grade <L0|L1|PPT> --json
```

探测五后端本地可用性（import 与 CLI 双探测，anydoc 为 dual 型双通道首选）：`anydoc / python-pptx / markitdown / pandoc / libreoffice`。决策规则：等级建议 × 本地可用性 → 选定后端 + 降级链（探测 JSON 决定，NEVER Agent 另选）；`.ppt/.pps/.pot` 旧格式 anydoc 可用时直读；全缺失 → 输出安装指引并停在预检报告态。

**四档分级策略**（完整矩阵含安装命令/许可证见 `references/backends.md`，grep 模式：`L0|L1|PPT`）：

| 档位 | 适用 | 首选 | 降级 | 预期质量 |
|---|---|---|---|---|
| L0 快速 | .pptx/.pptm/.ppsx/.ppsm 全场景 | anydoc | python-pptx（仅 .pptx/.pptm）→ markitdown | 图表/SmartArt 文本化 + 备注保留（基准 per-format 第一） |
| L1 标准 | anydoc 缺失时的 .pptx 复杂版式/图表 | pandoc | python-pptx → markitdown | 结构更完整，图表转图片 |
| PPT 旧格式 | .ppt/.pps/.pot（二进制记录流） | anydoc 直读 | LibreOffice headless 转 .pptx 中间格式 → L0/L1 链（anydoc 缺失时） | 直读免中转（基准 .ppt 80） |
| L3 兜底 | 后端全失败或用户极致要求 | LLM 视觉 API | 商业 API | 不稳定且付费，须用户确认 |

### 门C · 结构降维转换（本 skill 指导，后端干活）

> 用户硬要求：PPT→MD 是「结构降维」——动画/过渡/母版/精确排版必然丢失，图表以图片资产保留。转换不是「抽文本」而是「重建每页结构」。

1. 按选定后端的官方命令执行（命令模板见 `references/backends.md` §已验证命令，grep 模式：`命令`）：anydoc 主链直转 GFM（演讲者备注自动保留；图表/SmartArt 文本化按契约 #8 MUST 化执行）；markitdown/python-pptx/pandoc 走既有链（M7 裁决：降级链 markitdown 优先于 python-pptx）。
2. 产出 `<同名>.md`，**每张 slide 一个 `## Slide N` 二级标题块**（标题 + 正文要点 + 备注 + 图片引用），图片提取为 `assets/`；演讲者备注保留为引用块（`> 备注：…`）。**anydoc 主链资产契约**：anydoc 的图片 bytes 在文档模型（MD 不输出 `![]()` 引用），MUST 运行 `python scripts/dump_assets.py --doc <file> --md <同名>.md` 落盘 `assets/` 并追加资产清单段（P0-4 唯一路径）。
3. 后处理：统一图片相对路径、校验 MD 语法（列表/引用块闭合）、保留页序（NEVER 打乱 Slide 顺序）。
4. 失败或超时 → **MUST 调用 `python scripts/convert_pipeline.py --doc <路径> --md <同名>.md --chain "<selected>,<fallback_chain>" --json` 一次性代码化执行降级链（M1，NEVER Agent 手工逐后端重试）**；输出 JSON 的 `backend_used`/`attempts`（逐后端异常聚合）MUST 写入门D 报告「降级轨迹」字段；退出码 3（全后端失败）时向用户输出聚合诊断并停止。

### 门D · 质量校验与报告（scripts/quality_check.py · 用户硬要求）

```bash
python scripts/quality_check.py --ppt <路径> --md <路径> [--report-dir <目录>] --json
```

**校验指标**（全部确定性计算，NEVER 目测）：

| 指标 | 定义 | 算法 |
|---|---|---|
| **页覆盖率** | 源 slide 数被 MD `## Slide` 块覆盖的比例 | `## Slide N` 块数 / 源 slide 数 |
| **文本召回率（保真率）** | 源提取文本被 MD 覆盖的比例 | 归一化（NFKC 折叠后保留字母/数字/CJK）后**逐页**字符 bigram 集合覆盖率（逐页切分避免跨页伪词），中文/英文自适应 |
| **丢失率** | 1 − 文本召回率；附缺页明细 | 同上，按页统计 |
| 结构对比 | 每页文本/图片/备注：PPT 侧计数 vs MD 侧计数 | python-pptx/zipfile 计数 vs MD 语法计数 |
| 异常清单 | 乱码（U+FFFD）/空输出/缺页（源有而 MD 无的 Slide） | 正则 + 长度启发式 |

**质量四维 LLM 抽评（可选 · 默认关闭 · P2-1）**：completeness / structure / formatting / cleanliness 四维盲评（LLM-judge 双 swap），方法论唯一真源 `references/fidelity-spec.md` §质量四维抽评。启用属付费确认场景（总则②）：MUST 用户二次确认，NEVER 默认或自动调用；基准引用一律标注来源。默认仅交付确定性指标。

**置信度分级**（阈值唯一真源 `references/fidelity-spec.md`，grep 模式：`置信度`）：

| 置信度 | 判定 | 处置 |
|---|---|---|
| **A 直接可用** | 页覆盖 100% 且文本召回 ≥95% | 交付，报告标注 |
| **B 抽查复核** | 页覆盖 ≥90%（且召回 ≥85%），或召回 85–95% 而页覆盖未达 90% | 交付 + 列出复核项 |
| **C 强制人工复核** | 页覆盖 <90% 或召回 <85% 或异常 | 交付 + 醒目警示 + 建议升级档位重转 |

> **判定顺序（v1.4.4）**：召回 <85% 优先判 C，页覆盖达标也不放行——否则一份「页都在但正文大面积缺失」的 MD 会被判成 B。口径唯一真源 `references/fidelity-spec.md` §三。

**report.md 关键数据段（固定结构，NEVER 省略）**：页覆盖率、文本召回率、丢失率、缺页明细、结构对比表、置信度等级与原因、转换元数据（后端/档位/页数/耗时/资产数/降级轨迹）、异常清单、固定复核项清单。

### 可扩展性

1. **新增后端**：在 `references/backends.md` 矩阵追加一行 + `detect_backends.py` 的 `BACKENDS` 表追加探测项，零改流程。
2. **调整档位阈值**：只改 `preflight.py` 顶部常量（复杂版式信号阈值等）。
3. **调整保真度阈值**：只改 `references/fidelity-spec.md`（单一事实源）。
4. **新增质量指标**：在 `quality_check.py` 追加计算函数 + 报告模板加一行。

---

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：本 skill 内部 `references/version-check-spec.md`（不依赖任何外部上游 skill）。**可执行实现**：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

**执行方式（MUST）**：运行 `python scripts/check_update.py --slug tri-pptx2md --json`，解析 `state` 字段——`A`/`B`/`C`/`D` 一律放行并标注口径，`BLOCK`（退出码 ≥20）绝对禁止执行并按 `block_code` 输出恢复指引。退出码 `<20` 放行；脚本自身异常兜底降级放行，NEVER 因版本门故障阻断启动。四态判定、升级流程、节流缓存细则均在 `references/version-check-spec.md`，本章节 NEVER 内联。

---

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 门A → 门B → 门C → 门D → 交付。版本检查未通过前 NEVER 进入以下任一步骤。

1. **入口分流**：声明自检句 → 模式 A 读快照 §三 / 模式 C 自构造输入；提取 PPT 路径、输出期望。
2. **门A 预检**：运行 `preflight.py`；BLOCK（非 PPT 文件）则停止并提示；取得等级建议与风险项。
3. **门B 探测**：运行 `detect_backends.py`；向用户报告「等级建议 + 本地可用后端 + 选定方案」；缺失后端给出安装命令，经同意后安装并复测。
4. **门C 结构降维转换**：按选定后端官方命令执行 → 产出 MD（每页 Slide 块）+ assets → 后处理（图片路径/MD 语法/保留页序）→ 失败经 scripts/convert_pipeline.py 代码化执行降级链（M1）。
5. **门D 校验**：运行 `quality_check.py` → 产出 report.md（含页覆盖率/文本召回率等关键数据段）；C 级时向用户醒目警示并给出升级重转选项。
6. **交付**：`<同名>.md + assets/ + report.md` 落输出目录（默认 `.tribro/pptx2md/<命名>/`）；回显产物路径与置信度结论。
7. **链路落盘**：本次转换的过程数据（预检 JSON/探测 JSON/质量 JSON）落 `.tribro/pptx2md/<命名>/` 供追溯。

---

## 交付产物

| 产物 | 文件名 | 内容 | 审批门 |
|------|--------|------|--------|
| Markdown 正文 | `<同名>.md` | 每页 `## Slide N` 块（标题+正文+备注引用+图片引用） | 门D 校验后 |
| 图片资产 | `assets/` | 提取的图表/图片 + 页内引用对应 | 与正文同步 |
| 质量报告 | `report.md` | 页覆盖率/文本召回率/丢失率/结构对比/置信度/复核项/异常清单 | 门D（MUST，NEVER 省略） |
| 过程数据 | `.tribro/pptx2md/<命名>/*.json` | 预检/探测/质量三份 JSON（追溯用） | 自动 |

---

## 质量标准

| 维度 | 标准 | 验证方式 |
|------|------|----------|
| 报告完整性 | report.md 含页覆盖率/文本召回率/丢失率/结构对比/置信度/元数据/异常/复核项全段 | `quality_check.py` 输出核对 |
| 保真度诚实 | 召回率不可计算时显式「不适用」，NEVER 编造数值 | 报告字段校验 |
| 图片引用一致 | MD 图片引用与 assets/ 文件一一对应 | 计数比对 |
| 降级完整 | 后端失败必留降级轨迹，全缺失停在预检态 | 过程 JSON 核对 |
| 结构保留 | 每页 Slide 块齐全、页序不乱、备注引用块闭合 | MD 语法检查 |
| 页序锚点完整 | 每个 Slide 块带 `## Slide N` 页序锚点；文档级带版本元数据 | `quality_check.py` 输出核对 |
| 边界恪守 | 不破解、不擅自装重依赖、不擅自调付费 API | 流程审查 |
| 版本联动 | SKILL.md / CHANGELOG / tests 三处版本一致 | 发布前核对 |

---

## 落盘规则

- 本 skill 为 tri-forge 生成物，包落盘于 `.tribro/skills/tri-pptx2md/`（安装后经 junction 同步平台）。
- 用户成果物（`<同名>.md + assets/ + report.md`）落 `.tribro/pptx2md/<命名>/`——全部产物统一落盘至 `.tribro/`。
- 过程数据（预检/探测/质量 JSON）落 `.tribro/pptx2md/<命名>/`（命名沿用家族规范 `PPTX2MD_<日期>_<时间>_<会话ID>`）。
- 全程不生成 LICENSE / .gitignore。

---

## 目录结构

```
tri-pptx2md/
├── SKILL.md                       主入口：契约 + 四门管道 + 保真度契约 + 代码版权合规
├── README.md                      特性/目录/安装/使用/测试/设计原则
├── CHANGELOG.md                   Keep a Changelog + SemVer
├── _meta.json                     平台元数据
├── references/
│   ├── backends.md                后端矩阵（能力/安装/许可证/已验证命令 · grep 索引）
│   ├── fidelity-spec.md           保真度分级规范（阈值唯一真源 + 复核项清单）
│   └── version-check-spec.md      版本检查与更新规范（内部唯一真源）
├── scripts/
│   ├── preflight.py               门A：预检分级（文件类型/页数/备注/图片/旧格式 + 输入规模守卫）
│   ├── detect_backends.py         门B：五后端探测与档位决策（anydoc 双通道首选 + 降级链）
│   ├── postprocess.py             门C：转换后处理（两遍锚点保护/实体解码/围栏感知清理）
│   ├── convert_pipeline.py        门C：降级链执行器（M1：逐后端 attempts 异常聚合 + 聚合诊断 + meta 钩子，自包含副本）
│   ├── md_table.py                M8：自产表转义（竖线转义/换行折空格/列对齐，家族同源副本）
│   ├── sniffer.py                 M9：内容真身二次校验 + charset 嗅探（家族同源副本）
│   ├── _io_safe.py                输出编码兜底（M2：GBK 控制台 safe_print，家族同源副本）
│   ├── dump_assets.py             门C：anydoc 资产落盘 assets/ + MD 资产清单段（幂等）
│   ├── quality_check.py           门D：页覆盖率/文本召回率/丢失率/结构对比/异常/报告生成
│   ├── verify_recall.py           门D 召回率口径回归自检（零依赖：跨页粘连/全角/低召回/多写块）
│   ├── scale_guard.py             门A 输入规模守卫（anydoc limits.rs 口径 · P2-2）
│   └── check_update.py            版本检查与更新（家族同源）
└── tests/
    ├── tri-pptx2md-full-testcases.md  全场景全能力测试用例（审计版）
    ├── mutation_smoke.py          变异冒烟测试（确定性变异 × N 轮 · P2-3）
    └── samples/                   真实格式样本 ×8（anydoc fixture 固化）
```

### 运行时落盘结构（`.tribro/pptx2md/`）

```
.tribro/pptx2md/<命名>/
├── preflight.json     门A 预检输出（等级建议 + 风险项）
├── backends.json      门B 探测输出（可用后端 + 降级链）
└── quality.json       门D 质量输出（指标 + 置信度）
```

---

## 进化契约

> 本 skill 生成物自带进化契约（compliance #23）——如何接收反馈、沉淀经验、自我修订：

- **反馈接收点**：用户对 report.md 复核项的回填与投诉（「这页备注丢了」「这个图表没提出来」）写入 `.tribro/pptx2md/feedback/`；每次 C 级报告自动视为一条改进信号。
- **经验沉淀位**：后端版本漂移（CLI 参数变更）、新后端出现、格式兼容问题（WPS 变体/旧 .ppt 变体）沉淀入 `.tribro/pptx2md/lessons.md`；规范修订回写 `references/backends.md` 与 `references/fidelity-spec.md`。
- **自我修订触发条件**：① 同类 PPT 连续 ≥3 次 C 级 → 修订档位判定阈值或首选后端；② 后端能力排名显著变化 → 修订 `references/backends.md` 矩阵；③ 新高质量开源后端出现 → 评估纳入矩阵并更新 `detect_backends.py` 的 `BACKENDS` 表；④ 用户对某类版式（SmartArt/母版占位符）投诉高频 → 修订 `fidelity-spec.md` 复核项清单。
- **质量闭环归属**：本 skill 负责「转换 + 度量 + 报告」，复核与采信由用户执行；report.md 的复核项回填是下一次转换阈值/后端选型调优的输入。

---

## 代码版权与许可证合规（硬红线）

- 本 skill 只**编排调用**后端官方 CLI / Python API，NEVER 复制、改写或内嵌任何后端源码。
- 后端许可证口径（MIT：python-pptx/markitdown；GPL-2.0：pandoc；MPL-2.0：LibreOffice）见 `references/backends.md` §许可证——GPL/MPL 后端以「外部依赖调用、不分发其代码」方式使用；用户对许可证敏感时引导改用 MIT 后端（python-pptx/markitdown）。
- 报告与文档引用基准数据 MUST 标注来源与版本，NEVER 混用口径。
