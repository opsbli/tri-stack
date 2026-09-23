---
name: security-audit-static-part2
description: security-audit-static 续篇（part2）——fan-out / allowed-tools 的本环境等价翻译，以及步骤 4「自我反驳」的 6 条豁免判据、attacker/victim 点名规则与 5 类禁用清单。
source: pm-skills-main/pm-ai-shipping/commands/security-audit-static.md
domain: AI 交付
---

# /security-audit-static → 审计你手上已有的代码（part2）

> 蒸馏自命令 `security-audit-static`｜域：AI 交付｜源词数：1293
> 本文件是 `security-audit-static.md` 的续篇（三部分之二），因单文件超 900 词上限而拆出。用途、范围、审计引擎五步见 part1；高漏检清单 10 项、输出格式、严重性锚点与 Notes 见 part3。
> **拆分只切分了说明性散文的落点：下面的判据清单与禁用清单逐条完整保留。**
> 归因（源文声明照抄）：方法改编自 Anthropic `claude-plugins-official` 仓库中公开的 Apache-2.0 `security-guidance` 插件。与 Anthropic 无隶属关系，亦未获其背书。

## fan-out / allowed-tools 翻译（完整版）

源 frontmatter 用 `allowed-tools` 锁定工具面为 `Read, Grep, Glob, Task, Bash(git log:*), Bash(git diff:*), Bash(git show:*), Write(reports/**)`，并在范围超约 **30 文件 / 5000 行**时以**并行 subagent 扇出**。本环境无这两个原语，等价做法是**只读代理 + 沙箱静态分析**：

- 只读文件、只做搜索、git 只读；**只允许写 `reports/` 下的产物，绝不编辑被审计的代码**。
- 大范围时按「模块 / 功能簇」切成多个只读分析批次，**每批完整读取自己那一片**并跑 part1 的步骤 1–3。
- 每批返回候选记录：`{file, line, category, code（逐字片段）, explanation, severity, confidence}`；**此阶段 medium confidence 可接受**。
- **合并候选集后，由你自己在全集上跑步骤 4 的自我反驳**（不要在分片内提前反驳）。
- **`file:line` 证据机制原样保留**：任何候选与最终发现都必须能引用到具体文件与行号。

## 自我反驳判据（对应 part1 步骤 4）

**默认保留（keep）**，除非你找到**引用证据（file + line）**支撑以下 **6 条豁免判据之一**：

1. 真实存在的 sanitizer/encoder/validator/授权检查**在 sink 处**阻止了利用；
2. sink 本身不危险（typed、hardcoded、isolated、schema-decoded）；
3. 前端闸门在**后端被独立地再执行了一次**；
4. 一个未经校验的凭据被**立即转交给一个会校验它的上游系统**；
5. 一个 config/flag 把关了这条路径，且**用户无法按请求影响它**；
6. 这条路径**在生产中不可达**。

### 点名 attacker 与 victim

- **反驳掉**：若唯一受害者就是攻击者本人（在他自己的机器 / 账号 / 租户 / 数据上），且**没有跨越任何共享系统或权限边界**。
- **保留**：若影响触及**其他用户、其他租户、共享基础设施、计费、邮件信誉、密钥或合规敏感数据**。

### 绝不适用「攻击者=受害者」反驳的 5 类（照抄）

**Never apply attacker-equals-victim refutation to：**

1. **SSRF / 对外网络 sink**；
2. **共享计费或配额 sink**；
3. **数据暴露类发现**；
4. **跨租户或跨主体（cross-tenant / cross-principal）流**；
5. **服务端执行 / 渲染**。

**——它们按定义就会伤到攻击者以外的人。**

### 两条绝对禁令

- **绝不因为「这段代码是既有的（pre-existing）」就反驳一条发现——既有 bug 正是重点。**
- **不要臆测（Do not speculate）。**

## Checkpoint

> **反驳阶段**：默认 keep；豁免必须有 `file + line` 证据，且不得落在上面 5 类禁用清单内。

## Further Reading

（源未提供 Further Reading）
