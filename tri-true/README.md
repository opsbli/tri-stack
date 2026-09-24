# tri-true

消除幻觉方法论横向 skill。为 tri-xxx 家族提供"置信度评估 + 事实源验证 + 多模型多方事实源交叉验证 + 自我反思修正"四道防线的幻觉消除能力。VERIFY_EXECUTE 执行深度验证（含段级置信度评估、RAG 句级引用、T1-T4 信源分级、UAF 多模型加权融合、CoVe/Reflexion 闭环修正、人审兜底）；VERIFY_QUERY 查询历史验证；VERIFY_ADMIN 管理信源/校准/模型池。下游 skill 委派或用户直接调用激活。

本 skill **不认领任何 L2 意图编码**，是家族的横切关注点（cross-cutting concern），不破坏 21 个下游执行 skill（数量见 family-spec §1.3）的 MECE 划分。核心理念：**幻觉不可根除，但可层层拦截——置信度筛低信、事实源锚真、多模型仲裁纠错、自反思闭环修复。**

## 特性

- **四道防线**：① 置信度评估（VC+SC+CC 三层）→ ② 事实源验证（RAG + T1-T4 分级）→ ③ 多模型交叉验证（异构并行 + UAF 融合）→ ④ 自我反思修正（CoVe/Reflexion/Critique-Refine），层层拦截
- **三层置信度评估**：Verbalized Confidence（直接自评）+ Self-Consistency（N 次采样一致度）+ Calibrated Confidence（基于 ECE 反推校准系数 k 修正过度自信）
- **四级信源分级**：T1 权威事实类（1.0）/ T2 权威观点类（0.8）/ T3 一般参考类（0.5）/ T4 待验证类（0.2），可信度加权 `Final = α×Relevance + β×Credibility + γ×Freshness`
- **异构多模型交叉验证**：≥2 家供应商 + ≥1 开源 + 不同架构家族，UAF 加权融合 `final = argmax(Σ weight_i × confidence_i × agreement_i)`，强/弱共识阈值 + 冲突解决策略
- **闭环自我反思修正**：CoVe（主张→查询→证据→修订）→ Reflexion（thought/answer/confidence 反思）→ Critique-Refine（核查员-修订员迭代），最多 3 轮
- **人审兜底**：critical 风险 + 置信度 < 0.8 强制人审，高风险操作（删除/发布/资金）双人审；综合置信 < 0.5 且无 T1/T2 拒答或列多答案
- **幻觉类型分流**：Factuality（事实性，走防线二）/ Faithfulness（自洽性，走自洽性检测），NEVER 混淆处理
- **三个独立调用接口**：VERIFY_EXECUTE / VERIFY_QUERY / VERIFY_ADMIN，可独立运行
- **隐私过滤与成本控制**：第三方模型调用前扫描密钥脱敏，敏感度过高不外传；单任务多模型调用上限 5 次，超限降级
- **委派关系**：作为 tri-coding 等下游执行 skill 的可选委派目标，不主动接管（原 tri-ask / tri-content 本分支未包含）
- **独立安装三态依赖检测**：快照模式 / 引导安装 / 降级模式（自构造等价输入声明精度低）

## 目录结构

```
tri-true/
├── SKILL.md                          主入口：消除幻觉契约 + 四道防线 + 三层置信度 + 四级信源 + 异构多模型
├── README.md                         特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                      Keep a Changelog + SemVer
├── LICENSE                           MIT
├── .gitignore
├── schemas/
│   ├── verify-task.schema.md         验证任务数据模型（5 表结构）
│   ├── source.schema.md              信源 schema（T1-T4 + 可信度）
│   └── model.schema.md               模型池 schema（异构要求 + UAF 权重）
└── templates/
    ├── meta.json                     配置模板（阈值/权重/模型池/信源/隐私）
    ├── sources.json                  默认信源库（含 T1-T4 常见信源）
    ├── calibration.json              默认校准表（各模型 ECE/Brier/k）
    ├── models.json                   默认模型池（异构组合）
    ├── verify.md                     验证报告模板
    ├── sources.md                    引用清单模板
    ├── alignment.md                  段落对照模板
    ├── confidence.md                 置信度明细模板
    ├── revisions.md                  修订记录模板
    └── quality.md                    质量报告模板
```

运行时落盘结构（`.tribro/true/`）：

```
.tribro/true/
├── verify-index.db                   SQLite 主索引（WAL）
├── verify-index.jsonl                JSONL 增量日志（容灾）
├── meta.json                          配置
└── <命名>/
    ├── verify.md                      验证报告
    ├── sources.md                     引用清单
    ├── alignment.md                   段落对照
    ├── confidence.md                  置信度明细
    ├── revisions.md                   修订记录
    └── quality.md                     质量报告
```

## 安装

将 `tri-true/` 目录放入你的 skills 目录即可：

```bash
cp -r tri-true/ /path/to/your/skills/
```

本 skill 可独立安装。激活时检测上游 tri-intent skill 是否可用，据检测结果选择执行模式：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| A · 快照模式 | `.tribro/snapshots/` 有快照 或 skills 目录有 `tri-intent/` | 读取快照 §三 提取上下文（D1 任务领域 / D5 确定性），增强风险等级判定与领域适配 |
| B · 引导安装 | 以上均不满足 | 向用户提示依赖并引导安装 `skillhub install tri-intent` |
| C · 降级模式 | 用户拒绝安装 | 从用户请求自构造等价输入，声明降级精度低 |

> 三态逻辑：本 skill 为方法论型 skill，支持降级——降级模式仍可执行验证，但上下文感知精度低（风险等级=medium，domain=general）。

## 使用

### 三种工作模式

| 模式 | 触发源 | 输入 | 输出 |
|------|--------|------|------|
| VERIFY_EXECUTE（深度验证） | 下游 skill 委派 / 用户直接调用 / 高风险 hook | 待验证内容 + 风险等级 + 上下文 | 验证报告 + 引用清单 + 置信度 + 修订记录 + 质量报告 |
| VERIFY_QUERY（历史查询） | skill 或用户查询 | claim 或 task_id | 历史验证状态 + 置信度 + 信源 + 模型 |
| VERIFY_ADMIN（管理） | 用户管理命令 | 管理命令 | 操作结果 |

### VERIFY_EXECUTE 流程

```
接收 {待验证内容 + 风险等级 + 上下文}
        │
        ▼
  声明自检句 + 上下文收集（快照§三若可用 + 调用方入参 + 内置资源）
        │
        ▼
  段落切分 + Factuality/Faithfulness 类型分流
        │
        ▼
  防线一：置信度评估（VC + SC + CC 三层）
        │
        ├─ 高置信 ──→ 标记 verified（附置信度）
        │
        ▼ 中/低置信
  防线二：事实源验证（RAG + T1-T4 + 句级引用 + 可信度加权）
        │
        ├─ T1/T2 支撑 ──→ verified（附引用）
        │
        ▼ T3/T4 或无源
  防线三：多模型交叉验证（异构并行 + UAF + 共识阈值）
        │
        ├─ 强/弱共识 ──→ verified（标注 N 模型）
        │
        ▼ 分歧
  防线四：自我反思修正（CoVe → Reflexion → Critique-Refine，最多 3 轮）
        │
        ├─ 修订后置信 ≥ 阈值 ──→ verified（标注修订次数）
        │
        ▼ 仍不达标
  兜底：拒答 / 多答案 / 人审
```

### 四级信源分级表

| Tier | 类型 | 可信度权重 | 示例 |
|------|------|-----------|------|
| T1 | 权威事实类 | 1.0 | 法律法规、政府公报、官方 API 文档、ISO 标准 |
| T2 | 权威观点类 | 0.8 | 研究机构报告、同行评议论文、内部审核方案 |
| T3 | 一般参考类 | 0.5 | 媒体报道、行业文章、技术博客 |
| T4 | 待验证类 | 0.2 | 论坛、营销内容、匿名内容 |

### 管理命令

```bash
tri-true execute --source "<file|text>" [--risk high] [--domain medical]  # 执行验证
tri-true query --claim "<claim>"                                          # 查询历史验证
tri-true query --task-id <id>                                             # 按 ID 查询
tri-true sources add --url "..." --tier T2 --domain medical               # 添加信源
tri-true sources list [--tier T1|T2|T3|T4] [--domain medical]             # 列出信源
tri-true sources remove --url "..."                                       # 删除信源
tri-true calibrate --model "<name>"                                       # 重算 ECE/Brier/k
tri-true models add --name "<name>" --family GPT --is-open-source false   # 添加模型
tri-true models list                                                      # 列出模型池
tri-true stats                                                            # 验证统计
tri-true test --suite truthqa                                             # 跑 TruthfulQA 评估
tri-true export --out <path>                                              # 导出验证任务
```

### 落盘规则

- 快照由 tri-intent 已落盘于 `.tribro/snapshots/`
- 本 skill 链路文档落盘于 `.tribro/true/<命名>/`（含 verify.md / sources.md / alignment.md / confidence.md / revisions.md / quality.md）
- 验证索引落盘于 `.tribro/true/verify-index.db` + `verify-index.jsonl`（双轨容灾）
- 验证最终结论由调用方决定是否落至用户工作区
- VERIFY_QUERY 返回为即时对话回应，不落盘
- 降级模式仍落盘链路文档，但 quality.md 标注"降级模式，精度低"

## 测试

完整测试用例见 `tests/tri-true-full-testcases.md`，覆盖元数据、强制执行契约、输入契约、四道防线（置信度/事实源/多模型/自反思）、幻觉类型分流、人审兜底、自检声明验证、交付产物、职责边界、质量标准、独立性等全部能力点。

## 设计原则

- **横向方法论**：不认领 L2 意图编码，不破坏家族 MECE 划分，是横切关注点
- **四道防线**：置信度筛低信 → 事实源锚真 → 多模型仲裁 → 自反思修复，层层拦截
- **三层置信度**：VC 黑盒基础 + SC 随机误差过滤 + CC 过度自信修正，基于 ECE 校准
- **四级信源分级**：T1-T4 可信度加权，句级引用归因（ReClaim 模式），高 tier 支撑方可 verified
- **异构多模型仲裁**：≥2 家供应商 + ≥1 开源 + 不同架构家族，UAF 加权融合 + 共识阈值
- **闭环自我反思**：CoVe → Reflexion → Critique-Refine，最多 3 轮修订，修订后置信达标方可交付
- **人审兜底**：critical 风险强制人审，高风险操作双人审，拒答"我不懂"的工程化映射
- **可独立运行**：三态依赖检测，无 tri-intent 时降级为单模型 + 自反思仍可工作
- **委派不接管**：作为下游 skill 可选委派目标，不主动接管，不改动调用方
