# 原型解析（tri-prototype）

![version](https://img.shields.io/badge/version-1.0.0-blue) ![license](https://img.shields.io/badge/license-MIT-green)

> **PM→Dev 桥接 skill**：解析产品原型链接与 PRD 文档，产出 tri-coding 门② 可直接消费的 `requirements.md`——无缝衔接 tri 家族开发流程。

## 特性

- **五步流水线**：平台识别 → 原型解析 → PRD 解析 → 规则合并 → 规范映射
- **保真度分级**：高（≥80%）/ 中（50–80%）/ 低（<50%），NEVER 在信息不足时编造
- **PRD 优先**：PRD 与原型冲突时以 PRD 为准，标注冲突项
- **无缝衔接**：产出的 `requirements.md` 按 tri-coding 门② 九章结构组织，**tri-coding 可直接读取消费**
- **多平台适配**：Axure / Figma / 摹客 / 墨刀 / 蓝湖 / 即时设计 / 本地导出 / PRD 文档

## 安装

本 skill **支持独立安装**，含上游依赖检测**三态**逻辑（快照模式 / 引导安装 / 降级模式）。

## 使用

```
用户：PM 给了 Axure 链接 https://share.axure.com/xxx，帮我解析后开始编码
     ↓
tri-intent 识别 I11 + L3=pm-prototype
     ↓
tri-prototype 五步流水线解析
     ↓
产出 .tribro/coding/<命名>/requirements.md
     ↓
tri-coding 门② 直接读取该文件，产出 design.md → tasks.md → 代码
```

## 设计原则

1. **衔接优先**：产出格式 MUST 与 tri-coding 门② 期望对齐
2. **保真度诚实**：NEVER 在信息不足时编造页面结构或交互规则
3. **PRD 优先**：PRD 是业务规则的权威来源，冲突时以 PRD 为准

## 版本

当前版本见 `SKILL.md` frontmatter 与 `CHANGELOG.md` 首条。

## 许可证

MIT — 详见仓库根 `LICENSE`。
