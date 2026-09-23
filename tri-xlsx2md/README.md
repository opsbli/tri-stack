# tri-xlsx2md · Excel 转 Markdown（编排与质量保障层）

> tri-xxx 家族路由型 skill，认领 **I08 翻译转换 · L3 子意图 `xlsx2md`**（经 tri-intent 一跳覆写路由）。也可独立运行。
> 核心理念：**先体检、再选刀、干完活、必须交验**——把「无损」落为可验证的分级保真；**Excel 视为有时效、有结构的数据源**，工作表/单元格坐标锚点框架硬编码，全链路可控不依赖模型自觉。

## 特性

- **四阶段管道**：门A 预检分级（`preflight.py`）→ 门B 后端探测（`detect_backends.py`）→ 门C 结构降维转换（每工作表一个 `## Sheet` 块 + Markdown 表格 + 合并单元格展开）→ 门D 质量校验（`quality_check.py`）
- **anydoc 全族直读首选（Firecrawl，MIT）**：L0/L1 均为 anydoc 首选（.xlsx/.xlsm/.xls/.xlsb/.csv 直读，合并单元格网格不变量）；降级链 openpyxl/markitdown/xlrd → pandas/LibreOffice headless
- **P2 方法论落地（anydoc 蒸馏）**：输入规模守卫 `scripts/scale_guard.py`（anydoc limits.rs 硬上限，表格类网格槽位超预算强制 L1）+ `tests/mutation_smoke.py` 变异冒烟（可失败但永不挂起）+ 「绝不半成品交付」条款 + 可选质量四维 LLM 抽评（默认关闭，用户二次确认后启用）
- **双格式兼容**：.xlsx（OOXML）与 .xls（旧二进制 BIFF）双格式；WPS 生成的 .xlsx/.xls 同格式兼容
- **保真度契约**：报告 MUST 含**单元格覆盖率、工作表数对比**等关键数据（行数对比/置信度 A/B/C/异常清单/固定复核项）——用户硬要求
- **结构降维诚实边界**：公式默认取缓存值（公式语义丢失）、格式/图表/数据透视不转正文、合并单元格展开为左上角值 + 其余空——NEVER 声称无损
- **加密不破解**：xlsx OOXML 加密 / xls BIFF FILEPASS 无法解密时 BLOCK 停止，提示合法解密后重试

## 目录结构

```
tri-xlsx2md/
├── SKILL.md                       主入口（契约 + 四阶段管道 + 保真度契约 + 代码版权合规）
├── README.md                      本文件
├── CHANGELOG.md                   Keep a Changelog + SemVer
├── _meta.json                     平台元数据 + 档位/阈值配置
├── references/
│   ├── backends.md                后端矩阵（能力/安装/许可证/已验证命令）
│   └── fidelity-spec.md           保真度分级规范（阈值唯一真源 + 复核项清单）
├── scripts/
│   ├── preflight.py               门A：预检分级
│   ├── detect_backends.py         门B：后端探测与档位决策
│   ├── quality_check.py           门D：质量校验与报告生成
│   └── check_update.py            版本检查与更新（家族同源）
└── tests/
    └── tri-xlsx2md-full-testcases.md  全场景全能力测试用例
```

## 安装

```bash
skillhub install tri-xlsx2md --dir <目标目录>
# 或本地源树直接复制 tri-xlsx2md/ 到 skills 识别路径
```

上游（可选增强）：`skillhub install tri-intent`——安装后「把 xxx.xlsx 转成 MD」会被自动识别为 I08·xlsx2md 并路由到本 skill。

后端依赖（按需）：`pip install openpyxl xlrd pandas markitdown[all]`；L1 公式求值可选安装 LibreOffice（`soffice --headless`）。

## 使用

```bash
# 门A 预检（等级建议 + 风险项）
python scripts/preflight.py --xlsx data.xlsx --json

# 门B 探测（选定后端 + 降级链 + 缺失安装指引）
python scripts/detect_backends.py --grade L0 --type xlsx --json

# 门C 结构降维转换（按 references/backends.md §三 已验证命令执行所选后端）

# 门D 校验与报告（产出 report.md：单元格覆盖率/工作表数对比/置信度等关键数据）
python scripts/quality_check.py --xlsx data.xlsx --md data.md --backend openpyxl --grade L0 --json
```

交付：`<同名>.md` + `report.md`，落 Excel 同目录或用户指定目录。

## 测试

见 `tests/tri-xlsx2md-full-testcases.md`：能力清单扫描 + 分组用例（管道/降级/保真/边界/合规/版本），基于 tri-xlsx2md v1.3.4。

## 设计原则

- **编排不重造**：复用成熟后端官方 CLI/API，不自研表格解析引擎
- **确定性下沉**：预检/探测/校验全部脚本化输出 JSON，prompt 层不做数值推断
- **可验证分级保真**：「无损」重定义为单元格覆盖率可计算、置信度可分级、复核项可执行
- **结构降维诚实**：Excel→MD 是结构降维，公式取缓存值、格式/图表/数据透视丢失 MUST 显式告知
- **MECE 边界**：仅认领 I08·xlsx2md；Excel 其它操作归内置 xlsx skill，翻译归 tri-content/tri-translate
