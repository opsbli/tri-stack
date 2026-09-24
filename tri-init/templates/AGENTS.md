# AGENTS.md — {{project_name}}

> **本文件由 `tri-init` 生成，是 AI 工具在此项目中协作的强制规范。**
> AI 工具（WorkBuddy / TRAE / Cursor / Claude Code）加载本文件后，MUST 遵循以下全部规则。

---

## ⭐ tri-stack 强制规则（最高优先级 · 高于以下所有章节）

> **本节是 tri-stack 的入口守门规则。没有这一节，AI 会绕过 tri-intent 直接执行，导致流程失控。**

- **对任何用户请求，MUST 先通过 tri-intent 进行意图识别，NEVER 直接执行。**
- tri-intent 位于: `{{tri_intent_path}}/SKILL.md`
- tri-intent 产出快照后，根据快照的「下游路由建议」调度对应 skill
- **NEVER 跳过 tri-intent 直接调用下游 skill**（tri-coding / tri-fix / tri-review / tri-plan 等）
- 如果下游 skill 检测到快照缺失（上游依赖检测 A0/B 态），MUST 引导用户先走 tri-intent
- **NEVER 在无快照的情况下按空上下文静默执行**

> **为什么需要这条规则**：没有它，AI 会绕过 tri-intent 的意图识别直接写代码——导致需求不清、规范不一致、产物散落。这一条规则是 tri-stack 整个流程的入口守门人。

---

## 项目概述

| 项 | 内容 |
|---|---|
| 项目名称 | {{project_name}} |
| 项目描述 | {{project_description}} |
| 仓库路径 | {{repo_path}} |

---

## 技术栈

{{tech_stack_section}}

---

## 项目结构

```
{{directory_structure}}
```

---

## 编码规范

> 以下规范基于项目扫描结果 + 用户确认。AI 写代码时 MUST 逐条遵循。

{{coding_standards}}

---

## 构建与验证命令

```bash
{{build_commands}}
```

---

## tri-stack 工具链

| 工具 | 命令 | 用途 |
|---|---|---|
| 版本一致性校验 | `python ops/version-lint.py` | 校验五点版本声明一致 |
| 补丁层重放 | `python ops/patches/apply.py` | 重放本地修正（修改 skill 文件后必跑） |
| 缺失 skill 检测 | `python ops/skills-install.py --detect` | 检测缺失的 skill |
| 门④ 合规自检 | `python tri-forge/scripts/compliance_check.py --all` | 全仓 22 条合规检查 |
| 门④ 负向测试 | `python tri-forge/tests/mutation-gate.py` | 验证门④ 判据有牙 |

---

## 贡献指南

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献流程。

## 许可证

{{license}}
