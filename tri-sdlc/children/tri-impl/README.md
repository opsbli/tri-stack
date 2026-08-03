# tri-impl（tri-sdlc P4 编码实现子SKILL）

tri-sdlc 九阶段编排中的 **P4 编码实现专家子 SKILL**。接收 tri-sdlc 派发的阶段任务，按 P3 任务看板逐项编码落盘至用户工作区，产出 `implements.md` 与 `unit-test-report.md`，交 tri-sdlc 门禁审计。

## 特性

- **任务驱动**：每段代码可回指任务 ID，看板外功能须先申请补任务，杜绝夹带
- **看板回写**：完成即回写 `task-board.md` 状态，为 `P4-M1` 提供判定依据
- **不改上游规格**：发现设计缺陷记「设计偏差」并回报，绝不自行改设计后继续
- **测试必跑**：用例数 / 通过数 / 覆盖率带执行命令与输出摘要，禁止凭空写数字
- **合规五条**：原创不照搬 / 许可证兼容 / 依赖已授权 / 披露到位 / LICENSE 已声明
- **源码落工作区**：绝不写进 `.tribro/`，路径逐条登记

## 交付物

| 产物 | 位置 |
|---|---|
| `implements.md` | `.tribro/sdlc/<命名>/P4-implementation/` |
| `unit-test-report.md` | 同上 |
| 源码 | 用户工作区，路径登记于 `implements.md` |
| `task-board.md` 状态回写 | `.tribro/sdlc/<命名>/P3-devsetup/` |

## 目录结构

```
tri-impl/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-impl-full-testcases.md
```

## 安装

随 tri-sdlc 包分发，置于 `tri-sdlc/children/tri-impl/`。独立安装需先装 tri-sdlc：

```
skillhub install tri-sdlc --dir <目标目录>
```

> 只想直接写一段代码而不走全流程，请改用 `tri-coding`。

## 使用

```
tri-sdlc 派发 P4 阶段任务（附 P3 看板 + P2 设计 + P1 验收标准）
      → 加载技术栈规范与覆盖率阈值
      → 逐任务编码落工作区（对齐接口契约与数据模型）
      → 单测执行 + 覆盖率统计 + 合规五条自检
      → 回写任务状态
      → implements.md + unit-test-report.md 落盘
      → 门禁自查（8 必检 / 2 建议）
      → 交回 tri-sdlc 审计
```

> P4 在 full / standard / lite 三剖面下均启用，不可跳过。

## 设计原则

- **面向验收标准产出**：七维实现与 P4 门禁条目一一对应
- **自检不等于评审**：本阶段只做自检式把关，系统性评审结论归 P5 `tri-cr`
- **不越权**：不判门禁、不推进阶段、不改需求与设计、不做集成/验收测试

## 许可证

MIT
