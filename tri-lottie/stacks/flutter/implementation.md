---
name: flutter-implementation
description: Flutter 端动效实现——pub lottie 包（纯 Dart 六平台）、隐式/显式动画选型、API 映射、资产规范、代码模板。核验于 2026-09，lottie 主版本 3.x，Flutter SDK 2.0+。
---

# Flutter 端实现（stacks/flutter）

## 一、库选型决策树

```
动效需求
├── 简单属性动效 → 隐式动画（AnimatedContainer/AnimatedOpacity，零样板）
├── 编排/弹性动效 → 显式动画（AnimationController + CurvedAnimation）/ flutter_animate
├── 复杂矢量动效 / 设计师资产 → lottie 包（Lottie.asset / Lottie.network）
└── 页面转场 → Hero / PageRouteBuilder 自定义
```

**选型铁律**：隐式动画能表达的不上 AnimationController；Lottie 仅用于设计师资产。纯 Dart 实现，Android/iOS/macOS/Web/Linux/Windows 六平台一致。

## 二、安装与版本约束

```yaml
# pubspec.yaml
dependencies:
  lottie: ^3.x        # flutter pub add lottie
flutter:
  assets:
    - assets/animations/   # 资产目录声明（坑位 1）
```

- **Flutter SDK 2.0+**；Dart null-safety 必须
- `flutter pub get` 后生效；锁版本直接写 `lottie: 3.x.y`

## 三、概念 → API 映射

| 决策概念 | Flutter 实现 |
|---------|-------------|
| ease-out | `Curves.easeOutCubic` / `Cubic(0, 0, 0.2, 1)` |
| ease-in-out | `Curves.easeInOutCubic` / `Cubic(0.4, 0, 0.2, 1)` |
| 过冲（Playful） | `Curves.easeOutBack` / `Curves.elasticOut` |
| 时长 | `AnimationController(duration: Duration(milliseconds: 350))` / 隐式动画 duration |
| 加载资产 | `Lottie.asset('assets/animations/x.json', repeat: false)` / `Lottie.network(url)` / `Lottie.memory(bytes)` |
| 播放控制 | 自动：`animate: true`；精控：`controller: _controller` + `onLoaded` |
| 循环 | `repeat: true` / `_controller.repeat()` |
| 速度 | 调 controller duration / `Lottie.delegates` |
| 跳帧/分段 | controller 值域锚定（`_controller.value` 区间） |
| 反向 | `_controller.reverse()` / `reverse: true` |
| 换色 | `Lottie.delegates`（ValueDelegate 颜色替换） |
| 完成回调 | `_controller.addStatusListener(AnimationStatus.completed)` |
| 释放 | `_controller.dispose()`（State.dispose MUST 调用） |

## 四、资产规范与坑位（逐条必防）

1. **pubspec 声明铁律**：JSON 必须在 `flutter: assets:` 节声明，路径精确匹配且**大小写敏感**（Linux/macOS 构建机编译不过）
2. **时长同步铁律**：用 AnimationController 精控时，MUST 在 `onLoaded(composition)` 回调里 `_controller.duration = composition.duration`——否则 controller 默认 300ms 与动画实际时长失步
3. **远程占位铁律**：`Lottie.network` 必须提供 loading/fallback UI（网络慢时白块）
4. 性能三件：`Lottie.cache.width/height` 缓存组合；包 `RepaintBoundary` 隔离重绘；大列表项禁大资产（用冻结帧）
5. zip 资产直接 `Lottie.asset('assets/xx.zip')`（带图动画）
6. Web 平台：SVG 渲染特征与移动端一致，但注意包体积（首帧解析成本）

## 五、代码模板（黄金用例）

规格单：〔卡片入场|Premium|position+opacity|350ms|cubic-bezier(0.4,0,0.2,1)|0%|primary+secondary(shadow 延迟 50ms)〕

**分支 A：显式动画（本规格推荐）**

```dart
import 'package:flutter/material.dart';

// 决策概念映射：Premium 0 过冲 → Cubic(0.4,0,0.2,1)，禁 Curves.easeOutBack/elasticOut
class PremiumCardEnter extends StatefulWidget {
  const PremiumCardEnter({super.key, required this.child});
  final Widget child;

  @override
  State<PremiumCardEnter> createState() => _PremiumCardEnterState();
}

class _PremiumCardEnterState extends State<PremiumCardEnter>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 350),
    );
    // CRITICAL 自检：Transform.translate/Opacity = transform 等价，非 layout 属性
    _animation = CurvedAnimation(
      parent: _controller,
      curve: const Cubic(0.4, 0, 0.2, 1),   // Premium 签名缓动
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();   // 释放铁律
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // a11y 降级（HIGH：H6）
    final bool reduceMotion =
        MediaQuery.of(context).disableAnimations;
    if (reduceMotion) {
      return widget.child;   // 直接落终态
    }
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        final t = _animation.value;
        return Opacity(
          opacity: t,
          child: Transform.translate(
            offset: Offset(0, 20 * (1 - t)),
            child: DecoratedBox(
              // secondary：阴影延迟由 Interval 实现（50ms/350ms ≈ 0.14 起）
              decoration: BoxDecoration(
                boxShadow: [
                  BoxShadow(
                    blurRadius: 12 * t,
                    color: Color.fromRGBO(0, 0, 0,
                        0.15 * Interval(0.14, 1, curve: Curves.linear).transform(t)),
                  ),
                ],
              ),
              child: child,
            ),
          ),
        );
      },
      child: widget.child,
    );
  }
}
```

**分支 B：Lottie 资产（复杂矢量动效）**

```dart
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';

class LottieCardEnter extends StatefulWidget {
  const LottieCardEnter({super.key, this.onFinish});
  final VoidCallback? onFinish;

  @override
  State<LottieCardEnter> createState() => _LottieCardEnterState();
}

class _LottieCardEnterState extends State<LottieCardEnter>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(                        // 坑位 4：隔离重绘
      child: Lottie.asset(
        'assets/animations/card_enter.json',       // 坑位 1：路径 + pubspec 声明
        controller: _controller,
        repeat: false,                             // Premium 单次
        onLoaded: (composition) {
          // 坑位 2：时长同步铁律
          _controller
            ..duration = composition.duration
            ..forward()
            ..addStatusListener((status) {
              if (status == AnimationStatus.completed) {
                widget.onFinish?.call();
              }
            });
        },
      ),
    );
  }
}
```

## 六、性能与 a11y

- 动画属性仅 `Transform`/`Opacity`/`AnimatedOpacity`（合成层）；NEVER 动画 `Container` 尺寸/margin（触发 layout 管线）
- 组合动画用 `Interval` 错峰（替代多 controller）；`RepaintBoundary` 隔离高频重绘区域
- 大资产低端机掉帧：预解析 `AssetLottie(...).load()` 缓存 composition；`frameRate: FrameRate.max` 按需
- **reduced-motion**：`MediaQuery.of(context).disableAnimations`——降级：直接落终态/仅保留 Opacity 过渡/去 Transform 位移；Lottie 可冻结末帧（`animate: false` + `LottieCache`）
- 关键信息 NEVER 仅靠动效传达；`Semantics` 补充语义
