# Changelog

All notable changes to this skill will be documented in this file.


## [1.2.7] - 2026-09-28

### 新增

- **家族横切第 10 节「宿主兼容与提问呈现」**：紧跟「版本检查与更新机制」追加 `host-compat-stub v1` 自包含瘦节——
  在提供交互式提问工具的宿主（如 Proma 的 `AskUserQuestion`）中，🔴 STOP 用户确认检查点与 clarify-gate
  MUST 以**普通 Markdown 文本**呈现为聊天问题，**NEVER 调用交互式提问工具**
  （`AskUserQuestion` / `ask_user_question` / `request_user_input` / `clarify` 及等价物）；
  用户回复契约（逐条补充 / 按默认 / 继续 / 是·否）保持不变。
  **只管呈现形式，不改任何门控的判定条件、触发时机与处置动作**；在无交互式提问工具的宿主中本条自然空转。
  细则真源 `tri-intent/references/host-compat.md`；家族规范登记于 `tri-forge/references/family-spec.md`
  §四（第 10 节注）+ §五（待登记项）。

## [1.2.6] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.2.5] - 2026-09-25

### 变更

- **新增「兜底处理（NEVER 静默失败）」章节**：补齐家族合规判据第 14 条要求的五类异常显式降级路径（版本检查异常 / 门禁不过 / 上游缺失 / hook 缺失 / 异常场景），并按本 skill 的触发源与既有机制定制。属文档补全，无行为变更（无代码改动）。

## [1.2.4] - 2026-09-24

### 变更

- **版本门节收敛为瘦指针 STUB**：`## 版本检查与更新机制` 由 35 行全量版收敛为 14 行（执行方式 + 真源指针），移除已失效的**远端 skillhub 内联细则**（端点解析 / 四态判定 / 升级流程 / SemVer 比较算法）。依据 `references/version-check-spec.md` §六（该节须 ≤30 行、禁内联细则）；本仓库已转自维护 fork（`scripts/check_update.py` 内置 `SELF_MAINTAINED = True`，完全跳过远端请求），原节描述的行为**永不执行**。
- **强制执行契约 §0 同步修正**：版本门措辞由「连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级」改为「运行 `scripts/check_update.py` 做本地版本一致性校验，本仓库为自维护 fork、不做远端比对」，消除 prompt 层与脚本实际行为的直接矛盾。
- 非功能性变更（文档口径），无行为变更。

## [1.2.3] - 2026-09-24

### 变更

- **分支收窄为编程工作流专线（22 skill）**：清理对已移除 skill 的交叉引用——职责边界表 / 不由本 skill 处理表的对应行改为「本分支未包含（原 tri-xxx）」或删除；已删的委派关系与相邻边界说明同步失效。非功能性变更（文档）。

## [1.2.2] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手一次性完成即交付的任务执行（对应 I 落点 skill）、对既有代码的单点调试修复（tri-fix）与意图识别（tri-intent），强化「建长期运行循环体」边界。

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

- frontmatter version `1.1.2` → `1.2.0`

## [1.1.2] - 2026-08-02

### 变更

- **`### 五、质量标准` 提升为 `## 质量标准`**：与 §落盘规则 同级，消除「二级章节下挂三级质量标准」的层级错位
- **`## 核心能力` 与 `## 处理流程` 去重合并**：`## 处理流程` 确立为 scaffold/bootstrap 全链路的唯一权威定义；`## 核心能力` 六项能力压缩为索引表（一句话定义 + 权威定义位置），删除重复叙述，SKILL.md 由 402 行降至 352 行
- **处理流程补入被合并的权威内容**：新增 `### Charter 5 项输入`（含默认值与收集策略）、`### 真实测试运行`（小规模动作示例 + dry run 规则）、`### 记录格式（两个必需输出）`（Timeline 一行格式 + LOG.md 条目格式）三个子节
- **§交付产物 · LOG.md 条目结构** 改为指向 §处理流程 · 记录格式，避免格式两处维护

### 新增

- **`tests/tri-loop-full-testcases.md` 补齐 frontmatter**（name/description，标注被测版本 v1.1.2）与 `## 零、能力清单`（A–H 八组共 40 个能力点），并给出「能力组 → 测试组」映射，使 47 个既有用例可回溯覆盖率

## [1.1.1] - 2026-07-30

### 变更

- **落盘规则标题层级统一**：`### 五、落盘规则` 提升为 `## 落盘规则`（二级标题），与 tri-action/tri-content/tri-plan 等 10 个 skill 保持一致
- **子章节编号顺延**：`### 六、质量标准` 顺延为 `### 五、质量标准`（消除落盘规则移出后的编号断号）

## [1.1.0] - 2026-07-30

### Added
- 新增 `templates/result.md` 执行结果模板（8 章节：Loop Charter + Substrate 状态 + 测试运行摘要 + Artifact 记录 + 缺失项 + 如何再次运行 + 引用 + 自检）
- tri-loop 链路文档统一落盘到 `.tribro/loops/<命名>/result.md`，与 tri-intent（`.tribro/snapshots/`）、tri-action（`.tribro/actions/`）保持一致
- 新增落盘规则 section，明确 tri-loop 链路文档与知识库内容文件的路径分离
- 阶段速查表新增第 8 阶段「执行结果落盘 result.md」
- 质量标准新增「执行结果落盘」和「.tribro 目录一致」两个维度
- 新增 TG-11 测试组（4 个用例）：result.md 落盘路径、结构完整性、与知识库分离、.tribro 目录一致性
- 自动化测试新增 TG-10（20 个用例）：.tribro/loops/ 路径引用、落盘规则、result.md 结构、模板内容验证

### Changed
- SKILL.md 产物结构规格中 result.md 引用 `templates/result.md` 模板
- 目录结构新增 `templates/result.md`
- 测试用例总数从 43 增至 47

## [1.0.0] - 2026-07-30

### Added
- 初始版本，蒸馏自 new-loop 开源项目
- 6 大核心能力：Substrate Bootstrap、Loop Charter 收集、Loop README Scaffold、真实测试运行、Timeline + LOG.md 记录、回报
- 三态依赖检测：Mode A（快照模式）、Mode B（引导安装）、Mode C（降级模式）
- 强制执行契约 5 条（含最小化原则门禁规则）
- 9 个模板文件：loop-readme、architecture、log、claude-template、claude-kb-section、signals-readme、docs-readme、domains-readme、knowledge-setup
- 全场景测试用例
- 支持 tri-intent 下游路由（I14 · loop/domain 创建子类）
- 支持独立运行（降级模式）
