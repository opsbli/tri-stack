---
name: loop-design
description: 【Doing·loop/domain 创建子类路由】I14 任务要点含 loop/domain 创建语义时触发。L2 保持 I14 不变，仅覆写下游路由建议为 tri-loop。Doing 大类子类路由项，与工作流设计子类路由并列。
---

# loop/domain 创建子类路由（Doing · I14 子类路由项）

> 本项是 Doing 大类下 I14 的**子类路由项**，不改变 L2 意图编码，仅覆写 `下游路由建议` 为 tri-loop。设计依据：知识库 loop/domain 的创建涉及 substrate bootstrap、charter 收集、README scaffold、真实测试运行、Timeline+LOG.md 记录等专属全链路，与通用操作执行（tri-action）不同，tri-loop 采用「检测 substrate → 收集 charter → scaffold → 真实测试运行 → 记录 → 回报」的闭环工作流，属于专业域执行而非通用操作，故单列子类路由。

## 识别特征

- L2 已判定为 **I14 操作执行**
- 任务要点中出现以下**loop/domain 创建语义关键词**之一：
  - loop / domain / 循环 / 知识库
  - beat / workstream
  - charter / cadence
  - 起一个知识库 loop / 建一个 domain / 跑起来一个循环
- 典型语料：
  - 「帮我在知识库起一个 monitoring loop」→ I14 + loop 创建子类
  - 「创建一个 domain 来自动分诊工单」→ I14 + loop 创建子类
  - 「搭一个每周跑的 research loop」→ I14 + loop 创建子类

## 与邻近意图边界

- vs **I14 通用操作执行（tri-action）**：通用执行侧重运行/操作既有系统，loop 创建子类侧重在知识库中 bootstrap substrate、scaffold 一个可验证运行的 loop
- vs **工作流设计子类（tri-workflow）**：工作流设计产出可执行的工作流定义（DAG/CI 配置），loop 创建产出知识库 domain + 真实测试运行记录，二者语义不同，分别路由
- vs **I21 蒸馏造物（tri-god）**：I21 产出可独立调用的 skill，loop 创建产出知识库内的一个 domain/loop，不产出 skill

## 路由规则

| 字段 | 取值 |
|---|---|
| L1_交互类型 | B.Doing |
| L2_核心意图 | I14 操作执行（loop/domain 创建子类） |
| 下游路由建议 | tri-loop（覆写默认的 tri-action） |
| 落盘 | 快照（snapshot.md） |

## 路由判定流程

1. **L2 判定**：按常规流程判定 L2 = I14
2. **子类检测**：扫描 `任务要点` 是否含 loop/domain 创建语义关键词
3. **路由覆写**：
   - 命中关键词 → `下游路由建议` = tri-loop，L2 保持不变
   - 未命中关键词 → `下游路由建议` = tri-action，保持默认
4. **快照标注**：在快照 §三 `任务要点` 中保留 loop/domain 创建语义关键词，供 tri-loop 激活时校验

## tri-loop 激活条件（下游 skill 侧）

> tri-loop 收到快照后，按以下条件校验是否激活：

- `intent.L2_核心意图` = I14
- `下游路由建议` 指向 tri-loop
- `任务要点` 含 loop/domain 创建语义

三者同时满足即激活 tri-loop 的启动工作流。若 L2 越界（非 I14），tri-loop 将停止并回退 tri-intent 重新路由。

## 与 tri-loop 上游依赖检测的对称关系

- tri-intent 侧：产出快照后检测 `tri-loop/` 目录是否存在，未安装时提示 `skillhub install tri-loop --dir <目标目录>`
- tri-loop 侧：激活时检测上游 tri-intent 是否可用（模式 A 快照模式 / 模式 B 引导安装 / 模式 C 降级模式）
- 双向检测确保：无论用户先安装哪一端，缺失的另一端都会被检测到并给出安装引导
