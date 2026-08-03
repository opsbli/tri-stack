# tri-coding

编码开发下游执行 skill。读取 tri-intent 快照 §三 结构化结论，处理 I11（编码开发）意图，自主管理「需求 → 设计 → 任务 → 执行 → 实现报告」完整编码工作流。通过 registry 驱动的技术栈动态加载机制匹配项目技术栈并叠加编码规范，含双审批门 + 执行前确认 + 最小化原则门禁。当 tri-intent 快照下游路由建议指向本 skill 时激活。

## 特性

- **双审批门 + 执行前确认**：门①需求审计 → 门②设计审计 → 门③执行前确认，三道关卡严格串行，任一门未通过则携反馈回炉，禁止跳门抢跑直接写代码
- **registry 驱动技术栈加载**：内置 24 个技术栈 skill + 通用基底，覆盖语言/框架/平台/工具 5 大分类，支持叠加匹配（如 TypeScript + React + Tailwind），新增技术栈仅需追加注册表一行
- **复选框任务跟踪**：tasks.md 每个原子任务与测试条目含完成状态复选框，执行完成 `- [ ]` → `- [x]`，回炉重做重置回 `- [ ]`，与状态明细字段同步更新
- **最小化原则门禁**：执行前校验变更范围最小化，只实现任务清单范围内功能，不顺便重构、优化或清理无关代码；需扩大范围须经用户确认后追加
- **三态依赖检测**：独立安装时检测上游 tri-intent，支持快照模式（标准）/ 引导安装 / 降级模式三态逻辑
- **完整链路文档**：requirements.md → design.md → tasks.md → implements.md 四件套链路文档全程留痕，审计记录可追溯

## 目录结构

```
tri-coding/
├── SKILL.md              # 主入口：编码工作流 + 双审批门 + 执行前确认 + 技术栈加载方法论
├── templates/            # 链路文档模板
│   ├── requirements.md   # 编码需求说明书模板（门①载体）
│   ├── design.md         # 技术设计说明书模板（门②载体）
│   ├── tasks.md          # 编码任务清单+测试清单模板（门③载体+执行蓝图）
│   └── implements.md     # 编码实现清单报告模板（最终交付物）
├── references/           # 静态参考资料
│   └── license-compliance.md          # 代码版权与许可证合规完整参考
├── tech-skills/          # 技术栈子 skill（registry 驱动，可扩展）
│   ├── registry.md       # 技术栈注册清单（唯一扩展入口）
│   ├── README.md         # 如何添加新技术栈
│   ├── general.md        # 通用编程基底（始终加载）
│   ├── typescript.md     # TypeScript 语言规范
│   ├── react.md          # React 框架规范
│   ├── vuejs.md          # Vue.js 框架规范
│   ├── ...               # 更多技术栈（共 24 个技术栈 skill + 通用基底）
│   └── gitflow.md        # Git Flow 工具规范
├── 代码合规自查小卡片.html   # 提交/发布前一页式合规速查卡
├── CHANGELOG.md          # 版本变更记录
└── tests/
    └── tri-coding-full-testcases.md   # 45 条全场景全能力测试用例（审计版）
```

## 安装

将 `tri-coding/` 目录放入你的 skills 目录即可：

```bash
cp -r tri-coding/ /path/to/your/skills/
```

> 本 skill 依赖 tri-intent 进行意图识别与输入校验。若未安装 tri-intent，激活时会进入引导安装或降级模式（见 SKILL.md §上游依赖检测）。

## 使用

### 1. 编码工作流（核心流程）

收到 tri-intent 快照（L2 = I11）后，按以下链路串行推进：

```
快照 §三 → requirements.md → 门①审计 → design.md → 门②审计 → tasks.md → 门③执行前确认 → 执行 → implements.md
```

| 阶段 | 产出物 | 审批门 | 关键动作 |
|---|---|---|---|
| 1 | `requirements.md` | 门① | 从快照 §三 提取意图结论，明确功能需求 + 技术约束 + 验收标准 |
| 2 | `design.md` | 门② | 氛围校准 + 技术栈加载 + 模块/接口/数据模型/技术选型 |
| 3 | `tasks.md` | 门③ | 据 design.md 拆解原子任务 + 三层测试清单（UT/IT/AT）+ 依赖图 |
| 4 | 代码成果物 | — | 按 tasks.md 逐项编码 + 测试，复选框状态切换 |
| 5 | `implements.md` | — | 汇总执行记录 + 测试结果 + 变更说明 + 交付物清单 |

### 2. 技术栈加载

在 design.md 的氛围校准步骤中，读取 `tech-skills/registry.md` 按项目特征文件匹配技术栈：

- 始终加载 `general.md`（基底）
- 命中的技术栈 skill 可叠加多个（如 TypeScript + React + Tailwind）
- 全部未命中 → 仅用 general.md 兜底

新增技术栈无需修改 SKILL.md：在 `tech-skills/` 创建 `<tech-id>.md`，在 `registry.md` 追加一行即可。

### 3. 交付产物

链路文档落盘于 `.tribro/coding/<命名>/`，命名沿用 tri-intent 快照：

```
.tribro/coding/I11_20250211_143022_6a5c037d/
├── requirements.md
├── design.md
├── tasks.md
└── implements.md
```

## 测试

完整测试用例见 `tests/tri-coding-full-testcases.md`（45 条），覆盖元数据、强制执行契约、上游依赖检测与输入契约、技术栈加载机制、双审批门+执行前确认逻辑、链路文档产物、职责边界（tri-fix / tri-review / tri-sdlc / tri-plan / tri-content）、代码版权与许可证合规等全部能力点，含正例 / 诱饵反例 / 边界模糊三类。

## 设计原则

- **先方案后动手**：编码属设计类意图，必须经过需求审批 + 设计审批 + 执行前确认三道关卡，禁止跳门直接写代码
- **最小化变更**：只实现任务清单范围内功能，不顺便重构、优化或清理无关代码
- **registry 可扩展**：技术栈加载通过注册表驱动，新增技术栈零侵入，无需修改核心 SKILL.md
- **职责边界**：本 skill 既出方案也动手写代码；tri-plan 只出方案不写代码，tri-fix 专注调试修复
