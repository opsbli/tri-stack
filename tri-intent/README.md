# tri-intent

用户提问意图识别总路由。任何用户新提问在正式作答/执行前都先经此 skill 处理——完成第一层三分法（Asking / Doing / Expressing / Meta）判定，下钻二级意图（I01–I21 / CR / M01–M05），标注正交维度（D1–D5），产出快照（`snapshot.md`）作为唯一交付产物，交接下游 skill 精准执行。

遵循 **MECE 原则**（相互独立、完全穷尽），确保任一提问有且仅有一个落点。本 skill **仅负责识别和结构化输出**用户真实意图，不产出需求文档、设计文档、任务清单、实现报告或最终回答——那些由下游 skill 依据快照自行产出。

## 特性

- **三层 MECE 分类体系**：L1 四大类 × L2 二十七落点（I01–I21 + CR + M01–M05）× D1–D5 正交维度，100% 覆盖零空白
- **唯一交付产物**：快照（`snapshot.md`），内含原始提问、分析过程、结构化结论，供下游 skill 直接读取执行
- **可选轻量复述**：识别完成后可至多一次复述供用户发现误识别，不设审批门
- **澄清对齐门**：需求模糊/矛盾时 AI 主动反问（G1 苏格拉底式 / G2 批判式）
- **可运行工具**：`intent-gate.py` 提供落盘决策计算与路由建议，支持 JSON 输出
- **103 条全场景测试**：覆盖正常命中、邻近消歧、异常兜底、边界跨界、维度标注、降级规则等全部能力点
- **下游依赖检测**：产出快照后检测下游 skill 是否已安装，未安装时提示用户安装命令（与下游 skill 的上游检测构成对称双向检测）

## 目录结构

```
tri-intent/
├── SKILL.md              主 skill 定义与执行契约
├── asking/               I01–I05 信息查询/概念解释/建议咨询/决策辅助/推理计算
│   ├── SKILL.md
│   └── I01-info-query.md ... I05-reasoning.md
├── doing/                I06–I16 生成/改写/翻译/总结/分析/编码/调试/规划/执行/多媒体/头脑风暴 + I21 蒸馏造物 + CR 代码审查
│   ├── SKILL.md
│   ├── I06-content-gen.md ... I16-brainstorm.md
│   ├── I21-distill.md    蒸馏造物
│   ├── code-review.md    代码审查特殊路由（CR）
│   ├── workflow-design.md 工作流设计子类路由（→ tri-workflow）
│   ├── loop-design.md    loop/domain 创建子类路由（→ tri-loop）
│   └── sdlc-design.md    全生命周期子类路由（→ tri-sdlc）
├── expressing/           I17–I20 角色扮演/情感陪伴/闲聊娱乐/观点表达
│   ├── SKILL.md
│   └── I17-roleplay.md ... I20-opinion.md
├── meta/                 M01–M05 澄清追问/纠错反馈/追加细化/能力询问/中止确认
│   ├── SKILL.md
│   └── M01-clarify-followup.md ... M05-abort-confirm.md
├── clarify-gate/         澄清对齐门（G1 苏格拉底式 / G2 批判式反问）
│   └── SKILL.md
├── hooks/                可运行工具
│   ├── intent-gate.py    意图识别结果呈现器（落盘决策 + 路由建议 + 轻量复述）
│   └── intent-gate.md    工具文档
├── templates/            模板
│   └── snapshot.md       快照模板（唯一交付产物）
└── tests/                测试
    ├── tri-intent-full-testcases.md   103 条全场景测试用例
    └── tri-intent-full-testreport.md  测试执行报告
```

## 意图分类体系

### L1 第一层（四选一，互斥穷尽）

| 大类 | 判定信号 | 用户心智 | 下钻 |
| --- | --- | --- | --- |
| A. Asking 咨询求解 | 问「是什么/为什么/怎么办/哪个好」 | 把 AI 当顾问/信息源 | `asking/` (I01–I05) |
| B. Doing 委托执行 | 说「帮我写/做/改/算/查代码」 | 把 AI 当执行者 | `doing/` (I06–I16 + I21 + CR) |
| C. Expressing 表达陪伴 | 倾诉、闲聊、扮演、表态 | 把 AI 当倾听者/伙伴 | `expressing/` (I17–I20) |
| Meta 元操作 | 针对「上一轮回复」或「AI 本身」发问 | 关于对话本身 | `meta/` (M01–M05) |

### L2 第二层（27 个落点）

- **I01–I05**：信息查询 / 概念解释 / 建议咨询 / 决策辅助 / 推理计算
- **I06–I16**：内容生成 / 内容改写 / 翻译转换 / 总结提炼 / 分析处理 / 编码开发 / 调试修复 / 规划拆解 / 操作执行 / 多媒体生成 / 头脑风暴
- **I17–I20**：角色扮演 / 情感陪伴 / 闲聊娱乐 / 观点表达
- **I21**：蒸馏造物
- **CR**：代码审查（无数字编码的特殊路由项）
- **M01–M05**：澄清追问 / 纠错反馈 / 追加细化 / 能力询问 / 中止确认

### L3 子类路由（不改 L2，仅覆写下游 slug）

| L3 子意图 | 触发 L2 | 下游 slug | 说明 |
|---|---|---|---|
| `sdlc` | I11 / I13 / I14 | `tri-sdlc` | 全生命周期九阶段编排（优先级高于 workflow / loop） |
| `workflow` | I13 / I14 | `tri-workflow` | 产出流程定义产物（DAG / CI 配置 / 审批模板） |
| `loop` | I14 | `tri-loop` | 知识库 loop/domain 创建 |
| `music` | I15 | `tri-mm` → `tri-music` | 二跳委派，tri-intent 不直接路由 tri-music |
| `article` | I06 | `tri-article` | 去 AI 化长文 / 技术文章 |
| `arch-viz` | I10 | `tri-html` | 项目架构可视化分析（单文件 HTML，六维架构分析） |
| `audit-checklist` | I10 | `tri-checklist` | 项目审计清单生成（Markdown 复选框，四维审计） |

### D1–D5 正交维度

| 维度 | 取值 |
|---|---|
| D1 任务领域 | 办公 / 学习 / 编程 / 生活 / 创作 / 商业 / 情感 / 科研 / 未指定 |
| D2 输入形态 | 文本 / 代码 / 图片 / 文档 / 表格 / 音视频 / 链接 / 无 |
| D3 交互轮次 | 单轮 / 多轮 / 长程 Agent |
| D4 输出期望 | 简答 / 长文 / 结构化数据 / 可执行代码 / 文件产物 / 分步指引 |
| D5 确定性 | 明确 / 模糊 / 开放 |

## 安装

将 `tri-intent/` 目录放入你的 skills 目录即可：

```bash
cp -r tri-intent/ /path/to/your/skills/
```

## 使用

### 1. 意图识别（核心流程）

任何新用户提问进入工作流的第一步，按路由步骤完成意图识别，产出快照交接下游 skill。

### 2. intent-gate 工具（可选）

产出快照后，可调用 `intent-gate.py` 获取轻量复述文案与路由建议：

```bash
# 按意图编码快速判定落盘去向与路由（返回 JSON）
python hooks/intent-gate.py --intent I13 --json

# 结合快照渲染轻量复述 + 路由决策
python hooks/intent-gate.py --snapshot .tribro/snapshots/I13_xxx.md

# clarify-gate 命中时（先澄清）
python hooks/intent-gate.py --intent I11 --clarify --json
```

**退出码**：`0` 正常 / `2` 输入错误或意图无法识别

### 3. 快照产出

识别完成后，产出唯一交付产物——快照，存放于 `.tribro/snapshots/`：

```
.tribro/snapshots/<问题类型>_<日期>_<时间>_<会话ID前8位>.md
```

示例：`I08_20250211_143022_6a5c037d.md`

### 4. 下游依赖检测

产出快照后，自动检测 `下游路由建议` 指向的下游 skill 是否已安装：

- **已安装**：正常交接，下游 skill 将读取快照 §三 执行
- **未安装**：提示用户安装，示例：
  ```
  意图识别已完成，快照已产出（.tribro/snapshots/I11_xxx.md）。
  路由建议指向 tri-coding，但当前未检测到该下游 skill。
  请安装：skillhub install tri-coding --dir <目标目录>
  安装后下游 skill 将读取快照自动接手执行。
  ```

> **对称双向检测**：下游 skill 激活时也会检测 tri-intent 是否可用（上游检测）。无论用户先安装哪一端，缺失的另一端都会被检测到并给出安装引导。
>
> 「不落盘」类意图（Expressing I17–I20、M05）直接自然回应，无下游 skill 需交接，跳过检测。

## 测试

```bash
# 验证 intent-gate.py Flow 计算
python hooks/intent-gate.py --intent I01 --json   # 落盘快照
python hooks/intent-gate.py --intent I17 --json   # 不落盘
python hooks/intent-gate.py --intent I11 --clarify --json  # 先澄清
python hooks/intent-gate.py --intent XX9 --json   # 退出码 2
```

完整测试用例见 `tests/tri-intent-full-testcases.md`（103 条），执行报告见 `tests/tri-intent-full-testreport.md`（100% 通过）。

## 设计原则

- **MECE**：L1 四分类、L2 二十七落点（I01–I21 + CR + M01–M05）、Flow 三态均互斥穷尽
- **职责边界**：仅识别意图 + 产出快照 + 交接下游，不越界产出下游交付物
- **对称双向检测**：产出快照后检测下游 skill 是否安装（下游检测），与下游 skill 的上游检测构成双向机制
- **单一事实源**：落盘规则在 `SKILL.md` 与 `intent-gate.py` 间保持一致
- **兜底闭环**：I19 闲聊娱乐为全体系兜底，保证零覆盖空白
