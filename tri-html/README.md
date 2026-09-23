# tri-html · 架构可视化分析

> tri-xxx 家族下游执行 skill · 认领 I10 arch-viz 子类 · 以系统架构设计师视角对项目进行六维架构分析，双引擎生成可视化产物：主报告单文件 HTML + viewer 高精度交互图表。

## 特性

- **六维架构分析**：架构设计 / 目录结构 / 技术栈 / 代码设计 / 功能设计 / 特殊设计（安全/性能/可观测性）
- **双渲染引擎**：
  - **viewer 高精引擎**（内置，零运行时 npm 依赖，Node ≥ 18）：架构图 / 工作流 / 时序图 / 数据流 / 生命周期五类技术图，Typed JSON IR → 确定性校验 → 独立单文件交互 HTML（深浅主题、搜索聚焦、路径探查、角色透镜、故事播放、PNG/SVG/WebM/分享卡导出）
  - **Mermaid 兼容模式**：目录树 / 技术栈矩阵 / 类图 / ER 图 / 旅程图，内联进主报告
- **showcase 客观门禁**：每张 viewer 图表 9 项检查（Schema/布局/HTML·SVG/线路/标签净空）全过才交付；失败输出结构化诊断（规则码 + 精确对象 + 测量证据 + supportedFixes），聚焦修复上限 2 轮
- **架构差分（显式启用）**：`compare` 将两份已校验架构快照对比为 Before / Delta / After，精确区分新增/删除/语义变化/移动
- **主报告单文件 HTML**：内联 CSS/JS + Mermaid.js，零外部依赖，可双击打开、可离线分享；viewer 图表以链接卡片嵌入
- **双审批门**：门①分析范围确认（含引擎模式）+ 门②HTML 交付确认（含 deliver 客观回执）
- **降级链（绝不阻断）**：Node 缺失 → 自动回落全 Mermaid 兼容模式；无 Chrome → visual-check 优雅跳过
- **三态外部检测**：快照模式 / 待识别 / 引导安装 / 降级模式
- **架构观察**：发现的问题按 BLOCKER/MAJOR/MINOR 三级标注，含修复建议
- **主题切换**：浅色/深色双主题，localStorage 记忆
- **交互组件**：折叠/展开维度、图表源码切换、图表全屏、复制代码

## 目录结构

```
tri-html/
├── SKILL.md                          # 主入口
├── README.md                         # 本文件
├── CHANGELOG.md                      # 版本变更记录
├── references/
│   ├── analysis-dimensions.md        # 六维分析维度详细参考
│   ├── mermaid-templates.md          # Mermaid 图表语法模板库
│   ├── viewer-authoring.md           # viewer 引擎作者契约（类型路由/创作不变量/修复循环）
│   ├── engine-evolution-notes.md     # 外部引擎演进对照登记（能力边界 + 同步评估要点）
│   ├── THIRD-PARTY-NOTICE.md         # vendored 引擎三方声明与许可证义务
│   └── version-check-spec.md       # 版本门细则（STUB 指针，NEVER 内联）
├── scripts/
│   ├── build_html.py                 # 单文件 HTML 组装器 + viewer 引擎集成
│   └── viewer/                       # 内置高精度图表引擎
│       ├── bin/viewer.mjs            # CLI：render/validate/deliver/compare/preview/visual-check/guide/brands/doctor/demo
│       ├── renderers/                # 五类渲染器 + shared 引擎内核
│       ├── schemas/                  # Typed JSON IR Schema
│       ├── delta/                    # architecture compare
│       ├── assets/template.html      # Viewer Runtime 模板
│       ├── references/               # authoring-contract / delivery-contract / viewer-runtime
│       ├── examples/                 # 各类型 IR 示例
│       └── recipes/                  # 场景配方（guide 数据源）
└── tests/
    ├── run_exec_tests.py             # 可执行面自动化测试（31 用例真实执行 + 硬性断言）
    └── tri-html-full-testcases.md    # 全场景测试用例
```

## 安装

```bash
skillhub install tri-html --dir <目标目录>
```

## 使用

### 标准模式（经 tri-intent 路由）

用户说「分析这个项目的架构」「生成项目架构可视化 HTML」「画一张项目架构图」等，tri-intent 识别为 I10 arch-viz 子类后路由到本 skill。

### 降级模式（独立使用）

未安装 tri-intent 时可直接调用，需自构造输入：

1. 扫描项目结构（`ls` / `find` / 读取 `package.json` 等）
2. 执行六维分析（参考 `references/analysis-dimensions.md`）
3. 探测渲染引擎：`python scripts/build_html.py --check-engine`
4. 五类技术图按 `references/viewer-authoring.md` 契约写 Typed JSON IR 并 validate/deliver；其余图表写 Mermaid
5. 组装 `analysis.json`（六维结论 + Mermaid 源码 + viewer_diagrams[]）
6. 运行 `python scripts/build_html.py --analysis analysis.json --out myapp-arch-viz.html`

### build_html.py 用法

```bash
# 标准用法（自动探测引擎：有 Node → viewer 图表高精渲染，无 → 全 Mermaid 兼容）
python scripts/build_html.py --analysis analysis.json --out myapp-arch-viz.html

# 仅校验不输出
python scripts/build_html.py --analysis analysis.json --out dummy.html --dry-run

# 仅探测 viewer 引擎可用性（退出码 0=可用 / 3=回落 Mermaid）
python scripts/build_html.py --check-engine
```

### viewer 引擎直接调用（高级）

```bash
cd scripts/viewer
node bin/viewer.mjs doctor              # 引擎健康自检
node bin/viewer.mjs demo /tmp/out       # 生成示例成品
node bin/viewer.mjs guide "CI/CD 流程" --json          # 场景→图类型路由
node bin/viewer.mjs validate architecture ir.json --quality showcase --json
node bin/viewer.mjs deliver architecture ir.json out.html --quality showcase --json
node bin/viewer.mjs compare architecture base.json head.json delta.html --json   # 架构差分
```

## analysis.json 格式

```json
{
  "meta": {
    "project_name": "myapp",
    "project_path": "/path/to/myapp"
  },
  "dimensions": {
    "architecture": {
      "title": "架构设计",
      "conclusion": "本项目采用分层单体架构...",
      "charts": [
        {"title": "Context 图", "mermaid": "C4Context\n  title ..."}
      ]
    },
    "directory": {"title": "...", "conclusion": "...", "charts": [...]},
    "techstack": {"title": "...", "conclusion": "...", "charts": [...]},
    "code": {"title": "...", "conclusion": "...", "charts": [...]},
    "function": {"title": "...", "conclusion": "...", "charts": [...]},
    "special": {"title": "...", "conclusion": "...", "charts": [...]}
  },
  "viewer_diagrams": [
    {
      "type": "architecture",
      "title": "运行时架构图",
      "ir": { "...": "Typed JSON IR（内联对象）或 IR 文件路径字符串" },
      "quality": "showcase"
    }
  ],
  "observations": [
    {"severity": "major", "title": "目录嵌套过深", "description": "...", "suggestion": "..."}
  ]
}
```

> 六维键 `architecture/directory/techstack/code/function/special` 必须齐全，缺一不可；`viewer_diagrams[]` 可选（缺省=全 Mermaid 兼容模式）。IR 字段契约见 `scripts/viewer/schemas/` 与 `references/viewer-authoring.md`。

## 测试

```bash
# 引擎健康
node scripts/viewer/bin/viewer.mjs doctor
python scripts/build_html.py --check-engine

# 全场景测试用例
cat tests/tri-html-full-testcases.md
```

## 设计原则

1. **规范是事实源**：六维分析维度、图表模板、viewer 作者契约均在 `references/` 单点维护，SKILL.md 仅留指针
2. **确定性算法下沉**：HTML 组装与 viewer 引擎调用逻辑在 `scripts/build_html.py`，引擎内部为 vendored 组件（外层适配、内层不动）
3. **单文件零依赖**：主报告与每张 viewer 成品均可离线打开，NEVER 依赖外部 CDN（Mermaid.js 内联；viewer 引擎自包含）
4. **客观门禁优先**：viewer 图表以 showcase 校验（9 项检查）与 deliver 回执（SHA-256）作为客观验收材料，主观审美让位于可验证事实
5. **双审批门护栏**：门①范围确认防分析跑偏，门②交付确认防半成品落地
6. **降级不阻断**：Node 缺失 / 引擎故障 / 无 Chrome 均有明确降级路径，且降级口径必须声明
7. **只分析不改代码**：发现问题记录于「架构观察」，修复由 tri-coding/tri-fix 执行

