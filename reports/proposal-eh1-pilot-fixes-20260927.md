# proposal · eh1 批：eval-harness pilot 三处修复（tri-html S4.x + tri-lottie T3/T5）

> **提案日期**：2026-09-27 ｜ **状态**：Approved: **yes**（2026-09-27 AskUserQuestion 放行，全流程执行）
> **来源**：eval-harness pilot 基线（run-id `pilot-gate-20260927`，7 执行 5 过）+ 一手归因实测
> **前置核实**：manifest 当前待写 0（他 session 在途冲突已解除），重放环境安全
> **执行更正**：实际入库 **7 op**（4 lottie + 3 html，正文误写 6）；另按家族惯例（f16 先例）将既有 settle `f85-ver-lottie` / `f93-ver-html` 目标**就地更新**至 1.0.6 / 1.3.8，并**撤回**本批初稿的两条链式 settle（`eh1-lottie-version` / `eh1-html-version`）——run2 曾因此出现 4 op 永动（f86/f97 同款），纠偏后 run3/run4 均「应用 0」。op 总数 331 → **336**（README ×2 已同批回写）。

## 一、归因结论（全部一手实测）

| 信号 | 归因 | 证据 |
|---|---|---|
| tri-html S4.1/S4.2/S4.4 恒 exit 0/state A | **测试期望过期**，非产品缺陷 | `check_update.py:728-732`：`SELF_MAINTAINED` 分支在 `args.simulate_net`（:756）被消费前提前 return。fork 脱离上游转自维护后，`--simulate-net/--simulate-fetch-ok` 永远走不到 fetch 层。带 `TRI_ALLOW_REMOTE=1` 复跑四探针：offline→B/10、html→C/11、9.9.9→D/12、1.2.2→A/0，**全部可达** ✅ |
| tri-lottie T3 tests=1.0.2 滞后 | 真缺陷（版本声明漏同步） | `tests/tri-lottie-full-testcases.md:4` = `基于 tri-lottie v1.0.2`，SKILL/CHANGELOG/_meta 均 1.0.5 |
| tri-lottie T5 missing=version-check-spec.md | 真缺陷（声明树漏列） | 文件**实际存在**于 `references/`；`compliance_check.py:145` missing = 磁盘−声明树，SKILL.md §目录结构 references/ 块只列 5 个文件 |

## 二、修复方案（6 op，前缀 `eh1-`，插入 index 273（首个 sync op）之前）

### tri-lottie（1.0.5 → 1.0.6，patch bump：缺陷修复）

| op | type | 目标 | 动作 |
|---|---|---|---|
| eh1-lottie-version | replace_regex（settle） | SKILL.md | `version: 1.0.5 → 1.0.6`（P1） |
| eh1-lottie-tests-t3 | replace_text | tests/…-testcases.md | `基于 tri-lottie v1.0.2 → v1.0.6`（T3 根因） |
| eh1-lottie-tree-t5 | replace_text | SKILL.md | 目录树 references/ 补列 `version-check-spec.md`（T5 根因；recipe-patterns 行 └→├） |
| eh1-lottie-changelog | replace_text | CHANGELOG.md | 前插 `## [1.0.6] - 2026-09-27` 条目（P2 人工内容） |

### tri-html（1.3.7 → 1.3.8，patch bump：测试修复）

| op | type | 目标 | 动作 |
|---|---|---|---|
| eh1-html-version | replace_regex（settle） | SKILL.md | `version: 1.3.7 → 1.3.8`（P1） |
| eh1-html-gate-env | replace_text | tests/run_exec_tests.py | `gate()` 注入 `TRI_ALLOW_REMOTE=1` env，使 S4.1–S4.5 走远端路径恢复 B/C/D 态覆盖 |
| eh1-html-changelog | replace_text | CHANGELOG.md | 前插 `## [1.3.8] - 2026-09-27` 条目 |

P3/P5（_meta.json / README 版本声明）由既有全局规则化 `sync-version-meta` / `sync-readme-version` 同轮跟随，**不新增 op**。

## 三、验收门（apply 后全跑）

1. 回执判据：连跑两次 `apply.py`，第二次「写入 0」；首轮逐 op「应用 1」核对（6/6）。
2. `ops/version-lint.py` 退出码 0。
3. `tri-lottie/scripts/compliance_check.py` T1–T10 全 PASS（10/10）。
4. `tri-html/tests/run_exec_tests.py` 31 例全 PASS。
5. `run_eval.py --split val` 复测：tri-lottie-envelope-01、tri-html-envelope-01 转 pass（台账 7/7）。

## 四、风险

- **低**：全部 replace 类 op 带 already_marker，幂等可重放；不触碰他 session 在途文件（tri-forge battery / 两份 proposal 仍保持未提交，不纳入本批 commit）。
- gate_env 改动使 S4 测试依赖 `~/.skillhub/metadata.json` 存在（端点解析）——已实测本机可达；若未来该文件缺失，S4 全组将转 C 态报错（fail-visible，非静默）。

## 五、回滚

op 均带 marker 可原地反向（版本 settle 目标就地改回）；或 git revert 本批 commit（skill 文件改动与 manifest 同 commit）。
