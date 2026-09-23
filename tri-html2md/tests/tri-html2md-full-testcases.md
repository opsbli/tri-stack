---
name: tri-html2md-full-testcases
description: tri-html2md 全场景全能力测试用例（审计版）——覆盖四阶段管道、两档降级链、保真度报告关键数据、编码检测、边界约束、合规与版本检查。基于 tri-html2md v1.3.5。
version: 1.3.5
---

# tri-html2md 全场景全能力测试用例

> 基于 **tri-html2md v1.0.0**。分组：T1 管道冒烟 / T2 降级链 / T3 保真度与报告 / T4 边界约束 / T5 合规 / T6 版本检查。
> 执行约定：`SKILL_DIR` = 本 skill 安装目录；`FIXTURE` = 临时测试目录。

## 能力清单扫描（用例与能力对齐）

| 能力 | 来源 | 覆盖用例 |
|---|---|---|
| 门A 预检分级 | `scripts/preflight.py` | T1.1–T1.4, T4.1, T4.2 |
| 门B 后端探测与决策 | `scripts/detect_backends.py` | T1.5, T2.1–T2.3 |
| 门C 转换执行指导 | SKILL.md + `references/backends.md` | T1.6, T2.2 |
| 门D 质量校验与报告 | `scripts/quality_check.py` | T1.7, T3.1–T3.6 |
| 编码检测 | `scripts/preflight.py` | T1.2, T4.2 |
| 保真度分级契约 | `references/fidelity-spec.md` | T3.1–T3.4 |
| 降级链 | SKILL.md 契约 6 | T2.1–T2.4 |
| 诚实边界（编码/无可见文本/编造禁令） | SKILL.md 契约 2/5 | T4.1–T4.3 |
| 上游依赖检测三态 | SKILL.md §上游依赖检测 | T1.8, T5.1 |
| 版本检查四态 | `scripts/check_update.py` | T6.1–T6.4 |

---

## T1 管道冒烟（四阶段全链路）

### T1.1 简单 HTML 预检 → L0
- **前置**：纯文本 HTML（标题 + 段落，无表格无脚本）
- **动作**：`python scripts/preflight.py --html <FIXTURE>/simple.html --json`
- **断言**：`ok=true`；`grade_suggestion="L0"`；`decode_ok=true`；`file_type_ok=true`；`table_count=0`

### T1.2 编码检测（utf-8 与 gbk）
- **前置**：中文 HTML 分别存为 utf-8 与 gbk 编码
- **动作**：同 T1.1
- **断言**：utf-8 文件 `encoding="utf-8"`；gbk 文件 `encoding="gbk"`；两者均 `decode_ok=true`、无乱码风险

### T1.3 复杂 HTML 预检 → L1
- **前置**：HTML 含 ≥3 个表格或 ≥10 个 img/script/style
- **断言**：`grade_suggestion="L1"`；`risks` 含「复杂 HTML 信号」

### T1.4 非 HTML 文件 → BLOCK
- **前置**：`.txt` 文件
- **断言**：`grade_suggestion="BLOCK"`；`ok=false`；提示仅支持 .html/.htm

### T1.5 后端探测决策
- **动作**：`python scripts/detect_backends.py --grade L0 --json`
- **断言**：`plan.grade="L0"`；本地已装 markitdown 时 `plan.selected` 非空且 `halted=false`；缺失后端均带 `install` 指引

### T1.6 门C 转换执行
- **动作**：按 `references/backends.md` §三 已验证命令执行选定后端
- **断言**：产出 `<同名>.md` 非空；图片后端输出 assets/ 时 MD 引用与文件对应

### T1.7 门D 报告生成（用户硬要求）
- **动作**：`python scripts/quality_check.py --html <FIXTURE>/simple.html --md <FIXTURE>/simple.md --backend markitdown --grade L0 --json`
- **断言**：report.md 生成；「关键数据（必读）」段含**文本召回率、丢失率**、噪声率、置信度、后端/档位、文件大小/耗时、图片资产、降级轨迹全部字段；`report_path` 正确

### T1.8 独立运行入口（三态）
- **断言**：无 tri-intent 时提示引导安装（模式 B）；拒绝后声明降级（模式 C）继续执行；有可用快照时读 §三（模式 A）

## T2 降级链

### T2.1 首选缺失自动降档
- **前置**：grade=L0 但 markitdown 未装（本地现状）
- **断言**：`plan.selected` 落到可用后端（html2text/beautifulsoup4），`fallback_chain` 含其余 L0 后端

### T2.2 执行失败降档重试
- **模拟**：选定后端执行抛错/超时
- **断言**：沿 L1→L0 链降级重试；轨迹写入报告「降级轨迹」字段；NEVER 空手交付

### T2.3 全缺失停机
- **模拟**：五后端全部不可用
- **断言**：`halted=true`；输出安装指引；停在预检报告态

### T2.4 C 级升档重转
- **前置**：L0 结果置信度 C 且用户要求重转
- **断言**：建议升档 L1（沿链反向），不重复同档同后端

## T3 保真度与报告（核心 · 用户硬要求）

### T3.1 A 级判定
- **前置**：简单 HTML + markitdown 转换（冒烟实测：文本召回率 100%）
- **断言**：`confidence="A"`；`reasons` 含「≥ 95%」

### T3.2 B 级判定
- **前置**：召回率被构造在 85–95% 区间（删 MD 部分段落）
- **断言**：`confidence="B"`；报告列出复核项

### T3.3 C 级判定（低召回）
- **前置**：MD 只保留 HTML 一半内容（召回 <85%）
- **断言**：`confidence="C"`；报告醒目警示 + 升档建议

### T3.4 无可见文本不编造
- **前置**：纯脚本/纯样式 HTML（无可见文本）+ 任意 MD
- **断言**：文本召回率/丢失率 =「不适用（无可见文本）」；`confidence="C"`；NEVER 出现编造数值

### T3.5 异常检测
- **构造**：MD 含 U+FFFD / 锟斤拷 / 空文件 / 围栏不成对 / script 内容泄漏进正文
- **断言**：`anomalies` 逐项命中；命中即 C 级

### T3.6 结构对比
- **断言**：HTML 有表格而 MD 无表格语法 → 至少 B 级并写明原因；HTML 有图片/链接而 MD 无对应引用 → 至少 B 级

## T4 边界约束（诚实声明铁律）

### T4.1 编码不可解阻断
- **前置**：随机二进制字节伪装 .html（候选解码全部失败）
- **断言**：`grade_suggestion="BLOCK"`；`ok=false`；提示提供正确编码，NEVER 猜测解码

### T4.2 meta charset 声明优先
- **前置**：HTML 头含 `<meta charset="gbk">` 且正文为 gbk 字节
- **断言**：`encoding="gbk"`（meta 声明优先于候选探测）

### T4.3 目录批量不静默
- **动作**：输入是目录
- **断言**：列清单并请求确认范围，NEVER 批量静默转换

### T4.4 图片提资产不转正文
- **前置**：HTML 含 `<img>`
- **断言**：图片提取为 assets/ 资产 + MD 保留引用，NEVER 试图转成 MD 正文

## T5 合规

### T5.1 三态检测语义匹配
- **断言**：本 skill 为内容转换类（可降级）→ 三态含模式 C 降级声明，与类型匹配

### T5.2 MECE 边界
- **断言**：仅认领 I08·html2md；语言翻译/其它格式转换归 tri-content；HTML 抓取/渲染归浏览器工具；PDF→MD 归 tri-pdf2md；不与 tri-translate 重叠

### T5.3 版本一致性
- **断言**：SKILL.md `version` == CHANGELOG 置顶 `[1.3.5]` == 本文件 frontmatter `version` == `_meta.json` `version`

### T5.4 代码版权
- **断言**：skill 包内无任何后端源码副本；GPL 后端（pandoc）仅以外部 CLI 调用方式使用；报告可注明许可证口径

### T5.5 落盘位置
- **断言**：用户成果物落用户输出目录（非 .tribro/）；过程 JSON 落 `.tribro/html2md/<命名>/`；无 LICENSE/.gitignore

### T5.6 无 L2/L3 档
- **断言**：`detect_backends.py` 的 `--grade` 仅接受 L0/L1；SKILL.md 明确声明「无 L2/L3（HTML 已有语义结构，不需要 OCR 档）」

## T6 版本检查

### T6.1 A 态放行
- **动作**：`python scripts/check_update.py --slug tri-html2md --json`（网络正常且已是最新）
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

## T7 真实格式样本固化（2026-09-08）

> 样本固化于 `tests/samples/`（anydoc 迁移测试同步产出；anydoc 不做 HTML，故本 skill 样本为手工构造的真实格式综合样本）。
> 执行方式：`python scripts/preflight.py --html tests/samples/real-sample.html --json` 并按门B→门C→门D 全链验证。

| 样本 | 覆盖点 | 关键断言 |
|---|---|---|
| `real-sample.html` | 综合真实格式 | CJK 中文保真；HTML 实体（`&amp;` `&lt;`）正确反转义；表格对齐；`<a href>` 锚点保留（collect_anchor_refs）；嵌套列表（ul>ol）；`<pre><code>` 代码块；`<blockquote>`；`<time>`/`<sup>` 语义标签合理降维 |

---

## 执行记录

| 日期 | 用例 | 结果 | 备注 |
|---|---|---|---|
| 2026-08-24 | T1.1 / T1.2 / T1.4 / T1.5 / T1.7 / T3.1 / T3.4 / T4.1 | 全过 | tri-forge 门②生成时冒烟实测（简单/复杂/无可见文本/编码不可解四路径） |
