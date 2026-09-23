# 版本检查与更新规范（瘦指针 STUB）

> 本文件是瘦指针：完整细则唯一真源为 tri-mm 包内 `references/version-check-spec.md`
> （随包分发路径 `tri-mm/references/version-check-spec.md`）。本 STUB 只保留独立可运行的
> 最小执行声明；细则与本文冲突时以真源为准，修订只改真源一处，NEVER 在此展开。

## 最小可执行声明

1. **确定性入口**：`python scripts/check_update.py --slug tri-video --json`
   （脚本与家族同源，位于本 skill `scripts/check_update.py`）。
2. 解析 JSON `state` 字段：`A`/`B`/`C`/`D` 一律放行并标注降级口径；`BLOCK` 绝对禁止执行。
3. 退出码：`< 20` 放行；`>= 20` 阻断（退出码是完成判据，NEVER 依赖模型自述）。
4. CLI 缺失或通道不可用时，按 SKILL.md §版本检查与更新机制 的四态判定降级继续，NEVER 阻断。
