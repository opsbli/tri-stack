---
name: tri-docx2md-full-testcases
description: tri-docx2md 全场景全能力测试用例（审计版）——覆盖四阶段管道、双档降级链、.doc 旧格式路径、保真度报告关键数据、边界约束、合规与版本检查。基于 tri-docx2md v1.4.5。
version: 1.4.5
---

# tri-docx2md 全场景全能力测试用例

> 基于 **tri-docx2md v1.1.0**。分组：T1 管道冒烟 / T2 降级链 / T3 保真度与报告 / T4 边界约束 / T5 合规 / T6 版本检查。
> 执行约定：`SKILL_DIR` = 本 skill 安装目录；`FIXTURE` = 临时测试目录。

## 能力清单扫描（用例与能力对齐）

| 能力 | 来源 | 覆盖用例 |
|---|---|---|
| 门A 预检分级 | `scripts/preflight.py` | T1.1–T1.3, T4.1, T4.2 |
| 门B 后端探测与决策 | `scripts/detect_backends.py` | T1.4, T2.1–T2.3 |
| 门C 结构降维转换执行指导 | SKILL.md + `references/backends.md` | T1.5, T2.2 |
| 门D 质量校验与报告 | `scripts/quality_check.py` | T1.6, T3.1–T3.6 |
| .doc 旧格式路径 | SKILL.md 契约 7 + `references/backends.md` | T1.3, T2.5, T4.5 |
| 保真度分级契约 | `references/fidelity-spec.md` | T3.1–T3.4 |
| 降级链 | SKILL.md 契约 6 | T2.1–T2.4 |
| 诚实边界（加密/结构降维/编造禁令） | SKILL.md 契约 2/5 | T4.1–T4.3 |
| 上游依赖检测三态 | SKILL.md §上游依赖检测 | T1.7, T5.1 |
| 版本检查四态 | `scripts/check_update.py` | T6.1–T6.4 |

---

## T1 管道冒烟（四阶段全链路）

### T1.1 简单 .docx 预检 → L0
- **前置**：python-docx 生成的纯文本 .docx（3 段，无表格无图片）
- **动作**：`python scripts/preflight.py --doc <FIXTURE>/sample.docx --json`
- **断言**：`ok=true`；`detected_type="docx"`；`grade_suggestion="L0"`；`doc_format=false`；`encrypted=false`；`paragraph_count > 0`

### T1.2 复杂 .docx 预检 → L1
- **前置**：python-docx 生成含 ≥5 表格或 ≥10 图片的 .docx
- **断言**：`grade_suggestion="L1"`；`risks` 含「复杂版式信号」

### T1.3 .doc 旧格式预检 → L1 + 旧格式标记
- **前置**：OLE 复合文档头（D0CF11E0）的 .doc 文件
- **断言**：`detected_type="doc"`；`doc_format=true`；`grade_suggestion="L1"`；`risks` 含「旧格式 .doc」

### T1.4 后端探测决策
- **动作**：`python scripts/detect_backends.py --grade L0 --json`
- **断言**：`plan.grade="L0"`；本地已装 mammoth/markitdown/python-docx 时 `plan.selected` 非空且 `halted=false`；缺失后端均带 `install` 指引

### T1.5 门C 转换执行
- **动作**：按 `references/backends.md` §三 已验证命令执行选定后端
- **断言**：产出 `<同名>.md` 非空；图片后端输出 assets/ 时 MD 引用与文件对应

### T1.6 门D 报告生成（用户硬要求）
- **动作**：`python scripts/quality_check.py --doc <FIXTURE>/sample.docx --md <FIXTURE>/sample.md --backend mammoth --grade L0 --json`
- **断言**：report.md 生成；「关键数据（必读）」段含**保真率、丢失率**、噪声率、置信度、后端/档位、源文本提取方式、耗时、图片资产、降级轨迹全部字段；`report_path` 正确

### T1.7 独立运行入口（三态）
- **断言**：无 tri-intent 时提示引导安装（模式 B）；拒绝后声明降级（模式 C）继续执行；有可用快照时读 §三（模式 A）

## T2 降级链

### T2.1 首选缺失自动降档
- **前置**：grade=L0 但 mammoth 未装（本地现状）
- **断言**：`plan.selected` 落到可用后端（markitdown/python-docx），`fallback_chain` 含其余 L0 后端

### T2.2 执行失败降档重试
- **模拟**：选定后端执行抛错/超时
- **断言**：沿 L1→L0 链降级重试；轨迹写入报告「降级轨迹」字段；NEVER 空手交付

### T2.3 全缺失停机
- **模拟**：L0 三后端全部不可用
- **断言**：`halted=true`；输出安装指引；停在预检报告态

### T2.4 C 级升档重转
- **前置**：L0 结果置信度 C 且用户要求重转
- **断言**：建议升档 L1（沿链反向），不重复同档同后端

### T2.5 .doc 中间转换路径
- **前置**：.doc 文件 + 本地有 LibreOffice
- **动作**：`python scripts/detect_backends.py --grade L1 --doc-format --json`
- **断言**：`plan.doc_convert.needed=true`；`doc_convert.selected="libreoffice"`；`doc_convert.halted=false`；门C 先 `soffice --headless --convert-to docx` 转中间格式再走标准链

## T3 保真度与报告（核心 · 用户硬要求）

### T3.1 A 级判定
- **前置**：简单 .docx + mammoth 转换（冒烟实测：保真率 100%）
- **断言**：`confidence="A"`；`reasons` 含「≥ 95%」

### T3.2 B 级判定
- **前置**：召回率被构造在 85–95% 区间（删 MD 部分段落）
- **断言**：`confidence="B"`；报告列出复核项

### T3.3 C 级判定（低召回）
- **前置**：MD 只保留源文档一半内容（召回 <85%）
- **断言**：`confidence="C"`；报告醒目警示 + 升档建议

### T3.4 源文本不可提取不编造
- **前置**：源文本 <50 字符（空文档）或 .doc 无法提取 + 任意 MD
- **断言**：保真率/丢失率 =「不适用（源文本不可提取）」；`confidence="C"`；NEVER 出现编造数值

### T3.5 异常检测
- **构造**：MD 含 U+FFFD / 空文件 / 围栏不成对
- **断言**：`anomalies` 逐项命中；命中即 C 级

### T3.6 结构对比
- **断言**：源文档有表格而 MD 无表格语法 → 至少 B 级并写明原因；源文档有图片而 MD 无图片引用 → 至少 B 级

## T4 边界约束（诚实声明铁律）

### T4.1 OOXML 加密阻断
- **前置**：zip 内含 EncryptionInfo/EncryptedPackage 的 .docx
- **断言**：`grade_suggestion="BLOCK"`；`ok=false`；提示合法解密，NEVER 破解

### T4.2 非 Word 文件阻断
- **前置**：魔数非 PK zip 头 / OLE 头的文件（如 .txt/.pdf）
- **断言**：`grade_suggestion="BLOCK"`；提示确认文件类型

### T4.3 结构降维诚实
- **断言**：报告固定复核项含「批注与修订丢失/页眉页脚/嵌入对象 OLE/中文字体/.doc 旧格式兼容/表格嵌套」六项，即使 A 级也不省略

### T4.4 目录批量不静默
- **动作**：输入是目录
- **断言**：列清单并请求确认范围，NEVER 批量静默转换

### T4.5 .doc 不直调 .docx 后端
- **断言**：.doc 文件 NEVER 直接调用 mammoth/python-docx/pandoc；MUST 先经 LibreOffice 转中间格式（或 antiword 兜底）

## T5 合规

### T5.1 三态检测语义匹配
- **断言**：本 skill 为内容转换类（可降级）→ 三态含模式 C 降级声明，与类型匹配

### T5.2 MECE 边界
- **断言**：仅认领 I08·docx2md；PDF 转 MD 归 tri-pdf2md；语言翻译/其它格式转换归 tri-content；Word 文档操作归内置 docx skill；不与 tri-translate 重叠

### T5.3 版本一致性
- **断言**：SKILL.md `version` == CHANGELOG 置顶 `[1.4.5]` == 本文件 frontmatter `version` == `_meta.json` `version`

### T5.4 代码版权
- **断言**：skill 包内无任何后端源码副本；GPL 后端（pandoc/antiword）仅以外部调用方式使用；报告可注明许可证口径

### T5.5 落盘位置
- **断言**：用户成果物落用户输出目录（非 .tribro/）；过程 JSON 落 `.tribro/docx2md/<命名>/`；无 LICENSE/.gitignore

## T6 版本检查

### T6.1 A 态放行
- **动作**：`python scripts/check_update.py --slug tri-docx2md --json`（网络正常且已是最新）
- **断言**：`state="A"`，退出码 0，放行

### T6.2 B 态离线降级
- **模拟**：断网
- **断言**：`state="B"`，标注「版本校验未完成（离线）」后继续

### T6.3 C 态通道降级
- **模拟**：API 404/响应无效
- **断言**：`state="C"`，标注「通道不可用」后继续

### T6.4 BLOCK 阻断
- **模拟**：升级后校验失败/签名不一致
- **断言**：退出码 ≥20；绝对禁止执行；输出 `block_code` 恢复指引

### T6.5 瘦指针 STUB
- **断言**：SKILL.md §版本检查与更新机制 ≤30 行，指向 `references/version-check-spec.md`，无内联细则

---

## T7 真实格式样本固化（anydoc 迁移 · 2026-09-08）

> 样本固化于 `tests/samples/`（源：anydoc-main 真实 fixture，见 `.tribro/migration-test-20260908/`）。
> 执行方式：对每个样本跑 `python scripts/preflight.py --doc tests/samples/<样本> --json` 并按门B→门C→门D 全链验证。

| 样本 | 覆盖点 | 关键断言 |
|---|---|---|
| `text.docx` | L0 基线 | `grade_suggestion="L0"`；anydoc 转 MD 非空 |
| `handmade-tables.docx` | 多表 L1 | `grade_suggestion="L1"`；表格列对齐（网格不变量） |
| `handmade-numbering.docx` | 编号列表 | 列表层级与编号保真 |
| `handmade-math.docx` | 公式 | OMML 公式文本化（elem_formulas 计数入报告） |
| `handmade-rich.docx` | 富样式 | 加粗/斜体/颜色样式保真 |
| `sample.docm` | 宏文档 | `detected_type="docx"` 族；正常转换 |
| `text.doc` | .doc 旧格式直读 | anydoc 首选直读，免 LibreOffice 中转 |
| `handmade-cyrillic.doc` | .doc 西里尔编码 | 字符集无损（保真率 ≥A） |
| `handmade-shiftjis.doc` | .doc Shift-JIS | 日文编码无损 |
| `handmade-blockstyle.doc` | .doc 块样式 | 样式结构保真 |
| `fake-odt-as-docx.docx` | 扩展名伪装防误判 | preflight 检出真实类型（ODT 头），拒收或如实标记，NEVER 按 .docx 盲转 |

---

## 执行记录

| 日期 | 用例 | 结果 | 备注 |
|---|---|---|---|
| 2026-08-24 | T1.1 / T1.4 / T1.6 / T3.1 / T3.4 / T4.1 / T4.2 | 全过 | tri-forge 门②生成时冒烟实测（简单 .docx / 加密 / 非 Word 三路径） |
