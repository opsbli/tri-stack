# tri 家族可评估性总账（SkillOpt 式训练的前置条件）

> **本文件由 `ops/eval-harness/coverage.py --emit` 生成于 2026-09-27 15:39。**
> 数值断言全部实测注入，**禁止手写**——改档位请改脚本里的 `TOP` 表再重生成。
> 口径：`A` = 有可运行门禁（可复核）；`B` = 有可复用脚本/真源但缺任务级 scorer；
> `C` = 流程/方法型、无 pass/fail，**不适用于训练循环**。
> 背景见 `researcher 结论`：SkillOpt（arXiv 2605.23904）的整套机制以**确定性验证集**为地基。

## 一、规模（实测）

- 物理 `SKILL.md` 共 **40** 份
  - 顶层：26 份
  - tri-intent 二层：5 份
  - tri-sdlc children：9 份
- 家族惯用计数 = 顶层 + children = 35
- 分档：**A 4 / B 5 / C 31**
- A 档可复核校验：✅ 全部通过

## 二、A 档 · 有可运行门禁（可直接进评估基座）

| skill | 版本 | 门禁 / 资产 | 依据 |
|---|---|---|---|
| `tri-forge` | 1.0.5 | `tri-forge/scripts/compliance_check.py` | 24 条判据 + case 电池 + mutation-gate |
| `tri-html` | 1.3.8 | `tri-html/tests/run_exec_tests.py` | 31 例可执行面病例 + validate/deliver 退出码 |
| `tri-lottie` | 1.0.6 | `tri-lottie/scripts/compliance_check.py` | T1–T10 十项合规判据 |
| `tri-verify` | 1.0.1 | `tri-verify/scripts/verify_gate.py` | 9 退出码映射 / 轮次 / 盖章 + self-test |

## 三、B 档 · 缺任务级 scorer（需先写断言）

| skill | 版本 | 门禁 / 资产 | 依据 |
|---|---|---|---|
| `tri-action` | 1.2.6 | `tri-action/scripts/hash_confirm.py` | 确认哈希可校验（缺 I14 执行结果度量） |
| `tri-checklist` | 1.1.6 | `tri-checklist/scripts/build_checklist.py` | 四维覆盖率可由 checklist 产物统计（缺 scorer） |
| `tri-code-analyzer` | 1.5.3 | `tri-code-analyzer/scripts/stack_detect.py` | 栈检测可测（缺七阶段报告质量度量） |
| `tri-evolve` | 1.1.8 | `tri-evolve/scripts/evolve_learn.py` | 归因可测（缺画像复用效果度量） |
| `tri-intent` | 1.14.3 | `ops/eval-harness/run_eval.py（rollout_file scorer）` | rollout_file scorer 已建（2026-09-27）：golden 6 case 确定性断言（§一 真源 GT）；余缺口=集成 check_downstream 安装检测与快照落盘断言 |

## 四、C 档 · 不适用于训练循环（显式排除）

| layer | 数量 | skill |
|---|---|---|
| tri-intent 二层 | 5 | asking · clarify-gate · doing · expressing · meta |
| tri-sdlc children | 9 | tri-charter · tri-cr · tri-design · tri-devenv · tri-impl · tri-ops · tri-release · tri-require · tri-test |

**判据**：这些 skill 的产物是自然语言规划/质询/路由，
没有「同输入必同输出」的裁决点 ⇒ 验证门无处落脚。
给它们硬造一个 pass/fail 只会退化成 LLM judge 绝对分
（SkillLens 实证 judge 准确率 46.4%，且跨 judge 换尺噪音 ±8）。

## 五、缺口（决定下一步优先级）

| # | 缺口 | 影响 |
|---|---|---|
| 1 | A 档 4 个中 3 个无 `--dir`（只能审自身，不能跑 fixture 变体） | 电池的 `fixture` 型 case 无法覆盖 tri-html / tri-lottie / tri-verify |
| 2 | B 档 5 个无任务级 scorer | golden 集建不起来，训练循环无 val |
| 3 | C 档 31 份无 pass/fail | 显式排除，不做无效拟合 |

