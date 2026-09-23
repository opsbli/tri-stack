---
name: Word 转 Markdown
slug: tri-docx2md
version: 1.4.5
displayName: Word 转 Markdown
description: 专门用于 Word 文档高质量转 Markdown 的编排与质量保障 skill——预检分级（.docx/.docm/.doc 家族魔数判定、OOXML 加密检测、段落/图片/表格计数）、多后端探测与编排（anydoc 全链首选：.docx/.docm/.doc 直读 + mammoth/markitdown/python-docx/pandoc 降级链 + LibreOffice/antiword 兜底）、结构降维转换（保留标题层级/表格网格不变量/公式 LaTeX/脚注/图片引用）、质量校验与保真度分级报告（保真率/丢失率/结构对比/置信度 A/B/C）；兼容 WPS 生成的 .docx/.docm/.doc；定位是编排与质量保障层，不自研文档解析引擎，复用成熟后端；支持独立安装，含上游依赖检测三态逻辑（快照模式/引导安装/降级模式）。
summary: 四阶段管道（预检分级→后端探测→结构降维转换→质量校验）+ 双档降级链 + .doc 旧格式兼容路径 + 可验证分级保真契约——把「无损」落为保真率/丢失率可计算、置信度可分级、复核项可执行的质量报告。
tags: [tri, docx, docm, doc, word, markdown, conversion, fidelity, quality-report, wps, orchestration, anydoc]
license: MIT
---

# Word 转 Markdown

> 本 skill 是 tri-intent 的**下游 skill（读取快照直接执行，绝不重识别意图）**，也可完全独立运行（直接给定 Word 路径）。执行路径：门A 预检分级 → 门B 后端探测 → 门C 结构降维转换 → 门D 质量校验与报告，交付 `<同名>.md + assets/ + report.md`。
>
> **诚实声明（铁律）**：Word→MD 是「结构降维」——OOXML 内含段落/标题/表格语义可保留，但**批注、修订痕迹、页眉页脚、嵌入对象（OLE）在 Markdown 中必然丢失**。本 skill 承诺的是「可验证的分级保真」（保真率/丢失率可计算、置信度 A/B/C 可分级），NEVER 承诺绝对无损。**绝不半成品交付（P2-4）**：降级链用尽仍有内容缺失时，MUST 在 report.md 标注「部分转换」并列出缺失块清单，NEVER 以完整姿态交付半成品；转换不可能完成时 MUST 输出类型化失败（对齐 anydoc「错误=完全不可能产出」），NEVER 静默吞错。
>
> **数据源观（总纲）**：Word 文档被视为**有结构、有修订语义的数据源**——标题/表格/图片语义由框架硬编码保留与计数，全链路可控，NEVER 依赖模型自觉补结构。

**用户心智**：你有一份 Word（.docx 或旧 .doc，可能是 WPS 生成），想要一份结构正确、表格图片齐全、且**知道自己丢了什么**的 Markdown。本 skill 像一个质检车间：先体检（这是 .docx 还是旧 .doc？加密吗？复杂吗？），再选刀（哪个后端最适合？本地装了什么？），干完活必须交验（保真率多少？丢了哪些？哪些地方必须人工复核？）。

---

## 强制执行契约（Execution Contract · 最高优先级）

> 本契约优先级高于 Agent 通用默认行为。用户明确要求「Word 转 MD / 转成 Markdown / docx2md」或经 tri-intent 路由（`L2=I08` 且 `L3_子意图=docx2md`，快照下游路由建议指向本 skill）即视为激活，不得仅当参考文档。

- 0. **版本检查前置硬门（第零步）**：MUST 先通过 §版本检查与更新机制（运行 `scripts/check_update.py`，按 `references/version-check-spec.md` 四态判定处置；非最新版自动升级，升级通道不可用则标注态降级继续）——此为执行流程第零步，优先于后续所有步骤。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他强制前置条目。
- 1. **强制前置**：独立使用时（未经 tri-intent 路由）MUST 先走 §上游依赖检测 判定模式；经快照激活时 MUST 先读取快照 §三（尤其 `L3_子意图=docx2md`、`任务要点`）。
- 2. **预检分级强制（门A）**：MUST 先运行 `scripts/preflight.py` 取得确定性预检 JSON（文件类型/加密/段落·图片·表格计数/等级建议），NEVER 凭肉眼或猜测跳级。OOXML 加密文档 NEVER 破解，MUST 停止并提示用户合法解密后重试。
- 3. **后端探测强制（门B）**：MUST 运行 `scripts/detect_backends.py` 取得本地后端可用性 JSON，按「等级建议 × 本地可用性」选定后端与降级链；NEVER 调用未探测到的后端。缺失后端 MUST 给出精确安装命令并经用户同意后安装。
- 4. **编排不重造铁律**：本 skill 是编排与质量保障层，MUST 复用成熟后端官方 CLI/API 完成转换，NEVER 自研文档解析引擎，NEVER 复制后端源码进本 skill（详见 §代码版权与许可证合规）；MIT 许可证后端的设计模式级迁移允许，MUST 在迁移文件头部保留归属声明（如 `Adapted from Microsoft markitdown, MIT`）——2026-09-09 用户裁决（迁移报告待定点①）。
- 5. **质量报告强制（门D · 用户硬要求）**：转换完成后 MUST 运行 `scripts/quality_check.py` 产出 report.md，报告 MUST 以醒目数据段告知用户**保真率、丢失率**等关键数据（结构对比、置信度等级、转换元数据、异常清单），NEVER 只交 MD 不交账。源文本不可提取时召回率 MUST 显式标注「不适用」，NEVER 编造数值。
- 6. **降级链强制**：选定档位后端执行失败或质量为 C 级且用户要求重转时，MUST 沿降级链 L1→L0 重试；全缺失时 MUST 输出安装指引并停在预检报告态，NEVER 空手交付。
- 7. **.doc 旧格式强制**：`.doc` 文件 MUST 先经 LibreOffice headless 转 `.docx` 中间格式再走标准链（LibreOffice 缺失时 antiword 纯文本兜底），NEVER 直接对 .doc 调用 .docx 专用后端（mammoth/python-docx/pandoc 均不读 OLE 二进制）。
- 8. **图表处置**：图表 NEVER 试图转成 MD 正文，MUST 提取为 `assets/` 图片资产 + 保留题注引用；转换后 MUST 校验 MD 内图片引用与资产文件一一对应。
- 9. **复核项永不消失**：report.md MUST 固定列出复核项清单（批注与修订丢失/页眉页脚/嵌入对象 OLE/中文字体/.doc 旧格式兼容/表格嵌套），NEVER 因置信度为 A 而省略。
- 10. **自检句**：作答前 MUST 声明「本次意图=I08（L3=docx2md），已读取快照=<是/否>，预检等级=<L0/L1>，选定后端=<slug>，保真度=<A/B/C/待检>」；与预检/探测结果冲突时 MUST 停止并纠正。
- 11. **不支持格式优雅跳过（家族统一 · 用户指令 2026-09-08）**：输入为 .odt/.ods/.odp/.rtf/.epub（tri-xx2md 家族统一不支持格式，含内容为此类格式的误标 zip/RTF 文件）时，门A preflight MUST 输出 `status=SKIP`（reason_code=unsupported_format，退出码 0），本 skill MUST 明确告知用户「无法转换」并列出支持格式与替代建议后跳过结束，NEVER 尝试强行转换，NEVER 报错中断。

---

## 触发时机

- **主触发（独立运行）**：用户明确要求「把 xxx.docx/.doc 转成 Markdown」「Word 转 MD」「docx 转 MD」且对象是 Word 文件（含 WPS 生成的 .docx/.doc）。
- **次触发（tri-intent 接入）**：上游 tri-intent 产出快照，`L2=I08 翻译转换` 且 `L3_子意图=docx2md`，`下游路由建议=tri-docx2md`——读取快照 §三 后按本契约执行。
- 任一触发成立即激活。Word 的其它操作（创建/编辑/批注/修订/合并）不归本 skill，见 §职责边界。

---

## 上游依赖检测（独立使用时 · 三态）

> 本 skill 可独立安装。激活时 MUST 检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟）且下游路由建议指向本 skill | 读取快照 §三（任务要点/输入文件/输出期望），按四阶段管道执行（标准模式） |
| **A0 · 待识别** | 有 `tri-intent/` 但无可用快照（或快照已过期/损坏） | MUST 提示用户「本次请求尚未经意图识别」，引导先经 tri-intent 产出快照；NEVER 按空上下文静默执行 |
| **B · 引导安装** | 以上均不满足 | MUST 向用户提示依赖并引导安装 |
| **C · 降级模式** | 用户明确拒绝安装 | 从用户请求自构造等价输入（意图判定默认 I08/L3=docx2md + Word 路径 + 输出期望），声明降级模式后按四阶段管道执行，生成的报告标注「未经意图识别」 |

**模式 B 提示语**：

> 本 skill 依赖 tri-intent 进行意图识别与输入校验。当前未检测到 tri-intent。
> 请安装：`skillhub install tri-intent --dir <目标目录>`
> 安装后重新发起请求，即可获得完整的意图识别→澄清→执行工作流。

**模式 C 降级声明**：

> 用户明确拒绝安装后，从用户请求自构造等价输入（意图判定 I08/L3=docx2md + Word 路径 + 输出期望），声明「当前为降级模式，意图识别精度低于完整工作流，转换质量不受影响但路由归属需人工复核」。

> **对称双向检测**：本 skill 检上游 tri-intent；tri-intent 亦在路由映射表登记本 skill 为 I08·docx2md 子类下游（一跳覆写），未安装时会提示安装。任一端缺失都被发现。

---

## 输入契约

| 来源 | 字段 | 用途 |
|------|------|------|
| 快照 §三（模式 A） | `任务要点` / `一句话复述` | 提取 Word 路径、输出目录、质量期望（是否要求表格精细/图片完整） |
| 用户直调（模式 C） | Word 文件路径 | 转换对象；MUST 存在且可读 |
| 用户直调（可选） | 输出目录 | 默认 `.tribro/docx2md/<命名>/`；assets/ 与 report.md 同级 |
| 用户直调（可选） | 档位偏好 `--grade` | 强制指定 L0/L1；缺省由门A 自动建议 |
| `references/backends.md` | 后端矩阵 | 门B/门C 选择与命令参考（grep 模式：后端名） |
| `references/fidelity-spec.md` | 保真度阈值 | 门D 分级判定（grep 模式：置信度） |

> 输入 Word 为目录时 NEVER 批量静默转换，MUST 先列清单与用户确认范围。

---

## 职责边界

- **本 skill 负责**：Word→MD 的预检分级、后端探测与编排、结构降维转换指导（保留标题层级/表格/图片引用）、质量校验与保真度分级报告、图片资产提取与引用校验。
- **不负责**：Word 文档创建/编辑/批注/修订/合并（归文档编辑器/内置 docx skill）；语言翻译（归 tri-content/tri-translate）；MD 之外的格式转换（归 tri-content）；意图识别（归 tri-intent）；PDF 转 MD（归 tri-pdf2md）。
- **与 tri-content（I08 默认下游）的边界**：I08 的语言翻译与其它格式转换仍路由 tri-content；仅「Word→MD」语义命中 `L3_子意图=docx2md` 时一跳覆写到本 skill。一个 L2（I08）对应一个一跳下游，仅由 L3 区分——与 I06 article→tri-article 同构。
- **与 tri-pdf2md 的边界**：tri-pdf2md 做 PDF→MD；本 skill 做 Word→MD。同属 I08 下的两个 L3 子类（pdf2md/docx2md），MECE 不重叠。
- **与 tri-translate 的边界**：无重叠。tri-translate 是语言翻译方法论（横向）；本 skill 是格式转换（Word→MD）。
- **与环境内置 docx skill 的边界**：内置 docx skill 做 Word 文档操作；本 skill 只做「Word→Markdown 格式转换 + 质量报告」这一件事。
- **不支持格式（家族统一）**：.odt/.ods/.odp/.rtf/.epub 五种格式为 tri-xx2md 家族统一不支持范围，preflight 命中即明确提示无法转换并跳过（status=SKIP），NEVER 强行处理，NEVER 报错中断。
- **不触发场景（Not-Trigger）**：本 skill 不接手「Word 文档创建/编辑/批注/修订/合并」（归环境内置 docx skill）；不接手「语言翻译」（归 tri-content/tri-translate）；不接手「MD 之外的格式转换」（归 tri-content）；不接手「PDF→MD」（归 tri-pdf2md）；不接手「意图识别」（归 tri-intent）。

---

## 四阶段管道方法论（核心能力 · 可扩展）

> 「先体检、再选刀、干完活、必须交验」。四阶段中门A/门B/门D 是确定性脚本（约束：算法下沉），门C 由本 skill 指导 Agent 调用后端官方命令。

### 门A · 预检分级（scripts/preflight.py）

```bash
python scripts/preflight.py --doc <路径> --json
```

> **输入规模守卫（P2-2）**：preflight 内置 `scripts/scale_guard.py`（anydoc limits.rs 口径：条目数 100k / 总解压 512MiB / 单条目 128MiB / 网格槽位 4M，刻意不可配置）。硬上限超限 → BLOCK（ResourceLimit=完全不可能产出语义）；表格类网格槽位超预算 → 固定走 L1 流式路径。守卫明细见预检 JSON `scale_guard` 字段。

> **内容真身二次校验（M9）**：preflight 输出含 `content_check` 字段（`scripts/sniffer.py` 按扩展名映射校验族：.docx/.docm 验 zip 内 `[Content_Types].xml`、.doc 验 OLE CFB 签名）。`match=false` → BLOCK「扩展名与内容不符」。

检测项：文件类型判定（魔数：docx=PK zip 头 / doc=OLE 复合文档头 D0CF11E0）/ OOXML 加密检测（EncryptionInfo/EncryptedPackage）/ 文件大小 / 段落·图片·表格计数（python-docx 可用时，否则 zipfile 降级）/ 旧格式标记。输出等级建议：

| 判定 | 等级建议 |
|---|---|
| OOXML 加密（检测到加密标记） | BLOCK——提示合法解密后重试，NEVER 破解 |
| 文件类型无法判定（魔数非 Word 格式） | BLOCK——提示确认文件 |
| .doc 旧格式（OLE 复合文档） | L1 起步 + 旧格式标记（anydoc 直读首选；anydoc 缺失时才转 docx 中间格式） |
| .docm（OPC zip，与 .docx 同魔数） | 按 .docx 规则分级（宏不转换，属结构降维预期内） |
| .docx + 复杂版式（表格 ≥5 或图片 ≥10） | L1（标准档） |
| .docx + 版式简单（纯文字为主） | L0（快速档） |

### 门B · 后端探测与选择（scripts/detect_backends.py）

```bash
python scripts/detect_backends.py --grade <L0|L1> [--doc-format] --json
```

探测七后端本地可用性（import 与 CLI 双探测，anydoc 为 dual 型双通道首选）：`anydoc / mammoth / markitdown / python-docx / pandoc / libreoffice / antiword`。决策规则：等级建议 × 本地可用性 → 选定后端 + 降级链（探测 JSON 决定，NEVER Agent 另选）；`.doc` 旧格式在 anydoc 可用时直读（自研 MS-DOC 解析器，`doc_convert.mode=direct`），anydoc 缺失时降级 LibreOffice 转 docx 中间格式（antiword 纯文本兜底）；全缺失 → 输出安装指引并停在预检报告态。

**双档分级策略**（完整矩阵含安装命令/许可证/已验证命令见 `references/backends.md`，grep 模式：`L0|L1|DOC`）：

| 档位 | 适用 | 首选 | 降级 | 预期质量 |
|---|---|---|---|---|
| L0 快速 | .docx/.docm/.doc 全场景（anydoc 直读） | anydoc | mammoth → markitdown → python-docx | 结构/表格/公式/脚注保真最高（基准 per-format 全第一） |
| L1 标准 | anydoc 缺失时的 .docx 复杂版式 | pandoc | L0 链 | 结构完整，表格/图片保真高 |
| DOC 旧格式 | anydoc 缺失时的 .doc 二进制旧格式 | LibreOffice headless（转 docx 中间格式） | antiword（纯文本兜底）→ L0 链 | 需先转中间格式，结构保真取决于转换 |

### 门C · 结构降维转换（本 skill 指导，后端干活）

1. **.doc 旧格式前置**：门B 探测 `doc_convert.mode=direct`（anydoc 可用）→ MUST anydoc 直读，NEVER 中转；`mode=convert`（anydoc 缺失）→ 先运行 LibreOffice headless `soffice --headless --convert-to docx --outdir <中间目录> <file>.doc` 产出中间 .docx 再走标准链；LibreOffice 亦缺失时 antiword 纯文本兜底（无结构，质量 C 级口径）。
2. 按选定后端的官方命令执行（命令模板见 `references/backends.md` §已验证命令，grep 模式：`命令`）：anydoc 直转 GFM（表格网格不变量/公式 LaTeX/脚注/锚点自动保留，图片资产走 dump_assets.py）；mammoth 保留标题层级/表格/图片引用；pandoc 复杂版式（`--extract-media=assets` 提图）。- **M3 预处理修复前置**：选定 mammoth/python-docx 后端时 MUST 先跑 `python scripts/repair_docx.py --doc <file> --output <修复文件> --json`（逐公式 OMML→LaTeX 编排调用 markitdown oMath2Latex + styles/dstrike/zip casing 修复；convert_pipeline 的对应 runner 已自动内置前置，NEVER 手工绕过）。
3. 产出 `<同名>.md` + `assets/` 图片资产；后端产出结构化中间产物时 MUST 保留供门D 复用，NEVER 丢弃。**anydoc 主链资产契约**：anydoc 的图片 bytes 在文档模型（MD 仅渲染 alt），MUST 运行 `python scripts/dump_assets.py --doc <file> --md <同名>.md` 落盘 `assets/` 并重写引用（P0-4 唯一路径）。
4. 后处理：MUST 先运行 `scripts/postprocess.py --md <同名>.md` 做确定性 HTML 标签清理（去 Word 书签锚点 `<a id="…">`/`</a>`/`<span>`/`<div>`/`<o:p>` 等，保留 br/sub/sup/code/img/table 白名单，实体解码 `&amp;`/`&lt;`/`&gt;`，围栏感知合并空行与行尾空白），再清理页眉页脚重复、统一图片相对路径、校验 MD 语法（表格列对齐/代码块闭合）、保留标题层级树与序号（NEVER 压平为纯段落、NEVER 删除有序/无序列表序号）。
5. 失败或超时 → **MUST 调用 `python scripts/convert_pipeline.py --doc <路径> --md <同名>.md --chain "<selected>,<fallback_chain>" --json` 一次性代码化执行降级链（M1，NEVER Agent 手工逐后端重试）**；输出 JSON 的 `backend_used`/`attempts`（逐后端异常聚合）MUST 写入门D 报告「降级轨迹」字段；退出码 3（全后端失败）时向用户输出聚合诊断并停止。

### 门D · 质量校验与报告（scripts/quality_check.py · 用户硬要求）

```bash
python scripts/quality_check.py --doc <路径> --md <路径> [--report-dir <目录>] --json
```

**校验指标**（全部确定性计算，NEVER 目测）：

| 指标 | 定义 | 算法 |
|---|---|---|
| **保真率（文本召回率）** | 源文档提取文本被 MD 覆盖的比例 | 归一化后字符 bigram 集合覆盖率（中文/英文自适应） |
| **丢失率** | 1 − 保真率 | 同上 |
| 噪声率 | MD 有而源文档无的比例（幻觉/冗余信号） | 反向 bigram 覆盖率 |
| 结构对比 | 标题/表格/图片：源侧计数 vs MD 侧计数 | python-docx/mammoth/zipfile 计数 vs MD 语法计数 |
| 异常清单 | 乱码（U+FFFD）/空输出/代码块围栏不成对 | 正则 + 长度启发式 |

**质量四维 LLM 抽评（可选 · 默认关闭 · P2-1）**：completeness / structure / formatting / cleanliness 四维盲评（LLM-judge 双 swap），方法论唯一真源 `references/fidelity-spec.md` §质量四维抽评。启用属付费确认场景（总则②）：MUST 用户二次确认，NEVER 默认或自动调用；基准引用一律标注来源。默认仅交付确定性指标。

**置信度分级**（阈值唯一真源 `references/fidelity-spec.md`，grep 模式：`置信度`）：

| 置信度 | 判定 | 处置 |
|---|---|---|
| **A 直接可用** | 保真率 ≥95% 且结构计数吻合 | 交付，报告标注 |
| **B 抽查复核** | 保真率 85–95% 或结构部分缺失 | 交付 + 列出复核项 |
| **C 强制人工复核** | 保真率 <85%，或检出乱码/截断/表格丢失 | 交付 + 醒目警示 + 建议升级档位重转 |

**report.md 关键数据段（固定结构，NEVER 省略）**：保真率、丢失率、结构对比表、置信度等级与原因、转换元数据（后端/档位/耗时/资产数/降级轨迹）、异常清单、固定复核项清单（批注与修订丢失/页眉页脚/嵌入对象 OLE/中文字体/.doc 旧格式兼容/表格嵌套）。源文本不可提取时保真率标注「不适用（源文本不可提取）」并降为 C 级口径。

### 可扩展性

1. **新增后端**：在 `references/backends.md` 矩阵追加一行 + `detect_backends.py` 的 `BACKENDS` 表追加探测项，零改流程。
2. **调整档位阈值**：只改 `preflight.py` 顶部常量（表格/图片复杂信号阈值等）。
3. **调整保真度阈值**：只改 `references/fidelity-spec.md`（单一事实源）。
4. **新增质量指标**：在 `quality_check.py` 追加计算函数 + 报告模板加一行。

---

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。skill 任一执行入口启动后的**第零步**，先于核心执行阶段。
> **细则唯一真源**：本 skill 内部 `references/version-check-spec.md`（不依赖任何外部上游 skill）。**可执行实现**：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、四态判定 MUST 由脚本完成；prompt 层 ONLY「调用脚本 + 解析其 JSON 输出 + 按 state 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

**执行方式（MUST）**：运行 `python scripts/check_update.py --slug tri-docx2md --json`，解析 `state` 字段——`A`/`B`/`C`/`D` 一律放行并标注口径，`BLOCK`（退出码 ≥20）绝对禁止执行并按 `block_code` 输出恢复指引。退出码 `<20` 放行；脚本自身异常兜底降级放行，NEVER 因版本门故障阻断启动。四态判定、升级流程、节流缓存细则均在 `references/version-check-spec.md`，本章节 NEVER 内联。

---

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 门A → 门B → 门C → 门D → 交付。版本检查未通过前 NEVER 进入以下任一步骤。

1. **入口分流**：声明自检句 → 模式 A 读快照 §三 / 模式 C 自构造输入；提取 Word 路径、输出期望。
2. **门A 预检**：运行 `preflight.py`；BLOCK（加密/非 Word）则停止并提示；取得等级建议与风险项。
3. **门B 探测**：运行 `detect_backends.py`；向用户报告「等级建议 + 本地可用后端 + 选定方案」；缺失后端给出安装命令，经同意后安装并复测。
4. **门C 结构降维转换**：.doc 先转 docx 中间格式 → 按选定后端官方命令执行 → 产出 MD + assets → 后处理（页眉页脚/图片路径/MD 语法/保留标题树）→ 失败经 scripts/convert_pipeline.py 代码化执行降级链（M1）。
5. **门D 校验**：运行 `quality_check.py` → 产出 report.md（含保真率/丢失率等关键数据段）；C 级时向用户醒目警示并给出升级重转选项。
6. **交付**：`<同名>.md + assets/ + report.md` 落输出目录（默认 `.tribro/docx2md/<命名>/`）；回显产物路径与置信度结论。
7. **链路落盘**：本次转换的过程数据（预检 JSON/探测 JSON/质量 JSON）落 `.tribro/docx2md/<命名>/` 供追溯。

---

## 交付产物

| 产物 | 文件名 | 内容 | 审批门 |
|------|--------|------|--------|
| Markdown 正文 | `<同名>.md` | 转换结果（含图片相对引用、保留标题树） | 门D 校验后 |
| 图片资产 | `assets/` | 提取的图表图片 + 题注对应 | 与正文同步 |
| 质量报告 | `report.md` | 保真率/丢失率/结构对比/置信度/复核项/异常清单 | 门D（MUST，NEVER 省略） |
| 过程数据 | `.tribro/docx2md/<命名>/*.json` | 预检/探测/质量三份 JSON（追溯用） | 自动 |

---

## 质量标准

| 维度 | 标准 | 验证方式 |
|------|------|----------|
| 报告完整性 | report.md 含保真率/丢失率/结构对比/置信度/元数据/异常/复核项全段 | `quality_check.py` 输出核对 |
| 保真度诚实 | 召回率不可计算时显式「不适用」，NEVER 编造数值 | 报告字段校验 |
| 图片引用一致 | MD 图片引用与 assets/ 文件一一对应 | 计数比对 |
| 降级完整 | 后端失败必留降级轨迹，全缺失停在预检态 | 过程 JSON 核对 |
| 结构保留 | 标题层级非空、表格语法闭合、代码块闭合 | MD 语法检查 |
| HTML 标签清理 | 无残留 `<a id="…">`/`</a>`/`<span>` 等非白名单标签；实体已解码 | `postprocess.py` 统计核对 |
| .doc 兼容 | .doc 旧格式先转中间格式再走标准链，NEVER 直接对 .doc 调 .docx 后端 | 流程审查 |
| 边界恪守 | 不破解加密、不擅自装重依赖、不擅自调付费 API | 流程审查 |
| 版本联动 | SKILL.md / CHANGELOG / tests 三处版本一致 | 发布前核对 |

---

## 落盘规则

- 本 skill 为 tri-forge 生成物，包落盘于 `.tribro/skills/tri-docx2md/`（安装后经 junction 同步平台）。
- 用户成果物（`<同名>.md + assets/ + report.md`）落 `.tribro/docx2md/<命名>/`——全部产物统一落盘至 `.tribro/`。
- 过程数据（预检/探测/质量 JSON）落 `.tribro/docx2md/<命名>/`（命名沿用家族规范 `DOCX2MD_<日期>_<时间>_<会话ID>`）。
- 全程不生成 LICENSE / .gitignore。

---

## 目录结构

```
tri-docx2md/
├── SKILL.md                       主入口：契约 + 四阶段管道 + 保真度契约 + 代码版权合规
├── README.md                      特性/目录/安装/使用/测试/设计原则
├── CHANGELOG.md                   Keep a Changelog + SemVer
├── _meta.json                     平台元数据
├── references/
│   ├── backends.md                后端矩阵（能力/安装/许可证/已验证命令 · grep 索引）
│   ├── fidelity-spec.md           保真度分级规范（阈值唯一真源 + 复核项清单）
│   └── version-check-spec.md      版本检查与更新规范（内部唯一真源）
├── scripts/
│   ├── preflight.py               门A：预检分级（文件类型/加密/段落图片计数/等级建议 + 输入规模守卫）
│   ├── detect_backends.py         门B：七后端探测与档位决策（anydoc 双通道首选 + 降级链 + .doc 路径）
│   ├── postprocess.py             门C：转换后处理（两遍锚点保护/实体解码/围栏感知清理/表格嫌疑检测）
│   ├── repair_docx.py             门C 前置：docx 预处理修复（M3：逐公式 OMML→LaTeX/styles/dstrike/zip casing）
│   ├── convert_pipeline.py        门C：降级链执行器（M1：逐后端 attempts 异常聚合 + 聚合诊断 + meta 钩子，自包含副本）
│   ├── md_table.py                M8：自产表转义（竖线转义/换行折空格/列对齐，家族同源副本）
│   ├── sniffer.py                 M9：内容真身二次校验 + charset 嗅探（家族同源副本）
│   ├── _io_safe.py                输出编码兜底（M2：GBK 控制台 safe_print，家族同源副本）
│   ├── dump_assets.py             门C：anydoc 资产落盘 assets/ + MD 资产清单段（幂等）
│   ├── quality_check.py           门D：保真率/丢失率/结构对比/异常/报告生成
│   ├── scale_guard.py             门A 输入规模守卫（anydoc limits.rs 口径 · P2-2）
│   └── check_update.py            版本检查与更新（家族同源）
└── tests/
    ├── tri-docx2md-full-testcases.md  全场景全能力测试用例（审计版）
    ├── mutation_smoke.py          变异冒烟测试（确定性变异 × N 轮 · P2-3）
    └── samples/                   真实格式样本 ×11（anydoc fixture 固化）
```

### 运行时落盘结构（`.tribro/docx2md/`）

```
.tribro/docx2md/<命名>/
├── preflight.json     门A 预检输出（等级建议 + 风险项）
├── backends.json      门B 探测输出（可用后端 + 降级链）
└── quality.json       门D 质量输出（指标 + 置信度）
```

---

## 进化契约

> 本 skill 生成物自带进化契约（compliance #23）——如何接收反馈、沉淀经验、自我修订：

- **反馈接收点**：用户对 report.md 复核项的回填与投诉（「这页表格丢了」「这个公式错了」）写入 `.tribro/docx2md/feedback/`；每次 C 级报告自动视为一条改进信号。
- **经验沉淀位**：后端版本漂移（CLI 参数变更）、新后端出现、.doc 中间转换质量经验沉淀入 `.tribro/docx2md/lessons.md`；规范修订回写 `references/backends.md` 与 `references/fidelity-spec.md`。
- **自我修订触发条件**：① 同类 Word 连续 ≥3 次 C 级 → 修订档位判定阈值或首选后端；② 后端排名显著变化 → 修订 `references/backends.md` 矩阵；③ 新高质量开源后端出现（社区 Stars/基准双高）→ 评估纳入矩阵并更新 `detect_backends.py` 的 `BACKENDS` 表；④ .doc 转换质量反馈高频 → 修订 LibreOffice 转换参数与复核项。
- **质量闭环归属**：本 skill 负责「转换 + 度量 + 报告」，复核与采信由用户执行；report.md 的复核项回填是下一次转换阈值调优的输入。

---

## 代码版权与许可证合规（硬红线）

- 本 skill 只**编排调用**后端官方 CLI / Python API，NEVER 复制、改写或内嵌任何后端源码。
- 后端许可证口径（BSD-2-Clause：mammoth；MIT：markitdown/python-docx；GPL-2.0：pandoc/antiword；MPL-2.0：LibreOffice）见 `references/backends.md` §许可证——GPL 后端以「外部依赖调用、不分发其代码」方式使用；用户对许可证敏感时引导改用 BSD/MIT 后端（mammoth/markitdown/python-docx）。
- 报告与文档引用基准数据 MUST 标注来源与版本，NEVER 混用口径。
