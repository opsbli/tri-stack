---
name: stack-qt
description: Qt / C++ 栈卡——信号槽、对象树、线程模型分析要点。
---

# 栈卡：Qt / C++

## 探测信号

- `.pro`（qmake）或 `CMakeLists.txt` 含 `find_package(Qt6|Qt5)` / `QT += ...`；源码含 `Q_OBJECT` 宏、`#include <QObject>`、`connect(`。

## 工程惯例（分析要点校准基线）

- **分层**：典型 `main.cpp` + `mainwindow.*`（或 QML 项目：`main.cpp` + `*.qml` + C++ 后端注册）。分析对象分两类：Widgets（C++ UI）与 Quick/QML（声明式 UI + C++ 逻辑），判定清楚。
- **对象模型（核心）**：QObject 父子所有权树（delete 自动化）、信号槽机制（`connect` 五种连接类型，跨线程队列连接）。剖析重点：信号槽链路即"路由"——枚举关键 connect 关系图。
- **线程与并发**：QThread（推荐 moveToThread 工作对象模式而非继承）、QThreadPool + QRunnable、QtConcurrent、互斥 QMutex/QReadWriteLock。跨线程信号槽自动队列化；直接跨线程调 UI 对象 = 高危债。
- **事件循环**：QEventLoop、自定义 event()/eventFilter、定时器 QTimer。
- **实体与数据**：Model/View 体系（QAbstractItemModel/QAbstractTableModel）；数据类常用 QSharedData / 值语义。
- **配置项**：QSettings（注册表/ini）、qmake `.pro` 的 DEFINES / CMake target_compile_definitions 区分构建配置；资源经 `.qrc`。
- **内存与债**：裸 new 的 QObject 由父对象管理；非 QObject 裸指针需智能指针。剖析时查内存管理策略一致性。

## 常见坑（剖析时重点核查）

1. 跨线程直接访问 UI（未走队列连接）→ 崩溃。
2. connect 第五参数用错（多线程下 DirectConnection）。
3. QObject 跨线程 delete（用 deleteLater）。
4. 信号槽循环触发（死循环）。
5. QML 与 C++ 交互未用属性绑定而靠轮询。

## 深读锚点

- `D:\demo\wikihub\qt\`、`D:\demo\wikihub\refrerence\qt.wiki\`。
- 官方：https://doc.qt.io/
