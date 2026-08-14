# Changelog

All notable changes to tri-music will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.2.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源 `tri-intent/references/version-gate.md`，消除各 skill 内的重复表述
- frontmatter version `2.2.0` → `2.2.1`

## [2.2.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `2.1.1` → `2.2.0`

## [2.1.1] - 2026-08-02

### 新增

- **`## 质量标准` 章节**：定义 Hook 命中（6 维 ≥5 维）/ 反罐头自检（8 维全过 + 抽象词黑名单）/ 平台矩阵覆盖（≥2 平台 × 四要素）三维硬指标，含验证方式与不达标返工路径；版权红线列为一票否决项
- **`tests/tri-music-full-testcases.md`**：全场景全能力测试用例集（68 例，A–H 八组能力清单），覆盖歌词创作、5 套 AI 工具提示词、5 平台发布矩阵、Hook 公式命中、反罐头自检、依赖检测四态与版权红线

### 变更

- **`## 文件结构` 更名为 `## 目录结构`**：与 tri-mm/tri-loop/tri-review 等同族 skill 章节命名对齐，并在树中补入 `tests/` 一行
- **README 版本对齐**：frontmatter `version` 由 `2.0.0` 更正为 `2.1.1`，「当前版本 / 上一版本」同步更新为 2.1.1 / 2.1.0，消除与 SKILL.md、CHANGELOG 的版本漂移；README 目录树补入 `tests/`

## [2.1.0] - 2026-07-30

### 新增

- **`.tribro/music/` 链路文档落盘**：与 tri-intent（`.tribro/snapshots/`）、tri-action（`.tribro/actions/`）、tri-loop（`.tribro/loops/`）、tri-mm（`.tribro/multimedia/`）保持一致
- **落盘规则 section**：新增完整落盘规则章节，定义 `.tribro/music/<命名>/result.md` 执行结果落盘路径
- **执行结果落盘**：tri-music 执行结果落盘于 `.tribro/music/<命名>/result.md`，含全案摘要 + 6 维 Hook 命中声明 + 反 AI 罐头自检结果 + 版权红线合规声明 + 引用

## [1.0.0] - 2026-07-27

### 首次发布（基于《爆款音乐深度解析报告》12 项优化建议全量吸收）

### Added

- **三态依赖检测（模式 A/B/C）**：新增上游 tri-intent 依赖检测逻辑，与 tri-coding/tri-content/tri-fix 保持一致
- **6 维 Hook 公式模板**：`templates/hook-formula.md`（旋律/节奏/歌词/编曲/结构/情绪 + 错误回避）
- **微情绪意象库**：`templates/lyrics-micros-emotion.md`（6 大情绪场景 + 60+ 具体意象）
- **5 平台发行策略矩阵**：`templates/platform-matrix.md`（抖音/汽水音乐/网易云/QQ 音乐/酷狗/酷我）
- **5 阶段发行 SOP**：`templates/release-sop.md`（预热→首发→加投→维护→复盘）
- **反 AI 罐头 8 维度自检清单**：`checklists/anti-can-music.md`
- **反 AI 罐头通用基底 Prompt**：`prompts/anti-can.md`（所有 AI 工具自动追加）
- **海绵音乐 Prompt 模板**：`prompts/haimian.md`（中文为主，含模式一/模式二双模板）
- **Suno Prompt 模板**：`prompts/suno.md`（英文为主，适配国际化发行）
- **Udio Prompt 模板**：`prompts/udio.md`（专业编辑+多轨混音控制）
- **Melo Prompt 模板**：`prompts/melo.md`（多模态输入 + 风格迁移）
- **音潮 Prompt 模板**：`prompts/yinchao.md`（影视/游戏/广告/单曲四大场景）
- **README.md**：使用说明与扩展指南

### Changed（变更）

- **SKILL.md 全文重写**：从 v1.0 的"通用音乐创作指引"重构为 v2.0 的"基于快照的工作流 + 核心方法论"双层结构
- **强制执行契约新增 5 条**：6 维 Hook 强制校验 / 微情绪意象库强制引用 / 多 AI 工具适配 / 多平台发行 / 反 AI 罐头自检
- **输入依赖校验从 2 字段扩到 4 字段**：增加「目标受众」「目标平台」两个必填字段
- **职责边界明确化**：与 tri-intent/tri-content/tri-mm 的职责划分清晰定义
- **可扩展性增强**：新增 AI 工具 / 新增平台 / 新增 Hook 维度 / 新增反 AI 罐头指令均无需修改 SKILL.md

### Deprecated（弃用）

- v1.0 中的「无结构创作指引」已弃用，全部由 6 维 Hook 公式 + 微情绪意象库替代
- v1.0 中的「单平台思维」已弃用，全部由 5 平台差异化策略矩阵替代
- v1.0 中的「无 AI 工具适配」已弃用，全部由 5 套 Prompt 模板替代

### Removed（移除）

- 无（v1.0 原文备份至 `legacy/v1.0-SKILL.md` 供回溯）

### Fixed（修复）

- v1.0 中缺少「微情绪意象库」导致副歌空泛（"孤独""爱""梦想"四件套）问题
- v1.0 中缺少「反 AI 罐头基底」导致多用户产出同质化问题
- v1.0 中缺少「平台差异化策略」导致全平台一刀切问题
- v1.0 中缺少「发行 SOP」导致有作品无运营问题

### Security（安全）

- 新增「版权自查小卡片」工具：覆盖 5 大高风险场景（旋律撞车/采样侵权/AI 训练数据/封面字体/平台签约）
