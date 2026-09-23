# tri-frontend-design

前端设计技能——为构建或重塑前端提供「风格锚点」驱动的可视化方向。把"前端设计"变成可由 AI 稳定执行的设计引擎：八个风格锚点各自锁定具体 CSS 令牌，配合"内容不是设计"纪律与发布前自检，交付高保真、不套话、不编造的前端。

蒸馏自开源 `frontend-design` 技能（原英文），按 tri-xxx 家族规范（12/13 章结构 + 版本检查门 + 26 条硬约束）合规化、中文化。

> 来源与归属：动效 / 多变体知识蒸馏自 emilkowalski/skills（MIT License, Copyright (c) 2026 Emil Kowalski），去产品化改写，保留法律归属声明，不建 LICENSE 文件。

## 特性

- **八个风格锚点**：瑞士风格 / 工业风 / 粗野主义 / 极光极繁主义 / 混沌极繁主义 / 复古未来主义 / 有机风 / 低保真。每个锚点锁定配色、字体、结构、质感到具体 CSS 令牌。
- **五步工作法**：情境 → 锚点（偏向出人意料）→ 差异化点 → 系统（匹配令牌）→ 实现。
- **单锚点铁律**：一个简报一个锚点，禁止杂交。
- **内容纪律**：§2 五项禁止（编造数据 / 填充标签 / 主题化替换 / 字形图标 / AI 套话）。
- **动效方向引擎（`motion` 模式）**：频率闸门 → 缓动/弹簧 → 可中断性 → GPU 属性白名单 → `prefers-reduced-motion` 同交；子动作 `build`/`review`/`find`/`audit`。
- **锚点↔动效基线映射（1+1>2）**：由锚点自动推导动效基线，`anchors.md` 八锚点各含 Motion baseline 段。
- **多变体探索（`variants` 模式）**：沿锚点内分歧轴产出 3–5 真正分歧变体 + picker harness + 权衡表。
- **发布前自检**：§5 六项逐条核对（含动效不浮）。
- **全量令牌规格**：`references/anchors.md` 是令牌单一事实源，含每个锚点的 Surface / Typography / Accent / Structure / Breaks if / Motion baseline。
- **7 个动效/变体 references**：`motion-standards.md`（数值真源）/ `motion-recipes.md`（13 配方）/ `motion-review.md`（十条标准）/ `motion-physics.md`（流体物理层）/ `motion-plan-template.md`（审计计划）/ `variants-picker.md`（多变体）/ `motion-vocabulary.md`（术语反查）。
- **版本检查门**：自带 `scripts/check_update.py`（第零步，四态判定，同源一致）。

## 目录结构

```
tri-frontend-design/
├── SKILL.md                       # 主入口：八锚点 + 动效引擎 + 多变体（三模式双引擎）
├── README.md
├── CHANGELOG.md
├── _meta.json
├── scripts/
│   └── check_update.py            # 版本检查与强制自动更新
├── references/
│   ├── anchors.md                 # 八个锚点全量令牌规格（含 Motion baseline）
│   ├── motion-standards.md        # 动效数值单一真源
│   ├── motion-recipes.md          # 13 个即用动效配方
│   ├── motion-review.md           # 十条不可协商标准 + 裁决
│   ├── motion-physics.md          # Apple 流体交互物理层
│   ├── motion-plan-template.md    # 自包含改进计划模板
│   ├── variants-picker.md         # 多变体 picker 规格
│   └── motion-vocabulary.md       # 100+ 动效术语反查词典
├── plans/
│   └── README.md                  # 运行时产物目录说明（audit 产出 plans/NNN-*.md）
└── tests/
    └── tri-frontend-design-full-testcases.md
```

## 安装

```bash
skillhub install tri-frontend-design --dir <目标目录>
```

## 使用

直接向 AI 提出前端设计需求即可，例如：

> "帮我做一个瑞士风格的数据看板，受众是金融分析师，内容是真实的季度营收数据。"

AI 会：选锚点 → 定差异化点 → 匹配令牌 → 审查内容纪律 → 交付设计方向与令牌规格 → 发布前自检。

## 测试

见 `tests/tri-frontend-design-full-testcases.md`（全场景测试用例，frontmatter 版本与 SKILL.md 强一致）。

## 设计原则

**追求出人意料。忠于锚点。内容有节制。绝不落入默认。**

> 设计不是逐字映射——风格锚点传达方向，令牌保信退守，内容命名真实，质量自检兜底。
