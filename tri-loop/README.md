# tri-loop

> 知识库 loop（domain）启动下游执行 skill。蒸馏自 new-loop 开源项目，适配 tri-intent 下游 skill 规范。

## 概述

tri-loop 是 tri-intent 意图识别总路由的下游执行 skill，处理 I14（操作执行·loop/domain 创建子类）意图。它在基于文件的知识库中 bootstrap substrate、收集 loop charter、scaffold loop README、执行一次真实测试运行并记录到 Timeline 和 LOG.md。

## 核心能力

| 能力 | 说明 |
|---|---|
| Substrate Bootstrap | 检查并创建知识库底层基座（ARCHITECTURE.md + LOG.md + CLAUDE.md + signals/docs/domains 文件夹），idempotent |
| Loop Charter 收集 | 收集 5 项输入（name/goal/cadence/做什么/工具数据），推断为主 + 简短澄清 |
| Loop README Scaffold | 从模板创建 domains/\<name\>/README.md，含 frontmatter + 描述 + Backlog + Timeline |
| 真实测试运行 | 真正运行一次 loop（小规模），证明 loop 确实能跑 |
| Timeline + LOG.md 记录 | 两个必需输出：Timeline 一行 + LOG.md 一条，无论是否产出 artifact |
| 回报 | 总结 charter + 测试结果 + artifact + 缺失项 + 如何再运行 |

## 三态依赖检测

| 模式 | 触发条件 | 行为 |
|---|---|---|
| A · 快照模式 | tri-intent 可用 | 读取快照 §三，按标准工作流推进 |
| B · 引导安装 | tri-intent 不可用，用户拒绝降级 | 提示安装 tri-intent |
| C · 降级模式 | tri-intent 不可用，用户选择直接使用 | 内联澄清自构造输入后执行 |

## 使用方式

### 作为 tri-intent 下游 skill

```
tri-intent 识别意图 → 产出快照 → 下游路由建议指向 tri-loop → tri-loop 读取快照 §三 执行
```

### 独立使用（降级模式）

直接告诉 tri-loop 你要创建什么 loop：
```
帮我创建一个每周 SEO loop，目标是追踪关键词排名变化，每周拉一次 SERP 数据
```

## 文件结构

```
tri-loop/
├── SKILL.md                    # 主入口
├── README.md                   # 本文件
├── CHANGELOG.md                # 变更日志
├── templates/                  # 模板文件
│   ├── loop-readme.md          # domain README 模板
│   ├── architecture.md         # ARCHITECTURE.md 模板
│   ├── log.md                  # LOG.md 模板
│   ├── claude-template.md      # CLAUDE.md 完整模板
│   ├── claude-kb-section.md    # CLAUDE.md 知识库章节（追加块）
│   ├── signals-readme.md       # signals/ README
│   ├── docs-readme.md          # docs/ README
│   ├── domains-readme.md       # domains/ README
│   ├── knowledge-setup.md      # 知识库引导搭建流程
│   └── result.md               # 执行结果模板（落盘于 .tribro/loops/）
└── tests/
    └── tri-loop-full-testcases.md  # 全场景测试用例
```

## 蒸馏来源

蒸馏自 new-loop 开源项目，保留全量能力：
- SKILL.md → 6 大核心能力 + 处理流程 + 交付产物 + 安全约束
- references/ARCHITECTURE.md → templates/architecture.md
- references/LOG.md → templates/log.md
- references/CLAUDE.template.md → templates/claude-template.md + claude-kb-section.md
- references/KNOWLEDGE_SETUP.md → templates/knowledge-setup.md + signals/docs/domains-readme.md

## 许可证

MIT
