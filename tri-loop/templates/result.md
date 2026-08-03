<!--
  文件头说明：
  本文件为 tri-loop 执行结果模板，适用于 I14（操作执行·loop/domain 创建子类）全部场景。
  用途：记录 loop 创建的完整执行结果，含 charter + substrate 状态 + 测试运行摘要 + artifact 记录 + 缺失项 + 如何再运行，确保 loop 可验证运行。
  生命周期：执行结果落盘后不修改（审计完整性）；知识库内容文件（loop README / LOG.md）可覆盖/追加更新。
  质量要求：Timeline 一行 + LOG.md 一条 + result.md 一份，三个记录 MUST 有；charter 不完整的 loop 不得 scaffold。
  填入指引：以下 <...> 为占位符，需据实际执行情况填入；<!-- --> 注释为结构说明，落盘时可保留或删除。
-->

# 执行结果（result · loop 创建）

> **意图编码**：I14（操作执行·loop/domain 创建子类）
> 命名：<问题类型>_<日期>_<时间>_<会话ID>
> 快照来源：`.tribro/snapshots/<命名>.md` §三
> 执行模式：<Mode A 快照模式 / Mode C 降级模式>

---

## 一、Loop Charter

<!-- Loop 的 5 项输入，定义该 loop 是什么、做什么、怎么跑。charter 不完整的 loop 不得 scaffold。 -->

| 输入项 | 内容 |
|---|---|
| name | `<kebab-case，loop 的主文件夹名>` |
| goal | `<一句话：该 loop 驱动的成果>` |
| cadence | `<manual / daily / weekly / cron 表达式>` |
| 做什么 | `消费：<消费什么——signal？数据？收件箱？URL？>` / `产出：<产出什么——signal？doc？报告？代码变更？>` |
| 工具/数据 | `<数据源或凭证，指向 setup skill 或 .env；切勿内联密钥>` |

---

## 二、Substrate 状态

<!-- 记录 substrate 检测结果。全部存在 → 已就绪；有缺失 → 已 bootstrap。 -->

- **Substrate 状态**：<已就绪 / 已 bootstrap>
- **检测详情**：
  - `ARCHITECTURE.md`：<已存在 / 新创建（从 templates/architecture.md 拷贝）>
  - `LOG.md`：<已存在 / 新创建（从 templates/log.md 拷贝）>
  - `CLAUDE.md`：<已存在含 Knowledge base 章节 / 追加了 KB 章节 / 新创建（从 templates/claude-template.md scaffold）>
  - `signals/`：<已存在 / 新创建 + README.md>
  - `docs/`：<已存在 / 新创建 + README.md>
  - `domains/`：<已存在 / 新创建 + README.md>
- **idempotent 校验**：<仅创建缺失文件，已有文件未被修改 / 不适用（substrate 已就绪）>

---

## 三、测试运行摘要

<!-- 真正运行一次 loop（小规模），证明 loop 确实能跑。产出 artifact 可选。 -->

- **运行状态**：<已执行 / dry run（凭证缺失）>
- **做了什么**：<一行——实际执行了什么操作，如「拉取了 3 条 SERP 数据」「分诊了 2 张工单」>
- **发现了什么**：<一行——运行结果，如「关键词排名无变化」「2 张工单已分诊到对应队列」/ "nothing actionable yet">
- **dry run 标注**：<不适用（真实运行）/ dry run——缺少 <凭证/工具>，仅做到 <最远步骤>>
- **运行规模**：<小规模——处理了 N 条/张/个，非全量>

---

## 四、Artifact 记录

<!-- 仅当测试运行确实产出了 signal/doc 时才记录。一次合法的运行可能不会产出值得归档的东西。 -->

- **产出 artifact**：<有 / 无——本次运行无可执行事项>
- **artifact 路径**：
  - `<signals/<slug>.md 或 docs/<slug>.md>`（如有）
- **artifact frontmatter 校验**：<kind + domain 字段完整 / 不适用>

---

## 五、缺失项

<!-- 记录待接入的工具/凭证，指向 setup skill 或 .env。切勿内联密钥。 -->

| 缺失项 | 类型 | 解决指向 |
|---|---|---|
| <缺失的工具/凭证名称> | <API 凭证 / 数据源 / 工具配置> | <指向 setup skill 或 .env> |
| — | — | <无缺失项时填「无」> |

---

## 六、如何再次运行

<!-- 说明 loop 的 cadence 和入口点，让用户知道下次怎么跑。 -->

- **Cadence**：<manual / daily / weekly / cron 表达式>
- **入口点**：<如何触发下一次运行——手动执行 / 定时触发 / 调用命令>
- **运行命令**（如适用）：`<触发命令或操作步骤>`

---

## 七、引用

<!-- 记录本次执行涉及的文件路径，便于审计追溯。 -->

- **快照路径**：`.tribro/snapshots/<命名>.md`
- **loop README 路径**：`domains/<name>/README.md`
- **LOG.md 条目位置**：`<仓库根>/LOG.md`（`## YYYY-MM-DD · <loop-name> loop created + first run` 条目）
- **Timeline 记录**：`domains/<name>/README.md` 的 `## Timeline` 章节

---

## 八、执行可追溯性自检

<!-- 按 SKILL.md §六 质量标准自检，确保 loop 可验证运行。 -->

| 质量维度 | 标准 | 自检结果 |
|---|---|---|
| loop 可验证运行 | README 存在 + Timeline 有测试运行记录 | <达标/不达标：说明> |
| 执行结果落盘 | result.md 存在于 `.tribro/loops/<命名>/` | <达标（本文件即为此记录）> |
| charter 完整 | 5 项输入全部有值 | <达标/不达标：说明> |
| substrate 一致 | ARCHITECTURE.md + LOG.md + CLAUDE.md(Knowledge base) 存在 | <达标/不达标：说明> |
| 记录可追溯 | Timeline 一行 + LOG.md 一条 + result.md 一份 | <达标/不达标：说明> |
| idempotent | bootstrap 仅创建缺失文件 | <达标/不达标：说明> |
| 最小化 | 只创建指定 loop，不擅自扩展 | <达标/不达标：说明> |
| .tribro 目录一致 | 链路文档在 `.tribro/loops/` 下，与 snapshots/actions 同级 | <达标/不达标：说明> |

- **自检结论**：<全部达标→交付 / 存在不达标项→说明问题>
