---
name: quality-gate
description: 动效三级质量门（CRITICAL/HIGH/MEDIUM，映射 P0/P1/P2）+ 8 类症状排障表 + 10 条快速诊断。门L4 与审查模式查表源。
---

# 动效质量门（三级）

## CRITICAL（一票否决 · 映射 P0）

| # | 条款 |
|---|------|
| C1 | 空间移动禁用 linear 缓动（仅旋转/进度条/计时器可用 linear） |
| C2 | 重要状态变更禁用纯 opacity（必须组合 position 或 scale） |
| C3 | 单段移动不得超过容器 1/3（须加中间关键帧：变向/变速/弧线） |
| C4 | 必须有 primary 层（缺失主运动 = 不合格） |
| C5 | stagger 总时长必须 < 500ms |
| C6 | 禁止动画触发 layout 的属性（width/height/margin → 改 transform）造成掉帧 |

## HIGH（强烈要求 · 映射 P1）

| # | 条款 |
|---|------|
| H1 | 时长匹配元素类型预算（查 motion-tokens.md） |
| H2 | 方向性缓动正确（入场 ease-out / 出场 ease-in / 屏内 ease-in-out） |
| H3 | 应用迪士尼原则（尤其 anticipation 预备、follow-through 跟随） |
| H4 | 同场景人格一致（同一交互 = 同一动效） |
| H5 | 子元素 follow-through 偏移 50-150ms 存在 |
| H6 | 提供 prefers-reduced-motion 降级 |

## MEDIUM（建议 · 映射 P2）

缺 ambient 层｜缺 anticipation 预备段｜过冲幅度与场景失配｜可用更好弧线｜缺 counter-motion 反向运动。

## 三层运动完整性

| 层 | 幅度 | 时序 | 作用 |
|----|------|------|------|
| Primary | 100% | 主体 | 观众跟随的主运动 |
| Secondary | 30-50% | 延迟 50-100ms，缓动不同于 primary | 支撑丰富度（阴影/图标联动） |
| Ambient | 10-20% | 连续/缓慢 | 背景生命感，永不索取注意力 |

注意力预算：每时刻一个 hero；同时活跃运动元素 ≤2-3；ambient 不占预算；错峰优于同步。

## 排障表（症状 → 根因 → 修复）

| 症状 | 根因 | 修复 |
|------|------|------|
| 机器人感 | linear 缓动/直线路径/全同步 | ease-out + 中点 10-20px 弧线 + 元素间 50-150ms 错峰 |
| 太慢 | 超元素类型预算/滥用 ease-in-out/预备过长 | 查时长表；换 ease-out（体感更快）；预备降至 10% 或移除 |
| 太快/突兀 | 低于最小时长/无缓动/缺落定 | 弹窗 ≥300ms、页面 ≥400ms；补 ease-out；加 50-100ms settle |
| 廉价感/扁平 | 只有 primary/纯 opacity/全员同缓动/无跟随 | 补 secondary+ambient；组合 position/scale；子元素延迟 50-150ms；加 3-10% 过冲 |
| 太吵 | 同时运动元素多/幅度过大/多 hero | 1/3 法则；幅度取最小必要；每时刻一个 hero 其余 dim；环境动效降至 10-20% |
| 没人格 | 全默认缓动/时长无差异/无统一入场 | 套用原型签名缓动；用人格时长三档；定义统一入场模式；90%+ 用同一原型 |
| 感觉不一致 | 同类动效缓动/时长/方向漂移 | 按运动类型标准化；时长用三档 palette；统一入场起点 |
| 掉帧 | 动画 layout 属性/元素过多/重阴影滤镜 | 全部改 transform+opacity；视口内 <20 元素；简化阴影或预渲染；stagger 摊平负载 |

## 人格专属翻车点

- **Playful**：过冲 >25% 破坏感；不必处处弹；短时长+弹跳=glitch。
- **Premium**：过 subtle 不可见；过慢成等待；零动效=失效。
- **Corporate**：过保守=死板；混弹跳缓动破坏信任；完全一致=单调。
- **Energetic**：处处最强=无重点；粒子泛滥；无落定=混乱。

## 10 条快速诊断（审查模式顺序执行）

1. 空间移动无 linear？
2. 时长匹配元素类型？
3. primary + secondary 层齐备？
4. 人格一致？
5. 方向性缓动正确？
6. 位移 ≤1/3 容器？
7. 同时活跃元素 ≤1/3？
8. follow-through 存在（50-150ms 偏移）？
9. 每段运动有明确目的？
10. 第 100 次观看仍可接受？
