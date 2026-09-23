# tri-lottie — 跨端动效决策与执行库

> tri-intent 下游执行 skill（I11 编码开发 · motion 动效实现子类）。

## 特性

- **决策与执行分离**：8 步清单产出技术栈无关「动效规格单」→ 六端实现翻译，规格可跨端复用
- **六端覆盖**：Web（lottie-web）/ Android（lottie-android+lottie-compose）/ iOS（lottie-ios）/ 鸿蒙 ArkTS（@ohos/lottie）/ React Native（lottie-react-native）/ Flutter（lottie 包）
- **坑位前置**：各端 implementation.md 内置防御清单（ArkTS 路径铁律、Expo 版本匹配、Flutter pubspec 声明等）
- **质量门**：CRITICAL/HIGH/MEDIUM 三级（映射家族 P0/P1/P2），一票否决条款
- **可访问性内建**：六端 reduced-motion 降级实现随代码模板交付
- **上游信息零残留**：产物不含任何上游作者/品牌署名（第三方库仅保留安装坐标）

## 目录结构

```
tri-lottie/
├── SKILL.md               # 主入口：工作流 + 六端路由 + 质量门
├── scripts/
│   ├── check_update.py    # 版本门第零步（同源 tri-forge）
│   └── compliance_check.py # 结构合规 + 六端断言测试执行器
├── references/            # 决策层（5 篇）：tokens/personality/emotion/quality/recipes
├── stacks/                # 执行层（6 端）：web/android/ios/harmonyos-arkts/react-native/flutter
└── tests/                 # 全场景测试用例
```

## 安装

```bash
skillhub install tri-lottie --dir <目标目录>
# 或经 tri-intent 快照路由自动检测安装
```

## 使用

```
「给这个按钮加个俏皮的按压动画，Web」      → 规格单 + CSS/lottie-web 代码
「鸿蒙上用 Lottie 做加载态」              → stacks/harmonyos-arkts 实现（含路径铁律）
「审查这段动画代码」                      → 三级问题清单 + 修复方案
「优雅的卡片入场」（无技术栈）             → 规格单 + 追问目标端（停车态）
```

## 测试

```bash
python scripts/compliance_check.py          # T1-T10 结构与六端断言（退出码 0=全过）
python scripts/check_update.py --slug tri-lottie --json   # 版本门
python <tri-forge>/scripts/verify_sync.py --slug tri-lottie --intent-dir <tri-intent 路径>
```

## 设计原则

1. 决策先行：NEVER 跳过规格单直接写代码
2. 端知识唯一事实源：端上 API 以 stacks/ 文档为准，NEVER 凭记忆内联
3. 简单动效零依赖：CSS/框架内置动画优先，Lottie 仅用于设计师资产
4. 诚实边界：无法在本机编译的端如实标注，交付目标环境验证路径
