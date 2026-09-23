---
name: backends
description: tri-pptx2md 后端矩阵——五后端的能力/安装/许可证/已验证命令，含四档分级策略、anydoc 一等首选与 .ppt/.pptm/.pps/.pot/.ppsx/.ppsm 全族直读、降级链。SKILL.md 门B/门C 的参考唯一真源（grep 检索）。
---

# 后端矩阵（tri-pptx2md 唯一事实源）

> 本文件是后端选型、安装指引、许可证口径与已验证命令的唯一事实源。SKILL.md 仅留概览与指针。
> **grep 检索模式**：按档位 `grep -n "L0|L1|PPT|L3"`；按后端 `grep -n "anydoc|python-pptx|markitdown|pandoc|LibreOffice"`；按命令 `grep -n "命令"`。

---

## 一、五后端矩阵（2026-09 调研口径）

| 后端 | 档位 | 技术路线 | 许可证 | 格式 | 备注保留 | 图片 | 安装 | 定位 |
|---|---|---|---|---|---|---|---|---|
| **anydoc** | L0/L1/PPT 首选 | Rust 原生解析（PresentationML + 二进制记录流自研）→ 统一 GFM | **MIT** | .pptx/.pptm/.pps/.pot/.ppsx/.ppsm/.ppt 全族直读 | ✓（演讲者备注固定策略） | ✓（模型内 bytes，配 dump_assets.py 落盘；图表/SmartArt 文本化） | `pip install firecrawl-anydoc` 或 `npm i -g @firecrawl/anydoc` | 全链首选：基准 .pptx 74 / .ppt 80 全部第一，旧格式免 LibreOffice 中转 |
| **python-pptx** | L0 降级1 | 纯规则 | **MIT** | .pptx | ✓ | ✓（提取） | `pip install python-pptx`（极轻） | .pptx 快速提取 |
| **markitdown** | L0 降级2 | 纯规则 | MIT | .pptx | 有限 | ✓ | `pip install markitdown[all]` | 通用格式转 MD（29+ 格式）（M1 起兼作降级链 runner；M7 裁决起为 .pptx 降级链 python-pptx 之前首选） |
| **pandoc** | L1 降级 | 纯规则 | **GPL-2.0** | .pptx | ✓ | ✓ | https://pandoc.org/installing.html | 复杂版式/图表 |
| **LibreOffice** | PPT 降级（anydoc 缺失） | 渲染引擎 | **MPL-2.0** | .ppt/.pptx | ✓ | ✓ | https://www.libreoffice.org/download/ | .ppt 旧格式转中间 .pptx |

**兼容性说明**：WPS 生成的 .pptx/.ppt 与 Microsoft Office 同格式（OOXML/OLE），上述后端可直接处理；WPS 特有版式（如部分 SmartArt 变体）以图片资产保留。

---

## 二、四档分级策略与降级链

| 档位 | 适用场景 | 首选 | 降级链 | 预期质量 | 成本 |
|---|---|---|---|---|---|
| **L0 快速** | .pptx/.pptm/.ppsx/.ppsm 全场景 | anydoc | markitdown → python-pptx（仅 .pptx/.pptm） | 图表→MD 表格 + 备注保留（M7 裁决：markitdown 优先；基准 per-format 第一为 anydoc 主链） | 秒级 |
| **L1 标准** | anydoc 缺失时的 .pptx 复杂版式/图表 | pandoc | markitdown → python-pptx | 结构更完整，图表转 MD 表格（M7 裁决） | 秒级 |
| **PPT 旧格式** | .ppt/.pps/.pot（二进制记录流） | anydoc 直读 | LibreOffice headless 转 .pptx 中间格式 → L0/L1 链（anydoc 缺失时） | 直读免中转（基准 .ppt 80） | 秒级 |
| **L3 兜底** | 后端全失败或用户极致要求 | LLM 视觉 API | 商业 API | 不稳定，MUST 用户确认 | 付费 |

**降级触发**：① 后端执行失败/超时；② 门D 置信度 C 且用户要求重转；③ 探测到档位首选缺失。降级 MUST 记录轨迹进报告「降级轨迹」字段。

---

## 三、已验证命令（门C 执行参考）

> 后端版本漂移（CLI 参数变更）时 MUST 回填本节并更新版本号——进化契约触发条件之一。

### anydoc（L0/L1/PPT 首选，2026-09-08 已验证 v0.2.4）

```bash
# Python 绑定（import 探测通过后首选通道）
python -c "import anydoc, pathlib; pathlib.Path('<同名>.md').write_text(anydoc.to_markdown('<pptx|ppt|ppsm|...>'), encoding='utf-8')"
# CLI 通道（npx 免安装）
npx -y @firecrawl/anydoc <file> -o out.md
# 图片资产落盘（anydoc 资产契约唯一路径，P0-4）
python scripts/dump_assets.py --doc <file> --md <同名>.md
```

安装：`pip install firecrawl-anydoc`（Python 3.10+ wheel）或 `npm i -g @firecrawl/anydoc`（Node 20+）。

### python-pptx（L0 降级1，本机已验证 2026-08-24，v1.0.3）

```bash
python -c "import pptx; from pptx import Presentation; p = Presentation('<ppt>'); print(len(p.slides))"
```

### markitdown（L0 降级2，本机已验证 2026-08-24）

```bash
python -c "from markitdown import MarkItDown; r = MarkItDown().convert('<ppt>'); pathlib.Path('<同名>.md').write_text(r.text_content, encoding='utf-8')"
```

### pandoc（L1 降级）

```bash
pandoc "<ppt>" -t markdown -o "<同名>.md" --extract-media=assets
```

### LibreOffice（PPT 降级：anydoc 缺失时中间转换）

```bash
soffice --headless --convert-to pptx --outdir "<中间目录>" "<旧文件>.ppt"
# 转换后对中间 .pptx 走 L0/L1 标准链
```

### 图片资产补提（后端不提图时）

```bash
python -c "import pptx; from pptx import Presentation; p = Presentation('<ppt>'); [print([(s.shape_type, s.name) for s in sl.shapes]) for sl in p.slides]"
```

---

## 四、许可证口径（代码版权合规支撑）

- 本 skill 只**编排调用**后端官方 CLI/API，NEVER 复制后端源码——GPL/MPL 传染风险因此被隔离在「外部依赖调用」层面。
- **MIT**：python-pptx、markitdown。**GPL-2.0**：pandoc（CLI 调用，不链接分发）。**MPL-2.0**：LibreOffice（外部进程调用）。
- 用户对许可证敏感时，报告与执行日志 MUST 注明所用后端许可证口径。

---

## 五、后端演进记录

| 日期 | 变更 | 触发源 |
| 2026-09-08 | anydoc 0.2.4 接入为 L0/L1/PPT 全链首选（MIT，Python/CLI 双探测）；.ppt/.pps/.pot 路径改 anydoc 直读首选（冲突 4 裁定） | anydoc-main 蒸馏报告 v1.3.0 P0-1 |
|---|---|---|
| 2026-08-24 | 初版矩阵（四后端：python-pptx/markitdown/pandoc/LibreOffice） | tri-forge 门②生成 |
