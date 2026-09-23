# tri-devenv（tri-sdlc P3 开发准备子SKILL）

tri-sdlc 九阶段编排中的 **P3 开发准备专家子 SKILL**。接收 tri-sdlc 派发的阶段任务，读取 P2 设计三件套与 P1 需求，经六维准备产出 `devenv.md` 与 `task-board.md`，交 tri-sdlc 门禁审计。

## 特性

- **步骤照抄能跑**：环境搭建每步带版本号 + 验证命令，拦截「自行安装依赖」类模糊表述
- **分支三类齐全**：主干 / 特性 / 发布，各含命名规则与合并规则（含合并方式与前置条件）
- **任务五要素**：ID + 标题 + 关联需求 ID + 预估 + 负责角色，缺一即无效
- **三向校验**：任务→需求、需求→任务、设计→任务，杜绝悬空引用与设计无落地
- **工作区产物登记**：落工程骨架必须登记路径，不静默写入
- **不写业务代码**：本阶段只搭台子，功能实现归 P4

## 交付物

| 产物 | 位置 |
|---|---|
| `devenv.md` | `.tribro/sdlc/<命名>/P3-devsetup/` |
| `task-board.md` | 同上 |
| 工程配置骨架（可选） | 用户工作区，路径登记于 `devenv.md` |

## 目录结构

```
tri-devenv/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-devenv-full-testcases.md
```

## 安装

随 tri-sdlc 包分发，置于 `tri-sdlc/children/tri-devenv/`。独立安装需先装 tri-sdlc：

```
skillhub install tri-sdlc --dir <目标目录>
```

## 使用

```
tri-sdlc 派发 P3 阶段任务（附 P2 三件套 + P1 需求）
      → 六维准备（分支 → 环境 → 规范 → 提交 → 任务拆分 → 回链校验）
      → devenv.md + task-board.md 落盘
      → 工程骨架落工作区并登记
      → 门禁自查（7 必检 / 2 建议）
      → 交回 tri-sdlc 审计
```

> 剖面为 `standard` / `lite` 时本阶段未启用，tri-sdlc 不会派发。

## 设计原则

- **面向验收标准产出**：六维与 P3 门禁条目一一对应
- **任务看板是 P4 的输入**：`P4-M1` 会检查本看板任务状态是否全部完成
- **不越权**：不判门禁、不推进阶段、不写业务功能代码

## 许可证

MIT
