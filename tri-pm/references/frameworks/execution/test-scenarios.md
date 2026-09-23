---
name: test-scenarios
description: 从用户故事生成全面测试场景——测试目标、起始条件、用户角色、逐步动作与预期结果。
source: pm-skills-main/pm-execution/skills/test-scenarios/SKILL.md
domain: 执行
---

# 测试场景（test-scenarios）

> 蒸馏自 `test-scenarios`｜域：执行｜源词数：≈520

## 必含章节清单（MUST-SECTIONS）

- [ ] Test Scenario — 清晰场景名
- [ ] Test Objective — 验证的具体行为
- [ ] Starting Conditions — 系统状态/数据/配置/用户设置
- [ ] User Role — 执行测试的角色
- [ ] Test Steps — 逐步交互（动作 + 预期）
- [ ] Expected Outcomes — 每步后可观察结果

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] （无）

## 逐段引导问题

- **Review**：读用户故事与验收标准。
- **Objectives**：定义验证什么具体行为。
- **Starting Conditions**：系统状态、数据/配置、用户权限。
- **User Roles**：谁执行。
- **Steps**：逐步拆解交互。
- **Expected Outcomes**：每步后可观察结果。
- **Edge cases**：无效输入、边界条件。

## 输出模板

```markdown
**Test Scenario:** [Clear scenario name]
**Test Objective:** [What this test validates]
**Starting Conditions:**
- [System state] / [Data] / [User setup]
**User Role:** [Who performs the test]
**Test Steps:**
1. [Action] → [Expected result]
2. [Action] → [Observable outcome]
**Expected Outcomes:**
- [Observable result 1]
- [Observable result 2]
```

## 输出命名规则

源文件未规定（输出可直接供 QA 执行）

## 关键规则

- 每个验收标准至少对应一个测试场景
- 覆盖正向/边界/异常
- 结果可观察、QA 无需额外解释即可测

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- （源未提供 Further Reading 或全部不合规，已丢弃）
