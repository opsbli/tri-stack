---
name: backends
description: tri-html2md 后端矩阵——五后端的能力/安装/许可证/已验证命令，含两档分级策略与降级链。SKILL.md 门B/门C 的参考唯一真源（grep 检索）。
---

# 后端矩阵（tri-html2md 唯一事实源）

> 本文件是后端选型、安装指引、许可证口径与已验证命令的唯一事实源。SKILL.md 仅留概览与指针。
> **grep 检索模式**：按档位 `grep -n "L0|L1"`；按后端 `grep -n "markitdown|html2text|beautifulsoup4|pandoc|trafilatura"`；按命令 `grep -n "命令"`。

---

## 一、五后端矩阵（2026-08 调研口径）

| 后端 | 档位 | 技术路线 | 许可证 | 表格 | 标题层级 | 图片 | 中文 | 安装 | 定位 |
|---|---|---|---|---|---|---|---|---|---|
| **markitdown** | L0 首选 | 纯规则 | MIT | 有限 | ✓ | ✓ | 良 | `pip install markitdown[all]` | 通用格式转 MD（29+ 格式）（M1 起兼作降级链 runner；M3 公式 LaTeX 修复来源） |
| **html2text** | L0 备选 | 纯规则 | MIT | 有限 | ✓ | ✓ | 良 | `pip install html2text`（极轻） | 经典 HTML→MD 转换器 |
| **beautifulsoup4** | L0 兜底 | 纯规则 | MIT | 手写 | 手写 | 手写 | 良 | `pip install beautifulsoup4`（极轻） | 结构提取/自定义转换 |
| **pandoc** | L1 首选 | 通用文档转换器 | GPL-2.0（CLI） | ✓ | ✓ | ✓ | 良 | `winget install pandoc` / `apt install pandoc` | 标准档主力，GFM 输出 |
| **trafilatura** | L1 备选 | 正文提取 | Apache-2.0 | 有限 | 部分 | 有限 | 良 | `pip install trafilatura` | 网页正文/结构化提取 |

**说明**：HTML 本身含语义结构（标题/表格/链接标签），因此本 skill **无 L2/L3 档**——不需要 OCR 档（L2）也不需要 LLM 视觉兜底（L3）。这是与 tri-pdf2md 的关键差异。

---

## 二、两档分级策略与降级链

| 档位 | 适用场景 | 首选 | 降级链 | 预期质量 | 成本 |
|---|---|---|---|---|---|
| **L0 快速** | 简单 HTML、大批量、正文为主 | markitdown | html2text → beautifulsoup4 | 文本优，表格/嵌套结构有限 | 秒级 |
| **L1 标准** | 复杂 HTML、表格/嵌套结构、学术/文档导出 | pandoc | trafilatura → markitdown → html2text → beautifulsoup4 | 结构优，表格/标题层级完整 | 秒级，需装 pandoc |

**降级触发**：① 后端执行失败/超时；② 门D 置信度 C 且用户要求重转；③ 探测到档位首选缺失。降级 MUST 记录轨迹进报告「降级轨迹」字段。

---

## 三、已验证命令（门C 执行参考）

> 后端版本漂移（CLI 参数变更）时 MUST 回填本节并更新版本号——进化契约触发条件之一。

### markitdown（L0，本机已验证 2026-08-24，v0.1.5）

```bash
python -c "from markitdown import MarkItDown; r = MarkItDown().convert('<html>'); pathlib.Path('<同名>.md').write_text(r.text_content, encoding='utf-8')"
```

### html2text（L0）

```bash
python -c "import html2text, pathlib; pathlib.Path('<同名>.md').write_text(html2text.html2text(pathlib.Path('<html>').read_text(encoding='utf-8')), encoding='utf-8')"
```

### beautifulsoup4（L0 兜底/结构提取）

```bash
python -c "from bs4 import BeautifulSoup; s = BeautifulSoup(pathlib.Path('<html>').read_text(encoding='utf-8'), 'html.parser'); [t.extract() for t in s(['script','style'])]"
```

### pandoc（L1）

```bash
pandoc "<html>" -f html -t gfm -o "<同名>.md"
```

### trafilatura（L1）

```bash
python -c "import trafilatura, pathlib; html = pathlib.Path('<html>').read_text(encoding='utf-8'); pathlib.Path('<同名>.md').write_text(trafilatura.extract(html, output_format='markdown') or '', encoding='utf-8')"
```

### 图片资产补提（后端不提图时）

```bash
python -c "from bs4 import BeautifulSoup; s = BeautifulSoup(pathlib.Path('<html>').read_text(encoding='utf-8'), 'html.parser'); [i.get('src') for i in s.find_all('img')]"
```

---

## 四、许可证口径（代码版权合规支撑）

- 本 skill 只**编排调用**后端官方 CLI/API，NEVER 复制后端源码——GPL 传染风险因此被隔离在「外部 CLI 调用」层面。
- **MIT**：markitdown、html2text、beautifulsoup4。**Apache-2.0**：trafilatura。**GPL-2.0**：pandoc（独立 CLI 程序，以外部进程调用方式使用，不分发其代码）。
- 用户对许可证敏感时，报告与执行日志 MUST 注明所用后端许可证口径；GPL 敏感场景引导改用 MIT/Apache 后端链（markitdown → html2text → beautifulsoup4 / trafilatura）。

---

## 五、后端演进记录

| 日期 | 变更 | 触发源 |
|---|---|---|
| 2026-08-24 | 初版矩阵（HTML→MD 后端调研沉淀） | tri-forge 门②生成 |
