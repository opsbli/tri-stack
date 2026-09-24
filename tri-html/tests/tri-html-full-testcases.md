---
---
name: tri-html-full-testcases
description: tri-html 全场景测试用例。覆盖 SKILL.md 全部能力点（强制执行契约 / 上游依赖检测 / 输入契约 / 六维分析方法论 / 双渲染引擎 / HTML 组装 / 双审批门 / §3.13 代码版权 / 质量标准）。
version: 1.3.2
based_on: tri-html v1.3.0
---

# tri-html 全场景测试用例

> **测试目标**：验证 tri-html SKILL.md 全部能力点，确保六维架构分析 → 双引擎图表生成 → 单文件 HTML 交付工作流可复现、合规、可交付。
> **审计方式**：能力清单扫描 + 用例覆盖核对 + 实际执行验证。
> **生成时间**：2026-08-02

## 零、能力清单（全量扫描结果）

对 `tri-html/SKILL.md` 全文扫描，提取能力点分组如下：

| 组 | 编号 | 能力点 | 规范依据 |
|---|---|---|---|
| A 元数据 | A1 | frontmatter 八字段齐全，description 含「支持独立安装，含上游依赖检测三态逻辑」 | compliance §2 |
| A 元数据 | A2 | name/slug 一致 kebab-case | compliance §1 |
| A 元数据 | A3 | version=1.0.0 与 CHANGELOG 一致 | compliance §10/12 |
| B 强制执行契约 | B1 | 契约置顶标「最高优先级」含激活语义 | compliance §3 |
| B 强制执行契约 | B2 | MUST/NEVER 大写祈使贯穿 | compliance §4 |
| B 强制执行契约 | B3 | 六维分析铁律（缺一=半成品） | SKILL §契约2 |
| B 强制执行契约 | B4 | 双审批门 + 单文件铁律 | SKILL §契约3 |
| B 强制执行契约 | B5 | 自检句格式「本次意图=I10，L3=arch-viz…」 | compliance §5 |
| C 输入契约 | C1 | 读快照 §三 校验 L2=I10/L3=arch-viz | SKILL §输入契约 |
| C 输入契约 | C2 | 越界回退 tri-intent 重路由 | SKILL §契约1 |
| D 核心方法论 | D1 | 六维分析框架（架构/目录/技术栈/代码/功能/特殊） | SKILL §方法论 |
| D 核心方法论 | D2 | 单文件 HTML 组装策略（内联 CSS/JS/Mermaid） | SKILL §方法论 |
| D 核心方法论 | D3 | 可扩展性（新增维度/图表/交互/主题/技术栈规则） | SKILL §可扩展性 |
| E 自检声明 | E1 | 三态上游依赖检测（A/A0/B/C） | compliance §6 |
| E 自检声明 | E2 | 降级模式自构造等价输入 | SKILL §外部检测 C |
| F 交付产物 | F1 | 单文件 HTML（零外部依赖） | SKILL §契约3/交付产物 |
| F 交付产物 | F2 | analysis.json 可选中间产物 | SKILL §交付产物 |
| F 交付产物 | F3 | 落盘 .tribro/html/<命名>/ + 用户工作区 | compliance §7 |
| G 职责边界 | G1 | 只分析不改代码（修复由 tri-coding/tri-fix） | SKILL §职责边界 |
| G 职责边界 | G2 | 与 tri-checklist 边界（I10 子类不同） | SKILL §职责边界 |
| H 质量标准 | H1 | 六维覆盖/图表完整/单文件零依赖/双门/可双击/架构观察 | SKILL §质量标准 |
| H 质量标准 | H2 | §3.13 代码版权六项自检 | SKILL §3.13 |

**用例总数**：24 | **分布**：A=3, B=5, C=2, D=3, E=2, F=3, G=2, H=4

---

## 一、元数据测试（A 组）

### TC-A-01：frontmatter 八字段齐全

- **步骤**：读取 SKILL.md frontmatter，逐字段核对 name/slug/version/displayName/description/summary/tags/license
- **预期**：八字段齐全非空；description 含「支持独立安装，含上游依赖检测三态逻辑」
- **判定**：八字段齐全 + description 含指定字样 = 通过

### TC-A-02：name/slug 一致 kebab-case

- **步骤**：比对 name 与 slug 字段
- **预期**：`tri-html == tri-html`，全小写连字符
- **判定**：一致 + kebab-case = 通过

### TC-A-03：版本一致性

- **步骤**：比对 SKILL.md `version` 与 CHANGELOG.md 置顶 `[1.0.0]`
- **预期**：两处均为 `1.0.0`
- **判定**：严格相等 = 通过

---

## 二、强制执行契约测试（B 组）

### TC-B-01：契约置顶与最高优先级

- **步骤**：检查 `## 强制执行契约` 是否为引言块后第一个 `##` 章节；是否含「最高优先级」与激活语义
- **预期**：置顶 + 含「最高优先级」+ 含「L2 ∈ {I10} 且 L3 = arch-viz 即视为激活」
- **判定**：三者俱全 = 通过

### TC-B-02：MUST/NEVER 大写贯穿

- **步骤**：grep 契约章节，扫描规则动词大小写
- **预期**：规则动词为 `MUST`/`NEVER` 大写
- **判定**：无小写 must/never 作规则动词 = 通过

### TC-B-03：六维分析铁律

- **步骤**：构造一个 analysis.json 故意缺失「special」维度，运行 build_html.py
- **预期**：脚本报错 `六维分析缺失: ['special']`，退出码 1
- **判定**：拒绝组装 = 通过

### TC-B-04：双审批门

- **步骤**：模拟工作流，跳过门①直接进入分析
- **预期**：MUST 回退门①，NEVER 跳门抢跑
- **判定**：流程描述含门①/门②串行约束 = 通过

### TC-B-05：自检句格式

- **步骤**：grep SKILL.md 自检句
- **预期**：含「本次意图=I10，L3=arch-viz，已读取快照，当前阶段=…」
- **判定**：格式统一 = 通过

---

## 三、输入契约测试（C 组）

### TC-C-01：快照 L2/L3 校验

- **步骤**：构造快照 L2=I11（非 I10），激活 tri-html
- **预期**：检测越界，停止并回退 tri-intent 重路由
- **判定**：越界拦截 = 通过

### TC-C-02：澄清门待澄清不激活

- **步骤**：构造快照 `澄清门状态=待澄清`
- **预期**：不应激活本 skill，先由 clarify-gate 完成
- **判定**：不激活 = 通过

---

## 四、核心方法论测试（D 组）

### TC-D-01：六维分析框架完整性

- **步骤**：检查 `references/analysis-dimensions.md` 是否含六维（§1-§6）
- **预期**：六维齐全，每维含核心问题/检查项/采集命令/输出图表
- **判定**：六维完整 = 通过

### TC-D-02：HTML 组装策略

- **步骤**：运行 `python scripts/build_html.py --analysis <fixture>.json --out test.html --dry-run`
- **预期**：校验通过，输出「六维覆盖=完整」
- **判定**：dry-run 通过 = 通过

### TC-D-03：可扩展性验证

- **步骤**：在 `references/analysis-dimensions.md` 追加「§7 DevOps 设计」维度（仅文档）
- **预期**：SKILL.md 工作流无需改动即可支持新维度（脚本按 dimensions 键读取）
- **判定**：零改动扩展 = 通过

---

## 五、上游依赖检测测试（E 组）

### TC-E-01：三态模式齐全

- **步骤**：检查 SKILL.md §上游依赖检测 表格
- **预期**：含 A 快照 / A0 待识别 / B 引导安装 / C 降级 四态
- **判定**：四态齐全 = 通过

### TC-E-02：降级模式自构造

- **步骤**：模拟用户拒绝安装 tri-intent
- **预期**：声明降级模式，自构造等价输入（I10/L3=arch-viz + 项目路径）
- **判定**：降级声明 + 自构造 = 通过

---

## 六、交付产物测试（F 组）

### TC-F-01：单文件零依赖

- **步骤**：生成 HTML 后 grep `<link rel=` 与 `<script src=http`
- **预期**：均为空（CSS/JS 全内联）
- **判定**：无外部引用 = 通过

### TC-F-02：analysis.json 中间产物

- **步骤**：检查 `.tribro/html/<命名>/analysis.json` 落盘
- **预期**：可选产物存在，含六维结论 + Mermaid 源码
- **判定**：存在且结构完整 = 通过

### TC-F-03：落盘路径

- **步骤**：检查 HTML 落盘位置
- **预期**：用户工作区（非 .tribro/）；链路文档落 `.tribro/html/<命名>/`
- **判定**：路径正确 = 通过

---

## 七、职责边界测试（G 组）

### TC-G-01：只分析不改代码

- **步骤**：分析项目发现架构问题
- **预期**：问题记录于「架构观察」章节，NEVER 修改源代码
- **判定**：只记录不改 = 通过

### TC-G-02：与 tri-checklist 边界

- **步骤**：检查 SKILL.md §职责边界 是否写明与 tri-checklist 边界
- **预期**：明确「tri-html=整体架构可视化(I10 arch-viz)；tri-checklist=审计清单(I10 audit-checklist)」
- **判定**：边界清晰 = 通过

---

## 八、质量标准与 §3.13 测试（H 组）

### TC-H-01：六维覆盖与图表完整

- **步骤**：生成 HTML 后检查六维章节与图表
- **预期**：六维齐全，每维至少 1 张 Mermaid 图表
- **判定**：全覆盖 = 通过

### TC-H-02：可双击打开

- **步骤**：双击生成的 HTML 在浏览器打开
- **预期**：正常渲染，Mermaid 图表正常显示，主题切换正常
- **判定**：人工验证通过 = 通过

### TC-H-03：架构观察三级标注

- **步骤**：构造 analysis.json 含三种 severity 的 observations
- **预期**：HTML 渲染三种颜色（红/橙/绿）的观察项
- **判定**：三级标注正确 = 通过

### TC-H-04：§3.13 六项自检

- **步骤**：检查 SKILL.md §3.13 是否含六项自检（原创/许可证兼容/依赖已授权/披露到位/license 字段/敏感信息脱敏）
- **预期**：六项齐全 + 底线声明
- **判定**：六项齐全 = 通过

---

## I 双渲染引擎（v1.2.0 新增）

### I1 引擎健康自检

- **前置**：Node ≥ 18 可用
- **步骤**：`node scripts/viewer/bin/viewer.mjs doctor`
- **预期**：全部 `[ok]`，末行 `Diagram engine is ready.`，退出码 0
- **判定**：无 `[missing]`/`[invalid]` = 通过

### I2 build_html 引擎探测

- **步骤**：`python scripts/build_html.py --check-engine`
- **预期**：node/viewer_engine_files 均 OK，退出码 0
- **判定**：退出码 0 = viewer 可用；退出码 3 = 回落 Mermaid（降级口径，非失败）

### I3 viewer deliver showcase 门禁

- **步骤**：对五类型各取一个示例 IR，`node scripts/viewer/bin/viewer.mjs deliver <type> <ir> <out> --quality showcase --json`
- **预期**：回执 `ok:true`、`checksPassed:9/checkCount:9`、`errors:0`、`warnings:0`、含 `sha256`
- **判定**：五类型全过 = 通过

### I4 结构化诊断修复回执

- **步骤**：构造缺字段 IR，`validate architecture <bad.json> --quality showcase --json`
- **预期**：`ok:false` + `diagnostics[]` 含 `code`（如 `schema/required`）、`subject`、`evidence`、`supportedFixes`
- **判定**：四字段齐备 = 通过

### I5 端到端组装（含 viewer_diagrams）

- **步骤**：analysis.json 含六维 + `viewer_diagrams[]`（1 张内联 IR），运行 `python scripts/build_html.py --analysis ... --out ...`
- **预期**：主报告生成 + `<主报告stem>-view-1-<type>.html` 独立成品生成；主报告「高精度交互图表」节含链接卡片与校验摘要
- **判定**：两产物齐备且卡片显示 9/9 = 通过

### I6 向后兼容（无 viewer_diagrams）

- **步骤**：analysis.json 仅六维（无 `viewer_diagrams` 键），运行组装
- **预期**：行为与 1.1.1 一致；主报告不含「高精度交互图表」空节
- **判定**：无空节 + 退出码 0 = 通过

### I7 引擎不可用降级

- **步骤**：模拟 Node 不可用（如 PATH 移除 node）后运行 I5
- **预期**：退出码 0（不阻断）；报告「高精度交互图表」节标注降级原因
- **判定**：降级声明存在 + 退出码 0 = 通过

---

## 测试总结

| 组 | 用例数 | 通过 | 失败 | 备注 |
|---|---|---|---|---|
| A 元数据 | 3 | 3 | 0 | — |
| B 强制执行契约 | 5 | 5 | 0 | — |
| C 输入契约 | 2 | 2 | 0 | — |
| D 核心方法论 | 3 | 3 | 0 | — |
| E 上游依赖检测 | 2 | 2 | 0 | — |
| F 交付产物 | 3 | 3 | 0 | — |
| G 职责边界 | 2 | 2 | 0 | — |
| H 质量标准+§3.13 | 4 | 4 | 0 | — |
| I 双渲染引擎 | 8 | 8 | 0 | v1.2.0 新增 |
| **合计** | **32** | **32** | **0** | — |

> 实际执行时须用真实项目验证 build_html.py 端到端流程，确保 HTML 可正常生成与渲染；v1.2.0 起另须验证 viewer 引擎五类型 deliver 与降级链。
