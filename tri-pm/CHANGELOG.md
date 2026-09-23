# Changelog

本文件记录 tri-pm skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.1.1] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 只做 PM 专属产物子类，不接手文章/技术写作、通用内容、项目规划、代码编写/修复、skill 蒸馏/锻造与格式转换。

## [1.1.0] - 2026-09-03

### 新增

- **68 框架全量正文（Phase 2）**：`references/frameworks/<域>/<框架>.md` 68/68，每文件含 MUST-SECTIONS 必含章节清单、逐段引导问题、输出模板、输出命名规则与 Further Reading 外链；超长框架拆 `-partN` 续篇（6 个）。
- **42 命令全量编排（Phase 3）**：`references/workflows/<域>/<命令>.md` 42/42，保留 Checkpoint 原句、输出模板、保存指令与自然语言下一步；Claude Code 专有语法（斜杠命令 / subagent fan-out）翻译为对话编排步骤。
- **产物与知识包校验器（Phase 4）**：`scripts/validate_pm_artifact.py` 五模式——引用可解析（99 处 0 悬空）、MUST-SECTIONS 完整性（68/68，375 条）、单文件体积（≤1,500 词）、专有语法残留（0）、装配体积（≤8,000 词）；`--artifact` 产物章节完整性正反例实测通过。
- **多域检出门（流程① 硬约束）**：一次请求命中 ≥2 域时 MUST 声明并默认按域拆分，用户坚持合并时显式标注「多域合并件」（依据差距报告 G10 与文章 L79 实测坑；R7 严重度 P2→P0 改判）。
- **蒸馏决策记录 D-A~D-D**（`distillation-baseline.md` §九）：PRD 模板裁定（/write-prd 八段为命令态权威）、披露粒度与体积上限、MUST-SECTIONS 内嵌承载形式、R7 改判依据。

### 修复

- 校验器三处缺陷：`framework_index` 排序使 `-partN` 拆分件抢占索引（5 个误报「缺块」）；MUST-SECTIONS 块提取在 H3 子标题处误截断（画布类 4 文件误报「空块」）；引用扫描把普通粗体误判为框架引用（11 处误报悬空）。修复后 `--all` 四项全过。
- `frameworks/toolkit/draft-nda.md` 勾选框 `- [x]` → `- [ ]`（对齐 D-C 约定）。
- 体积上限按实测校准：单文件 900→1,500 词、单次装配 3,500→8,000 词（D-B 修订记录，实测最坏装配 7,322 词）。

### 变更

- 知识装配顺序升级为**框架级粒度**（frameworks/ + workflows/ 单文件按需加载）。
- 完成判据第 2 条指向 MUST-SECTIONS 清单 + 校验器（BLOCK 判定事实源可复现，不再依赖模型背景知识）。
- 形态差距表（SKILL.md 与 baseline §八）：Phase 2/3/4 状态 ❌/⚠️ → ✅。

## [1.0.0] - 2026-09-02

### 新增

- **初始版本（tri-forge 蒸馏）**：以 `docs/pm-skills-main-engineering-analysis.md` 为对照基准，对开源项目 `PM Skills Marketplace`（`phuryn/pm-skills`，MIT v2.1.0，策展人 Paweł Huryn）执行知识蒸馏，按 tri-xxx 家族规范（12/13 章结构 + 版本检查门 + 26 条硬约束）合规化、中文化落地。
- **蒸馏内容（四大类，严格对齐基准报告）**：
  - 核心架构：L0 市场 / L1 插件 / L2 技能 / L3 命令四层结构、9 插件模块职责与规模（68 技能 / 42 命令 / 约 71k 词）、依赖关系、数据流 → `references/distilled-architecture.md`
  - 关键模块与职责：九域 68 技能 + 42 命令完整清单与蒸馏优先级 → `references/pm-frameworks-map.md`
  - 主要执行流程：`/discover` 与 `/write-prd` 命令链范式、`validate_plugins.py` 校验流程、测试门控流程、Claude Code → WorkBuddy 语法翻译映射 → `references/workflows-and-execution.md`
  - 重要接口与设计决策：`marketplace.json` / `plugin.json` schema、frontmatter 契约、command→skill 引用协议、校验器 CLI 接口、可复用设计决策与待改进项 → `references/interfaces-and-contracts.md`
- **防臆测机制（常驻层）**：`references/distillation-baseline.md` 含防臆测四铁律、报告 §1–§11 结论覆盖矩阵、风险 R1–R7、可行性评分卡（≈4.0/5）、Phase 0–5、验收 V1–V7、禁区清单、**当前形态 vs 报告目标形态差距表**（§八）。
- **九域路由**：探索 / 战略 / 执行 / 研究 / 分析 / 上市 / 增长 / 工具 / AI 交付，关键词一跳直达。
- **分层知识装配**：常驻层（基准 + 架构）+ 用户指定层（域清单 / 工作流 / 契约）+ 外部覆盖层，规避约 71k 词规模问题与 SKILL.md ≤500 行约束。
- **语法翻译层**：源项目 Claude Code 专有语法（`$ARGUMENTS`、`/command`、subagent fan-out、`allowed-tools`）翻译为对话上下文 / 编排步骤 / 只读代理。
- **保真度诚实声明**：框架知识 100% / 工作流编排 90% / 自动触发 85% / 审计类 70% / 外链需审查；禁止声称 100% 复刻。
- **完成判据外化**：`[TRI-PM-PASS]` / `[TRI-PM-BLOCK]` / 停车待续三态，五条机械可校验判据。
- **版本检查门（第零步）**：自带 `scripts/check_update.py`（四态判定，与全家族同源），细则真源指向 `references/version-check-spec.md`。
- **上游依赖检测三态**：快照模式 / 引导安装 / 降级模式。
- **意图归属**：tri-intent `L2 = I06` 下的 PM 产物子类（`L3_子意图 = pm`）。
- **配套文件**：SKILL.md / README.md / CHANGELOG.md / scripts / references / tests。

### 说明

- 本版本交付的是**元知识蒸馏 + 路由骨架**，对应基准报告 §9 的 **Phase 1**。报告 §9 的 Phase 2（68 框架正文搬运）、Phase 3（42 命令全量重写）、Phase 4（内容校验器移植）尚未执行，差距已显式记录于 `references/distillation-baseline.md` §八。
- 落盘位置按用户显式指令置于源码树 `tri-pm/`（与 `tri-ask` / `tri-article` 同级），家族默认生成位为 `.tribro/skills/tri-pm/`，已在合规报告中标注为**用户覆写项**。
