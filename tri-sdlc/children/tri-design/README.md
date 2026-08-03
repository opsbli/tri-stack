# tri-design（tri-sdlc P2 方案设计子SKILL）

tri-sdlc 九阶段编排中的 **P2 方案设计专家子 SKILL**。接收 tri-sdlc 派发的阶段任务，读取 P1 需求四件套，经八维设计产出设计三件套，交 tri-sdlc 门禁审计。

## 特性

- **Must 需求 100% 落点**：逐条映射到模块 / 接口 / 数据表，漏一条即视为未完成
- **选型必对比**：每个选型点候选 ≥2 + 选定 + 理由，杜绝「就用 XX」
- **接口五要素**：方法 / 路径 / 入参 / 出参 / 错误码，错误码 ≥2 类；CLI 与 SDK 同样适用
- **无数据库也要建模**：纯文件存储项目须给等价数据结构定义，不得跳过
- **指标可度量**：性能容量必须带单位数值，拦截「高性能」类空话
- **安全三项不缺**：鉴权 / 加密 / 越权防护，单机项目有等价答法

## 交付物

| 产物 | 位置 |
|---|---|
| `design.md` | `.tribro/sdlc/<命名>/P2-design/` |
| `api-contract.md` | 同上 |
| `data-model.md` | 同上 |

## 目录结构

```
tri-design/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-design-full-testcases.md
```

## 安装

随 tri-sdlc 包分发，置于 `tri-sdlc/children/tri-design/`。独立安装需先装 tri-sdlc：

```
skillhub install tri-sdlc --dir <目标目录>
```

## 使用

```
tri-sdlc 派发 P2 阶段任务（附 P1 四件套）
      → 八维设计（架构 → 需求映射 → 数据 → 接口 → 链路 → 选型 → 安全 → 性能）
      → 三件套落盘
      → 门禁自查（9 必检 / 3 建议）
      → 交回 tri-sdlc 审计
```

## 设计原则

- **面向验收标准产出**：八维与 P2 门禁条目一一对应
- **可评审**：产出物按技术评审（TRD）的检查口径组织
- **不越权**：不判门禁、不推进阶段、不写代码与任务看板

## 许可证

MIT
