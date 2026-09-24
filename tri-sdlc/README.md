# tri-sdlc · 软件工程全生命周期驱动

> tri-intent 家族下游编排 skill。把一个软件项目拆成 **P0 立项 → P8 运维** 共 9 个阶段，逐阶段派发专职子 SKILL 产出规定交付物，每阶段用 **68 条必检项**自动审计，审不过自己打回重做，审过了再交你确认。

## 特性

- **九阶段全覆盖**：源自 `docs/SDLC工作流.md` 阶段 0–8 的 51 条原子任务，无遗漏收编立项、开发准备、运维监控三段常被跳过的环节。
- **子 SKILL 分工**：9 个阶段各有专职子 SKILL（`children/`），编排器只管调度与审计，不越俎代庖写内容。
- **双闸门门禁**：闸门① 自动审计（逐条对照验收标准，必检项 FAIL 即硬阻断）+ 闸门② 用户确认。快速模式下闸门② 可自动放行，闸门① 永不降标准。
- **回炉可执行**：门禁 FAIL 输出的修订意见含「未过项 → 问题 → 修订要求 → 责任子 SKILL」四要素，可直接回炉重做；同阶段连续 3 轮 FAIL 自动停机请求人工介入。
- **状态机 + 级联回退**：`manifest.md` 维护 10 态阶段状态机；`回退到 P2` 会把 P3–P8 一律置 `失效` 并标记 `stale`，杜绝「上游改了下游还挂着已通过」。
- **自然语言驱动**：12 类指令（启动/进度/通过/打回/回退/跳过/切剖面/重审/快速模式/暂停/继续/终止），无需记命令格式。
- **三种执行剖面**：`full`(P0–P8) / `standard`(跳过 P3、P8) / `lite`(P1 P2 P4 P6)，按项目体量裁剪，未启用阶段不触发门禁。
- **跨阶段一致性核对**：需求 ID 贯穿设计、任务、测试；范围不得漂移出 charter 的 in-scope；阈值按 manifest → P2/P3 约定 → 默认逐级继承。
- **产物分流**：链路文档进 `.tribro/sdlc/`，源码与 `CHANGELOG.md` 进用户工作区。

## 目录结构

```
tri-sdlc/
├── SKILL.md                          主入口
├── README.md
├── CHANGELOG.md
├── gates/
│   └── acceptance-criteria.md        九阶段验收标准总表（68 必检 + 21 建议）
├── templates/
│   ├── manifest.md                   主控清单模板
│   └── gate-report.md                门禁审计报告模板
├── tests/
│   ├── tri-sdlc-full-testcases.md
│   └── tri-sdlc-e2e-testreport.md
└── children/
    ├── tri-charter/    P0 立项与规划
    ├── tri-require/    P1 需求分析
    ├── tri-design/     P2 方案设计
    ├── tri-devenv/     P3 开发准备
    ├── tri-impl/       P4 编码实现
    ├── tri-cr/         P5 代码评审
    ├── tri-test/       P6 测试验证
    ├── tri-release/    P7 构建与发布
    └── tri-ops/        P8 运维与监控
```

## 安装

```bash
python ops/install-skills.py --target <目标目录>
```

9 个子 SKILL 随包分发，无需单独安装。建议同时安装上游：

```bash
python ops/install-skills.py --target <目标目录>
```

未安装 tri-intent 时本 skill 进入引导安装模式，用户拒绝安装则可降级执行（精度低于标准链路）。

## 使用

### 启动

```
按完整流程做一个「待办事项 CLI 工具」
```

skill 会先确认执行剖面，再初始化 `manifest.md`，进入 P0。

### 查看进度

```
现在到哪了？
```

输出阶段状态表 + 当前门禁结论 + 下一步动作，**不改变任何状态**。

### 确认与打回

```
通过                          → 闸门② 放行，进入下一阶段
打回，非功能需求缺兼容性一条    → 当前阶段回炉，轮次 +1
回退到 P2                     → P2 重做，P3–P8 级联置失效
跳过 P8                       → 登记理由与风险后跳过
快速模式                      → 闸门② 自动放行（闸门① 仍硬阻断）
```

### 交付物位置

```
.tribro/sdlc/<问题类型>_<日期>_<时间>_<会话ID>/
├── manifest.md          主控状态机
├── summary.md           交付汇总
├── P0-charter/          charter.md + gate-report.md
├── P1-requirements/     requirements / user-stories / acceptance-criteria / traceability-matrix + gate-report
├── P2-design/           design / api-contract / data-model + gate-report
├── P3-devsetup/         devenv / task-board + gate-report
├── P4-implementation/   implements / unit-test-report + gate-report
├── P5-code-review/      review-report + gate-report
├── P6-testing/          test-plan / test-report / defects + gate-report
├── P7-release/          release-plan / release-report + gate-report
└── P8-operations/       ops-runbook / monitoring + gate-report
```

源代码、构建产物、`CHANGELOG.md` 落**用户工作区**，路径记录在 `implements.md` / `release-report.md`。

## 测试

- `tests/tri-sdlc-full-testcases.md`：全场景测试用例，按 A–H 八组能力清单逐条覆盖。
- `tests/tri-sdlc-e2e-testreport.md`：端到端实跑测试报告，覆盖全阶段、全指令、门禁 FAIL 回炉与级联回退。

## 设计原则

1. **编排与执行分离**：编排器只做调度、审计、汇总；专业内容一律由子 SKILL 产出，替换子 SKILL 实现不影响编排逻辑。
2. **门禁单一事实源**：所有验收标准集中在 `gates/acceptance-criteria.md`，审计只能引用其条目编号，杜绝临场造标准。
3. **禁跳门抢跑**：状态机保证前一阶段未 `已通过`/`已跳过`，后一阶段不得启动实质工作。
4. **回炉必须可执行**：修订意见四要素齐备，否则视为无效意见。
5. **零改动可扩展**：新增阶段 = 建子 SKILL 目录 + 追加标准一节 + 路由表追加一行；新增验收标准 = 表格追加一行。
6. **状态与磁盘一致**：manifest 声称「已通过」的阶段，其交付物必须实际存在。

## 与相邻 skill 的边界

| skill | 边界 |
|---|---|
| `tri-coding` | 单功能四步闭环 vs 整项目九阶段闭环；P4 复用其技术栈规范与合规红线 |
| `tri-plan` | 产出规划文档本身 vs 驱动实现的工程交付物链 |
| `tri-workflow` | 产出流程定义（CI/DAG/审批模板） vs 驱动真实项目走完流程 |
| `tri-review` | 独立代码审查工作流 vs P5 复用其审查维度但门禁归 tri-sdlc |
| `tri-action` | 单次带副作用动作 vs 多阶段长程编排 |
| `tri-loop` | 长期运行的知识域/循环体 vs 有明确终点的项目交付 |

## 许可证

MIT（见 `SKILL.md` frontmatter `license` 字段）。
