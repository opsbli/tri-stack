# Changelog

本文件记录 智引（tri-geo）skill 的版本变更历史。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.3] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手传统 SEO、海外引擎优化、逆向破解与内容写作/技术改造实现，只做国内主流引擎 GEO 全链路。

## [1.0.2] - 2026-09-16

### 变更（skillhub 发布兼容性修复）

- **模板扩展名**：`templates/report.html.j2`、`templates/quick-card.html.j2` 重命名为 `.html`（去掉 `.j2`）。原因：skillhub 平台上传接口拒绝 `.j2` 扩展名（HTTP 400「不允许的文件类型」）；模板内容为零第三方依赖的标准库子集渲染（非 Jinja2），扩展名仅为命名约定，改名不影响任何渲染行为与对外能力语义。
- **`scripts/report_build.py`**：加载逻辑由 `*.html.j2` 改为 `*.html`（第 216 行三元表达式 + 第 12 行注释同步更新）。
- **文档同步**：`SKILL.md` 目录结构、`README.md` 目录树中模板文件名由 `.j2` 改为 `.html`。
- 纯发布载体兼容性调整；**评分口径、脚本行为、对外能力语义零变更**；版本四件套（SKILL / CHANGELOG / _meta / tests frontmatter）强一致 1.0.2。

## [1.0.1] - 2026-09-16

### 变更（tri-forge 家族合规审计修复 · 审计报告 `docs/audit-tri-geo-20260916.md`）

- **frontmatter**：`name` 由「智引」改为 `tri-geo`（约束 1：name==slug kebab-case，中文名保留于 displayName）；description 删除「纳米」（与 `validate_input.py` 8 引擎白名单漂移，R3），追加「支持独立安装，含上游依赖检测三态逻辑」（约束 2）
- **强制执行契约**：补激活语义与独立使用前置（约束 3）；自检句增「触发源」「已读教训」字段（约束 5）；新增条目 9「教训文件读写闭环」（`.tribro/tri-geo/lessons.md`，约束 23）与条目 10「结论置信标注」三要素（约束 27）
- **新增章节**：上游依赖检测（三态）/ 输入契约 / 职责边界（含 tri-intent 豁免理由与相邻 skill 边界）/ 知识装配顺序（6 references 分层 + grep 模式 + 覆盖优先级，约束 25）/ 质量标准（约束 16）/ 版本检查与更新机制 STUB（≤30 行指向 version-check-spec.md，约束 22-③）/ 目录结构（与磁盘 diff 一致，约束 15）/ 进化契约（三要素，约束 23）
- **章节更名**：「数据落盘约定」→「落盘规则」（约束 7 统一标题），增登 lessons.md 路径与「NEVER 生成 LICENSE/.gitignore」
- **完成判据**：增补教训写入判据与「停车态 ≠ 结束态」区分（约束 24）
- **tests**：新增 `tests/tri-geo-full-testcases.md`（带 frontmatter，能力清单 A-H 41 项 + 用例矩阵，约束 9/14）
- **README**：目录结构补登记 full-testcases；测试章节补执行口径；新增「来源与归属」（geo-seo-claude-main 方法论参考，MIT 归属声明）
- 纯合规与文档补全，**评分口径、脚本行为、对外能力语义零变更**

## [1.0.0] - 2026-09-16

首个发布版本。面向**中国主流生成式引擎**（DeepSeek、豆包、Kimi、智谱 GLM、文心一言、元宝、通义、百度 AI、纳米）的 GEO 通用 skill，严格依据 `docs/zhiyin-design-guide-20260915.md` 实现。

### 定位与问题解法

| 行业空白 | 智引的解法 |
|---------|-----------|
| 既有 GEO 工具默认以海外搜索引擎为目标，国内引擎适配缺失 | 全链路只优化国内 8 类引擎，全部规则按中文语料与国内平台重写 |
| 优化建议停留于"经验清单"，无确定性评分 | 双轨评分全部由脚本计算：轨道 A 站内信号分（`site_signal.py`）、轨道 B 引擎实测分（`probe_runner.py` + `answer_judge.py`） |
| 效果靠自我推演，无法复核 | 证据链落盘：原始 HTML、引擎原始回答、判定 JSON、快照台账全程留痕；每个分数携带「脚本 + 证据路径 + 采样轮数与波动区间」 |
| 关键环节依赖 prompt 约束，输出不稳定 | 参数校验、流程控制、规范校验、来源核验、结果判定、快照与 delta、报告渲染**全部脚本化**；prompt 仅保留 4 处白名单且每处有脚本打回闭环 |
| 数据可捏造、广告法违规可绕过 | 两条硬阻断红线：`citation_check.py` 命中捏造即退出码 3；`writing_rules.py` 命中广告法禁用语即退出码 3，**NEVER 降级、NEVER 豁免** |

### 核心能力（七大模块）

- **M1 快检（60 秒）**：5 项确定性快指标 + 1 次引擎实测 → 结论卡（分数 + Top3 修复项 + 证据路径）
- **M2 全站诊断**：双轨评分 + veto 一票否决（无正文 / 全爬虫封禁）→ 双分数报告 + P0-P2 行动清单
- **M3 内容重写**：证据狩猎 → 直答前置 → 配额补足 → 反模式清除 → Schema 注入，打回闭环最多 2 轮
- **M3+ 国内模型引用适配（CN-Fit）**：按引擎 RAG 偏好产出可直引答案块，实测验证引用友好度
- **M4 技术基建**：爬虫访问矩阵、llms.txt、JSON-LD、SSR 检测
- **M5 渠道矩阵**：百科 / 知乎 / 公众号 / CSDN / 搜狐 / POI 布局（P0-P3 优先级）
- **M6 监测迭代**：快照追加 + delta 计算 + pattern 沉淀

### 脚本（9 个领域脚本 + 1 个家族版本门）

| 脚本 | 职责 | 退出码 |
|------|------|-------|
| `check_update.py` | 版本门第零步（家族共用逻辑，自 tri-cache 逐字复制） | <20 放行 / ≥20 阻断 |
| `validate_input.py` | 参数校验与规范化（URL 归一化、按模式校验必填、引擎白名单） | 0 / 1 缺必填 / 2 非法 |
| `fetch_page.py` | 抓取解析 + 原始 HTML 落盘（urllib + html.parser，零第三方依赖） | 0 / 2 失败 / 3 正文过少 |
| `site_signal.py` | 站内信号五维评分 + 技术基建 + Schema + 权威信号 + 爬虫/llms.txt | 0 / 1 封顶 / 2 阻断 |
| `writing_rules.py` | 写作规范校验 R1-R10（直答前置、120-200 字、代词密度、统计密度、广告法红线 R9） | 0 / 2 打回 / 3 红线 |
| `citation_check.py` | 来源核验与捏造检测（数字/年份/引文在来源页定位） | 0 / 2 未核验 / 3 硬阻断 |
| `probe_runner.py` | 实测执行与流程控制（`plan` / `ingest` / `status`），**NEVER 伪造回答** | 0 / 2 校验失败 |
| `answer_judge.py` | 实测结果规则判定（提及率 / 引用位次 / 情感 / 波动区间由实测统计） | 0 / 2 无样本 |
| `snapshot.py` | 快照台账与 delta（追加写，同日重复用 `--revision`，NEVER 覆盖） | 0 / 2 无数据 / 3 拒绝覆盖 |
| `report_build.py` | 报告渲染（标准库子集模板引擎，模板缺失降级 Markdown） | 0 / 2 缺入参 |

### 其他交付

- **6 个 references**：`geo-theory.md`、`geo-writing-zh.md`、`models-cn.md`、`channels-cn.md`、`scoring-spec.md`、`anti-patterns.md`，**全部带「最后验证日期 2026-09-16」戳**；国内引擎生态相关结论统一标记 `unverified`（待实测填充，不捏造）
- **6 套 JSON-LD 模板**（`schema/`）：organization / local-business / article-author / software-saas / product-ecommerce / searchaction，`sameAs` 优先国内高权重源
- **2 套报告模板**（`templates/`）：`report.html.j2`、`quick-card.html.j2`，含证据路径注入
- **离线验收套件**（`tests/verify_tri_geo.py`）：T1 管线冒烟 / T2 确定性回归 / T4 重写 A-B / T5 红线注入，**23/23 全绿**

### 实现约束

- 全脚本**零第三方依赖**（仅 Python 标准库），确保任意环境可跑
- 技术选型遵循设计指南：模板保留 `.j2` 后缀但由 `report_build.py` 内置标准库子集引擎渲染（不引入 Jinja2）
- 版本强一致：SKILL.md == CHANGELOG.md == tests == `_meta.json` == `1.0.0`

### 已知未覆盖（非缺陷，属设计边界）

- **T3 双站点真实对比测试**、**T6 四引擎真实会话测试**需联网与引擎账号访问，设计为上线后由使用者执行；样本不足时脚本标注 `source_type: trace_search/unavailable`，NEVER 以 0 分或估算填充
- `models-cn.md` 中引擎偏好为框架级描述，随实测留痕回填
