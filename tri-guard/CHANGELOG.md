# Changelog

本文件遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [1.0.1] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手通用审计清单、代码质量审查与漏洞修复落地，只做 agent skill 安全红线审计，转出/归属对应 skill 呼应家族 MECE。

## [1.0.0] - 2026-08-23

### 新增

- 初始版本：从 SkillSpector（NVIDIA，Apache-2.0）蒸馏能力的横向方法论型 skill `tri-guard`。
- 双轨检测：工具轨（委派 `skillspector` 确定性扫描）+ 知识库降级轨（内嵌 70 漏洞模式 / 19 大类规则手册启发式）。
- 语义双轨复核：十一维复核框架 + SSD/SDI/SQP 问题集，区分 malicious / negligent / benign-but-sensitive。
- 风险评分确定性实现 `scripts/risk_score.py`（严重点数 / 置信度缩放 / 同级递减权重 / 可执行乘数 / 严重带 / 退出码）。
- 上游依赖检测三态：工具轨 / 引导安装 / 降级轨，`skillspector` 作为可选上游，无则降级并明示 unconfirmed。
- 裁决三态 `APPROVE / CAUTION / REJECT` + `security-report.md` 报告模板（user 语言正文 + 英文术语）。
- 配套 `references/`（规则手册 / 语义审查 / 风险评分）、README、tests 全场景用例、版本检查 STUB。