---
name: ios-implementation
description: iOS 端动效实现——lottie-ios UIKit AnimationView 与 SwiftUI LottieView 双轨、API 映射、资产规范、代码模板。核验于 2026-09，lottie-ios 主版本 4.x。
---

# iOS 端实现（stacks/ios）

## 一、库选型决策树

```
动效需求
├── 简单属性动效 → UIView.animate（UIKit）/ withAnimation（SwiftUI）
├── 弹性交互动效 → UIViewPropertyAnimator（spring）/ SwiftUI .spring()
├── 复杂矢量动效 / 设计师资产 → Lottie
│   ├── SwiftUI → LottieView（库内置，iOS 13.0+）
│   └── UIKit → AnimationView（新）／LottieAnimationView（4.x 命名）
└── 转场编排 → UIViewControllerAnimatedTransitioning / .transition
```

**选型铁律**：简单反馈用系统动画（零依赖）；Lottie 用于设计师资产。

## 二、安装与版本约束

```
SPM: https://github.com/airbnb/lottie-ios  （Xcode → Add Package Dependency）
CocoaPods: pod 'lottie-ios'
```

- **iOS 13.0+ / macOS 10.15+ / tvOS 13.0+ / visionOS 1.0+**
- **Swift 5.7+**（5.4 及以下不再支持）
- 4.x 起主类型改名：`LottieAnimation`（原 `Animation`）、`LottieAnimationView`（旧 `AnimationView(name:)` 初始化已 deprecated）

## 三、概念 → API 映射

| 决策概念 | SwiftUI | UIKit |
|---------|---------|-------|
| ease-out | `.animation(.easeOut(duration: 0.35))` / `.timingCurve(0.4, 0, 0.2, 1, duration: 0.35)` | `UIView.animate(..., options: [.curveEaseOut])` |
| 过冲（Playful） | `.spring(response: 0.3, dampingFraction: 0.5)` | `UIViewPropertyAnimator` + `UISpringTimingParameters(damping < 1)` |
| 时长 | duration 参数 | duration 参数 |
| 加载资产 | `LottieView(LottieAnimation(named: "card_enter"))` | `AnimationView(name: "card_enter")`（bundle 内） |
| 播放控制 | `.playing()` / `.paused()` modifier | `view.play()` / `view.pause()` / `view.stop()` |
| 循环 | `.looping()` | `view.loopMode = .loop` |
| 速度 | `.animationSpeed(x)` | `view.animationSpeed = x` |
| 跳帧/分段 | progress 绑定 | `view.play(fromProgress:toProgress:completion:)` / `currentProgress` |
| 反向 | progress 反向 | `play(fromProgress: 1, toProgress: 0)` |
| 换色 | `valueProviders`（KeyPath） | `view.setValueProvider(_:keypath:)` |
| 完成回调 | `.onAnimationFinished { }` | play 的 completion 闭包 |
| 释放 | 视图移除即释放 | `view.removeFromSuperview()` 释放 |

## 四、资产规范与坑位

1. JSON 放 App bundle（Xcode target 勾选）；带图资产为 JSON 同名 `.imageset` 或 zip 内嵌
2. 4.x API 命名迁移：`Animation` → `LottieAnimation`；`AnimationView` → `LottieAnimationView`（旧初始化器 deprecated，NEVER 用 `AnimationView(name:)` 新代码）
3. SPM 平台声明 iOS 13.0+；Swift 5.4 以下编译不过
4. 大资产在低端机掉帧：`renderEngine = .coreAnimation`（默认）已优化；列表 cell 禁大资产（用静态帧或 `currentProgress` 冻结）
5. 深色模式：资产色彩固定时验证双外观对比度

## 五、代码模板（黄金用例）

规格单：〔卡片入场|Premium|position+opacity|350ms|cubic-bezier(0.4,0,0.2,1)|0%|primary+secondary(shadow 延迟 50ms)〕

**分支 A：SwiftUI（本规格推荐）**

```swift
import SwiftUI
import Lottie

struct PremiumCardEnter<Content: View>: View {
    let content: Content
    @State private var appeared = false

    // 决策概念映射：Premium 0 过冲 → timingCurve(0.4,0,0.2,1)，禁 spring 低 dampingFraction
    var body: some View {
        content
            // CRITICAL 自检：offset/opacity = transform 等价，非 layout 属性
            .opacity(appeared ? 1 : 0)
            .offset(y: appeared ? 0 : 20)
            .shadow(color: .black.opacity(appeared ? 0.15 : 0), radius: 12) // secondary
            .onAppear {
                withAnimation(.timingCurve(0.4, 0, 0.2, 1, duration: 0.35)) {
                    appeared = true
                }
            }
            // a11y 降级（HIGH：H6）
            .environment(\.accessibilityReduceMotion) // 读取系统设置
    }
}

// reduced-motion 正确写法：
struct ReducedMotionCard: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var appeared = false
    var body: some View {
        CardContent()
            .opacity(appeared ? 1 : 0)
            .offset(y: reduceMotion ? 0 : (appeared ? 0 : 20)) // 降级：去位移
            .onAppear {
                if reduceMotion {
                    appeared = true                              // 直接落终态
                } else {
                    withAnimation(.timingCurve(0.4, 0, 0.2, 1, duration: 0.35)) { appeared = true }
                }
            }
    }
}

// Lottie 资产分支（复杂矢量动效）
struct LottieCardEnter: View {
    var body: some View {
        LottieView(animation: .named("card_enter"))   // bundle 内 JSON
            .playing()                                  // 单次播放（looping() 才循环）
            .animationSpeed(1.0)
            .onAnimationFinished { _ in /* 完成回调 */ }
    }
}
```

**分支 B：UIKit**

```swift
import Lottie

let cardView = LottieAnimationView(name: "card_enter")  // 4.x 类型
cardView.loopMode = .playOnce
cardView.contentMode = .scaleAspectFit
view.addSubview(cardView)
cardView.play(completion: { finished in /* 回调 */ })
// 释放：cardView.removeFromSuperview()
```

## 六、性能与 a11y

- 属性动画仅 `frame` 以外的 transform 系（`transform`/`alpha`）；NEVER 动画 `frame`/`constraints`（触发 layout）
- Core Animation 渲染引擎默认启用（4.x）；离屏渲染（masks/shadows）注意每帧成本
- 视口内动画元素 < 20；UITableView/UICollectionView cell 禁大资产
- **reduced-motion**：`UIAccessibility.isReduceMotionEnabled`（UIKit）/ `@Environment(\.accessibilityReduceMotion)`（SwiftUI）——降级策略：去位移、去弹性、保留 opacity 淡入或直接落终态
- 关键信息 NEVER 仅靠动效传达
