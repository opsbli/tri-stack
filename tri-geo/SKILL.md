---
name: tri-geo
slug: tri-geo
version: 1.0.3
displayName: 智引
description: 面向中国主流生成式引擎（DeepSeek、豆包、Kimi、智谱 GLM、文心一言、元宝、通义、百度 AI）的 GEO（生成式引擎优化）通用 skill。双轨评分：站内信号分由 site_signal.py 确定性计算（可引用性五维/技术基建/Schema/权威信号/爬虫与 llms.txt），引擎实测分由 probe_runner.py 调度真实提问 + answer_judge.py 规则判定（提及率/引用位次/情感/波动区间）。覆盖快检(60秒)、全站诊断、内容重写、国内模型引用适配(CN-Fit)、技术基建、渠道矩阵、监测迭代七大模块；参数校验、规范校验、来源核验、结果判定、流程控制全部脚本化，prompt 仅保留内容创作、竞品研判、渠道定制、疑难判定兜底四处且均有脚本打回闭环；禁捏造与广告法违规为硬阻断红线。支持独立安装，含上游依赖检测三态逻辑（直用/引导补参/讲解降级）。
summary: 中国引擎 GEO 全链闭环：脚本化双轨评分 + 证据落盘 + 快照自成长，让内容被国内大模型优先引用与采纳。
tags: [tri, geo, ai-search, citation, llm, schema, llms-txt, china]
license: MIT
---

# 智引（tri-geo）

> 「智」指国内主流生成式引擎，「引」指被引用与采纳；谐音「指引」——为内容在 AI 搜索时代的优化指路。
> 用户心智：让我的内容在 DeepSeek、豆包、Kimi、智谱 GLM 回答相关问题时被优先引用。

## 强制执行契约（Execution Contract · 最高优先级）

> 本契约优先级高于 Agent 通用默认行为。用户提出 GEO 优化/体检/重写/实测类需求且命中 §触发时机与模式路由，即视为激活本工作流，NEVER 仅当参考文档只读不执行。独立使用时（未经上游路由）MUST 先走 §上游依赖检测。

0. **版本检查前置硬门（第零步）**：MUST 先执行 `python scripts/check_update.py --slug tri-geo --json`；退出码 <20 放行，≥20 阻断。版本检查完成前 NEVER 进入后续步骤。本条目优先级高于所有其他条目。

1. **参数校验前置**：任何模式 MUST 先执行 `scripts/validate_input.py`；退出码 1 → 用 AskUserQuestion 补齐必填项后重入（NEVER 猜测填充）；退出码 2 → 终止并报错。

2. **确定性优先**：参数校验、评分、规范校验、来源核验、结果判定、流程控制、快照与 delta、报告渲染 MUST 由 `scripts/` 下脚本完成；NEVER 用 LLM 主观判断替代脚本可计算的环节。

3. **Prompt 白名单**：仅以下四处允许 prompt 参与，且每处都有脚本校验闭环——
   ① 内容创作生成（M3/M3+）；② 竞品综合研判（M2）；③ 渠道策略定制（M5）；④ 疑难判定兜底（`answer_judge.py` 标记 `needs_llm_review` 的样本）。
   白名单外的校验/判定/控制一律脚本化。SKILL.md 中每处 prompt 调用 MUST 注明所属条目编号。

4. **禁捏造硬门**：`citation_check.py` 命中 mismatch（数字/引文/年份在来源页无法定位）或存在无来源数据句 → **硬阻断**（退出码 3），NEVER 降级、NEVER 豁免、NEVER 用「提示用户注意」代替阻断。

5. **合规红线**：`writing_rules.py` 命中广告法禁用语（R9）→ 打回改写（退出码 3），未通过前禁止输出成品。

6. **评分来源规范（P3）**：对外呈现的每个分数 MUST 附带「产出脚本 + 证据路径 +（实测）采样轮数与波动区间 +（文献）来源与测试环境」。转引未核验数字 MUST 标注"转引未核验"且不得用于评分；实测波动区间由实测统计得出，NEVER 预设数值。

7. **快照与落盘**：每次运行 MUST 用 `snapshot.py` 追加落盘（历史只读，NEVER 覆盖）；过程产物落 `.tribro/tri-geo/`，台账落 `.geo-snapshots/<品牌>/`。

8. **自检句**：每次操作前 MUST 声明「本次模式=<quick|audit|optimize|cn_fit|infra|channels|monitor>，触发源=<用户显式调用|上游路由>，目标=<url/域名/品牌>，引擎=<...>，已执行 check_update=<A/B/C/D>，已执行 validate_input=<通过/补齐/报错>，已读教训=<N 条/无文件>，脚本链=<...>」；与契约/快照冲突时 MUST 停止并纠正。

9. **教训文件读写闭环**：激活时（版本门第零步后）MUST 先读取 `.tribro/tri-geo/lessons.md`（历史执行沉淀的教训；目录或文件不存在则**静默跳过**——NEVER 报错、NEVER 阻断、NEVER 追问）；执行结束后 MUST 追加本次教训（含日期/场景/教训/可操作规避动作；空泛内容如「本次顺利」NEVER 写入，无新增写「无新增」占位留痕）；写入失败 MUST 提示用户但不阻断交付。

10. **结论置信标注**：本 skill 产出的一切结论性表达/观点/判定（评分解读、适配建议、渠道判断、疑难兜底结论）MUST 附三要素：① 置信度（高/中/低）；② 依据类型六选一（`事实 known`/`计算 computed`/`推断 inferred`/`常识 common`/`框架 iframe`/`猜测 guess`）；③ 可验证事实源 URL 或本地证据锚（脚本名 + 证据路径）。`猜测 guess` 类 MUST 标低置信并提示人工验证；NEVER 引用无法访问的编造链接。

## 触发时机与模式路由

| 用户意图（示例） | 模式 | 层级 |
|------------------|------|------|
| "帮我看看这个页面 AI 会不会引用" | `quick` | L0（60 秒） |
| "把这篇改写成 AI 爱引用的" | `optimize` | L1（5 分钟） |
| "让国内大模型（DeepSeek/豆包/Kimi/智谱）引用这段话" | `cn_fit` | L1 |
| "给我的网站做 GEO 体检" | `audit` | L2（30 分钟） |
| "检查爬虫、llms.txt、结构化数据" | `infra` | L2 |
| "该发哪些平台？百科/知乎/公众号怎么布局" | `channels` | L3 |
| "跟踪这个月的提升情况" | `monitor` | L3 |

**意图路由三原则**：① 用户不必知道模块名，说"不知道从哪开始"→ 路由 L0；② 已提供的信息直接提取，只补必缺项（由 `validate_input.py` 判定）；③ 实测分标注波动区间，推演/定性内容显式标注依据类型。

## 上游依赖检测（独立使用时）

| 模式 | 触发条件 | 行为 |
|------|---------|------|
| A · 直用模式 | 用户已给出目标（URL/域名/品牌）与意图 | 直接进入 §模块矩阵 对应模式（本 skill 无强制上游 skill） |
| B · 引导补参 | 缺模式必填项（`validate_input.py` 退出码 1） | 按 `missing_required` 清单用 AskUserQuestion 补齐后重入；NEVER 猜测填充 |
| C · 讲解降级 | 用户只想了解 GEO 原理/边界，不提供目标 | 仅讲解 `references/geo-theory.md` 与 §评分解读，不执行脚本链 |

## 输入契约

参数与默认值以 `scripts/validate_input.py` 为唯一事实源（`--help` 可查全量）：

| 参数 | 用途 | 默认/必填 | 约束 |
|------|------|----------|------|
| `--url` / `--domain` | 目标页面/域名（二选一，统称 target） | 按模式必填 | 无 scheme 自动补 `https://`；域名须 idna 合法 |
| `--brand` | 品牌名 | `audit`/`optimize`/`cn_fit`/`channels`/`monitor` 必填 | MUST 与用户原话一致，禁改写 |
| `--product-type` | 品类/产品类型 | `cn_fit` 必填 | — |
| `--target-query` | 目标问题（本内容应被 AI 引用以回答的提问） | 可选 | M3/M3+ 直答校验用 |
| `--engines` | 引擎编码逗号分隔 | 全选 8 引擎 | 白名单外 → 退出码 2；`cn_fit` 未指定时默认 `deepseek,doubao,kimi,zhipu` |
| `--mode` | 运行模式 | 必填 | `quick\|audit\|optimize\|cn_fit\|infra\|channels\|monitor` |

模式必填矩阵：`quick`/`infra`→target；`audit`/`optimize`→target+brand；`cn_fit`→target+brand+product_type；`channels`/`monitor`→brand。

## 职责边界

- **本 skill 负责**：国内 8 类生成式引擎的 GEO 全链路——站内信号评分、引擎实测调度与判定、内容重写与 CN-Fit 适配、技术基建建议、渠道矩阵规划、快照监测。
- **不负责 / NEVER 代办**：传统 SEO 排名优化（外链/关键词排名）；海外引擎（ChatGPT/Perplexity/Gemini 等）的优化执行；引擎接口逆向破解或风控规避；刷收录/虚假流量类灰产手段。
- **与 tri-intent 的关系**：独立领域入口型 skill，不认领 I 系列意图编码、不经 tri-intent 路由，由用户显式调用激活（豁免理由：GEO 是跨内容/技术/渠道的独立领域闭环，现行 27 个 L2 落点无对应项；后续若家族裁定纳入路由，按 L3 子类回填并同步计数）。
- **与相邻 skill 边界**：长文写作与去 AI 化归 tri-article / tri-content（本 skill 只产出「可引用性优化」重写稿并过脚本校验）；网站技术改造归 tri-coding（本 skill 只输出 JSON-LD / llms.txt / robots 建议）。
- **事实源**：评分口径唯一真源 `references/scoring-spec.md`；引擎偏好框架 `references/models-cn.md`（unverified 待实测校准）；脚本实现唯一真源 `scripts/*.py`。
- **不触发场景（Not-Trigger）**：本 skill 不接手「传统 SEO 排名优化（外链/关键词排名）」（NEVER）；不接手「海外引擎优化执行」（NEVER）；不接手「引擎接口逆向破解或风控规避」（NEVER）；不接手「长文写作与去 AI 化」（属 tri-article / tri-content，本 skill 只产出可引用性重写稿并过脚本校验）；不接手「网站技术改造实现」（属 tri-coding，本 skill 只输出 JSON-LD / llms.txt / robots 建议）。

## 模块矩阵（七大模块）

| 模块 | 能力 | 关键脚本 | 交付物 |
|------|------|---------|--------|
| M1 快检 | 5 项确定性快指标 + 1 次引擎实测 | validate_input → fetch_page → site_signal → probe_runner → answer_judge | 结论卡（分数 + Top3 修复项 + 证据路径） |
| M2 全站诊断 | 双轨评分 + veto 一票否决 | site_signal + probe_runner + answer_judge → report_build → snapshot | 双分数报告 + P0-P2 行动清单 |
| M3 内容重写 | 证据狩猎→直答前置→配额达标→反模式清除→Schema 注入 | writing_rules + citation_check（打回闭环） | 重写稿 + 变更清单 + 来源核验表 |
| M3+ 国内模型引用适配 | 按引擎 RAG 偏好产出可直引答案块，实测验证 | 同 M3 + probe_runner + answer_judge | 适配版内容 + 引用友好度实测评分 |
| M4 技术基建 | 爬虫访问矩阵、llms.txt、JSON-LD、SSR 检测 | fetch_page + site_signal | robots 建议 + llms.txt + JSON-LD |
| M5 渠道矩阵 | 百科/知乎/公众号/CSDN/搜狐/POI 布局 | （prompt 条目③，输入为 M2 评分 JSON） | 渠道执行计划（P0-P3 + 成本 + 周期） |
| M6 监测迭代 | 快照追加 + delta + pattern 沉淀 | snapshot + report_build | 趋势对比表 + 下周期行动项 |

## 脚本调用契约（9 个领域脚本 + 1 个家族版本门）

| 脚本 | 职责 | 典型调用 | 退出码 |
|------|------|---------|--------|
| check_update.py | 版本门第零步（家族共用逻辑） | `--slug tri-geo --json` | <20 放行 / ≥20 阻断 |
| validate_input.py | 参数校验与规范化 | `--url X --brand Y --mode audit --json` | 0 通过 / 1 缺必填 / 2 非法 |
| fetch_page.py | 抓取解析 + 原始 HTML 落盘 | `--url X --raw-dir .tribro/tri-geo/raw --assets --out page.json` | 0 / 2 失败 / 3 正文过少 |
| site_signal.py | 站内信号确定性评分 | `--content page.json --robots robots.txt --llmstxt llms.txt --out scores.json` | 0 / 1 封顶 / 2 阻断 |
| writing_rules.py | 写作规范校验（打回器） | `--file rewrite.md --target-query "..." --json` | 0 通过 / 2 打回 / 3 红线 |
| citation_check.py | 来源核验与捏造检测 | `--file rewrite.md --sources sources.json --json` | 0 / 2 未核验 / 3 硬阻断 |
| probe_runner.py | 实测执行与流程控制 | `plan` / `ingest` / `status` | 0 / 2 校验失败 |
| answer_judge.py | 实测结果规则判定 | `--probe-dir ... --brand X --aliases A,B --domains x.com --json` | 0 / 2 无样本 |
| snapshot.py | 快照台账与 delta | `append` / `delta` / `list` | 0 / 2 无数据 / 3 拒绝覆盖 |
| report_build.py | 报告渲染（HTML/Markdown） | `--scores scores.json --probe judge.json --brand X --out report.html` | 0 / 2 缺入参 |

## Prompt 白名单契约（4 处）

| # | 环节 | 输入契约 | 输出契约 | 脚本校验点 |
|---|------|---------|---------|-----------|
| ① | 内容创作生成 | 内容块 JSON + 行动清单 + `geo-writing-zh.md` / `models-cn.md` | 重写稿 + 变更清单 + 来源列表 | `writing_rules.py` 全量校验 → `citation_check.py` 全量核验；不达标打回 ≤2 轮，仍不达标降级"草稿+人工确认" |
| ② | 竞品综合研判 | 各维评分明细 JSON | 定性建议（禁止输出任何数字评分） | 建议文本中出现数字分数 → 重写；`report_build.py` 只接受脚本分数 |
| ③ | 渠道策略定制 | M2 评分 JSON + `channels-cn.md` | 渠道执行计划（P0-P3 排序） | 每项 MUST 引用评分明细或证据路径，无依据项剔除 |
| ④ | 疑难判定兜底 | 单条原始回答 + 判定问题 | 判定结果 + 理由（落盘标注 `judge: llm`） | 兜底占比 >30% → 必须回头补规则，NEVER 扩大兜底 |

## 评分与报告

- **轨道 A 站内信号分**：五维可引用性 40% + 技术基建 20% + Schema 15% + 权威信号 15% + 爬虫与 llms.txt 10%（细则见 `references/scoring-spec.md`，脚本与文档 MUST 一致）。
- **轨道 B 引擎实测分**：prompt 集 × 多轮采样 → 提及率 / 引用位次 / 情感；判定由 `answer_judge.py` 规则完成，存疑样本标记 `needs_llm_review`。
- **报告结构**：每个分数呈现为「分数 ｜ 产出脚本 ｜ 证据路径 ｜ 采样轮数与波动区间 ｜ 文献来源与测试环境」。
- **实测纪律**：NEVER 用 LLM 自我推演冒充实测；引擎不可达时标注 `source_type: trace_search/unavailable`；样本为空 NEVER 记 0 分。

## 落盘规则

```
.tribro/tri-geo/raw/        抓取原始证据（HTML / robots.txt / llms.txt）
.tribro/tri-geo/lessons.md  执行教训台账（追加式：日期/场景/教训/规避动作）
.geo-snapshots/<品牌>/<YYYY-MM-DD>-<mode>.json     台账快照（追加，历史只读）
.geo-snapshots/<品牌>/probe/<engine>/<Pxx>-r<N>.txt 实测原始回答
```

- 过程产物统一落 `.tribro/tri-geo/` 与 `.geo-snapshots/`（目录不存在自动创建，NEVER 散落工作区根目录）；快照历史只读，同日重复运行用 `--revision`。
- **NEVER 生成 `LICENSE` 与 `.gitignore`**——许可证仅由 frontmatter `license: MIT` 声明。

## 错误恢复表

| 错误 | 处置 |
|------|------|
| 页面抓取失败（重试 2 次） | 报错 + 建议用户粘贴正文，NEVER 伪造内容块 |
| 引擎实测单轮失败 | 重试 1 次；有效轮数 <2 标注「样本不足」 |
| 引擎整体不可达 | 降级留痕检索（`source_type: trace_search`）并标注；两条路都不可行时报告只含站内分并声明实测缺失 |
| 判定规则不确定 | 标记 `needs_llm_review`（NEVER 猜测） |
| 快照写入失败 | 输出 JSON 请用户手动保存 |
| 报告渲染失败 | 降级 Markdown；再失败输出原始 JSON |

## Schema 模板选型（schema/，6 套）

| 模板文件 | @type | 适用场景 | 必填字段（缺失即扣分） |
|---------|-------|---------|---------------------|
| organization.json | Organization | 品牌主体/官网首页（**所有站点必做**） | name、url、logo、description、`sameAs` ≥3 条 |
| local-business.json | LocalBusiness | 有线下门店/服务网点 | name、address、telephone、geo、openingHoursSpecification |
| article-author.json | Article + Person（数组） | 内容页/博客/问答/白皮书 | headline、author（Person 对象）、datePublished、dateModified、`speakable` |
| software-saas.json | SoftwareApplication | SaaS / App / 工具型产品 | name、applicationCategory、operatingSystem、offers |
| product-ecommerce.json | Product | 电商商品详情页 | name、image、brand、offers（price + priceCurrency）、sku |
| searchaction.json | WebSite + SearchAction | 官网首页站内搜索框 | url、name、potentialAction.target.urlTemplate |

**注入纪律**：① 模板内 `[REPLACE: ...]` 全部替换后才可上线，**NEVER 保留占位符**；② `sameAs` 优先填国内高权重源（百度百科 → 中文维基 → 知乎机构号 → 公众号 → 企查查/天眼查 → 微博/B 站），链接 MUST 真实可达（`citation_check.py` 同款可达性核验思路）；③ 模板 MUST 落在**服务端渲染的初始 HTML** 中，JS 注入的 JSON-LD 对不执行 JS 的 AI 爬虫不可见；④ 注入后用 `fetch_page.py --assets` 复抓并跑 `site_signal.py`，确认 `schema` 维度分数确有变化（**NEVER 口头声称已注入**）。

## references 按需加载

| 文件 | 加载时机 |
|------|---------|
| geo-theory.md | 任何模式启动前 |
| geo-writing-zh.md | M3 / M3+ 前 |
| models-cn.md | M3+ 前 |
| channels-cn.md | M5 前 |
| scoring-spec.md | 调用 site_signal / answer_judge 前 |
| anti-patterns.md | writing_rules / citation_check 维护与调用时 |

## 知识装配顺序

`references/` 共 6 个文件，按层装配、同名只加载一次、冲突以本 skill 内 `references/` 为准：

| 层 | 文件 | 加载时机 | grep 检索模式 |
|----|------|---------|--------------|
| 常驻层 | geo-theory.md | 任何模式启动前 MUST 读 | 「GEO 定义」「SEO 对比」「文献」 |
| 评分层 | scoring-spec.md | 调用 site_signal / answer_judge 前 | 维度名（`citability`/`veto`）、「llms.txt 分档」 |
| 模式层 | geo-writing-zh.md | M3 / M3+ 前 | 「直答段」「120-200」「R1」 |
| 模式层 | models-cn.md | M3+ 前 | 引擎编码（`deepseek` 等）、「unverified」 |
| 模式层 | channels-cn.md | M5 前 | 平台名（「百度百科」「知乎」「公众号」） |
| 维护层 | anti-patterns.md | writing_rules / citation_check 维护与调用时 | 规则号（R1–R10）、「禁用语」 |

## 质量标准

| 维度 | 标准 | 验证方式 |
|------|------|---------|
| 评分可复现 | 同输入逐字节一致；`--stamp` 默认关闭 | T2 回归项 + 两次运行 diff |
| 红线阻断 | 捏造来源与广告法命中 → 退出码 3，不降级 | T4/T5 红线注入用例 |
| 证据可溯 | 每个分数可回溯至脚本结果 + 落盘文件 | 按报告分数抽查证据路径（T7） |
| 实测诚实 | 缺失标 `trace_search/unavailable`；样本空不记 0 分 | 判定 JSON `source_type` 抽查 |
| 版本强一致 | SKILL == CHANGELOG == tests == `_meta.json` | `tests/verify_tri_geo.py` T0 |
| 文档同步 | README/SKILL 描述无矛盾；目录树与磁盘 diff 一致 | 家族审计清单复核 |

## 版本检查与更新机制（强制技术约束 · 硬红线）

> 家族级强制技术约束，优先级与「强制执行契约」同级。细则唯一真源：`references/version-check-spec.md`；可执行实现：本 skill 自带 `scripts/check_update.py`（与 tri-forge 同源，按 `--slug` 自适应）。

```bash
python scripts/check_update.py --slug tri-geo --json
```

- 退出码 `<20` 放行（`0`=A 最新 / `10`=B 离线 / `11`=C 未注册 / `12`=D 升级降级），`20`=BLOCK 绝对禁止执行。
- `state A/B/C/D` 一律放行并按 `warnings/notes` 标注口径；检出陈旧 MUST 先真实执行自动升级（`skillhub upgrade tri-geo`），失败方可落 D 态。
- **发布前特例**：skill 尚未注册 skillhub 时版本检查自然落 C 态降级放行，属预期行为；发布后 C 态提示需核查端点配置。
- 铁律：版本比较/升级/四态判定 MUST 由脚本完成，prompt 层仅调用脚本 + 解析 JSON，NEVER 内联推断；四态判定/升级流程/节流缓存等细则 NEVER 在本文件内联，一律见真源。

## 目录结构

```
tri-geo/
├── SKILL.md                        # 主入口：契约/路由/脚本契约/评分/红线
├── README.md                       # 特性/目录结构/安装/使用/测试/设计原则
├── CHANGELOG.md                    # 版本历史（Keep a Changelog）
├── _meta.json                      # slug + version
├── references/                     # 6 个按需加载文档（见 §知识装配顺序）
├── schema/                         # 6 套 JSON-LD 模板（organization/local-business/article-author/software-saas/product-ecommerce/searchaction）
├── scripts/                        # 9 个领域脚本 + check_update.py 版本门
├── templates/                      # report.html + quick-card.html
└── tests/
    ├── verify_tri_geo.py           # 离线验收（T0/T1/T2/T4/T5）
    ├── tri-geo-full-testcases.md   # 全场景测试用例（带 frontmatter）
    └── fixtures/                   # 固定夹具（页面/重写稿/来源清单/引擎回答）
```

## 进化契约

- **反馈接收点**：用户对评分解读、重写稿、实测判定、渠道建议的任何反馈与纠错，MUST 记入 `.tribro/tri-geo/lessons.md`。
- **经验沉淀位**：`.tribro/tri-geo/lessons.md`（启动读取 → 缺失静默跳过 → 结束追加写入，见契约条目 9）。
- **自我修订触发条件**：① `writing_rules.py` / `citation_check.py` 词表漏报或误报 → 修订词表并同步 `references/anti-patterns.md`；② 引擎白名单或评分细则漂移 → 修订 `validate_input.py` / `references/scoring-spec.md`（脚本与文档 MUST 同改）；③ 章节或能力调整 → 按 SemVer bump（SKILL/CHANGELOG/tests/`_meta.json` 四处联动 + README 同步）。修订后 MUST 重跑 `tests/verify_tri_geo.py`。

## 完成判据（每次运行结束 MUST 自检）

1. 版本门已执行且退出码 <20；
2. 参数校验通过（或已补齐后重入）；
3. 评分均由脚本产出且证据路径已记录；
4. 重写类产出已通过 writing_rules + citation_check（或明确降级为草稿并说明原因）；
5. 快照已追加且历史未被覆盖；
6. 报告中的每个数字符合评分来源规范；
7. 给出唯一下一步动作（学 geo-studio：NEVER 一次给 10 条建议）；
8. 教训已写入 `.tribro/tri-geo/lessons.md`（或写入失败已提示用户）；
9. 交付形态明确「停车态」或「结束态」。

**停车态 ≠ 结束态**：重写稿降级为「草稿+人工确认」、实测等待用户回填引擎回答、报告待用户确认发布——均为停车态，NEVER 在用户确认前宣告任务结束；脚本链跑完且判据 1-8 全绿方为结束态。
