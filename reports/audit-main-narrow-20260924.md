# 审计报告：main 收窄为「编程工作流专线」收尾校验

- 日期：2026-09-24
- 基线：`main @ ee4c694`（与 `origin/main` 同步，工作区干净）
- 范围：24 个非编程 skill 移除后的残留引用、版本一致性、仓库级文档口径
- 结论：**校准完成，0 blocker 遗留**；本轮修复 4 个文件，待放行后提交

---

## 一、生产现状

| 项 | 实测 | 判定 |
|---|---|---|
| 分支 | `main` @ ee4c694，`origin/main` 同 commit | 🟢 已推送 |
| 收窄动作提交 | 9293321（移除 24 skill）→ 199fcc4（路由收窄 + 16 skill 升版）→ ee4c694（README/手册改版） | 🟢 |
| 磁盘残留 | 24 个已删目录在工作树命中 **0** | 🟢 |
| 版本一致性 | `ops/version-lint.py`：22 个 skill，漂移 **0** | 🟢 22/22 ✅ |
| ops 三件套 | `versions.json` skills=22 / `patches/manifest.json` ops=13 / `skills-install.py` 已删 slug 命中 **0** | 🟢 |
| 回滚兜底 | 归档分支 `archive-full-skills-20260924` 含全量 47 目录 | 🟢 可回溯 |
| tri-intent 路由 | 已裁为编程专线，description 带分支声明，版本 1.14.0（P1/P2/P3 一致） | 🟢 |

---

## 二、问题（本轮发现，均已修复）

| ID | 严重度 | 位置 | 问题 | 状态 |
|---|---|---|---|---|
| P0-1 | 🔴 | `WORKFLOW-GUIDE.html` 分层图 | **17 处**版本 chip 未跟随 199fcc4 升版（tri-intent 1.13.1 vs 实 1.14.0、tri-coding 1.7.0 vs 1.7.1、tri-html 1.3.0 vs 1.3.2 等） | ✅ 已同步 |
| P0-2 | 🔴 | `README.md` 技能目录表 | **16 行**版本未同步，与 P0-1 同源 | ✅ 已同步 |
| P0-3 | 🔴 | `WORKFLOW-GUIDE.html` 页脚 | 契约基线 7 项全为旧号 | ✅ 已同步 |
| P1-1 | 🟠 | `WORKFLOW-GUIDE.html` L108 | chip 仍写「版本一致性 **46/46**」 | ✅ → 22/22 |
| P1-2 | 🟠 | `WORKFLOW-GUIDE.html` §09/§07/最短路径 | 6 处仍按 46-skill 世界描述，未标「本分支未包含」（tri-cache / tri-evolve / tri-guard / tri-true / tri-geo / tri-mm / tri-article 等） | ✅ 已加注 + 删除线 |
| P1-3 | 🟠 | `tri-intent/tests/tri-intent-full-testcases.md` | frontmatter `version: 1.14.0` 已升，但正文 L9/L15 仍写 v1.13.1 | ✅ 已同步 |
| P2-1 | 🟡 | 根 `CHANGELOG.md` | 1.0.0 历史清单含 11 个已移出 skill，无任何分支说明 | ✅ 加分支说明注（历史不改） |
| P2-2 | 🟡 | `ops/README.md` L159、`ops/patches/README.md`、`ops/version-lint.py` 注释 | 已删 skill 仅出现在历史记录与举例中 | 🟢 保留（属历史/说明，改写反而失真） |

**根因**：199fcc4 一次性升版 17 个 skill 时，同步只覆盖 skill 包内的 P1/P2/P3，**未覆盖仓库级文档**（手册 + README + 页脚）。这不是遗漏若干处，而是漏了一整层同步点。

**已正确处理、无需再动的残留**：分发树内 313 行命中里，绝大多数已带「本分支未包含（原 X）」注解——包括各 skill 的 SKILL.md 负向路由表、测试用例、`tri-forge/scripts/compliance_check.py` 的历史实测注释。这是上一轮刻意保留的正确模式。

---

## 三、优化方向（未做，待裁定）

| 优先级 | 事项 | 说明 |
|---|---|---|
| 1 | 根 `CHANGELOG.md` 补 `[2026-09-24]` 正式条目 | 目前只加了分支说明注，没有版本条目；是否补取决于 releases 流程 |
| 2 | `.workbuddy/_upstream/` 仍含 24 个已删 skill 的上游镜像 | 占 46 文件命中中的大部分；属内部工作区，是否清理/归档需你定 |
| 3 | 手册补「从归档分支取回单个 skill」操作卡 | 用户问「我要 tri-pm」时目前无标准动作 |
| 4 | `tri-forge` 合规检查器内已删 skill 的实测注释 | 建议保留——它们是检查器容错规则的设计依据，删了会丢失「为什么这么判」 |

---

## 四、评分

| 维度 | 得分 | 说明 |
|---|---|---|
| 删除彻底性 | 9.5 / 10 | 磁盘 0 残留、ops 三件套 0 残留 |
| 引用清理 | 9.0 / 10 | skill 包内 100% 加注；仅仓库级文档漏 |
| 版本一致性 | 10 / 10（修复后） | 修复前 6.0：17+16+7 处漂移 |
| 文档口径 | 9.5 / 10（修复后） | 修复前 5.0：46/46 chip + 6 处 46-skill 世界描述 |
| 可回溯性 | 10 / 10 | 归档分支 + 全量 47 目录 |

---

## 五、测试

| 校验 | 命令 | 结果 |
|---|---|---|
| 版本漂移 | `python ops/version-lint.py` | 检查 22 个 skill，漂移 **0**；✅ 计数 22 |
| 磁盘残留 | 遍历 24 个已删 dir | 不存在 **0** 项 |
| 残留引用 | 分发树全量扫描（排除 `.workbuddy`/`reports`） | 46 文件 / 324 行，均已加注或属历史 |
| ops 三件套 | 已删 slug 命中计数 | `versions.json` 0 / `skills-install.py` 0 / `manifest.json` 0 |
| 手册 vs 实测版本 | 正则比对 22 处 chip + 22 行 README | 漂移 **0 / 0** |
| HTML 结构 | 标签闭合计数 | `div` 68/68、`li` 24/24、`s` 2/2，全闭合无错配 |

---

## 六、审计结论与放行项

**结论**：main 收窄动作本体已完成且正确；本轮补齐的是「仓库级文档同步层」这一遗漏维度。当前 0 blocker。

**待放行（不可逆 / 外部动作）**：
1. 提交 4 个改动文件：`CHANGELOG.md`、`README.md`、`WORKFLOW-GUIDE.html`、`tri-intent/tests/tri-intent-full-testcases.md`
2. 推送至 `origin/main`

**fix dependency order（本轮已按此执行）**：先同步版本号（P0）→ 再改口径 chip（P1-1）→ 再加本分支未包含标注（P1-2）→ 最后补历史注记（P2）。顺序不可反：口径 chip 依赖版本已对齐，否则标注与数字仍会打架。
