# tri-pptx2md · PPT 转 Markdown（编排与质量保障层）

> tri-xxx 家族路由型 skill，认领 **I08 翻译转换 · L3 子意图 `pptx2md`**（经 tri-intent 一跳覆写路由）。也可独立运行。
> 核心理念：**先体检、再选刀、干完活、必须交验**——把「无损」落为可验证的分级保真；**PPT 视为有时效、有结构的数据源**，页序锚点框架硬编码，全链路可控不依赖模型自觉。

## 特性

- **四门管道**：门A 预检分级（`preflight.py`）→ 门B 后端探测（`detect_backends.py`）→ 门C 结构降维转换（每页 Slide 块 + 标题/正文/备注/图片引用）→ 门D 质量校验（`quality_check.py`）
- **双格式兼容**：.pptx（OOXML）与 .ppt（旧二进制 OLE）；WPS 生成的 .pptx/.ppt 同格式兼容
- **anydoc 全族直读首选（Firecrawl，MIT）**：L0（.pptx/.pptm/.ppsx/.ppsm）与 PPT 旧格式（.ppt/.pps/.pot 直读）均为 anydoc 首选；降级链 python-pptx/markitdown → pandoc → LibreOffice（anydoc 缺失时中转）→ L3 LLM 兜底（须确认成本）；图片资产经 dump_assets.py 落盘
- **P2 方法论落地（anydoc 蒸馏）**：输入规模守卫 `scripts/scale_guard.py`（anydoc limits.rs 硬上限，表格类网格槽位超预算强制 L1）+ `tests/mutation_smoke.py` 变异冒烟（可失败但永不挂起）+ 「绝不半成品交付」条款 + 可选质量四维 LLM 抽评（默认关闭，用户二次确认后启用）
- **保真度契约**：报告 MUST 含**页覆盖率、文本召回率、丢失率**等关键数据（缺页明细/结构对比/置信度 A/B/C/异常清单/固定复核项）——用户硬要求
- **输出结构**：每张 slide 一个 `## Slide N` 二级标题块（标题 + 正文要点 + 备注引用块 + 图片引用），图片提取为 `assets/`，演讲者备注保留为引用块
- **诚实边界**：非 PPT 文件 BLOCK；动画/过渡/母版/精确排版必然丢失（结构降维）；图表/SmartArt 提资产不转正文；GPL/MPL 后端只调用不分发

## 目录结构

```
tri-pptx2md/
├── SKILL.md                       主入口（契约 + 四门管道 + 保真度契约 + 代码版权合规）
├── README.md                      本文件
├── CHANGELOG.md                   Keep a Changelog + SemVer
├── _meta.json                     平台元数据 + 档位/阈值配置
├── references/
│   ├── backends.md                后端矩阵（能力/安装/许可证/已验证命令）
│   ├── fidelity-spec.md           保真度分级规范（阈值唯一真源 + 复核项清单）
│   └── version-check-spec.md      版本检查与更新规范（内部唯一真源）
├── scripts/
│   ├── preflight.py               门A：预检分级（文件类型/页数/备注/图片/旧格式）
│   ├── detect_backends.py         门B：四后端探测与档位决策
│   ├── quality_check.py           门D：质量校验与报告生成
│   └── check_update.py            版本检查与更新（家族同源）
└── tests/
    └── tri-pptx2md-full-testcases.md  全场景全能力测试用例
```

## 安装

```bash
skillhub install tri-pptx2md --dir <目标目录>
# 或本地源树直接复制 tri-pptx2md/ 到 skills 识别路径
```

上游（可选增强）：`skillhub install tri-intent`——安装后「把 xxx.pptx 转成 MD」会被自动识别为 I08·pptx2md 并路由到本 skill。

## 使用

```bash
# 门A 预检（等级建议 + 风险项）
python scripts/preflight.py --ppt deck.pptx --json

# 门B 探测（选定后端 + 降级链 + 缺失安装指引）
python scripts/detect_backends.py --grade L0 --json

# 门C 结构降维转换（按 references/backends.md §三 已验证命令执行所选后端）

# 门D 校验与报告（产出 report.md：页覆盖率/文本召回率/置信度等关键数据）
python scripts/quality_check.py --ppt deck.pptx --md deck.md --backend python-pptx --grade L0 --json
```

交付：`<同名>.md` + `assets/` + `report.md`，落 PPT 同目录或用户指定目录。

## 测试

见 `tests/tri-pptx2md-full-testcases.md`：能力清单扫描 + 分组用例（管道/降级/保真/边界/合规/版本），基于 tri-pptx2md v1.4.4。

门D 召回率口径另附零依赖回归自检（跨页粘连/全角数字/低召回判 C/多写 Slide 块）：

```bash
python scripts/verify_recall.py      # 退出码 0 全过 / 1 存在 FAIL
```

## 设计原则

- **编排不重造**：复用成熟后端官方 CLI/API，不自研 PPT 解析/渲染引擎
- **确定性下沉**：预检/探测/校验全部脚本化输出 JSON，prompt 层不做数值推断
- **可验证分级保真**：「无损」重定义为页覆盖率可计算、置信度可分级、复核项可执行
- **结构降维诚实**：动画/过渡/母版/精确排版必然丢失，图表以图片资产保留；承诺「可验证的分级保真」而非绝对无损
- **MECE 边界**：仅认领 I08·pptx2md；PPT 其它操作归内置 pptx skill，翻译归 tri-content/tri-translate，PDF→MD 归 tri-pdf2md
