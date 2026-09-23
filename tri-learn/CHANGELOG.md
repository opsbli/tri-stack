# Changelog

本文档遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/) 规范，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [1.0.2] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手一次性课程大纲、业务代码/文档/报告生成与专业医疗/法律/财务意见，只做一对一学习教练。

## [1.0.1] - 2026-08-30

### 变更

- **产物集中落盘硬规则**：把「一切运行产物落盘于 `.tribro/learning/<主题>/`」上升为强制执行契约第 8 条硬规则（家族约束「所有 skill 产出存 `.tribro`」），并同步至落盘规则、五流程（学习/复习/错题/全局复习/间隔查询）、质量标准与自检句。
- 已将既有学习主题记录从 `learning/` 迁移至 `.tribro/learning/`。

## [1.0.0] - 2026-08-30

### 新增

- **tri-learn 学习教练 skill 蒸馏落地**：从通用「交互式学习教练」方法论蒸馏（掌握学习 / 间隔重复 / 主动回忆 / 苏格拉底式提问），作为独立的 tri-* 家族横向型 skill 落盘于 `tri-learn/`。
- **五种入口路由**：学习 / 复习 / 全局复习 / 错题 / 间隔查询，外加「回答检查站判掌握」。
- **掌握判断矩阵**：完全掌握 / 基本掌握 / 部分理解 / 尚未理解 四档到动作映射，含「未掌握不推进」铁律。
- **间隔重复排期**：固定节奏 1/3/7/14/30 天，绝对日期记法。
- **三个固定记录文件契约**：`进度.md` / `错题与遗漏.md` / `复习计划.md` 精确模板。
- **可执行脚本**：`scripts/learn_tool.py`（route / create-topic / interval / days-since / due / scan / mastery / audit）与 `scripts/check_update.py`（版本检查第零步硬门）。
- **版权与作者信息移除**：不复制参考仓库的 LICENSE 与作者署名，许可证仅由 frontmatter `license: MIT` 声明；出处仅以中性描述留存于溯源文档。