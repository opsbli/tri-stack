# Changelog

本文件记录 tri-translate skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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

#### 渐进披露与一致性（全量评审优化）
- 19 类不译规则集正则表从 SKILL.md 内联移入 `references/no-translate-rules.md`（单一事实源，grep 检索），SKILL.md 保留摘要+指针。
- `### 五、质量标准` 提升为独立 `## 质量标准` 二级标题（对齐 family-spec §3.10）。
- `## 目录结构` 补登 `references/` 与 `tests/`，与磁盘实况对齐。
- `## 职责边界` 补充 tri-content I08 委派决策反向指针（委派条件 a–d + `alignment.md`/`对照表.md` 二选一，杜绝双份产出）。
- 测试集 frontmatter 版本联动至 v1.0.2。

## [1.0.1] - 2026-08-01

### 修复

#### 目录结构图清理（合规）
- 删除 SKILL.md「目录结构 / 配套文件」中列出的 `LICENSE` / `.gitignore` 条目，遵循《tri-skill-规范与生成指南》§4.1「禁止生成的文件」硬约束（许可证仅由 frontmatter `license` 字段声明，忽略策略由仓库统一管控）。
- 本版本无功能变更，仅文档合规修正（PATCH）。

## [1.0.0] - 2026-08-01

### 新增

- **初始版本**：横向方法论型翻译 skill，为 tri-xxx 家族提供"意译优先 → 直译次之 → 不译兜底"三策略分层翻译能力
- **三策略分层方法论**：意译（达旨）→ 直译（信）→ 不译（玄奘五不翻现代映射），源自严复信达雅 + 奈达功能对等 + 李长栓理解表达变通 + 玄奘五不翻
- **19 类不译规则集**：路径/代码块/行内代码/命令行/API/URL/域名/邮箱/配置键/环境变量/版本号/SHA/品牌名/商标/首字母缩写/技术标识符/数字单位/日期时间，正则模式预扫描占位
- **隔离区占位法**：两步占位法（预处理占位 → 翻译 → 还原），杜绝 LLM"贴心地"重新格式化代码与 markup
- **三层术语表**：Priority A 不可译（品牌名/商标）/ Priority B 已批准译法（屏蔽同义词）/ Priority C 推荐译法
- **MQM Core 4 维 + Hallucination 子维质量自检**：Accuracy / Fluency / Terminology / Design + Hallucination，Critical+Major 错误 0 容忍
- **三个独立调用接口**：TRANSLATE_EXECUTE（深度翻译）/ TRANSLATE_QUERY（术语查询）/ TRANSLATE_ADMIN（术语表/规则管理）
- **翻译策略矩阵**：6 场景（技术文档/营销/UI/学术/对话/法律）× 主策略/退守/不译要素
- **三态依赖检测**：快照模式（读取 tri-intent §三 上下文增强语境感知）/ 引导安装 / 降级模式（自构造等价输入声明精度低）
- **委派关系**：作为 tri-content I08 的可选委派目标，不主动接管，不改动 tri-content
- **配套文件**：SKILL.md / README.md / CHANGELOG.md / .gitignore / schemas（glossary + never-translate）/ templates（meta.json + glossary.json + never-translate.json + deliverable.md + alignment.md + quality.md + style-examples/）/ tests（全场景测试用例）
