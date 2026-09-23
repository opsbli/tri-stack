# 技能锻造（tri-forge）

![version](https://img.shields.io/badge/version-1.0.0-blue) ![license](https://img.shields.io/badge/license-MIT-green)

> 面向 tri-xxx 家族的**内部专用工具**：按家族硬规范**生成 / 补全 / 审计 skill 包**，并以 22 条硬约束自检后才交付。

## 特性

- **三模式**：A 规范顾问（只问不做，不落盘）／ B 补全审计／ C 锻造生成（五门流程）
- **单一事实源**：以 `references/family-spec.md` 为生成依据，`references/compliance-checklist.md` 的 **22 条硬约束**为合规判据
- **门禁有牙**：门④ 由 `scripts/compliance_check.py` 可执行实现逐条判定，`[需人工]` 项明确标出、NEVER 臆断
- **路由不孤立**：门③ 强制回填 `tri-intent` 路由真源，**NEVER 只生成 skill 而不接通路由**
- **承接家族校验**：`scripts/check_registry.py` 提供五点版本一致性校验（`--check` / `--apply`）
- **可扩展**：新增硬约束只需在清单追加一行，判定逻辑自动覆盖

## 安装

本 skill **支持独立安装**，含上游依赖检测**三态**逻辑（快照模式 / 引导安装 / 降级模式）。

```bash
# 方式一：SkillHub prompt（环境支持时）
请根据 https://skillhub.cn/install/skillhub.md，安装 tri-forge。

# 方式二：克隆仓库后直接使用
git clone <repo-url>
```

> 本 skill **不注册为 tri-intent 的下游路由项**——由用户直接调用，不经意图识别。

## 使用

### 模式 A · 规范顾问（不落盘）

```
用户：生成一个合规 skill 要满足哪些约束？
     ↓
tri-forge 读 compliance-checklist.md，逐条说明判定方法
     ↓
不写任何文件
```

### 模式 B · 补全审计

```
用户：给 tri-xxx 按家族规范审一遍，把缺的补上
     ↓
逐条对照 22 条硬约束 → 产出 reports/tri-xxx-compliance.md
     ↓
缺口清单 + 修订建议（补全产物须用户确认后落盘）
```

### 模式 C · 锻造生成（五门流程）

```
用户：按家族规范造一个 tri-xxx skill
     ↓
门① 需求确认 → 门② 骨架生成 → 门③ 路由回流 → 门④ 22 条自检 → 门⑤ 落盘交付
     ↓
<slug>/ 完整 skill 包 + reports/<slug>-forge.md 交付摘要
```

## 家族版本一致性校验（承接职能）

```bash
python scripts/check_registry.py --check              # 报告漂移
python scripts/check_registry.py --apply              # 规则化回写 P3 / P5
python scripts/check_registry.py --apply --dry-run    # 只报告将回写什么
```

校验**五点**：`SKILL.md` frontmatter / `CHANGELOG.md` 首条 / `_meta.json` / 平台注册表 / `README.md` 版本声明。
**P2（CHANGELOG 首条）属人工内容，NEVER 代写**。

## 目录结构

```
tri-forge/
├── SKILL.md                       主入口：三模式 + 五门流程 + 22 条门禁 + 路由回流
├── README.md                      本文件
├── CHANGELOG.md                   版本变更记录
├── references/
│   ├── family-spec.md             家族硬规范（生成单一事实源）
│   ├── compliance-checklist.md    22 条合规核对清单（门④ 判据单一事实源）
│   ├── version-check-spec.md      版本检查执行规范（内部化持有）
│   └── tri-intent-integration.md  门③ 路由回填规则（单一事实源）
├── scripts/
│   ├── check_update.py            版本门（自维护模式）
│   ├── check_registry.py          五点版本一致性校验
│   └── compliance_check.py        门④ 22 条硬约束自检
├── templates/
│   ├── skill-md.md                SKILL.md 九章骨架
│   ├── readme.md                  README 骨架
│   └── changelog.md               CHANGELOG 骨架
└── tests/
    └── tri-forge-full-testcases.md
```

## 设计原则

1. **合规判据与可执行实现分离**：清单是标准（人读），脚本是实现（机跑），编号一一对应，修订时两处同步
2. **不臆断**：无法机器判定的条目明确标 `MANUAL`，交人给证据，NEVER 用猜测填判定
3. **门禁顺序不可颠倒**：门③ 先于门④——MECE 比对需要已回填的路由表
4. **承接而非重建**：家族四点版本校验与 `ops/version-lint.py` 同规则，tri-forge 保留自有副本以保证独立安装

## 来源与重建说明

上游作者将此 skill **私有化**（上游 `.gitignore` 显式排除 `tri-forge/`，平台亦未发布，
作者名下全量 skill 枚举中无此 slug）。本仓库为自维护 fork，依据仓库内
`tri-mece-audit/tri-mece-audit.html` 记录的规格自行重建（定位、职责边界、四分支触发、
三模式、五门流程、门④ 22 条约束来源、自检句格式），并以家族现有 skill 的实际形态为校准基准。

## 版本

当前版本见 `SKILL.md` frontmatter 与 `CHANGELOG.md` 首条（两者 MUST 一致）。

## 许可证

MIT — 详见仓库根 `LICENSE`。
