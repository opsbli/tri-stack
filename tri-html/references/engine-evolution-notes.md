# 外部图表引擎演进对照（engine-evolution-notes）

> 本文件是 `scripts/viewer/`（vendored 图表引擎）的**维护者视角演进对照登记**，供后续引擎同步评估使用。命名遵循 `references/THIRD-PARTY-NOTICE.md` 的中性称谓约定（「外部项目」/「外部引擎」）。**本文件描述的差距项在引擎补齐前不进入创作路径**——作者契约（`viewer-authoring.md`）永远只承诺当前 vendored 引擎真实具备的能力。

## 一、现状基线

vendored 基线能力（已验证可用）：

- 五类渲染器（architecture / workflow / sequence / dataflow / lifecycle）+ shared 共享层（validator / geometry / diagnostics / i18n / legend 等 16 模块）；
- 16 子命令 CLI（render / compare / deliver / preview / validate / inspect / check / visual-check / guide / brands / brands capture / examples / doctor / demo 等）；
- showcase 客观门禁（9 项检查）、原子提交 + SHA-256 回执、失败保留上一成品、compare 回滚恢复（恢复目录保留）；
- `visual-check` 四档桌面视口量测（1440×900 / 1600×1000 / 1920×1080 / 2048×1320）+ 深浅主题截图；
- `meta.locale`（en / zh-CN）渲染器 UI 本地化；sequence `meta.column_fit: "spread"`；`meta.visual_preset`（signal-flow / blueprint / editorial）；`meta.engineering_profile`；
- `brands capture <url>` digest 固定捕获路径（需网络）；
- 零运行时 npm 依赖，Node ≥ 18。

## 二、外部演进差距登记（按能力域）

> 以下能力在外部引擎后续版本中已出现，vendored 基线**未跟进**。每项标注：现状、外部形态摘要（以对照基准档为据）、同步前置条件。

| # | 能力域 | vendored 现状 | 外部形态摘要 | 同步前置条件 |
|---|---|---|---|---|
| E1 | 工作流约束驱动编译器 | workflow 走 fixed 几何（schema v1 契约） | schema v2 `readable-v2`：列 `0..5` 逻辑秩 + 实测场景推导几何；`--layout-json` 暴露稳定编译器回执；相邻列容量失败给单因果诊断；字节稳定 v1 兼容承诺 | 移植 4400 行编译器 + 迁移几何模块；workflow schema 扩展；golden 测试重录 |
| E2 | workflow v1→v2 迁移通道 | 无 | `migrate workflow --to-schema 2`：非破坏坐标映射（via/labelAt/channelX → 秩空间），目标全检后才写盘，幂等可验证 | 依赖 E1 |
| E3 | 品牌标记目录数据与生成链 | **内置品牌发现可用**（标记编译于 `generated-brand-marks.mjs`，实测 `brands` 查询命中）；缺目录数据文件与生成链一致性检查（capture 溯源能力受限） | 目录数据文件 + 生成脚本 + `--check` fail-closed 一致性检查 | 移植目录 + 生成脚本；评估文件数预算与商标合规 |
| E4 | 机器可读参数错误回执 | 参数错误走 stderr 文本 | `validate --json` / `deliver --json` 把无效参数、未知选项、用法错误收进统一版本化失败回执（`arguments` 阶段 + 稳定诊断码 + 退出码 2） | CLI 层改造 + 回执 schema |
| E5 | 产物字体自包含 | **已轻量修复（2026-09-22）**：模板已移除 Google Fonts 外部引用，产物零外部引用可离线打开；字体走 local()/系统等宽回退链（跨机一致渲染未达成） | 交付 HTML/SVG 内嵌等宽变量字体子集（约 +96KB/件），离线渲染逐字节一致 | 模板与导出链改造；许可随包分发核验 |
| E6 | 输出文件类型白名单 | 常规校验 | render/deliver/preview/compare 拒绝非 HTML/非 JSON 目标（含符号链接路径） | CLI 层改造 |
| E7 | 包内更新探测 | 无（tri-html 由家族版本门承担，**建议保持不引入**，避免双更新通道冲突） | 缓存式仅通知检查 + 两段确认 | 评估后大概率**豁免** |

## 三、同步评估要点（下次引擎同步 MUST 核对）

1. **改名重放**：外部代码引入前须完整重放既有去标识改名（`viewer` 命名空间、`VIEWER:` 插槽标记、`viewer-` CSS 前缀、CLI 名称），grep 校验零残留。
2. **文件数预算**：skill 单包 ≤200 文件；外部包全量 219 文件，须按运行时子集裁剪（排除构建期生成器、渲染 HTML 示例、锁文件等）。
3. **「内层不动」记档**：`scripts/viewer/` 内部所有改动 MUST 在 `references/THIRD-PARTY-NOTICE.md`「修改说明」追加记录。
4. **能力-契约对齐**：引擎新增能力进入作者契约（`viewer-authoring.md`）前，MUST 在本机实测（doctor/demo/validate/deliver 冒烟）；未实测能力不得写入创作路径。
5. **回归门**：同步后跑通 `doctor`、`demo`、各类型 `validate` showcase、一次端到端 `deliver`，并把测试证据记入该次同步的 CHANGELOG 条目。

## 四、触发同步的时机建议

- 触发项（任一满足即评估）：① 用户场景明确需要工作流自动布局（E1）；② 需要批量内置品牌标记（E3）；③ 产物需要离线字体一致（E5）。
- 不触发项：E4/E6（体验增强，收益低于回归成本时延后）；E7（与家族版本门冲突，建议豁免）。

> 本文件为登记性文档：只陈述「外部已有什么、vendored 缺什么、同步要做什么」，不承诺同步时间表；同步决策属维护者职责。
