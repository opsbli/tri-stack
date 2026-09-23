---
name: caveman-distill
description: 蒸馏自开源项目 caveman（JuliusBrussee/caveman, v2.7.0）的 token 节省方法论——核心架构、关键模块、执行流程、依赖、接口与设计决策；含 caveman 与 tri-cost 全面对比；作为 tri-cost 降本增效建议的方法底座。内容严格依据 docs/analysis-caveman-main-20260919.md，不引入报告外臆测。
---

# caveman 知识蒸馏（token 节省方法论）

> **蒸馏基准报告**：`docs/analysis-caveman-main-20260919.md`（以下简称「基准报告」）。本文件内容严格依据该报告，剔除冗余实现细节，仅保留架构 / 模块 / 流程 / 依赖 / 接口 / 设计决策；不遗漏关键结论，不引入报告外臆测。
> **来源项目**：`https://github.com/JuliusBrussee/caveman`（本地克隆 `caveman-main`，v2.7.0）。
> **许可边界**：MIT 部分（skill / CLI / SDK / 中间件）可自由复用方法；BSL-1.1 的 engine / proxy / mcp / browse 等**方法可借鉴，源码不可在 tri-xxx 中再许可或打包**（见 §九）。

---

## 一、与 tri-cost 全面对比（差异与优劣势）

> 本对比基于 tri-cost SKILL.md（审计定位）与基准报告（caveman 定位）的已定义事实。
> 置信度：中；依据：推断 inferred；来源：tri-cost SKILL.md + 基准报告 §1 / §9 / §10。

| 维度 | caveman | tri-cost |
|------|---------|---------|
| 核心目标 | 主动削减 token 消耗（**节流层**） | 被动观测与评估 token 消耗（**账房层**） |
| 作用域 | 同时作用于「说」（输出风格）与「读」（上下文输入） | 作用于「记账」（全链路分账 N1–N8） |
| 机制 | 真实压缩引擎（Go 二进制 proxy/engine）+ prompt 风格规则 | 确定性成本聚合脚本 + 逐节点三问评估 |
| 运行时依赖 | 需独立运行时（proxy/engine 二进制、SQLite CCR） | 仅需 Python 脚本 + JSONL 索引，零外部运行时 |
| 是否真能省 | 是（实测输入侧约 -33%、输出侧约 -8.5%） | 否（只观测，建议交用户 / 对应 skill 落地） |
| 适用场景 | 长会话、大量日志 / 测试输出读取 | 看清「钱花在哪、该不该省」 |
| 家族定位 | 外部开源工具（非 tri-xxx） | 横向方法论型 skill（tri-xxx 横向层） |

**优劣势小结**：
- caveman 优势：真能省（实测显著）；劣势：重工程、Go+TS 双栈、BSL/MIT 双许可门槛、需运行时。
- tri-cost 优势：轻量、零运行时依赖、与全家族 skill 集成做审计；劣势：只观测不落地、建议需人工执行。
- **互补性（核心结论）**：tri-cost 的降本增效建议可引用 caveman 的方法库（输出风格压缩 + 13 类载荷感知摘要）作为具体可执行动作；caveman 的节省效果可由 tri-cost 量化审计（A/B 验证）。二者非竞争，是「节流」与「账房」的闭环协作。
  - 置信度：中；依据：推断 inferred；来源：基准报告 §10。

---

## 二、核心架构（双管齐下）

- **skill 一侧（纯 Markdown，MIT）**：约束 agent 输出风格以省 token（`skills/caveman/SKILL.md`）；强度档位 `lite` / `full`(默认) / `ultra` / `wenyan-*`；混入 **ASD-STE100 简化技术英语**；**Auto-Clarity 回退**（安全警告 / 不可逆操作 / 歧义风险时恢复常规表达）。核心原则：*压缩只缩短风格、绝不增长输出；若 caveman 表达不比平白短，就用平白*。
  - 来源：基准报告 §3.1。
- **proxy + engine 一侧（Go，BSL）**：本地 **loopback HTTP** 代理，base-URL 替换，位于 agent 与提供商之间；`detect()` 分类负载 → 路由压缩器 → **CCR SQLite 备份原文** → 转发上游。`contextwindow.Pack()` 用 **BM25 + 近因 + 错误信号** 做令牌预算打包。
  - 来源：基准报告 §3.2 / §3.3。

---

## 三、关键模块及其职责

| 模块 | 语言 / 许可 | 职责 |
|------|-----------|------|
| `engine/` | Go / BSL | 压缩核心：detect、compressors、ccr 备份、contextwindow 打包、pixel、safety、tokens |
| `proxy/` | Go / BSL | 字节安全代理网关 + 提供商适配 + 本地支出存储 |
| `mcp/` | Go / BSL | 向 agent 暴露 5 个 Engine 工具 |
| `packages/cli` | TS / MIT | CLI 漏斗，仅启动 BSL 二进制，自身不含引擎 |
| `packages/middleware` / `packages/sdk` | TS / MIT | 框架中间件与薄客户端 |
| `skills/` | Markdown / MIT | 主 skill + 子 skill + 元 skill |
| `src/hooks/` | TS / JS | 插件 hooks：激活 / 模式跟踪 / 状态栏 |
| `agents/profiles/` | JSON | 各 agent 包裹 profile（声明式） |
| `cavemem`（`mem/`） | Go BSL + JS/Py MIT | 持久记忆（BM25 召回 + recovery_handle） |

> 完整入口点见基准报告 §4。

---

## 四、主要代码执行流程

1. **工具输出经代理**：`detect → compress → backup(CCR) → forward`；恢复经 `caveman_retrieve` / `Retrieve` 解析 `ccr_ / ccr://` 句柄返回字节精确原文；fail-closed 兜底（不确定即原样转发）。
2. **CLI 路由**（`packages/cli/src/index.ts`）：动词表（约 70 个）dispatch 到 `shrink` / `toon` / `convert` / `browse` / `trial` / `learn` / `wrap` / `stats` / `mem` 等；缺失二进制只禁用对应命令，不崩整体。
3. **skill 激活 / 模式切换**（`src/hooks/`）：`SessionStart` 持久化模式；`UserPromptSubmit` 检测 `/caveman` 命令与自然语言开关；状态写经原子 `safeWriteFlag()` + session id 白名单。
   - 来源：基准报告 §5。

---

## 五、依赖关系

- **Go**：chromedp、pgx、modernc/sqlite（纯 Go 无 cgo）、tiktoken-go、klauspost/compress、minio-go、go-tree-sitter、go-winio、x/crypto、yaml、xxhash。
- **TS**：pnpm workspace 16 包，根依赖 `@caveman-ai/cli`。
- **Python**：benchmarks / evals / mem-py。
- **内部耦合**：`proxy → engine(+ccr, safety, tokens)`、`mem`；`mcp → engine`；`packages/cli`(MIT) **仅启动** BSL 二进制、不引引擎代码（许可边界清晰）。
  - 来源：基准报告 §6。

---

## 六、重要接口与设计决策

- **detect() 13 类载荷分类法**（`engine/detect.go:13-24`）：`json / log / code / diff / search-result / toon / html / a11y / terminal / tabular / config`；检测顺序严格（先 `json` → `terminal`(ANSI 结论性信号) → `diff` → `html`(JSX 防误判) → `tabular` → `code` → `log` → `search-result` → `config` → 否则 `text`）；**fail-open**（不自信归 `text`）。这是蒸馏给 tri-cost 的「载荷类型感知摘要」方法底座（见 §七 / §八）。
- **fail-closed 设计哲学**：任何压缩 / 摘要不确定时原样保留或显式声明「未压缩」，绝不伪造「零 token 收益」；S4 有损变换无 CCR 存储即回退原字节（`engine.go:120-135`）。
- **recovery-handle 心智模型**：有损摘要配 `recovery_handle` + 原文可找回；蒸馏为「摘要时标注 `<<原始在 X>>`、按需 retrieve」的使用约定。
- **safety 等级 S0–S4**（`engine/safety/safety.go:14-48`）：S0 字节安全 / S1 提供商提示 / S2 结构化 / S3 行为级 / S4 有损结构化（必须 CCR）；可映射为 tri-cost 的「变换风险分级」。
- **BM25 式上下文打包**（`engine/contextwindow/contextwindow.go`）：打分 = `BM25(k1=1.5, b=0.75)` + `Priority` + `RecencyWeight·exp(-age/halfLife)`(默认半衰期 6h) + `ErrorBoost`(+0.8) + `Pin`(+1e6)；贪心装袋 + 原始时序重排。可简化为 tri-cost 提示「按任务相关性裁剪历史上下文」。
- **压缩器纯字节变换**：15 个内置压缩器，接口 `Compressor{ContentType(), SafetyClass(), Compress()}`；registry 模式；引擎在外做检测 / 计数 / 备份 / 恢复（可测试性根基）。

---

## 七、13 类载荷「如何读 / 如何摘要」提示规则（蒸馏给 tri-cost 的建议知识底座）

> 将 caveman `detect` 分类法转译为 tri-cost 降本增效建议的「输入侧摘要」动作库。仅保留策略要点，细节见基准报告 §3.2 / §9.1。
> grep 模式：`载荷摘要`。

| 载荷类型 | 保留 | 可丢弃 | 预期节省* | 对应 tri-cost 建议 |
|----------|------|--------|-----------|-------------------|
| json | keys / 结构 / 错误子树；折叠重复数组 | 冗余数组项 | 70–90% | 裁剪上下文 / 复用缓存 |
| log | 错误 / 堆栈 / 首末行 | INFO / 进度噪声 | 85–95% | 裁剪上下文 |
| code | imports / 签名 / 类型 | 函数体 | 40–70% | 裁剪上下文 |
| diff | 文件 / hunk 头 + 变更行 | 重复上下文 | 60–80% | 裁剪上下文 |
| search-result | 顶部 / 底部命中 + 诊断 | 中部冗长命中 | 80–95% | 裁剪上下文 |
| text / html | 标题 / 关键段 / 开闭上下文 | 装饰 / 模板 | 50–80% | 摘要输出 |
| terminal | 结论性输出 / 末行 | 进度条 / 转义噪声 | — | 裁剪上下文 |
| tabular / config | 表头 / 变更行 / 差异项 | 全量重复行 | — | 裁剪上下文 |

> * 原始节省数据为 caveman 代理实测区间，来源：基准报告 §3.2 / README。tri-cost 引用为「建议动作」，不承诺同等压缩比（置信度：高；依据：事实 known；来源：基准报告 §3.2）。

---

## 八、输出风格压缩规则（蒸馏给 tri-cost 的建议知识底座）

> 对应 caveman SKILL.md 的输出侧（N7 / N8）节省。grep 模式：`输出风格`。

- **强度档位**：`lite`（去填充 / hedging，保冠词与完整句）/ `full`（丢冠词、片段、短同义词，默认）/ `ultra`（省连词、一字一词）/ `wenyan-*`（半文言语域，字符级非 token 级）。
- **规则要点**：删冠词 / 填充 / 客套 / hedging；片段式；短同义词（big 非 extensive）；禁装饰性表格 / emoji；不 dump 长错误日志（除非被问，引最短决定行）；技术术语 / 代码 / 错误串原样保留。
- **Auto-Clarity 回退**：安全警告、不可逆操作确认、歧义风险、压缩本身造成技术歧义时恢复常规表达。
- **核心原则**：*压缩只缩短风格、绝不增长输出；若 caveman 表达不比平白短，就用平白*。
- **tri-cost 落地**：将「输出风格压缩」列为 N7 / N8 节点「改进建议」的具体可执行动作（用户 / 下游 skill 采纳后由模型在生成时执行，tri-cost 不自带运行时）。

---

## 九、可蒸馏 vs 不可蒸馏（蒸馏边界，严格一致于基准报告 §9）

### 可蒸馏（作为 prompt 方法论层吸收）
1. 输出风格压缩规则（`skills/caveman/SKILL.md` 本身即 MIT Markdown）。
2. 13 类载荷分类法（`detect` taxonomy）转译为「如何读 / 如何摘要」提示规则。
3. fail-closed 设计哲学（不确定即原样保留）。
4. recovery-handle 心智模型（摘要标注原文可找回）。
5. BM25 式上下文裁剪策略（自然语言描述）。
6. safety 等级 S0–S4（映射为变换风险分级）。

### 不可蒸馏（需真实运行时 / 二进制，非 Markdown 可替代）
1. Go 代理二进制 `caveman-proxy`（loopback 网关 / 提供商适配 / 记账）。
2. SQLite CCR 存储（字节精确恢复）。
3. 确定性字节级压缩器（JSON / log / code / diff 等）。
4. pixel 渲染（pxpipe + Spleen 5×8 + GNU Unifont 字形图集）。
5. 浏览器自动化（chromedp / CDP 可访问性快照）。
6. BM25 / tokenizer 实际实现。
7. BSL-1.1 引擎源码本身（方法可借鉴，源码不可打包进 tri-xxx）。

---

## 十、与 tri-cost 的落地结合点（增强边界 · v1.3.0 升级）

> v1.2.0 起，tri-cost 从"只观测建议"升级为"主动执行方法论 + 量化前后对比"，本蒸馏文件的方法论已**落地为可执行动作**；v1.3.0 进一步把 §五（BM25 令牌预算打包）与 §六（safety S0–S4 分级）落成**代码级强约束**，token 使用在流程中被自动校验与限制。

- **方法论已落地执行**：§七（13 类载荷摘要法）与 §八（输出风格压缩规则）已由 tri-cost `scripts/token_optimize.py` 落成确定性可执行逻辑（detect → compress → count → accuracy → recovery → report），对应 COST_OPTIMIZE 模式；该脚本为纯 Python、零外部运行时，仅实现 caveman 方法层，**不打包其 BSL-1.1 引擎**（Go 代理 / engine / SQLite CCR）。
- **预算闸门已代码化（v1.3.0）**：§五 BM25 打包思路 → `scripts/token_budget.py pack_context`（Okapi BM25 近似，错误/钉住项强制保留）；§六 S0–S4 分级 → `safety_class_of`；流程级强约束 `enforce_node`（COST_TRACK 写入前闸门：超预算自动优化，超硬上限 fail-closed 阻断保留原文）与 `gate_index`（COST_AUDIT 全链路预算核查）。规范见 `references/budget-spec.md`，配置单一真源 `_meta.json` 的 `budget` 段。
- **tri-cost 定位演进**：审计（COST_AUDIT，账房层：观测与评估）与优化（COST_OPTIMIZE，节流执行层：主动省 token 并量化前后对比）互补——先用审计找到高消耗节点，再用优化对对应载荷/输出执行方法论并出前后 token 与内容准确性对比验证收益。
- **本文件作为方法底座**：§七 / §八的具体动作被 `references/cost-model.md` 的建议类型、SKILL.md 的「降本增效建议类型速查」与「token 节省方法论执行（COST_OPTIMIZE · active）」小节共同引用，使建议更具体、且可一键执行。
- **不引入新运行时义务**：tri-cost 不打包 Go 二进制；压缩为方法论级规则摘要与风格压缩，非 caveman 的确定性字节级压缩器。
- **合规**：仅引用 MIT 的 `skills/caveman/SKILL.md` 与公开设计文档的方法，不复制 BSL 的 engine / proxy 源码，注明来源（见顶部）。
- 置信度：中；依据：推断 inferred；来源：基准报告 §9 / §10。

---

## 附录：置信度与依据

| 结论 | 置信度 | 依据 | 来源 |
|------|--------|------|------|
| caveman 是 skill + proxy / engine 双结构 token 削减工具 | 高 | 事实 known | 基准报告 §1 / §3 |
| caveman 与 tri-cost 互补（节流 vs 账房） | 中 | 推断 inferred | tri-cost SKILL.md + 基准报告 §10 |
| 完整能力不可蒸馏为单个 Markdown skill | 高 | 推断 inferred | 基准报告 §9.2 |
| 方法论层可蒸馏 | 高 | 推断 inferred | 基准报告 §9.1 |
| BSL 引擎不可在 tri-xxx 再许可 | 高 | 事实 known | 基准报告 §1.3 |
| 13 类载荷分类法可转译为摘要规则 | 高 | 推断 inferred | 基准报告 §9.1 / §3.2 |
