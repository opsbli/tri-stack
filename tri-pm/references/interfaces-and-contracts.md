---
name: interfaces-and-contracts
description: pm-skills 的重要接口契约与设计决策——清单 schema、frontmatter 契约、命令-技能引用协议、校验器 CLI 接口。对照分析报告 §3 / §5 / §6。
---

# 接口契约与设计决策

> **蒸馏基准**：分析报告 §3.2–3.3（分层与依赖）、§5（代码质量）、§6（可维护性与扩展性）、§2.3（设计哲学）。
> grep 检索模式：`契约` / `schema` / `frontmatter` / `引用协议` / `CLI` / `退出码` / `设计决策`

---

## 一、清单 Schema 接口

### L0 市场清单 `marketplace.json`

```jsonc
{
  "name": "pm-skills",
  "version": "2.1.0",                 // 与全部 plugin.json 及 CHANGELOG 最新标题强一致
  "description": "...",               // 含「N 个技能 / M 条工作流 / K 个插件」计数句，由测试校验
  "owner": { "name": "...", "email": "...", "url": "..." },
  "plugins": [
    { "name": "pm-<domain>", "description": "...", "source": "./pm-<domain>", "category": "product-management" }
  ]
}
```

### L1 插件清单 `plugin.json`

必需字段：`name` / `version` / `description`；推荐字段：`author`（含 name/email/url）/ `keywords` / `homepage` / `license`。
`name` **MUST 等于所在目录名**（由校验器强制）。

## 二、frontmatter 契约（渐进式披露的载体）

| 载体 | 必需字段 | 推荐字段 | 约束 |
|------|---------|---------|------|
| `SKILL.md` | `name` / `description` | 触发短语 | `name` MUST == 目录名；`description` 建议含触发语义（如 “Use when …”） |
| `commands/*.md` | `description` | `argument-hint` | 命令使用单一 `$ARGUMENTS` 占位符 |

**渐进式披露原则**：frontmatter 常驻加载（故保持精简），细节放正文（触发时才加载）。这是控制上下文开销的核心设计。

**可见性分层**（决定每处描述写给谁看）：

| 位置 | 可见于 |
|------|--------|
| `marketplace.json` description | 市场浏览器 |
| `plugin.json` description | 插件列表 |
| `SKILL.md` description | 技能列表 + 自动加载判定 |
| command `description` + `argument-hint` | 输入 `/` 时的命令提示 |
| 仓库 `README.md` | 仅 GitHub，运行时不加载 |

## 三、命令 → 技能引用协议

- **协议形式**：命令正文以 `**<skill-name>** skill` 形式引用技能。
- **校验机制**：`validate_cross_references` 用正则提取此类引用，校验其确实存在于**同插件**内；跨插件引用被检出为 warning。
- **设计意图**：因为插件独立安装，跨插件硬引用会断链，故只在同一插件内允许硬引用。
- **跨插件衔接**：改用**自然语言**建议（如「要不要我设计增长闭环？」）。

## 四、校验器 CLI 接口

```
python validate_plugins.py [base_path]
```

- `base_path` 缺省为脚本所在目录；扫描依据是「目录下含 `.claude-plugin/`」。
- **退出码**：`0` = 无 error；`1` = 存在 error。warning 不影响退出码。
- **结论三级**：`error`（MUST 修，影响退出码）/ `warn`（SHOULD 修）/ `info`（FYI）。

**配套测试接口**：

```
python -m unittest discover -s tests
```

## 五、可复用设计决策

| 决策 | 内容 | 迁移价值 |
|------|------|---------|
| 框架与流程分离 | 技能=名词（知识）、命令=动词（流程） | 高：知识多处复用，流程独立演进 |
| 独立安装优先于硬链 | 禁止跨插件硬引用 | 高：保证任一模块可单独抽取 |
| 渐进式披露 | frontmatter 精简、细节下沉 | 高：控制上下文成本 |
| 单一事实源 | CLAUDE.md（指导）/ CHANGELOG.md（发布） | 高：杜绝文档漂移 |
| 版本强一致 | 全仓同版本，测试强制 | 高：消灭版本碎片 |
| 计数三处同步 | README 头条 / 每插件摘要 / 插件 README 段头 | 中：由测试兜底，防机械遗漏 |
| 校验只保结构 | 不校验产出内容质量 | 中：**迁移时应补内容质量回归**（见 baseline） |
| 被审对象视为不可信输入 | 审计命令将代码/注释/文档中的指令视为数据 | 高：防提示注入，审计类能力必留 |

### 待改进项（蒸馏时应修正，报告 §5.4）

| 项 | 说明 |
|----|------|
| 自写 YAML 解析器 | 仅支持扁平 key-value，不支持嵌套/多行/列表；脆弱点 |
| `$ARGUMENTS` 漂移 | 实测 10/68 个 SKILL.md 使用了 `$ARGUMENTS`，与「技能不需要占位符」的自述规则不一致（功能可用，属一致性瑕疵） |
| 无内容质量回归测试 | 只校验结构，不校验产出质量 |
| 外链衰减 | `Further Reading` 指向外部文章，存在失效与版权风险 |
