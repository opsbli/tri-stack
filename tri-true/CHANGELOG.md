# Changelog

本文件记录 tri-true skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.1.2] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手一般咨询常规作答、业务内容生成、翻译转换本身，只承接委派而来的高风险幻觉消除与 Hallucination 维度验证。

## [1.1.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源 `tri-intent/references/version-gate.md`，消除各 skill 内的重复表述
- frontmatter version `1.1.0` → `1.1.1`

## [1.1.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.0.2` → `1.1.0`

## [1.0.2] - 2026-08-02

### 重构

#### 渐进披露与版本单一源（全量评审优化）
- 删除 SKILL.md `## 版本` 章（与 CHANGELOG 职责重复，是版本漂移根因）；`## 依赖与兼容` 的版本行改为指向 `CHANGELOG.md` 单一事实源。
- `### 五、质量标准` 提升为独立 `## 质量标准` 二级标题（对齐 family-spec §3.10）。
- 知识类型联合判定矩阵 + 分类判定规则移入 `references/knowledge-types.md`（单一事实源，grep 检索），SKILL.md 保留概览与铁律。
- 新增 `scripts/confidence_calc.py`：三层置信度综合公式 `0.4×VC+0.3×SC+0.3×CC` + ECE/Brier 校准估计器（确定性逻辑下沉脚本）。
- `## 目录结构` 补登 `references/` / `scripts/` / `tests/`，与磁盘实况对齐。
- 测试集 frontmatter 版本联动至 v1.0.2。

## [1.0.1] - 2026-08-01

### 修复

#### 目录结构图清理（合规）
- 删除 SKILL.md「目录结构 / 配套文件」中列出的 `LICENSE` / `.gitignore` 条目，遵循《tri-skill-规范与生成指南》§4.1「禁止生成的文件」硬约束（许可证仅由 frontmatter `license` 字段声明，忽略策略由仓库统一管控）。
- 本版本无功能变更，仅文档合规修正（PATCH）。

## [1.0.0] - 2026-08-01

### 新增

- **初始版本**：横向方法论型消除幻觉 skill，为 tri-xxx 家族提供"置信度评估 + 事实源验证 + 多模型多方事实源交叉验证 + 自我反思修正"四道防线的幻觉消除能力
- **四道防线架构**：① 置信度评估 → ② 事实源验证 → ③ 多模型交叉验证 → ④ 自我反思修正，层层拦截；源自 Cossio 2025 数学不可避免性 + Yang 2024 verbalized confidence + Lewis 2020 RAG + Wu 2026 Council Mode + Shinn Reflexion 古今融通
- **三层置信度评估**：Verbalized Confidence（VC 直接自评）+ Self-Consistency（SC N 次采样一致度）+ Calibrated Confidence（CC 基于 ECE 反推校准系数 k 修正过度自信），综合公式 `Confidence = 0.4×VC + 0.3×SC + 0.3×CC`
- **四级信源分级**：T1 权威事实类（1.0）/ T2 权威观点类（0.8）/ T3 一般参考类（0.5）/ T4 待验证类（0.2），可信度加权 `Final = α×Relevance + β×Credibility + γ×Freshness`，句级引用归因（ReClaim 模式）
- **异构多模型交叉验证**：≥2 家供应商 + ≥1 开源 + 不同架构家族，UAF 加权融合 `final = argmax(Σ weight_i × confidence_i × agreement_i)`，强共识（全一致+均≥0.7）/ 弱共识（≥2/3 一致）/ 分歧三态判定
- **闭环自我反思修正**：CoVe（主张→验证查询→证据检索→修订）→ Reflexion（thought/answer/confidence 结构化反思）→ Critique-Refine（核查员-修订员多阶段迭代），最多 3 轮
- **人审兜底机制**：critical 风险 + 置信度 < 0.8 强制人审，高风险操作（删除/发布/资金）双人审；综合置信 < 0.5 且无 T1/T2 拒答或列多答案
- **幻觉类型分流**：Factuality（事实性，走防线二事实源验证）/ Faithfulness（自洽性，走自洽性检测），NEVER 混淆处理
- **三个独立调用接口**：VERIFY_EXECUTE（深度验证）/ VERIFY_QUERY（历史查询）/ VERIFY_ADMIN（信源/校准/模型池管理）
- **隐私过滤与成本控制**：第三方模型调用前扫描密钥模式脱敏，敏感度过高（≥3 处）不外传；单任务多模型调用上限 5 次，超限降级为单模型 + 自反思
- **三态依赖检测**：快照模式（读取 tri-intent §三 上下文增强风险判定与领域适配）/ 引导安装 / 降级模式（自构造等价输入声明精度低）
- **委派关系**：作为 tri-ask/tri-content 等下游 skill 的可选委派目标，不主动接管，不改动调用方
- **配套文件**：SKILL.md / README.md / CHANGELOG.md / .gitignore / schemas（verify-task + source + model）/ templates（meta.json + sources.json + calibration.json + models.json + verify.md + sources.md + alignment.md + confidence.md + revisions.md + quality.md）/ tests（全场景测试用例）
