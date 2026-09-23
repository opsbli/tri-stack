---
name: backends
description: tri-xlsx2md 后端矩阵——六后端的能力/安装/许可证/已验证命令，含三档分级策略、anydoc 全族直读首选（.xlsx/.xlsm/.xls/.xlsb/.csv）与降级链。SKILL.md 门B/门C 的参考唯一真源（grep 检索）。
---

# 后端矩阵（tri-xlsx2md 唯一事实源）

> 本文件是后端选型、安装指引、许可证口径与已验证命令的唯一事实源。SKILL.md 仅留概览与指针。
> **grep 检索模式**：按档位 `grep -n "L0|L1"`；按后端 `grep -n "anydoc|openpyxl|markitdown|xlrd|pandas|libreoffice"`；按命令 `grep -n "命令"`。

---

## 一、六后端矩阵（2026-09 调研口径）

| 后端 | 档位 | 技术路线 | 许可证 | 支持格式 | 公式求值 | 合并单元格 | 安装 | 定位 |
|---|---|---|---|---|---|---|---|---|
| **anydoc** | L0/L1 首选 | Rust 原生解析（SpreadsheetML + BIFF + xlsb 自研 + RFC 4180 CSV）→ 统一 GFM | **MIT** | .xlsx/.xlsm/.xls/.xlsb/.csv | ✗（取缓存值） | ✓（GridBuilder 网格不变量，列永不错位） | `pip install firecrawl-anydoc` 或 `npm i -g @firecrawl/anydoc` | 全链首选：合并单元格保真最高（基准 .xls 80 / .xlsm 76 / .xlsx 72 全部第一）；.xlsb 直读免 LibreOffice；CSV 多分隔符/多编码 |
| **openpyxl** | L0 降级1 | 纯解析 | **MIT** | .xlsx | ✗（取缓存值） | ✓（可读 merged_cells） | `pip install openpyxl`（轻量） | .xlsx 快速转换 |
| **markitdown** | L0 降级2 | 纯规则 | MIT | .xlsx 等 29+ 格式 | ✗ | 有限 | `pip install markitdown[all]` | 通用格式转 MD（M1 起兼作降级链 runner；M3 公式 LaTeX 修复来源；M5 showZeroes 二进制修复预处理来源 `scripts/repair_xlsx.py`，openpyxl/pandas runner 自动重试钩子） |
| **xlrd** | L0 降级（.xls） | 纯解析 | **BSD-3** | 仅 .xls | ✗ | ✓ | `pip install xlrd`（轻量） | 旧二进制格式转换 |
| **pandas** | L1 降级1 | 纯解析+求值 | **BSD-3** | .xlsx/.xls | 有限（read_excel 取缓存值） | ✓ | `pip install pandas` | 复杂/超大表 |
| **libreoffice** | L1 降级2 | 官方套件 | **MPL-2.0** | .xlsx/.xls/.ods 等 | ✓（headless 可重算） | ✓ | 系统包（见下） | 公式求值/格式保真 |

**兼容性备注**：
- **WPS 兼容**：WPS 生成的 .xlsx/.xls 与微软 Office 同格式（OOXML/BIFF），上述后端均可解析；个别 WPS 私有扩展（如特殊样式）可能丢失，属结构降维预期内。
- **openpyxl 不支持 .xls**：.xls 旧二进制格式 MUST 走 xlrd/pandas/LibreOffice 链。
- **公式语义**：openpyxl/xlrd/pandas 默认读取缓存值（公式语义丢失）；LibreOffice headless 可重算公式（`--convert-to xlsx` 后走标准链）。

---

## 二、三档分级策略与降级链

| 档位 | 适用场景 | 首选 | 降级链 | 预期质量 | 成本 |
|---|---|---|---|---|---|
| **L0 快速（.xlsx/.xlsm）** | 纯数据、规模正常 | anydoc | openpyxl → markitdown | 合并单元格网格不变量 + 公式取缓存值（基准 per-format 第一） | 秒级 |
| **L0 快速（.xls/.xlsb/.csv）** | 旧二进制/直读/CSV | anydoc | xlrd（.xls）→ pandas → libreoffice | .xlsb 直读免中转；CSV 多分隔符/多编码（P1-7） | 秒级 |
| **L1 标准** | anydoc 缺失时的复杂/超大/公式求值 | pandas | libreoffice → openpyxl → markitdown → xlrd | 公式可求值，超大表可流式 | 分钟级 |

**降级触发**：① 后端执行失败/超时；② 门D 置信度 C 且用户要求重转；③ 探测到档位首选缺失。降级 MUST 记录轨迹进报告「降级轨迹」字段。

---

## 三、已验证命令（门C 执行参考）

> 后端版本漂移（CLI 参数变更）时 MUST 回填本节并更新版本号——进化契约触发条件之一。

### anydoc（L0/L1 首选，2026-09-08 已验证 v0.2.4）

```bash
# Python 绑定（import 探测通过后首选通道）
python -c "import anydoc, pathlib; pathlib.Path('<同名>.md').write_text(anydoc.to_markdown('<xlsx|xls|xlsb|csv>'), encoding='utf-8')"
# CLI 通道（npx 免安装；CSV 无魔数时显式 --format csv）
npx -y @firecrawl/anydoc <file> -o out.md
```

安装：`pip install firecrawl-anydoc`（Python 3.10+ wheel）或 `npm i -g @firecrawl/anydoc`（Node 20+）。资产契约：表格类转换 `assets: N/A`（quality_check 写死判定，P0-4）。

### openpyxl（L0 降级1 · .xlsx）

```bash
python -c "import openpyxl, pathlib; wb=openpyxl.load_workbook('<xlsx>', data_only=True); out=[]; [out.append(f'## Sheet {ws.title}') or [out.append('|'+'|'.join(['' if c.value is None else str(c.value) for c in row])+'|') for row in ws.iter_rows()] for ws in wb.worksheets]; pathlib.Path('<同名>.md').write_text('\n'.join(out), encoding='utf-8')"
```

### markitdown（L0 降级2 · .xlsx）

```bash
python -c "from markitdown import MarkItDown; r = MarkItDown().convert('<xlsx>'); pathlib.Path('<同名>.md').write_text(r.text_content, encoding='utf-8')"
```

### xlrd（L0 降级 · .xls）

```bash
python -c "import xlrd, pathlib; book=xlrd.open_workbook('<xls>'); out=[]; [out.append(f'## Sheet {sh.name}') or [out.append('|'+'|'.join(['' if v in (None,'') else str(v) for v in sh.row_values(r)])+'|') for r in range(sh.nrows)] for sh in book.sheets()]; pathlib.Path('<同名>.md').write_text('\n'.join(out), encoding='utf-8')"
```

### pandas（L1 降级1 · .xlsx/.xls）

```bash
python -c "import pandas as pd, pathlib; xl=pd.ExcelFile('<xlsx>'); out=[]; [out.append(f'## Sheet {s}') or out.append(pd.read_excel(xl, sheet_name=s).to_markdown(index=False)) for s in xl.sheet_names]; pathlib.Path('<同名>.md').write_text('\n\n'.join(out), encoding='utf-8')"
```

### LibreOffice headless（L1 降级2 · 公式求值/格式保真）

```bash
soffice --headless --convert-to xlsx --outdir <中间目录> "<xlsx>"   # 转中间格式后走标准链
```

---

## 四、许可证口径（代码版权合规支撑）

- 本 skill 只**编排调用**后端官方 CLI/API，NEVER 复制后端源码——所有后端均以「外部依赖调用、不分发其代码」方式使用。
- **MIT**：openpyxl、markitdown。**BSD-3**：xlrd、pandas。**MPL-2.0**：LibreOffice headless。
- 用户对许可证敏感时，报告与执行日志 MUST 注明所用后端许可证口径。

---

## 五、后端演进记录

| 日期 | 变更 | 触发源 |
|---|---|---|
| 2026-08-24 | 初版矩阵（openpyxl 3.1.5 / xlrd 2.0.2 / pandas 2.3.3 / markitdown 本机已验证） | tri-forge 门②生成 |
