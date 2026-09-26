# External Gate 豁免登记表

> external_skill_gate.py 的 MANUAL 命中经语境核验后在此登记方可降级为 PASS。
> **NEVER 静默豁免**；每条 = skill / 判据 / 命中路径（条目级豁免）/ 语境理由 / 日期。
> `X1`（密钥字面量）**不可豁免**（工具强制，登记无效）。
> 未登记的 MANUAL 项保持 🟡 待人工核验；新增命中须重新核验（跨轮单调性：只增不减，NEVER 因催促降级）。

| skill | 判据 | 路径 | 语境理由 | 日期 |
|---|---|---|---|---|
| `skill-auditor` | `X2` | | SKILL.md:72,75 为「安全扫描解读」教学文本（描述他人脚本危险模式清单），非实际执行 | 2026-09-26 |
| `skill-auditor` | `X3` | | 同上，`rm -rf` 出现在扫描判据说明行 | 2026-09-26 |
| `install-github-skill` | `X3` | | SKILL.md:148 为 grep 审计命令文本（教学） | 2026-09-26 |
| `install-github-skill` | `X4` | | SKILL.md:59–67 curl 下载为本 skill 声明性本职（GitHub skill 安装器），目标限于用户指定 skill 目录 | 2026-09-26 |
| `skills-security-check` | `X2` | | 安全扫描 skill 的判据教学文本（SKILL.md:97） | 2026-09-26 |
| `skills-security-check` | `X3` | | 同上（SKILL.md:132,151 为扫描模式说明） | 2026-09-26 |
| `skills-security-check` | `X4` | | 同上（SKILL.md:71–73 安装/扫描指引文本） | 2026-09-26 |
| `skill-vetter` | `X2` | | vetting 判据教学文本（SKILL.md:49） | 2026-09-26 |
| `skill-vetter` | `X4` | | SKILL.md:43,117,120 安装指引（声明性） | 2026-09-26 |
| `skill-ce-shi__skillhub` | `X2` | | references/dynamic-testing-guide.md 动态测试教学文本 | 2026-09-26 |
| `archify` | `X5` | | vendored viewer 引擎代码内 URL（示例数据/license 链接 197 处）；vendored 组件不逐版本审计，演进登记由 engine-evolution-notes 思路管理 | 2026-09-26 |
| `agent-code-crew` | `X4` | | references 文档中的安装/验证示例命令 | 2026-09-26 |
| `make-skill` | `X4` | | references/convertible-patterns.md 模板示例命令 | 2026-09-26 |
| `qa-agent-testing__skillhub` | `X4` | | SKILL.md:8,53 安装指引（声明性） | 2026-09-26 |
| `darwin-skill` | `X4` | | README.md 安装指引（pip install 示例文本）；Q1/Q2 FAIL 为真缺陷不豁免（darwin fork 后续改进） | 2026-09-26 |
| `skill-standardize` | `X4` | | references/common-issues.md 常见问题示例命令 | 2026-09-26 |
| `skillhub-fork-sync` | `X4` | | SKILL.md:15,57 git clone/pip 操作为本 skill 声明性本职（fork 同步器） | 2026-09-26 |
| `skill-doctor__skillhub` | `X4` | | README.md:49 安装指引；X5（scripts/deep_analysis.py 代码内 URL）**不豁免**，留待人工核验 | 2026-09-26 |

## 未豁免的已知真缺陷（后续改进项，非本轮范围）

| skill | 判据 | 问题 |
|---|---|---|
| `darwin-skill` | Q1/Q2 | SKILL.md 软化措辞 4 处 + AI 腔 3 处（🔴 总评来源；darwin fork 可修） |
| `grill-me` | Q3 | 无反例/禁区表述 |
| `show-me` | Q3 | 同上 |
| `install-github-skill` | S3 | 引用 `scripts/screenshot.mjs` 断链（与上游非自包含问题一致） |
| `skillhub-fork-sync` | S3 | 引用 `scripts/check_update.py` 断链 |
| `make-skill` | S3 | 引用 5 个路径断链（`scripts/x.py` 等示例占位符） |
| `skill-test-generate__skillhub` | S3 | 引用 `scripts/analyze.py` 断链 |
| `qa-agent-testing__skillhub` | S2 | description <30 字符 |
| `skill-auditor` | S2 | 同上 |
| `skill-standardize` | S2 | 同上 |
| `using-agent-skills` | S2 | 同上 |
| `skill-doctor__skillhub` | X5 | scripts/deep_analysis.py 代码内 URL，待人工核验是否实际外呼 |
