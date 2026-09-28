# tri-workflow 变更日志


## [1.2.8] - 2026-09-28

### 新增

- **家族横切第 10 节「宿主兼容与提问呈现」**：紧跟「版本检查与更新机制」追加 `host-compat-stub v1` 自包含瘦节——
  在提供交互式提问工具的宿主（如 Proma 的 `AskUserQuestion`）中，🔴 STOP 用户确认检查点与 clarify-gate
  MUST 以**普通 Markdown 文本**呈现为聊天问题，**NEVER 调用交互式提问工具**
  （`AskUserQuestion` / `ask_user_question` / `request_user_input` / `clarify` 及等价物）；
  用户回复契约（逐条补充 / 按默认 / 继续 / 是·否）保持不变。
  **只管呈现形式，不改任何门控的判定条件、触发时机与处置动作**；在无交互式提问工具的宿主中本条自然空转。
  细则真源 `tri-intent/references/host-compat.md`；家族规范登记于 `tri-forge/references/family-spec.md`
  §四（第 10 节注）+ §五（待登记项）。

## [1.2.7] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.2.6] - 2026-09-25

### 变更

- **新增「兜底处理（NEVER 静默失败）」章节**：补齐家族合规判据第 14 条要求的五类异常显式降级路径（版本检查异常 / 门禁不过 / 上游缺失 / hook 缺失 / 异常场景），并按本 skill 的触发源与既有机制定制。属文档补全，无行为变更（无代码改动）。

## [1.2.5] - 2026-09-24

### 变更

- **版本门节收敛为瘦指针 STUB**：`## 版本检查与更新机制` 由 35 行全量版收敛为 14 行（执行方式 + 真源指针），移除已失效的**远端 skillhub 内联细则**（端点解析 / 四态判定 / 升级流程 / SemVer 比较算法）。依据 `references/version-check-spec.md` §六（该节须 ≤30 行、禁内联细则）；本仓库已转自维护 fork（`scripts/check_update.py` 内置 `SELF_MAINTAINED = True`，完全跳过远端请求），原节描述的行为**永不执行**。
- **强制执行契约 §0 同步修正**：版本门措辞由「连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级」改为「运行 `scripts/check_update.py` 做本地版本一致性校验，本仓库为自维护 fork、不做远端比对」，消除 prompt 层与脚本实际行为的直接矛盾。
- 非功能性变更（文档口径），无行为变更。

## [1.2.4] - 2026-09-24

### 变更

- **分支收窄为编程工作流专线（22 skill）**：清理对已移除 skill 的交叉引用——职责边界表 / 不由本 skill 处理表的对应行改为「本分支未包含（原 tri-xxx）」或删除；已删的委派关系与相邻边界说明同步失效。非功能性变更（文档）。

## [1.2.3] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手节点内具体业务逻辑编码（tri-coding）、驱动真实项目走完流程的落地交付（tri-sdlc）、单次副作用动作（tri-action）与意图识别（tri-intent），强化「产流程定义即交付」边界。

## [1.2.2] - 2026-08-14

### 变更

- **description 补全「支持独立安装」声明**：frontmatter description 追加「支持独立安装，含上游依赖检测三态逻辑」字样，满足 compliance-checklist 第 2 条字面要求（MECE 审计 F5）
- frontmatter version `1.2.1` → `1.2.2`
- **SKILL.md ≤500 行合规（约束 #13）**：将 §核心架构 的 45 行 ASCII 流水线架构图下沉至 `references/workflow-architecture.md`（含阶段职责速查表），正文改指针；目录结构树同步新增该文件。版本号不变（内部重构，无接口/行为变更）

## [1.2.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源 `tri-intent/references/version-gate.md`，消除各 skill 内的重复表述
- frontmatter version `1.2.0` → `1.2.1`

## [1.2.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.1.1` → `1.2.0`

## [1.1.1] - 2026-08-02

### 变更（合规与一致性）

- **上游依赖检测三态对齐**：描述与 `## 上游依赖检测` 章节统一为三态（A 快照模式 / A0 待识别 / B 独立降级），修正原 description 中「两态逻辑（快照模式/独立降级模式）」的不一致
- **作答前声明标准化**：强制执行契约第 7 条改为「本次意图=<I13/I14>，已读取快照=<是/否>，模式=<快照/待识别/降级>，当前阶段=<1-7>」
- **删除过时路由注记**：移除「若 tri-intent 尚未注册本 skill 的路由…」段落——tri-intent 已注册本 skill 路由（I13/I14）

### 重构（去重）

- **阶段 1/2/4/5 内联 schema/规则表外置**：将 env-profile、workflow-model 内联 yaml 与校验维度表替换为摘要 + 指针，详细定义统一指向 `schemas/`（env-profile.schema.md、workflow-model.schema.md）与 `validators/`（dependency-checker.md、executability-validator.md）；SKILL.md 由 ~548 行精简至 ~453 行，保留 13 章骨架

### 新增

- **README.md**：特性、独立安装、用法、目录结构
- **tests/tri-workflow-full-testcases.md**：基于 tri-workflow v1.1.1 全量扫描生成（能力清单 A–H + 覆盖 7 阶段真实用例）

## [1.1.0] - 2026-07-30

### 新增

- **`.tribro/workflows/` 链路文档落盘**：与 tri-intent（`.tribro/snapshots/`）、tri-action（`.tribro/actions/`）、tri-loop（`.tribro/loops/`）保持一致
- **执行结果落盘**：tri-workflow 执行结果落盘于 `.tribro/workflows/<命名>/result.md`，含工作流摘要 + 产物清单 + 模板匹配度 + 优化变更摘要 + 依赖校验结果 + 可执行性验证结果 + 引用
- **中间产物落盘**：env-profile.yml / workflow-model.yml / validation-report.md 统一落盘于 `.tribro/workflows/<命名>/` 下，供追溯
- **落盘规则 section 重构**：明确区分 tri 链路文档（`.tribro/workflows/`）与工作流产物（用户指定目录 / 默认业务目录），路径分离不混淆

## [1.0.3] - 2026-07-29

### 功能增强（P2）

- **阶段 7 补充自动触发场景**：新增 §7.4 自动触发场景，包含三个子机制：
  - **7.4.1 Webhook 回调自动收集**：工作流设计文档嵌入 Webhook 回调端点，外部系统在节点完成/失败/工作流完成时自动上报执行数据
  - **7.4.2 定时运行报告生成**：schedule/event 触发类型的工作流自动附带定时报告配置（成功率/耗时/SLA达标率/失败TOP5），报告渠道支持飞书消息卡片/邮件/文档链接
  - **7.4.3 自动重入流水线**：SLA 达标率 < 80% 自动触发阶段 4 优化、新 Skill/MCP 注册自动触发阶段 1 环境感知、模板版本落后自动提示升级。默认为建议模式，用户确认后切换自动模式

## [1.0.2] - 2026-07-29

### 严重阻断修复（P0）

- **N1 incident-response postmortem 全路径死锁**：`postmortem` 的 `depends_on: [notify_recovered, create_ticket]` AND 语义导致所有路径死锁（P0/P1 路径 create_ticket 不执行，P2/P3 路径 notify_recovered 不执行）。修复为 `depends_on: [notify_recovered]`，新增 `close_ticket` 节点处理 P2/P3 工单关闭路径，移除 `create_ticket → postmortem` 边，新增 `create_ticket → close_ticket` 边

### 重要缺陷修复（P1）

- **N2 SKILL.md 版本号不一致**：frontmatter `version` 从 `1.0.0` 更新为 `1.0.2`，与 CHANGELOG 保持同步
- **N3 SKILL.md 触发类型遗漏**：§2.3 产出模板中 `api_callback` 修复为 `webhook`，§输入契约 模式 B 中「API回调」修复为「Webhook」，与 workflow-model schema 和 workflow-dsl schema 完全一致
- **N4 code-review-flow edge 条件不匹配**：edges 中 `all_passed == true` 无对应节点输出变量（`all_passed` 未在任何节点 outputs 中定义），修复为与 condition 节点表达式一致的条件，同时统一为不带节点前缀的输出变量名（`review_passed`/`ci_passed`/`approved`）
- **N5 code-review-flow 非标准 else 关键字**：condition 节点使用 `expression: "else"` 但 schema 未定义 `else` 关键字，修复为显式否定表达式 `review_passed == false || ci_passed == false || approved == false`
- **N6 release-flow rollback 空输入**：`rollback` 节点 `inputs: []` 无法确定回滚目标，补充引用 `version_package.outputs.release_artifact` 和 `release_version` 作为回滚目标依据

### 设计优化（P2）

- **N7 ci-cd-pipeline 审批与部署分离**：将 `deploy_production`（type: approval）拆分为 `approve_production`（type: approval，输出审批结果）和 `deploy_production`（type: auto，依赖审批通过后执行部署），使审批与执行职责清晰分离，edges 同步更新

## [1.0.1] - 2026-07-29

### 严重阻断修复（P0）

- **B1 独立模式矛盾**：将模式 B 从「硬阻断引导安装」改为「独立降级模式」，使独立使用真正可用。降级模式下跳过快照读取，直接从对话提取需求，阶段 1 环境感知仅扫描本地 Skills/MCP
- **B2 incident-response 死锁**：修复 `impact_assess` 的 `depends_on` 从 `[severity_check, notify_oncall]` 改为 `[severity_check]`，P1 路径不再阻塞
- **B3 multi-agent-orchestration 死锁**：修复 `final_output` 的 `depends_on` 从 `[conflict_decision, resolve_conflict]` 改为 `[conflict_decision]`，无冲突路径不再阻塞
- **B4 approval-flow 死锁**：将 `notify_reject` 拆分为 `notify_first_reject` 和 `notify_second_reject` 两个独立通知节点，消除 AND 语义死锁
- **B5 缺失 DAG 输出后端**：新建 `templates/output-backends/dag-config-output.md`，支持 Airflow/Prefect/Dagster/通用 YAML 四种 DAG 配置输出
- **B6 edges 条件不一致**：统一 approval-flow edges 中的条件表达式变量名（`approved` → `first_approval_result`/`second_approval_result`）

### 重要缺陷修复（P1）

- **M1 触发类型命名统一**：workflow-model schema 中 `api_callback` 统一为 `webhook`，与 DSL schema 一致
- **M2 deploy_production 审批机制**：ci-cd-pipeline 模板中 `deploy_production` 从 `type: auto` 改为 `type: approval`，添加审批人配置
- **M3 post_deploy_check 输入引用**：release-flow 模板中 `post_deploy_check` 的 `inputs` 从空数组补充为引用 `full_deploy.outputs.deploy_result`
- **M4 孤立节点检测 DSL 适配**：executability-validator 规则 3 增加从 `jobs.needs` 推导边的逻辑，支持 workflow-dsl 格式输入
- **M5 审批驳回检测逻辑**：dependency-checker 规则 7 增加通知分支模式检测，识别 AND 语义死锁并要求拆分

### 新增

- env-profile schema 新增 `tech_stack.orchestration` 字段，支持 DAG 平台检测
- SKILL.md 输出后端映射表新增 DAG 配置输出条目
- SKILL.md 目录结构更新，包含 dag-config-output.md

## [1.0.0] - 2026-07-29

### 首次发布

- **核心架构**：7 阶段混合智能流水线（环境感知→模板匹配→对话补全→编译优化→校验验证→多目标输出→迭代反馈）
- **双模式入口**：独立使用（对话提取需求）和下游执行（读取 tri-intent 快照 §三）
- **上游依赖检测**：两态逻辑（快照模式/独立降级模式）
- **7 个预置工作流模板**：CI/CD 流水线、代码审查流、业务审批流、数据处理流、发布流水线、多 Agent 协作编排、故障响应流程
- **5 种交付形态**：SKILL.md、设计文档、CI/CD 配置、审批流模板、DAG 配置
- **统一 DSL**：工作流声明式 DSL（`workflows/<name>.wf.yml`）作为可版本管理的单一事实来源
- **Node Registry**：可复用节点注册表，积累 34 个高频节点，覆盖代码工程/协作沟通/审批流程/数据处理/监控告警/条件分支 6 大类
- **3 个 Schema 定义**：env-profile、workflow-model、workflow-dsl
- **2 个校验器**：依赖校验（8 规则）、可执行性验证（8 规则）
- **5 个输出后端**：SKILL.md、设计文档、CI 配置、审批模板、DAG 配置
- **质量门禁**：9 维度质量标准，阻断项 = 0 方可进入阶段 6
- **设计原则**：编译器三段式、混合智能四阶段、Terraform plan-apply、BPMN 五要素节点、GitHub Actions 可复用市场
- **MECE 合规**：独立使用完整闭环，作为下游 skill 不越界，最小化原则