---
name: pm-frameworks-map
description: pm-skills 九大 PM 域的能力清单——68 个技能与 42 条链式工作流的完整映射。对照分析报告 §2.2 / §4。
---

# PM 域能力清单（9 域 · 68 技能 · 42 工作流）

> **蒸馏基准**：分析报告 §2.2（规模统计）与 §4（核心功能清单）。清单逐项源自源项目 README 与目录实测。
> grep 检索模式：`<域名>`（如 `执行`、`战略`、`探索`）/ `技能` / `命令` / `框架`

> **加载策略**：本文件属**用户指定层·导航**——MUST 在用户点名某域后才加载对应段落，NEVER 全量灌入。
> **全量正文**（v1.1.0）：68 个框架正文见 `references/frameworks/<域>/<框架>.md`；42 条命令编排见 `references/workflows/<域>/<命令>.md`——导航到具体框架后 MUST 装配对应单文件（框架级粒度）。

---

## 1. pm-product-discovery（产品探索 · 13 技能 / 5 命令）

**技能（13）**

- `brainstorm-ideas-existing` — 既有产品的多视角构思（PM/设计师/工程师）
- `brainstorm-ideas-new` — 新产品的初始探索构思
- `brainstorm-experiments-existing` — 为既有产品假设设计实验
- `brainstorm-experiments-new` — 为新产品设计精益 pretotype（Alberto Savoia）
- `identify-assumptions-existing` — 识别价值/可用性/可行性/存续性风险假设
- `identify-assumptions-new` — 识别 8 类风险假设（含 GTM、战略、团队）
- `prioritize-assumptions` — 影响 × 风险矩阵排序并给出实验建议
- `prioritize-features` — 按影响、投入、风险、战略契合度排序需求池
- `analyze-feature-requests` — 按主题与战略契合度归类客户需求
- `opportunity-solution-tree` — 机会解树（Teresa Torres）：结果→机会→方案→实验
- `interview-script` — 结构化访谈脚本（JTBD 追问）
- `summarize-interview` — 访谈记录 → JTBD、满意度信号、行动项
- `metrics-dashboard` — 指标看板（North Star、输入指标、告警阈值）

**命令（5）**：`/discover`（全探索周期：构思→假设→排序→实验）、`/brainstorm`、`/triage-requests`、`/interview`、`/setup-metrics`

## 2. pm-product-strategy（产品战略 · 12 技能 / 5 命令）

**技能（12）**

- `product-strategy` — 九段式产品战略画布（愿景→可防御性）
- `startup-canvas` — 创业画布（战略九段 + 商业模型）
- `product-vision` — 有感召力且可达成的产品愿景
- `value-proposition` — 六段式 JTBD 价值主张
- `lean-canvas` — 精益画布
- `business-model` — 商业模型画布（九宫格）
- `monetization-strategy` — 3–5 种变现策略 + 验证实验
- `pricing-strategy` — 定价模型、竞争分析、支付意愿、价格弹性
- `swot-analysis` — SWOT 与可执行建议
- `pestle-analysis` — 宏观环境（政治/经济/社会/技术/法律/环境）
- `porters-five-forces` — 波特五力（竞争/供应商/买方/替代品/新进入者）
- `ansoff-matrix` — 安索夫增长矩阵（市场 × 产品）

**命令（5）**：`/strategy`、`/business-model`、`/value-proposition`、`/market-scan`、`/pricing`

## 3. pm-execution（执行管理 · 16 技能 / 11 命令）

**技能（16）**

- `create-prd` — 八段式 PRD 模板
- `brainstorm-okrs` — 团队级 OKR
- `outcome-roadmap` — 特性清单 → 结果导向路线图
- `sprint-plan` — 冲刺规划（容量估算、故事选择、风险识别）
- `retro` — 结构化迭代回顾
- `release-notes` — 面向用户的发布说明
- `pre-mortem` — 风险分析（老虎/纸老虎/大象分类）
- `stakeholder-map` — 权力 × 利益网格 + 沟通计划
- `summarize-meeting` — 会议记录 → 决策 + 行动项
- `user-stories` — 用户故事（3C + INVEST）
- `job-stories` — Job Stories（当…我想要…以便…）
- `wwas` — 待办项（Why-What-Acceptance）
- `test-scenarios` — 测试场景（正向/边界/异常）
- `dummy-dataset` — 仿真数据集（CSV/JSON/SQL/Python）
- `prioritization-frameworks` — 9 种优先级框架参考（机会评分、ICE、RICE、MoSCoW、Kano 等）
- `strategy-red-team` — 对抗式压力测试：找出承重假设、命名失败条件、按最省成本排序

**命令（11）**：`/write-prd`、`/plan-okrs`、`/transform-roadmap`、`/sprint`、`/pre-mortem`、`/red-team-prd`、`/meeting-notes`、`/stakeholder-map`、`/write-stories`、`/test-scenarios`、`/generate-data`

## 4. pm-market-research（市场研究 · 7 技能 / 3 命令）

**技能（7）**：`user-personas`、`market-segments`、`user-segmentation`、`customer-journey-map`、`market-sizing`（TAM/SAM/SOM，自顶向下 + 自底向上）、`competitor-analysis`、`sentiment-analysis`

**命令（3）**：`/research-users`、`/competitive-analysis`、`/analyze-feedback`

## 5. pm-data-analytics（数据分析 · 3 技能 / 3 命令）

**技能（3）**：`sql-queries`（自然语言 → SQL，支持 BigQuery/PostgreSQL/MySQL）、`cohort-analysis`（留存曲线、功能采纳、参与度趋势）、`ab-test-analysis`（统计显著性、样本量校验、上线/延长/停止建议）

**命令（3）**：`/write-query`、`/analyze-cohorts`、`/analyze-test`

## 6. pm-go-to-market（上市策略 · 6 技能 / 3 命令）

**技能（6）**：`gtm-strategy`、`beachhead-segment`、`ideal-customer-profile`、`growth-loops`、`gtm-motions`、`competitive-battlecard`

**命令（3）**：`/plan-launch`、`/growth-strategy`、`/battlecard`

## 7. pm-marketing-growth（营销增长 · 5 技能 / 2 命令）

**技能（5）**：`marketing-ideas`、`positioning-ideas`、`value-prop-statements`、`product-name`、`north-star-metric`

**命令（2）**：`/market-product`、`/north-star`

## 8. pm-toolkit（工具箱 · 4 技能 / 5 命令）

**技能（4）**：`review-resume`（对照 10 条最佳实践，XYZ+S 公式）、`draft-nda`、`privacy-policy`（GDPR/CCPA）、`grammar-check`

**命令（5）**：`/review-resume`、`/tailor-resume`、`/draft-nda`、`/privacy-policy`、`/proofread`

## 9. pm-ai-shipping（AI 交付审计 · 2 技能 / 5 命令）

**技能（2）**

- `shipping-artifacts` — 让 AI 生成应用「可评审」的文档集：核心集（架构、用户/权限流、权限、变量与密钥、测试覆盖映射）+ 条件集（邮件、定时任务、SEO、嵌入式 agent/自动化）
- `intended-vs-implemented` — **差异化能力**：找出「文档声明的意图」与「代码实际行为」之间的缺口，缺口两侧均须引用证据

**命令（5）**：`/ship-check`、`/document-app`、`/derive-tests`、`/security-audit-static`、`/performance-audit-static`

---

## 蒸馏优先级建议（报告 §9）

按使用频次与差异化价值排序搬运：

1. `execution`（16 技能 / 11 命令）——覆盖最高频 PM 场景
2. `strategy`（12 / 5）——框架密度最高
3. `discovery`（13 / 5）——探索流程最完整
4. `ai-shipping`（2 / 5）——**差异化能力**（意图 vs 实现审计法），单列高优

> 保真度评估与处理方式的完整对照见 `distillation-baseline.md`。
