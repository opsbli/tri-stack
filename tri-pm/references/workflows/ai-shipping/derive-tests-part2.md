---
name: derive-tests-part2
description: derive-tests 续篇（part2）——工作流步骤 4–6（提议测试、建议 CI 门、汇报覆盖与缺口）、输出模板、保存指令与关键规则。
source: pm-skills-main/pm-ai-shipping/commands/derive-tests.md
domain: AI 交付
---

# /derive-tests → 把意图变成测试（part2）

> 蒸馏自命令 `derive-tests`｜域：AI 交付｜源词数：1222
> 本文件是 `derive-tests.md` 的续篇，因单文件超 900 词上限而拆出。用途、前提、步骤 1–3（含测试类型四分法与 policy shadow 警告）见 part1。
> **语法翻译**：源以 `/derive-tests` 斜杠调用；本环境无斜杠命令，以下即等价编排步骤。

## 工作流步骤（4–6）

4. **提议测试（Propose the tests）** — 对每一条你**能用确定性自动化测试（unit 或 integration）锚定**的规则，写出用例：**名称、arrange/act/assert 意图、以及它必须拒绝的 negative case**。**按它所防守的文档或流程分组**。**优先能锚住该规则的最小测试**——「一个边界一条清晰断言」胜过一个会因十种原因失败的臃肿 integration 测试。

5. **建议 CI 门（Recommend the CI gate）** — **建议，不要默默安装**。给出与仓库技术栈和既有工具链匹配的 CI 配置：
   - **每个 pull request 上跑确定性本地集**（unit + 任何无需实时服务即可运行的 integration 测试）；
   - **guarded-live 测试保持 opt-in**（手动或定时触发，**永不阻塞**）；
   - 通过**必需状态检查（required status check）+ 分支保护（branch protection）**，**对合入 `main` 设「绿灯才可合入」的门**。

   **把 workflow 文件与分支保护设置作为一个清晰标注的「建议」输出给用户审批，而不是一个已生效的改动。**

6. **汇报覆盖与缺口** — 把 `tests.md` 写成**三个清晰分隔的小节**：
   - **Existing coverage（现有覆盖）** — 仓库里的测试**今天**就锚定的规则（来自步骤 1 的清点）。
   - **Proposed tests（提议的测试）** — 你建议但**尚不存在**的用例，**按类型分**。
   - **Gaps（缺口）** — **完全没有任何验证**的成文规则，**按跨过它会暴露什么排序**。

   **缺口就是待办清单**，而且它们正是下一次 AI 编辑能悄悄破掉一条边界的地方。**要诚实说明 proposed ≠ existing：一条规则在真有测试断言它之前，都不算被覆盖。**

## Checkpoint

> **Step 5 后**：CI workflow 与分支保护只能作为**待用户审批的建议**输出，**不得直接应用**。
> **Step 6 后**：三小节必须物理分隔，`Existing / Proposed / Gaps` 不得混写。

## 输出模板

```markdown
Test Coverage: [scope]

| Use case | Rule (doc) | Expected behavior (+ deny case) | Evidence | Type | Status |
|----------|-----------|---------------------------------|----------|------|--------|
[status: existing / proposed / none]

### Existing coverage
[tests already in the repo, each tied to the rule it pins]

### Proposed tests
[grouped by flow/doc — name · assert · negative case · type]

### Recommended CI gate
[workflow snippet for the detected stack + "green-before-merge" branch-protection note]

### Gaps — documented but unverified
[rules with no test yet, ranked by what crossing them exposes]
```

**Evidence 列格式**：`doc + code`，代码侧用 `file:line`。**Type 取值**：unit / integration (deterministic) / guarded live / manual。**Status 取值**：existing / proposed / none。

## 保存指令

- 覆盖映射写到 `documentation/tests.md`
- 完整报告写到 `reports/test_plan_{timestamp}.md`
- **两个路径都要给用户。**

## 关键规则（源 Notes）

- 这是「documented == implemented」的**验证那一半**：审计找出**今天**的缺口，这些测试让它**明天不会重开**。
- **不要为了制造覆盖而编造规则。文档沉默之处，缺口在文档里**——先去修 `document-app` 那一环。
- **不要把外部服务接进默认 CI 运行**；不稳定的实时测试会一点点侵蚀「绿灯才可合入」这道门，直到大家开始无视它。
- 本流程**只管测试派生**。缺口审计本身走 `security-audit-static` 流程；完整的「文档 → 审计 → 测试 → 交付包」序列走 `ship-check` 流程。

## 下一步建议

把 Gaps 小节当作待办清单排期；先实现能锚住 Critical/High 边界规则的确定性测试，再向用户提交 CI 门建议等待审批。

## Further Reading

（源未提供 Further Reading）
