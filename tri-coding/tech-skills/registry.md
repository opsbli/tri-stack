# 技术栈 Skill 注册清单（Registry）

> 本文件是 tri-coding 技术栈加载机制的**唯一注册入口**。
> 新增技术栈 skill 只需：① 在本目录创建 `<tech-id>.md` → ② 在本文件追加一条注册记录。
> tri-coding 在 design.md 阶段（氛围校准步骤）读取本文件，按触发规则匹配并加载对应技术栈 skill。

## 加载机制

```
tri-coding design.md 阶段·氛围校准
        │
        ▼
  读取本 registry.md
        │
        ▼
  按注册表「触发规则」逐条匹配项目特征
        │
        ├── 命中 ≥1 个 → 加载对应技术栈 skill（可叠加多个）
        ├── 全部未命中 → 加载 general.md（通用兜底）
        └── 始终加载 general.md 作为基底（技术栈 skill 作为增强层叠加）
```

**加载规则**：
1. `general.md` 始终作为基底加载，提供通用编程规范
2. 其余技术栈 skill 按触发规则匹配，可叠加多个（如 TypeScript + React）
3. 加载的技术栈 skill 内容注入 design.md 的「氛围校准」和「技术选型」环节
4. 执行阶段编码时遵循已加载技术栈 skill 的编码规范

**匹配顺序**（按分类层级依次匹配，避免遗漏）：
1. `base` → 始终加载 `general.md`
2. `language` → 按项目文件特征匹配语言层 skill
3. `framework` → 按依赖配置匹配框架层 skill，与语言层叠加
4. `platform` → 按平台特征文件匹配平台层 skill
5. `tool` → 按工具配置文件匹配工具层 skill

**互斥规则**（同类互斥，仅加载首个命中项）：
- 框架层互斥组：`react` ↔ `vuejs`（同一项目不应同时使用 React 和 Vue）
- 框架层互斥组：`django` ↔ `fastapi` ↔ `flask`（同一项目不应同时使用多个 Python Web 框架）
- 平台层互斥组：`arkts` ↔ `wechat` ↔ `h5`（同一项目通常面向单一平台）
- 互斥组内多个命中时，优先加载注册表中靠前的条目，其余跳过并记录告警

**可叠加示例**：
- `general` + `typescript` + `react` + `tailwind`（语言 + 框架 + 框架，无互斥冲突）
- `general` + `python` + `fastapi`（语言 + 框架，无互斥冲突）
- `general` + `typescript` + `taro`（语言 + 框架，无互斥冲突）

## 注册表

| tech_id | 技术栈名称 | 分类 | 触发规则（满足任一即命中） | 文件 |
|---|---|---|---|---|
| general | 通用编程 | base | 始终加载（基底） | `general.md` |
| typescript | TypeScript | language | `tsconfig.json` / `*.ts` / `*.tsx` / package.json 含 `typescript` 依赖 | `typescript.md` |
| python | Python | language | `*.py` / `requirements.txt` / `pyproject.toml` / `Pipfile` / `setup.py` | `python.md` |
| golang | Go | language | `*.go` / `go.mod` / `go.sum` | `golang.md` |
| java | Java | language | `*.java` / `pom.xml` / `build.gradle` / `build.gradle.kts` | `java.md` |
| cpp | C++ | language | `*.cpp` / `*.cc` / `*.h` / `*.hpp` / `CMakeLists.txt` / `*.cmake` | `cpp.md` |
| css | CSS | language | `*.css` / `*.scss` / `*.sass` / `*.less` | `css.md` |
| react | React | framework | package.json 含 `react` / `*.jsx` / `*.tsx` 且含 JSX | `react.md` |
| vuejs | Vue.js | framework | package.json 含 `vue` / `*.vue` | `vuejs.md` |
| nextjs | Next.js | framework | package.json 含 `next` / `next.config.*` / `app/` 或 `pages/` 目录 | `nextjs.md` |
| tailwind | Tailwind CSS | framework | package.json 含 `tailwindcss` / `tailwind.config.*` | `tailwind.md` |
| uniapp | uni-app | framework | package.json 含 `@dcloudio/uni-app` / `manifest.json` 含 uni-app | `uniapp.md` |
| taro | Taro | framework | package.json 含 `@tarojs/taro` / `config/index.*` 含 Taro 配置 | `taro.md` |
| react-native | React Native | framework | package.json 含 `react-native` / `*.ios.js` / `*.android.js` | `react-native.md` |
| flutter | Flutter | framework | `pubspec.yaml` / `*.dart` | `flutter.md` |
| swiftui | SwiftUI | framework | `*.swift` / `*.xcodeproj` / `Package.swift` | `swiftui.md` |
| arkts | 鸿蒙 ArkTS | platform | `*.ets` / `build-profile.json5` / `oh-package.json5` / `module.json5` | `arkts.md` |
| electron | Electron | platform | package.json 含 `electron` / `main.js` 引入 electron | `electron.md` |
| h5 | H5 移动端 | platform | 项目含移动端 H5 特征（viewport meta / `*.html` + 移动端 UI 框架） | `h5.md` |
| wechat | 微信小程序 | platform | `app.json` 含 `pages` / `project.config.json` / `*.wxml` | `wechat.md` |
| django | Django | framework | `manage.py` / `settings.py` 含 django / `requirements.txt` 含 `django` | `django.md` |
| fastapi | FastAPI | framework | `*.py` 且含 `fastapi` 导入 / `requirements.txt` 含 `fastapi` | `fastapi.md` |
| flask | Flask | framework | `*.py` 且含 `flask` 导入 / `requirements.txt` 含 `flask` | `flask.md` |
| git | Git | tool | `.git/` 目录 / `.gitignore` / `.gitattributes` | `git.md` |
| gitflow | Git Flow | tool | `.git/` 且分支命名含 `feature/` / `release/` / `hotfix/` 前缀 | `gitflow.md` |

## 分类说明

| 分类 | 说明 | 加载策略 |
|---|---|---|
| base | 通用基底，所有场景始终加载 | 强制加载 |
| language | 编程语言层 | 按项目文件特征匹配，可叠加 |
| framework | 框架层（依赖语言层） | 按依赖配置匹配，与语言层叠加 |
| platform | 平台层（特定运行环境） | 按平台特征文件匹配 |
| tool | 工具层 | 按工具配置文件匹配 |

## 扩展指南

新增技术栈 skill 步骤：

1. **创建 skill 文件**：在本目录创建 `<tech-id>.md`，遵循 `general.md` 的格式规范
2. **注册**：在本文件「注册表」表格追加一行，填写 tech_id / 名称 / 分类 / 触发规则 / 文件名
3. **验证**：确认触发规则能正确匹配目标技术栈的项目特征
4. **无需修改 tri-coding/SKILL.md**——加载机制通过本 registry.md 驱动，天然可扩展
