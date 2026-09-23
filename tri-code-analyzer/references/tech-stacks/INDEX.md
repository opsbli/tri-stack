---
name: tech-stacks-index
description: tri-code-analyzer 技术栈知识库索引——栈→知识卡→本地深读锚点（wikihub）→官方文档→探测信号。
---

# 技术栈知识库索引（INDEX）

> 阶段 2「识别」的路由表：按探测信号（按优先级从上到下匹配）定位栈卡，读取栈卡后用其「分析要点」校准剖析。本索引是 skill 与知识卡的唯一关联点。

## 使用规则

1. 探测顺序：从上到下，某行「主信号」全部命中即选定（主信号必中原则）；「辅信号」仅用于细化打包方式 / 子栈，不参与命中判定。多栈主信号同时命中（如 Flutter + 通用后端 Go）→ 全部读卡，主栈取构建产物目标平台。
2. 未命中 → 读 `acquire-unknown-stack.md` 执行获取协议（官网抓取→建卡→回登本索引）。
3. 深读锚点：`D:\demo\wikihub\` 为本机外部覆盖层，仅当需要框架 API 级细节时按锚点查阅；wikihub 不存在时只用栈卡 + 官网。

## 索引表

| 技术栈 | 知识卡 | 探测信号（主信号必中 · 辅信号加权） | 本地深读锚点（wikihub） | 官方文档 |
|---|---|---|---|---|
| ArkTS / HarmonyOS | `arkts.md` | 主信号：`module.json5` 且 `.ets` 文件（或 `oh-package.json5`）；辅信号：`entry/src/main` | `D:\demo\wikihub\arkts\`（9114+ md）、`D:\demo\wikihub\refrerence\arkts\` | https://developer.huawei.com/consumer/cn/doc/ |
| Electron | `electron.md` | 主信号：devDependencies 含 `electron`；辅信号：`electron-builder` / `@electron-forge/cli` / `electron-forge` / 主进程入口 `main.js\|ts\|src/index.js` | `D:\demo\wikihub\electron\`、`D:\demo\wikihub\refrerence\electron\` | https://www.electronjs.org/docs/latest/ |
| Flutter / Dart | `flutter.md` | 主信号：`pubspec.yaml` 含 `flutter` 依赖 或 `.dart` 文件；辅信号：`lib/main.dart` | `D:\demo\wikihub\flutter\`、`D:\demo\wikihub\refrerence\flutter_samples\` | https://docs.flutter.dev/ |
| Qt / C++ | `qt.md` | 主信号：构建配置含 Qt 标识（`.pro` / `CMakeLists.txt` 含 `Qt` / `*.qml` 文件）；辅信号：`Q_OBJECT` 宏 / `#include <Q...>` | `D:\demo\wikihub\qt\`、`D:\demo\wikihub\refrerence\qt.wiki\` | https://doc.qt.io/ |
| React Native | `react-native.md` | 主信号：依赖含 `react-native`；辅信号：`react-native.config.js` / `ios/`+`android/` 目录 | `D:\demo\wikihub\react-native\`、`D:\demo\wikihub\refrerence\ohos_react_native\` | https://reactnative.dev/docs |
| Taro | `taro.md` | 主信号：依赖含 `@tarojs/taro`；辅信号：`config/index.js(ts)` | `D:\demo\wikihub\taro\`、`D:\demo\wikihub\refrerence\taro\` | https://docs.taro.zone/ |
| uni-app / uni-app x | `uni-app.md` | 主信号：`manifest.json` 且 `pages.json`（两者皆有，缺一不算）；辅信号：依赖含 `@dcloudio/uni-app` / `.uvue` 文件 | `D:\demo\wikihub\uni-app\`、`D:\demo\wikihub\refrerence\uni-app-uni-app-x\` | https://uniapp.dcloud.net.cn/ |
| Agent Skills 插件 | `agent-skills-plugin.md` | 主信号：`skills/*/SKILL.md`（YAML frontmatter）或根目录 `SKILL.md`（YAML frontmatter）；辅信号：`.claude-plugin/plugin.json` / `hooks/session-start` / 平台适配器目录（`.opencode/.pi/.gemini/.hermes-plugin` 等） | 无 | https://agentskills.io/specification |
| 通用后端（Spring/Django/FastAPI/Flask/Go/Node/.NET） | `generic-backend.md` | 清单文件：`pom.xml`·`build.gradle(.kts)`·`go.mod`·`requirements.txt`/`pyproject.toml`·`*.csproj`·`Cargo.toml`（**不含裸 `package.json`**——前端/后端共有，单独出现不判后端，需配合框架入口 token）；或框架入口：`@SpringBootApplication`·`FastAPI()`·`Flask(__name__)`·`gin.Engine`·`express()`·`@Module()`；.NET 以 `*.csproj` 清单判定（不用 `Program.cs` 文件名片段子串匹配）；子栈信号见 generic-backend.md 分表 | 无 | 按卡内分表 URL |
| 未覆盖栈 | `acquire-unknown-stack.md` | 以上均未命中 | — | 动态获取 |

## 装配与覆盖优先级

- 本目录各卡为「用户指定层」；`D:\demo\wikihub\` 与官网为「外部覆盖层」。
- 栈卡与 wikihub/官网冲突的处置：以**栈卡结论 + 外部原文佐证**注明分歧；官网证实栈卡过时 → 回写更新栈卡（MINOR bump）。
- 新增栈卡后 MUST：① 更新本索引表一行；② 在卡内标注深读锚点（若 wikihub 有对应目录）；③ bump skill 版本记 CHANGELOG。
