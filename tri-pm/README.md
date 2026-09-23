# tri-pm

产品管理（PM）领域产物与工作流 skill——把「AI 当资深产品经理用」：给一个模糊想法或一堆素材，拿到一份结构严谨、可直接评审的 PM 产物（PRD、战略画布、路线图、OKR、GTM、竞品分析、数据分析、AI 交付审计包），而不是一段泛泛而谈的文字。

蒸馏自开源项目 **PM Skills Marketplace**（`phuryn/pm-skills`，**MIT v2.1.0**，策展人 Paweł Huryn），按 tri-xxx 家族规范（12/13 章结构 + 版本检查门 + 26 条硬约束）合规化、中文化。

**蒸馏基准**：`docs/pm-skills-main-engineering-analysis.md`。本 skill 的一切领域结论均可回溯至该报告，NEVER 引入报告之外的臆测。

## 知识底座（源自蒸馏基准实测数据）

| 项 | 实测值 |
|---|---|
| 源项目形态 | Claude Code 插件市场（9 插件 / 4 层架构） |
| 技能（框架知识） | **68** 个 |
| 命令（链式工作流） | **42** 条 |
| 内容体量 | 约 **71k 词**（技能 40,975 + 命令 30,736） |
| 治理实证 | `validate_plugins.py` 9 插件全 PASS（0 错 0 警）；15 个 unittest 全 OK |
| 运行时依赖 | 零第三方包（Markdown + Python stdlib） |

## 特性

- **九域路由**：探索 / 战略 / 执行 / 研究 / 分析 / 上市 / 增长 / 工具 / AI 交付，关键词一跳直达。
- **渐进式披露**：约 71k 词源内容拆为分层知识包，按「常驻层 + 用户指定层 + 外部覆盖层」按需装配，NEVER 一次灌全量。
- **防臆测纪律**：`distillation-baseline.md` 为常驻层，含报告结论覆盖矩阵、风险 R1–R7、可行性评分卡（≈4.0/5）、验收 V1–V7、禁区清单与**形态差距表**。
- **语法翻译层**：源项目的 Claude Code 专有语法（`$ARGUMENTS`、`/command`、subagent fan-out、`allowed-tools`）全部翻译为对话上下文 / 编排步骤 / 只读代理，NEVER 原样输出。
- **保真度诚实声明**：框架知识 100% / 工作流编排 100%（42/42 全量落地） / 自动触发 85% / 审计类 70% / 外链 40 条唯一已回补；NEVER 声称逐字复刻。
- **多域检出门**：一次请求命中 ≥2 域时声明并默认按域拆分，NEVER 静默合并出「章节污染」产物。
- **产物校验器**：`scripts/validate_pm_artifact.py` 五模式（引用可解析 / MUST-SECTIONS 章节完整性 / 体积 / 语法残留 / 装配守卫），完成判据可机械复现。
- **版本检查门（第零步）**：自带 `scripts/check_update.py`（四态判定，与全家族同源）。
- **上游依赖检测三态**：快照模式 / 引导安装 / 降级模式。

## 当前形态（诚实声明）

本 skill v1.1.0 = **全量蒸馏**：Phase 1（骨架）+ Phase 2（68 框架正文，`references/frameworks/`）+ Phase 3（42 命令编排，`references/workflows/`）+ Phase 4（校验器 `scripts/validate_pm_artifact.py`）均已落地。

报告推荐的目标形态为「1 路由 skill + 9 领域子技能」；实际以「框架级单文件 + 分层装配」承载（规避 SKILL.md ≤500 行上限，且装配粒度更细）。差距与决策记录见 `references/distillation-baseline.md` §八/§九。

## 目录结构

```
tri-pm/
├── SKILL.md                              # 主入口（307 行，≤500 行约束）
├── README.md
├── CHANGELOG.md
├── _meta.json                            # 安装元数据（install_skill.py 生成）
├── scripts/
│   ├── check_update.py                   # 版本检查与强制自动更新（第零步硬门）
│   └── validate_pm_artifact.py           # 产物与知识包校验器（五模式）
├── references/
│   ├── distillation-baseline.md          # 【常驻层】防臆测铁律 / 覆盖矩阵 / 风险 / 验收 / 决策记录 D-A~D-D
│   ├── distilled-architecture.md         # 【常驻层】四层架构 / 模块职责 / 依赖 / 数据流 / 设计决策
│   ├── pm-frameworks-map.md              # 【用户指定层·导航】九域 68 技能 + 42 命令清单
│   ├── workflows-and-execution.md        # 【用户指定层·范式】命令链范式 / 校验流程 / 翻译映射
│   ├── interfaces-and-contracts.md       # 【模式层】schema / frontmatter / 引用协议 / CLI
│   ├── version-check-spec.md             # 版本检查门细则真源（与 tri-forge 同源）
│   ├── frameworks/                       # 【用户指定层·框架级】68 框架全量正文（9 域 + partN 拆分）
│   └── workflows/                        # 【用户指定层·命令级】42 命令全量编排（9 域 + partN 拆分）
└── tests/
    └── tri-pm-full-testcases.md
```

## 安装

```bash
skillhub install tri-pm --dir <目标目录>
```

## 使用

直接提出 PM 需求即可，例如：

> "帮我写一份面向 B 端团队协作工具的 PRD，目标用户是 50–200 人规模的研发团队。"

> "用机会解树拆解『用户留存低』这个问题，并给一份 RICE 排序。"

> "审计这个 AI 生成的后台管理系统，找出意图与实现的缺口，每条结论要带 file:line 证据。"

AI 会：判定目标域 → 分层装配知识 → 补齐框架必需字段 → 产出结构化产物 → 保真核对 → 输出 `[TRI-PM-PASS]`。

## 测试

见 `tests/tri-pm-full-testcases.md`（全场景测试用例，frontmatter 版本与 SKILL.md 强一致）。

## 归属与许可

- **意图路由**：tri-intent `L2 = I06`（内容生成）下的 **PM 产物子类**（`L3_子意图 = pm`），与 `tri-article`（文章）/ `tri-html`（架构可视化）/ `tri-checklist`（审计清单）并列，由上游按 `下游 slug` 分发，**非独占 I06 顶层路由**（I06–I10 顶层认领方为 `tri-content`）。
- **触发方式**：主触发＝用户点名或 PM 产物类需求（独立运行）；次触发＝tri-intent 下游路由建议指向本 skill。
- **路由登记**：`family-spec.md` §1.3 路由表登记为**待办项**（跨 skill 改动，须经确认后执行），当前不影响独立使用。
- **相邻边界**：文章撰写 → `tri-article`；通用内容 → `tri-content`；项目规划 → `tri-plan`；格式转换 → `tri-pdf2md` 等。
- **许可**：MIT。保留原项目 MIT 归因与作者声明（Paweł Huryn / The Product Compass）；不生成 `LICENSE` 或 `.gitignore` 文件。
