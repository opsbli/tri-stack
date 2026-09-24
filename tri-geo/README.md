# 智引（tri-geo）

面向**中国主流生成式引擎**的 GEO（Generative Engine Optimization，生成式引擎优化）通用 skill。

「智」指国内主流生成式引擎（DeepSeek、豆包、Kimi、智谱清言、文心一言、元宝、通义千问、百度 AI 搜索），「引」指被引用与采纳；谐音「指引」——为内容在 AI 搜索时代的优化指路。用户心智只有一句：**让我的内容在 DeepSeek、豆包、Kimi、智谱回答相关问题时被优先引用。**

---

## 目录

- [特性](#特性)
- [目录结构](#目录结构)
- [安装与前置](#安装与前置)
- [快速开始](#快速开始)
- [七大模块](#七大模块)
- [脚本契约](#脚本契约)
- [Prompt 白名单](#prompt-白名单)
- [评分解读](#评分解读)
- [Schema 模板选型](#schema-模板选型)
- [references 按需加载](#references-按需加载)
- [数据落盘约定](#数据落盘约定)
- [错误恢复](#错误恢复)
- [测试与验收](#测试与验收)
- [红线与合规](#红线与合规)
- [常见问题](#常见问题)
- [设计原则](#设计原则)

---

## 特性

### 1. 只做国内引擎，不做"翻译版 SEO"

全链路只针对国内 8 类生成式引擎优化，全部规则按**中文语料**重写：字数阈值按「字」而非「词」计、代词密度按中文定语/主语用法计、定义句式按 `X 是/指/包括` 匹配、统计密度正则覆盖 `万元/亿元/%/倍/年` 等中文表达。文档与脚本中不含海外市场优化内容。

### 2. 双轨评分：站内信号 + 引擎实测

| 轨道 | 产出 | 可信度来源 |
|------|------|-----------|
| **A · 站内信号分** | `site_signal.py` 确定性计算（可引用性五维 / 技术基建 / Schema / 权威信号 / 爬虫与 llms.txt） | 同一输入**逐字节可复现**，可回归 |
| **B · 引擎实测分** | `probe_runner.py` 调度真实提问 + `answer_judge.py` 规则判定（提及率 / 引用位次 / 情感 / 波动区间） | 原始回答全部落盘，波动区间由**多轮采样实测 min/max** 得出，NEVER 预设 |

**NEVER 用 LLM 自我推演冒充实测**：引擎不可达时标注 `source_type: trace_search` 或 `unavailable` 并显式声明；样本为空 NEVER 记 0 分。

### 3. 确定性优先：能脚本化的全部脚本化

参数校验、评分、规范校验、来源核验、结果判定、流程控制、快照与 delta、报告渲染**全部由 `scripts/` 完成**。prompt 仅保留 4 处白名单，且每处都有脚本打回闭环。

### 4. 两条硬阻断红线

| 红线 | 触发 | 处置 |
|------|------|------|
| **禁捏造** | `citation_check.py` 命中 mismatch（数字/年份/引文在来源页无法定位）或存在无来源数据句 | 退出码 3，**NEVER 降级、NEVER 豁免** |
| **合规** | `writing_rules.py` 命中广告法禁用语（R9） | 退出码 3，未通过前禁止输出成品 |

反绕过设计：来源核验的 `key_tokens` 拆为 `data / year / quote / weak` 四类，判定**要求 data 与 year 双命中**——防止"保留真实年份、篡改数字"的捏造绕过；`DATA_CLAIM_RE` 排除 `天/小时/人/家/款` 等通用量词，`META_LINE_RE` 跳过作者与日期行，避免误报。

### 5. 证据链全程留痕

每个对外呈现的分数都携带：`分数 ｜ 产出脚本 ｜ 证据路径 ｜（实测）采样轮数与波动区间 ｜（文献）来源与测试环境`。抓取的原始 HTML、引擎原始回答、判定 JSON、快照台账全部落盘可回溯。

### 6. 快照自成长

`.geo-snapshots/<品牌>/<YYYY-MM-DD>-<mode>.json` 追加写入，**历史只读、NEVER 覆盖**（同日重复运行用 `--revision N`）；`snapshot.py delta` 计算跨期变化，驱动 M6 监测迭代。

---

## 目录结构

```
tri-geo/
├── SKILL.md                          主入口：强制执行契约 / 模式路由 / 脚本调用契约 / 红线
├── README.md                         本文件：特性 / 用法 / 评分 / 测试 / 设计原则
├── CHANGELOG.md                      Keep a Changelog + SemVer（能力型发布日志）
├── _meta.json                        平台元数据（slug / version）
├── references/                       6 个按需加载文档
│   ├── geo-theory.md                GEO 理论基线（中国市场视角）+ 文献数字测试环境
│   ├── geo-writing-zh.md            中文可引用写作规范（直答段 120-200 字等）
│   ├── models-cn.md                 国内 8 引擎引用偏好框架（当前 unverified，待实测校准）
│   ├── channels-cn.md               国内信源渠道矩阵（百科 / 知乎 / 公众号 / POI 等）
│   ├── scoring-spec.md              双轨评分细则（唯一权威口径，脚本 MUST 一致）
│   └── anti-patterns.md             反模式词表与广告法禁用语（与脚本词表同步）
├── scripts/                          9 个领域脚本 + 1 个家族版本门
│   ├── check_update.py              版本门第零步（家族共用逻辑）
│   ├── validate_input.py            参数校验与规范化
│   ├── fetch_page.py                抓取解析 + 原始 HTML 落盘
│   ├── site_signal.py               站内信号确定性评分
│   ├── writing_rules.py             写作规范校验 R1-R10（打回器）
│   ├── citation_check.py            来源核验与捏造检测（硬阻断）
│   ├── probe_runner.py              实测执行与流程控制（plan / ingest / status）
│   ├── answer_judge.py              实测结果规则判定
│   ├── snapshot.py                  快照台账与 delta（append / delta / list）
│   └── report_build.py              报告渲染（stdlib 子集模板）
├── schema/                           6 套 JSON-LD 模板
│   ├── organization.json            Organization（品牌主体，所有站点必做）
│   ├── local-business.json          LocalBusiness（线下门店/服务网点）
│   ├── article-author.json          Article + Person 数组（内容页 + 作者实体）
│   ├── software-saas.json           SoftwareApplication（SaaS / App / 工具）
│   ├── product-ecommerce.json       Product（电商商品详情页）
│   └── searchaction.json            WebSite + SearchAction（站内搜索框）
├── templates/
│   ├── report.html                  全量报告模板
│   └── quick-card.html              60 秒快检结论卡模板
└── tests/
    ├── verify_tri_geo.py            离线验收脚本（T0/T1/T2/T4/T5，28 项）
    ├── tri-geo-full-testcases.md    全场景测试用例（能力清单 A-H 41 项 + 用例矩阵）
    └── fixtures/                    固定夹具（good/bad 页面、重写稿、来源清单、引擎回答）
```

运行时数据目录（**不随包发布**）：

```
.tribro/geo/                     过程产物（抓取原始证据、评分 JSON、判定 JSON、报告）
.geo-snapshots/<品牌>/               快照台账（追加，历史只读）
.geo-snapshots/<品牌>/probe/<engine>/ 实测原始回答
```

---

## 安装与前置

```bash
cp -r tri-geo/ /path/to/your/skills/
```

**环境要求**：Python 3.8+，**零第三方依赖**（全部脚本仅用标准库）。无网络、无 API Key 也能跑完整站内评分链路。

**家族激活三要素**（WorkBuddy）：标准路径安装 + `.skills_store_lock.json` 注册表 + `_meta.json`。本 skill 通过文件路径内部调度，`tri-intent` 负责意图路由。

**第零步版本门**：任何模式启动前 MUST 先执行

```bash
python scripts/check_update.py --slug tri-geo --json
```

退出码 `<20` 放行，`>=20` 阻断。

---

## 快速开始

### 60 秒快检（`quick`）

```bash
# 0. 版本门
python scripts/check_update.py --slug tri-geo --json

# 1. 参数校验
python scripts/validate_input.py --url example.com --brand 格力 --mode quick --json

# 2. 抓取解析（同时抓 robots.txt / llms.txt）
python scripts/fetch_page.py --url https://example.com/page \
  --raw-dir .tribro/geo/raw --assets --out page.json --json

# 3. 站内信号评分
python scripts/site_signal.py --content page.json \
  --robots .tribro/geo/raw/robots.txt \
  --llmstxt .tribro/geo/raw/llms.txt \
  --out scores.json --json

# 4. 渲染结论卡
python scripts/report_build.py --scores scores.json --brand 格力 \
  --mode quick --out quick-card.html
```

### 完整体检（`audit`，含引擎实测）

```bash
# 生成实测计划（品牌 / 对比 / 推荐 / 问题解决 四意图 × N 轮）
python scripts/probe_runner.py plan --brand 格力 --product-type 空调 \
  --engines deepseek,doubao,kimi,zhipu --rounds 3 \
  --out-dir .geo-snapshots/格力

# Agent 真实提问后，逐条回填原始回答（NEVER 编造回答）
python scripts/probe_runner.py ingest --out-dir .geo-snapshots/格力 \
  --engine deepseek --prompt-id P01 --round 1 \
  --file answer.txt --source-type session

# 查看完成度
python scripts/probe_runner.py status --out-dir .geo-snapshots/格力

# 规则判定
python scripts/answer_judge.py --probe-dir .geo-snapshots/格力/probe \
  --brand 格力 --aliases 格力电器,GREE --domains gree.com \
  --out judge.json --json

# 追加快照
python scripts/snapshot.py append --brand 格力 --mode audit \
  --scores scores.json --probe judge.json --evidence page.json,judge.json

# 出报告
python scripts/report_build.py --scores scores.json --probe judge.json \
  --brand 格力 --mode audit --out 智引-格力-audit-2026-09-16.html
```

### 内容重写（`optimize` / `cn_fit`）

```bash
# 写作规范校验（不达标则打回，最多 2 轮）
python scripts/writing_rules.py --file rewrite.md --target-query "空调怎么选" --json

# 来源核验（命中捏造 → 退出码 3 硬阻断）
python scripts/citation_check.py --file rewrite.md --sources sources.json \
  --out cite.json --json
```

---

## 七大模块

| 模块 | 能力 | 关键脚本 | 交付物 | 层级 |
|------|------|---------|--------|------|
| **M1 快检** | 5 项确定性快指标 + 1 次引擎实测 | validate_input → fetch_page → site_signal → probe_runner → answer_judge | 结论卡（分数 + Top3 修复项 + 证据路径） | L0（60 秒） |
| **M2 全站诊断** | 双轨评分 + veto 一票否决 | site_signal + probe_runner + answer_judge → report_build → snapshot | 双分数报告 + P0-P2 行动清单 | L2（30 分钟） |
| **M3 内容重写** | 证据狩猎 → 直答前置 → 配额补足 → 反模式清除 → Schema 注入 | writing_rules + citation_check（打回闭环） | 重写稿 + 变更清单 + 来源核验表 | L1（5 分钟） |
| **M3+ 国内模型引用适配** | 按引擎 RAG 偏好产出可直引答案块，实测验证 | 同 M3 + probe_runner + answer_judge | 适配版内容 + 引用友好度实测评分 | L1 |
| **M4 技术基建** | 爬虫访问矩阵、llms.txt、JSON-LD、SSR 检测 | fetch_page + site_signal | robots 建议 + llms.txt + JSON-LD | L2 |
| **M5 渠道矩阵** | 百科 / 知乎 / 公众号 / CSDN / 搜狐 / POI 布局 | （prompt 条目③，输入为 M2 评分 JSON） | 渠道执行计划（P0-P3 + 成本 + 周期） | L3 |
| **M6 监测迭代** | 快照追加 + delta + pattern 沉淀 | snapshot + report_build | 趋势对比表 + 下周期行动项 | L3 |

### 模式路由

| 用户意图（示例） | 模式 | 层级 |
|------------------|------|------|
| "帮我看看这个页面 AI 会不会引用" | `quick` | L0 |
| "把这篇改写成 AI 爱引用的" | `optimize` | L1 |
| "让国内大模型（DeepSeek/豆包/Kimi/智谱）引用这段话" | `cn_fit` | L1 |
| "给我的网站做 GEO 体检" | `audit` | L2 |
| "检查爬虫、llms.txt、结构化数据" | `infra` | L2 |
| "该发哪些平台？百科/知乎/公众号怎么布局" | `channels` | L3 |
| "跟踪这个月的提升情况" | `monitor` | L3 |

**意图路由三原则**：① 用户不必知道模块名，说"不知道从哪开始"→ 路由 L0；② 已提供的信息直接提取，只补必缺项（由 `validate_input.py` 判定）；③ 实测分标注波动区间，推演/定性内容显式标注依据类型。

**各模式必填项**（由 `validate_input.py` 强制）：

| 模式 | 必填 |
|------|------|
| `quick` / `infra` | target（URL 或域名） |
| `audit` / `optimize` | target + brand |
| `cn_fit` | target + brand + product_type |
| `channels` / `monitor` | brand |

引擎参数 `--engines` 默认全选 8 引擎；`cn_fit` 未指定时默认四引擎重点：`deepseek, doubao, kimi, zhipu`。

---

## 脚本契约

| 脚本 | 职责 | 典型调用 | 退出码 |
|------|------|---------|--------|
| `check_update.py` | 版本门第零步（家族共用逻辑） | `--slug tri-geo --json` | <20 放行 / ≥20 阻断 |
| `validate_input.py` | 参数校验与规范化（URL 补全 scheme、域名 idna 校验、按模式校验必填、引擎白名单） | `--url X --brand Y --mode audit --json` | 0 通过 / 1 缺必填 / 2 非法 |
| `fetch_page.py` | 抓取解析 + 原始 HTML 落盘（urllib + html.parser，10s 超时 2 次重试；支持 `--file` 离线解析） | `--url X --raw-dir .tribro/geo/raw --assets --out page.json` | 0 / 2 失败 / 3 正文过少 |
| `site_signal.py` | 站内信号五维评分 + 技术基建 + Schema + 权威信号 + 爬虫/llms.txt | `--content page.json --robots robots.txt --llmstxt llms.txt --out scores.json` | 0 / 1 封顶 / 2 阻断 |
| `writing_rules.py` | 写作规范校验 R1-R10 | `--file rewrite.md --target-query "..." --json` | 0 通过 / 2 打回 / 3 红线 |
| `citation_check.py` | 来源核验与捏造检测 | `--file rewrite.md --sources sources.json --offline --json` | 0 / 2 未核验 / 3 硬阻断 |
| `probe_runner.py` | 实测执行与流程控制 | `plan` / `ingest` / `status` | 0 / 2 校验失败 |
| `answer_judge.py` | 实测结果规则判定 | `--probe-dir ... --brand X --aliases A,B --domains x.com --json` | 0 / 2 无样本 |
| `snapshot.py` | 快照台账与 delta | `append` / `delta` / `list` | 0 / 2 无数据 / 3 拒绝覆盖 |
| `report_build.py` | 报告渲染（HTML / Markdown） | `--scores scores.json --probe judge.json --brand X --out report.html` | 0 / 2 缺入参 |

**确定性纪律**：`--stamp` 默认关闭（注入时间戳会破坏可复现性）；同输入重复运行输出逐字节一致，由 `tests/verify_tri_geo.py` 的 T2 回归项守住。

**引擎白名单（8 个）**：`deepseek` `doubao` `kimi` `zhipu` `wenxin` `yuanbao` `tongyi` `baidu_ai`。传入白名单外编码 → 退出码 2。

---

## Prompt 白名单

| # | 环节 | 输入契约 | 输出契约 | 脚本校验点 |
|---|------|---------|---------|-----------|
| ① | 内容创作生成 | 内容块 JSON + 行动清单 + `geo-writing-zh.md` / `models-cn.md` | 重写稿 + 变更清单 + 来源列表 | `writing_rules.py` 全量校验 → `citation_check.py` 全量核验；不达标打回 ≤2 轮，仍不达标降级"草稿+人工确认" |
| ② | 竞品综合研判 | 各维评分明细 JSON | 定性建议（**禁止输出任何数字评分**） | 建议文本中出现数字分数 → 重写；`report_build.py` 只接受脚本分数 |
| ③ | 渠道策略定制 | M2 评分 JSON + `channels-cn.md` | 渠道执行计划（P0-P3 排序） | 每项 MUST 引用评分明细或证据路径，无依据项剔除 |
| ④ | 疑难判定兜底 | 单条原始回答 + 判定问题 | 判定结果 + 理由（落盘标注 `judge: llm`） | 兜底占比 >30% → 必须回头补规则，NEVER 扩大兜底 |

白名单外的校验 / 判定 / 控制一律脚本化。

---

## 评分解读

### 轨道 A：站内信号分（`site_signal.py`）

| 维度 | 权重 | 构成 |
|------|------|------|
| 可引用性 citability | 40% | 答案块质量 30% + 段落自包含 25% + 结构可读性 20% + 统计密度 15% + 独特性 10% |
| 技术基建 infra | 20% | SSR 40% + 可索引 20% + 站点地图 20% + URL 10% + 语言 10% |
| 结构化数据 schema | 15% | JSON-LD 类型与必填字段（Organization / sameAs≥3 / Article+author+dateModified / Person / BreadcrumbList） |
| 权威信号 authority | 15% | 署名 30 + 更新时间可见 25 + 外链引用 25 + 一手数据/原创研究 20 |
| 爬虫与 llms.txt | 10% | 爬虫 70% + llms.txt 30% |

**关键规则**：

- 段落自包含：字数 120-200（40 分）/ 100-250（28）/ 80-300（16）/ 其他（6）；代词密度 <2%（30）或 <4%（18）；专名 ≥3（30）或 ≥1（15）
- 统计密度：每 500 字 ≥3 个统计点记满，按 `密度/3×100` 线性计分
- 爬虫判定只采信**已公开 UA**：Bytespider、Baiduspider、360Spider、Sogou web spider、YisouSpider；未公开 UA 的厂商（DeepSeek / Kimi / 智谱 / 元宝等）**不参与评分**，仅在报告中提示人工核查
- llms.txt 分档：0（无）/ 30（格式不完整）/ 50（有标题与少量链接）/ 70（结构完整）/ 90（含 llms-full.txt）
- 未提供 `robots.txt` 时爬虫维度**不计分**并标注"NEVER 猜测"

**veto 一票否决**：

| code | 类型 | 触发 | 处置 |
|------|------|------|------|
| `NO_CONTENT` | block | 正文 <100 字 | 退出码 2，无法评分 |
| `CRAWLER_BLOCKED_ALL` | cap60 | 全部已核验爬虫被禁 | 总分封顶 60，退出码 1 |

**评级**：90-100 优秀 ｜ 75-89 良好 ｜ 60-74 一般 ｜ 40-59 薄弱 ｜ 0-39 近乎不可见

### 轨道 B：引擎实测分（`probe_runner.py` + `answer_judge.py`）

| 项 | 规则 |
|----|------|
| prompt 集 | 覆盖品牌 / 对比 / 推荐 / 问题解决四意图，默认每引擎每问题 3 轮 |
| 提及判定 | 品牌名与别名字符串匹配（大小写不敏感），附命中位置摘录 ±30 字 |
| 引用位次 | 按回答中出现的域名顺序取品牌域名首次序号（1 起）；无 URL 时取引用标记位置 |
| 情感 | 推荐/值得/稳定 → positive；不推荐/投诉/避坑 → negative；冲突 → conflict；否则 neutral |
| 存疑样本 | 情感冲突或"有提及但无位次" → 标记 `needs_llm_review`，NEVER 猜测判定 |
| 波动区间 | 由多轮采样实测的 min/max 统计得出，**不预设数值** |
| 缺失数据 | 引擎不可达 → `source_type: trace_search/unavailable` 显式标注；样本为空 NEVER 记 0 分 |

### 报告呈现结构

```
分数 ｜ 产出脚本 ｜ 证据路径 ｜ （实测）采样轮数与波动区间 ｜ （文献）来源与测试环境
```

转引未核验数字 MUST 标注"转引未核验"且**不得用于评分**。

### 关于文献数字的立场

`references/geo-theory.md` 收录了 KDD 2024 的 GEO 研究结论（arXiv:2311.09735 / DOI 10.1145/3637528.3671900）：结构化优化最高 +40%（GEO-bench：10,000 查询 × 25 领域，内部 GPT-3.5 测试床），线上引擎复核约 +22%（Perplexity.ai 实测）。**这些数值产生于海外引擎实验环境，不可套用于国内引擎评分**；国内等效幅度必须由 `probe_runner.py` + `answer_judge.py` 实测建立自有基线。

---

## Schema 模板选型

| 模板文件 | @type | 适用场景 | 必填字段（缺失即扣分） |
|---------|-------|---------|---------------------|
| `organization.json` | Organization | 品牌主体 / 官网首页（**所有站点必做**） | name、url、logo、description、`sameAs` ≥3 条 |
| `local-business.json` | LocalBusiness | 有线下门店 / 服务网点 | name、address、telephone、geo、openingHoursSpecification |
| `article-author.json` | Article + Person（数组） | 内容页 / 博客 / 问答 / 白皮书 | headline、author（Person 对象）、datePublished、dateModified、`speakable` |
| `software-saas.json` | SoftwareApplication | SaaS / App / 工具型产品 | name、applicationCategory、operatingSystem、offers |
| `product-ecommerce.json` | Product | 电商商品详情页 | name、image、brand、offers（price + priceCurrency）、sku |
| `searchaction.json` | WebSite + SearchAction | 官网首页站内搜索框 | url、name、potentialAction.target.urlTemplate |

**注入纪律**：

1. 模板内 `[REPLACE: ...]` 全部替换后才可上线，**NEVER 保留占位符**；
2. `sameAs` 优先填国内高权重源（百度百科 → 中文维基 → 知乎机构号 → 公众号 → 企查查/天眼查 → 微博/B 站），链接 MUST 真实可达；
3. 模板 MUST 落在**服务端渲染的初始 HTML** 中——JS 注入的 JSON-LD 对不执行 JS 的 AI 爬虫不可见；
4. 注入后用 `fetch_page.py --assets` 复抓并跑 `site_signal.py`，确认 `schema` 维度分数确有变化（**NEVER 口头声称已注入**）。

---

## references 按需加载

| 文件 | 内容 | 加载时机 |
|------|------|---------|
| `geo-theory.md` | GEO 定义、SEO vs GEO 范式对比、可引用性要素、文献数字与测试环境 | 任何模式启动前 |
| `geo-writing-zh.md` | 直答段规范（120-200 字初始工程值）、问句标题、统计密度、来源声明、校准记录 | M3 / M3+ 前 |
| `models-cn.md` | 国内 8 引擎引用偏好**核验框架**（当前 `unverified`，待实测校准） | M3+ 前 |
| `channels-cn.md` | 百科 / 知乎 / 公众号 / CSDN / 搜狐 / POI 的审核规则、成本与见效周期 | M5 前 |
| `scoring-spec.md` | 双轨评分细则（**唯一权威口径**，脚本实现 MUST 一致） | 调用 site_signal / answer_judge 前 |
| `anti-patterns.md` | 写作反模式词表 + 广告法禁用语词表（与 `writing_rules.py` 同步） | writing_rules / citation_check 维护与调用时 |

全部 references 均带「最后验证日期」戳（当前 2026-09-16），由 `tests/verify_tri_geo.py` 的 T0-05 守门。

---

## 数据落盘约定

```
.tribro/geo/raw/                                    抓取原始证据（HTML / robots.txt / llms.txt）
.geo-snapshots/<品牌>/<YYYY-MM-DD>-<mode>.json           台账快照（追加，历史只读）
.geo-snapshots/<品牌>/probe/<engine>/<Pxx>-r<N>.txt      实测原始回答
```

同日重复运行同一模式：`snapshot.py append --revision 2`（或 `--force` 显式覆盖），**默认拒绝覆盖**并退出码 3。

---

## 错误恢复

| 错误 | 处置 |
|------|------|
| 页面抓取失败（重试 2 次） | 报错 + 建议用户粘贴正文，NEVER 伪造内容块 |
| 引擎实测单轮失败 | 重试 1 次；有效轮数 <2 标注「样本不足」 |
| 引擎整体不可达 | 降级留痕检索（`source_type: trace_search`）并标注；两条路都不可行时报告只含站内分并声明实测缺失 |
| 判定规则不确定 | 标记 `needs_llm_review`（NEVER 猜测） |
| 快照写入失败 | 输出 JSON 请用户手动保存 |
| 报告渲染失败 | 降级 Markdown；再失败输出原始 JSON |

---

## 测试与验收

```bash
python tests/verify_tri_geo.py          # 退出码 0 = 全部通过
```

全场景用例登记见 `tests/tri-geo-full-testcases.md`（能力清单 A-H 共 41 项 + 用例矩阵；标注「人工」的用例按其执行口径操作，执行结果与教训追加至 `.tribro/geo/lessons.md`）。

当前状态：**28/28 通过**，覆盖

| 组 | 内容 |
|----|------|
| T0 交付门禁 | 版本强一致（SKILL == CHANGELOG == `_meta.json`）、`schema/` 六套模板齐备且 JSON 合法、6 个 references 均带验证日期戳 |
| T1 管线冒烟 | 10 个脚本全部以固定夹具执行，校验退出码与关键字段（含 probe / judge / snapshot / report 全链路） |
| T2 确定性回归 | `site_signal.py` 同输入重复运行输出逐字节一致；劣样本分显著低于优样本 |
| T4 重写 A/B | 优稿通过 `writing_rules`；劣稿命中广告法红线退出码 3 |
| T5 红线注入 | 真实来源核验通过；捏造来源硬阻断；无来源数据句阻断 |

**已知边界（需真机环境，非缺陷）**：

- **T3 双样本实测**：需 2 个真实中文站点跑完整 L2 流程
- **T6 国内四引擎实测**：需 DeepSeek / 豆包 / Kimi / 智谱 GLM 的真实会话或接口访问

这两项由使用者在具备网络与引擎访问的环境按 `references/models-cn.md` 与 `SKILL.md` 流程执行；实测结果回填 `models-cn.md` 后，条目方可从 `unverified` 升级为 `verified`。

---

## 红线与合规

1. **禁捏造**：来源核验不通过 → 硬阻断，NEVER 降级为"提示用户注意"。
2. **合规**：广告法禁用语（国家级、最高级、最佳、第一等绝对化用语及变体）→ 打回改写，未通过前禁止输出成品。
3. **评分来源**：对外每个分数 MUST 可追溯至脚本结果与落盘文件；转引未核验数字不得用于评分。
4. **引擎对接合规**：优先官方开放接口 / 官方合作通道；无接口能力时用**留痕检索**（`site:` 核验信源收录与内容存在性）并标注 `source_type: trace_search`；会话自动化遵守平台条款与速率限制（`probe_runner.py` 内置请求间隔与失败熔断）。
5. **不承诺效果**：国内引擎的等效提升幅度未经实测前不对外承诺。

---

## 常见问题

**Q：没有 API Key 能用吗？**
能。轨道 A（站内信号评分）完全离线可跑，零依赖。轨道 B 需要真实提问；无接口时用留痕检索降级并标注 `source_type: trace_search`。

**Q：`--engines` 支持哪些引擎？**
`deepseek` `doubao` `kimi` `zhipu` `wenxin` `yuanbao` `tongyi` `baidu_ai` 共 8 个。留空默认全选。

**Q：为什么爬虫分只判 5 个爬虫？**
只有公开 UA 的爬虫（Bytespider / Baiduspider / 360Spider / Sogou / Yisou）可被客观核验；未公开 UA 的厂商不参与评分，仅在报告中提示人工核查——NEVER 用猜测填补评分。

**Q：快照能覆盖吗？**
默认拒绝（退出码 3）。同日重复运行请加 `--revision N`，或显式 `--force`。历史快照视为只读。

**Q：报告里的分数为什么有的没有波动区间？**
只有引擎实测分（轨道 B）有采样轮数与波动区间；站内信号分（轨道 A）是确定性计算，不存在波动。

**Q：`models-cn.md` 里的引擎偏好能直接用吗？**
不能。当前为 `unverified` 框架版，不得作为评分依据或对外结论输出（P3 红线）。必须经 `probe_runner.py plan` → 真实提问 → `ingest` 回填 → `answer_judge.py` 判定 → 证据写入本表后才能升级为 `verified`。

---

## 来源与归属

本 skill 的设计方法论参考了开源项目 geo-seo-claude-main（MIT License）的 GEO 工程思路；全部脚本、规则词表、评分细则与文档均为面向国内引擎场景的原创实现，未复制其代码。依据 MIT 许可证保留本归属声明。

## 设计原则

- **国内引擎优先**：只优化国内 8 类引擎，规则按中文语料重写，不做海外方案的翻译版
- **确定性优先**：能用脚本算的绝不用 LLM 判断；prompt 只保留 4 处白名单且每处有打回闭环
- **宁缺毋假**：拿不到的数据不估算、不虚构，缺失项显式标注
- **证据可回溯**：每个分数携带脚本、证据路径、采样信息；原始 HTML 与原始回答全程落盘
- **可复现可回归**：默认不注入时间戳，同输入逐字节一致，由 T2 回归项守住
- **红线不豁免**：禁捏造与广告法违规为硬阻断，NEVER 降级处理
- **唯一下一步**：学 geo-studio，每次只给一个唯一下一步动作，NEVER 一次抛 10 条建议
- **零依赖**：全部脚本仅用 Python 标准库，任意环境可跑
