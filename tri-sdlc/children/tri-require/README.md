# tri-require（tri-sdlc P1 需求分析子SKILL）

tri-sdlc 九阶段编排中的 **P1 需求分析专家子 SKILL**。接收 tri-sdlc 派发的阶段任务，读取 P0 `charter.md`，经六步需求工程产出需求四件套，交 tri-sdlc 门禁审计。

## 特性

- **ID 贯穿全链路**：`REQ-nnn` 唯一编号，作废只标记不删号，P2/P3/P4/P6 均可回溯
- **非功能不漏项**：性能 / 安全 / 兼容 三类各 ≥1 条，不适用必须显式声明理由
- **验收标准可判定**：强制 Given-When-Then，拦截「运行正常」「性能达标」类无效表述
- **矩阵双向连通**：自动检查孤儿需求与无源验收标准
- **范围不漂移**：逐条核对 charter in-scope，超出者进「范围外候选」并提请变更确认
- **基线可冻结**：版本号 + 冻结时间 + 冻结声明，回炉递增

## 交付物

| 产物 | 位置 |
|---|---|
| `requirements.md` | `.tribro/sdlc/<命名>/P1-requirements/` |
| `user-stories.md` | 同上 |
| `acceptance-criteria.md` | 同上 |
| `traceability-matrix.md` | 同上 |

> 本阶段 `acceptance-criteria.md` 是**项目需求验收标准**，与 tri-sdlc 的 `gates/acceptance-criteria.md`（门禁标准）不是同一份文件。

## 目录结构

```
tri-require/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── tests/
    └── tri-require-full-testcases.md
```

## 安装

随 tri-sdlc 包分发，置于 `tri-sdlc/children/tri-require/`。独立安装需先装 tri-sdlc：

```
python ops/install-skills.py --target <目标目录>
```

## 使用

```
tri-sdlc 派发 P1 阶段任务（附 charter.md）
      → 六步需求工程（采集分类 → ID 优先级 → 故事 → 验收标准 → 矩阵 → 基线冻结）
      → 四件套落盘
      → 门禁自查（8 必检 / 3 建议）
      → 交回 tri-sdlc 审计
```

## 设计原则

- **面向验收标准产出**：六步与 P1 门禁条目一一对应
- **验收标准 ≠ 测试用例**：本阶段定「什么算过」，P6 定「怎么验」
- **不越权**：不判门禁、不推进阶段、不写设计与测试用例

## 许可证

MIT
