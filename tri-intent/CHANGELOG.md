# Changelog

本文件记录 tri-intent skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.14.0] - 2026-09-24

### 变更

- **分支收窄为编程工作流专线（22 skill）**：清理对已移除 skill 的交叉引用——职责边界表 / 不由本 skill 处理表的对应行改为「本分支未包含（原 tri-xxx）」或删除；已删的委派关系与相邻边界说明同步失效。非功能性变更（文档）。

## [1.13.1] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：在「触发时机」新增 Not-Trigger 子节，明确不接手已定意图的重识别、下游产出（需求/设计/任务/报告/回答）与具体领域执行，强化意图识别总路由的 MECE 边界。

## [1.13.0] - 2026-09-16

### 变更

- **R4 豁免登记补记（tri-geo · 独立领域入口型）**：§一「其余不参与本表路由的 skill 及理由」全量枚举追加 `tri-geo` 行——GEO 单领域入口（国内生成式引擎优化），用户显式调用激活，不经 L2 意图路由；豁免理由：GEO 为跨内容/技术/渠道的独立领域闭环，现行 27 个 L2 落点无对应项。同步将该句中的硬编码「39 个顶层」改为非计数表述（约束 17：禁易漂移硬编码计数）。
- 来源：tri-geo v1.0.0→v1.0.1 家族合规审计 P-1 项（方案 A：豁免登记），审计报告 `docs/audit-tri-geo-20260916.md`。
- 版本联动：SKILL frontmatter / CHANGELOG / tests frontmatter / `_meta.json` 全部 1.13.0；顺带修正 tests frontmatter `version` 字段滞留 1.11.2 的约束 14 违例。

## [1.12.0] - 2026-09-15

### 变更

- **门③路由接通补记（I10 深度剖析子类 code-analyzer · tri-forge v1.15.0 门③第⑥步双向版本文件同步首次执行）**：
  - SKILL.md 路由映射表 I10 行追加「深度剖析子类（I10）→tri-code-analyzer/」；新增 I10 深度剖析子类说明 note（触发语义/一跳覆写/与 arch-viz MECE 及冲突消解/依赖检测路径）；计数 38→39 个顶层 skill、34→35 个 tri-*（28 路由型 + 7 横向型）。
  - README.md L3 子类路由表追加 `code-analyzer` 行。
  - doing/I10-analyze.md 子类路由扩为三个（arch-viz/audit-checklist/code-analyzer）+ MECE 表更新 + §冲突消解新增。
  - 2026-09-14 路由接通当日未随改 bump（门③五步时代无版本同步步），本条目按 tri-intent-integration.md §⑥ 补记。
- 版本联动：SKILL frontmatter / CHANGELOG / tests frontmatter / _meta.json（workbuddy + trae_cn）/ lock 注册表 全部 1.12.0；修复 trae_cn 侧 _meta 滞留 1.10.0 与 lock 缺 tri-intent 条目。

## [1.11.3] - 2026-09-08

### 变更

- I08 x2md 族路由说明回填（anydoc-main 蒸馏报告 v1.3.0 Phase 2 门③）：SKILL.md / doing/I08-translate.md / README 三处扩展名族更新——docx2md=.docx/.docm/.doc、pptx2md=.pptx/.pptm/.pps/.pot/.ppsx/.ppsm/.ppt、xlsx2md=.xlsx/.xlsm/.xls/.xlsb/.csv、html2md=.html/.htm；MECE 依据补「同族扩展名归同一 skill」与五格式 SKIP 语义；路由计数 27 不变

## [1.11.2] - 2026-09-03

### 修复

- **§四 对称关系计数口径修正**（描述性硬编码过期）：§四「下游 skill → 上游」括注原为「29 个 tri-* skill 已实现，含 25 个路由型 + 4 个横向型」，与 §一 现行枚举脱节（横向已于 1.11.0 扩为 7 个；路由型随 pm/frontend-design/sdlc/workflow/loop 等子类补齐而增长）。修正为现行口径「33 个（26 路由型 + 7 横向型）」，并新增计数口径说明（路由型 = 路由映射表下游 slug 去重 27 扣除「不落盘」tri-express；横向型 = §一全量枚举 7 个），附 MUST 联动防漂移约束

### 变更

- frontmatter version `1.11.1` → `1.11.2`（tests / testreport / _meta.json 四同步）

## [1.11.1] - 2026-09-02

### 变更

补齐二级下钻文档的子类路由定义（意图识别完整性收尾）：`doing/I06-content-gen.md` 补 article/pm 子类小节、`doing/I11-coding.md` 补 frontend-design/sdlc 子类小节、`doing/I15-multimedia.md` 补 music 子类小节，`doing/SKILL.md` 判定要点补 music 子类。此前主表 SKILL.md 已声明子类但二级下钻文档缺失，导致下钻时子类不可识别（意图识别不准确/分发错误根因）
## [1.11.0] - 2026-09-02

### 新增

- **I06 PM 产物子类路由**（P0 断链修复）：tri-pm 自声明「认领 I06 的 PM 产物子类（L3_子意图=pm）」，但本 skill 路由映射表/L3 表此前无 pm 子类定义，导致该下游经意图路由不可达。补齐：路由映射表 I06 行 + 子类说明 + `doing/SKILL.md` 判定要点 + README L3 表
- **I11 前端设计方向子类路由**（P0 真空断链修复）：tri-frontend-design 自含「快照/引导/降级」三态上游检测，但此前无任何路由入口或委派方（真空断链）。补齐 I11 frontend-design 子类：设计方向语义覆写为 tri-frontend-design，代码实现仍走 tri-coding 默认

### 变更

- 「横向 skill 不参与本表路由」说明扩为全量枚举：补 tri-cost / tri-guard / tri-humanize（横向方法论），并补 tri-forge / tri-learn / tri-jobhunt 不纳入路由的理由说明，使 38 个顶层 skill 路由状态全量可查
- frontmatter version `1.10.0` → `1.11.0`
## [1.10.0] - 2026-08-05

> 下游分发闭环版本。将「意图识别 → 下游安装 → 下游执行」串成不断链的流水线，并修复版本门自动升级的死命令。

### 新增

- **下游分发两道确认门**（SKILL.md §下游依赖检测 三、分发处置）：未安装下游时走门① 安装确认 → 发送安装 prompt → 复检 → 门② 执行确认，两个不可逆动作各留一个用户出口，含 mermaid 分发状态机
- **`scripts/check_downstream.py`**：确定性检测下游 skill 安装状态，覆盖四处安装位置（家族源码树 / `.tribro/skills/` / 平台用户级 / 平台项目级）+ `.skills_store_lock.json` 注册表，输出 `installed`/`activatable`，退出码 0=全装 / 1=有缺
- **强制执行契约第 6 条（下游分发强制）**：未安装时 MUST 走两道门，NEVER 擅自安装、NEVER 擅自执行、NEVER 越界代答

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，全量改为 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本门三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），P1 由「终态阻断」改为「过程阻断」（先触发自动升级，失败才降级）
- **契约第 7 条自检句**：扩充为含版本检查四态与下游分发状态
- frontmatter version `1.9.0` → `1.10.0`

## [1.9.0] - 2026-08-03

> 版本检查前置硬门版本。依据《tri-skill-规范与生成指南.md》§3.14 全 skill 强制约束，新增版本检查与更新机制作为执行流程第零步。

### 新增

- **版本检查与更新机制（§版本检查与更新机制）**：新增完整独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 下游依赖检测 → 路由识别的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入路由步骤
- **路由步骤第 0 步（版本检查）**：路由步骤顶部声明执行顺序固化，步骤 0 显式要求先通过版本检查方可进入核心路由流程

### 变更

- **自检句**：扩充 `版本检查=<已通过/离线降级>` 字段，使每次执行时版本检查状态可追溯
- frontmatter version `1.7.1` → `1.9.0`

## [1.7.1] - 2026-08-02

### 重构（全量评审优化 · 渐进披露 + 取消 tri-forge 下游注册）

#### 取消 tri-forge 下游注册（内部专用工具）
- 移除 forge 子类路由（路由步骤 step 9、§一路由映射表 forge note、doing/SKILL.md forge 消歧、doing/I21-distill.md forge 分支、README L3 表 forge 行）；tri-forge 重新定位为内部专用工具，用户直接调用。
- §四对称检测计数回正为「21 个 tri-* skill（17 路由型 + 4 横向型）」。
- 保留 `.tribro/skills/` 检测路径（服务被锻造的下游 skill 发现）。

#### 渐进披露（大块参考外移）
- 置信度机制（四维权重表+三档阈值）、快照定位契约与异常处置表、意图确认卡 YAML 模板三块移入 `references/`（confidence-mechanism.md / snapshot-contract.md / intent-confirm-card.md），SKILL.md 保留 H2 标题 + 摘要 + 指针。
- §目录结构 补登 `references/`。
- 修复重复的「9.」步骤编号（forge 步骤已移除，多意图消歧为唯一 step 9）。
- 测试集 frontmatter 版本联动至 v1.7.1。

## [1.7.0] - 2026-08-02

> 路由扩展版本。新增全生命周期（SDLC）子类路由，补全 tri-sdlc 九阶段编排器的一跳分发出口。

### 新增

- **I11/I13/I14 全生命周期（SDLC）子类路由**：L2 ∈ {I11 编码开发, I13 规划拆解, I14 操作执行} 且任务要点含全生命周期语义（全生命周期/SDLC/研发流程/立项到上线/端到端交付/完整开发流程/从需求到发布/阶段门禁）时，`L3_子意图` 标注 `sdlc`，`下游路由建议` 覆写为 **tri-sdlc**（一跳）。三个 L2 共用同一子类键——「按完整流程做个项目」的表层动词可能是编码、规划或推进执行，但交付对象同为「一个走完九阶段的真实项目」
- 新增子类路由指南 `doing/sdlc-design.md`：识别特征、7 类邻近意图边界表、优先级消歧规则、路由判定流程、剖面线索提示、tri-sdlc 激活条件、对称检测说明
- `hooks/intent-gate.py` 的 `SUBTYPE_SLUGS` 新增 `("I11","sdlc")` / `("I13","sdlc")` / `("I14","sdlc")` → `tri-sdlc`，使 `--intent I11 --subtype sdlc` 解析出 slug `tri-sdlc`
- §路由步骤 新增第 5 步「全生命周期（SDLC）子类路由」，并显式声明其**优先级高于** workflow 子类（原第 5 步，现第 6 步）与 loop 子类（原第 6 步，现第 7 步）；原第 7–11 步顺延为第 8–12 步

### 变更

- §顶部落盘映射表、§一路由映射表、`doing/SKILL.md` 二级判定表与消歧要点：I11/I13/I14 三行同步标注 sdlc 子类出口
- 意图确认卡 `L3_子意图` 取值由 `workflow | loop | music` 补全为 `sdlc | workflow | loop | music | article`（`article` 为 1.6.0 引入但未同步进确认卡的遗漏）
- §四 双向检测计数由「20 个（16 路由型 + 4 横向型）」更新为「21 个（17 路由型 + 4 横向型）」，新增路由型下游 tri-sdlc
- §目录结构 `doing/` 说明补入 loop 与全生命周期子类路由

### 说明

- tri-sdlc 的 9 个阶段子SKILL（`tri-sdlc/children/tri-charter` … `tri-ops`）随 tri-sdlc 包分发，**不是顶层 skill，不参与本 skill 路由表**；其上游检测对象为 tri-sdlc 编排器（两态：编排模式 / 引导安装）。该处理方式与 tri-mm 的 4 个媒体子SKILL 一致

## [1.6.1] - 2026-08-01

### 修复

- **下游 skill 计数更正**：§四「与下游 skill 上游检测的对称关系」中计数由「19 个（15 路由型 + 4 横向型）」更正为「20 个（16 路由型 + 4 横向型）」。原因：1.6.0 新增 I06 文章撰写子类路由（→ tri-article）后，路由型下游由 15 增至 16，总数由 19 增至 20；此前计数未随路由补全同步更新，与 §路由映射表（已含 tri-article 出口）不一致。本版本无功能性代码变更。

## [1.6.0] - 2026-08-01

> 路由补全版本。补上全量审计发现的唯一孤儿分发目标 tri-article（I06 文章撰写子类），并澄清 I08/tri-translate 边界。

### 新增

- **I06 文章撰写子类路由**：L2=I06 内容生成且任务要点含文章撰写语义（写文章/去 AI 化文章/技术文章/博客/个人风格长文）时，`L3_子意图` 标注 `article`，`下游路由建议` 直接覆写为 **tri-article**（一跳，无需中介），补全此前缺失的孤儿分发出口
- `hooks/intent-gate.py` 的 `SUBTYPE_SLUGS` 新增 `("I06", "article"): "tri-article"`，使 `--intent I06 --subtype article` 解析出 slug `tri-article`
- 路由映射表 §一 新增 I06 文章子类注解与 I08/tri-translate 边界说明（I08 统一路由 tri-content，tri-translate 为横向方法论由 tri-content 委派）

### 修复

- **[P1] tri-article 孤儿分发目标**：tri-article 自述「可经 tri-intent 下游路由接入」，但路由表与 `intent-gate.py` 均无指向它的出口，导致用户经意图识别无法自动路由到文章生成 skill。现通过 I06 文章子类闭环

## [1.5.0] - 2026-08-01

> 全量审计修复版本。修复 P0 级路由缺陷 4 项、P1 级能力缺失 3 项，新增置信度门控机制与快照定位契约。

### 新增

- **置信度机制（§置信度机制）**：四维加权打分（动词明确性 0.35 / 语料匹配度 0.25 / 邻近意图排除强度 0.25 / 上下文完备度 0.15），三档阈值门控——高(≥0.85) 直接交接、中(0.60–0.85) 强制轻量复述、低(<0.60) 强制回退 clarify-gate；竞争意图规则（主次分差 <0.15 强制复述并列候选）；Expressing/M05 免打断例外；未评估时按中档保守兜底
- **快照定位契约（§存放目录）**：新增 `.tribro/LATEST.md` 指针文件（覆盖写），下游按「指针 → 会话内最新 → 全局最新且 ≤30 分钟」三级优先级定位快照，解决快照永不覆盖导致下游无法确定读哪个文件的问题
- **快照异常处置表**：统一约定快照缺失/过期/损坏/字段不全/意图越界/低置信度六类异常的下游处置动作
- **CR 代码审查规范编码**：为原本游离于编码体系外的字符串路由键「代码审查」赋予机器可读编码 `CR`，落点总数明确为 27 个
- `hooks/intent-gate.py` 新增 `--confidence` / `--margin` / `--subtype` 三个参数，输出新增 `route_slug` / `confidence_grade` / `need_recap` / `force_clarify` 四个机器可读判定位
- `hooks/intent-gate.py` 新增 `ROUTE_SLUGS`（L2 → skill 目录名）与 `SUBTYPE_SLUGS`（子类覆写）映射表，供下游依赖检测直接消费；新增 `INTENT_ALIASES` 支持「代码审查」等中文别名归一化
- 快照模板与意图确认卡新增 `L3_子意图`、`置信度`、`主次分差`、`置信度档位`、`下游 slug` 字段；快照 §二 新增第 7 步「置信度评估」

### 修复

- **[P0] `hooks/intent-gate.py` I21 缺失导致崩溃**：`INTENT_NAMES` / `ROUTE_SUGGESTIONS` 未收录 I21，执行 `--intent I21` 抛 ValueError 并以退出码 2 终止，与 v1.4.0 声明的 I21 路由能力直接冲突
- **[P0] I12 错误路由**：`hooks/intent-gate.py:55` 与 `templates/snapshot.md` 均将 I12 调试修复指向「编码开发 skill」，与 §路由映射表 的 `I12 → tri-fix` 矛盾，会导致调试请求错误交接给 tri-coding
- **[P0] tri-music 路由死链**：tri-music 声称由 tri-intent 直接路由，但路由映射表无其条目；实际通路为 tri-intent → tri-mm → tri-music 二跳委派。现于映射表补充 I15 音乐创作子类说明，并同步修正 tri-music 侧的激活条件表述
- **[P0] `L3_子意图` 幽灵字段**：tri-music 输入契约依赖该字段，但快照模板从不产出，校验条件永远取不到值。现于快照模板与意图确认卡正式定义该字段（取值 workflow | loop | music | 无）
- **[P1] `doing/SKILL.md` 二级判定表漏配**：缺 I21 蒸馏造物与 CR 代码审查两行，L1→L2 下钻时无法命中，对应指南文件 `I21-distill.md` / `code-review.md` 形同孤儿
- **[P1] 模式 A 触发条件逻辑漏洞（18 个下游/横向 skill）**：原条件为「有快照 **或** 有 tri-intent 目录」，后者成立不代表本次请求有快照，会进入无快照可读的未定义分支。现改为「按快照定位契约定位到可用快照」，并统一新增 A0 待识别分支显式定义行为（覆盖 13 个下游执行 skill + tri-god/tri-express + 横向层 cache/translate/true）
- **[P1] 下游 skill 计数陈旧**：§四 双向检测说明称「11 个下游 skill 已实现」，实际为 19 个（15 路由型 + 4 横向型）
- **[P2] 版本号不一致**：SKILL.md frontmatter 为 1.4.0，CHANGELOG 已记录 1.4.1
- **[P2] 快照模板缺 `待确认项` 字段**：意图确认卡有该字段而快照模板无，澄清项无法随快照传递到下游

### 变更

- `tri-god` 输入契约与执行契约由模糊表述「本 skill 认领的蒸馏类意图」改为严格锚定 `L2 = I21`，使机器校验可执行
- §路由映射表 补充横向 skill 说明：tri-cache / tri-evolve / tri-translate / tri-true 为基础设施/方法论型，不参与 L2 意图路由
- §MECE 保证 明确落点总数为 27 个并说明 CR 的编码化处理
- 强制执行契约新增第 5 条「置信度强制」，自检句扩充置信度与 LATEST 指针声明


## [1.4.0] - 2026-07-31

### 新增

- **I21 蒸馏造物意图识别与下游路由（→ tri-god）**：用户要求把人/工作流/专业技能/事物/书籍等对象蒸馏、提炼、萃取、复刻为一个可复用的新 skill 时触发，L2 判定为 I21，`下游路由建议` 指向 tri-god
- **`doing/I21-distill.md`**：I21 蒸馏造物二级意图指南文件，含识别特征、与邻近意图边界（vs I11/I13/I06/I16）、路由规则、路由判定流程、tri-god 激活条件、对称双向检测说明
- 路由步骤新增第 6 步「蒸馏造物路由」（原步骤 6-9 顺延为 7-10）
- 下游依赖检测路由映射表新增 I21 → tri-god 映射

### 变更

- 路由概览表新增 I21（蒸馏造物）行
- 第一层判定表 B.Doing 行下钻范围更新为 `I06–I16 + I21 + 代码审查`
- 路由步骤从 9 步扩展为 10 步（新增蒸馏造物路由步骤）
- 动作泛化降级判定标准更新为「动作能否映射到具体 I06–I16 或 I21」
- MECE 保证第二层范围更新为 `I01–I21 或 M01–M05`
- 目录结构 doing 行追加 `+ I21 蒸馏造物`
- frontmatter version `1.3.1` → `1.4.0`，summary 意图编码覆盖数 25 → 26（I01–I21 + M01–M05），description 二级意图范围扩展含 I21 蒸馏语义

## [1.3.1] - 2026-07-30

### 变更

- **落盘规则标题层级统一**：`### 四、落盘规则` 提升为 `## 落盘规则`（二级标题），与 tri-action/tri-content/tri-plan 等 10 个 skill 保持一致
- **子章节编号顺延**：`### 五、可选轻量复述` 顺延为 `### 四、可选轻量复述`（消除落盘规则移出后的编号断号）

## [1.3.0] - 2026-07-30

### 新增

- **工作流设计子类路由**：I13/I14 任务要点含工作流设计语义（工作流/流水线/审批流/自动化流程/CI-CD/编排/pipeline）时，`下游路由建议` 覆写为 tri-workflow，L2 保持 I13/I14 不变
- **`doing/workflow-design.md`**：工作流设计子类路由指南文件，含识别特征、边界判定、路由规则、判定流程、tri-workflow 激活条件、对称双向检测说明
- 路由步骤新增第 5 步「工作流设计子类路由」（原步骤 5-8 顺延为 6-9）
- 下游依赖检测路由映射表更新：I13/I14 增加工作流设计子类→tri-workflow 的映射
- `doing/SKILL.md`、`doing/I13-planning.md`、`doing/I14-execute.md` 增加工作流设计子类路由指引
- 快照模板 `templates/snapshot.md` 下游路由建议示例更新

### 变更

- 路由步骤从 8 步扩展为 9 步（新增工作流设计子类路由步骤）
- 下游路由映射表 I13/I14 行增加子类路由标注

## [1.2.0] - 2026-07-27

### 新增

- **下游依赖检测机制**：产出快照后 MUST 检测 `下游路由建议` 指向的下游 skill 是否已安装。含路由映射表（L2 意图 → skill slug → skill 目录名）、检测步骤、未安装时的安装提示语。仅对「落盘快照」类意图执行检测，「不落盘」类（Expressing I17–I20、M05）跳过检测
- **对称双向检测**：tri-intent 的下游检测与下游 skill 的上游检测构成对称机制，无论用户先安装哪一端，缺失的另一端都会被检测到并给出安装引导
- 自检句追加下游检测结果声明（已安装/未安装-已提示）

## [1.1.0] - 2026-07-25

### 变更

- **职责边界收敛**：skill 仅负责识别意图 + 产出快照（唯一交付产物）+ 交接下游 skill
- **移除下游产物**：删除 requirements.md、design.md、tasks.md、implements.md、reports.md 模板
- **intent-gate 重新定位**：从「执行前闸门」降级为「可选轻量复述工具」，不编排下游执行链路
- **Flow 三态**：落盘快照 / 不落盘 / 先澄清，互斥穷尽

### 新增

- 快照（`snapshot.md`）作为唯一交付产物模板
- `intent-gate.py` 可运行工具：落盘决策计算 + 路由建议 + 轻量复述渲染
- 103 条全场景测试用例（正常 25 / 消歧 33 / 异常 12 / 边界 10 / 维度 6 / 降级 4 / 产出物 9 / 复述 4）
- README.md、.gitignore、CHANGELOG.md 开源项目文件

### 修复

- frontmatter `name` 字段统一为英文 kebab-case（修正中文 name、去除 `-router` 后缀）
- `intent-gate.py` PEP 8 规范（修正字典缺失空格）
- 测试文件路径引用修正为相对路径

## [1.0.0] - 2026-07-24

### 新增

- 初始版本：L1 四分类 + L2 二十五意图 + D1–D5 正交维度 MECE 分类体系
- clarify-gate 澄清对齐门（G1 苏格拉底式 / G2 批判式反问）
- 路由步骤七步法（提取核心动词 → L1 判定 → L2 下钻 → 多意图消歧 → 边缘兜底 → 澄清前置 → 动作泛化降级）
- 降级规则：动作明确对象缺失不降级 vs 动作泛化无法映射降级
- Expressing 例外：I17–I20 即使 Gate=是也仅在对话内对齐，Flow 仍为不落盘
