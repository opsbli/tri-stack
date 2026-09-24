# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
