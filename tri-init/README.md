# 项目初始化（tri-init）

> 将任意项目接入 tri-stack 开发流程：扫描技术栈 → 生成 AGENTS.md + project-profile → 创建 .tribro/。

## 使用

```
用户：初始化 D:/workspaces/ops-pilot 和 D:/workspaces/ops-pilot-web
     ↓
tri-init 扫描两个项目 → 检测 Java/Maven/RuoYi + TS/Vite
     ↓
生成 AGENTS.md（AI 协作编码规范）+ project-profile.json
     ↓
创建 .tribro/ 产物目录
     ↓
后续 tri-coding / tri-review 直接消费 project-profile
```

## 安装

支持独立安装（两态上游检测）。
