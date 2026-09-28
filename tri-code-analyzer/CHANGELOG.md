# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.4] - 2026-09-28

### 新增

- **家族横切第 10 节「宿主兼容与提问呈现」**：紧跟「版本检查与更新机制」追加 `host-compat-stub v1` 自包含瘦节——
  在提供交互式提问工具的宿主（如 Proma 的 `AskUserQuestion`）中，🔴 STOP 用户确认检查点与 clarify-gate
  MUST 以**普通 Markdown 文本**呈现为聊天问题，**NEVER 调用交互式提问工具**
  （`AskUserQuestion` / `ask_user_question` / `request_user_input` / `clarify` 及等价物）；
  用户回复契约（逐条补充 / 按默认 / 继续 / 是·否）保持不变。
  **只管呈现形式，不改任何门控的判定条件、触发时机与处置动作**；在无交互式提问工具的宿主中本条自然空转。
  细则真源 `tri-intent/references/host-compat.md`；家族规范登记于 `tri-forge/references/family-spec.md`
  §四（第 10 节注）+ §五（待登记项）。

## [1.5.3] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.5.2] - 2026-09-25

### 变更

- **新增「兜底处理（NEVER 静默失败）」章节**：补齐家族合规判据第 14 条要求的五类异常显式降级路径（版本检查异常 / 门禁不过 / 上游缺失 / hook 缺失 / 异常场景），并按本 skill 的触发源与既有机制定制。属文档补全，无行为变更（无代码改动）。

## [1.5.1] - 2026-09-24

### 变更

- **版本门节统一为 `version-stub v1` 形态**：`## 版本检查与更新机制` 收敛为 14 行（执行方式 + 真源指针）。原节为 8 行并**内联了四态判定 / 退出码语义**，违反 `references/version-check-spec.md` §六「≤30 行、禁内联细则」；细则唯一真源为该 spec，行为不变。
- 非功能性变更（文档口径），无行为变更。

## [1.5.0] - 2026-09-24

### 新增

- **交付前风险预筛自动门（tri-true 自动委派）**：解决「何时该对剖析结论深核」靠人工判断的缺口——阶段 7 交付前自动执行确定性风险预筛（R1 YMYL 领域 / R2 指导破坏性或高风险操作 / R3 无法本地自证的外部断言 / R4 低置信或 guess 溢出 / R5 作为决策或接手唯一依据），命中即自动委派 tri-true 开 `VERIFY_EXECUTE`，跑 `confidence_calc.py` 三层置信度门 + 人审盖章，落盘 `.tribro/true/<命名>/`。与契约第 10 条「结论置信标注」互补：第 10 条逐句标注（防线一行内），本条升级高影响结论为正式验证（防线升级闸）。诚实边界：自动层落地置信度门 + 事实源自检 + 人审标记；多模型交叉验证（UAF/T1-T4）需 key 与 RAG 基础设施，仅留方法论占位，NEVER 假装调用。版本号 1.4.1 → 1.5.0（新功能）。

## [1.4.1] - 2026-09-24

### 变更

- **分支收窄为编程工作流专线（22 skill）**：清理对已移除 skill 的交叉引用——职责边界表 / 不由本 skill 处理表的对应行改为「本分支未包含（原 tri-xxx）」或删除；已删的委派关系与相邻边界说明同步失效。非功能性变更（文档）。

## [1.4.0] - 2026-09-19

### Fixed

- **栈探测信号分级（根治 AND/OR 歧义，P-1）**：`references/tech-stacks/INDEX.md` 使用规则第 1 条改写为显式「主信号必中 + 辅信号加权」语义；索引表 9 行探测信号全部拆为「主信号（必中即选定）/ 辅信号（仅细化打包方式·不参与命中）」。实测修复前 AND 读法 12 个官方脚手架仅认出 7 个，修复后分级读法 16 目标命中 15 个、0 误判。
- **通用后端行信号可 grep（P-2）**：`INDEX.md` 通用后端行原信号写「按卡内信号分表匹配」（0 个可 grep token），违反 `acquire-unknown-stack.md` 自身「探测信号要可 grep」要求，导致 spring-boot/fastapi/go-mod 掉「未覆盖栈」触发联网建已存在的卡。现上提为清单文件 + 框架入口 token，仍保留「见 generic-backend.md 分表」指针。
- **uni-app 主信号收窄（P-3）**：主信号改为 `manifest.json` **且** `pages.json`（两者皆有），消除 Chrome 扩展（仅 `manifest.json`）被误判为 uni-app。
- **Agent Skills 行降为「主信号必中 + 辅信号 OR」（P-4）**：主信号仅 `skills/*/SKILL.md`（YAML frontmatter），辅信号为 OR 用于判断打包形态，解决真实插件只中 1 条被漏判。
- **`INDEX.md` 使用规则示例修正（P-5）**：原示例「Taro+React、uni-app+Vue」指向不存在的 React/Vue 独立行，改为真实并存的「Flutter + 通用后端 Go」。
- **SKILL.md 卡数声明同步（P-6）**：`SKILL.md`「已建卡栈」补 `agent-skills-plugin`（8→9）；目录结构树补 `agent-skills-plugin.md`；frontmatter description 栈列表同步补 `agent-skills-plugin`；README 目录树补 `agent-skills-plugin.md`。
- **去标识化清理（P-7）**：移除 `CHANGELOG.md` 1.3.0 条目与 `agent-skills-plugin.md` 第 8 行 / 官方文档段的 `obra/superpowers` 仓库名、上游版本号 `v6.3.0` 与 GitHub URL，中性化为「某 Agent Skills 方法论开源项目」（与家族去标识化铁律对齐）。

### Fixed（自扫描残留修复 · 2026-09-19 验证阶段发现）

- **R1 · 探测 frontmatter 闭合行扫描过窄**：`scripts/stack_detect.py` 的 `has_yaml_frontmatter` 原仅扫描前 4 行找闭合 `---`，对 5+ 行 frontmatter 的 `SKILL.md` 返回 False，导致多技能插件（如真实 find-skills 插件，frontmatter 跨 6 行）漏检为「未覆盖栈」。改为扫描前 64 行后回归集由 FAIL→PASS（16/16）。
- **R2 · 通用后端自匹配假阳性**：`Program.cs` 作为文件名片段做子串匹配会误中探测器自身源码（`stack_detect.py` 内含该 token 字符串列表）与任意提及该文件名的文本，使 tri-code-analyzer 自身被误判为通用后端。修复：① .NET 仅以 `*.csproj` 清单判定，移除 `Program.cs` 内容 token；② 新增 `IGNORE_DIRS`（`\.git`/`node_modules`/`__pycache__`/`\.tribro`/构建产物等）与 `SKIP_FILES`（`stack_detect.py`）跳过自身与仓库元数据；③ Agent Skills 主信号从 `skills/*/SKILL.md` 扩展为「或根目录 `SKILL.md`」，使单技能目录也能被识别（同步 `INDEX.md`）。修复后 tri-code-analyzer 自身正确识别为 Agent Skills 插件。

### Added

- **确定性栈探测脚本 `scripts/stack_detect.py`**：把 `INDEX.md` 分级信号落成可机械执行的逻辑，扫描目标仓库输出「命中栈 + 缺信号清单」；SKILL.md 阶段 2 与 `analysis-framework.md` 阶段 2 增加「可选确定性预检」入口，提升探测稳定性与可复现性（回归集 `.tribro/exp-code-analyzer-20260919/fixtures/` 14 骨架全绿）。

## [1.3.1] - 2026-09-18

### Added

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手架构可视化 HTML（tri-html）、通用非代码分析（tri-content）、直接改码（tri-coding/tri-fix）、代码质量打分（tri-review）与意图识别（tri-intent），强化「代码级剖析、只读不改」边界。

## [1.3.0] - 2026-09-17

### Added

- **新增第 9 张栈卡 `references/tech-stacks/agent-skills-plugin.md`**（Agent Skills 插件栈：SKILL.md 规范/渐进披露/跨平台引导注入三形态/零依赖插件工程），源于某 Agent Skills 方法论开源项目剖析实战按 `acquire-unknown-stack.md` 协议建卡；规范依据 agentskills.io/specification（已联网核验）。
- `references/tech-stacks/INDEX.md` 索引表同步登记一行（探测信号可 grep：`skills/*/SKILL.md`、`.claude-plugin/plugin.json`、`hooks/session-start`、平台适配器目录）。

## [1.2.0] - 2026-09-15

### Added

- **契约第 10 条「结论置信标注」（用户硬要求）**：报告中每一个结论性表达/观点/结果 MUST 附 ① 置信度（高/中/低）② 依据类型六选一（`事实 known`/`计算 computed`/`推断 inferred`/`常识 common`/`框架 iframe`/`猜测 guess`）③ 可验证事实源（URL 或本地代码锚，均无标「无外部来源」）；`guess` 类标低置信 + 需人工验证，占比 SHOULD ≤10%。
- `references/analysis-framework.md` 新增 §结论置信标注：三要素行内格式、六类依据判定表（含示例）、四条执行规则（判断句强制、与证据锚互补、guess 配额、联网核验降级）。
- 质量标准新增「结论置信标注」维度。本条对应 tri-forge 硬约束 27（v1.14.0），为该约束首个落地案例之一。

## [1.1.0] - 2026-09-15

### Changed

- **进化契约升级为「教训文件读写闭环」**（用户新要求，契约新增第 9 条）：
  - 启动时（版本检查第零步后）优先读取 `.tribro/code-analyzer/lessons.md`（历史执行沉淀的经验教训）；目录或文件不存在 → 静默跳过，NEVER 报错、NEVER 中断。
  - 每次执行结束后 MUST 追加本次经验教训（场景/问题/规避三段式，MUST 可操作，空泛内容禁写入）至该文件，供后续执行规避同类问题。
- 联动：自检句增加「已读教训=<N 条/无文件>」；完成判据结束态五项→六项（新增教训写入）；落盘规则补 lessons.md 载体；analysis-framework 管道新增「阶段 0 教训预载」并在阶段 7 补教训沉淀。

## [1.0.0] - 2026-09-14

### Added

- 首版发布（tri-forge 锻造，路由型下游：I10 · code-analyzer 子类）。
- 七阶段剖析管道（定位→识别→拓扑→穿透→横切→对照→交付）+ 大仓库入口优先采样策略。
- 双视角五部分交付框架（架构师视角/程序员视角/风格审计/Mermaid 图谱/上手指南）。
- 证据锚定铁律（file:line）+ 反捏造条件响应 + 深度三档（快速导览/标准剖析/深度穿透）。
- 技术栈知识库：`references/tech-stacks/` 索引 + 8 栈卡（arkts/electron/flutter/qt/react-native/taro/uni-app/generic-backend）+ 未覆盖栈获取协议（官网抓取→建卡→登记索引）+ wikihub 外部覆盖层锚点。
- Mermaid 四图引擎 + 渲染安全清单。
- 三态上游依赖检测（A 快照 / B 引导安装 / C 降级）、完成判据外化、进化契约、版本检查第零步硬门（`scripts/check_update.py` 同源）。
