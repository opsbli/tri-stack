# Changelog

本项目的所有重要变更都记录在本文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本管理遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.1.0] - 2026-09-20

### 新增

- **治理层门G（可选阶段）**：建库之后的持续保养能力——五个确定性脚本，全部仅依赖 Python 标准库。
  - `scripts/sync_incremental.py`：增量同步，mtime + sha256 双判据变更检测（`plan` / `apply` / `rebuild` 三模式，原子替换写盘）；确立「markdown 是真相、索引状态是缓存」原则，索引可随时删除重建。
  - `scripts/credibility_score.py`：内容可信度评分——五分量加权合成（来源可追溯 0.30 / 元数据完整 0.20 / 正文信息量 0.20 / 链接连通 0.15 / 时效 0.15），缺失分量**重归一化**而非按 0 计入，硬地板 0.05 只给「近乎空」或「已废弃」两类；附转载/衍生稿聚类（3-shingle Jaccard ≥0.70，簇内按 1/size 折权）。
  - `scripts/dedup_content.py`：内容级深度去重，补上 v1「转换产物不回溯去重」的缺口；小库走精确 Jaccard，超过 200 篇自动切换 minhash + LSH 分桶候选（`--apply` 写 `dup_group`）。
  - `scripts/lifecycle_govern.py`：生命周期状态机（成长轨 seedling→budding→evergreen，衰减轨 stale→deprecated→archive）；`--plan` 出建议、`--apply` 写 `status`/`reviewed`，衰减终态 MUST 人工仲裁。
  - `scripts/lint_vault.py`：结构化体检 12 条规则（error/warning/info 分级），把 v1 单一的断链检测扩展为可机检规则表；`--strict` 时 error 级问题以退出码 3 阻断。
- **三份新 references**：`credibility-spec.md`（可信度与转载聚类规范）、`lifecycle-spec.md`（生命周期与增量同步规范）、`lint-rules.md`（体检规则集与门禁）；`frontmatter-spec.md` 增补治理字段 `reviewed` / `dup_group` / `untrusted` 并把 `status` 扩展为六态；`output-structure-spec.md` 登记 `.wiki-meta/` 新增产物。
- **硬约束缺口补齐**：新增 `## 知识装配顺序`（约束 25：五层装配 + 去重 + 覆盖优先级 + grep 模式）、`## 完成判据`（约束 24：六条可机械校验判据 + 停车态/结束态区分）、契约第 15 条结论置信标注（约束 27）、契约第 11 条不可信输入隔离铁律、契约第 12 条索引缓存铁律；进化契约补「教训文件读写闭环」并登记 `.tribro/wiki/lessons.md`。
- **契约新增条目**：治理层门G 可选且非静默（写入类动作先 plan 后确认）、增量更新边界细化（增量同步只管变更检测与索引重建，NEVER 承担新旧合并）。

### 变更

- 自检句字段扩展：新增「已读教训=<N 条/无文件>」与阶段枚举 `A–F/G`。
- 质量指标表新增「可信度（门G）」行，明确其为**启发式合成**、不参与 A/B/C 分级，仅作复核项排序依据。
- 质量标准表新增规则化体检、可信度可解释、治理非静默、完成判据外化、新模式落地七处同步五行。
- 触发时机新增「治理触发（门G 单独运行）」分支；职责边界新增治理层能力边界与 Not-Trigger 补充（不接手网页抓取与学术检索执行）。

### 已知边界

- 治理层为**可选阶段**，MUST 由用户显式触发或确认后执行，NEVER 静默运行写入类动作。
- 可信度权重与阈值为启发式初值，首次在真实知识库运行后应按分布校准（校准入口为脚本顶部常量，回写 `references/credibility-spec.md`）。
- v1 仍不支持源数据增量合并建库（仅全量重建 + 索引增量同步）。

## [1.0.1] - 2026-09-18

### 新增

- **职责边界补「不触发场景（Not-Trigger）」**（对齐全家族 skill 写作规范）：明确本 skill 不接手单文档格式转换（归 x2md 族）、语言翻译、知识库维护循环体与 RAG 检索执行，只做集合级知识库编排。

## [1.0.0] - 2026-08-24

### 新增

- 初版发布：六阶段管道（A 需求与信息架构确认 → B 源数据扫描预检分级与去重标记 → C 批量转换委派 x2md 族 → D 内容组织与 frontmatter 注入 → E MOC 链接与索引构建 → F 质量校验与交付报告）。
- 三道人工确认门：门① 信息架构（不可跳过）、门② 分类归置（可 `--auto`）、门③ MOC 链接（可 `--auto`）。
- 源数据只读铁律：全程零写操作，产物独立目录。
- 委派三态检测：installed / missing+同意安装 / missing+拒绝（部分降级，不整体失败）。
- 默认组织方法论 `topic-moc`（主题树 + MOC 双层），可选 `para` / `jd` / `moc-only`。
- 五脚本确定性管道：`scan_sources.py` / `convert_orchestrate.py` / `organize.py` / `index_build.py` / `quality_check.py`（仅标准库依赖）。
- 质量契约：覆盖率/组织完整度/断链率/链接密度/重复率/转换保真率聚合 + 置信度 A/B/C 分级；不可计算项显式「不适用」。
- frontmatter 强制元数据五必填字段（title/type/source/source_format/created）+ 数字花园状态标签（seedling/budding/evergreen）。
- 大文档原子化拆分（按 H2 切分 + 父页 ToC 聚合 + `split_from` 溯源）。
- 断链检测与标签聚合页自动生成。
- `.wiki-meta/build-manifest.json` 源→产物映射（v1.1 增量更新预留）。
- RAG 语料出口（`--rag`，Small-to-Big 父子分块 JSONL，数据供给层边界）。
- 版本检查机制（`check_update.py` + `version-check-spec.md`，家族同源）。
- 进化契约（反馈接收点/经验沉淀位/自我修订触发条件）。

### 变更

- （无——初版）

### 已知边界（v1）

- 仅支持全量构建，增量更新规划于 v1.1。
- epub/邮件/图片/音视频源格式跳过 + 报告（v1.1+ 候选）。
- 不执行站点部署与云发布（仅输出指引）。
