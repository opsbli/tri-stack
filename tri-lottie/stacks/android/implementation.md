---
name: android-implementation
description: Android 端动效实现——lottie-android View 与 lottie-compose 双轨、API 映射、资产规范、代码模板。核验于 2026-09，lottie 主版本 6.x。
---

# Android 端实现（stacks/android）

## 一、库选型决策树

```
动效需求
├── 简单属性动效 → Compose animate*AsState / ObjectAnimator（View 体系）
├── 复杂矢量动效 / 设计师资产 → Lottie
│   ├── View 体系（XML 布局）→ lottie（LottieAnimationView）
│   └── Jetpack Compose → lottie-compose（rememberLottieComposition + LottieAnimation）
└── 交互驱动弹性动效 → Compose spring / 自定义 spring physics
```

**选型铁律**：Compose 项目用 lottie-compose；View 项目用 lottie。两者是**独立 artifact，NEVER 混引**。

## 二、安装与版本约束

```kotlin
// app/build.gradle.kts
dependencies {
    implementation("com.airbnb.android:lottie:6.x")          // View 体系
    implementation("com.airbnb.android:lottie-compose:6.x")  // Compose 体系（二选一或按需）
}
```

- **minSdk 21+**（Android 5.0）；lottie 2.8.0 起强制 AndroidX（`android.useAndroidX=true`）
- 带图片资产的动画：`.zip` 包（JSON+图片）
- 网络加载需 `INTERNET` 权限
- ProGuard/R8：`-keep class com.airbnb.lottie.** { *; }`

## 三、概念 → API 映射

| 决策概念 | Compose 实现 | View 实现 |
|---------|-------------|----------|
| ease-out | `CubicBezierEasing(0f, 0f, 0.2f, 1f)` | 插值器 `DecelerateInterpolator` / 资产内置 |
| 过冲（Playful） | `spring(dampingRatio = 0.4f, stiffness = 200f)` | `OvershootInterpolator` |
| 时长 | `tween(350, easing = ...)` | 资产帧率内嵌 |
| 加载资产 | `rememberLottieComposition(LottieCompositionSpec.RawRes(R.raw.x))` / `.Asset("x.json")` / `.Url(url)` | `LottieAnimationView.setAnimation("x.json")` |
| 播放控制 | `animateLottieCompositionAsState(composition, iterations, speed)` | `playAnimation()` / `pauseAnimation()` |
| 循环 | `LottieConstants.IterateForever` | `view.loop = true` / XML `lottie_loop` |
| 速度 | `speed = x` 参数 | `view.speed = x` |
| 跳帧/分段 | progress state 锚定 | `setMinFrame/setMaxFrame` |
| 反向 | progress 反向驱动 | `view.reverseAnimationSpeed()` |
| 换色 | `LottieAnimation(..., colorFilter)`（KeyPath 级需 Remappable） | `addValueCallback(KeyPath, LottieProperty.COLOR)` |
| 完成回调 | 监听 progress state 到 1f | `addAnimatorListener(onAnimationEnd)` |
| 释放 | Composition 由 Compose 生命周期托管 | view 分离即释放 |

## 四、资产规范与坑位

1. JSON 放 `src/main/assets/`（`Asset("x.json")`）或 `src/main/res/raw/`（`RawRes(R.raw.x)`）——带图动画必须 .zip
2. View 与 Compose artifact 勿混引（CRITICAL 常见误装）
3. 网络动画首包慢：预加载 `LottieCompositionFactory.fromUrl` + 缓存 LottieComposition，NEVER 让 UI 空白等网络
4. XML 使用 `app:lottie_rawRes` / `app:lottie_fileName` / `app:lottie_loop` / `app:lottie_autoPlay`
5. 低端机大资产掉帧：优先 `.lottie` 压缩格式或简化图层；列表项（RecyclerView/LazyColumn）禁放大资产

## 五、代码模板（黄金用例）

规格单：〔卡片入场|Premium|position+opacity|350ms|cubic-bezier(0.4,0,0.2,1)|0%|primary+secondary(shadow 延迟 50ms)〕

**分支 A：Compose（本规格推荐）**

```kotlin
import androidx.compose.animation.core.*
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.graphicsLayer
import com.airbnb.lottie.compose.*

// 决策概念映射：Premium = 0 过冲 → CubicBezierEasing(0.4,0,0.2,1)，禁 spring 低 damping
@Composable
fun PremiumCardEnter(content: @Composable BoxScope.() -> Unit) {
    var visible by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) { visible = true }

    val transition = updateTransition(targetState = visible, label = "cardEnter")
    val progress by transition.animateFloat(
        transitionSpec = { tween(350, easing = CubicBezierEasing(0.4f, 0f, 0.2f, 1f)) },
        label = "progress",
    ) { state -> if (state) 1f else 0f }

    Box(
        Modifier
            .graphicsLayer {
                // CRITICAL 自检：transform 等价（translationY/alpha），非 layout 属性
                translationY = 20f * (1f - progress)
                alpha = progress
                shadowElevation = 12f * progress   // secondary：阴影随进度抬升
            }
    ) { content() }
}

// Lottie 资产分支（复杂矢量动效）
@Composable
fun LottieCardEnter(modifier: Modifier = Modifier) {
    val composition by rememberLottieComposition(
        LottieCompositionSpec.Asset("card_enter.json")   // assets/ 目录
    )
    val progress by animateLottieCompositionAsState(
        composition,
        iterations = 1,          // 入场单次（Premium）
        speed = 1f,
    )
    LottieAnimation(composition = composition, progress = { progress }, modifier = modifier)
}
```

**分支 B：View（XML）**

```xml
<com.airbnb.lottie.LottieAnimationView
    android:id="@+id/card_enter"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:lottie_rawRes="@raw/card_enter"
    app:lottie_autoPlay="true"
    app:lottie_loop="false" />
```

## 六、性能与 a11y

- 属性动画仅 `translationX/Y/Z`、`scaleX/Y`、`rotation`、`alpha`（RenderThread 加速）；NEVER 动画 `layoutParams`（触发 measure/layout 掉帧）
- 视口内动画元素 < 20；列表项禁大资产
- 硬件层：`View.setLayerType(LAYER_TYPE_HARDWARE)` 仅在动画期间开启
- **reduced-motion**：读 `Settings.Global.getFloat(resolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f)`，=0 时跳过动画直接落终态；或系统「移除动画」开关 `Settings.Global.TRANSITION_ANIMATION_SCALE`；Lottie 可 `view.setFailureListener` 后静态展示末帧
- 关键信息 NEVER 仅靠动效传达（配文案/状态色）
