# tri-test（tri-sdlc P6 测试验证子SKILL）

tri-sdlc 九阶段编排中的 **P6 测试验证专家子 SKILL**。接收 tri-sdlc 派发的阶段任务，依据 P1 验收标准编制并执行三层测试，产出 `test-plan.md`、`test-report.md`、`defects.md`，交 tri-sdlc 门禁审计。

## 特性

- **验收标准 100% 覆盖**：每条 AC 至少一条用例，无法自动化的出人工验收用例
- **三层必答**：单元 / 集成 / 用户验收，不适用层须写理由
- **真实执行**：结果须附命令或人工执行记录，禁止编造通过率
- **缺陷四要素**：ID + 级别 + 可执行复现步骤 + 状态
- **Critical 清零**：严重缺陷不清零不放行，回报 tri-sdlc 判回炉 P4
- **复测闭环**：已修缺陷逐条复测，不通过即重开并计入遗留

## 交付物

| 产物 | 位置 |
|---|---|
| `test-plan.md` | `.tribro/sdlc/<命名>/P6-testing/` |
| `test-report.md` | 同上 |
| `defects.md` | 同上 |
| 自动化脚本（可选） | 用户工作区，路径登记于 `test-plan.md` |

## 目录结构

```
tri-test/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-test-full-testcases.md
```

## 安装

随 tri-sdlc 包分发，置于 `tri-sdlc/children/tri-test/`。独立安装需先装 tri-sdlc：

```
skillhub install tri-sdlc --dir <目标目录>
```

## 使用

```
tri-sdlc 派发 P6 阶段任务（附 P1 验收标准 + P4 实现 + P5 评审）
      → 编制测试计划（用例八要素 + 覆盖映射 100%）
      → 三层执行（单元 / 集成 / 用户验收）
      → 缺陷四要素登记与分级
      → 复测与回归（Critical 清零、闭环）
      → 三份交付物落盘
      → 门禁自查（7 必检 / 2 建议）
      → 交回 tri-sdlc 审计
```

> P6 在 full / standard / lite 三剖面下均启用，不可跳过。

## 设计原则

- **面向验收标准产出**：六维验证与 P6 门禁条目一一对应
- **动态验证与静态审查分工**：P5 查代码，P6 跑结果，缺陷台账不混用
- **不越权**：不判门禁、不推进阶段、不改代码与需求设计、不自行降阈值

## 许可证

MIT
