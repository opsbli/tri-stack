# tri-evolve

自进化学习横向型 skill。为 tri-xxx 家族全家族提供多渠道信号驱动的持续改进与用户画像构建能力。通过 OODA 闭环（观察-归因-提议-验证-沉淀）提升 skill 命中率与回答质量；构建演进式用户画像（静态/动态分层+时间衰减）使回答风格贴合用户偏好。

本 skill **不认领任何 L2 意图编码**，是家族的横切关注点（学习层），不破坏 14 个下游执行 skill 的 MECE 划分。核心理念：**进化不是瞎改——学要有据，改要有验，错要能回滚，隐私要护住。**

## 特性

- **OODA 进化闭环**：观察（六渠道信号采集）→ 归因（模式识别）→ 提议（带置信度）→ 验证（A/B 小流量）→ 沉淀（verified 入库），五阶段闭环
- **六渠道信号源**：用户显式反馈 / 隐式行为 / 缓存命中统计（原 tri-cache，本分支未包含）/ tri-meta 纠偏记录 / 快照分布 / 会话轨迹
- **经验条目库**：Voyager 式可检索复用（非 append-only 日志），每条经验带 embedding 索引，相似场景语义检索复用
- **用户画像四层**：静态属性 / 风格偏好 / 主题偏好 / 交互习惯；静态稳定、动态时间衰减（半衰期 30 天）；追踪偏好演变历史（应对 PERSONAMEM 揭示的动态演进问题）
- **外部信号锚定**：改进提议 MUST 锚定外部信号（generator-verifier gap 防护），纯自我批判 NEVER 沉淀
- **A/B 验证门**：提议经小流量对照验证（lift ≥5% 且 p<0.05 且样本 ≥30）才沉淀为 verified 经验
- **安全分级与回滚**：低/中/高三风险级（自动应用 / A/B 验证 / 人工审批）；每次沉淀带版本可回滚
- **画像隐私保护**：敏感属性（health/political/religious/sexual）NEVER 推断；支持导出/删除/脱敏（GDPR 式权利）
- **独立安装三态依赖检测**：完整模式 / 引导安装 / 降级模式（退化为会话内反馈学习）

## 目录结构

```
tri-evolve/
├── SKILL.md                          主入口：进化契约 + OODA 闭环 + 画像分层 + 验证门
├── README.md                         特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      Keep a Changelog + SemVer
├── LICENSE                           MIT
├── .gitignore
├── schemas/
│   └── evolve-schema.md             进化数据 schema（lessons/profile/proposals/baseline 表）
└── templates/
    └── meta.json                     配置模板（A/B 阈值/衰减/风险分级/敏感属性）
```

运行时落盘结构（`.tribro/evolve/`）：

```
.tribro/evolve/
├── signals.jsonl                     信号事件流（追加写）
├── lessons.db                        经验条目库（SQLite + embedding）
├── profile.db                        用户画像（静态/动态/演变历史）
├── proposals.db                      调优建议（pending/validating/verified/applied）
├── baseline.db                       质量基线时序
└── meta.json                         进化元信息（统计 + 配置）
```

## 安装

将 `tri-evolve/` 目录放入你的 skills 目录即可：

```bash
cp -r tri-evolve/ /path/to/your/skills/
```

本 skill 可独立安装。激活时检测上游 tri-intent 是否可用，据检测结果选择执行模式（原 tri-cache 缓存层本分支未包含）：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| A · 完整模式 | 检测到 `tri-intent/` 且 `.tribro/snapshots/` 有快照 | 六渠道信号全采集（缓存命中渠道来源原 tri-cache 本分支未包含）；画像持久化；经验库 embedding 检索 |
| B · 引导安装 | 未检测到 tri-intent | 向用户提示依赖并引导安装 `python ops/install-skills.py --target <目标目录>` |
| C · 降级模式 | 用户拒绝安装 | 退化为仅会话内反馈学习（无跨会话沉淀、无画像持久化、无经验复用），声明降级精度低 |

> 三态逻辑：本 skill 为学习型，支持降级——降级模式仍可采集会话内反馈学习，但精度低。

## 使用

### 三种工作模式

| 模式 | 触发源 | 输入 | 输出 |
|------|--------|------|------|
| EVOLVE_OBSERVE（被动观察） | 作答后 evolve-hook 触发 | 作答事件 + 用户行为 | 信号采集 + 归因 |
| EVOLVE_LEARN（主动学习） | 定时/批量触发 | 聚合信号 + 历史经验 | 经验条目 + 调优建议（待验证） |
| EVOLVE_APPLY（主动应用） | 下游 skill 请求画像/经验 | user_id + 场景 | 用户画像 + 经验复用 + 配置覆盖 |

### OODA 进化闭环

```
观察(Observe) → 归因(Attribute) → 提议(Propose) → 验证(Prove) → 沉淀(Persist)
   六渠道信号      模式识别          带置信度         A/B 小流量     验证通过
   采集聚合        归因到            改进建议         对照验证       入经验库/画像
                  skill/意图                        lift≥阈值
```

### 六渠道信号源

| 渠道 | 信号 | 来源 |
|------|------|------|
| ① 显式反馈 | 赞 / 踩 / 评分 / 纠偏文本 | 用户主动输入 |
| ② 隐式行为 | 采纳 / 修改 / 重试 / 中断 / 复制 | 作答后用户行为 |
| ③ 缓存命中 | 命中率 / 未命中模式 / stale 比例 | 原 tri-cache `cache_meta`（本分支未包含） |
| ④ 纠偏记录 | M02 纠偏事件 | tri-meta |
| ⑤ 快照分布 | 意图识别分布 / 澄清门触发率 | `.tribro/snapshots/` |
| ⑥ 会话轨迹 | 多轮交互偏好线索 | 会话历史 |

### 用户画像四层

| 层 | 内容 | 稳定性 | 更新方式 |
|----|------|--------|----------|
| 静态属性 | 年龄 / 职业 / 地域 / 技术栈 | 稳定 | 显式提供优先，保守推断 |
| 风格偏好 | 语气 / 长度 / 格式 | 中稳定 | 时间衰减加权（半衰期 30 天） |
| 主题偏好 | 擅长领域 / 兴趣主题 / 术语 | 动态 | 时间衰减 + 频次 |
| 交互习惯 | 提问风格 / 意图分布 / 活跃时段 | 动态 | 滑动窗口统计 |

### 安全分级

| 风险级 | 变更类型 | 审批方式 |
|--------|----------|----------|
| 低 | 画像动态偏好更新 | 自动应用，带版本 |
| 中 | 经验沉淀 / 配置覆盖 | A/B 验证门（lift≥5%, p<0.05, sample≥30） |
| 高 | skill 核心契约修改 | MUST 人工审批 |

### 管理命令

```bash
tri-evolve stats                      # 进化统计（信号数/经验数/验证通过率）
tri-evolve learn --batch              # 触发批量学习
tri-evolve profile --user <id>        # 查看用户画像
tri-evolve profile --export <id>     # 导出画像（隐私权利）
tri-evolve profile --delete <id>     # 删除画像
tri-evolve rollback --lesson <id>     # 回滚经验条目
tri-evolve restore --version <v>     # 恢复画像版本
tri-evolve reuse --scene <desc>      # 检索复用经验
tri-evolve ab-status                 # 查看 A/B 实验状态
```

### 落盘规则

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- 本 skill 进化产物落盘于 `.tribro/evolve/`（可覆盖更新）
- 信号事件流落盘于 `.tribro/evolve/signals.jsonl`（追加写）
- 画像/经验返回为即时对话回应，不落盘
- 降级模式（模式 C）仅会话内学习，不跨会话落盘

## 测试

完整测试用例见 `tests/tri-evolve-full-testcases.md`，覆盖元数据、强制执行契约、输入契约、自进化方法论、自检声明、交付产物、职责边界、质量标准等全部能力点。

## 设计原则

- **横向学习层**：不认领 L2 意图编码，不破坏家族 MECE 划分，是横切关注点
- **学要有据**：改进提议锚定外部信号，纯自我批判禁沉淀（generator-verifier gap 防护）
- **改要有验**：A/B 验证门强制，lift≥5% 且显著才沉淀
- **错要能回滚**：每次沉淀带版本，错误学习可回滚
- **隐私要护住**：敏感属性 NEVER 推断，画像支持导出/删除
- **可独立运行**：三态依赖检测，无 tri-intent 时降级为会话内学习仍可工作（缓存层原 tri-cache 本分支未包含）
