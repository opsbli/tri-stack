# tri-html2md · HTML 转 Markdown（编排与质量保障层）

> tri-xxx 家族路由型 skill，认领 **I08 翻译转换 · L3 子意图 `html2md`**（经 tri-intent 一跳覆写路由）。也可独立运行。
> 核心理念：**先体检、再选刀、干完活、必须交验**——把「无损」落为可验证的分级保真；**HTML 视为有时效、有结构的数据源**，结构锚点框架硬编码，全链路可控不依赖模型自觉。

## 特性

- **四阶段管道**：门A 预检分级（`preflight.py`：编码检测/HTML 合法性/内嵌资源/表格表单计数）→ 门B 后端探测（`detect_backends.py`）→ 门C 转换执行（保留标题层级/表格/图片/链接）→ 门D 质量校验（`quality_check.py`）
- **P2 方法论落地（anydoc 蒸馏）**：输入规模守卫 `scripts/scale_guard.py`（anydoc limits.rs 硬上限）+ `tests/mutation_smoke.py` 变异冒烟（仅门A，可失败但永不挂起）+ 「绝不半成品交付」条款 + 可选质量四维 LLM 抽评（默认关闭，用户二次确认后启用）
- **两档降级链**：L0 快速（markitdown/html2text/beautifulsoup4）→ L1 标准（pandoc/trafilatura）；**无 L2/L3**（HTML 已有语义结构，不需要 OCR 档）
- **保真度契约**：报告 MUST 含**文本召回率、丢失率**等关键数据（噪声率/结构对比/置信度 A/B/C/异常清单/固定复核项）——用户硬要求
- **结构对比可核对**：标题 h1-h6/表格/图片/链接：HTML 侧计数 vs MD 侧计数，逐项比对
- **编码检测**：BOM → meta charset → 候选解码探测（utf-8/gbk 等），中文乱码（U+FFFD/锟斤拷）入异常清单
- **诚实边界**：编码不可解不猜测；HTML 无可见文本召回率显式「不适用」不编造；图片提资产不转正文；GPL 后端只调用不分发

## 目录结构

```
tri-html2md/
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
    └── tri-html2md-full-testcases.md  全场景全能力测试用例
```

## 安装

```bash
skillhub install tri-html2md --dir <目标目录>
# 或本地源树直接复制 tri-html2md/ 到 skills 识别路径
```

上游（可选增强）：`skillhub install tri-intent`——安装后「把 xxx.html 转成 MD」会被自动识别为 I08·html2md 并路由到本 skill。

## 使用

```bash
# 门A 预检（等级建议 + 风险项）
python scripts/preflight.py --html page.html --json

# 门B 探测（选定后端 + 降级链 + 缺失安装指引）
python scripts/detect_backends.py --grade L0 --json

# 门C 转换执行（按 references/backends.md §三 已验证命令执行所选后端）

# 门D 校验与报告（产出 report.md：文本召回率/丢失率/置信度等关键数据）
python scripts/quality_check.py --html page.html --md page.md --backend markitdown --grade L0 --json
```

交付：`<同名>.md` + `assets/` + `report.md`，落 HTML 同目录或用户指定目录。

## 测试

见 `tests/tri-html2md-full-testcases.md`：能力清单扫描 + 分组用例（管道/降级/保真/边界/合规/版本），基于 tri-html2md v1.3.4。

## 设计原则

- **编排不重造**：复用成熟后端官方 CLI/API，不自研 HTML 解析引擎
- **确定性下沉**：预检/探测/校验全部脚本化输出 JSON，prompt 层不做数值推断
- **可验证分级保真**：「无损」重定义为文本召回率可计算、置信度可分级、复核项可执行
- **有时效、有结构的数据源**（用户硬要求）：版本（时效）与结构锚点（标题层级/表格/图片/链接）框架硬编码写入每个产物，全链路可控，NEVER 依赖模型自觉
- **MECE 边界**：仅认领 I08·html2md；HTML 抓取/渲染归浏览器工具，翻译归 tri-content/tri-translate，PDF→MD 归 tri-pdf2md
