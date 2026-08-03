# Changelog

本文件记录 `tri-sdlc` 的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.1.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.0.1` → `1.1.0`

## [1.0.1] - 2026-08-02

### 重构（全量评审优化 · 渐进披露）

#### 确定性逻辑下沉 + 大表外移
- 新增 `scripts/gate_audit.py`：门禁自动审计算法（68 必检项 ID 枚举 + 逐条判定 PASS/FAIL/WARN/N/A + 缺失/无理由 N/A 视为 FAIL + 汇总 + 修订意见生成），SKILL.md 保留规则摘要与指针。
- 自然语言指令表（12 类指令）+ 阶段状态机十态 + 级联回退规则移入 `references/sdlc-commands.md`（单一事实源，grep 检索），SKILL.md 改为指针。
- 合并重复的「子SKLL 产出表」与「阶段清单表」：交付物文件名以 §一阶段清单表为单一事实源，§二改为指针，消除双写漂移源。
- `## 目录结构` 补登 `references/` 与 `scripts/`，与磁盘实况对齐。
- 测试集 frontmatter 版本联动至 v1.0.1。

## [1.0.0] - 2026-08-02

### Added

- **主编排器 `SKILL.md`**：定义 I11/I13/I14 · `sdlc` 子类的九阶段全生命周期编排工作流，含 9 条强制执行契约、三态上游依赖检测（快照模式/引导安装/降级模式）、输入契约、职责边界与六类相邻 skill 边界判据。
- **九阶段划分与子 SKILL 路由表**：P0 立项与规划 → P1 需求分析 → P2 方案设计 → P3 开发准备 → P4 编码实现 → P5 代码评审 → P6 测试验证 → P7 构建与发布 → P8 运维与监控，各自映射到 `children/` 下专职子 SKILL，阶段目录与文件名固定不可改。
- **门禁验收标准总表 `gates/acceptance-criteria.md`**：九阶段共 **68 条必检项 + 21 条建议项**，定义 `PASS/FAIL/WARN/N-A` 四值判定口径与阻断规则，作为门禁审计唯一事实源。
- **双闸门门禁机制**：闸门① 自动审计（必检项 FAIL 即硬阻断，产出 `gate-report.md`）+ 闸门② 用户确认；含反规避规则与「连续 3 轮 FAIL 停机请求人工介入」保护。
- **十态阶段状态机与级联回退**：`未启用/未开始/进行中/待审计/审计未过/待确认/已通过/已跳过/失效/已暂停`；`回退到 Pn` 时其后阶段一律置 `失效` 并标记 `stale`。
- **12 类自然语言指令**：`START/STATUS/APPROVE/REJECT/ROLLBACK/SKIP/PROFILE/REGATE/FASTMODE/PAUSE/RESUME/ABORT`，含 `继续` 的状态相关消歧规则。
- **三种执行剖面**：`full`(P0–P8) / `standard`(跳过 P3、P8) / `lite`(P1 P2 P4 P6)，未启用阶段不触发门禁、不计入进度分母。
- **跨阶段一致性核对**：需求 ID 贯穿、范围不漂移、阈值继承、交付预期兑现四个核对点。
- **模板**：`templates/manifest.md`（主控清单，九区结构）、`templates/gate-report.md`（门禁报告，多轮追加式）。
- **九个阶段子 SKILL**（`children/`）：`tri-charter`、`tri-require`、`tri-design`、`tri-devenv`、`tri-impl`、`tri-cr`、`tri-test`、`tri-release`、`tri-ops`，各含 `SKILL.md` / `README.md` / `CHANGELOG.md` / `tests/`，统一两态上游依赖检测（编排模式/引导安装）。
- **配套文件**：`README.md`（特性/目录结构/安装/使用/测试/设计原则/边界）、`tests/tri-sdlc-full-testcases.md`（全场景用例）、`tests/tri-sdlc-e2e-testreport.md`（端到端实跑报告）。
- **可扩展性设计**：新增阶段 / 新增验收标准 / 新增剖面 / 新增指令 / 替换子 SKILL 实现，均为零改动扩展（追加一行或一节）。

[1.0.0]: https://github.com/tribro-agent/skills/releases/tag/tri-sdlc-v1.0.0
