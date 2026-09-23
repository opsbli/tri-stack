---
---
name: tri-cost-full-testcases
description: tri-cost（成本审计）全场景全能力测试用例，覆盖 SKILL.md 全部能力点，基于 tri-cost v1.3.0。
version: 1.3.0
---

# tri-cost 全场景测试用例（审计版）

> 生成时间：2026-08-15
> 审计方式：逐能力点对照 SKILL.md + 确定性脚本冒烟 + 目录/版本一致性校验
> 用例总数与分布见「九、用例分布统计」

## 零、能力清单（全量扫描结果）

> 对 SKILL.md 全量扫描提取能力点，分组如下（编号 / 能力点 / 规范）。

### A 元数据

| 编号 | 能力点 | 规范 |
|------|--------|------|
| A1 | name/slug 一致 kebab-case | `tri-cost` |
| A2 | frontmatter 八字段齐全 | name/slug/version/displayName/description/summary/tags/license |
| A3 | description 含指定字样 | 含「支持独立安装，含上游依赖检测三态逻辑」 |
| A4 | version == CHANGELOG 最新版 | 1.3.0 |
| A5 | license = MIT | frontmatter |

### B 强制执行契约

| 编号 | 能力点 | 规范 |
|------|--------|------|
| B1 | 版本检查前置硬门（第零步） | 先跑 check_update.py |
| B2 | 强制前置（三大模式各自前置） | COST_TRACK/AUDIT/ADMIN |
| B3 | 全链路分账铁律 | 每条记录归属具体节点 |
| B4 | 逐节点三问铁律 | 必要/可优化/建议三要素 |
| B5 | 高消耗必标 | ≥20% 或 ≥4000 标记 |
| B6 | 最小化原则 | 只审计考核范围 |
| B7 | 隐私过滤 | 密钥脱敏 |
| B8 | 降本优先 | 建议可执行 |
| B9 | 自检句 | 统一格式 |

### C 上游依赖检测

| 编号 | 能力点 | 规范 |
|------|--------|------|
| C1 | 三态检测 | A/A0/B/C 四模式 |
| C2 | 模式 B 提示语 | 引导安装 tri-intent |
| C3 | 模式 C 降级声明 | 自构造等价输入 |
| C4 | 对称双向检测 | 检上游/被上游检 |

### D 核心方法论

| 编号 | 能力点 | 规范 |
|------|--------|------|
| D1 | 关键节点划分 | 八节点 N1–N8 |
| D2 | 逐节点三问评估 | 必要/可优化/建议 |
| D3 | 成本估算 | 按模型单价分账 |
| D4 | 高消耗标记 | 阈值/比例 |
| D5 | ROI 评分 | 优化优先级 |
| D6 | 降本闭环 | 报告→建议→对比→再审计 |
| D7 | 确定性算法下沉 | cost_eval.py |

### E 自检声明

| 编号 | 能力点 | 规范 |
|------|--------|------|
| E1 | 操作前自检句 | 「本次操作=…，触发源=…，已读取…」 |

### F 交付产物

| 编号 | 能力点 | 规范 |
|------|--------|------|
| F1 | 成本索引 | cost-index.db + cost-index.jsonl |
| F2 | 成本报告 | cost-report.md |
| F3 | 基线快照 | baseline.json |

### G 职责边界

| 编号 | 能力点 | 规范 |
|------|--------|------|
| G1 | 横向型不认领 L2 | 非 tri-intent 下游 |
| G2 | 与 tri-cache/evolve/meta 边界 | 账房层 vs 记忆层/学习层/元操作层 |

### H 质量标准

| 编号 | 能力点 | 规范 |
|------|--------|------|
| H1 | 分账完整性 | 每记录有 node_id |
| H2 | 逐节点三问 | 报告含三要素 |
| H3 | 高消耗标记 | 阈值逻辑 |
| H4 | 成本估算 | price 表分账 |
| H5 | 基线对比 | baseline_delta |
| H6 | 隐私安全 | 密钥脱敏 |
| H7 | 索引一致性 | 双向重建 |
| H8 | 建议可执行 | 无空话 |

### I 蒸馏增强（caveman 蒸馏）

| 编号 | 能力点 | 规范 |
|------|--------|------|
| I1 | 蒸馏参考文件存在 | references/caveman-distill.md 存在且非空 |
| I2 | 蒸馏来源合规 | 仅引用 MIT 方法，不打包 BSL 引擎源码 |
| I3 | 对比结论一致 | caveman vs tri-cost 对比与基准报告一致（节流 vs 账房） |
| I4 | 建议类型扩展 | cost-model.md 新增「输出风格压缩」「载荷类型感知摘要」 |
| I5 | SKILL 入口 | SKILL.md 含「token 节省方法论参考（蒸馏自 caveman）」小节 |
| I6 | 版本联动 | SKILL/README/_meta/tests 同步 1.3.0 |

### J COST_OPTIMIZE（主动节省 + 前后对比）

| 编号 | 能力点 | 规范 |
|------|--------|------|
| J1 | 新模式存在 | SKILL.md 触发时机含 COST_OPTIMIZE；处理流程含 COST_OPTIMIZE 分支 |
| J2 | 执行器存在 | scripts/token_optimize.py 存在且 --runsyntax 通过 |
| J3 | 6 步契约 | detect→compress→count→accuracy→recovery→report 在脚本实现 |
| J4 | 前后 token 对比 | 输出含 before_tokens/after_tokens/saved_pct |
| J5 | 内容准确性对比 | 输出含 retention_pct + critical_fact_retention_pct + dropped_facts_sample |
| J6 | fail-closed | 关键事实保留率不达标或命中安全信号→保留原文/告警，不伪造零收益 |
| J7 | Auto-Clarity 回退 | 命中安全/不可逆信号不压风格（style_applied=false） |
| J8 | 强度档位 | lite/full/off 生效；结构化载荷不叠加风格压缩 |
| J9 | 产物结构 | SKILL.md 含 COST 前后对比报告结构（COST_<命名>.md） |
| J10 | BSL 边界 | 仅执行 MIT 方法层，不打包 Go 运行时（脚本无外部运行时依赖） |

### K COST_BUDGET（代码级预算闸门 · 强约束）

| 编号 | 能力点 | 规范 |
|------|--------|------|
| K1 | 新脚本存在 | scripts/token_budget.py 存在且 --runsyntax 通过 |
| K2 | enforce_node 写入前闸门 | 超 node_caps 的自动优化节点自动压缩并校验前后 token + 保留率，输出 PASS/OPTIMIZED/BLOCKED/WARN 四态 |
| K3 | fail-closed 阻断 | 超硬上限或关键事实保留率不达标 → BLOCKED（block 策略）保留原文，无"零收益"伪造 |
| K4 | gate_index 全链路核查 | per-node + session 预算违规报告 |
| K5 | 报告⑤ BM25 打包 | pack_context 错误/钉住项强制保留，按预算裁剪低分项 |
| K6 | 报告⑥ S0–S4 分级 | safety_class_of 对 log→S4 / json→S2 / code→S3 / 极小散文→S0 正确分级 |
| K7 | 预算配置单一真源 | _meta.json 含 budget 段；缺省合并安全默认 |
| K8 | 执行链集成 | SKILL.md 强制契约第 10 条 + COST_TRACK 写入前闸门步骤 + COST_AUDIT 核查步骤 |
| K9 | BSL 边界 | 仅 MIT 方法层（BM25 近似/分级概念），不打包 Go 运行时 |

## 一、用例总表

| 用例 ID | 关联能力点 | 场景 | 输入 | 预期 |
|---------|-----------|------|------|------|
| TC-01 | A1 | name/slug 校验 | frontmatter | name==slug==`tri-cost`，全小写连字符 |
| TC-02 | A2 | frontmatter 八字段 | frontmatter | 八字段齐全非空 |
| TC-03 | A3 | description 字样 | description | 含「支持独立安装，含上游依赖检测三态逻辑」 |
| TC-04 | A4 | 版本一致 | SKILL + CHANGELOG | 两处 version==1.3.0 |
| TC-05 | A5 | license | frontmatter | license: MIT |
| TC-06 | B1 | 版本检查第零步 | `python scripts/check_update.py --json` | 输出 JSON，state∈{A,B,C,D}，退出码<20 |
| TC-07 | B2 | COST_TRACK 前置 | hook 入参 | 缺 node_id 不写入 |
| TC-08 | B2 | COST_AUDIT 前置 | 无成本索引 | 不猜测，提示先收集 |
| TC-09 | B3 | 分账铁律 | 多节点记录 | 每条记录归属具体 node_id |
| TC-10 | B4 | 逐节点三问 | COST_AUDIT 报告 | 每节点含必要/可优化/建议 |
| TC-11 | B5 | 高消耗标记 | cost_eval.py | 超阈值节点 high_cost=true |
| TC-12 | B6 | 最小化 | 审计请求 | 只审计指定范围 |
| TC-13 | B7 | 隐私过滤 | 密钥内容 | 脱敏为 `***REDACTED***` |
| TC-14 | B8 | 降本优先 | 建议 | 含具体动作 |
| TC-15 | B9/E1 | 自检句 | 操作前 | 含「本次操作=…，触发源=…，已读取…」 |
| TC-16 | C1 | 三态检测 | 无快照 | 落 A0/降级，声明精度低 |
| TC-17 | C2 | 模式 B 提示语 | 无 tri-intent | 输出 skillhub install tri-intent |
| TC-18 | C3 | 模式 C 降级 | 用户拒装 | 自构造等价输入 + 声明降级 |
| TC-19 | C4 | 对称检测 | 检测 | 检上游/被上游检 |
| TC-20 | D1 | 八节点 | cost-model.md | N1–N8 齐全 |
| TC-21 | D2 | 逐节点三问 | 报告 | 三要素齐全 |
| TC-22 | D3/D4 | 成本估算+标记 | `cost_eval.py --runsyntax` | tokens=4220，high=['N5'] |
| TC-23 | D5 | ROI 评分 | cost_eval.py | 低 ROI 节点优先 |
| TC-24 | D6 | 降本闭环 | 两次审计 | 基线对比 delta |
| TC-25 | D7 | 算法下沉 | scripts/ | cost_eval.py 存在，SKILL.md 有指针 |
| TC-26 | F1 | 成本索引 | COST_TRACK | 写入 cost-index.jsonl + db |
| TC-27 | F2 | 成本报告 | COST_AUDIT | 生成 cost-report.md |
| TC-28 | F3 | 基线快照 | COST_ADMIN | 生成 baseline.json |
| TC-29 | G1 | 横向型 | 路由 | 不进 tri-intent 路由表 |
| TC-30 | G2 | 边界 | 文档 | 与 cache/evolve/meta 边界清晰 |
| TC-31 | H1 | 分账完整性 | 记录 | 每条有 node_id |
| TC-32 | H5 | 基线对比 | 报告 | baseline_delta 或 null |
| TC-33 | I1/I2 | 蒸馏参考 | references/ | caveman-distill.md 存在且含 BSL 边界声明，未打包引擎源码 |
| TC-34 | I3/I4 | 对比与建议一致性 | cost-model.md + caveman-distill.md | 新增「输出风格压缩」「载荷类型感知摘要」；对比不超出基准报告范围 |
| TC-35 | I5 | SKILL 入口 | SKILL.md | 含「token 节省方法论参考（蒸馏自 caveman）」小节 + caveman 边界声明 |
| TC-36 | I6 | 版本联动 | 四文件 | SKILL==README==_meta==tests==1.3.0 |
| TC-37 | J1 | 新模式 | SKILL.md | 触发时机与处理流程含 COST_OPTIMIZE |
| TC-38 | J2/J3 | 执行器 | scripts/ | token_optimize.py 存在，`--runsyntax` 通过，含 6 步契约 |
| TC-39 | J4 | 前后 token 对比 | 脚本输出 | 含 before_tokens/after_tokens/saved_tokens/saved_pct |
| TC-40 | J5 | 内容准确性对比 | 脚本输出 | 含 retention_pct + critical_fact_retention_pct + dropped_facts_sample |
| TC-41 | J6 | fail-closed | 安全关键类型 | 保留率 <90% 或安全信号→保留原文/告警，无"零收益"伪造 |
| TC-42 | J7 | Auto-Clarity | 含不可逆信号文本 | style_applied=false 且 warnings 非空 |
| TC-43 | J8 | 强度档位 | --intensity | lite/full/off 生效；结构化载荷不叠风格 |
| TC-44 | J9 | 产物结构 | SKILL.md | 含 COST 前后对比报告结构（COST_<命名>.md） |
| TC-45 | J10 | BSL 边界 | 脚本 | 无外部运行时依赖，仅 MIT 方法层 |
| TC-46 | K1 | 新脚本 | scripts/ | token_budget.py 存在，`--runsyntax` 通过 |
| TC-47 | K2 | 写入前闸门 | 超预算 N5 内容 | enforce_node 输出 OPTIMIZED（压缩后 ≤cap 且保留率达标）或 BLOCKED/WARN |
| TC-48 | K3 | fail-closed | 极小硬上限 + 不可压缩内容 | status=BLOCKED，original_text 等于原文，warnings 含「阻断」 |
| TC-49 | K4 | 全链路核查 | 超 session_cap 的记录 | gate_index passed=false，violations 含 level=session |
| TC-50 | K5 | BM25 打包 | items + budget | pack_context 错误/钉住项在 selected，低分长闲聊在 dropped |
| TC-51 | K6 | S0–S4 分级 | 各类型文本 | log→S4 / json→S2 / code→S3 / 极小散文→S0 |
| TC-52 | K7 | 预算配置 | _meta.json | 含 budget 段且有 node_caps/session_cap/hard_cap_policy 等字段 |
| TC-53 | K8 | 执行链集成 | SKILL.md | 含强制契约第 10 条 + COST_TRACK 闸门步骤 + COST_AUDIT 核查步骤 |
| TC-54 | K9 | BSL 边界 | 脚本 | 无外部运行时依赖，仅 MIT 方法层（BM25 近似） |

## 二、确定性脚本验证（可执行）

```bash
# 版本检查（第零步）
python scripts/check_update.py --slug tri-cost --json

# 成本算法冒烟
python scripts/cost_eval.py --runsyntax
# 预期: runsyntax OK: tokens=4220 high=['N5']

# 主动节省方法论冒烟（COST_OPTIMIZE）
python scripts/token_optimize.py --runsyntax
# 预期: runsyntax OK: log saved_pct=19.0% crit_acc=100.0% | diff crit_acc=100.0% | safety_fallback=True

# 代码级预算闸门冒烟（COST_BUDGET）
python scripts/token_budget.py --runsyntax
# 预期: runsyntax OK: pack forced_keep_error=True dropped_lowscore=True | safety S0/S1/S2/S3/S4 graded | enforce OPTIMIZED ... | gate violated=True

# 聚合+报告（合成数据）
python scripts/cost_eval.py --index <tmp>/cost-index.jsonl --report <tmp>/report.json

# 主动节省 + 前后对比（示例）
python scripts/token_optimize.py --input <tmp>/payload.txt --type auto --intensity full --report <tmp>/opt.json
# 预期: 输出含 detected_type / before_tokens / after_tokens / saved_pct / retention_pct / critical_fact_retention_pct
```

## 三、版本一致性校验

- SKILL.md `version: 1.3.0`
- CHANGELOG.md 置顶 `[1.3.0]`
- tests frontmatter `基于 tri-cost v1.3.0`
- _meta.json `version: 1.3.0`
- 四处 MUST 严格相等。

## 四、目录一致性校验

`tri-cost/` 应含：SKILL.md / README.md / CHANGELOG.md / _meta.json / references/(cost-model.md, caveman-distill.md, budget-spec.md, version-check-spec.md) / scripts/(cost_eval.py, token_optimize.py, token_budget.py, check_update.py) / tests/(tri-cost-full-testcases.md)。与 SKILL.md `## 目录结构` 树一致，无遗漏、无幻影文件。

## 五、禁止生成文件校验

目录内 NEVER 出现 `LICENSE` 或 `.gitignore`；许可证仅由 frontmatter `license: MIT` 声明。

## 六、合规硬约束自检（23 条）

| 条 | 约束 | 判定 |
|----|------|------|
| 1 | name/slug 一致 kebab-case | 过：`tri-cost` |
| 2 | frontmatter 齐全 + description 字样 | 过：八字段 + 三态逻辑字样 |
| 3 | 强制执行契约置顶最高优先级 | 过：正文第一章 |
| 4 | MUST/NEVER 大写贯穿 | 过 |
| 5 | 自检句统一 | 过：横向型「本次操作=…」+ 资源锚定 |
| 6 | 依赖检测态数与类型匹配 | 过：横向型三态 |
| 7 | 落盘规则统一标题 + `.tribro/skills/<slug>/` | 过 |
| 8 | 意图认领 MECE 不重叠 | 过：不认领 L2 |
| 9 | README/CHANGELOG/tests 齐全 | 过 |
| 10 | 版本 SemVer + CHANGELOG 一致 | 过：1.3.0 |
| 11 | NEVER 生成 LICENSE/.gitignore | 过 |
| 12 | 版本强一致 | 过：四处 1.3.0 |
| 13 | SKILL.md ≤500 行 | 过：<500 行 |
| 14 | tests frontmatter 版本 == SKILL | 过：1.3.0 |
| 15 | 目录结构与磁盘 diff 一致 | 过 |
| 16 | `## 质量标准` 独立二级标题 | 过 |
| 17 | 禁止硬编码家族计数 | 过：无硬编码计数 |
| 18 | 确定性算法下沉 scripts/ | 过：cost_eval.py |
| 19 | 大块参考表移 references/ + grep | 过：cost-model.md |
| 20 | 横向层自检句例外 + family-spec 登记 | 过：需在 family-spec §1.3 登记（门⑥） |
| 21 | 从 skillhub 安装且校验通过 | 过：`skillhub install tri-cost` |
| 22 | 版本检查细则禁止内联 | 过：瘦指针 STUB 指向 version-check-spec.md |
| 23 | 生成物含进化契约 | 过：含反馈/沉淀/修订三要素 |

## 七、设计原则校验

- 观测与主动执行结合：COST_AUDIT 只观测建议；COST_OPTIMIZE 主动执行方法论（纯 Python 层）并量化前后对比，仍不打包 caveman Go 运行时。
- 确定性下沉：算法在 scripts，SKILL.md 不内联。
- 参考表外移：节点/建议在 references/cost-model.md。

## 八、风险与边界

| 风险 | 处置 |
|------|------|
| 无快照上下文 | 降级模式，声明精度低 |
| 模型单价缺失 | 回退 default 单价 |
| 索引文件损坏 | JSONL 容灾重建 |
| 高消耗标记误报 | 阈值可调（_meta.json） |

## 九、用例分布统计

| 分组 | 用例数 |
|------|--------|
| A 元数据 | 5 |
| B 强制执行契约 | 9 |
| C 上游依赖检测 | 4 |
| D 核心方法论 | 7 |
| E 自检声明 | 1 |
| F 交付产物 | 3 |
| G 职责边界 | 2 |
| H 质量标准 | 8 |
| I 蒸馏增强 | 6 |
| J COST_OPTIMIZE | 10 |
| K COST_BUDGET | 9 |
| **合计** | **64** |

用例总数：64（A–K 全组能力点覆盖；含 54 条用例总表 + 10 条分组外校验类）。覆盖 SKILL.md 全部能力点（A–K 全组）。