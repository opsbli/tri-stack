# 变更日志

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

> **一致性硬约束**：本文件首个 `## [x.y.z]` MUST 与 `SKILL.md` frontmatter 的 `version` 相等，
> 且 MUST 为本文件的最大版本。违反即触发门④ 第 11 条 FAIL。

## [1.0.5] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.0.4] - 2026-09-24

### 变更

- **版本门节收敛为瘦指针 STUB**：`## 版本检查与更新机制` 由 35 行全量版收敛为 14 行（执行方式 + 真源指针），移除已失效的**远端 skillhub 内联细则**（端点解析 / 四态判定 / 升级流程 / SemVer 比较算法）。依据 `references/version-check-spec.md` §六（该节须 ≤30 行、禁内联细则）；本仓库已转自维护 fork（`scripts/check_update.py` 内置 `SELF_MAINTAINED = True`，完全跳过远端请求），原节描述的行为**永不执行**。
- **强制执行契约 §0 同步修正**：版本门措辞由「连接 skillhub 校验版本，非最新版 MUST 自动执行 `skillhub upgrade <slug>` 升级」改为「运行 `scripts/check_update.py` 做本地版本一致性校验，本仓库为自维护 fork、不做远端比对」，消除 prompt 层与脚本实际行为的直接矛盾。
- 节内 **skill 专属职能**（`scripts/check_registry.py` 家族级 P1–P5 校验）原样保留，未被本次收敛影响。
- 非功能性变更（文档口径），无行为变更。

## [1.0.3] - 2026-09-24

### 变更

- **§1.5 登记表更新**：`evolve-hook` 实现状态由「❌ 未交付」改为「✅ pi（形态 B）已交付 · ❌ 形态 A/C 未交付」，并登记其入参契约。

## [1.0.2] - 2026-09-24

### 变更

- **新增 hook 依赖契约 `family-spec.md` §1.5**：声明即须给降级路径 + 登记 + 命名 + `hooks/` 目录名纪律；登记 4 个 hook（实现数 0）。`compliance-checklist.md` 第 14 条由「四类」扩为「五类」（含 hook 缺失）。

## [1.0.1] - 2026-09-24

### 变更

- **分支收窄为编程工作流专线（22 skill）**：清理对已移除 skill 的交叉引用——职责边界表 / 不由本 skill 处理表的对应行改为「本分支未包含（原 tri-xxx）」或删除；已删的委派关系与相邻边界说明同步失效。非功能性变更（文档）。

## [1.0.0] - 2026-09-23

### 新增

- **首版发布**：三模式技能锻造工具（A 规范顾问 / B 补全审计 / C 锻造生成）
- **五门流程**：门① 需求确认 → 门② 骨架生成 → 门③ 路由回流 → 门④ 合规自检 → 门⑤ 落盘交付
- **家族硬规范单源**：`references/family-spec.md`（骨架清单 + 12 条家族硬约束 + 章序表 + 待登记项）
- **22 条合规核对清单**：`references/compliance-checklist.md`（12 家族 + 8 增强 + 1 安装 + 1 版本检查去重）
- **门④ 可执行实现**：`scripts/compliance_check.py`，逐条判定并明确标出 `MANUAL` 项
- **门③ 路由回填规则单源**：`references/tri-intent-integration.md`（含回填顺序与优先级仲裁）
- **五点版本一致性校验**：`scripts/check_registry.py`（`--check` / `--apply`）
- **三方模板**：`templates/skill-md.md` / `readme.md` / `changelog.md`
- **测试用例**：`tests/tri-forge-full-testcases.md`（含 22 条硬约束自检用例）

### 设计取舍

- **不注册为 tri-intent 下游**：定位为内部专用工具，由用户直接调用（与原上游设计一致）
- **承接而非重建版本校验**：五点校验规则与 `ops/version-lint.py` 同源，但保留自有副本以保证独立安装
- **P2 不代写**：`CHANGELOG.md` 首条属人工内容，`--apply` 只规则化回写 P3 / P5

### 来源说明

本 skill 系**自维护 fork 自行重建**。上游作者将其私有化：上游 `.gitignore` 显式排除 `tri-forge/`，
平台 `/api/v1/skills/tri-forge` 与 `/api/v1/download?slug=tri-forge` 均 404，
作者名下全量 skill 枚举中亦无此 slug。重建依据为仓库内 `tri-mece-audit/tri-mece-audit.html`
记录的规格（定位、职责边界表、四分支触发、三模式、五门流程、门④ 22 条约束来源、自检句格式）。
