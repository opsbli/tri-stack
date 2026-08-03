# 技术栈子 Skill 目录

> 本目录是 tri-coding 技术栈加载机制的实现层，存放各技术栈的编码规范子 skill。
> tri-coding 在 design.md 阶段（氛围校准步骤）通过 `registry.md` 动态匹配并加载。

## 目录结构

```
tech-skills/
├── registry.md       # 注册清单（唯一扩展入口）
├── general.md        # 通用编程基底（始终加载）
├── typescript.md     # TypeScript
├── react.md          # React
├── vuejs.md          # Vue.js
├── arkts.md          # 鸿蒙 ArkTS
├── taro.md           # Taro
├── python.md         # Python
├── golang.md         # Go
├── java.md           # Java
├── cpp.md            # C++
├── css.md            # CSS
├── nextjs.md         # Next.js
├── tailwind.md       # Tailwind CSS
├── uniapp.md         # uni-app
├── react-native.md   # React Native
├── flutter.md        # Flutter
├── swiftui.md        # SwiftUI
├── electron.md       # Electron
├── h5.md             # H5 移动端
├── wechat.md         # 微信小程序
├── django.md         # Django
├── fastapi.md        # FastAPI
├── flask.md          # Flask
├── git.md            # Git
└── gitflow.md        # Git Flow
```

## Skill 文件格式规范

每个技术栈 skill 文件必须遵循以下格式：

```markdown
---
name: tech-<tech_id>
description: <技术栈名称>开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供<技术栈>特定的编码标准与质量检查。
tech_id: <tech_id>
tech_name: <中文名称>
category: <language|framework|platform|tool>
---

# <技术栈名称> 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加<技术栈>特定规范。

## 技术栈定义
<简要定义与核心特性>

## 版本基线
<列出该技术栈的关键版本与破坏性变化，为编码规范提供版本语境>

## 编码规范（技术特定）
<只保留该技术独有的规范条目，通用原则（SOLID/DRY 等）由 general.md 覆盖，不重复>

## 质量检查清单（技术特定）
<只保留该技术独有的检查项>

## 参考资料
<官方文档、风格指南等链接>
```

## 设计原则

1. **只含技术特定内容**：通用编程规范（SDD 哲学、工作流程、通用检查清单、决策框架等）由 tri-coding 主 skill 和 `general.md` 覆盖，技术栈 skill 不重复
2. **精简聚焦**：每个文件聚焦该技术栈独有的编码标准、最佳实践和质量检查点
3. **可叠加**：多个技术栈 skill 可同时加载（如 TypeScript + React + Tailwind）
4. **基底 + 增强**：`general.md` 始终作为基底加载，其他技术栈 skill 作为增强层叠加

## 新增技术栈步骤

1. 在本目录创建 `<tech-id>.md`，按上述格式规范编写
2. 在 `registry.md` 注册表追加一行：`| <tech_id> | <名称> | <分类> | <触发规则> | <文件名> |`
3. 验证触发规则能正确匹配目标技术栈的项目特征
4. **无需修改 tri-coding/SKILL.md** —— 加载机制通过 registry.md 驱动，天然可扩展

## 分类体系

| 分类 | 说明 | 示例 |
|---|---|---|
| base | 通用基底，始终加载 | general |
| language | 编程语言层 | typescript, python, golang, java, cpp, css |
| framework | 框架层（依赖语言层） | react, vuejs, nextjs, taro, django, fastapi |
| platform | 平台层（特定运行环境） | arkts, electron, h5, wechat |
| tool | 工具层 | git, gitflow |
