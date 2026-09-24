# evolve-hook 契约（平台无关）

> 本文件是 `evolve-hook` 的**语义单一事实源**。各平台适配器（`pi/` · `shell/` · `instructions.md`）
> 只做「语义事件 → 平台接线」的翻译，**不重复描述语义** —— 这是保证三形态不漂移的前提。
> 依 `tri-forge/references/family-spec.md` §1.5。

## 一、语义事件

**一次「用户 ↔ 代理」交互彻底结束，且宿主不会再自动继续之后。**

不是「消息定型时」（一轮里消息会定型多次：用户一条、助手一条，可能还有工具消息），
也不是「底层 run 结束时」（其后可能仍有自动重试 / 恢复 / 压缩 / 排队工作）。

选错事件会导致同一轮被采集多次或采集到半成品 —— 这是本 hook 的唯一一类失败模式。

## 二、入参

| 字段 | 必填 | 说明 |
|---|---|---|
| `session_id` | ✅ | 会话标识，用于分组与去重 |
| `exchange_id` | ✅ | 本轮交互的唯一标识，**去重键**。同一 `(session_id, exchange_id)` 只允许采集一次 |
| `source_skill` | ⭕ | 若该轮由某下游 skill 执行，记其 slug；否则空 |
| `answer` | ✅ | 助手最终答复文本 |
| `user_feedback` | ⭕ | 用户的显式反馈（如纠正/点赞），无则为空 |

## 三、出参

**无返回值。** 唯一效果是**追加**一条信号事件到 `.tribro/evolve/signals.jsonl`。

- 追加式，NEVER 覆盖、NEVER 重写历史行
- 单行 JSON；字段至少含 `ts` / `session_id` / `exchange_id` / `answer_hash` / `produced_by`
- `.tribro/` 不存在时 MUST 先创建；写入失败 MUST 静默降级（hook 任何情况下 **NEVER 抛错中断代理**）

## 四、幂等要求

**同一 `(session_id, exchange_id)` 重复投递时必须只采集一次。**

去重状态 MUST 存放在**会话内可持久化的载体**中，NEVER 放模块级变量 ——
in-process 类宿主（如 pi 的 `ctx.reload()`）会替换运行时，模块级变量随之丢失，防重即失效。
（现象：同一轮被反复采集，`signals.jsonl` 迅速膨胀。）

## 五、宿主降级

| 情形 | 行为 |
|---|---|
| 宿主未配置本 hook | `EVOLVE_OBSERVE` 不可用；信号采集改由用户显式录入或跳过。`EVOLVE_LEARN` 因无原料而空转。**可正常工作的是 `EVOLVE_APPLY` 与 `EVOLVE_ADMIN`** |
| 事件缺失（宿主无等价语义事件） | 适配器 MUST 显式标注**语义偏差**，不得假装等价；必要时降级为「会话结束时批量采集」 |
| 写盘失败 | 静默降级 + 在宿主 UI（如有）提示一次，NEVER 中断代理循环 |

## 六、各平台接线（适配器索引）

| 形态 | 平台 | 落点 | 语义偏差 |
|---|---|---|---|
| **B · in-process** | pi（TypeScript） | `pi.on("agent_settled")` | **无** —— 官方定义为「final、notification-only，用于需要知道 Pi 不会再自动继续」时 |
| A · shell-hook | Claude Code / Cursor 等 | 宿主的「Stop」类事件 | 部分宿主无「不会再自动继续」概念 → 需标注偏差 |
| C · instructions-file | Gemini / AGENTS.md 类 | 指令文件里声明「每轮结束时执行 X」 | 由模型自觉执行，**不保证**；降级为尽力而为 |

## 七、验收标准（任一平台适配器交付时）

1. 一轮交互结束 → `.tribro/evolve/signals.jsonl` 新增 **恰好 1** 条
2. 同一轮重复投递 → 不新增（幂等）
3. 宿主热重载（如 pi `/reload`）后再跑一轮 → 幂等仍成立（**证明未依赖模块级变量**）
4. 无 UI 模式（headless）下不报错
5. 写盘失败不中断代理循环
