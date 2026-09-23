# 三方组件声明（THIRD-PARTY NOTICE）

> 本文件承载 tri-html 内置图表引擎（`scripts/viewer/`）的第三方来源声明与许可证义务，非本 skill 自身的许可证文件（本 skill 许可证以 frontmatter `license: MIT` 声明）。放置于 `references/` 下、不在用户可见交付物中出现，但 **MUST 随源码分发保留**。

## 内置图表引擎（scripts/viewer/）

- **二级来源**：外部项目自身基于 Cocoon-AI/architecture-diagram-generator（MIT, v1.0）。
- **再分发范围**：bin / renderers / schemas / delta / assets / recipes / references / examples / scripts（运行时子集；未含外部 test/ 与构建期生成器）。

## 外部同步约定

- 本 vendored 副本**不自动跟踪外部**：外部升级需维护者手动评估后重新同步，并在本文件更新版本锚点。外部演进差距的逐项登记见 `references/engine-evolution-notes.md`（2026-09-22 首次登记：工作流约束驱动编译器 / v1→v2 迁移通道 / 内置品牌目录 / 机器可读参数回执 / 字体自包含等 7 项）。
- 修改纪律：**外层适配、内层不动**——tri-html 的集成层（SKILL.md / build_html.py / 本目录外的包装脚本）可自由修改；`scripts/viewer/` 内部逻辑非必要不改动，改动 MUST 在本文件「修改说明」追加记录。
- 引擎内残留的 `viewer` 命名空间、`VIEWER:` 插槽标记、`viewer-` CSS 前缀均为重命名后的内部功能标识。

## 修改说明

- 2026-09-22（执行测试修复轮，三项引擎内改动，均有回归测试覆盖 `tests/run_exec_tests.py`）：
  1. `bin/viewer.mjs`：`runNode` 新增 worker 线程回退——当宿主环境禁止 node.exe 派生任何子进程（Windows 安全策略下 spawnSync 返回 EBUSY/EPERM）时，改经 `worker_threads` 在进程内执行同一渲染/检查脚本并以 SharedArrayBuffer+结果文件同步回传，保持 spawnSync 形结果契约不变；spawn 可用时行为与原版完全一致。
  2. `assets/template.html`：移除 Google Fonts（fonts.googleapis.com / fonts.gstatic.com）两处外部 `<link>` 引用——外部字体 CDN 违背产物「单文件零依赖、离线可打开」契约且在不可达网络会阻塞首屏；全部 font-family 规则本就有完整本地/系统等宽回退链，移除后渲染不受影响。
  3. `bin/viewer.mjs`：`commandValidate` / `commandRender` 补未知 `--选项` 与超量位置参数守卫（fail，exit 2），对齐 `commandDeliver` 既有守卫，消除静默吞错。

## 其他内联依赖

- Mermaid.js v10.9.1（MIT）：由 `scripts/build_html.py` 注入报告 HTML 时保留版权声明，详见该脚本注释。
