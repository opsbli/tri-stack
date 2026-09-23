# plans/ — motion.audit 自包含改进计划输出目录

本目录为**运行时生成**目录，不由 skill 预置内容。

## 用途

`motion.audit`（全库动效审计）模式在此产出自包含改进计划，文件命名 `NNN-<slug>.md`。
模板与硬规则见 `references/motion-plan-template.md`。

## 硬规则

1. **NEVER 修改源代码**——audit 模式下唯一可创建/编辑的文件位于本目录。
   若本目录已被别的事占用，则改用 `animation-plans/`。
2. **计划 MUST 完全自包含**——假设执行者零上下文零品味，
   内联确切的 `cubic-bezier`、确切时长、确切文件路径与代码摘录，NEVER 引用"上面讨论过的"。
3. **写完 plan 后 MUST 创建或更新 `plans/README.md`**——含 plan 表
   （编号、标题、严重度、状态）、建议执行顺序、plan 之间的依赖关系。
4. **令牌真源**——所有曲线/时长/弹簧值 MUST 取自 `references/motion-standards.md`，NEVER 凭记忆近似。

## 落盘规则

产物默认以对话回应交付；`motion.audit` 的计划落盘本目录。
若用户显式指定目标文件/目录，以用户指定路径为准。
