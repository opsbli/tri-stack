---
name: tri-prototype
slug: tri-prototype
version: 1.1.4
displayName: tri-prototype
description: "PM→Dev 桥接 skill：解析产品原型链接（Axure / 摹客 / 墨刀 / Figma / Figma Dev Mode）与 PRD 文档，提取页面结构、交互规则、业务规则与验收标准，产出 tri-coding 门② 可直接消费的 `requirements.md`（编码需求说明书）——无缝衔接 tri 家族开发流程。支持 Axure share 链接、Figma 文件链接、PRD 文档链接与本地文件输入。认领 I11 的 PM 原型解析子类（L3_子意图=pm-prototype，与 tri-frontend-design / tri-lottie / tri-code-analyzer 并列，非独占 I11）。支持独立安装，含上游依赖检测三态逻辑（快照模式 / 引导安装 / 降级模式）。"
summary: 解析 PM 原型与 PRD → 产出 tri-coding `requirements.md`（编码需求说明书），无缝衔接 tri-coding 门② 的设计审批流程。
tags: [prototype, pm, bridge, requirements, prd, axure, figma, mockingbot, modao]
license: MIT
---

# 原型解析（PM→Dev 桥接）

> 本 skill 是 tri-intent 的下游执行 skill（I11 编码开发 · L3=pm-prototype），依据快照 `snapshot.md` §三 直接执行，不再重新识别意图。
> 用户心智：**PM 给了原型链接，你不需要手动翻页面、手动摘规则——本 skill 帮你解析成 tri-coding 门② 直接可用的 `requirements.md`。**

## 强制执行契约（Execution Contract · 最高优先级）

> 本节定义 skill「被激活后必须做什么」，优先级高于 Agent 的通用默认行为。**读取快照且 `L2 = I11` 且 `L3_子意图 = pm-prototype` 即视为激活本工作流**，MUST NOT 仅将其当作参考文档。

0. **版本检查前置硬门（第零步）**：任一执行入口启动后、核心执行前，MUST 先运行 `python scripts/check_update.py --slug tri-prototype --json`，并按 `references/version-check-spec.md` 的态判定处置（退出码 `<20` 放行，`>=20` 阻断）。**版本检查完成前 NEVER 进入后续步骤**。本条目优先级高于所有其它强制前置条目。
1. **衔接铁律**：本 skill 的核心价值是**无缝衔接 tri-coding 门②**。产出的 `requirements.md` MUST 按 tri-coding 的九章结构（§需求说明书）组织，字段与 tri-coding 门② 期望对齐——NEVER 产出 tri-coding 无法直接消费的自由格式文档。
2. **原型解析诚实铁律**：原型解析的**保真度受平台限制**。MUST 按下列分级如实声明解析保真度，**NEVER 声称「已完整解析原型」**：
   - **高保真**（≥80%）：本地文件（HTML/JSON 导出）、Axure share 链接（公开可访问）
   - **中保真**（50–80%）：摹客 / 墨刀在线链接（需用户配合导出或截图）
   - **低保真**（<50%）：仅 PRD 文档、无原型或原型链接不可访问
   保真度不足时 MUST 告知用户并请求补充（截图 / 导出 / 口头说明），**NEVER 在信息不足时编造页面结构或交互规则**。
3. **PRD 优先铁律**：当 PRD 与原型**冲突**时，**以 PRD 为准**（PRD 是业务规则的权威来源），并在 `requirements.md` 中标注冲突项。NEVER 自行裁决业务规则。
4. **完整链路铁律**：MUST 覆盖「原型解析 → PRD 解析 → 规则提取 → 页面清单 → 交互规则 → 验收标准 → `requirements.md` 产出」完整链路，NEVER 只做部分然后跳过。
5. **最小化原则**：只做 `任务要点` 或用户明确要求范围内的解析工作，NEVER 擅自扩展范围（如顺手写代码、设计 UI、评审业务合理性）。
6. **职责边界**：本 skill 产出的是「**编码需求文档**」，不是业务代码（→ tri-coding）、不是设计方案（→ tri-frontend-design）、不是测试用例（→ 各 skill 的 tests）、不是 PM 文档（本分支未包含，原 tri-pm）。意图识别（tri-intent）、缺陷修复（tri-fix）、业务代码审查（tri-review）均不属于本 skill。
7. **最小输入要求**：至少需要**一个原型链接或一个 PRD 来源**。两者都没有时 MUST 澄清，NEVER 凭想象编造需求。
8. **自检**：作答前 MUST 声明「本次意图=<L2>，已读取快照，原型链接=<平台>，PRD=<有/无>，保真度=<高/中/低>，落盘=<requirements.md 路径>，衔接目标=<tri-coding 门②>」，若与上述规则冲突则停止并纠正。

## 触发时机

| 触发分支 | 典型信号 |
|---|---|
| 快照路由 | tri-intent 快照 `下游路由建议` 指向本 skill，`intent.L2` = I11 且 `L3_子意图` = pm-prototype |
| 直接触发 | 「PM 给了原型链接」「解析这个原型」「把原型转成需求文档」「PRD + 原型转成需求说明书」 |

**不由本 skill 处理**（命中以下信号 MUST 指向对应 skill，NEVER 在本工作流内代办）：

| 信号 | 归属 |
|---|---|
| 产出 PRD / 路线图 / OKR / 竞品分析（PM 文档） | 本分支未包含（原 tri-pm，I06 + L3=pm） |
| 写业务代码 / 实现功能 | tri-coding（I11，默认落点） |
| 界面设计方向 / 风格锚点 / 配色字体 | tri-frontend-design（I11 + L3=frontend-design） |
| 动效代码 / Lottie 集成 | tri-lottie（I11 + L3=motion） |
| 识别用户意图 / 路由 | tri-intent |
| 一次性生成完整课程大纲 | 本分支未包含（原 tri-learn） |

> **与 tri-pm 的关键边界（原 tri-pm，本分支未包含）**：tri-pm 产出**PM 用的文档**（PRD / 战略画布 / OKR）；本 skill 产出 **Dev 用的需求文档**（`requirements.md`）。tri-pm 是 PM 的写作助手；本 skill 是 PM→Dev 的**桥接翻译层**。一句话：tri-pm 写文档，tri-prototype 造需求。（该产出方未包含在本分支，本 skill 仍可消费任意来源的 PRD。）

## 上游依赖检测（独立使用时 · 三态）

| 模式 | 触发条件 | 行为 |
|---|---|---|
| **A · 快照模式** | 按 tri-intent §快照定位契约 定位到**可用快照**（`.tribro/LATEST.md` 指针 → 会话内最新 → 全局最新且 ≤30 分钟） | 读取快照 §三，按其 `任务要点` 执行解析与产出 |
| **B · 引导安装** | 未检测到 `tri-intent/`，或存在但无可用快照 | MUST 输出提示语引导安装，等待用户选择 |
| **C · 降级模式** | 用户明确拒绝安装 tri-intent | MUST 自构造等价输入（从用户描述提取原型链接与 PRD）并**显式声明降级**，再推进 |

**模式 B 提示语**：
> 本 skill 依赖上游 tri-intent 进行意图识别与输入校验（用于快照模式）。当前未检测到 tri-intent 或可用快照。
> 请安装：`python ops/install-skills.py --target <目标目录>`
> 安装后重新发起请求，即可获得完整的「意图识别 → 原型解析 → 需求文档」工作流。
> 若不便安装，可回复「降级执行」，我将基于自构造输入推进，但意图识别精度低于标准链路。

**模式 C 降级声明**（推进前 MUST 原样声明）：
> 未检测到 tri-intent 快照，已进入降级模式：本次基于自构造的等价输入执行，意图识别精度低于标准链路，
> 原型解析与需求文档的覆盖可能不完整，建议后续安装 tri-intent 以获得完整效果。

**模式 C 自构造等价输入**：从用户描述中提取「原型链接（含平台）/ PRD 来源 / 目标页面范围 / 交付预期」，写入交付物的「输入来源」区并标注 `degraded`。

> **对称双向检测**：tri-intent 侧的下游依赖检测会检查本 skill 是否存在（用于提示可委派）；本 skill 侧检查 tri-intent 是否可用。任一端缺失都会被检测到。

## 输入契约

| 字段 | 来源 | 必填 | 用途 |
|---|---|---|---|
| `原型链接` | 用户 / 快照 | 至少一个 | 支持 Axure share、摹客、墨刀、Figma 等平台链接 |
| `PRD 来源` | 用户 / 快照 | ⬜ | PRD 文档链接（web）或本地文件路径（.md / .docx / .pdf） |
| `目标页面范围` | 用户 / 快照 | ⬜ | 指定要解析的页面（如「登录页 + 首页 + 列表页」）；缺省 = 全部 |
| `技术栈偏好` | 用户 / 快照 | ⬜ | 前端框架偏好（React / Vue / ...），写入 requirements.md 的技术约束区 |
| `交付预期` | 快照 §三 | ⬜ | 最终交付物（`requirements.md` / `requirements.md + 页面清单`） |

> 必填项缺失且无法从快照 / 对话推断时，MUST 在解析前提出澄清，NEVER 凭默认值猜。

## 职责边界

- **本 skill 负责**：解析原型链接与 PRD → 提取页面结构、交互规则、业务规则、验收标准 → 按 tri-coding 九章规范产出 `requirements.md` → 无缝衔接 tri-coding 门②。
- **不负责**：写业务代码（tri-coding）、界面设计方案（tri-frontend-design）、动效实现（tri-lottie）、产出 PRD / 路线图 / OKR 等 PM 文档（本分支未包含）、意图识别（tri-intent）、缺陷修复（tri-fix）。
- **相邻边界**：

| 相邻 skill | 边界判据 |
|---|---|
| **tri-coding**（I11 默认） | 本 skill 产出 `requirements.md`（tri-coding 门② 的**输入**）；tri-coding 消费该文档产出 design.md / tasks.md / 代码 |
| **tri-frontend-design**（I11 + L3=frontend-design） | 本 skill 产出**需求层**（做什么）；tri-frontend-design 产出**设计层**（怎么做好看）。原型解析包含视觉线索提取，但不下设计结论 |
| **PM 文档产出**（原 tri-pm，本分支未包含，I06 + L3=pm） | 原 tri-pm 产出**PM 文档**（PRD / OKR）；本 skill 可**消费** PM 文档（作为输入源之一），但该产出方未包含在本分支 |
| **tri-workflow**（I13 + L3=workflow） | 本 skill 产出**需求文档**（单个功能的 requirements.md）；tri-workflow 产出**流程定义**（CI/CD / 审批流 / DAG），两者交付物类型不同 |

## 核心能力方法论（原型解析 · 可扩展）

> 核心能力是「**平台适配 + 规则提取 + 规范映射**」三层流水线，而非自由发挥。

1. **平台适配**：按原型平台（Axure / 摹客 / 墨刀 / Figma）选择解析策略；同一平台内按页面粒度逐页提取
2. **规则提取**：从原型（页面结构 / 交互标注）与 PRD（业务规则 / 验收标准）中提取**结构化规则**——业务规则 MUST 有 PRD 出处（章节号 / 页码），交互规则 MUST 有原型出处（页面名 / 区域）
3. **规范映射**：将提取结果映射到 tri-coding 的 `requirements.md` 模板（九章结构），确保下游门② 可直接消费

### 解析保真度分级

| 保真度 | 条件 | 产出可信度 | 处置 |
|---|---|---|---|
| **高**（≥80%） | 本地 HTML/JSON 导出、Axure 公开 share 链接 | 页面结构 + 交互标注完整 | 直接产出 |
| **中**（50–80%） | 摹客 / 墨刀在线链接（公开可访问但结构化程度有限） | 页面清单可提取，交互规则需用户补充 | 产出 + 标注待补充项 |
| **低**（<50%） | 原型链接不可访问 / 仅 PRD / 仅口头描述 | 仅能从 PRD 提取 | 产出 + 显式告知信息不足 |

### 可扩展性

1. **新增原型平台**：在 `references/prototype-platforms.md` 追加平台行（URL 特征 / 解析策略 / 保真度级别），解析逻辑自动适用
2. **新增需求模板字段**：在 `templates/requirements.md` 追加字段，产出文档自动对齐
3. **新增 PRD 格式**：在 §PRD 解析 追加格式行（.docx / .pdf / .md），解析逻辑零改动

## 处理流程

> 执行顺序固定：§版本检查与更新机制（第零步）→ 上游依赖检测 → 读取快照 §三 → 核心执行。

```
原型链接 + PRD
     ↓
① 平台识别与保真度判定
     ↓
② 子资源发现与递归抓取  ←—— 关键步骤：识别 iframe / script src 并递归抓取
     ↓
③ 原型解析（页面结构 + 交互标注）
     ↓
④ PRD 解析（业务规则 + 验收标准）
     ↓
⑤ 规则合并与冲突标注（PRD 优先）
     ↓
⑥ 映射到 tri-coding requirements.md 模板
     ↓
产出 requirements.md（tri-coding 门② 可直接消费）
```

**六步流水线**：

| 步骤 | 输入 | 产出 | 判据 |
|---|---|---|---|
| ① 平台识别 | 原型 URL | 平台名 + 保真度等级 | URL 特征匹配 `references/prototype-platforms.md` |
| **② 子资源发现** | 主页面 HTML | **子资源清单（PRD / 交互稿 / 数据文件）** | 解析 `<iframe src>` / `<script src>` / `<link href>`，**递归抓取**每个子资源 |
| ③ 原型解析 | 全部子资源内容 | 页面清单 + 交互规则（结构化） | 每页面 MUST 有名称 + 组件 + 交互 |
| ④ PRD 解析 | PRD 数据（spec-data.js 等） | 业务规则 + 验收标准（结构化） | 每规则 MUST 有 PRD 出处 |
| ⑤ 规则合并 | ③ + ④ 的产出 | 统一规则集（冲突标注） | 冲突 MUST 标注 PRD 优先 |
| ⑥ 规范映射 | ⑤ 的产出 | `requirements.md`（tri-coding 九章） | 九章齐全，tri-coding 门② 可直接消费 |

### 步骤 ② 子资源发现（关键步骤 · v1.1 新增）

> **为什么需要**：原型页面通常是**壳 + 子资源**架构。壳（`index.html`）只含导航结构和
> `<iframe>`/`<script>` 引用，**实际内容（PRD、交互稿）在子资源文件里**。
> 只抓壳而不跟进子资源，只能拿到 3–7% 的数据（实测：壳 13.7KB vs 实际 334.5KB，差 **24 倍**）。

**发现规则**：

| 子资源类型 | 发现方式 | 内容类型 |
|---|---|---|
| `<iframe src="...">` | 正则提取 src 属性 | 交互设计稿（HTML） |
| `<script src="...">` | 正则提取 src 属性 | PRD 数据（JS 对象，如 `SPEC_DATA = {...}`） |
| `<link href="...">` | 正则提取 href 属性 | CSS / 数据文件 |

**递归深度**：最多 2 层（壳 → 子资源 → 子资源的子资源），NEVER 无限递归。

**JS 数据文件解析**：若子资源是 `.js` 文件且含 `const VAR_NAME = {...}` 结构，
MUST 提取该对象并解析为 JSON（JS 对象 → JSON 的键值对）。值中的 HTML 字符串
MUST 去除标签后提取纯文本，按 `<h5 class="spec-func-title">` 等结构化标记分段。

**实测案例**（资产管理系统原型）：

```
index.html（壳，13.7KB）
├── <iframe src="ui/asset-mgmt.html">   → 186.7KB（交互设计稿）
└── <script src="spec-data.js">          → 147.8KB（PRD，SPEC_DATA 对象）
    └── 16 页 × 96 功能点 × 8 字段/功能点 = 852 个字段条目

⇒ 只抓壳 = 13.7KB（3%）；跟随子资源 = 334.5KB（100%）
```

**保真度影响**：完成子资源发现后，保真度从「中（50–80%）」升级为「高（≥80%）」。

### 兜底处理（NEVER 静默失败）

| 场景 | 处置 |
|---|---|
| 版本检查异常 | 自维护模式下版本声明不一致 → 标注漂移明细并放行（附修订动作）；脚本自身异常 → 兜底降级放行 |
| 上游缺失 | 降级模式 C（自构造输入 + 显式声明精度降低） |
| **原型链接不可访问** | 标注保真度=低，请求用户提供截图或口头描述，NEVER 编造页面结构 |
| **PRD 与原型冲突** | 以 PRD 为准，标注冲突项供用户裁决 |
| **原型平台不在支持列表** | 标注平台=未知，请求用户提供截图/导出文件 |

## 🔴 检查点与红灯清单（STOP · NEVER）

### 🔴 用户确认检查点（STOP）
- 🔴 **STOP**：最小输入要求——原型链接与 PRD 来源两者都没有时，未获用户澄清补充 NEVER 凭想象编造需求（§强制执行契约 条 7）。
- 🔴 **STOP**：必填项缺失且无法从快照/对话推断——MUST 在解析前向用户提出澄清，未获答复 NEVER 凭默认值猜（§输入契约）。
- 🔴 **STOP**：解析保真度不足（中/低保真或链接不可访问）——MUST 告知用户并请求补充（截图/导出/口头说明），未获补充 NEVER 继续推进（§解析保真度分级）。

### 🚫 红灯清单（NEVER）
- NEVER 声称「已完整解析原型」，保真度受平台限制（§强制执行契约（Execution Contract · 最高优先级））
- NEVER 在信息不足时编造页面结构或交互规则（§强制执行契约（Execution Contract · 最高优先级））
- NEVER 自行裁决业务规则，PRD 与原型冲突时以 PRD 为准并标注冲突项（§强制执行契约（Execution Contract · 最高优先级））
- NEVER 擅自扩展范围（如顺手写代码、设计 UI、评审业务合理性）（§强制执行契约（Execution Contract · 最高优先级））
- NEVER 产出 tri-coding 无法直接消费的自由格式文档（§强制执行契约（Execution Contract · 最高优先级））
- NEVER 无限递归抓取子资源，递归深度最多 2 层（§步骤 ② 子资源发现（关键步骤 · v1.1 新增））

## 交付产物

### 一、产物清单

| 产物 | 文件名 | 内容 | 触发模式 |
|---|---|---|---|
| **编码需求说明书** | `.tribro/coding/<命名>/requirements.md` | tri-coding 九章结构（§需求说明书） | A / C |
| 解析报告 | `reports/<slug>-parse.md` | 保真度声明 / 平台信息 / 页面清单 / 规则统计 / 冲突项 | A / C |

### 二、落盘规则

- **`requirements.md`** 落 `.tribro/coding/<命名>/`（tri-coding 门② 的标准读取位置）
- **解析报告** 落 `reports/` 或与 `requirements.md` 同目录
- 命名规则 `<问题类型>_<YYYYMMDD>_<HHMMSS>_<会话ID 前 8 位>`

## 版本检查与更新机制（强制技术约束 · 硬红线）

<!-- version-stub v1 · 瘦指针节点；细则唯一真源见 references/version-check-spec.md -->

> 任一执行入口启动后的**第零步**，先于核心执行阶段。细则唯一真源：`references/version-check-spec.md`；
> 可执行实现（逻辑唯一真源）：`scripts/check_update.py`。
> **铁律**：版本比较、升级执行、回退、状态判定 MUST 由脚本完成；prompt 层 ONLY
> 「调用脚本 + 解析其 JSON 输出 + 按 `state` 处置」，NEVER 在 prompt 内联推断版本或拼接升级命令。

```bash
python scripts/check_update.py --slug tri-prototype --json
```

- 处置：按脚本输出放行或阻断（判据与 `block_code` 语义见真源）；NEVER 因版本门自身故障阻断 skill 启动。

## 宿主兼容与提问呈现（横切硬约束 · 呈现纪律）

<!-- host-compat-stub v1 · 自包含瘦节；细则唯一真源见 tri-intent/references/host-compat.md（本节点文本自洽，独立安装时不依赖该文件可达） -->

> 本 skill 的「需要用户决策」时机全部以宿主中立自然语言书写（如「是否…？（是 / 否）」、clarify-gate 的
> 「逐条补充 / 按默认 / 继续」）。在**提供交互式提问工具**的宿主中（如 Proma 的 `AskUserQuestion`），
> 运行时会自动把这类句式升级为交互式问答横幅——**呈现形式由宿主决定，不由本 skill 决定**。
>
> **家族约定（MUST）**：凡触发 🔴 STOP 用户确认检查点或 clarify-gate 的时机，MUST 以**普通 Markdown 文本**
> 呈现为聊天问题，**NEVER 调用交互式提问工具**（`AskUserQuestion` / `ask_user_question` /
> `request_user_input` / `clarify` 及等价物）；用户回复契约（逐条补充 / 按默认 / 继续 / 是·否）
> **保持不变**。
>
> **边界**：本条只管呈现形式，MUST NOT 改动任何门控的判定条件、触发时机与处置动作；
> 在无交互式提问工具的宿主中本条自然空转；用户明确要求交互式提问时优先用户指令；
> 跨宿主判据只认「🔴 STOP 用户确认检查点」这一形态，NEVER 在 skill 内硬编码宿主工具名。
## 目录结构

```
tri-prototype/
├── SKILL.md                       主入口：五步流水线 + 保真度分级 + tri-coding 衔接契约
├── README.md                      特性 / 安装 / 用法 / 目录结构 / 设计原则
├── CHANGELOG.md                   版本变更记录
├── references/
│   ├── version-check-spec.md      版本检查执行规范（内部化持有）
│   └── prototype-platforms.md     支持的原型平台清单（URL 特征 / 解析策略 / 保真度）
├── scripts/
│   └── check_update.py            版本门（自维护模式）
├── templates/
│   └── requirements.md            tri-coding 门② 的需求说明书模板
└── tests/
    └── tri-prototype-full-testcases.md  全场景测试用例
```
