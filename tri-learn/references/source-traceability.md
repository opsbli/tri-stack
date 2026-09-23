# 资料溯源与版权/作者信息移除说明

> 本文件记录 tri-learn skill 的蒸馏来源、版权合规处置与用户要求的「移除版权及作者信息」落实情况（审计用）。

## 一、蒸馏来源（中性溯源）

- 能力与方法论来源：通用「交互式学习教练」方法论仓库 `xuexi-learning-skill-main`（含 `learning-skill/` 基础版与 `learning-skill-plus/` Plus 版两套 SKILL.md，及运行示例）。
- 蒸馏依据：`tri-learn/蒸馏分析报告-xuexi-learning-skill-main.md`（本目录已落盘的审计报告，§五给出 skill 设计、§六给出 16 项能力全覆盖对照表）。
- 上述参考仓库以 MIT 许可证发布。本 skill 的蒸馏属于「方法论规则的显性化改写」，不构成对版权素材原样转载。

## 二、版权与作者信息移除落实情况（用户硬要求）

| 项 | 处置 | 状态 |
|---|---|---|
| 原仓库作者署名 | 全部移除，生成物内不出现任何作者/维护者姓名 | ✅ 已移除 |
| 原仓库版权声明（Copyright 行） | 全部移除 | ✅ 已移除 |
| 原 LICENSE 全文 | 不复制；license 仅由 frontmatter `license: MIT` 声明 | ✅ 已移除 |
| 原仓库联系方式 / 邮箱 / 主页 | 全部移除 | ✅ 已移除 |
| 出处描述 | 仅以中性名称「xuexi-learning-skill-main」在溯源文档与蒸馏报告中出现，用于审计追溯，不含作者/版权持有人信息 | ✅ 脱敏保留追溯 |

## 三、版权合规边界

- 本 skill 只承载「学习方法论规则」与「可执行占位模板」，不承载任何具体课程正文、行业话术、受版权保护的案例叙述。
- 参考仓库中的示例课程内容（`examples/Python基础` 的变量/类型课、`examples/销售技巧` 的销售话术）属演示数据，**不并入本 skill**（见蒸馏报告 §4.3 死知识处置）。
- 可执行脚本 `scripts/learn_tool.py` 与 `scripts/check_update.py` 均为本 skill 自实现/家族规范同源实现，不携带第三方版权头。

## 四、许可证

- frontmatter：`license: MIT`。
- 生成物目录内 **NEVER 生成 `LICENSE` 或 `.gitignore` 文件**（tri-* 家族硬约束 11）。

## 五、审计复核

需要复核「是否残留原作者/版权信息」时，在 `tri-learn/` 目录执行：

```bash
# 查找常见版权/作者关键词（应无命中或仅命中本溯源说明）
rg -i "copyright|© |作者|author|maintainer|(技术)?作者" --glob '!references/source-traceability.md'
```