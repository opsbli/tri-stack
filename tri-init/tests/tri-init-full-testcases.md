# tri-init 全场景测试用例

## 测试用例

| # | 场景 | 预期结果 |
|---|---|---|
| T01 | 初始化 Java/Maven 项目（ops-pilot） | 检测到 Java 17 + Spring Boot 3.5.9 + RuoYi；生成 AGENTS.md + profile |
| T02 | 初始化 TS/Vite 项目（ops-pilot-web） | 检测到 Vue 3.5 + Vite 6 + Element Plus；生成 AGENTS.md + profile |
| T03 | 前后端分离多项目模式 | 两个路径分别扫描；profile 合并 |
| T04 | AGENTS.md 已存在 → 用户选覆盖 | 覆盖旧文件；产出新 AGENTS.md |
| T05 | AGENTS.md 已存在 → 用户选保留 | 跳过 AGENTS.md 生成；其余正常 |
| T06 | 检测到 RuoYi 代码生成器 | project-profile 含租户/审计/逻辑删除字段规范 |
| T07 | 无法检测技术栈 | 标注「未检测到」；请用户手动指定 |
| T08 | 项目路径不存在 | 澄清；NEVER 创建不存在的目录 |
| T09 | 重复运行（幂等） | 产生相同结果；不重复创建 |
| T10 | .tribro/ 已存在 | 跳过创建；标注已存在 |
