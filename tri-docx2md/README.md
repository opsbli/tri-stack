# tri-docx2md · Word 转 Markdown（编排与质量保障层）

> tri-xxx 家族路由型 skill，认领 **I08 翻译转换 · L3 子意图 `docx2md`**（经 tri-intent 一跳覆写路由）。也可独立运行。
> 核心理念：**先体检、再选刀、干完活、必须交验**——把「无损」落为可验证的分级保真；**Word 视为有结构、有修订语义的数据源**，标题/表格/图片语义框架硬编码保留与计数，全链路可控不依赖模型自觉。

## 特性

- **四阶段管道**：门A 预检分级（`preflight.py`）→ 门B 后端探测（`detect_backends.py`）→ 门C 结构降维转换（保留标题层级/表格/图片引用）→ 门D 质量校验（`quality_check.py`）
- **三后端全链首选 anydoc（Firecrawl，MIT）**：L0/L1/DOC 档降级链固定 anydoc → mammoth/markitdown/python-docx → pandoc；`.doc` 旧格式 anydoc 直读首选（自研 MS-DOC 解析器），anydoc 缺失时才降级 LibreOffice 中转（antiword 纯文本兜底）；图片资产经 dump_assets.py 落盘
- **P2 方法论落地（anydoc 蒸馏）**：输入规模守卫 `scripts/scale_guard.py`（anydoc limits.rs 硬上限，表格类网格槽位超预算强制 L1）+ `tests/mutation_smoke.py` 变异冒烟（可失败但永不挂起）+ 「绝不半成品交付」条款 + 可选质量四维 LLM 抽评（默认关闭，用户二次确认后启用）
- **双格式兼容**：.docx（OOXML）与 .doc（OLE 二进制）双格式；WPS 生成的 .docx/.doc 同格式兼容
- **保真度契约**：报告 MUST 含**保真率、丢失率**等关键数据（结构对比/置信度 A/B/C/异常清单/固定复核项）——用户硬要求
- **诚实边界**：Word→MD 是「结构降维」（批注/修订/页眉页脚/嵌入对象必然丢失）；OOXML 加密不破解（BLOCK）；图表提资产不转正文；GPL 后端只调用不分发

## 目录结构

```
tri-docx2md/
├── SKILL.md                       主入口（契约 + 四阶段管道 + 保真度契约 + 代码版权合规）
├── README.md                      本文件
├── CHANGELOG.md                   Keep a Changelog + SemVer
├── _meta.json                     平台元数据 + 档位/阈值配置
├── references/
│   ├── backends.md                后端矩阵（能力/安装/许可证/已验证命令）
│   ├── fidelity-spec.md           保真度分级规范（阈值唯一真源 + 复核项清单）
│   └── version-check-spec.md      版本检查与更新规范（内部唯一真源）
├── scripts/
│   ├── preflight.py               门A：预检分级
│   ├── detect_backends.py         门B：后端探测与档位决策
│   ├── quality_check.py           门D：质量校验与报告生成
│   └── check_update.py            版本检查与更新（家族同源）
└── tests/
    └── tri-docx2md-full-testcases.md  全场景全能力测试用例
```

## 安装

```bash
skillhub install tri-docx2md --dir <目标目录>
# 或本地源树直接复制 tri-docx2md/ 到 skills 识别路径
```

上游（可选增强）：`skillhub install tri-intent`——安装后「把 xxx.docx 转成 MD」会被自动识别为 I08·docx2md 并路由到本 skill。

## 使用

```bash
# 门A 预检（等级建议 + 风险项）
python scripts/preflight.py --doc doc.docx --json

# 门B 探测（选定后端 + 降级链 + 缺失安装指引；.doc 加 --doc-format）
python scripts/detect_backends.py --grade L0 --json
python scripts/detect_backends.py --grade L1 --doc-format --json

# 门C 结构降维转换（按 references/backends.md §三 已验证命令执行所选后端；
# .doc 先 soffice --headless --convert-to docx 转中间格式）

# 门D 校验与报告（产出 report.md：保真率/丢失率/置信度等关键数据）
python scripts/quality_check.py --doc doc.docx --md doc.md --backend mammoth --grade L0 --json
```

交付：`<同名>.md` + `assets/` + `report.md`，落 Word 同目录或用户指定目录。

## 测试

见 `tests/tri-docx2md-full-testcases.md`：能力清单扫描 + 分组用例（管道/降级/保真/边界/合规/版本），基于 tri-docx2md v1.4.4。

## 设计原则

- **编排不重造**：复用成熟后端官方 CLI/API，不自研文档解析引擎
- **确定性下沉**：预检/探测/校验全部脚本化输出 JSON，prompt 层不做数值推断
- **可验证分级保真**：「无损」重定义为保真率可计算、置信度可分级、复核项可执行
- **结构降维诚实**（铁律）：批注/修订/页眉页脚/嵌入对象必然丢失，承诺「可验证的分级保真」而非绝对无损
- **MECE 边界**：仅认领 I08·docx2md；PDF 转 MD 归 tri-pdf2md，语言翻译归 tri-content/tri-translate，Word 文档操作归内置 docx skill
