# Changelog

本文件记录 tri-review skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。


## [1.3.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.2.0` → `1.3.0`

## [1.2.0] - 2026-08-02

### 新增

- **增量审计模式（第三模式）**：用户直接要求「增量审计」「架构师视角审计改动」时激活，默认增量、默认当前项目；以系统架构设计师视角产出审计结果 + 修复建议 + 优先级
- **Phase 0 架构师增量审计（可选前置阶段）**：文档驱动学习链（4 级降级：用户文档→项目分析/介绍文档→README→全量代码兜底）+ 三维审计（代码设计改动/架构设计实现/功能设计实现，各 6 项 = 18 项）+ 修复建议模板（方向+方案+优先级）；详见 `references/audit-dimensions.md`
- **上游依赖检测升级为三态**：新增降级模式（C 态），增量审计模式不依赖快照可在降级模式下正常执行；原两态（快照/引导安装）保留
- **审计报告模板**：`templates/audit-report.md`（Phase 0 载体，三维审计+修复建议清单+门①②载体）
- **Phase 0 标记体系**：`[AUDIT-OK]` / `[AUDIT-ISSUE] BLOCKER/MAJOR/MINOR` / `[AUDIT-NOTE]` / `[AUDIT-FAIL]` / `[AUDIT-PASS]`，与 Phase 1/2 标记严格隔离
- **反规避机制增强**：交叉标记检测扩展为 Phase 0/1/2 三阶段互不交叉；阶段分离检测覆盖 Phase 0

### 变更（去重与一致性）

- **Phase 1/2 详细 checklist 外置**：SKILL.md 中 Phase 1（4 维度 × 4 项）与 Phase 2（6 维度 × 4-5 项）的详细 checklist、输出标记表、门禁判定表、严重程度分级表移至 `references/review-checklists.md`，原处改为维度概览表 + 指针；SKILL.md 由 460 行精简至 320 行
- **frontmatter 更新**：version 1.1.2→1.2.0；description 增「增量审计模式」「三态逻辑」；summary 增 Phase 0 架构师增量审计；tags 增 `incremental-audit` / `architecture-audit`
- **自检句增强**：新增「Phase 0 状态=<待审计/通过/未通过/未启动>」字段
- **目录结构更新**：新增 `references/review-checklists.md`、`references/audit-dimensions.md`、`templates/audit-report.md`
- **tests 版本对齐**：`tests/tri-review-full-testcases.md` frontmatter 与「被测对象」由 v1.1.2 更新为 v1.2.0；新增 Phase 0 / 增量审计模式测试用例；TC-04 调整为检查 references + SKILL.md 指针

## [1.1.2] - 2026-08-02

### 新增

- **`## 质量标准` 章节**：四维标准（规格覆盖率 / 坏味检出 / 门禁通过率 / 反规避命中），强化双审批门质量护栏说明

### 变更（去重与一致性）

- **Fowler 坏味基线外置**：`## 两阶段代码审查方法论` 中的 12 种坏味基线表移至 `references/code-smells.md`，原处改为摘要 + 指针（grep 模式：`坏味名`）；目录树同步新增 `references/`
- **作答前声明标准化**：强制执行契约第 4 条自检新增「本次意图=CR」四字前缀
- **tests 版本对齐**：`tests/tri-review-full-testcases.md` frontmatter 与「被测对象」由 v1.0.0 更新为 v1.1.2

## [1.1.1] - 2026-07-30

### 变更

- **落盘规则标题层级统一**：`### 四、落盘规则` 提升为 `## 落盘规则`（二级标题），与 tri-action/tri-content/tri-plan 等 10 个 skill 保持一致

## [1.1.0] - 2026-07-26

### 新增

- **上游依赖检测两态逻辑**：独立安装时支持快照模式（A · 读取快照按工作流推进）/ 引导安装（B · 提示安装 tri-intent），不支持降级模式（硬阻断，MUST 安装后方可使用）

### 修复

- **MECE 修复**：tri-intent 新增代码审查特殊路由（`doing/code-review.md`），定义代码审查特殊路由项（不占 I 编号位），消除意图分类体系中代码审查的覆盖空白

## [1.0.0] - 2026-07-24

### 新增

- 初始版本：代码审查下游执行 skill，支持混合模式（工作流集成 + 独立调用）
- 两阶段代码审查方法论：Phase 1 规格合规审查（4 维度 × 4 项）+ Phase 2 代码质量审查（6 维度 × 4-5 项）
- Fowler 代码坏味基线（12 种）：神秘命名/重复代码/依恋情结/数据泥团/基本类型偏执/重复 switch/霰弹式修改/发散式修改/投机性泛化/消息链/中间人/拒绝馈赠
- 反规避机制（4 种检测）：阶段分离 / 清单完整性 / 交叉标记 / 门禁执行
- review-report.md 审查报告模板（门①+门②载体+最终交付物）
- 双审批门机制（门①审查范围确认 / 门②审查结论确认）
- Phase 1 门禁判定（FAIL / PASS-WITH-CONDITIONS / PASS）+ Phase 2 回退机制
