---
name: workflows-and-execution
description: pm-skills 的执行流程——命令链范式、校验器代码执行流程、测试门控流程，以及向 WorkBuddy 的翻译映射。对照分析报告 §3.4 / §7。
---

# 执行流程与翻译映射

> **蒸馏基准**：分析报告 §3.4（数据流）、§5（代码质量）、§7（可行性分析）。
> grep 检索模式：`命令链` / `校验流程` / `测试门控` / `翻译映射` / `退出码`

---

## 一、命令链范式（L3 编排 L2）

以源项目两条代表性命令为例，提炼可复用的编排范式。

### 范式 A：`/discover` — 四段链式（发散 → 收敛 → 排序 → 验证）

```
Step 1 界定上下文      → 判定 existing / new 双轨
Step 2 头脑风暴（发散） → 调用 brainstorm-ideas-{existing|new}
Step 3 识别假设（批判） → 调用 identify-assumptions-{existing|new}
Step 4 排序假设（聚焦） → 调用 prioritize-assumptions（影响×风险矩阵）
Step 5 设计实验（验证） → 调用 brainstorm-experiments-{existing|new}
Step 6 汇总为发现计划文档
Step 7 自然语言建议下一步
```

**关键编排特征**：

- `existing` / `new` **双轨分支**：同一流程按产品阶段选不同技能对。
- **检查点（checkpoint）**：Step 2 与 Step 4 之后各设一处，用户可重定向、跳过、深入。
- 收尾以**自然语言**建议下一步，NEVER 硬引用其它插件的命令。

### 范式 B：`/write-prd` — 四步式（理解 → 采集 → 生成 → 迭代）

```
Step 1 理解特性      → 接受任意形态输入（特性名/问题陈述/用户请求/模糊想法/上传文档）
Step 2 采集上下文    → 对话式提问 6 类（用户问题/目标用户/成功指标/约束/既有方案/范围偏好）
                       文档已提供的信息直接抽取，只问缺口
Step 3 生成 PRD      → 调用 create-prd 技能，产出 8 段式文档
Step 4 评审迭代      → 提供收敛选项（缩范围 / 预验尸 / 拆用户故事 / 干系人同步）
```

**关键编排特征**：输入形态宽容、缺口驱动提问、生成后主动提供收敛路径。

## 二、校验器代码执行流程（源项目唯一真实代码）

`validate_plugins.py`（Python 标准库，无第三方依赖）：

```
main()
 ├─ win32：包装 stdout 为 UTF-8
 ├─ 定位 base_path（argv[1] 或脚本所在目录）
 ├─ 扫描插件目录（判定依据：目录下存在 .claude-plugin/）
 └─ for 每个插件 → validate_plugin(dir)
      ├─ ① validate_manifest   → plugin.json：必需字段 / name==目录名 / semver /
      │                            author 对象 / keywords 数组 / description 长度
      ├─ ② validate_skill      → 遍历 skills/*/SKILL.md：frontmatter 存在 / 必需字段 /
      │                            name==目录名 / description 质量与触发短语 / 词数区间
      ├─ ③ validate_command    → 遍历 commands/*.md：frontmatter / description /
      │                            argument-hint（推荐）
      ├─ ④ validate_readme     → 插件 README 存在性与预期段落（overview/install/skill/command）
      └─ ⑤ validate_cross_references
                               → 正则提取 `**<name>** skill` 引用，
                                  校验被引技能确实存在于同插件内
 print_report()  → 彩色分级输出（error/warn/info）+ 汇总
 sys.exit(1 if errors > 0 else 0)
```

**设计要点**：

- **三级结论**：`error`（MUST 修）/ `warn`（SHOULD 修）/ `info`（FYI）。只有 error 影响退出码。
- **校验边界**：只保**结构**，不保内容质量（不校验产出的 PRD 是否优秀）。
- **已知脆弱点**：`parse_yaml_frontmatter` 为自写扁平解析器，不支持嵌套、多行值与列表。

## 三、测试门控流程

`tests/` 两个文件构成一致性门控，CI（GitHub Actions，Python 3.11/3.13 双版本）每次 PR/push 运行：

| 文件 | 覆盖 |
|------|------|
| `test_validator.py` | frontmatter 解析器单测（4 例）+ 词数统计单测（1 例）+ **全仓库校验门**（所有插件零 error） |
| `test_consistency.py` | 市场清单 ↔ 磁盘目录一致；**版本唯一同步**（CHANGELOG ↔ marketplace ↔ 全部 plugin.json）；CHANGELOG 标题格式（well-formed/有日期/唯一/降序）；README 计数 ↔ 磁盘（头条 / 每插件摘要 / 插件 README 段头三处）；插件 README 中 `/plugin:command` 引用可解析为真实文件 |

**实测结果**：校验器 9/9 插件 PASS、0 错误 0 警告；测试 15/15 通过。

## 四、向 WorkBuddy 的翻译映射（报告 §7.1）

| 维度 | 源（Claude Code 插件） | 目标（WorkBuddy skill） | 翻译动作 |
|------|----------------------|------------------------|---------|
| 单元 | 9 插件 ×（技能 + 命令） | 路由 skill + 知识包 | 重新聚合为 references |
| 触发 | 话题自动加载 / `/command` 斜杠 | tri-intent 意图路由 / 描述触发 | 触发短语喂给路由 |
| 参数 | `$ARGUMENTS` 占位符 | 对话上下文 / 路由参数 | 替换 |
| 编排 | command 链式调用 skill | skill 内编排步骤 | 重写为流程小节 |
| 代理 | subagent fan-out、`allowed-tools` 只读工具集 | 子代理 + 沙箱只读 | 等价映射 |
| 校验 | `validate_plugins.py` + unittest | 可平移为自带校验 | 平移 |

### 保真度（报告 §7.3）

| 能力类别 | 保真度 | 处理 |
|----------|:------:|------|
| 框架知识（PRD/画布/矩阵等） | 100% | 直接承载，剥离 Claude 专有语法 |
| 工作流编排（42 命令） | 100% | 42/42 全量落地于 `references/workflows/<域>/<命令>.md`（v1.1.0） |
| 自动加载触发 | 85% | 用描述中触发短语接入路由 |
| 审计类（subagent / allowed-tools） | 70% | 只读代理 + 沙箱；`file:line` 证据机制保留 |
| 外链 / Further Reading | 40 条唯一外链已回补 | 113 个文件带 `## Further Reading`（v1.1.0，均来自策展人 Product Compass 站点） |
