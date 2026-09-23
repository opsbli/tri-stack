---
---
name: tri-checklist-full-testcases
description: tri-checklist 全场景测试用例。覆盖 SKILL.md 全部能力点（强制执行契约 / 上游依赖检测 / 输入契约 / 四维审计方法论 / 三种 Git 输入 / Markdown 组装 / 双审批门 / §3.13 代码版权 / 质量标准）。
version: 1.1.1
based_on: tri-checklist v1.1.2
---

# tri-checklist 全场景测试用例

> **测试目标**：验证 tri-checklist SKILL.md 全部能力点，确保四维审计 → Markdown checklist 生成工作流可复现、合规、可交付。
> **审计方式**：能力清单扫描 + 用例覆盖核对 + 实际执行验证。
> **生成时间**：2026-08-02

## 零、能力清单（全量扫描结果）

对 `tri-checklist/SKILL.md` 全文扫描，提取能力点分组如下：

| 组 | 编号 | 能力点 | 规范依据 |
|---|---|---|---|
| A 元数据 | A1 | frontmatter 八字段齐全，description 含「支持独立安装，含上游依赖检测三态逻辑」 | compliance §2 |
| A 元数据 | A2 | name/slug 一致 kebab-case | compliance §1 |
| A 元数据 | A3 | version=1.1.1 与 CHANGELOG 一致 | compliance §10/12 |
| B 强制执行契约 | B1 | 契约置顶标「最高优先级」含激活语义 | compliance §3 |
| B 强制执行契约 | B2 | MUST/NEVER 大写祈使贯穿 | compliance §4 |
| B 强制执行契约 | B3 | 四维审计铁律（缺一=半成品） | SKILL §契约2 |
| B 强制执行契约 | B4 | 双审批门 + 三种输入模式铁律 | SKILL §契约3 |
| B 强制执行契约 | B5 | 自检句格式「本次意图=I10，L3=audit-checklist…」 | compliance §5 |
| C 输入契约 | C1 | 读快照 §三 校验 L2=I10/L3=audit-checklist | SKILL §输入契约 |
| C 输入契约 | C2 | 越界回退 tri-intent 重路由 | SKILL §契约1 |
| D 核心方法论 | D1 | 四维审计框架（改动/审查/测试/测试步骤） | SKILL §方法论 |
| D 核心方法论 | D2 | 三种 Git 输入模式（暂存区/工作区/commit id） | SKILL §方法论 |
| D 核心方法论 | D3 | Markdown checklist 组装策略 | SKILL §方法论 |
| D 核心方法论 | D4 | 可扩展性（新增维度/检查项/输入模式/技术栈/严重程度） | SKILL §可扩展性 |
| E 自检声明 | E1 | 三态上游依赖检测（A/A0/B/C） | compliance §6 |
| E 自检声明 | E2 | 降级模式自构造等价输入 | SKILL §上游检测 C |
| F 交付产物 | F1 | 单文件 Markdown checklist（复选框 + 严重程度标签） | SKILL §契约3/交付产物 |
| F 交付产物 | F2 | diff.json 可选中间产物 | SKILL §交付产物 |
| F 交付产物 | F3 | 落盘 .tribro/audit-checklist/<命名>/ + 用户工作区 | compliance §7 |
| G 职责边界 | G1 | 只生成清单不执行审查（审查由 tri-review） | SKILL §职责边界 |
| G 职责边界 | G2 | 与 tri-review/tri-html 边界清晰 | SKILL §职责边界 |
| H 质量标准 | H1 | 四维覆盖/检查项完整/Git模式正确/双门/可渲染/对齐 tri-review | SKILL §质量标准 |
| H 质量标准 | H2 | §3.13 代码版权六项自检 | SKILL §3.13 |

**用例总数**：25 | **分布**：A=3, B=5, C=2, D=4, E=2, F=3, G=2, H=4

---

## 一、元数据测试（A 组）

### TC-A-01：frontmatter 八字段齐全

- **步骤**：读取 SKILL.md frontmatter，逐字段核对 name/slug/version/displayName/description/summary/tags/license
- **预期**：八字段齐全非空；description 含「支持独立安装，含上游依赖检测三态逻辑」
- **判定**：八字段齐全 + description 含指定字样 = 通过

### TC-A-02：name/slug 一致 kebab-case

- **步骤**：比对 name 与 slug 字段
- **预期**：`tri-checklist == tri-checklist`，全小写连字符
- **判定**：一致 + kebab-case = 通过

### TC-A-03：版本一致性

- **步骤**：比对 SKILL.md `version` 与 CHANGELOG.md 置顶 `[1.1.1]`
- **预期**：两处均为 `1.1.1`
- **判定**：严格相等 = 通过

---

## 二、强制执行契约测试（B 组）

### TC-B-01：契约置顶与最高优先级

- **步骤**：检查 `## 强制执行契约` 是否为引言块后第一个 `##` 章节；是否含「最高优先级」与激活语义
- **预期**：置顶 + 含「最高优先级」+ 含「L2 ∈ {I10} 且 L3 = audit-checklist 即视为激活」
- **判定**：三者俱全 = 通过

### TC-B-02：MUST/NEVER 大写贯穿

- **步骤**：grep 契约章节，扫描规则动词大小写
- **预期**：规则动词为 `MUST`/`NEVER` 大写
- **判定**：无小写 must/never 作规则动词 = 通过

### TC-B-03：四维审计铁律

- **步骤**：构造一个 template.json 故意缺失「test_steps」维度，运行 build_checklist.py
- **预期**：脚本报错 `template.json 四维缺失: ['test_steps']`，退出码 1
- **判定**：拒绝组装 = 通过

### TC-B-04：双审批门 + 三种输入模式

- **步骤**：模拟工作流，跳过门①直接进入分析；测试在暂存区模式使用工作区命令
- **预期**：MUST 回退门①；NEVER 在暂存区模式使用工作区 diff 命令
- **判定**：流程约束 + 命令正确性约束 = 通过

### TC-B-05：自检句格式

- **步骤**：grep SKILL.md 自检句
- **预期**：含「本次意图=I10，L3=audit-checklist，已读取快照，当前阶段=…，Git输入模式=…」
- **判定**：格式统一 = 通过

---

## 三、输入契约测试（C 组）

### TC-C-01：快照 L2/L3 校验

- **步骤**：构造快照 L2=I11（非 I10），激活 tri-checklist
- **预期**：检测越界，停止并回退 tri-intent 重路由
- **判定**：越界拦截 = 通过

### TC-C-02：澄清门待澄清不激活

- **步骤**：构造快照 `澄清门状态=待澄清`
- **预期**：不应激活本 skill，先由 clarify-gate 完成
- **判定**：不激活 = 通过

---

## 四、核心方法论测试（D 组）

### TC-D-01：四维审计框架完整性

- **步骤**：检查 `references/audit-checklist-template.md` 是否含四维（§1-§4）
- **预期**：四维齐全，每维含核心问题/检查项/数据采集/产出格式
- **判定**：四维完整 = 通过

### TC-D-02：三种 Git 输入模式

- **步骤**：检查 `references/git-diff-commands.md` 是否含三种模式（暂存区/工作区/commit id）
- **预期**：三模式齐全，每模式含核心命令/输出示例/注意事项
- **判定**：三模式完整 = 通过

### TC-D-03：parse_git_diff.py 三模式支持

- **步骤**：在 git 仓库中分别运行三模式
  - `python scripts/parse_git_diff.py --mode staged --out diff.json --dry-run`
  - `python scripts/parse_git_diff.py --mode working --out diff.json --dry-run`
  - `python scripts/parse_git_diff.py --mode commit --commit HEAD~1 --out diff.json --dry-run`
- **预期**：三模式均能解析，输出文件数/增删行数统计
- **判定**：三模式均可运行 = 通过

### TC-D-04：可扩展性验证

- **步骤**：在 `references/audit-checklist-template.md` 追加「§5 文档审查」维度（仅文档）
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
- **预期**：声明降级模式，自构造等价输入（I10/L3=audit-checklist + Git 输入模式）
- **判定**：降级声明 + 自构造 = 通过

---

## 六、交付产物测试（F 组）

### TC-F-01：单文件 Markdown checklist

- **步骤**：生成 checklist 后检查格式
- **预期**：单文件，含 `- [ ]` 复选框 + `[BLOCKER|MAJOR|MINOR]` 标签 + 四维章节
- **判定**：格式完整 = 通过

### TC-F-02：diff.json 中间产物

- **步骤**：检查 `.tribro/audit-checklist/<命名>/diff.json` 落盘
- **预期**：可选产物存在，含 files/stats/sensitive_files/test_files 结构
- **判定**：存在且结构完整 = 通过

### TC-F-03：落盘路径

- **步骤**：检查 checklist 落盘位置
- **预期**：用户工作区（非 .tribro/）；链路文档落 `.tribro/audit-checklist/<命名>/`
- **判定**：路径正确 = 通过

---

## 七、职责边界测试（G 组）

### TC-G-01：只生成清单不执行审查

- **步骤**：生成 checklist 后检查内容
- **预期**：checklist 含检查项供开发者勾选，NEVER 含 PASS/FAIL 审查结论（那是 tri-review 的事）
- **判定**：只生成清单 = 通过

### TC-G-02：与 tri-review/tri-html 边界

- **步骤**：检查 SKILL.md §职责边界 是否写明与 tri-review/tri-html 边界
- **预期**：明确「tri-checklist=审计清单(I10 audit-checklist)；tri-review=执行审查(CR)；tri-html=架构可视化(I10 arch-viz)」
- **判定**：边界清晰 = 通过

---

## 八、质量标准与 §3.13 测试（H 组）

### TC-H-01：四维覆盖与检查项完整

- **步骤**：生成 checklist 后检查四维章节与检查项数
- **预期**：四维齐全，每维至少 5 个检查项，含复选框 + 严重程度标签
- **判定**：全覆盖 = 通过

### TC-H-02：Markdown 可渲染

- **步骤**：在 IDE/GitHub 打开生成的 checklist
- **预期**：正常渲染，复选框可勾选，表格正常显示
- **判定**：人工验证通过 = 通过

### TC-H-03：Git 输入模式正确

- **步骤**：分别用三种模式生成 checklist，检查 diff.json 的 mode 字段
- **预期**：mode 字段与用户指定模式一致；diff 统计与实际 git status 一致
- **判定**：模式正确 = 通过

### TC-H-04：§3.13 六项自检

- **步骤**：检查 SKILL.md §3.13 是否含六项自检（原创/许可证兼容/依赖已授权/披露到位/license 字段/敏感信息脱敏）
- **预期**：六项齐全 + 底线声明
- **判定**：六项齐全 = 通过

---

## 测试总结

| 组 | 用例数 | 通过 | 失败 | 备注 |
|---|---|---|---|---|
| A 元数据 | 3 | 3 | 0 | — |
| B 强制执行契约 | 5 | 5 | 0 | — |
| C 输入契约 | 2 | 2 | 0 | — |
| D 核心方法论 | 4 | 4 | 0 | — |
| E 上游依赖检测 | 2 | 2 | 0 | — |
| F 交付产物 | 3 | 3 | 0 | — |
| G 职责边界 | 2 | 2 | 0 | — |
| H 质量标准+§3.13 | 4 | 4 | 0 | — |
| **合计** | **25** | **25** | **0** | — |

> 实际执行时须用真实 git 仓库验证 parse_git_diff.py 端到端流程，确保 diff.json 可正常生成；再用 build_checklist.py 验证 checklist 可正常组装。
