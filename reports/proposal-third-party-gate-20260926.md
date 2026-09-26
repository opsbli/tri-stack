# Proposal · 第三方 skills 接入质量门禁层（external_skill_gate）

**Approved: yes**（D30 契约 · AskUserQuestion 2026-09-26「按提案建工具」）
**日期**: 2026-09-26
**触发**: 用户指定下一线「第三方 skills 接质量门禁层」
**范围**: `~/.workbuddy/skills/` 下非 tri-* 非自有 skill（实测 **22 个**，非记忆口径的 17）

---

## 一、生产现状（一手实测）

### 1.1 全集盘点（22 个，`.workbuddy/output/third-party-gate-baseline-20260926.tsv`）

agent-code-crew / agent-harness-optimization / anti-distill / archify / darwin-skill / grill-me /
install-github-skill / make-skill / metago-adversarial-review / qa-agent-testing__skillhub /
show-me / skill-auditor / skill-ce-shi__skillhub / skill-doctor__skillhub / skill-pack-auditor /
skill-scanner / skill-standardize / skill-test-generate__skillhub / skill-vetter /
skillhub-fork-sync / skills-security-check / using-agent-skills

### 1.2 现有家族门④基线（tri-forge/scripts/compliance_check.py · 22 条）

**22/22 全 FAIL（FAIL 14–15 条/个）**，且方差为零——逐条聚合：

| 判据类 | 条目 | 第三方结果 |
|---|---|---|
| 家族专属（frontmatter slug/version/displayName、九类章节命名、独立安装声明、版本检查内部化、家族计数） | #1–7, #9–12, #14–15, #22（共 15 条） | **全 22 红** |
| 真质量信号 | #17 禁硬编码家族计数 | 21/22 PASS（仅 darwin-skill FAIL） |
| 真质量信号 | #21 安装评估 | 22/22 PASS |
| 条件触发 | #8, #13, #16, #18–20 | 大多 MISSING（不适用） |

### 1.3 安全模式扫描（`.workbuddy/output/third-party-security-scan-20260926.json`）

六模式（outbound-http / curl-wget / pkg-install / eval-exec / secret-literal / rm-rf）扫描
scripts+references+SKILL.md：**22/22 有命中**。抽检语境分类：

| 候选 | 命中 | 初判 |
|---|---|---|
| skill-auditor | `SKILL.md:72` eval-exec、`:75` rm-rf | 🔴 **真候选**——需人工核语境（若是「审计他人脚本时展示的危险模式示例」则降级） |
| archify | vendored `.mjs` 内 eval ×4、518 处 URL | 🟠 vendored 渲染器内部 eval（运行时模板），URL 多为 license/示例文档 |
| install-github-skill | curl ×7、rm-rf ×1、pkg-install ×4 | 🟡 本职功能即下载安装（声明性），须核 rm-rf 目标是否限自管目录 |
| darwin-skill / make-skill / skill-doctor 等 | README/文档 URL、pip install 示例 | 🟢 文档性假阳性为主 |

## 二、问题（blockers → action items）

| 级别 | 问题 | 证据 |
|---|---|---|
| 🔴 blocker | 现门④对第三方**零区分度**：15/22 条为家族专属判据，全红无信息量；「接入」不能=直接套用现门 | §1.2 矩阵 |
| 🔴 blocker | 第三方安全维度（外联/eval/密钥/危险删除）**无任何机械守卫**，仅安装时一次性人工审计，升级后无重扫机制 | §1.3 + 无工具 |
| 🟠 | 命中需语境判定（README 链接≠实际外呼），纯 grep 有假阳性 → 判据必须 PASS/FAIL/MANUAL 分层，MANUAL 豁免须**登记**（对齐 audit_gate 跨轮单调性思想） | §1.3 抽检 |
| 🟡 | 记忆口径「17 个」与实测 22 漂移 | §1.1 |

**明确排除的路线**：改第三方 skill 去过家族门④——侵入第三方文件、升级即被覆盖覆盖丢失，且家族判据（如版本门）本不适用。

## 三、优化方向（本提案内容）

新建 **`tri-forge/scripts/external_skill_gate.py`**（约 12 条判据，三组）+ 登记层：

1. **结构组**（家族 22 条的适用子集）：SKILL.md 存在、frontmatter 最小集（name/description）、description 含做什么+何时用、references/scripts 资源引用可达抽查。
2. **安全组**（第三方核心价值）：§1.3 六模式扫描；命中 → 默认 🟡 MANUAL，**豁免/降级须写入登记表**（`tri-forge/references/external-gate-registry.md`，含语境理由与日期），NEVER 静默豁免；`secret-literal` 命中直接 🔴。
3. **质量组**（darwin rubric 适用子集）：软化措辞 ≥3 处、AI 腔、「不要做什么」反例清单存在性。
4. **产物**：门④式回执（逐条 PASS/FAIL/MANUAL + 🔴🟠🟡🟢 总评）+ 首轮 22 个基线 TSV；`--self-test` 反例夹具（已知坏样本：eval/密钥/外联各一）。
5. **登记层**：`ops/patches/README.md` 与 `tri-forge` 文档声明「第三方不走家族门④、走 external gate」；**不改 compliance_check.py 逻辑**（避免波及 35 个家族 skill 门④）。第三方升级（备份→重装）后 MUST 重跑 external gate（对齐「装完立即重放」惯例）。

**fix dependency order**：工具 → self-test → 首轮基线 → 豁免登记（人工）→ 文档登记层。

## 四、评分（现状基线，工具建成后出正式分级）

| 维度 | 现值 | 说明 |
|---|---|---|
| 门禁覆盖率（第三方有机械守卫的比例） | **0/22** | 结构+安全双缺 |
| 现门④信噪比（适用判据/总判据） | 7/22（32%） | 直接套用不可行 |
| 真风险候选（待人工语境核验） | 1 🔴 + 2 🟠 | skill-auditor / archify / install-github-skill |

## 五、测试计划

1. `--self-test`：3 个反例夹具（eval/密钥/外联脚本）必须全 🔴；夹具通过 = 工具有 teeth。
2. 首轮 22 个全量跑，输出与 §1.2/§1.3 手工基线交叉核对（矩阵一致性）。
3. 抽 3 个预期-good 场景（如 metago/show-me 结构组）应 PASS，防「全红也当工具正常」。

## 六、验收

- [x] external_skill_gate.py 落盘 + self-test 全绿
- [x] 首轮基线 TSV（22 skill × 12 判据，🔴1 🟠8 🟡3 🟢10）
- [x] 豁免登记表建档（18 条豁免 + 12 条已知真缺陷清单）
- [x] 文档登记层（tri-forge README 双轨制声明 dw7-* 3 op；ops/patches/README.md 计数小节）
- [ ] daily log + MEMORY 口径更新（17→22）
