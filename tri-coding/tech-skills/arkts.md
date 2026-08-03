---
name: tech-arkts
description: 鸿蒙 ArkTS 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 ArkTS 特定的编码标准与质量检查。
tech_id: arkts
tech_name: 鸿蒙ArkTS
category: platform
---

# 鸿蒙 ArkTS 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加鸿蒙 ArkTS 特定规范。

## 技术栈定义

ArkTS 是鸿蒙操作系统（HarmonyOS）的应用开发语言，基于 TypeScript 扩展而来，专为鸿蒙应用开发设计。核心特性包括：声明式 UI（ArkUI）、状态管理装饰器、组件化开发、鸿蒙特有 API 与系统能力。ArkTS 通过 `@Component`、`@State` 等装饰器与 `build()` 方法描述界面结构与响应式更新。

## 版本基线

- **HarmonyOS 4.x**：基于 ArkUI 1.0，支持基础声明式 UI 与状态管理装饰器
- **HarmonyOS 5.x (NEXT)**：纯血鸿蒙，移除 AOSP 兼容层，API 12+，强化 ArkUI 组件能力与 Stage 模型
- **DevEco Studio**：推荐使用 DevEco Studio 5.0+ 进行开发与调试

## 编码规范（技术特定）

### 声明式 UI 与组件

- **`@Component` 装饰器**：使用 `@Component` 装饰 `struct`（非 `class`）声明自定义组件，组件须实现 `build()` 方法返回 ArkUI 组件树
- **`@Entry` 装饰器**：页面入口组件须同时使用 `@Entry` + `@Component` 装饰，一个页面有且仅有一个 `@Entry`
- **`build()` 方法**：每个组件必须有且仅有一个 `build()` 方法，通过链式调用构建组件树（如 `Column() { ... }.padding(20)`），**禁止使用 JSX 语法**
- **组件树结构**：UI 由内置容器组件（Column/Row/Stack/Flex/List/Grid 等）与基础组件（Text/Button/TextInput/Image 等）组合构成，通过尾随闭包嵌套

### 状态管理装饰器

- **`@State`**：组件内部状态，变更触发 UI 重新渲染；须在声明时初始化
- **`@Prop`**（单数形式，注意不要写成复数）：父→子单向数据传递，子组件不可修改；须在声明时初始化
- **`@Link`**：父↔子双向数据绑定，父子组件共享同一数据源；父组件须用 `$` 前缀传递（如 `@Link count: number`，父组件传 `$count`）
- **`@Provide` / `@Consume`**：跨层级数据传递，祖先 `@Provide` 后代 `@Consume`，避免逐层传递
- **`@ObjectLink` / `@Observed`**：用于嵌套对象/数组的深度响应式，`@Observed` 标记类，`@ObjectLink` 接收实例
- **`@Watch`**：监听 `@State`/`@Prop`/`@Link` 变化，触发回调函数

### 构建器与复用

- **`@Builder`**：将 UI 片段封装为可复用构建函数，类似渲染函数
- **`@BuilderParam`**：组件接收外部传入的 UI 构建逻辑，实现插槽模式
- **`@Styles`**：封装通用样式属性集合，可复用
- **`@Extend`**：扩展内置组件的样式方法

### 生命周期

- **`aboutToAppear`**：组件创建后、`build()` 前调用，用于数据初始化
- **`aboutToDisappear`**：组件销毁前调用，用于资源清理
- **`onPageShow` / `onPageHide`**：页面级生命周期（仅 `@Entry` 组件），页面显示/隐藏时触发
- **`onBackPress`**：返回键拦截（仅 `@Entry` 组件），返回 `true` 拦截返回

### 类型与异步

- **类型安全强化**：充分利用 ArkTS 类型系统，减少 `any` 类型使用；ArkTS 限制部分 TS 动态特性（如 `Object.assign` 运行时改属性）
- **异步处理标准化**：使用 `async/await`，错误处理模式统一；禁止在 `build()` 中直接调用异步方法
- **鸿蒙特有 API**：调用系统能力（认证、生物识别、分布式能力等）时遵循 `@ohos.*` 模块导入约定

### 资源管理与性能

- **资源引用**：使用 `$r('app.string.xxx')` / `$r('app.media.xxx')` 引用资源，禁止硬编码字符串与图片路径
- **LazyForEach**：长列表须使用 `LazyForEach` 替代 `ForEach` 实现按需加载，避免一次性渲染全量数据
- **`@Reusable`**：可复用组件标记 `@Reusable`，配合 `aboutToReuse` 实现组件复用，降低创建开销
- **Stage 模型**：HarmonyOS 5.x 须使用 Stage 模型（`module.json5` 配置），FA 模型已废弃

### 代码示例

```typescript
// 正确的 ArkUI 声明式语法示例
@Entry
@Component
struct LoginForm {
  @State username: string = ''
  @State password: string = ''
  @State isLoading: boolean = false
  @State errorMsg: string = ''

  aboutToAppear() {
    console.info('LoginForm aboutToAppear')
  }

  async handleLogin() {
    if (!this.username || !this.password) {
      this.errorMsg = '请输入用户名和密码'
      return
    }
    this.isLoading = true
    this.errorMsg = ''
    try {
      const result = await this.authenticate(this.username, this.password)
      if (result.success && result.token) {
        // 登录成功，路由跳转
      } else {
        this.errorMsg = result.error || '认证失败'
      }
    } catch (error) {
      this.errorMsg = '网络错误，请稍后重试'
      console.error('登录失败: ' + JSON.stringify(error))
    } finally {
      this.isLoading = false
    }
  }

  build() {
    Column({ space: 16 }) {
      Text('用户登录')
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
        .margin({ bottom: 20 })

      TextInput({ placeholder: '请输入用户名' })
        .type(InputType.Normal)
        .width('100%')
        .onChange((value: string) => {
          this.username = value
        })

      TextInput({ placeholder: '请输入密码' })
        .type(InputType.Password)
        .width('100%')
        .onChange((value: string) => {
          this.password = value
        })

      if (this.errorMsg) {
        Text(this.errorMsg)
          .fontSize(14)
          .fontColor('#f87171')
      }

      Button(this.isLoading ? '登录中...' : '登录')
        .width('100%')
        .type(ButtonType.Capsule)
        .enabled(!this.isLoading)
        .onClick(() => {
          this.handleLogin()
        })
    }
    .padding(20)
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

## 质量检查清单（技术特定）

- [ ] 自定义组件是否使用 `@Component` 装饰 `struct`（非 `class`）
- [ ] 页面入口组件是否同时使用 `@Entry` + `@Component`
- [ ] 每个组件是否提供唯一 `build()` 方法，使用链式调用构建组件树（禁止 JSX）
- [ ] 组件内部状态是否使用 `@State` 装饰并正确初始化
- [ ] 父→子单向传递是否使用 `@Prop`（单数形式，非复数）
- [ ] 双向绑定是否使用 `@Link`，父组件是否用 `$` 前缀传递
- [ ] 跨层级数据是否使用 `@Provide` / `@Consume`
- [ ] 嵌套对象/数组响应式是否使用 `@Observed` + `@ObjectLink`
- [ ] 是否避免使用 `any`，充分利用 ArkTS 类型系统
- [ ] 异步逻辑是否使用 `async/await` 并统一错误处理，`build()` 中无直接异步调用
- [ ] 长列表是否使用 `LazyForEach` 而非 `ForEach`
- [ ] 资源引用是否使用 `$r()` 而非硬编码
- [ ] HarmonyOS 5.x 项目是否使用 Stage 模型

## 参考资料

- [鸿蒙官方 ArkTS 文档](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-overview-0000001504854173)
- [ArkUI 组件参考](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-ts-components/ReadMe-0000001504434868)
- [ArkTS 状态管理](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-state-management-0000001504554092)
- [HarmonyOS 应用开发指南](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/application-dev-guide-0000001493784089)
