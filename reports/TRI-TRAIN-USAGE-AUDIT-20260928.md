# tri-stack-train 会话审计 · 「每个功能开发都有 bug」归因分析

> 冻结报告 · 2026-09-28 · 证据源：pi-agent 会话 01a0e250 全量导出（585 条目 / 34 用户消息 / 242 助手消息 / 301 toolCall）+ tri-stack-train 盘面实测。
> 会话范围：tri-init → M0 骨架 → M1 会话核心 → M2 项目与记忆 → M3a 工具与技能（2026-09-27 10:02 ~ 09-28 14:26）。

## 一、结论（先说答案）

**流程形态没有走偏，缩水发生在三个质量环节**。tri-intent 快照路由、tri-coding 门①②③双审批、tasks/implements/manifest 留痕全部忠实执行了 4 个里程碑——但：

1. **tri-verify 全程缺席**（🔴 主因）：「写完了 ≠ 能用」这一环被降级成「口头指导用户手测」，V1 命中却从未激活 Playwright 本地引擎，verdict 靠用户一句「成功了」盖章。
2. **renderer/UI 层测试空转**（🔴 主因）：13 个测试文件中 12 个在 main/shared 层，组件测试与 E2E 为零。用户实际踩到的 2 个功能性 bug（重命名无效、Attach 后指示不刷新）全部落在这个盲区。
3. **tri-review 执行严重缩水**（🟠）：全 session 只 read 过 1 次 SKILL.md，`references/review-checklists.md` **零加载**；三次审查实际只跑了 3 条 grep（any/TODO/通道对齐）→ 直接写报告，Phase 1/Phase 2 checklist 与 Fowler 12 坏味全部未执行，三次都「通过（无 P1）」。

次要缺口：**零 commit 纪律**（M1/M2/M3a 三个里程碑 0 commit）、**沙箱/真机环境差异无护栏**（Electron 二进制、.env 注释自相矛盾）。

**与 tri 无关的一项**：会话尾部 6 条「继续」无响应，根因是 pi-agent 自身模型 API 403（deepseek-ai/DeepSeek-V4-Flash，8 个 error 回合，配额/凭证问题）。

## 二、bug 清单（用户实际遇到的）

| # | 现象 | 根因 | 类型 | 本应被哪一环抓住 |
|---|---|---|---|---|
| 1 | `npm run dev` 报 `Error: Electron uninstall` | agent 沙箱装依赖时设 `ELECTRON_SKIP_BINARY_DOWNLOAD=1`，用户真机 `npm install` 判定 up-to-date 不重跑 postinstall | 环境差异 | tri-coding 执行阶段环境护栏（缺失） |
| 2 | 启动即提示「需配置 PROMA_API_KEY」 | 实现只读系统环境变量，`.env.example` 注释却写「复制为 .env」，自相矛盾 | 设计/UX | 门② 设计审批 + review（未覆盖配置可用性） |
| 3 | **重命名无效** | `App.tsx` 编辑态门控 `editingTitle === s.id`，但 ✎ 存的是 `setEditingTitle(s.title)`，永不相等 | UI 状态逻辑 | 组件测试 / E2E（零覆盖）；review 静态 grep 不可见 |
| 4 | **GUI 冒烟 AGENTS 显示「—」** | `attachProject` 成功后未调 `refreshCtx`，指示 stale | UI 状态刷新 | 组件测试 / E2E（零覆盖） |
| 5 | 会话尾部「继续」无响应 | pi-agent 模型 API 403（DeepSeek-V4-Flash） | 运行环境 | 与 tri 家族无关 |

M3a 的天气测试（web_search/web_fetch 工具循环）真机通过——M3a 交付本身质量正常。

## 三、逐环节体检表

| tri 环节 | 设计意图 | 实际执行 | 判定 | 证据 |
|---|---|---|---|---|
| tri-intent | 快照路由 + LATEST 指针 | 4 次里程碑全部正确路由 I11→tri-coding，快照/LATEST 齐全 | ✅ 合格 | `.tribro/snapshots/I11_*` ×4；skill 文件 read 11 次 |
| tri-coding 门①②③ | 双审批 + tasks 蓝图 | 全部执行，用户逐门「通过」 | ✅ 合格 | tasks.md 完成状态 28/28/31 块回填 |
| tri-coding 测试先行 | UT/IT/AT 三层 | typecheck+vitest+build 每里程碑全绿（32→36→49→57） | ⚠️ **AT 层空转** | renderer 仅 1 个纯函数测试（mergeStream.test.ts）；「会话 CRUD」AT02 实际只测 service 层 `renameSession`，UI 编辑流零测试 |
| tri-coding commit 门 | （设计即无此门） | M0 后 0 commit，15 文件悬空工作区 | 🔴 **skill 缺口** | `git log` 仅 `b147d2e`（M0）；SKILL.md grep commit/git 零命中 |
| tri-verify | 驱动运行中应用（默认 Playwright/pytest 引擎） | **从未激活**；每次盖章「未执行（无头环境）」→ 降级为口头指导用户手测 → 事后回填 verdict「通过（real-device）」 | 🔴 **全程缺席** | 全 session 0 次读取 tri-verify skill 文件（仅存性探测 1 次）；verdict.md 由 agent 依据用户聊天反馈书写 |
| tri-review | Phase1 规格合规 + Phase2 质量 + checklist + Fowler 坏味 | 3 次「审查」= 各 3 条 grep（any/TODO/通道对齐）→ 写报告；checklists.md 零加载 | 🟠 **严重缩水** | tri-review SKILL.md 全 session 仅 1 次 read（10:27:10）；报告自报「Phase 1=PASS, 2×P2」却漏掉两枚 UI 状态 bug |
| tri-init | AGENTS.md + 环境探测 | 执行合格、诚实标注 planned→detected | ⚠️ AGENTS.md 无 git/commit 条款、无环境差异清单沉淀 | AGENTS.md grep「git/commit」仅 1 处（.env gitignore） |
| 风险预筛门（tri-true） | R 规则评估 | 每次「自动验证通过」 | ✅ 形式执行 | implements.md 门禁节 |

## 四、根因链

```
bug 到达用户 = UI 状态逻辑零测试（tri-coding AT 层缺口）
            × tri-verify 缺席（无人真的"打开应用点一遍"）
            × tri-review 缩水（checklist 未加载，静态 grep 抓不到交互态 bug）
            → 三个环节同时失守，GUI bug 100% 由用户冒烟兜底发现
```

每个里程碑的「验证」实际只有：typecheck（静态）+ service 层单测（agent 自己写的同源测试）+ build（编译）——**没有任何一环是「驱动运行中的应用」**。这正是 tri-verify skill 自己的定位宣言（「写完了 ≠ 能用」）要解决的问题，但它在本次全程没有被调用。

## 五、优化建议（按 fix dependency order）

### 第 1 步 · 抢救现场（tri-stack-train 项目，立即可做）
1. **立即 commit**：M1/M2/M3a 拆 3 个 commit 入库，消除 15 文件悬空态（pi-agent 403 断连随时可能再发生）。
2. **补 2 个回归测试钉死已修 bug**：rename 编辑流（`editingId`/`editValue`）、attach 后 `refreshCtx`——用 Testing Library 挂组件测试。
3. **补 Playwright Electron E2E 冒烟**（5 条路径：对话 / 重命名 / Attach+AGENTS 注入 / 记忆 / 工具调用），接 `npm run e2e`——这正是 tri-verify 默认引擎的设计能力。

### 第 2 步 · tri 家族修补（tri-stack 仓库 patch 层 op，按依赖顺序）
4. **tri-coding 加 commit 门**：tasks.md §8 全勾后 MUST `git commit`，commit hash 回填 implements.md——先于其余 op（它建立回滚基线，其余修补靠它兜底）。
5. **tri-coding AT 清单硬化**：AC 涉及 renderer 交互时 MUST 产出组件测试/E2E 任务项，**禁止用「留用户冒烟」替代自动化断言**（需同步修改 tasks 模板 §3 说明）。
6. **tri-verify 委派降级规则收紧**：V1 命中但无法真机驱动时，降级产物 MUST 是「可执行冒烟脚本或结构化手测清单」；verdict「通过（real-device）」MUST 引用用户提供的具体证据（输出粘贴/截图路径），禁止仅凭「成功了」盖章。
7. **tri-review checklist 加载硬门**：工作流集成模式落盘报告前自检「checklist 加载 = 是」，Phase 1/2 每个维度至少 1 条 file:line 证据锚或显式 skip 登记；未读取 `references/review-checklists.md` 不得出具 PASS 结论。
8. **tri-init AGENTS.md 模板补 §git 纪律 + 环境差异清单**：每里程碑 commit 规则；沙箱探测到的降级（bun 缺失、electron postinstall 跳过）随 delivery-manifest 提示用户复验。

### 第 3 步 · 运行环境
9. **pi-agent 403**：DeepSeek-V4-Flash 渠道换 key/充值或降级模型；该故障与 tri 无关，但会让「零 commit」的风险放大。

### 版本漂移脚注
pi 安装副本落后于 tri-stack 仓库当前版（pi: tri-intent 1.14.3 / tri-coding 1.8.3；repo: 1.14.4）。建议在 tri-stack 侧跑一次 `ops/version-lint.py` 之外的**安装副本对账**（或由 check_update.py 的 state 机制覆盖），避免本次修补后副本再次脱节。
