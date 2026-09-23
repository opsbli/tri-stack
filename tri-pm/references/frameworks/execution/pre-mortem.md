---
name: pre-mortem
description: 对 PRD/发布计划做事前复盘风险分析，按老虎/纸老虎/大象分类，再分发布阻断/快速跟进/跟踪。
source: pm-skills-main/pm-execution/skills/pre-mortem/SKILL.md
domain: 执行
---

# 事前复盘风险分析（pre-mortem）

> 蒸馏自 `pre-mortem`｜域：执行｜源词数：≈600

## 必含章节清单（MUST-SECTIONS）

- [ ] Tigers — 真实风险（Real Risks）
- [ ] Paper Tigers — 被夸大的担忧（Overblown Concerns）
- [ ] Elephants — 未被讨论的担忧（Unspoken Worries）
- [ ] Action Plans for Launch-Blocking Tigers — 阻断级老虎的缓解计划

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] （无）

## 逐段引导问题

- **想象失败**：产品 14 天后发布却失败——客户不采用、收入未达、声誉受损。什么出错了？我们漏了/没执行好什么？哪里过度自信？
- **Tigers 分类口径**：基于证据/经验/清晰逻辑的真实问题；应让你夜不能寐；需行动。
- **Paper Tigers 口径**：表面合理但不可能/被夸大；不值大量投入；记录以对齐干系人。
- **Elephants 口径**：不确定是否为问题但团队讨论不足的隐忧；值得发布前调查。
- **紧迫度**：Launch-Blocking（发布前须解）/ Fast-Follow（发布后 30 天内）/ Track（发布后监控）。

## 输出模板

```markdown
## Pre-Mortem Analysis: [Product Name]
### Tigers (Real Risks)
[每条：category + mitigation]
### Paper Tigers (Overblown Concerns)
[每条：为何非真风险]
### Elephants (Unspoken Worries)
[每条：建议调查方式]
### Action Plans for Launch-Blocking Tigers
[Risk | Mitigation | Owner | Due Date]
```

## 输出命名规则

`PreMortem-[product-name]-[date].md`

## 关键规则

- 诚实建设性——目标是提升发布就绪度，非指责
- 不确定时默认归为 Tiger，早处理优于晚
- 纳入跨职能视角（工程/设计/GTM）
- 发布前 2-3 周重访，核实缓解就位

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- [How Meta and Instagram Use Pre-Mortems to Avoid Post-Mortems](https://www.productcompass.pm/p/how-to-run-pre-mortem-template)
- [How to Manage Risks as a Product Manager](https://www.productcompass.pm/p/how-to-manage-risks-as-a-product-manager)
