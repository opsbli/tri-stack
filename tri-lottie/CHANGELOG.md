# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.5] - 2026-09-26

### 变更

- **新增「🔴 检查点与红灯清单（STOP · NEVER）」章节**：把既有确认门收敛为显性 🔴 STOP 标记（darwin 9 维 rubric dim4），并聚合既有 NEVER 铁律为红灯清单（dim9）；仅聚合既有语义，不新增行为门。

## [1.0.4] - 2026-09-25

### 变更

- **新增「兜底处理（NEVER 静默失败）」章节**：补齐家族合规判据第 14 条要求的五类异常显式降级路径（版本检查异常 / 门禁不过 / 上游缺失 / hook 缺失 / 异常场景），并按本 skill 的触发源与既有机制定制。属文档补全，无行为变更（无代码改动）。

## [1.0.3] - 2026-09-24

### 变更

- **版本门节统一为 `version-stub v1` 形态**：`## 版本检查与更新机制` 收敛为 14 行（执行方式 + 真源指针）。原节为 4 行并**内联了四态判定 / 退出码语义**，违反 `references/version-check-spec.md` §六「≤30 行、禁内联细则」；细则唯一真源为该 spec，行为不变。
- 非功能性变更（文档口径），无行为变更。

## [1.0.2] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手界面视觉设计/动效方向规格（tri-frontend-design）、通用编码任务（tri-coding）、非动画类缺陷调试（tri-fix）、Lottie JSON 动画原创设计制作与意图识别（tri-intent），强化「消费资产、不产出设计」边界。

## [1.0.1] - 2026-09-13

### Changed
- harmonyos-arkts：真实编译验证回填——黄金用例已在 DevEco Studio 6.1.1（hvigor 6.24.2 / API 24）assembleHap 编译通过，HAP 内断言组件/资产/库符号齐全
- harmonyos-arkts：新增坑位 7/8/9——`curves.cubicBezier` API 24 弃用告警、ArkTS 严格模式 arkts-no-any-unknown（catch 参数须显式 BusinessError）、hvigor 6.x modelVersion 双文件声明铁律

## [1.0.0] - 2026-09-13

### Added
- 首版发布：跨端动效决策与执行库（tri-forge 按规范蒸馏生成）
- 决策层 `references/` 5 篇：motion-tokens（数值 token 表）/ motion-personality（4 人格原型）/ emotion-mapping（情绪映射）/ quality-gate（三级质量门+排障）/ recipe-patterns（成品配方）
- 执行层 `stacks/` 6 端 implementation.md：web / android / ios / harmonyos-arkts / react-native / flutter（统一六节模板：选型/安装约束/API 映射/坑位/黄金用例代码/性能与 a11y）
- SKILL.md 12+4 章路由型骨架：8 步规格单工作流、六端路由（双栈按技术事实判别）、知识装配顺序、进化契约、完成判据（停车/结束区分）
- `scripts/check_update.py`（版本门第零步，同源 tri-forge）+ `scripts/compliance_check.py`（T1-T10 确定性测试执行器）
- tri-intent 路由接通：I11 + L3_子意图=motion → tri-lottie（门③五步回填）
- 全场景测试用例 `tests/tri-lottie-full-testcases.md`（结构/六端断言/路由同步/工具链真实测试/场景行为）
