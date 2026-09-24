# tri-charter（tri-sdlc P0 立项与规划子SKILL）

tri-sdlc 九阶段编排中的 **P0 立项专家子 SKILL**。接收 tri-sdlc 派发的阶段任务，完成六维立项分析（业务背景与可证伪核心问题 / 范围双清单 / 三维可行性 / 里程碑 / 可度量目标 / 干系人假设风险），产出 `charter.md` 交 tri-sdlc 门禁审计。

## 特性

- **核心问题可证伪**：强制「谁 + 什么场景 + 什么损失」三要素检验，拦截「提升体验」类空话
- **范围双清单 + 交叉检验**：in-scope / out-of-scope 同时给出，杜绝后续范围漂移
- **可行性三维不缺项**：技术 / 资源 / 时间 各带结论与依据，「有条件可行」必须写明条件
- **面向门禁产出**：交付前逐条自查 `P0-M0`–`P0-M5`，不交半成品
- **回炉可闭环**：修订意见逐条对应修改并累积登记轮次

## 目录结构

```
tri-charter/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── references/
│   └── version-check-spec.md
├── scripts/
│   └── check_update.py
└── tests/
    └── tri-charter-full-testcases.md
```

## 安装

随 tri-sdlc 包分发，置于 `tri-sdlc/children/tri-charter/`。独立安装需先装 tri-sdlc：

```
python ops/install-skills.py --target <目标目录>
```

## 使用

```
tri-sdlc 派发 P0 阶段任务
      → 六维立项分析
      → charter.md 落盘 .tribro/sdlc/<命名>/P0-charter/
      → 门禁自查（6 必检 / 3 建议）
      → 交回 tri-sdlc 审计（闸门① + 闸门②）
      → FAIL 则携修订意见回炉，轮次 +1
```

## 交付物

| 产物 | 位置 |
|---|---|
| `charter.md` | `.tribro/sdlc/<命名>/P0-charter/` |

## 设计原则

- **面向验收标准产出**：方法论六维与 P0 门禁条目一一对应
- **不越权**：不判门禁、不推进阶段、不写其他阶段交付物
- **无占位交付**：残留 `<...>`/TODO/待定 视为未完成

## 许可证

MIT
