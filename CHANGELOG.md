# 变更日志

> **分支说明（2026-09-24）**：本分支 `main` 已收窄为**编程工作流专线，22 个 skill**。
> 下方 1.0.0 的 Skill 清单是 2026-08-03 初始发布时的快照，属追加型历史、不予改写；
> 其中 `tri-content` / `tri-article` / `tri-translate` / `tri-ask` / `tri-bs` / `tri-express` /
> `tri-cache` / `tri-evolve` / `tri-mm` / `tri-music` / `tri-true` 等 24 个非编程 skill 已移出本分支，
> 全量 46 个保存在归档分支 `archive-full-skills-20260924`。

## [未发布] - 2026-09-28

### 新增

- **家族横切第 10 节「宿主兼容与提问呈现」（35 个 skill 全量 PATCH 升版）**：
  在「版本检查与更新机制」节后统一追加 `host-compat-stub v1` 自包含瘦节——在提供交互式提问工具的宿主
  （如 Proma 的 `AskUserQuestion`）中，🔴 STOP 用户确认检查点与 clarify-gate MUST 以普通 Markdown 文本
  呈现为聊天问题，**NEVER 调用交互式提问工具**（`AskUserQuestion` / `ask_user_question` /
  `request_user_input` / `clarify` 及等价物）。触发背景：本分支 35 个 skill 对交互式提问工具**零引用**
  （宿主中立、跨宿主可移植），但家族内 94 处 🔴 STOP 硬门 + 55 处「是否…（是 / 否）」句式，
  在 Proma 等工具型宿主下会被运行时**自动升级**为问答横幅；且 clarify-gate 的
  「逐条补充 / 按默认 / 继续」自由文本契约在选项卡下会失真（「按默认」出口静默丢失）。
  **只管呈现形式，不改任何门控的判定条件、触发时机与处置动作**；无交互式提问工具的宿主中本条自然空转。
  细则真源新增 `tri-intent/references/host-compat.md`（成因 + 家族约定 + 契约失真对照表 + 六条边界与例外
  + 瘦节模板）；家族规范登记于 `tri-forge/references/family-spec.md` §四（第 10 节注）+ §五（待登记项，
  含「不参与九章章序、无需改 `compliance_check.py` 脚本」说明）。
  升版：26 个顶层 skill + 9 个 `tri-sdlc/children/*` 子 skill 各 PATCH +1；五处版本声明
  （frontmatter / 各 skill `CHANGELOG.md` / `_meta.json` / `ops/versions.json` / 文档层 D1–D4）全部同步，
  `ops/version-lint.py` P1–P5 与文档层均 **0 漂移**；`tri-forge/scripts/compliance_check.py --all`
  26/26 **零 FAIL**。
- **`ops/eval-harness/`**：SkillOpt 式训练循环基座（arXiv 2605.23904 工程落地）——
  `gate_adapter.py`（异构 skill 门禁归一，9 注册含 `eval-val` 验证集门禁类型与 `--clean`
  HEAD-worktree 模式）、`coverage.py/.md`（40 份 SKILL.md 可评估性总账 A9/B0/C31，脚本生成禁手写）、
  `golden/` + `split.json` + `run_eval.py`（25 case 任务级验证集，train/val/test 三分，
  三类确定性 scorer：command / gate_envelope / rollout_file，零 LLM judge）、
  `trace_store.py`（per-case trace 落盘 + 路径回传）、`optimizer-contract.md`
  （独立优化器契约：同源禁令 + 8 黑名单）、`fixtures/`（%TEMP% 隔离行为探针）、
  `op-candidates/`（optimizer 产物缓冲）
- **训练循环首跑 iter1**：val 基线 → 独立优化器（reasoning 冷启动）→ no-op candidate →
  paired 3-judge 盲评 3/3 keep；报告 `reports/iter1-train-loop-20260927.md`
- 用户级 skill **`eval-loop`**（训练循环工作流沉淀）

### 修复

- **tri-lottie 1.0.5 → 1.0.6**：T3 版本四件套对齐（tests 头部 v1.0.2 滞后）+ T5 目录树补列
  `references/version-check-spec.md`；compliance 复测 10/10
- **tri-html 1.3.7 → 1.3.8**：S4 版本门测试期望过期修复（fork 转自维护后 simulate 参数
  走不到 fetch 层；`gate()` 注入 `TRI_ALLOW_REMOTE=1` 恢复 B/C/D 态覆盖）；exec tests 复测 31/31
- **补丁层**：`apply.py` 新增 `drop_block` op（begin/end 锚点整块删除，两态/三态 witness）
  + 9 例 tempfile 隔离测试；f85/f93 settle 目标就地更新（消除链式 settle 永动）；op 总数 331 → 336

## [1.0.0] - 2026-08-03

### 新增

- 项目初始化，发布 24 个 tri-xxx skill
- 完整的 skill 目录结构、README、贡献指南、行为准则、安全策略
- GitHub Issue/PR 模板

### Skill 清单

- **核心**: tri-intent
- **编码**: tri-coding, tri-review, tri-fix, tri-plan
- **内容**: tri-content, tri-article, tri-translate, tri-html
- **交互**: tri-ask, tri-bs, tri-express
- **流程**: tri-loop, tri-workflow, tri-sdlc, tri-action
- **工具**: tri-checklist, tri-cache, tri-evolve, tri-god, tri-meta, tri-mm, tri-music, tri-true

各 skill 的详细变更记录见各自目录下的 `CHANGELOG.md`。