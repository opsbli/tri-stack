---
name: motion-personality
description: 四动效人格原型（Playful/Premium/Corporate/Energetic）+ 关键词匹配 + 品牌动效三常量。规格单第 2 步查表源。
---

# 动效人格原型

## 四原型参数表

### Playful（俏皮）

| 参数 | 值 |
|------|-----|
| 时长 | 150-300ms |
| 缓动 | ease-out-back / 弹性 spring |
| 过冲 | 10-20% |
| 路径 | 弧线曲线，禁直线 |
| 挤压拉伸 | 是（撞击时） |

签名手法：弹跳落定、按压挤压拉伸、旋转摆动、亮色弹出、错落 stagger。
适用：儿童应用、休闲游戏、社交、庆祝、引导流程、创意工具。
**翻车点**：过冲 >25% = 破坏感；不是所有元素都弹；短时长+弹跳 = 廉价 glitch 感。

### Premium（高级）

| 参数 | 值 |
|------|-----|
| 时长 | 350-600ms |
| 缓动 | cubic-bezier(0.4, 0, 0.2, 1) |
| 过冲 | **0%** |
| 路径 | 平滑曲线 + 轻视差 |
| 挤压拉伸 | 永不 |

签名手法：慢淡入、subtle scale（98%→100%）、慷慨停顿、极少属性（opacity+一维）。
适用：时尚、金融、奢侈品、高端 SaaS、作品集、编辑类。
**翻车点**：太 subtle = 看不见；太慢 = 等待感；完全无动效 = 失效。

### Corporate（专业，UI 默认）

| 参数 | 值 |
|------|-----|
| 时长 | 200-400ms |
| 缓动 | cubic-bezier(0.2, 0, 0, 1) |
| 过冲 | 0-3% |
| 路径 | 以直线为主，强调用小弧 |
| 挤压拉伸 | 否 |

签名手法：一致时长、清晰状态切换、功能性动效、可预测模式、均匀 stagger。
适用：企业、仪表盘、商业工具、后台、医疗、银行。
**翻车点**：过度保守 = 死板；混入弹跳缓动破坏信任感；完全同一 = 单调。

### Energetic（活力）

| 参数 | 值 |
|------|-----|
| 时长 | 100-250ms |
| 缓动 | ease-out-expo / elastic |
| 过冲 | 15-30% |
| 路径 | 夸张弧线、大位移、对角线 |
| 挤压拉伸 | 是（夸张） |

签名手法：大 scale 变化（50-150%）、快速色彩切换、粒子迸发、加速 stagger、边缘切入。
适用：游戏、体育、音乐、活动、营销、健身。
**翻车点**：处处最强 = 没有重点；粒子过多；无落定 = 混乱。

## 关键词匹配（用户 prompt → 人格）

| 关键词 | 人格 |
|--------|------|
| fun, whimsical, bouncy, cute, friendly, 俏皮, 可爱 | Playful |
| elegant, minimal, luxury, sophisticated, 高级, 优雅 | Premium |
| clean, professional, business, dashboard, 专业, 商务 | Corporate |
| dynamic, energetic, bold, exciting, 活力, 动感 | Energetic |
| 未指定 + UI 场景 | **Corporate（默认）** |
| 未指定 + 插画场景 | **Playful（默认）** |

## 品牌动效三常量（项目级一次性定义）

1. **签名缓动**（80% 动画共用）：Playful=ease-out-back｜Premium=(0.4,0,0.2,1)｜Corporate=(0.2,0,0,1)｜Energetic=ease-out-expo
2. **时长三档**（quick/standard/slow）：

| 档位 | Playful | Premium | Corporate | Energetic |
|------|---------|---------|-----------|-----------|
| Quick | 150ms | 350ms | 200ms | 100ms |
| Standard | 250ms | 500ms | 300ms | 180ms |
| Slow | 400ms | 800ms | 450ms | 300ms |

3. **统一入场模式**：Playful=自下弹升｜Premium=慢淡入+scale 98%→100%｜Corporate=右侧滑入+淡入｜Energetic=边缘切入+过冲

## 混合原则

- 90% 场景用主原型；特定时刻可借用另一原型（如 Corporate 仪表盘仅在成功态借 Playful）
- 人格切换须平缓过渡，NEVER 突变
