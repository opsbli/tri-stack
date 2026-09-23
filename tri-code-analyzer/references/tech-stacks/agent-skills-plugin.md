---
name: stack-agent-skills-plugin
description: Agent Skills 插件栈卡——SKILL.md 规范、渐进披露、跨平台引导注入、零依赖插件工程分析要点。
---

# 栈卡：Agent Skills 插件（AI 编码代理方法论插件框架）

> 本卡源于某 Agent Skills 方法论开源项目剖析实战建卡；规范依据 agentskills.io 官方规范（已联网核验）。

## 探测信号

- `skills/<name>/SKILL.md` 目录树：每个 SKILL.md 带 YAML frontmatter（`name`/`description`），无构建产物。
- `.claude-plugin/plugin.json`（Claude Code 插件清单）或 `marketplace.json`；`hooks/hooks.json` + `hooks/session-start` 等 shell hook 脚本。
- 跨平台适配器目录：`.opencode/plugins/*.js`、`.pi/extensions/*.ts`、`.gemini/`（contextFileName 指令文件）、`.hermes-plugin/`（Python）、`.codex/`、`.cursor-plugin/`、`.kimi-plugin/`、`.devin/`、`.agents/`。
- `commands/*.md`（斜杠命令）、`agents/*.md`（子代理定义）。
- package.json 无 `dependencies`/`devDependencies`（纯文档+脚本分发是常态，零 npm 依赖为惯例）。

## 工程惯例（分析要点校准基线）

- **SKILL.md 规范**（agentskills.io/specification）：`name` ≤64 字符小写连字符；`description` ≤1024 字符且是模型触发的唯一依据；正文建议 <500 行。渐进披露三层：frontmatter（常驻上下文）→ SKILL.md 正文（触发后加载）→ `references/`+`scripts/`+`assets/`（按需读取）。
- **引导注入机制**：SessionStart hook 读取引导 SKILL.md 转义后注入为 additionalContext，使代理会话一开始就遵循「低阈值主动调用 skill」规则；注入点即整个框架的运行时心脏，剖析 MUST 先读 hooks/。
- **跨平台三形态**：A=shell-hook（Claude Code/Cursor/Copilot 等，stdout JSON 注入）；B=in-process 插件（OpenCode JS/pi TS/Hermes Python，订阅 session 生命周期事件）；C=instructions-file（Gemini/AGENTS.md 类 @-include 或固定文件名约定）。同一方法论，三种接线方式。
- **方法论载体**：skill 正文 = 流程文档（触发条件/决策规则/反模式表/验收标准），代码占比低；脚本用于确定性步骤（提取/打包/校验），提示词模板作为子代理输入。
- **版本多文件联动**：清单文件（plugin.json/gemini-extension.json/marketplace 条目等 8 处）版本必须一致，常用 `.version-bump.json` 声明清单 + bump 脚本 + `--audit` 漂移检测。
- **测试双体系**：tests/（bash/node/python 测插件基建确定性逻辑）与 evals/（外部仓库，评测 LLM 行为是否按 skill 执行——"drill"）。

## 常见坑（剖析时重点核查）

1. SKILL.md 超长（>500 行）导致上下文浪费——核查正文是否该下沉 references/。
2. description 模糊或写成实现摘要，导致模型不触发（触发率是 skill 生命线）。
3. hook 脚本跨 shell 兼容：bash 版本差异（heredoc 挂起）、CMD/bash polyglot 包装、stdout 必须是合法 JSON（转义处理）。
4. 引导内容重复注入（in-process 适配器需生命周期标志位防重）。
5. 多平台清单版本漂移（改了一处漏七处）——核查版本联动脚本与 audit 命令。

## 深读锚点

- 无（wikihub 暂无对应目录）。

## 官方文档

- Agent Skills 规范：https://agentskills.io/specification （2026-09-17 已核验可达）
- 参考实现：某 Agent Skills 方法论开源项目（按家族去标识化铁律不点名仓库与版本号）
