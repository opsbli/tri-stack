# Changelog

本文件记录 tri-video（tri-mm 视频类子SKILL）的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.2.0] - 2026-09-22

### 修复

- **版本门可执行入口缺失**（P0）：独立使用时无确定性版本门入口。补齐 `scripts/check_update.py`（与家族同源，`--help` 冒烟 exit 0），SKILL.md §版本检查要点新增第 0 条（`python scripts/check_update.py --slug tri-video --json`，state 四态 + 退出码 <20 放行 / ≥20 阻断）
- **version-check-spec 引用悬空**（P1）：SKILL.md 引用 `references/version-check-spec.md` 但文件不存在。新增瘦指针 STUB（真源随 tri-mm 包分发 `tri-mm/references/version-check-spec.md`），装配顺序表与目录结构同步
- **参考实现依赖悬空**（P2）：用卡三读法则第 2 读隐含"必有 demo 源码"，与不随包分发参考实现的现实矛盾。补「库内暂无参考实现时」回退：以卡面参数表为参数真相 + 验收帧加倍（4 个）+ 实现后回填已知坑
- **采集模板依赖暗示**（P2）：capture-and-camera「复制后改」暗示随包存在模板文件，改为「现场编写一次性可配置采集脚本（Playwright/Puppeteer）」
- tests 增补 J 组能力点（J1–J4）与 T25–T28 用例（24 → 28），覆盖版本门脚本/瘦指针/无参考实现回退/采集自洽

### 新增

- **双制作路线判定**（契约⑧ + 七处同步）：新增 §制作路线判定——AI 生成工具路线（默认）与代码渲染精确路线（程序化逐帧渲染）；判定结果写入 design.md 首行与自检句；双路线均可行时对比交用户选择。同步更新：触发时机（追加代码渲染关键词）、强制契约、输入契约（D2/D4 路线信号）、职责边界（音频分工细化）、落盘规则、交付产物、自检句（含制作路线字段）
- **代码渲染方法论知识包**（`references/` 5 文件，常驻层，含装配顺序声明与 grep 路由表）：
  - `production-pipeline.md`：八阶段制作流水线、三推进模式（模板复现/自主推进/共创确认）、品牌→动效参数两轴六预设表、逐镜头实现常见坑、无头渲染三坑
  - `aesthetic-rules.md`：判例式审美准则 26 条（R 节奏 4 / Q 质感 11 / S 声音 5 / C 文案 3 / P 流程 4），编号不重排只追加，违反须写项目文档
  - `shot-card-system.md`：镜头配方卡 frontmatter schema、十类分类学、用卡三读法则（命门参数不得降档）、能量弧四段位模板、自建卡规范
  - `capture-and-camera.md`：素材采集三件套（全页 2x/per-element cutout/layout.json）、2.5D 页面相机 CamKey 模型、CSS zoom 高清栅格化技法、数据脱敏口径
  - `beat-sync-sound.md`：BGM 卡点方法论（网格拟合/残差 ≤±15ms/半倍双倍歧义/渲后回测 ≤3f）、声音设计（片种选音/钉帧表/防机枪三招/结尾句式）、音画对齐补偿公式
- **确定性算法下沉**：`scripts/beat_grid_fit.py`——节拍网格最小二乘拟合 + 覆盖率歧义裁决 + 分段拟合定位变速段（JSON 输出，PASS/FAIL 退出码）
- **质量标准**：新增准则自检/独立终检/确定性渲染/卡点精度（切点 ≤3f）/音画对齐 5 项（代码渲染路线）
- **交付产物**：新增静帧验收档案（`out/qa/`）与独立终检报告；配 BGM 的代码渲染片固定交付带/无 BGM 双版本
- tests 增补 T11–T24（路线判定/知识包装载/准则过检/独立终检/确定性渲染/卡点/双版本/音画对齐/分工边界），用例总数 10 → 24

## [1.1.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源 `tri-intent/references/version-gate.md`，消除各 skill 内的重复表述
- frontmatter version `1.1.0` → `1.1.1`

## [1.1.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
  - mermaid 流程图展示完整决策链路
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目，明确版本检查为执行流程第零步，更新完成前 NEVER 进入后续步骤

### 变更

- frontmatter version `1.0.0` → `1.1.0`

## [1.0.0] - 2026-08-02

### 新增

- 初始版本：tri-mm 的视频类子SKILL，处理 I15 视频意图
- 10 维视频设计方法论：时长结构/分镜头/运镜/转场/画面/旁白/字幕/节奏/画幅/平台
- 分镜头 design.md 模板（镜头/时长/画面/景别/运镜/转场/字幕/音效 表）
- 设计方案确认门：先分镜头方案确认，确认后再生成
- 子任务协同：旁白→tri-audio、BGM→tri-music
- 链路文档落盘 `.tribro/multimedia/video/<命名>/`（design.md + result.md）
