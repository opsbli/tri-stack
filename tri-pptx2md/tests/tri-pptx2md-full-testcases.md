---
name: tri-pptx2md-full-testcases
description: tri-pptx2md 全场景全能力测试用例（审计版）——覆盖四门管道、四档降级链、保真度报告关键数据、双格式兼容、边界约束、合规与版本检查。基于 tri-pptx2md v1.4.5。
version: 1.4.5
---

# tri-pptx2md 全场景全能力测试用例

> 基于 **tri-pptx2md v1.0.0**。分组：T1 管道冒烟 / T2 降级链 / T3 保真度与报告 / T4 边界约束 / T5 合规 / T6 版本检查。
> 执行约定：`SKILL_DIR` = 本 skill 安装目录；`FIXTURE` = 临时测试目录。

## 能力清单扫描（用例与能力对齐）

| 能力 | 来源 | 覆盖用例 |
|---|---|---|
| 门A 预检分级 | `scripts/preflight.py` | T1.1–T1.3, T4.1, T4.2 |
| 门B 后端探测与决策 | `scripts/detect_backends.py` | T1.4, T2.1–T2.3 |
| 门C 结构降维转换执行指导 | SKILL.md + `references/backends.md` | T1.5, T2.2 |
| 门D 质量校验与报告 | `scripts/quality_check.py` | T1.6, T3.1–T3.6 |
| 保真度分级契约 | `references/fidelity-spec.md` | T3.1–T3.4 |
| 降级链 | SKILL.md 契约 6 | T2.1–T2.4 |
| 双格式兼容（.pptx/.ppt/WPS） | SKILL.md + `references/backends.md` | T1.1, T1.2, T4.3 |
| 诚实边界（非 PPT 阻断/结构降维） | SKILL.md 契约 2/8 | T4.1, T4.4 |
| L3 付费确认 | SKILL.md 契约 7 | T4.5 |
| 上游依赖检测三态 | SKILL.md §上游依赖检测 | T1.7, T5.1 |
| 版本检查四态 | `scripts/check_update.py` | T6.1–T6.4 |

---

## T1 管道冒烟（四门全链路）

### T1.1 .pptx 预检 → L0
- **前置**：python-pptx 生成的 3 页纯文本 .pptx（含标题+正文）
- **动作**：`python scripts/preflight.py --ppt <FIXTURE>/sample.pptx --json`
- **断言**：`ok=true`；`file_type="pptx"`；`grade_suggestion="L0"`；`slide_count=3`；`old_format=false`

### T1.2 .ppt 预检 → PPT（旧格式）
- **前置**：OLE 复合文档头（D0CF11E0）的 .ppt 文件
- **动作**：同 T1.1
- **断言**：`file_type="ppt"`；`old_format=true`；`grade_suggestion="PPT"`；`risks` 含「LibreOffice」

### T1.3 复杂版式预检 → L1
- **前置**：.pptx 含 ≥5 张图片或备注页占比 ≥50%
- **断言**：`grade_suggestion="L1"`；`risks` 含「复杂版式信号」

### T1.4 后端探测决策
- **动作**：`python scripts/detect_backends.py --grade L0 --json`
- **断言**：`plan.grade="L0"`；本地已装 python-pptx/markitdown 时 `plan.selected` 非空且 `halted=false`；缺失后端均带 `install` 指引

### T1.5 门C 转换执行
- **动作**：按 `references/backends.md` §三 已验证命令执行选定后端
- **断言**：产出 `<同名>.md` 非空且每页一个 `## Slide N` 块；图片后端输出 assets/ 时 MD 引用与文件对应

### T1.6 门D 报告生成（用户硬要求）
- **动作**：`python scripts/quality_check.py --ppt <FIXTURE>/sample.pptx --md <FIXTURE>/sample.md --backend python-pptx --grade L0 --json`
- **断言**：report.md 生成；「关键数据（必读）」段含**页覆盖率、文本召回率、丢失率**、置信度、后端/档位、页数/耗时、图片资产、降级轨迹全部字段；`report_path` 正确

### T1.7 独立运行入口（三态）
- **断言**：无 tri-intent 时提示引导安装（模式 B）；拒绝后声明降级（模式 C）继续执行；有可用快照时读 §三（模式 A）

## T2 降级链

### T2.1 首选缺失自动降档
- **前置**：grade=L0 但 python-pptx 未装
- **断言**：`plan.selected` 落到可用后端（markitdown），`fallback_chain` 含其余可用项

### T2.2 执行失败降档重试
- **模拟**：选定后端执行抛错/超时
- **断言**：沿 L1→L0 链降级重试；轨迹写入报告「降级轨迹」字段；NEVER 空手交付

### T2.3 全缺失停机
- **模拟**：四后端全部不可用
- **断言**：`halted=true`；输出安装指引；停在预检报告态

### T2.4 C 级升档重转
- **前置**：L0 结果置信度 C 且用户要求重转
- **断言**：建议升档 L1（沿链反向），不重复同档同后端

## T3 保真度与报告（核心 · 用户硬要求）

### T3.1 A 级判定
- **前置**：3 页纯文本 .pptx + python-pptx 转换（MD 含全部 3 个 Slide 块）
- **断言**：`page_coverage=1.0`；`confidence="A"`；`reasons` 含「≥ 95%」

### T3.2 B 级判定（召回区间）
- **前置**：召回率被构造在 85–95% 区间（删 MD 部分段落）
- **断言**：`confidence="B"`；报告列出缺页/复核项

### T3.3 C 级判定（低覆盖/低召回）
- **前置**：MD 只保留一半 Slide 块（页覆盖 <90%）
- **断言**：`confidence="C"`；`missing_pages` 非空；报告醒目警示 + 升档建议

### T3.4 纯图片 PPT 不编造
- **前置**：无文本 .pptx + 任意 MD
- **断言**：文本召回率/丢失率 =「不适用（无文本）」；NEVER 出现编造数值；置信度按页覆盖率判定

### T3.5 异常检测
- **构造**：MD 含 U+FFFD / 空文件 / 缺页 / 围栏不成对
- **断言**：`anomalies` 逐项命中；命中即 C 级

### T3.6 结构对比
- **断言**：PPT 有图片而 MD 无图片引用 → 至少 B 级并写明原因；PPT 有备注而 MD 无备注引用块 → 至少 B 级

### T3.7 跨页粘连不产生伪 bigram（v1.4.5）
- **构造**：3 页纯文本 .pptx + **手工一字不差**抄写的 MD（含 `## Slide N` 锚点）
- **断言**：`recall == 1.0` 且 `confidence == "A"`；NEVER 因跨页边界出现 <100%（修复前为 0.9286/B）
- **回归脚本**：`python scripts/verify_recall.py`

### T3.8 全角数字计入统计（v1.4.5）
- **构造**：源页含全角数字（`２０２６`）；MD 变体 A 全保留、变体 B 删掉全角数字
- **断言**：`source_total_chars` 含 NFKC 折叠后的半角数字；变体 B 的 `recall` 显著低于 1.0（修复前恒为 1.0）

### T3.9 低召回优先判 C（v1.4.5）
- **构造**：10 页 PPT + 每页只保留标题的 MD（页覆盖 100%，召回 <85%）
- **断言**：`confidence == "C"`；理由文案与实际命中条件一致，NEVER 出现「45.8%（85–95%）」这类硬性区间表述

### T3.10 MD 多写 Slide 块（v1.4.5）
- **构造**：源 5 页，MD 写 12 个 `## Slide` 块
- **断言**：`md_extra_blocks == 7`；`anomalies` 含「超过源」；`confidence == "C"`（修复前 pc=1.0、零告警、A）

## T4 边界约束（诚实声明铁律）

### T4.1 非 PPT 文件阻断
- **前置**：纯文本 .txt / 随机字节文件
- **断言**：`file_type="unknown"`；`grade_suggestion="BLOCK"`；`ok=false`；提示确认输入

### T4.2 目录批量不静默
- **动作**：输入是目录
- **断言**：列清单并请求确认范围，NEVER 批量静默转换

### T4.3 WPS 兼容
- **前置**：WPS 生成的 .pptx/.ppt
- **断言**：魔数判定正常（.pptx=PK / .ppt=D0CF11E0）；走对应档位；WPS 特有版式以图片资产保留

### T4.4 结构降维诚实
- **断言**：动画/过渡/母版/精确排版在报告中显式声明「必然丢失」；图表/SmartArt 提取为 assets/ 不转正文

### T4.5 L3 付费确认
- **模拟**：需要 LLM 视觉 API/商业 API
- **断言**：先说明成本与数据外发风险并取得确认，NEVER 未经确认调用

## T5 合规

### T5.1 三态检测语义匹配
- **断言**：本 skill 为内容转换类（可降级）→ 三态含模式 C 降级声明，与类型匹配

### T5.2 MECE 边界
- **断言**：仅认领 I08·pptx2md；语言翻译/其它格式转换归 tri-content；PPT 操作归内置 pptx skill；PDF→MD 归 tri-pdf2md；不与 tri-translate 重叠

### T5.3 版本一致性
- **断言**：SKILL.md `version` == CHANGELOG 置顶 `[1.4.5]` == 本文件 frontmatter `version` == `_meta.json` `version`

### T5.4 代码版权
- **断言**：skill 包内无任何后端源码副本；GPL/MPL 后端仅以外部调用方式使用；报告可注明许可证口径

### T5.5 落盘位置
- **断言**：用户成果物落用户输出目录（非 .tribro/）；过程 JSON 落 `.tribro/pptx2md/<命名>/`；无 LICENSE/.gitignore

## T6 版本检查

### T6.1 A 态放行
- **动作**：`python scripts/check_update.py --slug tri-pptx2md --json`（网络正常且已是最新）
- **断言**：`state="A"`，退出码 0，放行

### T6.2 B 态离线降级
- **模拟**：断网
- **断言**：`state="B"`，标注「版本校验未完成（离线）」后继续

### T6.3 C 态通道降级
- **模拟**：API 404/响应无效
- **断言**：`state="C"`，标注「通道不可用」后继续

### T6.4 BLOCK 阻断
- **模拟**：升级后校验失败/签名不一致
- **断言**：退出码 ≥20；绝对禁止执行；输出 `block_code` 恢复指引

### T6.5 瘦指针 STUB
- **断言**：SKILL.md §版本检查与更新机制 ≤30 行，指向 `references/version-check-spec.md`，无内联细则

---

## T7 真实格式样本固化（anydoc 迁移 · 2026-09-08）

> 样本固化于 `tests/samples/`（源：anydoc-main 真实 fixture，见 `.tribro/migration-test-20260908/`）。
> 执行方式：对每个样本跑 `python scripts/preflight.py --ppt tests/samples/<样本> --json` 并按门B→门C→门D 全链验证。

| 样本 | 覆盖点 | 关键断言 |
|---|---|---|
| `handmade-order.pptx` | L0 基线 | `grade_suggestion="L0"`；anydoc 转 MD 非空 |
| `handmade-sparsenotes.ppt` | 演讲者备注稀疏 | 备注策略生效（缺失备注不编造） |
| `handmade-multimaster.ppt` | .ppt 旧格式直读 | anydoc 直读，免 LibreOffice 中转 |
| `sample.pptm` | 宏演示文稿 | `detected_type` 族识别正常 |
| `sample.ppsx` / `sample.ppsm` | 放映格式 | 全族扩展名识别（frontmatter 七扩展） |
| `sample.pps` / `sample.pot` | 旧版放映/模板 | 旧格式直读路径 |
| （对照）`pres.ppt`（464KB，未固化） | 大体积 .ppt | 仅驻留 `.tribro/migration-test-20260908/samples/`，避免发布包膨胀 |

---

## 执行记录

| 日期 | 用例 | 结果 | 备注 |
|---|---|---|---|
| 2026-08-24 | T1.1 / T1.2 / T1.4 / T1.6 / T3.1 / T4.1 | 全过 | tri-forge 门②生成时冒烟实测（.pptx / .ppt / 非 PPT 三路径） |
