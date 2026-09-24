# 变更日志

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

> **一致性硬约束**：本文件首个 `## [x.y.z]` MUST 与 `SKILL.md` frontmatter 的 `version` 相等，
> 且 MUST 为本文件的最大版本。违反即触发门④ 第 11 条 FAIL。

## [1.0.0] - 2026-09-24

### 新增

- **首版发布**：PM→Dev 桥接 skill——解析产品原型链接与 PRD，产出 tri-coding 门② 可直接消费的 `requirements.md`
- 五步流水线：平台识别 → 原型解析 → PRD 解析 → 规则合并 → 规范映射
- 解析保真度三级分级（高 ≥80% / 中 50–80% / 低 <50%），NEVER 在信息不足时编造
- PRD 优先铁律：PRD 与原型冲突时以 PRD 为准
- 九张原型平台适配表：Axure / Figma / 摹客 / 墨刀 / 蓝湖 / 即时设计 / 本地导出 / PRD / 未知
- `templates/requirements.md`：tri-coding 门② 九章需求说明书模板（九节 + 占位符）
- 测试用例 12 条（含保真度分级、冲突标注、衔接验证）

### 来源说明

本 skill 系 tri-forge 门①→⑤ 首次实战生成的产物（mode C · 锻造生成 · 五门流程）。
用户需求：「PM 给出原型链接，自动解析原型页面，如果有 PRD 文档说明业务规则再结合原型，
产出适合 tri 家族开发流程的产物，无缝衔接得上 tri 开发流程」。
