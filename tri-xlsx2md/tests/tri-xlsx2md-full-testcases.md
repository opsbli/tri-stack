---
name: tri-xlsx2md-full-testcases
description: tri-xlsx2md 全场景全能力测试用例（审计版）——覆盖四阶段管道、三档降级链、保真度报告关键数据、双格式兼容（.xlsx/.xls/WPS）、边界约束、合规与版本检查。基于 tri-xlsx2md v1.3.5。
version: 1.3.5
---

# tri-xlsx2md 全场景全能力测试用例

> 基于 **tri-xlsx2md v1.0.1**。分组：T1 管道冒烟 / T2 降级链 / T3 保真度与报告 / T4 边界约束 / T5 合规 / T6 版本检查。
> 执行约定：`SKILL_DIR` = 本 skill 安装目录；`FIXTURE` = 临时测试目录。

## 能力清单扫描（用例与能力对齐）

| 能力 | 来源 | 覆盖用例 |
|---|---|---|
| 门A 预检分级 | `scripts/preflight.py` | T1.1–T1.4, T4.1–T4.3 |
| 门B 后端探测与决策 | `scripts/detect_backends.py` | T1.5, T2.1–T2.3 |
| 门C 结构降维转换执行指导 | SKILL.md + `references/backends.md` | T1.6, T2.2 |
| 门D 质量校验与报告 | `scripts/quality_check.py` | T1.7, T3.1–T3.6 |
| 双格式兼容（.xlsx/.xls/WPS） | SKILL.md + `references/backends.md` | T1.2, T4.3 |
| 保真度分级契约 | `references/fidelity-spec.md` | T3.1–T3.4 |
| 降级链 | SKILL.md 契约 6 | T2.1–T2.4 |
| 诚实边界（加密/结构降维/编造禁令） | SKILL.md 契约 2/5/11 | T4.1–T4.4 |
| 上游依赖检测三态 | SKILL.md §上游依赖检测 | T1.8, T5.1 |
| 版本检查四态 | `scripts/check_update.py` | T6.1–T6.4 |

---

## T1 管道冒烟（四阶段全链路）

### T1.1 .xlsx 简单表预检 → L0
- **前置**：openpyxl 生成 3 工作表纯数据 .xlsx（每表 5 行 × 4 列）
- **动作**：`python scripts/preflight.py --xlsx <FIXTURE>/sample.xlsx --json`
- **断言**：`ok=true`；`file_type="xlsx"`；`grade_suggestion="L0"`；`sheet_count=3`；`encrypted=false`；`formula_cells=0`；`merged_cells=0`

### T1.2 .xls 旧格式预检 → L1
- **前置**：xlwt 生成 .xls（或 WPS 另存 .xls）
- **动作**：同 T1.1
- **断言**：`file_type="xls"`；`old_format=true`；`grade_suggestion="L1"`；`risks` 含「旧二进制格式」

### T1.3 含公式/合并单元格预检 → L1
- **前置**：openpyxl 生成含公式（`=SUM(...)`）与合并单元格的 .xlsx
- **断言**：`formula_cells>0`；`merged_cells>0`；`grade_suggestion="L1"`；`risks` 含「公式」「合并单元格」

### T1.4 超大文件预检 → L1
- **前置**：>10MB 或估算 >100k 行的 .xlsx
- **断言**：`oversized=true`；`grade_suggestion="L1"`；`risks` 含「超大」

### T1.5 后端探测决策
- **动作**：`python scripts/detect_backends.py --grade L0 --type xlsx --json`
- **断言**：`plan.grade="L0"`；本地已装 openpyxl 时 `plan.selected="openpyxl"` 且 `halted=false`；缺失后端均带 `install` 指引；`--type xls` 时 L0 首选为 xlrd

### T1.6 门C 转换执行
- **动作**：按 `references/backends.md` §三 已验证命令执行选定后端
- **断言**：产出 `<同名>.md` 非空；每工作表一个 `## Sheet <名>` 块；空工作表标注「（空工作表）」；合并单元格展开为左上角值 + 其余空

### T1.7 门D 报告生成（用户硬要求）
- **动作**：`python scripts/quality_check.py --xlsx <FIXTURE>/sample.xlsx --md <FIXTURE>/sample.md --backend openpyxl --grade L0 --json`
- **断言**：report.md 生成；「关键数据（必读）」段含**单元格覆盖率、工作表数对比**、行数对比、置信度、后端/档位、文件类型/源提取、耗时、降级轨迹全部字段；`report_path` 正确

### T1.8 独立运行入口（三态）
- **断言**：无 tri-intent 时提示引导安装（模式 B）；拒绝后声明降级（模式 C）继续执行；有可用快照时读 §三（模式 A）

## T2 降级链

### T2.1 首选缺失自动降档
- **前置**：grade=L0 但 openpyxl 未装（模拟）
- **断言**：`plan.selected` 落到可用后端（markitdown），`fallback_chain` 含 xlrd

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
- **前置**：.xlsx 简单表 + openpyxl 转换（冒烟实测：单元格覆盖 100%）
- **断言**：`confidence="A"`；`reasons` 含「≥ 95%」

### T3.2 B 级判定
- **前置**：覆盖率被构造在 85–95% 区间（删 MD 部分工作表）
- **断言**：`confidence="B"`；报告列出缺失工作表

### T3.3 C 级判定（低覆盖）
- **前置**：MD 只保留源一半单元格（覆盖 <85%）
- **断言**：`confidence="C"`；报告醒目警示 + 升档建议

### T3.4 空表不编造
- **前置**：源文件无非空单元格（空表）+ 空 MD
- **断言**：单元格覆盖率 = 1.0；`confidence="A"` 或按异常降级；NEVER 出现编造数值

### T3.5 异常检测
- **构造**：MD 含 U+FFFD / 空文件 / 工作表缺失
- **断言**：`anomalies` 逐项命中；命中即 C 级

### T3.6 工作表数对比
- **构造**：MD 缺一个 `## Sheet` 块
- **断言**：`sheet_match=false`；`anomalies` 含「工作表缺失」；至少 B 级并写明原因

## T4 边界约束（诚实声明铁律）

### T4.1 加密 .xlsx 阻断
- **前置**：OOXML 加密 .xlsx（EncryptionInfo）
- **断言**：`grade_suggestion="BLOCK"`；`ok=false`；提示合法解密，NEVER 破解

### T4.2 加密 .xls 阻断
- **前置**：BIFF FILEPASS 加密 .xls
- **断言**：`grade_suggestion="BLOCK"`；`ok=false`；提示合法解密，NEVER 破解

### T4.3 WPS 兼容
- **前置**：WPS 生成的 .xlsx/.xls
- **断言**：魔数判定为 xlsx/xls 正常预检；转换后单元格覆盖 ≥95% 或如实报告降级

### T4.4 结构降维诚实
- **断言**：公式默认取缓存值（公式语义丢失）、格式/图表/数据透视不转正文，报告与交付说明 MUST 显式告知，NEVER 声称无损

### T4.5 目录批量不静默
- **动作**：输入是目录
- **断言**：列清单并请求确认范围，NEVER 批量静默转换

## T5 合规

### T5.1 三态检测语义匹配
- **断言**：本 skill 为内容转换类（可降级）→ 三态含模式 C 降级声明，与类型匹配

### T5.2 MECE 边界
- **断言**：仅认领 I08·xlsx2md；语言翻译/其它格式转换归 tri-content；Excel 操作归内置 xlsx skill；与 tri-pdf2md 无重叠（L3 子意图区分）

### T5.3 版本一致性
- **断言**：SKILL.md `version` == CHANGELOG 置顶 `[1.3.5]` == 本文件 frontmatter `version` == `_meta.json` `version`

### T5.4 代码版权
- **断言**：skill 包内无任何后端源码副本；后端均以外部调用方式使用；报告可注明许可证口径

### T5.5 落盘位置
- **断言**：用户成果物落用户输出目录（非 .tribro/）；过程 JSON 落 `.tribro/xlsx2md/<命名>/`；无 LICENSE/.gitignore

## T6 版本检查

### T6.1 A 态放行
- **动作**：`python scripts/check_update.py --slug tri-xlsx2md --json`（网络正常且已是最新）
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
- **断言**：SKILL.md §版本检查与更新机制 ≤30 行，指向 `tri-forge/references/version-check-spec.md`，无内联细则

---

## T7 真实格式样本固化（anydoc 迁移 · 2026-09-08）

> 样本固化于 `tests/samples/`（源：anydoc-main 真实 fixture，见 `.tribro/migration-test-20260908/`）。
> 执行方式：对每个样本跑 `python scripts/preflight.py --xlsx tests/samples/<样本> --json` 并按门B→门C→门D 全链验证。

| 样本 | 覆盖点 | 关键断言 |
|---|---|---|
| `sheet.xlsx` | L0 基线 | `grade_suggestion="L0"`；anydoc 转 MD 非空 |
| `handmade-merged.xlsx` | 合并单元格 | GridBuilder 网格不变量（列永不错位） |
| `sheet.xls` | .xls 直读 | anydoc BIFF 解析，免 LibreOffice 中转 |
| `handmade-sheet.xlsb` | .xlsb 直读 | 二进制格式免中转 |
| `sample.xlsm` | 宏工作簿 | 族识别正常 |
| `handmade-quoted.csv` | CSV 引号转义 | RFC 4180 引号字段保真 |
| `handmade-semicolon.csv` | CSV 分号分隔 | 多分隔符自动探测 |
| `handmade-utf16.csv` | CSV UTF-16 | 多编码自动探测 |

---

## 执行记录

| 日期 | 用例 | 结果 | 备注 |
|---|---|---|---|
| 2026-08-24 | T1.1 / T1.5 / T1.7 / T3.1 / T4.1 / T4.2 | 全过 | tri-forge 门②生成时冒烟实测（.xlsx 简单表 / 后端探测 / 加密 BLOCK 路径） |
