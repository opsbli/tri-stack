---
name: tri-lottie-full-testcases
description: tri-lottie 全场景测试用例——结构合规 / 决策规格单 / 六端代码断言 / 审查模式 / Web 真实渲染 / RN·Flutter 语法解析。
基于 tri-lottie v1.0.6
---

# tri-lottie 全场景测试用例

> 执行器：`python scripts/compliance_check.py`（T1-T10 自动判定）；T11-T13 为工具链级真实测试（见各节执行命令）。

## 一、结构合规组（T1-T8 · compliance_check.py 自动执行）

| # | 用例 | 输入 | 预期 |
|---|------|------|------|
| T1 | frontmatter 合规 | SKILL.md | 八字段齐全；name==slug==tri-lottie（kebab）；description 含「支持独立安装，含上游依赖检测三态逻辑」 |
| T2 | 上游信息零残留 | 全部 .md/.py | 上游品牌关键词表（见 compliance_check.py T2 banned 清单，坐标白名单除外）= 0 命中 |
| T3 | 版本四件套 | SKILL/CHANGELOG/tests | 三处版本号 == 1.0.1 |
| T4 | 行数约束 | SKILL.md | ≤ 500 行 |
| T5 | 目录树 diff | SKILL.md §目录结构 vs 磁盘 | 无遗漏、无幻影 |
| T6 | 版本门三件套 | scripts/check_update.py | 退出码 <20 且 state∈{A,B,C,D}；SKILL.md 含第零步 + ≤30 行 STUB 指针 |
| T7 | 禁文件 | 目录扫描 | 无 LICENSE / .gitignore |
| T8 | 合规章节 | SKILL.md | 契约/三态检测/自检句/进化契约三要素/完成判据停车区分/知识装配顺序/质量标准独立二级 |

## 二、六端代码模板断言组（T9-T10 · compliance_check.py 自动执行）

| # | 用例 | 断言要点 |
|---|------|---------|
| T9-web | Web 模板 | `anim.destroy()` / `prefers-reduced-motion` / svg 渲染器 / loadAnimation / Premium bezier |
| T9-android | Android 模板 | lottie-compose artifact / minSdk 21 / ANIMATOR_DURATION_SCALE 降级 / CubicBezierEasing / AndroidX |
| T9-ios | iOS 模板 | iOS 13.0 / accessibilityReduceMotion / LottieAnimationView / timingCurve / Swift 5.7 |
| T9-arkts | ArkTS 模板 | onReady 内加载 / aboutToDisappear destroy / 抗锯齿上下文 / 路径禁 `./` `../` / @ohos/lottie |
| T9-rn | RN 模板 | expo install / development build / useIsFocused 暂停 / onAnimationFinish / colorFilters |
| T9-flutter | Flutter 模板 | pubspec assets 声明 / onLoaded 同步 duration / disableAnimations / controller.dispose |
| T10 | 黄金用例一致性 | 六端模板均含 350ms 时长 + Premium 缓动签名 (0.4, 0, 0.2, 1) 等价实现 |

## 三、路由同步组（T11 · verify_sync.py）

| # | 用例 | 命令 | 预期 |
|---|------|------|------|
| T11 | tri-intent 回填校验 | `python <tri-forge>/scripts/verify_sync.py --slug tri-lottie --intent-dir <tri-intent 路径>` | 输出 `status=OK`，tri-lottie 出现在路由映射表/计数/检测路径 |

## 四、工具链真实测试组（T12-T13 · 依本机工具链可用性执行）

| # | 用例 | 命令/方式 | 预期 | 本机执行策略 |
|---|------|----------|------|-------------|
| T12 | Web 真实渲染 | Node + lottie-web + 无头浏览器加载合法 Lottie JSON，断言 totalFrames>0 且帧推进 | 动画实例创建成功并播放 | MUST 真实执行（本机可跑） |
| T13 | RN/Flutter 语法解析 | esbuild/babel 解析 RN JSX；python 断言 Flutter Dart 模板结构 | 语法 0 错误 | 有工具链则真实执行；无则如实标注 |

> 无法在本机编译的端（Android/iOS/ArkTS 原生编译）由 T9 静态断言覆盖 + implementation.md「核验于」标注；NEVER 谎称已真机编译。

## 五、人工场景用例（agent 行为验证）

| # | 场景 | 输入 | 预期行为 |
|---|------|------|---------|
| S1 | 实现全流程 | 「支付成功庆祝动画，鸿蒙」 | 规格单（Joy+Confidence）→ stacks/harmonyos-arkts → 代码含路径铁律/onReady/destroy |
| S2 | 未指定技术栈 | 「加个优雅的卡片入场」 | 输出规格单并追问目标端（停车态，NEVER 猜端） |
| S3 | 审查模式 | 一段 linear + 纯 opacity 动画代码 | 报 CRITICAL C1+C2，给修复方案 |
| S4 | 选型防误用 | 「hover 高亮」 | 命中「简单属性动效」分支，不引入 Lottie |
| S5 | 降级模式 | 拒绝安装 tri-intent | 声明降级模式后照常产出规格单+代码 |
