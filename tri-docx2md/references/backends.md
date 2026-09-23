---
name: backends
description: tri-docx2md 后端矩阵——七后端的能力/安装/许可证/已验证命令，含双档分级策略、anydoc 一等后端链位与 .doc 直读路径、降级链。SKILL.md 门B/门C 的参考唯一真源（grep 检索）。
---

# 后端矩阵（tri-docx2md 唯一事实源）

> 本文件是后端选型、安装指引、许可证口径与已验证命令的唯一事实源。SKILL.md 仅留概览与指针。
> **grep 检索模式**：按档位 `grep -n "L0|L1|DOC"`；按后端 `grep -n "anydoc|Mammoth|MarkItDown|python-docx|Pandoc|LibreOffice|antiword"`；按命令 `grep -n "命令"`。

---

## 一、七后端矩阵（2026-09 调研口径）

| 后端 | 档位 | 技术路线 | 许可证 | 表格 | 图片 | 中文 | 安装 | 定位 |
|---|---|---|---|---|---|---|---|---|
| **anydoc** | L0/L1/DOC 首选 | Rust 原生解析 → 统一 Document 模型 → 单一 GFM 序列化器 | **MIT** | ✓（GridBuilder 网格不变量，列永不错位） | ✓（模型内 bytes，配 dump_assets.py 落盘） | 良 | `pip install firecrawl-anydoc` 或 `npm i -g @firecrawl/anydoc` | 全链首选：.docx/.docm/.doc 直读，公式/脚注/锚点/图表文本化 |
| **mammoth** | L0 降级1 | 纯规则（docx→HTML/MD 专用） | **BSD-2-Clause** | ✓ | ✓（提取） | 良 | `pip install mammoth`（极轻） | anydoc 缺失时的 .docx 快速转 MD |
| **markitdown** | L0 降级2 | 纯规则 | MIT | ✓ | ✓ | 良 | `pip install markitdown[all]` | 通用格式转 MD（29+ 格式，含 docx）（M1 起兼作降级链 runner；M3 公式 LaTeX 修复来源） |
| **python-docx** | L0 兜底 | 纯规则（docx 解析） | MIT | ✓ | ✓ | 良 | `pip install python-docx`（极轻） | 文本/结构精提与门A/门D 源侧计数 |
| **pandoc** | L1 降级 | 通用文档转换 | **GPL-2.0** | ✓ | ✓ | 良 | 官方安装包（见 §安装） | anydoc 缺失时的复杂版式标准档 |
| **LibreOffice** | DOC 降级 | 办公套件 headless | **MPL-2.0** | ✓ | ✓ | 良 | 官方安装包（见 §安装） | anydoc 缺失时 .doc → docx 中间格式转换 |
| **antiword** | DOC 兜底 | 纯文本提取 | **GPL-2.0** | ✗ | ✗ | 中 | `apt install antiword` / 官方包 | .doc 纯文本兜底（无结构） |

**anydoc 首选论据（实测，引用须标注来源）**：anydoc README 基准（100 真实文档、LLM 盲评双 swap）per-format 全部第一——.docx 88（vs mammoth 70 / markitdown 71）、.doc 87、.docm 84；综合 81 分、14/14 格式全覆盖、中位耗时 4.4ms。

**兼容性说明**：WPS 生成的 .docx/.doc 与 MS Office 同格式（OOXML / OLE 复合文档），上述后端按标准格式解析，WPS 文档可直接转换；WPS 特有扩展（如 .wps）不在本 skill 支持范围。

**基准参考（引用须标注来源）**：mammoth 官方 README 自述「保留标题层级/表格/图片引用，忽略批注与修订」；pandoc 官方支持 docx→markdown 双向转换（含样式映射）。无统一中文基准分——中文质量以门D 保真率实测为准，中文字体嵌入缺失列为固定复核项。

---

## 二、双档分级策略与降级链

| 档位 | 适用场景 | 首选 | 降级链 | 预期质量 | 成本 |
|---|---|---|---|---|---|
| **L0 快速** | .docx/.docm/.doc 全场景（anydoc 直读，含旧格式） | anydoc | mammoth → markitdown → python-docx | 结构/表格/公式/脚注保真最高 | 秒级/百页（中位 4.4ms） |
| **L1 标准** | anydoc 缺失时的 .docx 复杂版式 | pandoc | mammoth → markitdown → python-docx | 结构完整，表格/图片保真高 | 秒级，需装 pandoc |
| **DOC 旧格式** | anydoc 缺失时的 .doc 二进制旧格式 | LibreOffice headless（转 docx 中间格式） | antiword（纯文本兜底）→ L0 链 | 需先转中间格式，结构保真取决于转换 | 秒级，需装 LibreOffice |

**降级触发**：① 后端执行失败/超时；② 门D 置信度 C 且用户要求重转；③ 探测到档位首选缺失。降级 MUST 记录轨迹进报告「降级轨迹」字段。

**.doc 旧格式路径（2026-09-08 定案，冲突 4 裁定）**：anydoc 可用时 MUST 直读（自研 MS-DOC 解析器：piece table/STSH 链/PlfLst），NEVER 强制 LibreOffice 中转；anydoc 缺失时降级为 LibreOffice headless 转 `.docx` 中间格式再走标准链，LibreOffice 亦缺失时用 antiword 纯文本兜底（无结构，质量 C 级口径）。判定由 `detect_backends.py` 探测 JSON 决定（`doc_convert.mode = direct | convert`），NEVER Agent 现场裁量。

---

## 三、已验证命令（门C 执行参考）

> 后端版本漂移（CLI 参数变更）时 MUST 回填本节并更新版本号——进化契约触发条件之一。

### anydoc（L0/L1/DOC 首选，2026-09-08 已验证）

```bash
# Python 绑定（import 探测通过后首选通道）
python -c "import anydoc, pathlib; pathlib.Path('<同名>.md').write_text(anydoc.to_markdown('<docx|doc>'), encoding='utf-8')"
# CLI 通道（npx 免安装）
npx -y @firecrawl/anydoc <file> -o out.md   # 退出码：0 成功 / 1 转换失败 / 2 用法错误 / 3 需要 OCR
# 图片资产落盘（anydoc 资产契约唯一路径，P0-4）
python scripts/dump_assets.py --doc <file> --md <同名>.md   # to_document().assets → assets/asset_n.ext + 重写引用
```

安装：`pip install firecrawl-anydoc`（Python 3.10+ wheel）或 `npm i -g @firecrawl/anydoc`（Node 20+）。验证版本 0.2.4。

### mammoth（L0 降级1）

```bash
python -c "import mammoth, pathlib; r = mammoth.convert_to_markdown(open('<docx>','rb')); pathlib.Path('<同名>.md').write_text(r.value, encoding='utf-8')"
```

### markitdown（L0 降级2）

```bash
python -c "from markitdown import MarkItDown; r = MarkItDown().convert('<docx>'); pathlib.Path('<同名>.md').write_text(r.text_content, encoding='utf-8')"
```

### python-docx（L0 兜底 / 文本精提 / 门A·门D 源侧计数）

```bash
python -c "import docx; d = docx.Document('<docx>'); print('\n'.join(p.text for p in d.paragraphs))"
```

### pandoc（L1 降级）

```bash
pandoc "<docx>" -t gfm -o "<同名>.md" --extract-media=assets
```

### LibreOffice headless（DOC 降级：anydoc 缺失时中间转换）

```bash
soffice --headless --convert-to docx --outdir "<中间目录>" "<file>.doc"
```

### antiword（DOC 纯文本兜底）

```bash
antiword "<file>.doc" > "<同名>.txt"
```

### 图片资产补提（后端不提图时）

```bash
python -c "import docx; d = docx.Document('<docx>'); [r for r in d.part.rels.values() if 'image' in r.reltype]"
```

---

## 四、许可证口径（代码版权合规支撑）

- 本 skill 只**编排调用**后端官方 CLI/API，NEVER 复制后端源码——GPL 传染风险因此被隔离在「外部依赖调用」层面。
- **MIT**：anydoc、markitdown、python-docx。**BSD-2-Clause**：mammoth。**GPL-2.0**：pandoc、antiword。**MPL-2.0**：LibreOffice。
- anydoc 归属声明：Firecrawl anydoc（MIT），本 skill 仅编排调用其官方发行包（PyPI `firecrawl-anydoc` / npm `@firecrawl/anydoc`），NEVER 复制内嵌其源码。
- 用户对许可证敏感时，报告与执行日志 MUST 注明所用后端许可证口径；GPL 后端（pandoc/antiword）以「外部依赖调用、不分发其代码」方式使用，敏感场景引导改用 MIT/BSD 后端（anydoc/markitdown/python-docx/mammoth）。

---

## 五、后端演进记录

| 日期 | 变更 | 触发源 |
|---|---|---|
| 2026-09-08 | anydoc 0.2.4 接入为 L0/L1/DOC 全链首选（MIT，Python/CLI 双探测）；.doc 路径改 anydoc 直读首选（冲突 4 裁定）；mammoth/pandoc/LibreOffice 降级 | anydoc-main 蒸馏报告 v1.3.0 P0-1 |
