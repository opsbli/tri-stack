# tri-release（tri-sdlc P7 构建与发布子SKILL）

tri-sdlc 九阶段编排中的 **P7 构建与发布专家子 SKILL**。接收 tri-sdlc 派发的阶段任务，完成版本定级、构建、预发布冒烟、正式发布与巡检，产出 `release-plan.md`、`release-report.md`，并更新用户工作区 `CHANGELOG.md`，交 tri-sdlc 门禁审计。

## 特性

- **准入硬校验**：P6 未通过或 Critical 未清零，绝不发布
- **版本定级有据**：SemVer 递增位须与变更性质匹配并写明理由
- **冒烟先行**：预发布环境 ≥3 条核心链路冒烟全过，才进正式发布
- **回滚四要素**：触发条件 + 步骤 + 预计耗时 + 责任人，发布前就绪
- **灰度要素齐全**：比例 + 观察指标 + 放量条件；全量须给理由
- **发布不静默**：推远端 / 发制品 / 部署生产 / 打 tag 均须先取得用户确认

## 交付物

| 产物 | 位置 |
|---|---|
| `release-plan.md` | `.tribro/sdlc/<命名>/P7-release/` |
| `release-report.md` | 同上 |
| `CHANGELOG.md` | 用户工作区根目录（顶部追加新版本节） |

## 目录结构

```
tri-release/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-release-full-testcases.md
```

## 安装

随 tri-sdlc 包分发，置于 `tri-sdlc/children/tri-release/`。独立安装需先装 tri-sdlc：

```
skillhub install tri-sdlc --dir <目标目录>
```

## 使用

```
tri-sdlc 派发 P7 阶段任务（附 P6 测试结论 + P4 变更清单）
      → 版本定级 + 产物清单 + 流水线三段 + 回滚方案 + 发布策略
      → 构建 → 预发布部署 → ≥3 条冒烟
      → 用户确认 → 正式发布（灰度/全量）
      → 发布后巡检 → 更新 CHANGELOG.md
      → 两份交付物落盘
      → 门禁自查（9 必检 / 2 建议）
      → 交回 tri-sdlc 审计
```

> 剖面为 `lite` 时本阶段未启用，tri-sdlc 不会派发。

## 设计原则

- **面向验收标准产出**：八维发布与 P7 门禁条目一一对应
- **冒烟 ≠ 功能测试**：功能验证归 P6，本阶段冒烟只确认部署后可用性
- **巡检 ≠ 监控**：本阶段是发布窗口内一次性核对，持续监控归 P8 `tri-ops`
- **不越权**：不判门禁、不推进阶段、不改业务代码、不在 P6 未过时强行发布

## 许可证

MIT
