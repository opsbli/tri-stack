# tri-html · 架构可视化分析

> tri-xxx 家族下游执行 skill · 认领 I10 arch-viz 子类 · 以系统架构设计师视角对项目进行六维架构分析，生成单文件 HTML 可视化报告。

## 特性

- **六维架构分析**：架构设计 / 目录结构 / 技术栈 / 代码设计 / 功能设计 / 特殊设计（安全/性能/可观测性）
- **单文件 HTML**：内联 CSS/JS + Mermaid.js，零外部依赖，可双击打开、可离线分享
- **Mermaid 图表**：C4 架构图 / 目录树 / 技术栈矩阵 / 类图 / ER 图 / 旅程图 / 状态机 / 监控拓扑
- **双审批门**：门①分析范围确认 + 门②HTML 交付确认
- **三态上游检测**：快照模式 / 待识别 / 引导安装 / 降级模式
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
│   └── mermaid-templates.md          # Mermaid 图表语法模板库
├── scripts/
│   └── build_html.py                 # 单文件 HTML 组装器
└── tests/
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
3. 组装 `analysis.json`（六维结论 + Mermaid 源码）
4. 运行 `python scripts/build_html.py --analysis analysis.json --out myapp-arch-viz.html`

### build_html.py 用法

```bash
# 标准用法
python scripts/build_html.py --analysis analysis.json --out myapp-arch-viz.html

# 仅校验不输出
python scripts/build_html.py --analysis analysis.json --out dummy.html --dry-run
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
  "observations": [
    {"severity": "major", "title": "目录嵌套过深", "description": "...", "suggestion": "..."}
  ]
}
```

> 六维键 `architecture/directory/techstack/code/function/special` 必须齐全，缺一不可。

## 测试

```bash
# 全场景测试用例
cat tests/tri-html-full-testcases.md
```

## 设计原则

1. **规范是事实源**：六维分析维度与图表模板均在 `references/` 单点维护，SKILL.md 仅留指针
2. **确定性算法下沉**：HTML 组装逻辑在 `scripts/build_html.py`，避免散文描述让模型自律复现
3. **单文件零依赖**：产物 HTML 必须可离线打开，NEVER 依赖外部 CDN（Mermaid.js 内联）
4. **双审批门护栏**：门①范围确认防分析跑偏，门②交付确认防半成品落地
5. **只分析不改代码**：发现问题记录于「架构观察」，修复由 tri-coding/tri-fix 执行
