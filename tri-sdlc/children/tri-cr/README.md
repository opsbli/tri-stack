# tri-cr（tri-sdlc P5 代码评审子SKILL）

tri-sdlc 九阶段编排中的 **P5 代码评审专家子 SKILL**。接收 tri-sdlc 派发的阶段任务，对 P4 源码执行静态检查三项与四维人工审查，跟踪意见至闭环，产出 `review-report.md`，交 tri-sdlc 门禁审计。

## 特性

- **静态先行**：lint / 类型检查 / 构建三项真实执行，记录命令与失败数，失败数须为 0
- **意见三要素**：级别（Blocker/Major/Minor/Nit）+ 位置 + 状态，缺一即无效
- **零待修复交付**：Blocker 清零、无「待修复」遗留，未清零回炉 P4
- **四维必答**：可读性与命名 / 逻辑正确性与边界 / 性能 / 安全，均须给结论
- **变更-用例映射**：每个变更点须有测试用例覆盖且通过
- **只评不改**：默认不动业务代码，修复由 `tri-impl` 执行；获授权直接修复须登记

## 交付物

| 产物 | 位置 |
|---|---|
| `review-report.md` | `.tribro/sdlc/<命名>/P5-code-review/` |

## 目录结构

```
tri-cr/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-cr-full-testcases.md
```

## 安装

随 tri-sdlc 包分发，置于 `tri-sdlc/children/tri-cr/`。独立安装需先装 tri-sdlc：

```
skillhub install tri-sdlc --dir <目标目录>
```

> 只想对一段代码做通用审查而不走全流程，请改用 `tri-review`。

## 使用

```
tri-sdlc 派发 P5 阶段任务（附 P4 源码清单 + 单测报告 + P2 设计）
      → 静态检查三项（lint / 类型 / 构建）
      → 四维人工审查 + 坏味基线 + 设计一致性核对
      → 意见分级定位 → 回报 tri-sdlc 判定回炉修复
      → 复审闭环（Blocker 清零、无待修复）
      → review-report.md 落盘
      → 门禁自查（7 必检 / 2 建议）
      → 交回 tri-sdlc 审计
```

> 剖面为 `lite` 时本阶段未启用，tri-sdlc 不会派发。

## 设计原则

- **面向验收标准产出**：六维评审与 P5 门禁条目一一对应
- **方法论复用**：两阶段审查与 Fowler 坏味基线复用 `tri-review`，门禁判定权归 tri-sdlc
- **不越权**：不判门禁、不推进阶段、不改需求与设计、不代替 P6 出测试结论

## 许可证

MIT
