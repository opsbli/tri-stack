# Changelog

本文件记录 tri-ppt（tri-mm 演示文稿类子SKILL）的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.2.0] - 2026-08-11

### 新增（全流程自动化升级）

- **阶段一 · 全网素材采集**：从用户提问/主题出发，用 WebSearch/WebFetch 采集文字与图表数据、用 ImageGen 生成主题配图，整理为 `materials.md` + 机器可读 `materials.json`（模板见 `references/materials-template.md`）
- **审计门① · 素材审计**：素材库提交用户审计，通过/补充/剔除后方可进入设计
- **阶段二 · 大纲 + 逐页动效方案设计**：在既有 8 维设计基础上新增「逐页动效（转场）方案」，素材映射每页，产出 `design.md` + `design.json`（模板见 `references/design-template.md`，含动效目录表）
- **审计门② · 设计审计**：大纲 + 动效方案提交用户审计，支持多轮迭代直至通过
- **阶段三 · 确定性生成**：新增 `scripts/build_pptx.py`（python-pptx），按 design.json + materials.json 生成精美 PPTX，支持 9 种版式、主题色、原生图表、逐页转场（oxml 注入）
- **版权安全**：外采图片 MUST 可商用，否则改 ImageGen 生成；来源全程可追溯

### 变更

- SKILL.md 升级为全流水线结构（两态上游依赖检测不变，仍为 I15·PPT 子SKILL，MECE 零冲突）
- 大块模板/目录表移 `references/`（素材模板、设计+动效模板），正文仅留指针
- frontmatter version `1.1.1` → `1.2.0`

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

- frontmatter version `1.0.0` → `1.1.0`

## [1.0.0] - 2026-08-02

### 新增

- 初始版本：tri-mm 的演示文稿类子SKILL，处理 I15 演示文稿意图
- 8 维演示文稿设计方法论：主题受众/结构页数/每页大纲/版式/配色字体/图表图示/动画转场/交付格式
- 大纲 design.md 模板（每页版式/标题/要点/动画 表）
- 设计方案确认门：先大纲方案确认，确认后再生成
- 链路文档落盘 `.tribro/multimedia/ppt/<命名>/`（design.md + result.md）
