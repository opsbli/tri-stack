# Changelog

本文件记录 tri-image（tri-mm 图片类子SKILL）的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.0.0] - 2026-09-18

> 能力对齐大版本：从「9 维设计问卷」升级为「七场景 × 三轨生图执行引擎」。全部既有对外接口（输入契约字段、9 维设计契约、design.md / result.md、落盘根路径、两态上游依赖检测、自检句格式）保持不变。

### 新增

- **七场景能力层**：新增 `references/scenes/` 七个场景目录（cover / diagram / infographic / illustration / cards / slides / comic），每场景含操作规范 + Gallery 合订本
  - Gallery 合计 **157 个条目**合订为 17 个带锚点文件：信息图 21 版式 + 22 风格、配图 23 风格 + 4 调色板、卡片 12 预设 + 3 调色板 + 4 元素、幻灯片 17 风格 + 5 维度、漫画 6 画风 + 7 版式 + 5 体裁 + 7 基调、封面 11 调色板 + 7 渲染 + 3 维度、结构图 4 类布局细则
- **三轨管线**：Track-V（矢量确定性，结构图手绘 SVG，零额度）/ Track-R·T1（运行时原生生图，零第三方依赖）/ Track-R·T2（引擎 12 provider、批处理并行、精确比例）
- **生图引擎**（`scripts/engine/`）：整体平移，含 12 个 provider、批处理构建器、免密包装器；**零第三方依赖**（仅 Node 内置模块）
- **确定性脚本下沉**（家族硬约束 18）：
  - `scripts/aspect.py`——宽高比 → 像素尺寸，边长按 16 倍数对齐、长边 3840 上限、近似比自动折算
  - `scripts/svg_to_png.py`——SVG → @Nx PNG，多渲染器按序探测
  - `scripts/compress_image.py`——压缩/转码，跨平台探测 + 防覆盖
- **公共层去重**（`references/common/` 8 份）：原 6 份重复规则（用户输入工具、后端选择、批处理、确认门、参考图、水印、偏好键空间）合并为单一命名空间；补充统一输出契约
- **统一输出契约**：七种互不一致的落盘约定合并为 `.tribro/multimedia/image/<scene>-<slug>/`（根路径不变，`design.md`/`result.md` 位置不变）
- **开关别名统一**：`--quick` / `--yes` / `--no-confirm` 归一，新增 `--batch-size`、`--regenerate`、`--images-only`
- **完成判据外化**：P-1…P-6 机械校验项 + 停车态/结束态区分
- **知识装配顺序**：五层加载（常驻/场景/后端/参考图/外部覆盖）+ 去重优先级 + 每文件 grep 模式
- **进化契约与教训闭环**：新增 `.tribro/image/lessons.md` 读写闭环（启动读、缺失静默跳过、结束追加）
- **结论置信标注契约**：契约第 8 条，六类依据 + 可验证来源强制
- `_meta.json`（版本与元信息，纳入五处版本联动）

### 修复

- **P0-1 模态冲突**：原「禁止用 SVG 顶替光栅」与结构图产出 SVG 正面冲突 → 拆 Track-V / Track-R 双轨，该禁令作用域**限定为 Track-R**，并在场景路由表判定优先级
- **P0-2 文件数超限**：原 282 文件（剔测试 268）超单包 ≤200 → Gallery 合订（157 条目 → 17 文件）+ 公共层去重，最终 118 文件
- **P0-3 运行时依赖**：全部脚本原为 TS + Bun → 主链路改为零依赖（T1 原生轨 + Python 确定性脚本），TS 引擎降级为可选 T2
- **P1-1 Windows 不可用**：压缩脚本原用 `spawn("which")`（POSIX 专用）→ 改 `shutil.which` 跨平台探测
- **P1-1b 同名命令误伤（本次新发现）**：Windows `C:\Windows\system32\convert.exe` 是磁盘格式转换工具，与 ImageMagick `convert` 同名 → 新增身份校验（排除系统目录 + `-version` 输出含 `imagemagick`），NEVER 误调用
- **P1-2 重复配置追问**：原 6 个场景各自独立偏好命名空间 → 合并为单一 `preferred_image_backend` 等键空间，一次配置七场景通用
- **P1-3 输出目录冲突**：7 种落盘约定 → 统一（见上文「统一输出契约」）
- **P1-4 重复代码漂移**：引擎内免密包装器与 `packages/` 源为双份 → 只保留 skill 内副本
- **P1-5 并集丢失风险**：6 份免密调用档内容不一致（部分含 `n=1 per call` 批语义）→ 合并取**并集**，写入 `image-backend-rules.md` 的 coderef 契约
- **P1-7 SKILL.md 行数**：改为 Hub-Spoke，正文骨架 + 指针，大表下沉 `references/`
- **P2-1 开关不一致**：`--quick` / `--yes` / `--no-confirm` 归一
- **P2-2 缺少验证**：新增 `tests/verify_tri_image.py` 静态门禁 + 全场景用例

### 变更

- 强制执行契约由 7 条扩为 10 条（新增场景/轨道判定、提示词文件先行、结论置信标注）
- 自检句扩展为「本次意图=I15·图片，已读取快照，子类型=<…>，场景=<…>，轨道=<…>，设计方案已交付确认=<…>，已读教训=<…>」（原字段全部保留）
- frontmatter version `1.1.1` → `2.0.0`

## [1.1.1] - 2026-08-05

### 修复

- **版本门自动升级死命令**（P0）：`skillhub install <slug> --upgrade` 实测报 `unrecognized arguments: --upgrade`，改为正确命令 `skillhub upgrade <slug>`，并补 CLI 回退路径 `python ~/.skillhub/skills_store_cli.py upgrade <slug>`

### 变更

- **版本检查三态判定 → 四态判定**：新增 D 态（升级通道不可用降级），升级失败时标注降级继续而非死锁
- 版本检查节命令细则收敛为指向唯一真源，消除各 skill 内的重复表述
- frontmatter version `1.1.0` → `1.1.1`

## [1.1.0] - 2026-08-03

### 新增

- **版本检查与更新机制**：新增「版本检查与更新机制」独立章节，作为 skill 任一执行入口启动后的第零步。包含：
  - 设计原则与触发时机：版本检查 → 上游依赖检测 → 读取快照 → 核心执行 的执行顺序固化
  - 版本检查技术实现标准：校验端点、请求载荷、响应契约、SemVer 比较、超时控制（≤5s）、幂等性
  - 更新流程安全验证要求：来源校验（官方通道 ONLY）、SHA-256 完整性校验、签名校验、回滚保障、权限最小化、版本一致性联动
  - 六类禁止执行判定条件（P1–P6）及结构化阻断提示
- **强制执行契约第 0 条（版本检查前置硬门）**：优先级高于所有其他强制前置条目

### 变更

- frontmatter version `1.0.0` → `1.1.0`

## [1.0.0] - 2026-08-02

### 新增

- 初始版本：tri-mm 的图片类子SKILL，处理 I15 图片意图（位图/矢量图/图表）
- 9 维图片设计方法论：主题/风格/构图/色彩/光影/质感/画幅/参考/负向
- 设计方案确认门：先产出 `design.md` 交用户确认，确认后再生成
- 子类型差异参数（位图/矢量图/图表）
- design.md 模板与可扩展性机制（表格追加即扩展）
- 链路文档落盘 `.tribro/multimedia/image/<命名>/`（design.md + result.md）
