# 代码剖析（tri-code-analyzer）

对任意技术栈代码库做**全维度深度剖析**：以架构师+程序员双视角产出五部分 Markdown 报告（架构拓扑 / 工程实现 / 风格审计 / Mermaid 四图 / 上手指南），每条事实性结论强制附 `file:line` 证据锚，技术栈无关。

## 特性（Features）

- **七阶段剖析管道**：教训预载→定位→识别→拓扑→穿透→横切→对照→交付；大仓库入口优先采样策略（依赖清单→构建配置→路由→核心链路→外围）。
- **教训文件读写闭环（v1.1.0）**：启动读取 `.tribro/code-analyzer/lessons.md`（历史经验教训，缺失静默跳过不报错）；执行结束 MUST 追加本次教训（场景/问题/规避），越用越准。
- **证据锚定铁律**：每条事实性结论附 `文件:行号` 或标识符锚；无锚结论显式标注「推断」+ 推理依据。
- **结论置信标注（v1.2.0）**：每个结论性判断必附置信度（高/中/低）+ 依据类型（事实 known/计算 computed/推断 inferred/常识 common/框架 iframe/猜测 guess）+ 可验证来源（官网 URL 或代码锚）；猜测类结论标低置信并提示人工验证。
- **反捏造条件响应**：「如有」维度（路由/状态/异步/实体/配置/工具库）全部给出有/无明确判定，不凭空造章节。
- **技术栈知识对照**：内置 9 张栈卡（ArkTS/HarmonyOS、Electron、Flutter、Qt、React Native、Taro、uni-app(x)、通用后端 Spring/Django/FastAPI/Go/Node/.NET、Agent Skills 插件），外部覆盖层接 `D:\demo\wikihub\` 本地知识库与各官方文档；未覆盖栈走 `acquire-unknown-stack.md` 获取协议自动建卡。
- **Mermaid 四图引擎**：架构图/时序图/ER 图/状态或流程图，逐图过渲染安全清单。
- **上手与行动指南**：断点调试路线、新功能开发 Checklist（附本项目参照文件）、P0/P1/P2 重构优先队列。
- **深度三档**：快速导览 / 标准剖析（默认）/ 深度穿透。

## 目录结构

```
tri-code-analyzer/
├── SKILL.md                                  # 主入口
├── README.md
├── CHANGELOG.md
├── scripts/
│   └── check_update.py                       # 版本检查（第零步硬门，与 tri-forge 同源）
├── references/
│   ├── analysis-framework.md                 # 五部分框架 + 七阶段管道 + Mermaid 安全清单
│   └── tech-stacks/
│       ├── INDEX.md                          # 技术栈索引（栈→卡→wikihub 锚点→官网→探测信号）
│       ├── arkts.md / electron.md / flutter.md / qt.md
│       ├── react-native.md / taro.md / uni-app.md
│       ├── agent-skills-plugin.md            # Agent Skills 插件栈卡
│       ├── generic-backend.md                # Spring/Django/FastAPI/Flask/Go/Node/.NET 分表
│       └── acquire-unknown-stack.md          # 未覆盖栈获取协议
└── tests/
    └── tri-code-analyzer-full-testcases.md
```

## 安装（Installation）

```bash
python ops/install-skills.py --target <目标目录>
```

- 本 skill 是 tri-intent 下游（I10 · code-analyzer 子类），建议同时安装 `tri-intent` 以获得完整意图路由。
- 支持独立安装：未装 tri-intent 时走三态降级（A 快照 / B 引导安装 / C 降级自构造输入）。

## 使用（Usage）

最小示例：

1. 触发：「帮我深度剖析这个代码库，我要接手这个项目」（经 tri-intent → L3=code-analyzer → 本 skill）。
2. 输入：目标代码库路径（+ 可选深度档位/关注维度）。
3. 预期产物：五部分剖析报告；对话内交付或落盘 `.tribro/code-analyzer/<命名>-analysis.md`；执行结束后经验教训自动追加至 `.tribro/code-analyzer/lessons.md`（下次执行自动预载规避）。

## 测试（Testing）

见 `tests/tri-code-analyzer-full-testcases.md`（全场景用例，含能力清单 A–H 分组覆盖）。

## 设计原则与注意事项

- **没有证据锚的结论不是分析，是猜谜**——本 skill 与「泛泛的项目总结」的根本区别。
- **与 tri-html（arch-viz 子类）边界**：tri-html 把架构**画出来**（HTML 交互图表）；本 skill 把代码**讲透**（报告+上手指南）。两样都要：先本 skill 报告（Mermaid 内嵌已覆盖图形），再续接 tri-html。
- **与 tri-review 边界**：本 skill 是「理解」（剖析现状），tri-review 是「评判」（质量审查打分）。
- 报告结论被纠错时按 SKILL.md §进化契约 回写栈卡/框架文件；每次执行的踩坑与有效经验沉淀入 `.tribro/code-analyzer/lessons.md`，启动时预载为规避清单（文件不存在时静默跳过）。
