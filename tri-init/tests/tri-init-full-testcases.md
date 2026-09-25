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

## 三、扫描脚本测试

| # | 场景 | 预期结果 |
|---|---|---|
| T11 | project-scan.py 扫描 Java/Maven 项目 | 检出 Java 版本 / Spring Boot / Maven Modules |
| T12 | project-scan.py 扫描 RuoYi 项目 | 检出 RuoYi Framework + 模块清单 |
| T13 | project-scan.py 扫描 TS/Vite 项目 | 检出 TypeScript / Vite / Vue / Element Plus / Pinia / UnoCSS |
| T14 | project-scan.py 检测 BaseEntity.java | 提取审计字段（createDept/createBy/createTime/updateBy/updateTime） |
| T15 | project-scan.py 检测 TenantEntity.java | 提取租户字段（tenantId） |
| T16 | project-scan.py --json 输出 | 有效 JSON，可被 prompt 层解析 |

## 四、幂等性测试

| # | 场景 | 预期结果 |
|---|---|---|
| T17 | 重复运行 tri-init | AGENTS.md 覆盖（用户确认后）；.tribro/ 不重复创建 |
| T18 | 两个项目分别初始化 | 各自独立；profile 不混淆 |

## 五、兜底测试

| # | 场景 | 预期结果 |
|---|---|---|
| T19 | 项目路径为文件（非目录） | 澄清；NEVER 继续 |
| T20 | 项目目录为空 | 标注「空项目」；仍生成基础 AGENTS.md |
| T21 | 版本检查报 D 态 | 放行但告警 |

## 六、AGENTS.md 内容验证

| # | 场景 | 预期结果 |
|---|---|---|
| T22 | AGENTS.md 含项目概述 | 标题 + 一句话描述 + 技术栈摘要 |
| T23 | AGENTS.md 含技术栈表 | 与 project-scan.py 检出结果一致 |
| T24 | AGENTS.md 含编码规范 | 命名规范 / 分层规范 / 代码风格 |
| T25 | AGENTS.md 含目录结构说明 | 与实际目录结构一致 |
| T31 | AGENTS.md 含通用编码行为规则（8 条） | 8 条齐全，第 1 条为兼容安全版 |

## 七、project-profile.json 验证

| # | 场景 | 预期结果 |
|---|---|---|
| T26 | profile 含 slug / name / version | 与 SKILL.md frontmatter 一致 |
| T27 | profile 含 tech_stack 数组 | 与 project-scan.py 检出结果一致 |
| T28 | profile 含 db_conventions（如有代码生成器） | 含租户/审计/逻辑删除字段 |
| T29 | profile 含 directory_structure | 与实际目录一致 |
| T30 | profile JSON 可被 tri-coding 解析 | tri-coding 门② 消费时不报错 |

## 六、AGENTS.md 内容验证

| # | 场景 | 预期结果 |
|---|---|---|
| T22 | AGENTS.md 含项目概述 | 标题 + 一句话描述 + 技术栈摘要 |
| T23 | AGENTS.md 含技术栈表 | 与 project-scan.py 检出结果一致 |
| T24 | AGENTS.md 含编码规范 | 命名规范 / 分层规范 / 代码风格 |
| T25 | AGENTS.md 含目录结构说明 | 与实际目录结构一致 |
| T31 | AGENTS.md 含通用编码行为规则（8 条） | 8 条齐全，第 1 条为兼容安全版 |

## 七、project-profile.json 验证

| # | 场景 | 预期结果 |
|---|---|---|
| T26 | profile 含 slug / name / version | 与 SKILL.md frontmatter 一致 |
| T27 | profile 含 tech_stack 数组 | 与 project-scan.py 检出结果一致 |
| T28 | profile 含 db_conventions（如有代码生成器） | 含租户/审计/逻辑删除字段 |
| T29 | profile 含 directory_structure | 与实际目录一致 |
| T30 | profile JSON 可被 tri-coding 解析 | tri-coding 门② 消费时不报错 |
