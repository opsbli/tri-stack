# Changelog

All notable changes to this skill will be documented in this file.


## [1.2.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.1.2` → `1.2.0`

## [1.1.2] - 2026-08-02

### 变更

- **`### 五、质量标准` 提升为 `## 质量标准`**：与 §落盘规则 同级，消除「二级章节下挂三级质量标准」的层级错位
- **`## 核心能力` 与 `## 处理流程` 去重合并**：`## 处理流程` 确立为 scaffold/bootstrap 全链路的唯一权威定义；`## 核心能力` 六项能力压缩为索引表（一句话定义 + 权威定义位置），删除重复叙述，SKILL.md 由 402 行降至 352 行
- **处理流程补入被合并的权威内容**：新增 `### Charter 5 项输入`（含默认值与收集策略）、`### 真实测试运行`（小规模动作示例 + dry run 规则）、`### 记录格式（两个必需输出）`（Timeline 一行格式 + LOG.md 条目格式）三个子节
- **§交付产物 · LOG.md 条目结构** 改为指向 §处理流程 · 记录格式，避免格式两处维护

### 新增

- **`tests/tri-loop-full-testcases.md` 补齐 frontmatter**（name/description，标注被测版本 v1.1.2）与 `## 零、能力清单`（A–H 八组共 40 个能力点），并给出「能力组 → 测试组」映射，使 47 个既有用例可回溯覆盖率

## [1.1.1] - 2026-07-30

### 变更

- **落盘规则标题层级统一**：`### 五、落盘规则` 提升为 `## 落盘规则`（二级标题），与 tri-action/tri-content/tri-plan 等 10 个 skill 保持一致
- **子章节编号顺延**：`### 六、质量标准` 顺延为 `### 五、质量标准`（消除落盘规则移出后的编号断号）

## [1.1.0] - 2026-07-30

### Added
- 新增 `templates/result.md` 执行结果模板（8 章节：Loop Charter + Substrate 状态 + 测试运行摘要 + Artifact 记录 + 缺失项 + 如何再次运行 + 引用 + 自检）
- tri-loop 链路文档统一落盘到 `.tribro/loops/<命名>/result.md`，与 tri-intent（`.tribro/snapshots/`）、tri-action（`.tribro/actions/`）保持一致
- 新增落盘规则 section，明确 tri-loop 链路文档与知识库内容文件的路径分离
- 阶段速查表新增第 8 阶段「执行结果落盘 result.md」
- 质量标准新增「执行结果落盘」和「.tribro 目录一致」两个维度
- 新增 TG-11 测试组（4 个用例）：result.md 落盘路径、结构完整性、与知识库分离、.tribro 目录一致性
- 自动化测试新增 TG-10（20 个用例）：.tribro/loops/ 路径引用、落盘规则、result.md 结构、模板内容验证

### Changed
- SKILL.md 产物结构规格中 result.md 引用 `templates/result.md` 模板
- 目录结构新增 `templates/result.md`
- 测试用例总数从 43 增至 47

## [1.0.0] - 2026-07-30

### Added
- 初始版本，蒸馏自 new-loop 开源项目
- 6 大核心能力：Substrate Bootstrap、Loop Charter 收集、Loop README Scaffold、真实测试运行、Timeline + LOG.md 记录、回报
- 三态依赖检测：Mode A（快照模式）、Mode B（引导安装）、Mode C（降级模式）
- 强制执行契约 5 条（含最小化原则门禁规则）
- 9 个模板文件：loop-readme、architecture、log、claude-template、claude-kb-section、signals-readme、docs-readme、domains-readme、knowledge-setup
- 全场景测试用例
- 支持 tri-intent 下游路由（I14 · loop/domain 创建子类）
- 支持独立运行（降级模式）
