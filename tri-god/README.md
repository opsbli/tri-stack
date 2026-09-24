# tri-god

蒸馏元 skill（造物主·蒸馏元技能）。作为路由分发器识别蒸馏对象类型（human / workflow / skill / thing / general），从 `methodologies/registry.md` 加载对应方法论，把「一个人的思维方式、一套工作流、一门专业技能、一本书/一门课等长内容」蒸馏提炼为可被 Agent 独立调用的 skill。它是 tri-intent 的下游执行 skill，当 tri-intent 快照下游路由建议指向本 skill 时激活；支持独立安装，含上游依赖检测三态逻辑。

![version](https://img.shields.io/badge/version-1.2.2-blue) ![license](https://img.shields.io/badge/license-MIT-green)

## 特性

- **蒸馏元 skill**：产物是「一个新 skill」而非普通答复或业务代码，把值得复用的存在封装为可独立调用的能力
- **五类对象方法论路由**：按对象类型（human / workflow / skill / thing / general）路由到差异化方法论，NEVER 用统一模板套用
- **registry 驱动可扩展**：`methodologies/registry.md` 为唯一注册入口，新增蒸馏类型零改动主 SKILL.md，只需追加一行 + 新增一个 `distill-<type>.md`
- **双审批门 + 执行前确认**：门①需求 → 门②设计 → 门③执行前确认 → 执行 → 报告，任一门未过携反馈回炉，禁跳门抢跑
- **三态上游依赖检测**：独立使用时检测上游 tri-intent，据结果选择模式 A 快照 / B 引导安装 / C 降级
- **tri-intent 下游集成**：读取快照 §三 结构化结论直接执行，不重新识别意图（由 tri-intent 负责）
- **脱敏边界与结论置信标注**：敏感素材先声明脱敏范围经确认再蒸馏，结论性表达必附置信度 + 依据类型 + 可验证来源
- **完成判据外化 + 进化契约**：结束态六项可机械校验判据，停车/结束显式区分；`.tribro/god/lessons.md` 教训读写闭环支撑自进化

## 能力定义（五能力）

| # | 能力 | 输入 | 输出 |
|---|------|------|------|
| C1 | 对象类型识别 | 快照 §三 + 来源素材 | 对象类型判定（五类 MECE） |
| C2 | 方法论路由加载 | 对象类型 | 已加载的 `distill-<type>.md` |
| C3 | 蒸馏执行 | 来源素材 + 方法论阶段 | 各阶段蒸馏产物 |
| C4 | 产物封装 | 蒸馏成果 | 可独立调用的 skill |
| C5 | 脱敏与合规 | 素材敏感度评估 | 脱敏后的产物 + 引用合规记录 |

## 目录结构

```
tri-god/
├── SKILL.md                          主入口：蒸馏元 skill 路由框架 + 双审批门流程
├── methodologies/
│   ├── registry.md                   方法论注册表（唯一注册入口）
│   ├── distill-human.md              蒸馏人类方法论
│   ├── distill-workflow.md           蒸馏工作流方法论
│   ├── distill-skill.md              蒸馏专业技能方法论
│   ├── distill-thing.md              蒸馏事物（长内容）方法论
│   └── distill-general.md            通用兜底方法论
├── scripts/
│   └── check_update.py               版本检查门可执行实现（第零步）
├── README.md                         本文件
├── CHANGELOG.md                      版本变更记录
├── _meta.json                        安装元数据（slug + version）
└── tests/
    └── tri-god-full-testcases.md     全场景测试用例
```

## 安装

将 `tri-god/` 目录放入你的 skills 目录，或通过 skillhub 安装：

```bash
python ops/install-skills.py --target <目标目录>
```

本 skill 可独立安装，但依赖上游 tri-intent 产出的快照以获得完整效果。激活时检测上游 tri-intent 是否可用，据检测结果选择执行模式；未安装时建议先安装依赖：

```bash
python ops/install-skills.py --target <目标目录>
```

## 使用

### 使用场景（通用示例）

| 场景 | 对象类型 |
|------|----------|
| 把某领域专家的决策方式沉淀为决策辅助 skill | human |
| 把一套已验证的协作流程沉淀为可执行 workflow skill | workflow |
| 把一门手艺的专家经验显性化为技能 skill | skill |
| 把一本书/一门课的知识框架蒸馏为知识 skill | thing |
| 跨类型混合或无法归类的对象 | general |

### 调用方式（三通道）

| 通道 | 条件 | 行为 |
|------|------|------|
| ① 快照路由（标准） | tri-intent 产出快照且下游路由建议指向本 skill | 读取快照 §三，标准链路执行 |
| ② 独立显式调用 | 用户直接指名调用（触发词命中） | 先走上游依赖检测（三态），再按对应模式执行 |
| ③ 降级调用 | 用户拒绝安装上游 | 自构造等价输入 + 降级声明 |

### 核心流程

收到 tri-intent 快照且 `下游路由建议` 指向本 skill 后，按以下链路推进：

```
读取快照 §三 + 确认来源素材（含脱敏范围声明）
        │
        ▼
识别蒸馏对象类型（human / workflow / skill / thing / general）
        │
        ▼
查 methodologies/registry.md → 加载对应 distill-<type>.md
        │
        ▼
门① 需求审批 requirements.md
        │
        ▼
门② 设计审批 design.md（写明已识别对象类型 + 加载方法论 + 各阶段规划）
        │
        ▼
门③ 执行前确认 tasks.md
        │
        ▼
执行蒸馏（最小化原则，按方法论阶段推进）
        │
        ▼
验收报告 implements.md + 蒸馏产出 skill
```

### 五类对象方法论映射表

| 对象类型 | type_id | 识别特征 | 方法论文件 |
|---|---|---|---|
| 人类 | human | 蒸馏某个人的思维/表达/决策方式；对象是人物、专家、作者；素材含著作/访谈/演讲/社媒 | `methodologies/distill-human.md` |
| 工作流 | workflow | 蒸馏一套可复用流程/步骤序列/协作机制/SOP；素材含流程实例/记录 | `methodologies/distill-workflow.md` |
| 专业技能 | skill | 蒸馏一门可操作的专业技能/手艺/方法；素材含教程/操作文档/示范 | `methodologies/distill-skill.md` |
| 事物 | thing | 蒸馏书/视频/课程/文档等长内容中的知识框架；素材是可通读的长文本/内容 | `methodologies/distill-thing.md` |
| 其它/不确定 | general | 无法归入上述类型，或跨类型混合 | `methodologies/distill-general.md` |

### 落盘规则

- 快照已由 tri-intent 落盘于 `.tribro/snapshots/`
- 本 skill 链路文档落盘于 `.tribro/god/<命名>/`（requirements / design / tasks / implements，可覆盖更新）
- 经验教训文件：`.tribro/god/lessons.md`（跨会话累积，追加写，见 SKILL.md §进化契约）
- 最终蒸馏产出的 skill 落盘至 `.tribro/skills/<slug>/`

## 测试

完整测试用例见 `tests/tri-god-full-testcases.md`，覆盖五类对象方法论路由、registry 驱动加载、双审批门 + 执行前确认流程、来源素材真实性校验、敏感信息脱敏、结论置信标注、三态上游依赖检测、输出契约、完成判据与进化契约等全部能力点。

## 设计原则

- **路由器思维**：主 SKILL.md 只负责识别对象类型与分发，具体方法论下沉到 `methodologies/`，主入口保持精简
- **渐进式披露**：仅在识别对象类型后按需加载单个方法论文件，不预载全部方法论，控制上下文体积
- **registry 驱动可扩展**：新增蒸馏类型零改动主 SKILL.md，通过 `registry.md` 注册表 + 独立方法论文件扩展
- **MECE 对象分类**：五类对象类型互斥且以 general 兜底穷尽，每次蒸馏只加载一个方法论，禁叠加
- **可独立可集成**：既能独立安装运行（三态依赖检测），也能作为 tri-intent 的下游执行 skill 无缝集成
- **脱敏安全复用**：蒸馏素材与产物全程执行脱敏边界，确保内容可在通用场景安全复用
