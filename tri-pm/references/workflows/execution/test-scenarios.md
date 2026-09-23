---
name: test-scenarios
description: 从用户故事/功能 spec 生成全面测试场景——正常/边界/异常。
source: pm-skills-main/pm-execution/commands/test-scenarios.md
domain: 执行
---

# /test-scenarios → 测试场景生成器

> 蒸馏自命令 `test-scenarios`｜域：执行｜源词数：≈480
> **语法翻译**：源项目以 `/test-scenarios` 斜杠调用；本环境无斜杠命令，以下「工作流步骤」即等价编排步骤，由 Agent 按步执行。

## 用途

把用户故事或功能描述转为 QA 可立即执行的全面测试场景，覆盖正常流、边界、错误处理与跨浏览器/设备。

## 参数提示

`<user stories, feature spec, or description>`（亦接受上传 PRD/spec）

## 调用示例（翻译为对话形态）

- 源：`/test-scenarios [paste user stories]`
- 本环境等价说法：「根据这些用户故事生成测试场景」
- 源：`/test-scenarios User can reset their password via email link`
- 本环境等价说法：「为『用户通过邮件链接重置密码』建测试场景」

## 工作流步骤

1. **接受输入** — 用户故事、验收标准、PRD 段落、功能描述、任何预期行为规格。
2. **生成场景**〔引用技能：`**test-scenarios**`〕— 每故事/需求生成：Happy Path（预期流）、Edge Cases（边界/异常输入/并发）、Error Scenarios（出错时）、Security（如适用：鉴权/权限/数据）、Performance（如适用：负载/超时/大数据）。
3. **结构输出** — 输出 Test Scenarios（见模板，含 Coverage Matrix、Test Data Requirements）。保存 markdown。
4. **下一步** — 提议：生成测试数据、加更多边界、建这些场景测的用户故事。

## Checkpoint

> **Step 2 后**："Every acceptance criterion should map to at least one test scenario" — 每个验收标准应映射到至少一测试场景。

## 输出模板

```markdown
## Test Scenarios: [Feature]
**Source** / **Total** / **Coverage**
### Scenario N: [Title] | Tests | Preconditions | User role
| Step | Action | Expected Result |
**Postconditions** / **Priority**
### Coverage Matrix | ### Test Data Requirements
```

## 保存指令

保存为 markdown

## 下一步建议

- 「要为这些场景生成测试数据吗？」
- 「要为某场景加更多边界吗？」
- 「要建这些场景所测的用户故事吗？」

## Further Reading

- （源未提供 Further Reading 或全部不合规，已丢弃）
