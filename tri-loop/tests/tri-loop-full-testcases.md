---
---
name: tri-loop-full-testcases
description: 基于 tri-loop v1.2.2 全量扫描生成的覆盖全场景全能力测试用例集，供人工审计。覆盖 frontmatter 元数据、5 条强制执行契约、上游依赖检测（A/A0/B/C）、输入契约、substrate bootstrap、charter 收集、README scaffold、真实测试运行、Timeline+LOG.md 记录、回报、落盘规则、质量标准八维、安全约束与最小化原则。
version: 1.2.2
---

# tri-loop 全场景测试用例

> 被测对象：`tri-loop` v1.2.2（下游执行 skill：I14 · loop/domain 创建子类）
> 本文件覆盖 tri-loop skill 的全部能力路径，包括依赖检测、substrate bootstrap、charter 收集、scaffold、真实测试运行、记录、回报，以及边界条件和异常处理。
> 审计方式：逐条对照「预期行为 / 预期输出 / 验证点」独立判定。

---

## 零、能力清单（全量扫描结果）

> 以下为对 tri-loop SKILL.md 全部内容的扫描提取，测试用例须覆盖每一项能力点。

### A. 元数据能力

| 编号 | 能力点 | 规范 |
|---|---|---|
| A1 | name / slug 一致（tri-loop） | frontmatter |
| A2 | version 存在且与 CHANGELOG 最新条目一致（1.2.1） | frontmatter |
| A3 | displayName / summary 描述 substrate bootstrap + charter + scaffold + 测试运行 + 记录全链路 | frontmatter |
| A4 | description 含「支持独立安装，含上游依赖检测三态逻辑」等效表述 | frontmatter |
| A5 | tags 含 loop/domain/knowledge-base/bootstrap；license=MIT | frontmatter |

### B. 强制执行契约能力

| 编号 | 能力点 | 规范 |
|---|---|---|
| B1 | 强制前置：先读快照 §三，核心铁律「没有 charter 的 loop 不启动」 | 契约① |
| B2 | 串行链路：substrate 检测 → charter → scaffold → 真实测试运行 → 记录 → 回报 | 契约② |
| B3 | 最小化原则：只做任务要点范围内操作，扩范围须确认 | 契约③ |
| B4 | 职责边界：不做意图识别/编码/内容产出/通用操作 | 契约④ |
| B5 | 自检句格式统一（意图/快照/substrate/charter/测试运行/记录） | 契约⑤ |

### C. 上游依赖检测与输入契约

| 编号 | 能力点 | 规范 |
|---|---|---|
| C1 | 模式 A 快照模式（LATEST 指针 → 会话内最新 → 全局 ≤30min） | §上游依赖检测 |
| C2 | 模式 A0 待识别（有 tri-intent 无可用快照） | §上游依赖检测 |
| C3 | 模式 B 引导安装（用户拒绝降级时硬提示） | §上游依赖检测 |
| C4 | 模式 C 降级模式（内联澄清 5 项输入，自构造等价输入） | §上游依赖检测 |
| C5 | 快照字段映射（L2/D1/D2/D4/任务要点/交付预期） | §输入契约 |
| C6 | 触发语义识别（loop/domain/循环/知识库/beat/workstream/charter/cadence） | §触发时机 |

### D. Substrate Bootstrap 能力

| 编号 | 能力点 | 规范 |
|---|---|---|
| D1 | 检测三要素：ARCHITECTURE.md + LOG.md + CLAUDE.md(Knowledge base 章节) | §Substrate Bootstrap 流程 |
| D2 | 从 `templates/architecture.md` / `templates/log.md` 逐字拷贝缺失文件 | §Substrate Bootstrap 流程 |
| D3 | 创建 signals/ docs/ domains/ 及各自 README（README 即 schema） | §Substrate Bootstrap 流程 |
| D4 | CLAUDE.md 已存在无 KB 章节 → 仅追加 `templates/claude-kb-section.md` | §Substrate Bootstrap 流程 |
| D5 | idempotent：仅创建缺失内容，绝不覆盖已有文件 | §Substrate Bootstrap 流程 |
| D6 | 不预建 `tasks/` 或其他 kind | §Substrate Bootstrap 流程 / §注意事项 |

### E. Charter 收集与 Scaffold 能力

| 编号 | 能力点 | 规范 |
|---|---|---|
| E1 | Charter 5 项输入（name/goal/cadence/做什么/工具数据）与默认值 | §处理流程 · Charter 5 项输入 |
| E2 | 收集策略：能推断则推断，仅对缺失项做一轮简短澄清 | §处理流程 · Charter 5 项输入 |
| E3 | 从 `templates/loop-readme.md` 创建 `domains/<name>/README.md` | §处理流程 |
| E4 | 冲突检查：`domains/<name>/` 已存在 → 停止并询问，不覆盖 | §处理流程 / §安全约束 |
| E5 | loop README 必需章节（frontmatter + Current focus + Backlog + Timeline） | §交付产物 · 产物结构规格 |

### F. 测试运行与记录能力

| 编号 | 能力点 | 规范 |
|---|---|---|
| F1 | 小规模真实运行（真实工具/数据优先） | §处理流程 · 真实测试运行 |
| F2 | 凭证缺失 → 最远 dry run 并记录差距 | §处理流程 · 真实测试运行 |
| F3 | artifact 可选，仅当确实产出 signal/doc 时创建 | §处理流程 · 真实测试运行 |
| F4 | Timeline 一行记录格式 | §处理流程 · 记录格式 |
| F5 | LOG.md 一条记录格式（标题 + What + Refs） | §处理流程 · 记录格式 |
| F6 | 两个记录 MUST 有，无论是否产出 artifact | 契约② |
| F7 | 回报：charter + 测试结果 + artifact + 缺失项 + 如何再运行 | §处理流程 |

### G. 落盘与产物能力

| 编号 | 能力点 | 规范 |
|---|---|---|
| G1 | result.md 落盘 `.tribro/loops/<命名>/`，基于 `templates/result.md` | §落盘规则 |
| G2 | 知识库内容文件落知识库仓库根目录，与 tri 链路文档路径分离 | §落盘规则 |
| G3 | 命名沿用快照 `<问题类型>_<日期>_<时间>_<会话ID>` | §交付产物 |
| G4 | `.tribro/loops/` 与 snapshots/actions 同级 | §落盘规则 |
| G5 | 执行结果落盘后不修改；知识库内容文件可覆盖更新 | §落盘规则 |

### H. 质量标准与安全约束

| 编号 | 能力点 | 规范 |
|---|---|---|
| H1 | loop 可验证运行（README 存在 + Timeline 非空） | §质量标准 |
| H2 | 执行结果落盘（result.md 存在且非空） | §质量标准 |
| H3 | charter 完整（5 项全有值） | §质量标准 |
| H4 | substrate 一致 / 记录可追溯 / idempotent / 最小化 / .tribro 目录一致 | §质量标准 |
| H5 | L1 可逆操作免确认；覆盖已有 domain、修改已有 CLAUDE.md 为 L2 必须确认 | §安全约束 |
| H6 | 不过度装饰 scaffold；近似副本应并入已有 loop | §注意事项 |

> 能力组 → 测试组映射：A→元数据核对；B→TG-8/TG-9 + 各组自检；C→TG-1；D→TG-2；E→TG-3/TG-4；F→TG-5/TG-6/TG-7；G→TG-11；H→TG-8/TG-9/TG-10。

---

## 测试矩阵概览

| 测试组 | 用例数 | 覆盖范围 |
|---|---|---|
| TG-1 三态依赖检测 | 6 | Mode A/B/C 全路径 |
| TG-2 Substrate Bootstrap | 5 | 全存在/部分缺失/全缺失/idempotent/不预建 |
| TG-3 Charter 收集 | 5 | 全推断/部分澄清/全澄清/请求已具体/缺失凭证 |
| TG-4 Scaffold | 4 | 正常创建/冲突检查/模板填充/最小化 |
| TG-5 真实测试运行 | 5 | 有artifact/无artifact/dry run/凭证缺失/小规模 |
| TG-6 Timeline+LOG记录 | 4 | 标准记录/无artifact记录/LOG格式/Timeline格式 |
| TG-7 回报 | 3 | 完整回报/缺失项回报/简洁回报 |
| TG-8 最小化原则 | 4 | 不扩domain/不改已有loop/不重构substrate/不预建kind |
| TG-9 安全约束 | 3 | 覆盖确认/CLAUDE.md追加确认/可逆直接执行 |
| TG-10 边界与异常 | 4 | 空name/非法cadence/重复创建/降级模式拒绝 |
| TG-11 result.md 落盘 | 4 | 落盘路径/结构完整/与知识库分离/.tribro一致 |
| **合计** | **47** | |

---

## TG-1 三态依赖检测

### TC-1.1 Mode A · 快照模式（tri-intent 可用）
- **前置条件**：`.tribro/snapshots/` 有快照，skills 目录有 `tri-intent/`
- **输入**：tri-intent 快照 §三，L2=I14，任务要点含"创建 SEO loop"
- **预期行为**：
  1. 检测到快照存在 → 进入 Mode A
  2. 读取快照 §三 结构化结论
  3. 校验 L2=I14
  4. 按标准工作流推进（substrate 检测 → charter → scaffold → 测试运行 → 记录 → 回报）
- **预期输出**：loop README 创建 + Timeline 记录 + LOG.md 条目
- **验证点**：不触发 Mode B/C 提示

### TC-1.2 Mode A · tri-intent 目录存在但无快照
- **前置条件**：skills 目录有 `tri-intent/`，但 `.tribro/snapshots/` 为空
- **输入**：用户直接说"帮我创建一个 loop"
- **预期行为**：
  1. 检测到 `tri-intent/` 存在 → 进入 Mode A
  2. 提示用户先经 tri-intent 识别意图产出快照，或选择降级模式
- **预期输出**：提示语或降级询问
- **验证点**：不直接报错，提供路径选择

### TC-1.3 Mode B · 引导安装（tri-intent 不可用，用户拒绝降级）
- **前置条件**：`.tribro/snapshots/` 无快照，skills 目录无 `tri-intent/`
- **输入**：用户直接调用 tri-loop，且拒绝降级
- **预期行为**：
  1. 检测到 tri-intent 不可用 → 询问是否降级
  2. 用户拒绝 → 进入 Mode B
  3. 输出引导安装提示语
- **预期输出**：包含 `skillhub install tri-intent --dir <目标目录>` 的提示
- **验证点**：硬性阻断，不执行任何操作

### TC-1.4 Mode C · 降级模式（tri-intent 不可用，用户选择直接使用）
- **前置条件**：`.tribro/snapshots/` 无快照，skills 目录无 `tri-intent/`
- **输入**：用户直接说"帮我创建一个每周 SEO loop"，选择降级模式
- **预期行为**：
  1. 检测到 tri-intent 不可用 → 询问是否降级
  2. 用户选择降级 → 进入 Mode C
  3. 内联澄清：从用户输入推断 5 项 charter 输入
  4. 询问缺失项（如工具/数据）
  5. 构造等价输入后按标准工作流推进
- **预期输出**：loop README 创建 + Timeline 记录 + LOG.md 条目
- **验证点**：降级模式下仍完成全链路

### TC-1.5 Mode C · 降级模式全量澄清
- **前置条件**：同 TC-1.4
- **输入**：用户只说"建一个 loop"，无任何细节
- **预期行为**：
  1. 进入 Mode C
  2. 逐一询问 5 项 charter 输入（name/goal/cadence/做什么/工具数据）
  3. cadence 默认 manual
  4. 全部收集后确认
- **预期输出**：确认后执行工作流
- **验证点**：不臆测任何输入

### TC-1.6 三态互斥性验证
- **前置条件**：分别设置 Mode A/B/C 的触发条件
- **预期行为**：同一时间只进入一个模式，不混用
- **验证点**：Mode A 不会同时触发 Mode B 提示

---

## TG-2 Substrate Bootstrap

### TC-2.1 Substrate 全存在
- **前置条件**：仓库根目录有 `ARCHITECTURE.md` + `LOG.md` + 含 "Knowledge base" 章节的 `CLAUDE.md`
- **预期行为**：跳过 bootstrap，直接进入 charter 收集
- **验证点**：不创建任何文件

### TC-2.2 Substrate 部分缺失（缺 ARCHITECTURE.md）
- **前置条件**：有 `LOG.md` + `CLAUDE.md`(含 KB 章节)，缺 `ARCHITECTURE.md`
- **预期行为**：
  1. 检测到 `ARCHITECTURE.md` 缺失
  2. 从 `templates/architecture.md` 逐字拷贝创建
  3. 不触碰已有的 `LOG.md` 和 `CLAUDE.md`
- **验证点**：idempotent，仅创建缺失文件

### TC-2.3 Substrate 全缺失
- **前置条件**：仓库根目录无任何 substrate 文件
- **预期行为**：
  1. 创建 `ARCHITECTURE.md` ← `templates/architecture.md`
  2. 创建 `LOG.md` ← `templates/log.md`
  3. 创建 `signals/README.md` ← `templates/signals-readme.md`
  4. 创建 `docs/README.md` ← `templates/docs-readme.md`
  5. 创建 `domains/README.md` ← `templates/domains-readme.md`
  6. 提议从 `templates/claude-template.md` scaffold `CLAUDE.md`
- **验证点**：全部文件均为逐字拷贝，不修改模板内容

### TC-2.4 Idempotent 验证（重复运行不覆盖）
- **前置条件**：Substrate 已存在，再次运行 tri-loop
- **预期行为**：检测到全部存在，跳过 bootstrap
- **验证点**：已有文件内容未被修改

### TC-2.5 不预建 tasks/ 或其他 kind
- **前置条件**：Substrate 全缺失
- **预期行为**：bootstrap 只创建 `signals/`、`docs/`、`domains/`，不创建 `tasks/`
- **验证点**：`tasks/` 目录不存在

---

## TG-3 Charter 收集

### TC-3.1 全量推断（请求已足够具体）
- **输入**：快照 §三 任务要点含全部 5 项信息
- **预期行为**：直接推断全部五项，在总结中确认
- **验证点**：不做任何澄清询问

### TC-3.2 部分澄清（推断不全）
- **输入**：快照 §三 任务要点有 name/goal/cadence，缺"做什么"和"工具数据"
- **预期行为**：做一轮简短澄清，仅问缺失的 2 项
- **验证点**：不重复问已有的信息

### TC-3.3 全量澄清（快照无任务要点）
- **输入**：快照 §三 任务要点为空或无 loop 相关信息
- **预期行为**：逐一询问 5 项 charter 输入
- **验证点**：cadence 默认 manual

### TC-3.4 请求已具体（降级模式下用户输入详细）
- **输入**：降级模式下用户说"建一个 weekly 的竞品观察 loop，每周拉竞品 SERP，输出分析 doc"
- **预期行为**：推断出 name=competitor-watch, cadence=weekly, 做什么=拉SERP+输出doc, 仅确认
- **验证点**：不做多余询问

### TC-3.5 缺失凭证记录
- **输入**：charter 收集中发现需要某 API 凭证但未提供
- **预期行为**：
  1. 不内联密钥
  2. 指向 setup skill 或 `.env`
  3. 在回报中标注缺失项
- **验证点**：密钥不出现在任何文件中

---

## TG-4 Scaffold

### TC-4.1 正常创建 loop README
- **输入**：charter 已收集，name=seo-watch
- **预期行为**：
  1. 从 `templates/loop-readme.md` 创建 `domains/seo-watch/README.md`
  2. 填入 frontmatter（kind: domain, domain: seo-watch, status: active, goal, cadence）
  3. 填入描述、Current focus、Backlog（空）、Timeline（空）
- **验证点**：frontmatter 字段完整且有值

### TC-4.2 冲突检查（domain 已存在）
- **输入**：`domains/seo-watch/` 已存在
- **预期行为**：
  1. 停止 scaffold
  2. 询问用户是否更新而非覆盖
- **验证点**：不覆盖已有文件

### TC-4.3 模板填充完整性
- **输入**：charter = {name: support-triage, goal: "分诊支持工单", cadence: daily, 做什么: "消费工单→产出分诊doc", 工具: "helpdesk API"}
- **预期行为**：README 包含：
  - frontmatter: `kind: domain, domain: support-triage, status: active, goal: 分诊支持工单, cadence: daily`
  - 描述含"消费工单"和"产出分诊doc"
  - Backlog 有占位项
  - Timeline 为空模板
- **验证点**：5 项 charter 全部体现在 README 中

### TC-4.4 最小化 scaffold（不过度装饰）
- **输入**：正常 charter
- **预期行为**：README 从简开始，不添加不必要的章节
- **验证点**：不含 Evidence & analysis 的详细内容（仅占位）、不含 Metrics 的具体数值（仅 TBD）

---

## TG-5 真实测试运行

### TC-5.1 运行产出 artifact
- **输入**：loop = SEO 关键词追踪，测试运行拉一条真实 SERP
- **预期行为**：
  1. 真正执行一次小规模运行
  2. 产出一个 `signal` 或 `doc`（如关键词排名记录）
  3. artifact 落盘到 `signals/` 或 `docs/`
- **验证点**：artifact 有正确的 frontmatter（kind, domain 等）

### TC-5.2 运行无 artifact（nothing actionable）
- **输入**：loop = 竞品观察，测试运行发现"nothing actionable yet"
- **预期行为**：
  1. 真正执行一次运行
  2. 不创建 artifact（运行未产出有价值内容）
  3. Timeline 记录含 "nothing actionable yet"
- **验证点**：不强行创建空 artifact

### TC-5.3 Dry run（凭证缺失）
- **输入**：loop 需要 API 凭证但未配置
- **预期行为**：
  1. 做能达到的最远 dry run
  2. 记录差距（缺少什么凭证）
  3. Timeline 记录含 dry run 说明
- **验证点**：不因凭证缺失而中止整个流程

### TC-5.4 小规模运行
- **输入**：loop = 工单分诊，测试运行分诊 2-3 张真实工单（非全量）
- **预期行为**：
  1. 只处理少量样本（2-3 张工单）
  2. 不处理全量数据
- **验证点**：运行规模合理，不过度执行

### TC-5.5 产出 artifact 可选性
- **输入**：loop = 收件箱监控，测试运行抓取收件箱但无新邮件
- **预期行为**：
  1. 执行抓取
  2. 无新邮件 → 不创建 artifact
  3. Timeline 记录"no new items"
- **验证点**：artifact 创建是可选的，不是强制的

---

## TG-6 Timeline + LOG.md 记录

### TC-6.1 标准记录（有 artifact）
- **输入**：测试运行产出了一个 signal
- **预期行为**：
  1. 向 `domains/<name>/README.md` 的 `## Timeline` 追加一行：
     `YYYY-MM-DD | test run — <做了什么及发现了什么>`
  2. 向 `LOG.md` 追加一条：
     ```
     ## YYYY-MM-DD · <loop-name> loop created + first run · #ops
     What: <一行描述>.
     Refs: domains/<name>/README.md (new), signals/<artifact-slug>.md (new).
     ```
- **验证点**：两个记录格式正确且内容匹配

### TC-6.2 无 artifact 记录
- **输入**：测试运行未产出 artifact
- **预期行为**：
  1. Timeline 仍追加一行（含 "nothing actionable yet"）
  2. LOG.md 仍追加一条（Refs 只有 README，无 artifact）
- **验证点**：两个必需记录都存在，即使无 artifact

### TC-6.3 LOG.md 条目格式
- **输入**：正常运行
- **预期行为**：LOG.md 条目严格遵循语法：
  - 标题行：`## YYYY-MM-DD · <loop-name> loop created + first run · #ops`
  - What: 1-2 行，成果优先
  - Refs: README (new) + artifact（如有）
- **验证点**：标题行含日期 + loop 名 + 标签

### TC-6.4 Timeline 格式
- **输入**：正常运行
- **预期行为**：Timeline 行格式：`YYYY-MM-DD | test run — <描述>`
- **验证点**：日期格式为 YYYY-MM-DD

---

## TG-7 回报

### TC-7.1 完整回报
- **输入**：正常流程完成
- **预期行为**：回报含：
  1. loop 的 charter（5 项输入）
  2. 测试运行做了/发现了什么
  3. 创建的 artifact（或"无"）
  4. 待接入的工具/凭证缺失项
  5. 如何再次运行（cadence + 入口点）
- **验证点**：5 个部分都存在

### TC-7.2 缺失项回报
- **输入**：测试运行发现凭证缺失
- **预期行为**：回报明确标注缺失项，指向 setup skill 或 `.env`
- **验证点**：缺失项可操作（有明确的下一步）

### TC-7.3 简洁回报
- **输入**：正常流程完成
- **预期行为**：回报保持简洁，不冗长
- **验证点**：每个部分 1-2 句话

---

## TG-8 最小化原则

### TC-8.1 不擅自创建额外 domain
- **输入**：用户要求创建 1 个 loop
- **预期行为**：只创建 1 个 domain，不擅自创建"相关"的额外 domain
- **验证点**：`domains/` 下只新增 1 个子文件夹

### TC-8.2 不擅自修改已有 loop
- **输入**：用户要求创建新 loop，但已有 loop 存在
- **预期行为**：不修改已有 loop 的 README，只创建新的
- **验证点**：已有 loop 的 README 内容未变

### TC-8.3 不擅自重构 substrate
- **输入**：substrate 已存在，运行 tri-loop
- **预期行为**：不修改 ARCHITECTURE.md / LOG.md 的已有内容，只在 LOG.md 追加
- **验证点**：已有 substrate 文件内容未被修改（追加除外）

### TC-8.4 不预建 kind
- **输入**：substrate bootstrap 执行
- **预期行为**：不创建 `tasks/` 或其他 kind 文件夹
- **验证点**：只有 `signals/`、`docs/`、`domains/` 被创建

---

## TG-9 安全约束

### TC-9.1 覆盖已存在 domain 需确认（L2 不可逆）
- **输入**：`domains/seo-watch/` 已存在，用户要创建同名 loop
- **预期行为**：
  1. 停止并询问是否更新而非覆盖
  2. 用户确认后方可继续
- **验证点**：不默默覆盖

### TC-9.2 修改已有 CLAUDE.md 需确认（L2 不可逆）
- **输入**：CLAUDE.md 已存在但无 "Knowledge base" 章节
- **预期行为**：
  1. 仅追加 KB 章节，不碰其余部分
  2. 追加前说明操作
- **验证点**：已有 CLAUDE.md 内容未被修改（追加除外）

### TC-9.3 创建新文件直接执行（L1 可逆）
- **输入**：创建新 domain 文件夹 + README
- **预期行为**：无需确认，直接执行
- **验证点**：不阻塞创建新文件

---

## TG-10 边界与异常

### TC-10.1 空 name
- **输入**：charter 收集时 name 为空
- **预期行为**： MUST 澄清，不允许空 name 创建 loop
- **验证点**：不创建 `domains//README.md`

### TC-10.2 非法 cadence
- **输入**：cadence = "sometimes"（非 manual/daily/weekly/cron）
- **预期行为**：提示合法值，默认 manual
- **验证点**：不使用非法 cadence 值

### TC-10.3 重复创建同一 loop
- **输入**：已创建 seo-watch loop，再次请求创建
- **预期行为**：冲突检查触发，询问是否更新而非覆盖
- **验证点**：不创建重复

### TC-10.4 降级模式用户中途拒绝
- **输入**：Mode C 降级模式中，用户拒绝提供 charter 信息
- **预期行为**：中止流程，不做任何文件操作
- **验证点**：无文件被创建

---

## TG-11 result.md 落盘

### TC-11.1 result.md 落盘到 .tribro/loops/
- **前置条件**：tri-loop 执行完成，charter 已收集、测试运行已执行
- **预期行为**：
  1. 执行结果落盘于 `.tribro/loops/<命名>/result.md`
  2. 若 `.tribro/` 目录不存在，MUST 先创建
  3. 命名沿用 tri-intent 快照命名：`<问题类型>_<日期>_<时间>_<会话ID>`
- **验证点**：`.tribro/loops/<命名>/result.md` 存在且非空

### TC-11.2 result.md 结构完整性
- **前置条件**：result.md 已落盘
- **预期行为**：result.md 包含以下章节：
  1. Loop Charter（5 项输入）
  2. Substrate 状态（已就绪 / 已 bootstrap）
  3. 测试运行摘要（做了什么 + 发现了什么 + dry run 标注）
  4. Artifact 记录（创建的路径，或"无"）
  5. 缺失项（待接入的工具/凭证）
  6. 如何再次运行（cadence + 入口点）
  7. 引用（快照路径 + loop README 路径 + LOG.md 条目位置）
  8. 执行可追溯性自检
- **验证点**：8 个章节全部存在，无遗漏

### TC-11.3 result.md 与知识库内容文件分离
- **前置条件**：tri-loop 执行完成
- **预期行为**：
  1. **tri-loop 链路文档**（result.md）落盘于 `.tribro/loops/` 下
  2. **知识库内容文件**（substrate + loop README + LOG.md 条目）落盘于知识库仓库根目录
  3. 两者路径分离，不混淆
- **验证点**：result.md 在 `.tribro/loops/`，loop README 在 `domains/<name>/`，LOG.md 在仓库根

### TC-11.4 .tribro 目录一致性
- **前置条件**：检查 `.tribro/` 目录结构
- **预期行为**：
  1. `.tribro/snapshots/` — tri-intent 产出
  2. `.tribro/actions/` — tri-action 产出
  3. `.tribro/loops/` — tri-loop 产出
  4. 三者同级，命名规范一致
- **验证点**：三个子目录命名与 tri-intent/tri-action/tri-loop 对应，路径结构一致

---

## 测试执行说明

### 运行方式

1. **准备测试环境**：创建临时知识库仓库目录
2. **按测试组顺序执行**：TG-1 → TG-2 → ... → TG-10
3. **每个用例独立执行**：前置条件独立设置，不依赖前一用例的状态
4. **验证点逐一检查**：每个验证点必须通过

### 通过标准

- 全部 47 个用例的验证点通过
- 无遗漏的能力路径
- 三态依赖检测互斥正确
- 最小化原则未被违反
- 安全约束未被绕过

### 测试覆盖矩阵

| 核心能力 | 覆盖用例 |
|---|---|
| Substrate Bootstrap | TC-2.1 ~ TC-2.5 |
| Loop Charter 收集 | TC-3.1 ~ TC-3.5 |
| Loop README Scaffold | TC-4.1 ~ TC-4.4 |
| 真实测试运行 | TC-5.1 ~ TC-5.5 |
| Timeline + LOG.md 记录 | TC-6.1 ~ TC-6.4 |
| 回报 | TC-7.1 ~ TC-7.3 |
| 三态依赖检测 | TC-1.1 ~ TC-1.6 |
| 最小化原则 | TC-8.1 ~ TC-8.4 |
| 安全约束 | TC-9.1 ~ TC-9.3 |
| 边界与异常 | TC-10.1 ~ TC-10.4 |
| result.md 落盘 | TC-11.1 ~ TC-11.4 |
