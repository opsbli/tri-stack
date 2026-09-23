# 高精度图表引擎作者契约（viewer-authoring）

> 本文件是 tri-html「高精度渲染模式」的**唯一作者契约真源**。适用于 `scripts/viewer/`（Typed JSON IR → 确定性校验 → 单文件交互 HTML）。Mermaid 兼容模式的模板见 `references/mermaid-templates.md`，两者互为补充：**五类技术图走 viewer 引擎，其余图表类型走 Mermaid**。本契约只承诺 vendored 引擎真实具备的能力；引擎尚不具备的外部演进能力一律不进入创作路径（差距登记见 `references/engine-evolution-notes.md`）。

## 一、快速创作路径（Fast Authoring Path）

按此有界路径生成，**首个候选写盘之前禁止阅读渲染器源码 / validator 源码 / 测试**（实现细节仅在诊断不支持或两轮聚焦修复失败后才查）。

1. **选类型**：从需求中判定 `architecture` / `workflow` / `sequence` / `dataflow` / `lifecycle` 之一（类型路由表见 §二）。
2. **读样例**：只读 `scripts/viewer/schemas/` 中对应 schema + `schemas/common.schema.json` + `scripts/viewer/examples/` 中一个同类型 JSON。示例仅学字段形态，**事实必须新写**（新稳定 ID、领域措辞、布局）。
3. **先写候选**：下一个动作必须是写出候选 JSON，不要在散文里规划坐标。起点纪律：
   - 一条清晰主路径 + 短侧支 + 稀疏标签，主节点 ≤ 12 个；
   - `meta.quality_profile` 设为 `"showcase"`（用户显式要密集大图才用 `standard`）；
   - 先用自动路由（auto）与自动标签，**诊断未要求前不加** `via` / `channelX` / `channelY` / `labelAt`；每次修复只应用一个被诊断指出的几何控制。
4. **每轮编辑后校验**，交付前必校验：
   ```bash
   node scripts/viewer/bin/viewer.mjs validate <type> <candidate.json> --quality showcase --json
   ```
   仅 4 项 artifact 检查的回执是 basic 校验，**不是** showcase 验收；showcase 通过必须报告全部 9 项检查且 0 组合错误、0 警告。候选若漏写或拼错 `meta.quality_profile`，先修它再修几何。**最终通过校验的候选即冻结：之后永不改动。**
5. **交付**：
   ```bash
   node scripts/viewer/bin/viewer.mjs deliver <type> <candidate.json> <output.html> --quality showcase --json
   ```
   `deliver` 冻结规格字节到同目录私有快照、渲染并检查、**原子提交** HTML，报告规格与成品的 SHA-256 与字节数。非零退出码**永远不得**被描述为成功。

### 修复循环（硬上限 2 轮）

校验失败时：读 `diagnostics[]` → **只修改其中 `subject` 指向的对象** → 核对 `evidence` → 从 `supportedFixes` 列出的方式中选择 → 重跑。客观错误计数下降则继续；**连续 2 轮未创新低即停止**，如实报告未解决的诊断。绝不整图重写、绝不为了过 showcase 删掉有语义的标签。

## 二、类型路由表

| 类型 | 适用 | Prompt/需求中应包含 |
|---|---|---|
| `architecture` | 组件、服务、存储、系统/信任边界 | 范围、核心组件、主要路径 |
| `workflow` | CI/CD、审批、工具调用、Runbook | 参与者、顺序、分支、异常 |
| `sequence` | API 调用、缓存回源、鉴权、异步链路 | 调用方、被调用方、返回、时序 |
| `dataflow` | 数据管线、血缘、PII、下游消费者 | 来源、转换、存储、边界 |
| `lifecycle` | 状态、重试、等待、终态 | 状态、事件、重试与取消路径 |

不确定时运行：
```bash
node scripts/viewer/bin/viewer.mjs guide "<场景描述>" --json
```
场景证明示例是结构参照，不是可抄的事实。

## 三、Mermaid 输入转换

读入 Mermaid 时**只取拓扑与语义**，然后重新创作全新 viewer JSON；不机械复刻 Mermaid 样式：

- `flowchart` / `graph` → `workflow`；组件图语义则 `architecture`；
- `sequenceDiagram` → `sequence`；participants 成为语义参与者，箭头成为消息；
- `stateDiagram` → `lifecycle`；状态与迁移保留语义。

tri-html 自身的 Mermaid 模板（目录树/类图/ER/旅程图）没有对应 viewer 类型，仍走 Mermaid 通道。

## 四、创作不变量（Authoring Invariants）

- **一条明显主路径**；侧支从最近的主路径节点离开。加路由控制之前先删低价值边。
- 默认**省略** `meta.visual_preset`（默认 `classic` 打开）；`signal-flow` / `blueprint` / `editorial` 仅在用户显式要求视觉风格时设置。色板模式（深/浅）与视觉预设相互独立。
- 默认**省略** `meta.subtitle`；永不发明复述标题的副标题。
- 桌面首屏观感：为一个响应式成品设计足够的纵向节奏，让图表面板与结论卡片在 1440×900 / 1600×1000 / 1920×1080（大屏另查 2048×1320）都是平衡整体；要求 `scrollWidth <= innerWidth` 且 `scrollHeight <= innerHeight`。修复溢出的顺序：删真正冗余的内容 → 压缩间距 → 才考虑缩小节点/标签。**禁止**用 `overflow: hidden`、裁剪内容、内部滚动条、拉伸 SVG 高度、缩小字号来伪造通过。
- `meta.legend` 默认省略（诚实的 `auto`）；需要时只用 `mode: auto|all|hidden` 与 renderer 支持的 `entries.<kind>.label|visible`。
- **语言**：`meta.locale` 只控制 renderer 拥有的 Viewer UI（`"en"` / `"zh-CN"`）；创作内容语言由用户选择决定，renderer 永不翻译创作内容。其他语言须省略 `meta.locale` 并向用户披露 Viewer UI 回退英文。
- 精确保留产品名、代码标识符、命令、协议、API 路径、环境名。
- **品牌徽标可选且显式**：节点命名真实产品时才在 `brand` 放 ID；无匹配且用户提供了官方 URL 时，先 `brands capture` 再使用返回的 digest-pinned 值；否则省略。永不从模糊角色（如 "database"）推断品牌，徽标永不替代语义 `type`/标签/关系事实。**当前基线说明**：内置品牌发现可用（标记编译于引擎 generated 模块，`brands "<名>"` 直接查询）；目录数据文件与 capture 溯源生成链未随包（见 `references/engine-evolution-notes.md` E3）。
- sequence 图默认省略 `meta.column_fit`（稳定 `fixed`）；宽 viewBox 留白或参与者标签放不下时设 `"spread"`，且先试 `spread` 再考虑缩短语义标签。
- 组件类型：`frontend` / `backend` / `database` / `cloud` / `security` / `messagebus` / `external`；变体：`default` / `emphasis` / `security` / `dashed`。
- **关系标签是语义数据**：碰撞时先移标签、调路由/间距，然后才在保义前提下缩短措辞。仅当两端完全隐含关系且不含协议/动作/方向/同步异步/跨界机制时才可删标签，且须说明为何冗余。**永不仅为过 showcase 删有语义的标签。**
- `meta.engineering_profile` 默认省略；仅当用户显式要求生产部署拓扑/负责人交接/fail-closed 部署评审且事实已知时启用 `deployment-ownership`。一旦启用，**不得为过校验而移除工程画像**——修复事实或如实报告诊断。
- 间距 = **净空**（clear gap）而非中心距；关系标签的净空必须大于其测量遮罩宽度。
- 自动路由拥有其端点侧向：首段与末段必须垂直于该侧离开/进入。
- 自动端口展开（Automatic Port Spread）是 architecture/workflow/dataflow/lifecycle 的默认行为：跳过单关系与显式 `via`/`channelX`/`channelY`/`labelAt`/非 `auto` 路由。
- **永不接受**：边穿过不相关不透明节点、歧义共享走廊、关系标签遮挡其他路由。

字段枚举、间距数学、几何修复规则、仓库证据、模式化放置的完整细则：`scripts/viewer/references/authoring-contract.md`（按需查阅，不默认读取）。

## 五、交付与验收

- `validate` 用于修复循环，`deliver` 一次用于最终验收。deliver 冻结规格字节 → 渲染检查 → 原子提交 → SHA-256 + 字节数回执。
- 交付后收集桌面证据（不改不重渲信任 HTML）：
  ```bash
  node scripts/viewer/bin/viewer.mjs visual-check <output.html> --json
  ```
  `visual-check` 在四档视口测量容纳性并抓深浅主题截图；自动回执恒为 `visualReview: "pending"`（截图是检查证据，不是自动抛光声明）。无 Chrome/Chromium 时 exit 2 = skipped，不视为失败。
- **失败交付禁跑 visual-check**：`deliver` 失败时上一成品被保留（引擎行为：previous artifact was preserved），此时跑 `visual-check` 检查到的是**过期的最后好图**而非失败候选——NEVER 在失败交付路径上跑 `visual-check`，先修候选再重新 deliver。
- **三声明分离**：`deliver` 证明确定性成品检查、`visual-check` 证明真实浏览器内的有界行为证据、感知性视觉审查只能由人或图像模型完成——三者独立汇报，不互相替代。
- `--open` 仅在用户要即时预览时加。活跃桌面创作循环用 `preview`（仅监听 127.0.0.1，失败保留最后好图），**默认不启动**。
- `compare`（显式启用，PR/设计评审场景）：两份已校验 architecture 快照 → Before/Delta/After + 机器回执：
  ```bash
  node scripts/viewer/bin/viewer.mjs compare architecture base.json head.json <output.html> --json
  ```
  **compare 失败恢复**：提交失败时引擎回滚恢复上一成品；若恢复自身失败，恢复目录会被保留并报告「备份→目标」路径，而不是在清理中删除剩余备份——据此定位手工恢复。

## 六、环境与降级

- 引擎零运行时 npm 依赖，仅需 Node ≥ 18。健康自检：
  ```bash
  node scripts/viewer/bin/viewer.mjs doctor
  node scripts/viewer/bin/viewer.mjs demo <output-dir>
  ```
- 无 shell 环境时的兜底：把架构 SVG 手工放入 `scripts/viewer/assets/template.html`，用 CSS 语义类而非内联颜色（此时不产生交互 Viewer 能力，产物质量受限，须向用户声明）。
- **tri-html 集成降级链**：Node ≥ 18 不可用 → 本 skill 全量回落 Mermaid 兼容模式（`scripts/build_html.py`），声明降级口径后继续，**绝不阻断交付**。

## 七、产出汇报口径

返回：已检查的 HTML 路径、图表类型、校验摘要（checksPassed/checkCount/errors/warnings）、规格与成品回执（SHA-256/字节数）、诚实的 visual-review 状态。**不得**为非零命令宣称成功，不得宣称执行过未做的视觉检查。
