---
name: backends
description: tri-pdf2md 后端矩阵——七后端的能力/安装/许可证/基准分/已验证命令，含四档分级策略、anydoc 文本层首选与 NeedsOcr 信号分流、降级链。SKILL.md 门B/门C 的参考唯一真源（grep 检索）。
---

# 后端矩阵（tri-pdf2md 唯一事实源）

> 本文件是后端选型、安装指引、许可证口径与已验证命令的唯一事实源。SKILL.md 仅留概览与指针。
> **grep 检索模式**：按档位 `grep -n "L0|L1|L2|L3"`；按后端 `grep -n "anydoc|Docling|Marker|MinerU|pymupdf4llm|markitdown|pdfplumber"`；按命令 `grep -n "命令"`。

---

## 一、七后端矩阵（2026-09 调研口径）

| 后端 | 档位 | 技术路线 | 许可证 | 表格 | 公式 | OCR | 中文 | 安装 | 定位 |
|---|---|---|---|---|---|---|---|---|---|
| **anydoc** | L0 首选（仅文本层 PDF） | Rust 原生解析（pdf-inspector 直出 GFM） | **MIT** | ✓ | ✗ | ✗（报 NeedsOcr 列页码） | 良 | `pip install firecrawl-anydoc` 或 `npm i -g @firecrawl/anydoc` | 文本层 PDF 快速档首选（基准 per-format 第一、中位 4.4ms）；扫描页 NeedsOcr 信号 → 自动置 L2 链 |
| **pymupdf4llm** | L0 降级1 | 纯规则 | **AGPL-3.0** | 有限 | ✗ | 有限 | 中 | `pip install pymupdf4llm`（极轻） | 数字 PDF 快速提取 |
| **markitdown** | L0 降级2 | 纯规则 | MIT | ✗ | ✗ | 有限 | 中 | `pip install markitdown[all]` | 通用格式转 MD（29+ 格式）（M1 起兼作降级链 runner；M3 公式 LaTeX 修复来源；M6 无边框表格词坐标聚类预处理来源 `scripts/pdf_form_extract.py`） |
| **pdfplumber** | L0 兜底 | 纯规则 | MIT | ✓ | ✗ | ✗ | 中 | `pip install pdfplumber`（极轻） | 表格调试/文本精提 |
| **docling** | L1 首选 | 深度学习 | MIT | ✓ | ✓ | ✓（多后端） | 良 | `pip install docling`（模型中等） | 标准档主力 |
| **marker** | L1 备选 | 深度学习 | Apache-2.0 | ✓ | ✓ | ✓ | 良 | `pip install marker-pdf`（CPU 可跑） | 标准档备选，吞吐 2.9 pg/s |
| **MinerU** | L2 首选 | DL+规则 | Apache-2.0（3.3.0+ OSL）/ AGPL（旧版） | ✓ | ✓ | ✓ | 良（109 语言） | `pip install -U "mineru[core]"`（权重数 GB） | 精细档主力 |

**基准分（OmniDocBench，引用须标注版本）**：

- v1.6：MinerU2.5-Pro 综合 **95.69**（文本编辑距离 0.019 / 公式 CDM 97.29 / 表格 TEDS 93.42 / 阅读顺序 0.120）
- v1.5：PaddleOCR-VL 92.86（0.9B）、MinerU2.5 90.67、PP-StructureV3 86.73（pipeline 最强）、Marker 1.8.2 71.30、GPT-4o 仅 75.02
- olmOCR-bench：Marker 2 balanced 76.0 vs MinerU pipeline 72.7
- 第三方（Ertas）：Docling 扫描 OCR 89.1%、页眉页脚去除 91.3%（三者最高）
- 中文短板：PaddleOCR-VL 中文公式 CDM 0.6956 vs 英文 0.9616——中文公式仍是行业难点，列为固定复核项

**商业 API（仅 L3 兜底，须用户确认成本与数据外发）**：Doc2X ¥0.02/页、TextIn ¥0.042/页起、LlamaParse $1.25/1K credits（10K/月免费）、Mistral OCR ~$1/页、Reducto $0.015/页。GPT-4o 视觉直转基准仅 75.02，质量不稳定。

---

## 二、四档分级策略与降级链

| 档位 | 适用场景 | 首选 | 降级链 | 预期质量 | 成本 |
|---|---|---|---|---|---|
| **L0 快速** | 文本层 PDF、简单版式、大批量 | anydoc | pymupdf4llm → markitdown → pdfplumber | 文本优（NeedsOcr 信号自动置 L2，见 needsocr_check.py） | 秒级/百页（中位 4.4ms） |
| **L1 标准** | 多栏、表格、少量公式 | docling | marker → pymupdf4llm → markitdown → pdfplumber | 表格 TEDS 80+ | 分钟级，需装 DL 后端 |
| **L2 精细** | 扫描件、学术文献、复杂版面 | MinerU | docling → marker → L0 链 | 文本 98+/公式 CDM 97/表格 TEDS 93 | 较慢，需下模型权重 |
| **L3 兜底** | 后端全失败或用户极致要求 | LLM 视觉 API | 商业 API（Doc2X/TextIn/LlamaParse） | 不稳定（GPT-4o 75.02） | 付费，MUST 用户确认 |

**降级触发**：① 后端执行失败/超时；② 门D 置信度 C 且用户要求重转；③ 探测到档位首选缺失。降级 MUST 记录轨迹进报告「降级轨迹」字段。

---

## 三、已验证命令（门C 执行参考）

> 后端版本漂移（CLI 参数变更）时 MUST 回填本节并更新版本号——进化契约触发条件之一。

### anydoc（L0 首选：仅文本层 PDF，2026-09-08 已验证 v0.2.4）

```bash
# Python 绑定（import 探测通过后首选通道）
python -c "import anydoc, pathlib; pathlib.Path('<同名>.md').write_text(anydoc.to_markdown('<pdf>'), encoding='utf-8')"
# CLI 通道（npx 免安装；扫描页退出码 3）
npx -y @firecrawl/anydoc <file> -o out.md
# NeedsOcr 信号检测（P0-2）：扫描页页码清单 + 自动置 L2 建议
python scripts/needsocr_check.py --pdf <file> --json
```

安装：`pip install firecrawl-anydoc`（Python 3.10+ wheel）或 `npm i -g @firecrawl/anydoc`（Node 20+）。隔离边界：anydoc 不做 OCR——扫描件/图片页 MUST 经 needsocr_check.py 信号分流到 L2 DL 链（MinerU/docling），NEVER 对扫描件强行走 anydoc。

### pymupdf4llm（L0 降级1）

```bash
python -c "import pymupdf4llm, pathlib; pathlib.Path('<同名>.md').write_text(pymupdf4llm.to_markdown('<pdf>'), encoding='utf-8')"
```

### markitdown（L0 降级2，本机已验证 2026-08-24，v0.1.5）

```bash
python -c "from markitdown import MarkItDown; r = MarkItDown().convert('<pdf>'); pathlib.Path('<同名>.md').write_text(r.text_content, encoding='utf-8')"
```

### pdfplumber（L0 兜底/表格补提）

```bash
python -c "import pdfplumber; pages = [p.extract_text() or '' for p in pdfplumber.open('<pdf>').pages]"
```

### docling（L1）

```bash
python -c "from docling.document_converter import DocumentConverter; r = DocumentConverter().convert('<pdf>'); pathlib.Path('<同名>.md').write_text(r.document.export_to_markdown(), encoding='utf-8')"
```

### marker（L1）

```bash
marker_single "<pdf>" --output_dir "<目录>"
```

### MinerU（L2）

```bash
mineru -p "<pdf>" -o "<目录>"    # 3.3.0+ 新 CLI；旧版为 magic-pdf -p ... -o ...
```

### 图片资产补提（后端不提图时）

```bash
python -c "import pypdf; [p.images[i].name for p in pypdf.PdfReader('<pdf>').pages for i in p.images]"
```

---

## 四、许可证口径（代码版权合规支撑）

- 本 skill 只**编排调用**后端官方 CLI/API，NEVER 复制后端源码——AGPL 传染风险因此被隔离在「外部依赖调用」层面。
- **AGPL-3.0**：pymupdf4llm、MinerU 3.3.0 前旧版。闭源/商用合规敏感场景改用 MIT/Apache 后端链（markitdown → pdfplumber / docling / marker）。
- **MIT**：anydoc、docling、pdfplumber、markitdown。**Apache-2.0**：marker、MinerU 3.3.0+（OSL）。
- 用户对许可证敏感时，报告与执行日志 MUST 注明所用后端许可证口径。

---

## 五、后端演进记录

| 日期 | 变更 | 触发源 |
|---|---|---|
| 2026-08-24 | 初版矩阵（三路调研沉淀：开源工具/agent 生态/技术边界） | tri-forge 门②生成 |
