# Changelog

本文件记录 tri-cache skill 的版本变更历史。

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

- frontmatter version `1.0.1` → `1.1.0`

## [1.0.1] - 2026-08-01

### 修复

#### 目录结构图清理（合规）
- 删除 SKILL.md「目录结构 / 配套文件」中列出的 `LICENSE` / `.gitignore` 条目，遵循《tri-skill-规范与生成指南》§4.1「禁止生成的文件」硬约束（许可证仅由 frontmatter `license` 字段声明，忽略策略由仓库统一管控）。
- 本版本无功能变更，仅文档合规修正（PATCH）。

## [1.0.0] - 2026-08-01

### 新增

- **初始版本**：tri-cache 横向基础设施型 skill，为 tri-xxx 家族全家族提供缓存与检索能力
- **三种工作模式**：CACHE_WRITE（被动写，hook 触发）/ CACHE_LOOKUP（主动检索）/ CACHE_ADMIN（管理命令）
- **三层存储架构**：内存热层（LRU dict，<1ms）/ SQLite 温层（WAL 索引，1-5ms）/ Markdown 冷层（按月分桶，5-20ms）
- **内容指纹去重**：提问归一化后 SHA-256 前 16 位作 cache_key，相同提问不重复写原文，仅更新 hit_count
- **差异化 TTL**：按意图 L2 设置不同 TTL（I01-I02 30 天 / I03-I05 7 天 / I06-I10 1 天 / I11-I12 与 I17-I20 与 M01-M04 不缓存）
- **命中复用策略**：按意图差异化复用（I01-I02 直接复用 / I03-I05 参考注入标注「请核实」/ I11-I12 不缓存）
- **失效四策略组合**：TTL 过期 + LRU 淘汰（容量超限至 80% 水位）+ 事件驱动失效（文件变更标记 stale）+ 手动失效（key/session/intent 批量）
- **隐私过滤**：写入前扫描密钥模式（password/token/secret/api_key/sk-/AKIA/PRIVATE KEY），命中脱敏 `***REDACTED***`，敏感度过高跳过缓存
- **双轨索引**：SQLite 主索引（7 索引覆盖组合查询）+ JSONL 增量日志（容灾，可重建 index.db）
- **上游依赖检测三态逻辑**：快照模式 / 引导安装 / 降级模式（退化为纯内存 LRU 缓存，声明降级精度低）
- **schema 与模板**：`schemas/cache-entry.schema.md` 定义 SQLite 表结构与 Markdown frontmatter；`templates/entry.md` 原文模板；`templates/meta.json` 配置模板
- **质量标准八维**：写入完整性 / 去重正确性 / 检索延迟 / 失效准确性 / 隐私安全 / 容量合规 / 索引一致性 / 复用建议准确
