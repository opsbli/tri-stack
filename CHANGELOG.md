# 变更日志

> **分支说明（2026-09-24）**：本分支 `main` 已收窄为**编程工作流专线，22 个 skill**。
> 下方 1.0.0 的 Skill 清单是 2026-08-03 初始发布时的快照，属追加型历史、不予改写；
> 其中 `tri-content` / `tri-article` / `tri-translate` / `tri-ask` / `tri-bs` / `tri-express` /
> `tri-cache` / `tri-evolve` / `tri-mm` / `tri-music` / `tri-true` 等 24 个非编程 skill 已移出本分支，
> 全量 46 个保存在归档分支 `archive-full-skills-20260924`。

## [未发布] - 2026-09-27

### 新增

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