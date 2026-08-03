# tri-translate

完美翻译横向 skill。为 tri-xxx 家族提供"意译优先 → 直译次之 → 不译兜底"三策略分层翻译能力。TRANSLATE_EXECUTE 执行深度翻译（含隔离区占位、术语表强制、MQM 质量自检）；TRANSLATE_QUERY 查询术语译法；TRANSLATE_ADMIN 管理术语表/不译规则/风格示例。tri-content I08 委派或用户直接调用激活。

本 skill **不认领任何 L2 意图编码**，是家族的横切关注点（cross-cutting concern），不破坏 21 个下游执行 skill（数量见 family-spec §1.3）的 MECE 划分。核心理念：**翻译不是逐字映射——意译传达意义，直译保信退守，不译保留原貌，质量自检兜底。**

## 特性

- **三策略分层**：意译优先（达旨，传达原文意义而非逐字）→ 直译次之（保信退守，仍须中文通顺）→ 不译兜底（路径/代码/专有名词保留原文）；源自严复信达雅 + 奈达功能对等 + 李长栓理解表达变通 + 玄奘五不翻
- **19 类不译规则集**：路径/代码块/行内代码/命令行/API/URL/域名/邮箱/配置键/环境变量/版本号/SHA/品牌名/商标/首字母缩写/技术标识符/数字单位/日期时间，正则模式预扫描
- **隔离区占位法**：两步占位法（预处理占位 → 翻译 → 还原），杜绝 LLM 破坏代码 markup
- **三层术语表**：Priority A 不可译（品牌名/商标永不本地化）/ Priority B 已批准译法（屏蔽同义词）/ Priority C 推荐译法（可上下文调整）
- **MQM Core 4 维 + Hallucination 子维质量自检**：Accuracy（语义等价性）/ Fluency（中文通顺度）/ Terminology（术语一致性）/ Design（markup 保留度）+ Hallucination（幻觉检测），Critical+Major 错误 0 容忍
- **三个独立调用接口**：TRANSLATE_EXECUTE / TRANSLATE_QUERY / TRANSLATE_ADMIN，可独立运行
- **翻译策略矩阵**：6 场景（技术文档/营销/UI/学术/对话/法律）差异化主策略与退守策略
- **委派关系**：作为 tri-content I08 的可选委派目标，不主动接管，不改动 tri-content
- **独立安装三态依赖检测**：快照模式 / 引导安装 / 降级模式（自构造等价输入声明精度低）

## 目录结构

```
tri-translate/
├── SKILL.md                          主入口：翻译契约 + 三策略 + 19 类不译规则 + MQM 自检
├── README.md                         特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      Keep a Changelog + SemVer
├── LICENSE                           MIT
├── .gitignore
├── schemas/
│   ├── glossary.schema.md            术语表 schema（三层优先级 + 字段定义）
│   └── never-translate.schema.md     不译规则集 schema（19 类 + 正则模式）
└── templates/
    ├── meta.json                     配置模板（默认语言/register/质量门槛/TM）
    ├── glossary.json                 默认术语表（含常见 Priority A 品牌名）
    ├── never-translate.json          默认不译规则集（19 类预置）
    ├── deliverable.md                译文模板
    ├── alignment.md                  原文对照表模板
    ├── quality.md                    MQM 质量报告模板
    └── style-examples/               风格示例（Few-shot）
        ├── technical-doc.md          技术文档风格示例
        └── marketing.md              营销文案风格示例
```

运行时落盘结构（`.tribro/translate/`）：

```
.tribro/translate/
└── <命名>/
    ├── deliverable.md                译文
    ├── preserved.md                  不译清单
    ├── alignment.md                  原文-译文对照
    └── quality.md                    MQM 质量报告
```

## 安装

将 `tri-translate/` 目录放入你的 skills 目录即可：

```bash
cp -r tri-translate/ /path/to/your/skills/
```

本 skill 可独立安装。激活时检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| A · 快照模式 | `.tribro/snapshots/` 有快照 或 skills 目录有 `tri-intent/` | 读取快照 §三 提取上下文（D1 任务领域 / D4 输出期望），增强翻译语境感知 |
| B · 引导安装 | 以上均不满足 | 向用户提示依赖并引导安装 `skillhub install tri-intent` |
| C · 降级模式 | 用户拒绝安装 | 从用户请求自构造等价输入，声明降级精度低 |

> 三态逻辑：本 skill 为方法论型高频 skill，支持降级——降级模式仍可执行翻译，但上下文语境感知精度低（任务领域=未指定，目标读者=未指定）。

## 使用

### 三种工作模式

| 模式 | 触发源 | 输入 | 输出 |
|------|--------|------|------|
| TRANSLATE_EXECUTE（深度翻译） | tri-content I08 委派 / 用户直接调用 | 原文 + 目标语言 + 上下文 | 译文 + 不译清单 + 原文对照 + 质量报告 |
| TRANSLATE_QUERY（术语查询） | 其它 skill 查询术语 | 术语 + 上下文 | 译法 + 优先级 + 来源 |
| TRANSLATE_ADMIN（管理） | 用户管理命令 | 管理命令 | 操作结果 |

### TRANSLATE_EXECUTE 流程

```
接收 {原文 + 目标语言 + 上下文}
        │
        ▼
  声明自检句 + 上下文收集（快照§三若可用 + 调用方入参 + 内置资源）
        │
        ▼
  隔离区提取（19 类不译规则扫描 → 占位符替换）
        │
        ▼
  策略① 意译优先（据上下文 + 风格示例）
        │
        ├─ 触发退守 ──→ 策略② 直译次之（术语表强制）
        │                  │
        │                  ├─ 触发退守 ──→ 策略③ 不译兜底（占位符保留）
        │                  │
        ▼                  ▼
  质量自检（MQM Core 4 维 + Hallucination）
        │
        ├─ Critical+Major 错误 ──→ 重译（最多 2 次）或退守直译
        │
        ▼
  占位符还原（验证残留 = 0）
        │
        ▼
  产物组装（译文 + 不译清单 + 原文对照 + 质量报告）
```

### 三策略分层表

| 策略 | 触发场景 | 执行方式 | 退守条件 |
|------|----------|----------|----------|
| ① 意译优先 | 一般文本、解释性段落、营销文案、对话 | 据上下文意译，传达原文意义 | 术语密集 / 命令上下文 / 法律精确性 / 数字版本号 |
| ② 直译次之 | 术语密集、技术文档、法律条款、命令式语句 | 按字面直译但符合中文表达习惯 | 路径/代码/URL/品牌名/首字母缩写 |
| ③ 不译兜底 | 路径、代码块、命令、API、URL、品牌名、商标、首字母缩写 | 占位符保留原文，译后还原 | — |

### 管理命令

```bash
tri-translate execute --source "<file|text>" --target zh-CN [options]  # 执行翻译
tri-translate query --term "<term>"                                      # 查询术语
tri-translate glossary add --source "X" --target "Y" --priority C       # 添加术语
tri-translate glossary list [--priority A|B|C]                           # 列出术语
tri-translate glossary remove --source "X"                                # 删除术语
tri-translate never-translate add --pattern "..." --placeholder "..."      # 添加不译规则
tri-translate stats                                                       # 翻译统计
tri-translate test --suite mqm                                            # 质量评估测试
tri-translate export --out <path>                                         # 导出术语表+规则
```

### 落盘规则

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- 本 skill 链路文档落盘于 `.tribro/translate/<命名>/`（含 deliverable.md / preserved.md / alignment.md / quality.md）
- 译文最终成果物落盘至用户工作区（由调用方或用户指定路径）
- TRANSLATE_QUERY 返回为即时对话回应，不落盘
- 降级模式仍落盘链路文档，但 quality.md 标注"降级模式，精度低"

## 测试

完整测试用例见 `tests/tri-translate-full-testcases.md`，覆盖元数据、强制执行契约、输入契约、完美翻译（三策略/19 类不译规则/三层术语表/MQM 自检/可扩展性）、自检声明验证、交付产物、职责边界、质量标准、独立性等全部能力点。

## 设计原则

- **横向方法论**：不认领 L2 意图编码，不破坏家族 MECE 划分，是横切关注点
- **三策略分层**：意译优先传达意义，直译保信退守，不译保留原貌，源自古今翻译理论融通
- **隔离区占位法**：不译要素先抽出为占位符，翻译过程不触碰，译后还原，杜绝格式破坏
- **术语表强制**：三层优先级，Priority A 永不本地化，Priority B 屏蔽同义词，全文一致性
- **MQM 质量自检**：4 维 + Hallucination 子维，Critical+Major 0 容忍，未达标重译或退守
- **可独立运行**：三态依赖检测，无 tri-intent 时降级为自构造等价输入仍可工作
- **委派不接管**：作为 tri-content I08 可选委派目标，不主动接管，不改动 tri-content
