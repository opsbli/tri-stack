# tri-learn · 学习教练

> 把「我想学 X」变成一个可持续推进、可检查掌握、可回头复习的一一个性化学习系统。Agent 扮演一位不赶进度的长期学习教练：一次只推进一小节、掌握后才进入下一步，并记录你的错题、按时提醒你复习。

版本：`1.0.1` ｜ 类型：横向型（tri-* 家族） ｜ 许可证：MIT

## 一句话介绍

**tri-learn** 不是一次性生成课程大纲的工具，而是一套「专家式、留白」的学习推进协议——它把掌握学习、间隔重复、主动回忆、错题追踪、苏格拉底式提问内化为 Agent 可执行的教学决策，并仰赖固定文件契约保证学习记录可跨会话自动回溯。

## 特性

- **五入口路由**：学习 / 复习 / 全局复习 / 错题 / 间隔查询，外加「回答检查站判掌握」。
- **掌握为本**：「未掌握不推进下一课」铁律，绝不因进度凑内容。
- **间隔重复排期**：1/3/7/14/30 天固定节奏，绝对日期记法，可计算可回溯。
- **主动回忆复习**：复习先提问、不复读原文、不泄答案。
- **错题追踪闭环**：活跃遗漏 + 已解决遗漏（带解决证据）。
- **知识锚点守真**：有可靠来源才写，NEVER 编造出处。
- **可执行确定性脚本**：间隔计算 / 到期判断 / 全局扫描 / 掌握判断 / 路由识别 / 主题初始化 / 契约审计。
- **版权与作者信息移除**：毛坯 `xuexi-learning-skill-main` 的版权与作者信息已剥离，许可证仅由 frontmatter 声明。

## 目录结构

```
tri-learn/
├── SKILL.md                        # 主入口：方法论 + 五入口路由 + 掌握矩阵 + 交互流程
├── README.md
├── CHANGELOG.md
├── _meta.json
├── scripts/
│   ├── check_update.py             # 版本检查（第零步硬门）
│   └── learn_tool.py               # 确定性算法工具
├── references/
│   ├── learning-methodology.md     # 方法论细化（三原则/五入口/掌握矩阵/反模式）
│   ├── file-templates.md           # 三个记录文件精确模板
│   ├── version-check-spec.md       # 版本检查规范（自包含副本）
│   └── source-traceability.md      # 资料溯源与版权/作者信息移除说明
├── tests/
│   └── tri-learn-full-testcases.md
├── _forge/                         # 锻造链路审计文档
└── 蒸馏分析报告-xuexi-learning-skill-main.md   # 蒸馏审计报告（不参与执行）
```

## 安装

作为 tri-* 家族横向型 skill，二选一：

```bash
# 1) 标准安装（若接入 tri-intent 家族）
skillhub install tri-learn --dir <目标目录>

# 2) 直接引入
把 SKILL.md 所在目录作为 skill 目录加载即可（独立可用，无强制上游依赖）
```

## 使用

### 触发语

```text
我想学 Python 基础，带我一步步学。
我想复习销售技巧。
今天该复习什么？
看看我的错题。
我多久没学过这个主题了？
```

### 提交检查站回答

你回答上一课检查站后，skill 判断掌握程度并决定下一步（下一课 / 补充课 / 拆解卡点重建）。

### 脚本速查

> 学习主题记录统一存于 `.tribro/learning/<主题>/`（家族约定下所有 skill 产出在 `.tribro`）。

```bash
# 初始化主题
python scripts/learn_tool.py create-topic "Python基础" --dir .tribro/learning --json

# 计算下次复习日期（掌握日 + 复习次）
python scripts/learn_tool.py interval 2026-08-30 1 --json

# 距最后学习天数
python scripts/learn_tool.py days-since "Python基础" --dir .tribro/learning --json

# 到期复习项
python scripts/learn_tool.py due "Python基础" --dir .tribro/learning --json

# 全局复习扫描（三档分组）
python scripts/learn_tool.py scan --dir .tribro/learning --json

# 掌握判断
python scripts/learn_tool.py mastery "部分理解" --json

# 识别流程模式
python scripts/learn_tool.py route "今天该复习什么" --json
```

## 测试

全场景测试用例见 `tests/tri-learn-full-testcases.md`（frontmatter 版本与 SKILL.md 一致）。

## 设计原则

- **掌握为本**，不赶进度；未掌握不推进。
- **文件契约固定**：三个记录文件文件名不改，保证自动可检索。
- **绝对日期** vs 相对时间，保证跨会话可计算。
- **守真**：知识锚点有来源才写，无则省略。
- **默认不推送**：不擅自 git commit/push。

## 进化的来源

本 skill 蒸馏自通用「交互式学习教练」方法论（掌握学习 / 间隔重复 / 主动回忆 / 苏格拉底提问）。所有课程示例与话术为方法论载体，不构成版权素材转载；本 skill 已移除参考仓库的作者署名、版权声明与 LICENSE 原文（详见 `references/source-traceability.md`）。