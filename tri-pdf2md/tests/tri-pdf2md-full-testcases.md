---
name: tri-pdf2md-full-testcases
description: tri-pdf2md 全场景全能力测试用例（审计版）——覆盖五阶段管道、四档降级链、保真度报告关键数据、门E 结构化交付（类 Obsidian/父子分块/人工调优/RAG 对接）、边界约束、合规与版本检查。基于 tri-pdf2md v1.4.5。
version: 1.4.5
---

# tri-pdf2md 全场景全能力测试用例

> 基于 **tri-pdf2md v1.1.0**。分组：T1 管道冒烟 / T2 降级链 / T3 保真度与报告 / T4 边界约束 / T5 合规 / T6 版本检查 / T7 结构化交付（门E）。
> 执行约定：`SKILL_DIR` = 本 skill 安装目录；`FIXTURE` = 临时测试目录。

## 能力清单扫描（用例与能力对齐）

| 能力 | 来源 | 覆盖用例 |
|---|---|---|
| 门A 预检分级 | `scripts/preflight.py` | T1.1–T1.3, T4.1, T4.2 |
| 门B 后端探测与决策 | `scripts/detect_backends.py` | T1.4, T2.1–T2.3 |
| 门C 版面分析转换执行指导 | SKILL.md + `references/backends.md` | T1.5, T2.2 |
| 门D 质量校验与报告 | `scripts/quality_check.py` | T1.6, T3.1–T3.6 |
| 门E 类 Obsidian 结构化输出 | `scripts/structure_pack.py` + `references/obsidian-output-spec.md` | T7.1–T7.4 |
| 门E Small-to-Big 父子分块 | `scripts/structure_pack.py` + `references/chunking-spec.md` | T7.2, T7.5–T7.7 |
| 门E 人工调优审阅页 | `structure_pack.py`（review.html） | T7.8–T7.10 |
| 门E RAG 对接数据供给 | `references/rag-handoff-spec.md` | T7.11–T7.13 |
| 保真度分级契约 | `references/fidelity-spec.md` | T3.1–T3.4 |
| 降级链 | SKILL.md 契约 6 | T2.1–T2.4 |
| 诚实边界（加密/扫描/编造禁令） | SKILL.md 契约 2/5 | T4.1–T4.3 |
| L3 付费确认 | SKILL.md 契约 7 | T4.4 |
| 上游依赖检测三态 | SKILL.md §上游依赖检测 | T1.7, T5.1 |
| 版本检查四态 | `scripts/check_update.py` | T6.1–T6.4 |

---

## T1 管道冒烟（五阶段全链路）

### T1.1 数字 PDF 预检 → L0
- **前置**：纯文本数字 PDF（reportlab 生成 3 页）
- **动作**：`python scripts/preflight.py --pdf <FIXTURE>/sample.pdf --json`
- **断言**：`ok=true`；`grade_suggestion="L0"`；`scanned=false`；`avg_chars_per_page > 50`；`encrypted=false`

### T1.2 扫描件预检 → L2
- **前置**：无文本层 PDF（reportlab 只画矩形）
- **动作**：同 T1.1
- **断言**：`grade_suggestion="L2"`；`scanned=true`；`risks` 含「扫描件」

### T1.3 混合类型预检 → L1
- **前置**：部分页有文本层、部分无
- **断言**：`grade_suggestion="L1"`；`mixed=true`；`risks` 含「混合类型」

### T1.4 后端探测决策
- **动作**：`python scripts/detect_backends.py --grade L0 --json`
- **断言**：`plan.grade="L0"`；本地已装 markitdown/pdfplumber 时 `plan.selected` 非空且 `halted=false`；缺失后端均带 `install` 指引

### T1.5 门C 转换执行
- **动作**：按 `references/backends.md` §三 已验证命令执行选定后端
- **断言**：产出 `<同名>.md` 非空；图片后端输出 assets/ 时 MD 引用与文件对应

### T1.6 门D 报告生成（用户硬要求）
- **动作**：`python scripts/quality_check.py --pdf <FIXTURE>/sample.pdf --md <FIXTURE>/sample.md --backend markitdown --grade L0 --json`
- **断言**：report.md 生成；「关键数据（必读）」段含**保真率、丢失率**、噪声率、置信度、后端/档位、页数/耗时、图片资产、降级轨迹全部字段；`report_path` 正确

### T1.7 独立运行入口（三态）
- **断言**：无 tri-intent 时提示引导安装（模式 B）；拒绝后声明降级（模式 C）继续执行；有可用快照时读 §三（模式 A）

### T1.8 结构化场景分流
- **前置**：用户请求含「知识库/RAG 语料/Obsidian 笔记/父子分块」语义
- **断言**：自检句含「结构化=Obsidian+分块」；门E 启用；交付物含结构化三件套

## T2 降级链

### T2.1 首选缺失自动降档
- **前置**：grade=L0 但 pymupdf4llm 未装（本地现状）
- **断言**：`plan.selected` 落到可用后端（markitdown），`fallback_chain` 含 pdfplumber

### T2.2 执行失败降档重试
- **模拟**：选定后端执行抛错/超时
- **断言**：沿 L2→L1→L0 链降级重试；轨迹写入报告「降级轨迹」字段；NEVER 空手交付

### T2.3 全缺失停机
- **模拟**：六后端全部不可用
- **断言**：`halted=true`；输出安装指引；停在预检报告态

### T2.4 C 级升档重转
- **前置**：L0 结果置信度 C 且用户要求重转
- **断言**：建议升档 L1/L2（沿链反向），不重复同档同后端

## T3 保真度与报告（核心 · 用户硬要求）

### T3.1 A 级判定
- **前置**：数字 PDF + markitdown 转换（冒烟实测：保真率 100%）
- **断言**：`confidence="A"`；`reasons` 含「≥ 95%」

### T3.2 B 级判定
- **前置**：召回率被构造在 85–95% 区间（删 MD 部分段落）
- **断言**：`confidence="B"`；报告列出丢失集中页

### T3.3 C 级判定（低召回）
- **前置**：MD 只保留 PDF 一半内容（召回 <85%）
- **断言**：`confidence="C"`；报告醒目警示 + 升档建议

### T3.4 扫描件不编造
- **前置**：无文本层 PDF + 任意 MD
- **断言**：保真率/丢失率 =「不适用（无文本层）」；`confidence="C"`；NEVER 出现编造数值（冒烟实测通过）

### T3.5 异常检测
- **构造**：MD 含 U+FFFD / 空文件 / 围栏不成对
- **断言**：`anomalies` 逐项命中；命中即 C 级

### T3.6 结构对比
- **断言**：PDF 有表格而 MD 无表格语法 → 至少 B 级并写明原因；PDF 有图片而 MD 无图片引用 → 至少 B 级

## T4 边界约束（诚实声明铁律）

### T4.1 加密 PDF 阻断
- **前置**：pypdf `encrypt('secret123')` 加密的 PDF
- **断言**：`grade_suggestion="BLOCK"`；`ok=false`；提示合法解密，NEVER 破解（冒烟实测通过）

### T4.2 空口令可解
- **前置**：`encrypt('')` 空口令加密
- **断言**：`decryptable_with_empty=true`，正常继续分级

### T4.3 目录批量不静默
- **动作**：输入是目录
- **断言**：列清单并请求确认范围，NEVER 批量静默转换

### T4.4 L3 付费确认
- **模拟**：需要 LLM 视觉 API/商业 API
- **断言**：先说明成本与数据外发风险并取得确认，NEVER 未经确认调用

## T5 合规

### T5.1 三态检测语义匹配
- **断言**：本 skill 为内容转换类（可降级）→ 三态含模式 C 降级声明，与类型匹配

### T5.2 MECE 边界
- **断言**：仅认领 I08·pdf2md；语言翻译/其它格式转换归 tri-content；PDF 操作归内置 pdf skill；不与 tri-translate 重叠

### T5.3 版本一致性
- **断言**：SKILL.md `version` == CHANGELOG 置顶 `[1.4.5]` == 本文件 frontmatter `version` == `_meta.json` `version`

### T5.4 代码版权
- **断言**：skill 包内无任何后端源码副本；AGPL 后端仅以外部调用方式使用；报告可注明许可证口径

### T5.5 落盘位置
- **断言**：用户成果物落用户输出目录（非 .tribro/）；过程 JSON 落 `.tribro/pdf2md/<命名>/`；无 LICENSE/.gitignore

## T6 版本检查

### T6.1 A 态放行
- **动作**：`python scripts/check_update.py --slug tri-pdf2md --json`（网络正常且已是最新）
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

## T7 结构化交付（门E · 用户补充要求）

### T7.1 门E 三件套产出
- **动作**：`python scripts/structure_pack.py --pdf <FIXTURE>/sample.pdf --md <FIXTURE>/sample.md --backend markitdown --grade L0 --confidence A --fidelity-rate 0.98 --doc-version v1 --json`
- **断言**：`ok=true`；`products` 含 `<同名>.obsidian.md` / `<同名>.chunks.json` / `<同名>.review.html` 三路径且文件存在（冒烟实测通过：5 父块/9 子块/锚点覆盖 100%）

### T7.2 frontmatter 强制元数据（文档名/版本/页码）
- **断言**：obsidian.md YAML frontmatter 含 title/source_file/doc_version/pages 四字段（缺一即 `exit_code=3`）；`--doc-version` 覆盖生效；缺省版本=PDF修改日期_指纹

### T7.3 页码锚点（零侵入语法）
- **断言**：正文每节尾有 `%% p.N %%`（或 `%% p.N-M %%` 跨页）；锚点为 Obsidian 注释语法（预览不渲染）；正则 `%%\s*p\.\d+(-\d+)?\s*%%` 可一键剥离

### T7.4 锚点判定诚实性
- **构造**：MD 段落在 PDF 中不存在（伪造段落）
- **断言**：该块 `anchor_source="inherited"` 或页码不命中时 NEVER 编造页码；扫描件输出 `%% p.? %%`

### T7.5 父子结构完整
- **断言**：每个子块有 `parent_id`；每个父块 `children` 与实际子块 ID 双向一致；`heading_path` 反映标题树层级

### T7.6 子块切分规则
- **构造**：MD 含超长段落（>800 字符）、表格、代码块
- **断言**：超长段按句末标点二次切分；表格/代码块整体为一个子块 NEVER 从中切断

### T7.7 块级坐标锚点
- **断言**：数字 PDF 子块 `bbox` 为四元数组（pt 口径）且 `bbox_confidence ∈ {exact, approx, unavailable}`；`page` 为 1-based 页码

### T7.8 审阅页自包含
- **断言**：review.html 无外部网络依赖（无 CDN/无 import）；数据内嵌（`const DATA`）；浏览器直接打开可用

### T7.9 人工调优交互
- **动作**：review.html 中合并相邻子块 / 在光标处拆分子块 / 补全 entity（如「同比增长 3%」→ 腾讯控股）/ 标记已核
- **断言**：四操作均生效并反映到导出数据；统计栏（子块数/锚点覆盖/已核数）实时更新

### T7.10 导出与保真红线
- **动作**：「导出修订版」按钮
- **断言**：下载 `chunks.revised.json`（含 `revised_at` 与 `revision_stats`）；合并/拆分只重组原文（字符集合不变，无改写无删改），元数据补全只进 metadata 槽位；原 `<同名>.chunks.json` NEVER 被覆盖

### T7.11 RAG 数据供给字段
- **断言**：chunks.json 顶层含 `doc_id`（文件名+页数+大小短哈希）与 `doc_version`（每块继承）；子块含 BM25 纯文本与向量可拼接的 metadata

### T7.12 版本更新整体替换
- **模拟**：同 doc_id 新版本 PDF 重新转换
- **断言**：产出新 doc_version 块集；按 rag-handoff-spec 约定下游整体替换 NEVER 增量 patch 旧块

### T7.13 评测四指标分工
- **断言**：`evaluation_supply.parse_completeness_source` 指向门D 保真率；`citation_traceability` = anchor_coverage（数字 PDF 冒烟实测 1.0 / 扫描件 0.0）；召回命中率与生成忠实度 NEVER 在本 skill 报告编造

### T7.14 扫描件覆盖率如实
- **前置**：无文本层 PDF（冒烟实测通过）
- **断言**：`anchor_coverage=0.0`；warnings 含「无文本层——页码/坐标锚点不可计算」；NEVER 输出编造坐标

---

## T8 真实格式样本固化（anydoc 迁移 · 2026-09-08）

> 样本固化于 `tests/samples/`（源：anydoc-main 真实 fixture，见 `.tribro/migration-test-20260908/`）。
> 执行方式：对每个样本跑 `python scripts/preflight.py --pdf tests/samples/<样本> --json` + `needsocr_check.py` 分流验证。

| 样本 | 覆盖点 | 关键断言 |
|---|---|---|
| `text.pdf` | L0 文本层首选 | anydoc 快速档转换非空；`anchor_coverage` 正常计算 |
| `handmade-mixed.pdf` | 混合页 NeedsOcr 分流 | 文本层页走 anydoc；扫描页经 NeedsOcr 信号自动置 L2 DL 链，NEVER 对扫描件强行走 anydoc |

---

## 执行记录

| 日期 | 用例 | 结果 | 备注 |
|---|---|---|---|
| 2026-08-24 | T1.1 / T1.2 / T1.4 / T1.5 / T1.6 / T3.1 / T3.4 / T4.1 | 全过 | tri-forge 门②生成时冒烟实测（数字/扫描/加密三路径） |
| 2026-08-24 | T7.1 / T7.2 / T7.3 / T7.5 / T7.7 / T7.8 / T7.11 / T7.13 / T7.14 | 全过 | v1.1.0 门E 回写时冒烟实测（数字 PDF：5 父块/9 子块/锚点覆盖 100%/bbox exact 9；扫描件：coverage 0 如实报告） |
