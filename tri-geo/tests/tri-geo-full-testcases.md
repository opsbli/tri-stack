---
name: tri-geo-full-testcases
description: 「智引」(tri-geo) 全场景测试用例——能力清单 A-H 全量扫描 + 用例覆盖矩阵；离线自动化部分由 tests/verify_tri_geo.py 承载，本文件为用例登记与人工执行口径（基于 tri-geo v1.0.3）。
---

# tri-geo 全场景测试用例

> 用例总数：41（A1-A4 元数据 4 ｜ B1-B9 契约 9 ｜ C1-C4 输入契约 4 ｜ D1-D10 方法论与评分 10 ｜ E1-E2 自检 2 ｜ F1-F4 交付产物 4 ｜ G1-G3 职责边界 3 ｜ H1-H5 质量标准与门禁 5）
> 生成时间：2026-09-16 ｜ 审计方式：脚本实测（verify_tri_geo.py）+ 人工执行项标注
> 离线自动化：`python tests/verify_tri_geo.py`（T0/T1/T2/T4/T5，28 项，退出码 0 = 全过）

## 零、能力清单（全量扫描结果）

| 编号 | 能力点 | 规范 |
|------|--------|------|
| A1 | frontmatter 八字段齐全，name==slug==tri-geo（kebab-case） | 约束 1/2 |
| A2 | version SemVer；SKILL==CHANGELOG==tests==_meta 四件套一致 | 约束 10/12/14、R3 |
| A3 | description 含「支持独立安装，含上游依赖检测三态逻辑」 | 约束 2 |
| A4 | 引擎白名单 8 个：deepseek/doubao/kimi/zhipu/wenxin/yuanbao/tongyi/baidu_ai | 输入契约 |
| B1 | 强制执行契约置顶 + 最高优先级 + 激活语义 | 约束 3 |
| B2 | 版本检查前置硬门（第零步）+ STUB 指针不内联 | 约束 22 |
| B3 | 禁捏造硬门（citation_check mismatch/unsourced → 退出码 3 不降级） | 契约 4 |
| B4 | 合规红线（writing_rules R9 → 退出码 3 打回） | 契约 5 |
| B5 | 评分来源规范 P3（脚本+证据路径+采样区间+文献环境） | 契约 6 |
| B6 | 快照追加不覆盖（--revision；--force 显式） | 契约 7 |
| B7 | 教训文件读写闭环（.tribro/tri-geo/lessons.md） | 契约 9、约束 23 |
| B8 | 结论置信标注三要素 | 契约 10、约束 27 |
| B9 | prompt 白名单 4 处，白名单外一律脚本化 | 契约 3 |
| C1 | 模式必填矩阵（validate_input REQUIRED_BY_MODE） | 输入契约 |
| C2 | URL 归一化（补 scheme / idna 校验 / 非法 → 退出码 2） | 输入契约 |
| C3 | engines 白名单外 → 退出码 2；cn_fit 默认四引擎 | 输入契约 |
| C4 | 上游依赖检测三态（A 直用 / B 引导补参 / C 讲解降级） | 约束 6 |
| D1 | M1 快检 60 秒结论卡（5 快指标 + 1 实测） | 模块矩阵 |
| D2 | M2 双轨评分 + veto（NO_CONTENT block / CRAWLER_BLOCKED_ALL cap60） | 模块矩阵 |
| D3 | M3 重写打回闭环（≤2 轮，仍不达标降级草稿+人工确认=停车态） | 模块矩阵 |
| D4 | M3+ CN-Fit 引擎 RAG 偏好适配 + 实测验证 | 模块矩阵 |
| D5 | M4 技术基建（robots/llms.txt/JSON-LD/SSR） | 模块矩阵 |
| D6 | M5 渠道矩阵（prompt 条目③，输入 M2 评分 JSON） | 模块矩阵 |
| D7 | M6 快照 delta + pattern 沉淀 | 模块矩阵 |
| D8 | 站内信号五维权重（40/20/15/15/10）与可引用性五维（30/25/20/15/10） | scoring-spec |
| D9 | 爬虫判定仅采信公开 UA（Bytespider/Baiduspider/360Spider/Sogou/Yisou） | scoring-spec |
| D10 | 实测波动区间由采样 min/max 得出，NEVER 预设；样本空不记 0 分 | scoring-spec |
| E1 | 自检句含模式/触发源/目标/引擎/版本门/参数校验/教训/脚本链 | 约束 5 |
| E2 | 独立领域入口定位：不认领 L2、用户显式调用激活 | 职责边界 |
| F1 | 证据落盘 .tribro/tri-geo/raw/ + .geo-snapshots/（目录自动创建） | 落盘规则、R2 |
| F2 | 报告分数带证据路径；report_build 模板缺占位符即失败 | 评分与报告 |
| F3 | NEVER 生成 LICENSE/.gitignore | 约束 11 |
| F4 | 教训/快照/实测回答路径与文档声明一致（R0-3） | 落盘规则 |
| G1 | 不做传统 SEO / 海外引擎执行 / 风控规避 / 灰产手段 | 职责边界 |
| G2 | 与 tri-article/tri-coding 边界（只产重写稿与建议，不代办） | 职责边界 |
| G3 | 事实源指针（scoring-spec / models-cn / scripts） | 职责边界 |
| H1 | 同输入逐字节可复现（--stamp 默认关闭） | 质量标准 |
| H2 | references 装配顺序 + grep 模式 + 同名覆盖优先级 | 约束 25 |
| H3 | 目录结构与磁盘 diff 一致 | 约束 15 |
| H4 | T3 双站点实测（人工，需真机）：脚本分 vs 人工评估偏差 ≤10 分 | 设计指南 §4.3 |
| H5 | T6 国内四引擎实测（人工，需真机）：M3+ 产出对 4 引擎各 ≥1 组 prompt | 设计指南 §4.3 |

## 用例矩阵

| 用例 | 对应能力点 | 方式 | 通过判据 |
|------|-----------|------|---------|
| TC-01 | A1/A2/A3 | 脚本（verify T0-01~03） | 四件套版本一致；frontmatter 齐全 |
| TC-02 | B2/H3/F3 | 脚本（T0-04）+ 人工 | schema 六套合法；无 LICENSE/.gitignore；STUB 指针存在 |
| TC-03 | C1/C2/C3 | 脚本（T1-01~03） | 合法输入 0 / 缺必填 1 / 非法 2 |
| TC-04 | D1/D8 | 脚本（T1-04~06, T2-01~02） | 优样本分 > 劣样本分；同输入逐字节一致 |
| TC-05 | B4/D3 | 脚本（T4-01~02） | 优稿 pass；劣稿 redline=true 退出码 3 |
| TC-06 | B3/B5 | 脚本（T5-01~03） | 真实来源过；捏造/无来源 → 3 |
| TC-07 | D7/B6 | 脚本（T1-12~14） | append 成功；--revision 生效；delta 可算 |
| TC-08 | D10/F2 | 脚本（T1-10~11, T1-15~16） | 提及判定正确；采样区间存在；报告无残留占位符 |
| TC-09 | E1/E2 | 人工 | 自检句逐字段可声明；独立激活路径走通 |
| TC-10 | C4 | 人工 | 三态各演练一次：直用/补参/讲解 |
| TC-11 | D2 | 人工 | 构造无正文页 → NO_CONTENT 退出码 2；全爬虫封禁 → cap60 退出码 1 |
| TC-12 | D4/H5 | 人工（真机） | 四引擎各 ≥1 组 prompt 实测，判定 JSON 附回答证据路径 |
| TC-13 | D5/D6 | 人工 | M4 输出可被 M5 消费；渠道计划每项有评分依据 |
| TC-14 | B7/F4/G1-G3/H2 | 人工 | lessons.md 闭环三动作；落盘路径与声明一致；装配顺序可检索 |
| TC-15 | H4 | 人工（真机） | 2 个不同行业中文站 L2 全流程，偏差 ≤10 分 |
| TC-16 | A2/R5 | 人工 | 任意文件改动后四件套 + CHANGELOG + README 联动复查 |

> 人工用例执行后 MUST 将结果与教训追加至 `.tribro/tri-geo/lessons.md`（空泛内容禁写入）。
