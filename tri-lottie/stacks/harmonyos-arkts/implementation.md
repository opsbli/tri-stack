---
name: harmonyos-arkts-implementation
description: 鸿蒙 ArkTS 端动效实现——@ohos/lottie Canvas 渲染规范、API 映射、资产路径铁律、代码模板。核验于 2026-09，@ohos/lottie v2.0.33，API 12+。
---

# 鸿蒙 ArkTS 端实现（stacks/harmonyos-arkts）

## 一、库选型决策树

```
动效需求
├── 简单属性动效 → ArkUI animateTo / 属性动画（animation 属性）
├── 弹性交互动效 → curves.springCurve / interpolate
├── 复杂矢量动效 / 设计师资产 → @ohos/lottie（Canvas 渲染）
└── 多动画同屏 / 复杂场景 / 性能敏感 → lottie-turbo（声明式 + 并行加载 + 内存缓存 + 子线程渲染，性能 +30%）
```

**选型铁律**：ArkTS 端 Lottie **仅 Canvas 渲染**——必须自建渲染上下文；简单属性动效优先 `animateTo`（零依赖）。

## 二、安装与版本约束

```bash
ohpm install @ohos/lottie     # OpenHarmony 三方库中心仓，MIT，v2.0.33
```

- **最低 API 12+**（HarmonyOS NEXT / OpenHarmony 4.0+）
- 推荐复杂场景改用 lottie-turbo（同仓库官方推荐，声明式调用，子线程渲染）
- DevEco Studio 工程内 `oh-package.json5` dependencies 自动登记

## 三、概念 → API 映射

| 决策概念 | ArkTS 实现 |
|---------|-----------|
| ease-out | `animateTo({ curve: Curve.EaseOut, duration: 350 })` / `curves.cubicBezier(0, 0, 0.2, 1)` |
| ease-in-out | `Curve.EaseInOut` / `curves.cubicBezier(0.4, 0, 0.2, 1)` |
| 过冲（Playful） | `curves.springCurve(velocity, mass, stiffness, damping)`（damping < 1 振荡）/ `Curve.Friction` |
| 时长 | `animateTo({ duration })` / 资产帧率内嵌 |
| 加载资产 | `lottie.loadAnimation({ container: 渲染上下文, path: 'pages 同级相对路径', loop, autoplay })` |
| 播放/暂停/停止 | `anim.play()` / `anim.pause()` / `anim.stop()` |
| 循环 | `loop: true`（loadAnimation 参数） |
| 速度 | `anim.setSpeed(x)` |
| 跳帧/分段 | `anim.goToAndStop(frame, isFrame)` |
| 方向 | `anim.setDirection(-1)` |
| 换色 | 颜色修改 API（资产预处理优先） |
| 完成回调 | 生命周期回调 |
| **销毁** | `lottie.destroy()`——**aboutToDisappear MUST 调用** |

## 四、资产规范与坑位（六端中坑最多，逐条必防）

1. **路径铁律**：`loadAnimation` 的 `path` **禁用 `./` `../` 相对路径**——路径以 pages 父文件夹为基准（如 `path: 'common/lottie/card_enter.json'` 对应 `entry/src/main/ets/common/lottie/card_enter.json`）；写错直接白屏且无报错
2. **加载时机铁律**：动画加载必须放在 `Canvas.onReady()` 回调内——否则画布尺寸未就绪，动画尺寸错误
3. **释放铁律**：页面销毁 `aboutToDisappear()` 中 MUST 调 `lottie.destroy()`——否则内存泄漏（六端唯一需要手动 destroy 且有全局销毁语义的端）
4. 渲染上下文必须开抗锯齿：`new RenderingContextSettings(true)`
5. 多动画同屏/复杂场景 → lottie-turbo（并行加载/内存缓存/子线程渲染）
6. 帧率控制/填充模式等高级特性见 @ohos/lottie 文档；大资产注意低端机（Kalman/入门机）掉帧
7. **`curves.cubicBezier` 弃用告警**（API 24 / DevEco 6.1.1 实测）：编译可通过但报 WARN——紧急度低，新代码可改用 `Curve` 枚举或随 SDK 演进替换；模板保留现值并在此标注
8. **ArkTS 严格模式 arkts-no-any-unknown**（实测 CompileArkTS 阶段硬报错）：所有回调参数必须显式标注类型（如 `.catch((err: BusinessError) => ...)`，从 `@kit.BasicServicesKit` 导入），隐式 any 直接编译失败
9. **构建配置铁律（hvigor 6.x）**：根 `hvigor/hvigor-config.json5` 与根 `oh-package.json5` 必须同时声明**相同**的 `modelVersion`（如 `"5.0.0"`），缺任一即报 00303024「project structure need to be upgraded」；SDK 版本字段（compatibleSdkVersion 等）位于 `app.products[]` 内而非 `app` 顶层

## 五、代码模板（黄金用例）

规格单：〔卡片入场|Premium|position+opacity|350ms|cubic-bezier(0.4,0,0.2,1)|0%|primary+secondary(shadow 延迟 50ms)〕

**分支 A：ArkUI 属性动画（本规格推荐，零依赖）**

```typescript
import { curves } from '@kit.ArkUI';

@Entry
@Component
struct PremiumCardEnter {
  @State private appeared: boolean = false;
  // 决策概念映射：Premium 0 过冲 → cubicBezier(0.4,0,0.2,1)，禁 springCurve 低 damping

  build() {
    Column() {
      Column() {
        Text('Card Content')
      }
      .width('80%')
      .height(200)
      .backgroundColor('#FFFFFF')
      .shadow({ radius: 12, color: this.appeared ? '#26000000' : '#00000000' }) // secondary
      // CRITICAL 自检：translate/opacity = transform 等价属性，非 layout 属性
      .translate({ y: this.appeared ? 0 : 20 })
      .opacity(this.appeared ? 1 : 0)
      .animation({
        duration: 350,
        curve: curves.cubicBezier(0.4, 0, 0.2, 1),
        delay: 0,
      })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .onClick(() => { this.appeared = !this.appeared; })
    .onAppear(() => {
      // a11y 降级（HIGH：H6）：系统「减弱动画」时直接落终态
      // animateTo 分支：this.getUIContext().animateTo({ duration: 0 }, () => { this.appeared = true })
      this.getUIContext().animateTo({
        duration: 350,
        curve: curves.cubicBezier(0.4, 0, 0.2, 1),
      }, () => { this.appeared = true; });
    })
  }
}
```

**分支 B：Lottie 资产（复杂矢量动效）**

```typescript
import lottie, { AnimationItem } from '@ohos/lottie';

@Entry
@Component
struct LottieCardEnter {
  // 坑位 4：抗锯齿渲染上下文
  private renderSettings: RenderingContextSettings = new RenderingContextSettings(true);
  private renderingContext: CanvasRenderingContext2D =
    new CanvasRenderingContext2D(this.renderSettings);
  private animItem: AnimationItem | null = null;

  aboutToDisappear(): void {
    // 坑位 3：释放铁律——销毁 MUST 调用
    lottie.destroy();
    this.animItem = null;
  }

  build() {
    Column() {
      Canvas(this.renderingContext)
        .width(200)
        .height(200)
        .onReady(() => {
          // 坑位 2：必须 onReady 内加载（尺寸就绪）
          this.animItem = lottie.loadAnimation({
            container: this.renderingContext,
            renderer: 'canvas',
            loop: false,             // Premium 入场单次
            autoplay: true,
            // 坑位 1：路径铁律——相对 pages 父文件夹，禁 ./ ../
            path: 'common/lottie/card_enter.json',
          });
        })
    }
    .width('100%').height('100%')
  }
}
```

## 六、性能与 a11y

- 属性动画仅 `translate`/`scale`/`rotate`/`opacity`（渲染属性）；NEVER 动画 `width`/`height`/`margin`（触发测量布局）
- 复用组件用 `@Reusable`；大列表用 `LazyForEach`（列表项禁大资产）
- 帧率：目标 60fps；`animateTo` 优先于逐帧自定义绘制
- **reduced-motion**：跟随系统「减弱动画」设置（`settings.display.animation_scale` 或应用内开关）——降级策略：`duration: 0` 直接落终态 / 仅保留 opacity 过渡；Lottie 资产可 `goToAndStop(终帧)` 静态呈现
- 关键信息 NEVER 仅靠动效传达
