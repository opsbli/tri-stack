---
name: acquire-unknown-stack
description: 未覆盖技术栈获取协议——识别→官网抓取→建卡→登记索引的四步标准动作。
---

# 未覆盖技术栈获取协议

> 触发条件：阶段 2「识别」未命中 INDEX.md 任何探测信号。本协议使知识库随使用自增长。

## 四步标准动作

### 步骤 1 识别与拆解

从代码库自身提取栈事实（优先级从高到低）：

1. 清单文件：`package.json` / `pom.xml` / `go.mod` / `pubspec.yaml` / `*.csproj` / `Cargo.toml` / `composer.json` / `*.gemspec` / `Podfile` / `build.gradle`。
2. 构建与 CI 配置：Dockerfile、`.github/workflows`、Jenkinsfile（内含构建/测试命令即运行时线索）。
3. 主入口文件 import 特征与目录命名惯例。
4. 产出：**框架 + 语言 + 版本 + 周边生态（ORM/状态/测试/部署）**清单。

### 步骤 2 官网获取（联网）

1. 访问官方文档（URL 优先级：清单文件 homepage/repository 字段 > 官网搜索）。
2. 抓取四类信息：**目录组织惯例、路由/导航机制、官方推荐状态/数据方案、并发/异步模型**。
3. 联网不可用 → 降级：基于依赖名与代码特征反向工程，报告头部 MUST 声明「知识层缺失，分析基于代码特征推断」。

### 步骤 3 建卡

新建 `tech-stacks/<stack>.md`，结构对齐既有栈卡（五段）：

1. 探测信号（下次能命中）
2. 工程惯例（分析要点校准基线：分层/路由/状态/异步/实体/配置/持久化）
3. 常见坑（剖析时重点核查 3~5 条）
4. 深读锚点（wikihub 有对应目录则登记路径，无则留「无」）
5. 官方文档 URL

卡内结论 MUST 附官网来源 URL 或代码证据，NEVER 凭背景知识裸写。

### 步骤 4 登记索引

1. 在 `INDEX.md` 索引表追加一行（栈名/卡/探测信号/锚点/官网）。
2. 探测信号要写得**可 grep**（文件名/依赖名/目录名）。
3. bump skill 版本（MINOR）记 CHANGELOG。

## 快速安装态写不进去时

skill 处于只读安装目录时：新卡落 `.tribro/code-analyzer/stack-cards/<stack>.md`，并在交付说明中提示用户「手工回流到 skill 的 references/tech-stacks/」；回流前 INDEX 记一行注记。
