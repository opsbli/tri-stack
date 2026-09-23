---
name: react-native-implementation
description: React Native 端动效实现——lottie-react-native 双工作流（bare/Expo）、API 映射、资产规范、代码模板。核验于 2026-09，lottie-react-native 主版本 7.x（Expo SDK 内置集成）。
---

# React Native 端实现（stacks/react-native）

## 一、库选型决策树

```
动效需求
├── 简单属性动效 → Animated API / react-native-reanimated（手势驱动推荐）
├── 复杂矢量动效 / 设计师资产 → Lottie
│   ├── bare RN → npm i lottie-react-native + pod install（iOS）
│   └── Expo → npx expo install lottie-react-native（SDK 自动选兼容版本）
└── 屏幕转场 → react-navigation 内置转场（勿用 Lottie）
```

**选型铁律**：Lottie 组件渲染走原生桥（非 WebView）；简单反馈优先 Reanimated——NEVER 为 fade/slide 引入 Lottie 资产。

## 二、安装与版本约束

```bash
# bare RN
npm i lottie-react-native
cd ios && pod install && cd ..

# Expo（MUST 用 expo install，NEVER 手动 npm 装指定版本）
npx expo install lottie-react-native
# app.json 注册插件后重新预构建：
# { "expo": { "plugins": ["lottie-react-native"] } }
# npx expo run:ios / npx expo run:android
```

- **iOS 11+ / Android API 21+ / RN 0.71+**
- v6.0+ 原生支持 .lottie 压缩格式（约 -75% 体积）
- **Expo Go 沙箱不支持**——必须 development build

## 三、概念 → API 映射

| 决策概念 | RN 实现 |
|---------|--------|
| ease-out | Reanimated `Easing.out(Easing.cubic)` / Animated `Easing.out` |
| 过冲（Playful） | Reanimated `Easing.elastic()` / `withSpring({ damping: 低 })` |
| 时长 | Reanimated `withTiming(x, { duration: 350 })` |
| 加载资产 | `source={require('./card_enter.json')}`（打包）或 `source={{ uri: 'https://...' }}`（远程） |
| 播放/暂停 | ref 方法 `play(start?, end?)` / `pause()` / `resume()` / `reset()`；或 `autoPlay` prop |
| 循环 | `loop={true}` prop |
| 速度 | `speed={x}` prop |
| 跳帧/分段 | `ref.play(startFrame, endFrame)` |
| 换色 | `colorFilters={[{ keypath: 'layer', color: '#RRGGBB' }]}`（keypath 层名映射） |
| 完成回调 | `onAnimationFinish={(isCancelled) => {}}` |
| 销毁 | 组件卸载自动释放（无需手动 destroy） |

## 四、资产规范与坑位（逐条必防）

1. **Expo Go 不支持**：必须 dev build（`npx expo run:ios/android` 或 EAS Build）；App.json 需声明 plugin 后**重新预构建**（改原生配置不重预构建 = 不生效）
2. **版本匹配铁律**：Expo 项目必须 `npx expo install`（SDK 自动选兼容版本）——手动 `npm i lottie-react-native@旧版` 会在 Expo SDK 49+ 上 **Android 直接崩溃且无日志**
3. **列表铁律**：FlatList/FlashList 的列表项**禁放大资产**（每 cell 渲染代价高）——列表行用静态图标，动画留给独立屏
4. **不可见暂停**：屏幕失焦时 `ref.pause()`（`useIsFocused` + useEffect），省电省帧
5. 资产路径：`require('./assets/xxx.json')` 相对当前文件；远程 uri 需自带 loading 占位
6. 优先 .lottie 格式（v6.0+，-75% 体积，启动更快内存更省）

## 五、代码模板（黄金用例）

规格单：〔卡片入场|Premium|position+opacity|350ms|cubic-bezier(0.4,0,0.2,1)|0%|primary+secondary(shadow 延迟 50ms)〕

**分支 A：Reanimated 属性动画（本规格推荐）**

```tsx
import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  Easing,
  withDelay,
  interpolate,
} from 'react-native-reanimated';

// 决策概念映射：Premium 0 过冲 → withTiming + Easing.out 系，禁 withSpring 低 damping
// 等价曲线：Easing.bezier(0.4, 0, 0.2, 1)
export function PremiumCardEnter() {
  const progress = useSharedValue(0);

  useEffect(() => {
    // CRITICAL 自检：transform/opacity 等价，非 layout 属性
    progress.value = withTiming(1, {
      duration: 350,
      easing: Easing.bezier(0.4, 0, 0.2, 1),
    });
  }, []);

  const cardStyle = useAnimatedStyle(() => ({
    opacity: progress.value,
    transform: [{ translateY: interpolate(progress.value, [0, 1], [20, 0]) }],
  }));

  // secondary：阴影延迟 50ms
  const shadowStyle = useAnimatedStyle(() => ({
    shadowOpacity: withDelay(50, withTiming(0.15 * progress.value, { duration: 300 })),
  }));

  // a11y 降级（HIGH：H6）
  // const reduceMotion = useReducedMotion();  // reanimated 内置
  // reduceMotion ? progress.value = 1（直接落终态）: 正常动画

  return (
    <Animated.View style={[styles.card, cardStyle]}>
      <View style={StyleSheet.absoluteFill}>
        <Animated.View style={[styles.shadowLayer, shadowStyle]} />
      </View>
      <Text>Card Content</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  card: { padding: 16, backgroundColor: '#fff', borderRadius: 12 },
  shadowLayer: { flex: 1, borderRadius: 12 },
});
```

**分支 B：Lottie 资产（复杂矢量动效）**

```tsx
import React, { useRef, useEffect } from 'react';
import LottieView from 'lottie-react-native';
import { useIsFocused } from '@react-navigation/native';

export function LottieCardEnter({ onFinish }: { onFinish?: () => void }) {
  const animRef = useRef<LottieView>(null);
  const isFocused = useIsFocused();

  // 坑位 4：不可见暂停
  useEffect(() => {
    if (!isFocused) animRef.current?.pause();
  }, [isFocused]);

  return (
    <LottieView
      ref={animRef}
      source={require('./assets/card_enter.json')}   // 本地打包资产
      autoPlay                                        // Premium：入场即播
      loop={false}                                    // 单次
      speed={1}
      onAnimationFinish={(cancelled) => { if (!cancelled) onFinish?.(); }}
      style={{ width: 200, height: 200 }}
    />
  );
}
```

## 六、性能与 a11y

- 动画属性仅 `transform`/`opacity`（native driver 走 UI 线程）；NEVER 动画 `width/height/margin`（JS 桥逐帧通信 = 卡顿）；Reanimated 3 worklet 走 UI 线程
- 视口内动画元素 < 20；大列表用 `getItemType` 复用 + 静态图标
- `useNativeDriver: true`（Animated API）或 Reanimated（默认 UI 线程）
- **reduced-motion**：Reanimated `useReducedMotion()` / RN 内置 `AccessibilityInfo.isReduceMotionEnabled()`——降级：去位移/去弹性/保留 opacity 或直接落终态
- 关键信息 NEVER 仅靠动效传达；`accessibilityLabel` 补充语义
