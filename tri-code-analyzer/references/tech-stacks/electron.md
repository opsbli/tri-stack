---
name: stack-electron
description: Electron 栈卡——主/渲染进程架构、IPC 分析要点、常见坑。
---

# 栈卡：Electron

## 探测信号

- devDependencies 含 `electron`（及 `electron-builder`/`electron-vite`/`forge`）；主进程入口 `main.js|main.ts`（package.json `main` 字段）。
- 渲染层任意（React/Vue/原生）； preload 脚本 + `contextBridge` 是现代项目标志。

## 工程惯例（分析要点校准基线）

- **进程模型（核心）**：主进程（Node 能力、窗口/生命周期/系统 API）+ 渲染进程（UI，默认无 Node）+ utilityProcess。剖析 MUST 先画出进程拓扑与 IPC 通道清单。
- **IPC 链路穿透**：`ipcMain.handle/on` ↔ `ipcRenderer.invoke/send` ↔ preload `contextBridge.exposeInMainWorld`。分析时枚举全部通道：名称/方向/处理器位置/数据校验有无。通道名杂乱无命名空间是常见债。
- **窗口管理**：BrowserWindow 创建与生命周期、单实例锁、托盘/菜单。
- **状态管理**：渲染进程内任意前端状态库；主进程状态（配置存储）常在 `store/`（electron-store 或自研 JSON 存储）。
- **异步与并发**：主进程 Node 异步（Promise/事件循环）；CPU 密集用 `utilityProcess` 或 Worker。
- **配置项**：`electron-builder.yml/json`（打包）、环境区分常靠 `app.isPackaged` + `.env` 注入；敏感密钥 MUST 在主进程侧，NEVER 经 IPC 泄给渲染层明文。
- **安全基线**：`contextIsolation: true`、`nodeIntegration: false`、`sandbox` 配置——剖析时必查（关闭即高危债）。

## 常见坑（剖析时重点核查）

1. 渲染进程直接 nodeIntegration=true（安全债）。
2. IPC 无输入校验（渲染层可传任意参数调主进程 fs/shell）。
3. 主进程同步 IPC（`sendSync`）阻塞 UI。
4. 密钥存渲染层 localStorage。
5. 自动更新（autoUpdater）缺签名校验或回滚方案。

## 深读锚点

- `D:\demo\wikihub\electron\`、`D:\demo\wikihub\refrerence\electron\`。
- 官方：https://www.electronjs.org/docs/latest/
