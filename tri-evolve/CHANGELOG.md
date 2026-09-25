# Changelog

本文件记录 tri-evolve skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.1.7] - 2026-09-25

### 变更

- **新增「兜底处理（NEVER 静默失败）」章节**：补齐家族合规判据第 14 条要求的五类异常显式降级路径（版本检查异常 / 门禁不过 / 上游缺失 / hook 缺失 / 异常场景），并按本 skill 的触发源与既有机制定制。属文档补全，无行为变更（无代码改动）。

## [1.1.6] - 2026-09-24

### 变更

- **版本门节收敛为瘦指针 STUB**：`## 版本检查与更新机制` 由 35 行全量版收敛为 14 行（执行方式 + 真源指针），移除已失效的**远端 skillhub 内联细则**（端点解析 / 四态判定 / 升级流程 / SemVer 比较算法）。依据 `references/version-check-spec.md` §六（该节须 ≤30 行、禁内联细则）；本仓库已转自维护 fork（`scripts/check_update.py` 内置 `SELF_MAINTAINED = True`，完全跳过远端请求），原节描述的行为**永不执行**。
- **强制执行契约 §0 同步修正**：版本门措辞由「连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级」改为「运行 `scripts/check_update.py` 做本地版本一致性校验，本仓库为自维护 fork、不做远端比对」，消除 prompt 层与脚本实际行为的直接矛盾。
- 非功能性变更（文档口径），无行为变更。

## [1.1.5] - 2026-09-24

### 变更

- **新增 evolve-hook 的 pi 适配器**：`hooks/spec.md`（平台无关契约）+ `hooks/pi/index.ts`（形态 B）。落点 `agent_settled` 经真机验证一轮恰好触发 1 次；去重状态用 `pi.appendEntry` 持久化到 session（跨 reload 存活），**不使用模块级变量**。§触发时机 降级列同步更新。

## [1.1.4] - 2026-09-24

### 变更

- **补 hook 降级声明**：§触发时机 表新增「无 hook / 无调度时的降级路径」列，并显式声明 `evolve-hook` 不随包交付、未配置时仅 `APPLY`/`ADMIN` 可用。依 `family-spec.md` §1.5。

## [1.1.3] - 2026-09-24

### 变更

- **清理对已移除 skill 的引用**：正文中 `tri-cache` / `tri-ask` 的边界说明与示例改为「本分支未包含（原 tri-xxx）」标注或指向现存 skill；信号渠道③（缓存命中）加注「本分支不可用」。非功能性变更（文档）。

## [1.1.2] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手意图识别、业务作答、历史缓存存储与元操作纠偏，转出/归属对应 skill 呼应家族 MECE。

## [1.1.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源 `tri-intent/references/version-gate.md`，消除各 skill 内的重复表述
- frontmatter version `1.1.0` → `1.1.1`

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

- frontmatter version `1.0.2` → `1.1.0`

## [1.0.2] - 2026-08-02

### 安全与一致性（全量评审优化 · P0）

#### 调度安全门（自主执行约束）
- 新增 `## 调度安全门（自主执行约束 · P0）`：明确本 skill 默认为**手动批处理技能，不是自主 Agent**；定时/批量能力依赖外部调度器，未配置时降级为手动触发。
- `EVOLVE_LEARN` 默认仅接受用户显式指令；定时为 opt-in（`templates/meta.json` 中 `schedule.enabled=true`，默认 false）。
- 批次幂等：`run.lock` + `run-log.jsonl`（run_id / 水位 `last_processed_offset`）；连续 3 次失败自动停用并通知；`signals.jsonl`/`run-log.jsonl` 按容量轮转。
- 副作用门控：所有自动写入可回滚；中/高风险经 A/B 验证门或人工审批，NEVER 静默自动应用。

#### 一致性
- 「14 个下游」陈旧计数 → 「21 个下游执行 skill（数量见 family-spec §1.3）」。
- 经验条目库字段表与 `schemas/evolve-schema.md` 去双写，SKILL.md 改为指针。
- `## 目录结构` 补登 `tests/`，与磁盘实况对齐。
- 测试集 frontmatter 版本联动至 v1.0.2。

## [1.0.1] - 2026-08-01

### 修复

#### 目录结构图清理（合规）
- 删除 SKILL.md「目录结构 / 配套文件」中列出的 `LICENSE` / `.gitignore` 条目，遵循《tri-skill-规范与生成指南》§4.1「禁止生成的文件」硬约束（许可证仅由 frontmatter `license` 字段声明，忽略策略由仓库统一管控）。
- 本版本无功能变更，仅文档合规修正（PATCH）。

## [1.0.0] - 2026-08-01

### 新增

- **初始版本**：tri-evolve 横向学习/进化型 skill，为 tri-xxx 家族提供多渠道信号驱动的持续改进与用户画像构建能力
- **三种工作模式**：EVOLVE_OBSERVE（被动观察，hook 触发）/ EVOLVE_LEARN（主动学习，定时批量）/ EVOLVE_APPLY（主动应用，下游请求）
- **OODA 进化闭环**：观察（六渠道信号采集）→ 归因（模式识别+异常检测）→ 提议（带置信度）→ 验证（A/B 小流量）→ 沉淀（verified 入库），五阶段闭环
- **六渠道信号源**：用户显式反馈 / 隐式行为 / tri-cache 命中统计 / tri-meta 纠偏记录 / 快照分布 / 会话轨迹
- **经验条目库**：Voyager 式可检索复用（非 append-only 日志），每条经验带 embedding 索引，相似场景语义检索复用
- **用户画像四层**：静态属性 / 风格偏好 / 主题偏好 / 交互习惯；静态稳定、动态时间衰减（半衰期 30 天）；追踪偏好演变历史
- **外部信号锚定**：改进提议 MUST 锚定外部信号（generator-verifier gap 防护，Reflexion 启示），纯自我批判 NEVER 沉淀
- **A/B 验证门**：提议经小流量对照验证（lift ≥5% 且 p<0.05 且样本 ≥30）才沉淀为 verified 经验
- **安全分级与回滚**：低/中/高三风险级（自动应用 / A/B 验证 / 人工审批）；每次沉淀带版本可回滚；`rollback` / `restore` 命令
- **画像隐私保护**：敏感属性（health/political/religious/sexual）NEVER 推断 NEVER 写入；支持导出（export）/ 删除（delete）/ 脱敏（GDPR 式权利）
- **上游依赖检测三态逻辑**：完整模式（有 tri-intent+tri-cache）/ 引导安装 / 降级模式（退化为会话内反馈学习）
- **schema 与模板**：`schemas/evolve-schema.md` 定义 lessons/profile/proposals/baseline 四库表结构与状态机；`templates/meta.json` 配置模板（A/B 阈值/衰减/风险分级/敏感属性）
- **质量标准九维**：信号完整性 / 外部锚定 / 验证门 / 高风险审批 / 画像分层 / 隐私保护 / 回滚可用 / 经验复用延迟 / 错误学习率
