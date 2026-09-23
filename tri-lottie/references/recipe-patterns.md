---
name: recipe-patterns
description: 成品动效配方——按钮按压/卡片入场/成功态/错误态/加载态/hover/弹窗/页面转场/仪表盘编排。常见场景直接套用后微调。
---

# 成品动效配方

> 用法：命中场景 → 取配方 → 按人格微调（括号内标注人格差异）→ 套规格单格式输出。数值基线见 motion-tokens.md。

## 按钮按压

| 阶段 | 参数 |
|------|------|
| Press | scale 0.95-0.98（60-80ms, ease-out）；背景加深 10% |
| Release | 回弹 1.0；Playful 过冲至 1.05（80ms）再 spring 落定（120ms）；Corporate 0-2% 过冲 |
| Secondary | 阴影收缩/扩展；图标下移 2px |
| 总时长 | ~150-260ms |

## Hover 态（Web/Desktop）

| 元素 | 效果 | 时长 |
|------|------|------|
| 按钮 | scale 1.02-1.05 | <100ms |
| 卡片 | scale 1.01-1.02 + 阴影抬升 | <100ms |
| 链接 | 色变 + 下划线 | <100ms |
| 图标 | scale 1.1 + 旋转 2-5° | <100ms |
| 图片 | scale 1.03（overflow hidden） | 150ms |

进入 <100ms；退出 150-200ms（更慢 = 精致感）。

## 卡片入场（Premium 基线）

1. 起点：目标位下方 20px，opacity 0
2. 路径：轻微弧线（中点 X 偏移 10px）
3. 缓动：ease-out-cubic 减速
4. follow-through：阴影比卡片晚 50ms 到位
5. Secondary：内容比卡片晚 100ms 淡入
6. Staging：其余卡片 dim 至 80%

（Playful：位移 30-50px + ease-out-back + 10-15% 过冲；Energetic：40-80px + ease-out-expo）

## 成功态（Checkmark）

1. 容器：scale 0.9→1.0（200ms, ease-out-back, 过冲 5-10%）
2. 对勾：stroke 描画（150ms, ease-out, 延迟 100ms）
3. 色彩：过渡到绿色（200ms）
4. Ambient：微光晕/粒子（300ms，可选）
5. 总时长：400-500ms

## 错误抖动（Error Shake）

1. Primary：水平振荡 ±10-15px，2-3 次，幅度递减
2. 缓动：ease-in-out（锐利停顿）
3. 色彩：红色 tint（闪现后回落）
4. **无过冲**（错误要坚定）；回到原位
5. 总时长：300-400ms

## 内联校验错误

错误文本下滑+淡入（200ms）→ 边框变红（150ms）→ 图标 scale 进入（150ms, 延迟 50ms）→ 可选单次轻抖（200ms）。

## 表单提交失败

按钮复位（200ms）→ 错误消息滑入（250ms）→ 出错字段红色高亮（150ms, stagger 30ms）→ 平滑滚动到首个错误（300ms, ease-in-out）。

## 加载态

| 形态 | 参数 |
|------|------|
| Spinner | 连续 360°，linear，1000-1500ms/圈；可加 2-3s 呼吸脉冲 |
| Skeleton | 渐变扫过 L→R，1500-2000ms；底 10-20% 透明度，峰 30-40% |
| 进度条 | width/transform，ease-in-out；可加色彩里程碑 + shimmer |
| 不定进度 | 位置/宽度振荡，1500-2500ms，ease-in-out；连续但永不狂躁 |

## 弹窗打开（Modal）

背景 dim（200ms）→ 弹窗 scale 95%→100% + 淡入（300ms, 延迟 50ms）→ 标题（延迟 200ms）→ 正文（280ms）→ 按钮（350ms）→ 关闭钮最后（400ms）。内容按阅读顺序错峰。

## Toast 通知

右侧滑入+淡入（250ms, ease-out）→ 过冲 3-5%（Corporate）/10-15%（Playful）→ 图标（100ms, 延迟 50ms）。退场：滑向边缘+淡出（180ms, ease-in）；剩余 toast 上移补位（200ms, ease-in-out）。

## 页面转场（前进）

当前页左滑+淡出（300ms, ease-in）→ 新页自右入+淡入（400ms, ease-out, 延迟 100ms）→ 共享元素 morph（400ms, ease-in-out）→ 新页内容 stagger（50ms 间隔）。

## 仪表盘首载编排

```
0ms    骨架屏可见
100ms  Hero 指标卡（250ms, ease-out）
200ms  组件卡开始（每个 200ms，间隔 60ms stagger）
350ms  Hero 完成；图表开始描画（300ms）
500ms  全部落定
650ms  主指标开始 ambient 脉冲
```

## 下拉菜单展开

容器 scaleY 0→100%（200ms, ease-out）→ 菜单项淡入（每项间隔 30ms，容器后 50ms 开始）。

## 手风琴

展开：箭头旋转（150ms）+ 高度展开（250ms）+ 内容延迟 50ms 淡入（200ms）+ 兄弟项位移（200ms）。收起：反向 + ease-in。

## 拖放

拖起：scale 1.03 抬升（150ms）+ 其余项让位（200ms）。放下：scale 1.0 落定（200ms）+ 间隙闭合。

## 环境动效（Ambient）

| 类型 | 参数 |
|------|------|
| 呼吸/脉冲 | scale 0.98-1.02，sine，2000-4000ms/圈（±5% 以上变索取注意力） |
| 漂浮 | Y ±5-15px，sine，3000-5000ms；多层用不同时长（4000/5500/3500ms）防同步 |
| 渐变流转 | 背景 position/角度 ±10-20%，8000-20000ms，一瞥不可察觉 |
| 视差 | 前景 1.0x / 中景 0.5x / 背景 0.2x；滚动驱动总位移 <100px；移动端禁用；永不视差正文 |
| 微光 shimmer | 渐变扫过 1500-2500ms，间隔暂停 2000-5000ms |
| 粒子 | <20 个元素；transform+opacity only；大而少优于小而多 |

环境总能量 ≤ 主运动的 20%。
