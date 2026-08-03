---
name: tech-electron
description: Electron 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 Electron 桌面应用特定的编码标准与质量检查。
tech_id: electron
tech_name: Electron
category: platform
---

# Electron 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 Electron 桌面应用特定规范。

## 技术栈定义

Electron 是基于 Chromium 与 Node.js 的桌面应用框架，使用 Web 技术（HTML/CSS/JavaScript）构建跨平台桌面应用。核心特性：主进程/渲染进程双进程架构、IPC 进程间通信、预加载脚本（Preload Script）安全桥接、contextIsolation 安全隔离、跨平台（Windows/macOS/Linux）、原生能力调用。

## 版本基线

- **Electron 28+（ESM 支持）**：主进程与预加载脚本支持 ES Modules（`package.json` 中 `"type": "module"`），`require` 与 `import` 的互操作规则需注意；部分依赖库从 CJS 迁移到 ESM 后可能无法直接 `require`，属破坏性变化，需审查依赖与构建配置（electron-builder/esbuild/electron-forge）。底层 Chromium 升级也带来 Web API 与安全策略变化
- **contextIsolation 默认 true（安全破坏性变化）**：Electron 12+ 起 `contextIsolation` 默认为 `true`，渲染进程无法直接访问 `window.require`/Node.js API，必须通过 `contextBridge` 暴露白名单接口；旧代码直接在渲染进程使用 `require('electron')` 或 `require('fs')` 会全部失效，属必须修复的安全破坏性变化。同理 `nodeIntegration` 默认更严格为 `false`，`sandbox` 在较新版本趋向默认启用
- **Electron 30+（放弃旧 Windows 支持）**：Electron 30 起放弃 Windows 7/8/8.1 支持，最低要求 Windows 10；底层 Chromium 升级带来渲染与 API 行为变化（如 `Notification`、`<webview>` 标签行为、`protocol.handle` 替代 `protocol.registerSchemesAsPrivileged` 部分场景）。面向企业内网或老旧终端的应用需在升级前评估目标系统兼容性，并回归测试原生 API

## 编码规范（技术特定）

### 进程架构与目录结构

- **职责分离**：清晰分离主进程（Main Process）、渲染进程（Renderer Process）和预加载脚本（Preload Script）的职责
  - 渲染进程只负责 UI
  - 主进程负责系统交互
  - 通过预加载脚本进行安全桥接
- **目录结构**：遵循 Electron 推荐的目录结构（如 `src/main`, `src/renderer`, `src/preload`, `src/shared`），清晰分离关注点
- **模块化封装**：对常用的 Electron API 进行封装（如窗口管理、系统托盘、自动更新）

### 安全最佳实践

- **Context Isolation（上下文隔离）**：始终启用 `contextIsolation: true`
- **Node Integration（Node 集成）**：始终禁用渲染进程的 `nodeIntegration: false`（除极特殊情况外）
- **Sandbox（沙箱）**：尽可能启用 `sandbox: true`
- **Content Security Policy（CSP）**：为渲染进程配置严格的 CSP
- **IPC 安全**：验证所有 IPC 消息的 `sender`，不信任来自渲染进程的任意数据

### 进程间通信（IPC）

- **双向通信**：优先使用 `ipcRenderer.invoke` 和 `ipcMain.handle` 进行双向通信
- **contextBridge**：使用 `contextBridge` 安全地将 API 暴露给渲染进程，**切勿直接暴露整个 `ipcRenderer` 对象**
- **通道命名**：定义清晰的 IPC 通道名称常量，避免魔法字符串
- **类型安全**：对 IPC 数据结构定义共享的类型接口

### 进程管理与性能

- **进程管理**：妥善处理窗口生命周期（如 `ready-to-show`）、应用退出流程（`window-all-closed`）
- **性能优化**：避免阻塞主进程（Main Thread），耗时操作（如大文件读写、图像处理）应放入 Web Workers 或 Node.js Worker Threads 中
- **延迟加载**：遵循性能优化技术，如延迟加载模块、使用 `BrowserWindow` 的 `paintWhenInitiallyHidden` 选项
- **日志框架**：优先使用日志框架（如 `electron-log`）记录错误信息

### UI 与平台一致性

- **现代 UI 框架**：使用现代 UI 框架（如 Tailwind CSS、Shadcn UI、Radix UI）进行样式设计
- **平台一致性**：确保应用在 Windows、macOS 和 Linux 上有适配的 UI 表现（如标题栏样式、字体、快捷键）
- **原生体验**：模拟原生应用的交互模式（如右键菜单、拖拽、系统通知）

### 原有代码

- **谨慎修改**：在修复原有代码时，务必先阅读并理解原有代码，特别注意不要破坏现有的 IPC 协议和安全配置

## 质量检查清单（技术特定）

- [ ] 主进程/渲染进程/预加载脚本职责是否清晰分离
- [ ] 目录结构是否遵循 `src/main`、`src/renderer`、`src/preload`、`src/shared` 规范
- [ ] 是否启用 `contextIsolation: true`
- [ ] 是否禁用渲染进程的 `nodeIntegration`（设为 false）
- [ ] 是否尽可能启用 `sandbox: true`
- [ ] 是否为渲染进程配置严格的 CSP
- [ ] IPC 消息是否验证 `sender`，不信任渲染进程任意数据
- [ ] 是否使用 `ipcRenderer.invoke`/`ipcMain.handle` 进行双向通信
- [ ] 是否使用 `contextBridge` 暴露 API，而非直接暴露整个 `ipcRenderer`
- [ ] IPC 通道名称是否使用常量定义，避免魔法字符串
- [ ] IPC 数据结构是否定义共享类型接口
- [ ] 窗口生命周期是否妥善处理（ready-to-show / window-all-closed）
- [ ] 耗时操作是否放入 Web Workers 或 Worker Threads，未阻塞主进程
- [ ] 安全配置是否正确（Context Isolation、Node Integration 等）
- [ ] 是否在 Windows/macOS/Linux 上有适配的 UI 表现

## 参考资料

- [Electron 官方文档](https://www.electronjs.org/docs/latest)
- [Electron 安全指南](https://www.electronjs.org/zh/docs/latest/tutorial/security)
- [Electron IPC 通信](https://www.electronjs.org/docs/latest/tutorial/ipc)
- [contextBridge API](https://www.electronjs.org/docs/latest/api/context-bridge)
- [Node.js 最佳实践](https://nodejs.org/en/docs/guides/)
