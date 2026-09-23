---
name: tri-jobhunt
slug: tri-jobhunt
version: 1.0.3
displayName: 求职全流程路由
description: 覆盖求职全生命周期的单入口领域 skill：ATS 兼容简历优化、要点量化、JD 匹配决策、定向定制、求职信/申请表/自荐邮件/LinkedIn/案例研究/推荐人产出、面试 STAR 故事库、薪资谈判、Offer 比较、专项角色（技术/高管/学术/创意/转行）定制。用户显式 `/tri-jobhunt` 调用后，按请求类型分发委派给 children 子 skill（tri-jd / tri-resume-core / tri-docs / tri-interview / tri-negotiate / tri-role）。支持独立安装，含上游依赖检测2态逻辑。
summary: 求职材料生成与策略决策的唯一入口，单入口分发到 6 个 children 子 skill 完成简历/面试/谈判全流程。
tags: [jobhunt, resume, interview, negotiation, career, recruiter, ats]
license: MIT
---

# tri-jobhunt · 求职全流程路由（单入口 · 子 skill 分发）

> 本 skill 是**独立领域入口 skill**：不认领 tri-intent 的 L2/L3 意图编码、不进 tri-intent 路由表，
> 由用户显式 `/tri-jobhunt` 调用激活。它把求职/简历/面试/谈判的完整能力收敛为**单一入口**，
> 内部按请求类型分发到 6 个 children 子 skill，不产生第二个独立入口。
> 用户心智：把 AI 当「求职顾问」——丢一份简历 + 一个岗位或一段描述，拿到一份可投的简历/求职信/面试题库/谈判方案。

## 强制执行契约（Execution Contract · 最高优先级）

> 本节优先级高于 Agent 通用默认行为。用户显式调用本 skill，或请求明显属于求职/简历/面试/谈判领域
> 且指向本 skill 时，即视为**激活**，不得仅当参考文档。

0. **版本检查前置硬门（第零步）**：任一执行入口启动后、核心执行前，MUST 先运行
   `python scripts/check_update.py --slug tri-jobhunt --json`；解析 `state` 字段并按四态处置
   （详情见 §版本检查与更新机制）。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其它强制前置条目。

1. **单入口强制**：NEVER 绕过本 skill 直接对外暴露 children 子 skill 作为第二个入口——子 skill
   仅由本 skill 依路由表（§方法论 / `references/jobhunt-routes.md`）分发调用。
2. **分发强制**：识别请求类型命中 R1-R11 后，MUST 分发到对应 children 子 skill 并复用共享
   `references/`，NEVER 在主 skill 内重复内联子 skill 方法论。
3. **真实性把关（R11）**：任何产出涉及「用户可能伪造数据」→ MUST 严守 HIGHLIGHT-不-Fabricate 边界，
   NEVER 加假技能 / 假数字 / 编造荣誉。
4. **一次一环节**：按求职生命周期串行推进（如 JD 决策 → 定制 → 求职信），NEVER 一次性交付「全套」。
5. **量化诚实**：无精确数字时 MUST 用保守/区间/最小边界估算，NEVER 硬造数字。
6. **职责边界**：NEVER 越界做其它 skill 的事（详见 §职责边界）。
7. **自检句**：作答前 MUST 声明「本次操作=<子流程>，触发源=用户显式调用，分发给子 skill=<…>，
   已读取 jobhunt-references」；与用户意图冲突则停止并纠正，不擅自继续。

## 触发时机

| 触发源 | 模式 | 激活条件 |
|---|---|---|
| 用户显式调用 `/tri-jobhunt` | 求职全流程 | 任意求职/简历/面试/谈判请求 |
| 用户请求属于求职领域 | 求职全流程 | 优化简历/ATS / 加量化 / 判断岗位 / 写求职信/申请表/自荐邮件 / LinkedIn / 案例研究 / 推荐人 / 备面试 / 谈薪 / 比 Offer / 转行/技术/高管/学术/创意简历 |
| 分发 → tri-jd | JD 决策 | 用户给 JD 问匹配度/值不值得投 |
| 分发 → tri-resume-core | 简历核心 | ATS / bullet / 量化 / 格式 / 定制 / 多版本 |
| 分发 → tri-docs | 求职产出文档 | 求职信 / 申请表 / 冷邮件 / LinkedIn / 案例研究 / 推荐人 |
| 分发 → tri-interview | 面试 | STAR 故事库 / 预测题 / 问面试官 |
| 分发 → tri-negotiate | 谈判与 Offer | 薪资谈判 / 多 Offer 比较 |
| 分发 → tri-role | 专项角色 | 技术 / 高管 / 学术 / 创意 / 转行 |

> 子 skill 模式见 `references/jobhunt-routes.md` §一决策规则表。

## 上游依赖检测（独立使用时 · 两态）

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 完整模式** | children 子 skill 与 references 全部就位 | 按路由表分发执行（标准） |
| **B · 降级/引导** | 部分子 skill 或 references 缺失 | 提示「子 skill 未就位，本次由主 skill 以内联方式降级执行部分能力」；若缺失导致能力不可用，列出手动补齐命令 |

> 本 skill 不依赖 tri-intent（非下游）；其上游是自身的 children 子 skill 与 references 资源。
> 检测方式：检查 `children/<子skill>/SKILL.md` 与 `references/*.md` 存在性。两态均放行，
> B 态声明降级精度低并给出补齐指引。

## 输入契约

| 输入 | 用途 |
|---|---|
| 用户求职请求文本（含简历/JD/岗位/问题） | 判定命中 R1-R11 并分发 |
| 可选：简历正文 / JD 文本 / 面试邀请 / Offer 信 | 各子 skill 的解析与产出输入 |
| 用户角色/行业（技术/高管/学术/创意/转行） | 触发 R9 走 tri-role 角色分支 |

## 职责边界

- **本 skill 负责**：求职全流程的路由分发（识别 R1-R11 → 派发到 6 子 skill）+ 真实性/量化把关
  （R11）+ 共享 references 的装配与复用。
- **不负责**：意图识别（归 tri-intent）；AI 生成业务代码（归 tri-coding）；代码修复（归 tri-fix）；
  代码审查（归 tri-review）；非求职场景的通用内容创作（归 tri-content，如年度述职可复用但不主适用）。
- **关键边界**：与 tri-content 的边界在「是否聚焦求职产出」——简历/求职信/面试/谈判等求职物料归本
  skill；通用文章/报告/文档归 tri-content。本 skill 不重新识别意图（自身即用户显式入口）。
- **不触发场景（Not-Trigger）**：本 skill 不接手「意图识别」（归 tri-intent）；不接手「AI 生成业务代码」（归 tri-coding）；不接手「代码修复」（归 tri-fix）；不接手「代码审查」（归 tri-review）；不接手「非求职场景的通用内容创作」（归 tri-content）。

## tri-jobhunt 方法论（核心能力 · 单入口分发）

**单入口分发范式**：

```
用户请求 → 本 skill(唯一入口) → 识别 R1-R11 → 分发到 6 子 skill → 子 skill 复用 references → 产出收尾
```

**决策规则**：完整 R1-R11 表见 `references/jobhunt-routes.md` §一（grep 模式：`R1`-`R11`），
本处列速查：

| # | 请求类型 | 分发 |
|---|---|---|
| R1 | ATS/关键词 | tri-resume-core |
| R2 | bullet/量化 | tri-resume-core |
| R3 | JD 匹配/投否 | tri-jd |
| R4 | 定向定制 | tri-resume-core |
| R5 | 求职产出文档 | tri-docs |
| R6 | 面试准备 | tri-interview |
| R7 | 薪资谈判 | tri-negotiate |
| R8 | Offer 比较 | tri-negotiate |
| R9 | 专项角色 | tri-role |
| R10 | 版本管理 | tri-resume-core |
| R11 | 真实性边界 | 主 skill 把关 |

**知识装配顺序（references 覆盖层）**：

| 层级 | 触发 | 文件 |
|---|---|---|
| 常驻层（每次加载） | 总是 | `ats-compliance.md`（ATS 铁律与匹配核心） |
| 角色模式层（按 R9 触发） | 命中专项角色 | `role-branches.md` |
| 复用层（各子 skill 按需） | 命中具体子流程 | `quantification.md` / `star-framework.md` |
| 路由层（主 skill 分发） | 任何请求 | `jobhunt-routes.md` |

> 同名覆盖优先级：路由层 > 角色模式层 > 常驻层；装配去重（同一文件名只加载一次）。
> 各文件 grep 模式见文件头注释（grep pattern）。

**可扩展性**：新增求职能力 = 在 `children/` 增一个子 skill + 在 `jobhunt-routes.md` 决策表加一行
（触发词 + 分发目标），主 skill 骨架不动。

## 处理流程（单入口分发 · 可核对）

1. **识别主请求类型**：命中 R1-R11 其一（简历 / JD 决策 / 文档产出 / 面试谈判 / 角色定制）。
2. **分发到子 skill**：委派对应 children 子 skill，主 skill 只做路由与把关。
3. **复用共享层**：子 skill 从 `references/` 取 ATS / 量化 / STAR / 角色差异，不重复内联。
4. **产出合格物料**：按目标类型输出对应模板，并附「可对接下一步的前置产出」（如 JD 分析 → 求职信谈点）。
5. **收尾**：涉及版本/追踪写回 master 与追踪表；涉及数字标注估算；敏感/未证实数据标注或省略。

## 交付产物机制

| 产物 | 位置 | 内容 |
|---|---|---|
| 求职物料 | 用户工作区 `.tribro/tri-jobhunt/` | 简历 / 求职信 / 面试题库 / 谈判方案等最终产物 |
| 子 skill 产物 | 各 children 执行产出 | 报告头见 `jobhunt-routes.md` §三 |
| legacy 追踪 | 用户工作区 `.tribro/tri-jobhunt/` | master 简历 + 追踪表（R10） |

> 文件名沿用用户提供的材料命名（必要处加 `[名称]_[角色]_[公司]_[日期]`），不强制快照命名。

## 质量标准

| 维度 | 标准 | 验证方式 |
|---|---|---|
| 单入口 | 仅本 skill 对外，子 skill 不外暴露 | 无第二入口路径 |
| 分发正确 | 请求类型与 R1-R11 命中一致 | 分发目标校验 |
| ATS 合规 | 单列/标准字体/无表格图片/标准章节/联系方式入正文 | 按 `ats-compliance.md` 过检 |
| 量化诚实 | 每 bullet ≥1 数字，无精确数用估算 | 按 `quantification.md` 检查 |
| 真实性 | HIGHLIGHT 不 Fabricate，无假技能/假数字 | R11 把关 |
| 完成判据 | 见 §完成判据，可机械校验 | grep/文件存在性 |

## 完成判据

> 达成判据（**结束态**，全部满足即本轮完成）：
> - 主产物已产出且通过对应共享层质检（ATS/量化/真实性）。
> - 若命中 R10，master 与追踪表已更新。
> - 涉及数字已标注估算；敏感数据已标注或省略。
>
> 未完成态（**停车态**，非结束）：等待用户补充必要输入（如简历/JD 缺失）或等待用户确认方向时，
> 明确向用户声明「已停车待补充」，NEVER 把停车当成完成。

## 落盘规则

> 统一用 `## 落盘规则`。本 skill 为 tri-forge 生成的机器 skill，MUST 落盘 `.tribro/skills/<slug>/`
> （NEVER `skills/` 源树或其它路径）。链路审计文档落 `.tribro/forge/tri-jobhunt/`。用户成果物
> 落 `.tribro/tri-jobhunt/`（tri-forge 生成物的用户工作区）。
> **NEVER 生成 `LICENSE` 或 `.gitignore`**；许可证由 frontmatter `license: MIT` 声明。

## 版本检查与更新机制

- **执行方式**：`python scripts/check_update.py --slug tri-jobhunt --json`；解析 `state` 字段
  （A/B/C/D 一律放行；BLOCK 按 `block_code` 恢复；脚本异常兜底放行，NEVER 阻断启动）。
- **唯一真源**：版本比较、升级流程、四态判定、节流缓存细则，以 `references/version-check-spec.md`
  为准（NEVER 在本 skill 内联推导；NEVER 指向其它外部上游 skill 的版本规范）。
- children 子 skill 不携带版本脚本，其版本一致性由本 skill 统一巡检并校验。

## 进化契约

- **反馈接收点**：用户对产出的改进建议、对路由/决策规则的纠偏，于任意轮次提出。
- **经验沉淀位**：本次生成/使用中暴露的缺口、教训写入 `references/` 对应文件与
  `CHANGELOG.md`；锻造侧同步沉淀至 `.tribro/forge/tri-jobhunt/forge-lessons.md`。
- **自我修订触发**：当同一决策/边界缺口重复出现（≥2 次）或用户明确要求时，修订本 SKILL 的
  路由表/决策规则并升级 MINOR 版本。

## 目录结构

```
tri-jobhunt/
├── SKILL.md  README.md  CHANGELOG.md  _meta.json(#安装元数据,由 install_skill.py 生成)
├── references/
│   ├── jobhunt-routes.md        # R1-R11 路由表 + 分发契约
│   ├── quantification.md        # 六类/五估算/四模板/动词库
│   ├── ats-compliance.md        # ATS 铁律/格式/章节/匹配
│   ├── star-framework.md        # STAR/XYZ/CAR + 故事库
│   ├── role-branches.md         # 五角色差异增量
│   └── version-check-spec.md    # 版本检查规范真源(自包含副本)
├── scripts/check_update.py      # 版本检查门可执行实现
├── children/                    # 6 个子 skill（随父包分发，不独立发布）
│   ├── tri-jd/SKILL.md          # JD 匹配 / 投否决策 (R3)
│   ├── tri-resume-core/SKILL.md # 简历优化核心 (R1/R2/R4/R10/R11)
│   ├── tri-docs/SKILL.md        # 求职产出文档 (R5)
│   ├── tri-interview/SKILL.md   # 面试 STAR 库 (R6)
│   ├── tri-negotiate/SKILL.md   # 谈判 + Offer (R7/R8)
│   └── tri-role/SKILL.md        # 专项角色 (R9)
└── tests/tri-jobhunt-full-testcases.md
```