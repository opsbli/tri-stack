---
name: kb-formats
description: tri-wiki 源数据格式×转换 skill×降级链映射矩阵——门B 分级与门C 委派的唯一事实源。
---

# 源格式 × 转换 skill × 降级链映射矩阵（kb-formats）

> tri-wiki 门B（分级）与门C（委派）的唯一事实源。新增源格式时在本矩阵追加一行 + `scan_sources.py` 的 `FORMAT_MAP` 追加映射，零改流程。
> grep 检索模式：格式扩展名（如 `pdf`、`docx`）/ `FORMAT_MAP` / `skip`。

## 一、格式映射矩阵（v1.0.0）

| 扩展名 | 分级 | 委派 skill | skill 内部降级链（摘要） | 直通处理 |
|---|---|---|---|---|
| `.pdf` | convert | tri-pdf2md | pymupdf4llm → docling → marker → MinerU（四档） | — |
| `.docx` | convert | tri-docx2md | mammoth → markitdown → python-docx → pandoc | — |
| `.doc` | convert | tri-docx2md | LibreOffice 转 docx → 上述链；antiword 兜底 | — |
| `.pptx` | convert | tri-pptx2md | python-pptx → markitdown → LibreOffice | — |
| `.ppt` | convert | tri-pptx2md | LibreOffice 转 pptx → 上述链 | — |
| `.xlsx` | convert | tri-xlsx2md | pandas → openpyxl | — |
| `.xls` | convert | tri-xlsx2md | LibreOffice/openpyxl 兼容读取 | — |
| `.html` / `.htm` | convert | tri-html2md | html2text →BeautifulSoup 链 | — |
| `.md` / `.markdown` | direct | — | — | 规范化（frontmatter 补全/命名对齐） |
| `.txt` | direct | — | — | 包装为 md + frontmatter |
| `.csv` | direct | — | — | 转 Markdown 表格 + frontmatter |

## 二、v1 跳过格式（记录原因，不处理）

| 扩展名 | 原因 | v1.1+ 候选方案 |
|---|---|---|
| `.epub` | 无家族 skill 覆盖 | markitdown / pandoc 直转 |
| `.eml` / `.mbox` | 邮件解析需专用后端 | markitdown / 邮件正文抽取 |
| `.png` / `.jpg` 等图片 | 需 OCR，单文档场景归 tri-pdf2md L3 | DeepSeek-OCR / MinerU OCR 委派 |
| `.mp3` / `.wav` 等音频 | 需 ASR | whisper 转写 → direct |
| `.mp4` 等视频 | 需转写管线 | 视频→音频→ASR |
| 无扩展名 / 未知魔数 | 无法可靠识别 | 魔数嗅探扩展 |

## 三、格式识别规则（scan_sources.py 实现）

1. **扩展名优先**：按上表扩展名映射定级。
2. **魔数校验**：扩展名与魔数冲突时以魔数为准（如 `.pdf` 扩展名但非 `%PDF` 头 → `skip` + 原因 `magic_mismatch`）。
3. **大小写不敏感**：`.PDF` 与 `.pdf` 同级。
4. **可读性抽检**：0 字节文件 → `skip`（`empty_file`）；不可读 → `skip`（`unreadable`）。

## 四、去重标记规则

| 标记 | 判定 | 处置 |
|---|---|---|
| `duplicate_of` | MD5 与已登记文件相同 | 跳过，记录指向首个文件的路径 |
| `near_dup` | direct 类文本内容 simhash 海明距离 ≤3 | 保留首个，其余入 `00-Inbox/` 待人工仲裁（NEVER 自动删除） |

> 近重复仅对 direct 类（md/txt/csv）计算（内容可直接读取）；convert 类转换后不回溯去重（转换保真差异属正常波动）。

## 五、委派安装三态（门C 处置）

| 状态 | 判定 | 处置 |
|---|---|---|
| installed | `.tribro/skills/<slug>/` 或源树 `skills/<slug>/` 或用户 skill 目录存在 SKILL.md | 按计划委派 |
| missing + 用户同意安装 | 未检出，用户同意 | 输出 `skillhub install <slug>` 指引，安装后复测 |
| missing + 用户拒绝 | 未检出，用户拒绝 | 该格式全部标记 `skip`（原因 `skill_not_installed`），**部分降级**——其余格式正常构建 |

> 全部 convert 类 skill 缺失且无 direct 类文件 → 阻断（MUST 输出安装指引并停止，NEVER 空手交付）。
