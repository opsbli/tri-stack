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
- **每完成一个里程碑（功能可用 + 测试通过）MUST `git commit`**：commit 前先跑构建/测试命令确认绿；禁止把大量变更长期悬空在工作区（断连/崩溃即丢工作成果）
- **沙箱/环境降级 MUST 随交付提示**：探测到依赖缺失、安装跳过等环境差异（如 bun 缺失、electron postinstall 跳过），MUST 在 `delivery-manifest.md`（落 `.tribro/coding/<命名>/`）中列明并提示用户复验，NEVER 静默降级

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

## 通用编码行为规则（8 条 · 写码纪律）

> 与「编码规范」正交：编码规范管**本项目代码长什么样**，本节管 **AI 怎么克制地写**。
> 来源：社区 600 亿 token 实践总结（2026-09 收录）；第 1 条采用兼容安全版（英文原版「直接移除旧路径」仅适用个人项目）。

1. **兼容性**：改动旧接口、数据结构或行为前，先确认兼容要求。只有明确不需要兼容时，才移除旧路径；不要自行删除迁移或回退方案。
2. **最简实现**：选择能满足当前需求的最简单实现，别为尚未出现的需求增加抽象、配置和间接层。
3. **分层成长**：先做出能从头到尾跑通的最小版本，再逐步添加能力；不要为了尚未完成的复杂设计拆掉现有可用功能。
4. **职责分离**：保持组件职责清楚，相关代码放在合适的位置。
5. **优先成熟库**：成熟且维护良好的库能降低复杂度或提高可靠性时，优先使用；没有明确理由不要重写常见功能。
6. **先用已有依赖**：写新实现或加新依赖前，先检查项目已有依赖的文档、类型和现成能力，不要未经查证就假定它缺某个能力。
7. **长期架构**：做架构选择时考虑后续维护，不用明知很快要推倒的临时方案糊弄过去。
8. **先看先例**：设计方案前，先看成熟产品怎样解决同类问题；适合当前需求时，沿用已验证过的做法。

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
| skill 安装 | `python ops/install-skills.py --target ~/.workbuddy/skills --dry-run` | junction 安装到 AI 工具（源在仓库，单源） |
| 门④ 合规自检 | `python tri-forge/scripts/compliance_check.py --all` | 全仓 22 条合规检查 |
| 门④ 负向测试 | `python tri-forge/tests/mutation-gate.py` | 验证门④ 判据有牙 |

---

## 贡献指南

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献流程。

## 许可证

{{license}}
