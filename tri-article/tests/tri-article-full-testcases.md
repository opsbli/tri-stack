---
---
name: tri-article-full-testcases
description: 基于 tri-article v1.4.1 全量扫描生成的覆盖全场景测试用例集，供人工审计。覆盖占位符/profile 机制、去AI化写作引擎、去AI化引擎委派（tri-humanize）、文末安装指引要素（TRI_INSTALL_NOTE）、产品植入开关、质量门禁、独立/接入两种模式、落盘规则，以及 hooks/index.py 脚本调用（add/dedup/search/edit_distance）等全部能力点。
version: 1.4.1
---

# tri-article 全场景测试用例

> 被测对象：`tri-article` v1.4.0（通用去AI化文章生成 skill；占位符+profile 驱动；去 AI 化改写委派 tri-humanize）
> 用例总数：**50**（文档层 36 + 脚本层 14）
> 生成时间：2026-08-23
> 审计方式：逐条对照预期结果独立判定（占位符替换与生成流程按 SKILL.md 步骤推演；质量门禁按 `references/de-ai-rules.md` §六 的 13 项清单核对；委派用例按 SKILL.md §去 AI 化引擎委派 三态判定；TC-S 系列须真实执行命令并比对 stdout JSON 与退出码）

---

## 零、能力清单（全量扫描结果）

| 组 | 能力点 | 规范出处 |
|----|--------|---------|
| A 元数据 | frontmatter 齐全、description 含「支持独立安装，含上游依赖检测两态逻辑」与委派 tri-humanize 说明 | 规范第二章 |
| B 强制执行契约 | 占位符替换前置、禁用词/视角/门禁、委派契约、NEVER 泄露隐私、NEVER 生成 LICENSE/.gitignore | 规范第三章 §3.2 |
| C 输入契约 | profile 字段映射、PRODUCT_ENABLED 关闭时不植入 | §输入契约 |
| D 核心方法论 | 去AI化引擎、选题轮转、质量门禁、产品植入、可扩展性 | §方法论 |
| D' 委派 | 去 AI 化改写委派 tri-humanize（HUMANIZE-EMBED）、三态检测、降级回退 | §去 AI 化引擎委派 |
| E 自检声明 | 「本次意图=…已读取profile…去 AI 化引擎=…」格式 | §3.2 |
| F 交付产物 | 文章 + profile.md 落盘 | §交付产物 |
| G 职责边界 | 不识别意图、不替用户发平台、委派决策由本 skill 持有、不与 tri-content 重叠 | §职责边界 |
| H 质量标准 | 去AI化/委派/实战/通用/合规五维 | §质量标准 |

---

## 一、占位符 / profile 机制（TC-P01~P08）

| 编号 | 场景 | 输入 | 预期 |
|------|------|------|------|
| TC-P01 | 首次运行 profile 缺失 | 无任何 profile | 进入初始化，反问必填项后落盘 `.tribro/tri-article/profile.md` |
| TC-P02 | profile 已存在 | `.tribro/tri-article/profile.md` 齐全 | 直接替换占位符执行，不重复反问 |
| TC-P03 | 必填项缺失 | profile 缺 `AUTHOR_PROFILE` | 仅反问缺失项，补齐后继续 |
| TC-P04 | 占位符全部替换 | 含 `{{AUTHOR_PROFILE}}` 等 | 最终文章无任何 `{{}}` 残留 |
| TC-P05 | DOMAIN_POOL 缺失 | profile 未配领域池 | 回退内置默认 6 领域，提示用户 |
| TC-P06 | LICENSE_STMT 缺失 | profile 未配声明 | 回退默认 MIT 声明 |
| TC-P07 | DISABLED_WORDS 缺失 | profile 未配禁用词 | 回退内置默认禁用词表 |
| TC-P08 | 重新配置指令 | 用户说「重新配置 tri-article」 | 清空/覆盖 profile，重新反问 |

## 二、去 AI 化写作引擎（TC-W01~W10）

| 编号 | 场景 | 输入 | 预期 |
|------|------|------|------|
| TC-W01 | 选题轮转 | 给定日期 | `index=(年+月+日)%len(DOMAIN_POOL)` 取对应领域 |
| TC-W02 | 类型不连续 | 上一篇为踩坑型 | 本次随机选非踩坑型 |
| TC-W03 | 去重检查 | history 已有同角度标题 | 换切入点 |
| TC-W04 | 禁用词命中 | 文章含「综上所述」 | 门禁否决，重写 |
| TC-W05 | 主观细节不足 | 全文 0 处主观判断 | 门禁否决（要求≥2处） |
| TC-W06 | 开头空泛 | 以「随着…发展」开头 | 门禁否决，换开头 |
| TC-W07 | 结尾机械总结 | 结尾带编号列表 | 门禁否决 |
| TC-W08 | 人称随机 | 生成前 | 四人称之一，不每次「我」 |
| TC-W09 | 结构模式轮换 | 上一篇模式A | 本次选模式B |
| TC-W10 | 代码可运行 | 含代码示例 | 完整片段+语言标注，非伪代码 |

## 三、去 AI 化引擎委派（TC-D01~D06）

> 依据 SKILL.md §去 AI 化引擎委派（tri-humanize · 横向委派）三态判定与委派流程推演。

| 编号 | 场景 | 输入 | 预期 |
|------|------|------|------|
| TC-D01 | 委派模式（A） | tri-humanize 可用，草稿完成 | 委派 HUMANIZE-EMBED 改写，返回仅终稿；声明「去 AI 化引擎=tri-humanize」 |
| TC-D02 | 引导安装（B 软降级） | tri-humanize 未安装 | 提示 `skillhub install tri-humanize`，回退内置 de-ai-rules 继续生成，声明降级；不硬阻断独立运行 |
| TC-D03 | 降级模式（C） | 用户拒绝安装 | 按内置 de-ai-rules 完成改写，声明「去 AI 化引擎=内置 de-ai-rules（降级）」 |
| TC-D04 | 委派时机 | 草稿撰写完成后 | 委派发生在质量门禁自查前；委派返回终稿后再跑 §4 门禁，命中即重写 |
| TC-D05 | 委派不改事实 | 草稿含具体数字/名称/日期 | 委派改写不增删事实（tri-humanize 铁律）；门禁后仍无禁用词、≥2 处主观细节 |
| TC-D06 | 对称双向检测 | tri-humanize 触发时机表 | tri-humanize 声明「tri-article 等下游委派」触发源（HUMANIZE-EMBED），任一端缺失都被发现 |

## 四、产品自然植入（TC-R01~R05）

| 编号 | 场景 | 输入 | 预期 |
|------|------|------|------|
| TC-R01 | 植入关闭 | `PRODUCT_ENABLED=false` | 文章不出现产品名 |
| TC-R02 | 植入开启-篇幅 | `PRODUCT_ENABLED=true` | 涉及产品 ≤3 句，占比 ≤5% |
| TC-R03 | 植入开启-语气 | 开启 | 无「快来下载」等推广语气/感叹号/emoji |
| TC-R04 | 植入开启-位置 | 开启 | 仅开头/中间/结尾 1 处 |
| TC-R05 | 一票否决 | 多处提及或割裂 | 重写 |

## 五、模式与边界（TC-M01~M05）

| 编号 | 场景 | 输入 | 预期 |
|------|------|------|------|
| TC-M01 | 独立运行 | 无 tri-intent | 标准模式直接生成 |
| TC-M02 | 接入 tri-intent | 快照路由指向本 skill | 读取 §三 后执行 |
| TC-M03 | 两态 B 引导 | 用户要路由但未装 tri-intent | 提示 `skillhub install tri-intent` |
| TC-M04 | 隐私泄露 | 人设含手机号 | NEVER 写入文章 |
| TC-M05 | LICENSE/.gitignore | 生成过程 | 全程不创建这两类文件 |

---

## 六、脚本调用用例 · `hooks/index.py`（TC-S01~S14）

> **被测脚本**：`hooks/index.py`（纯标准库）。以下用例均为**真实命令行调用**，需在临时工作目录执行，`--root` 统一指向 `./articles`。
> **通用前置（P0）**：`rm -rf ./articles`，随后按用例顺序执行；标注「依赖 TC-Sxx」的用例须先跑完前置用例。
> **判定方式**：比对 stdout 的 JSON 结构/字段 与进程退出码（`echo $?`）。

### 5.1 `add` — index.json 字段完整性（TC-S01~S04）

| 编号 | 场景 | 命令 | 预期 |
|------|------|------|------|
| TC-S01 | 首次 add 建索引 | `python hooks/index.py --root ./articles add --title "Electron 桌面开发的 3 个坑" --domain "Electron 桌面开发" --slug "electron-3-pits" --tags "Electron/性能优化" --path "articles/electron-桌面开发/20260801-electron-3-pits.md" --created_at "2026-08-01"` | 自动创建 `./articles/index.json`；stdout 为单条记录 JSON；退出码 `0` |
| TC-S02 | 记录字段完整性 | 同 TC-S01 的输出 | 记录 MUST 含全部 11 个字段：`id / title / slug / domain / tags[] / created_at / title_norm / title_hash / content_hash / path / status`；其中 `domain="electron-桌面开发"`（已 slug 化）、`tags=["Electron","性能优化"]`（按 `/` 拆分）、`title_norm="electron 桌面开发的 3 个坑"`（小写+去标点）、`title_hash` 为 64 位 hex、`status="done"`（默认值）、`content_hash=""`（未传时为空串） |
| TC-S03 | 省略 `--slug` 时自动派生 | `... add --title "FastAPI 依赖注入实测" --domain "后端架构"` | `slug` = `slugify(title)` = `fastapi-依赖注入实测`，且 `id == slug`；退出码 `0` |
| TC-S04 | 同 (slug, domain) 覆盖不追加 | 重跑 TC-S01 同参数但 `--path` 改为 `.../20260802-electron-3-pits.md`（依赖 TC-S01） | `index.json` 记录**总数不变**（原地替换而非追加），该条 `path` 更新为新值；退出码 `0` |

### 5.2 `dedup` — 硬/软/无重复三档（TC-S05~S09）

| 编号 | 场景 | 命令 | 预期 |
|------|------|------|------|
| TC-S05 | **hard** 硬重复 | `python hooks/index.py --root ./articles dedup --title "Electron 桌面开发的 3 个坑" --domain "Electron 桌面开发"`（依赖 TC-S01） | `{"duplicate": true, "level": "hard", "hard": [{title, path}], "soft": []}`；**退出码 `1`**（供脚本判定阻断） |
| TC-S06 | **soft** 软重复（slug 编辑距离 ≤2） | `... dedup --title "完全不同的标题啊" --domain "Electron 桌面开发" --slug "electron-3-pit"`（依赖 TC-S01） | `level="soft"`、`duplicate=true`、`hard=[]`、`soft` 命中 TC-S01 记录；**退出码 `0`**（仅提示换角度，不阻断） |
| TC-S07 | **none** 无重复 | `... dedup --title "另一个标题" --domain "后端架构" --slug "backend-xyz"` | `{"duplicate": false, "level": "none", "hard": [], "soft": []}`；退出码 `0` |
| TC-S08 | 硬重复优先级高于软重复 | 标题哈希命中 **且** 同域 slug 近似 | `level` MUST = `hard`（hard 优先），`soft` 数组可非空但不改变档位；退出码 `1` |
| TC-S09 | 跨域不触发软重复 | `... dedup --title "新标题" --domain "AI 工程" --slug "electron-3-pit"`（依赖 TC-S01） | 软重复仅在**同 domain** 内比对，故 `level="none"`；退出码 `0` |

### 5.3 `search` — 按 tag / domain / keyword 过滤（TC-S10~S12）

| 编号 | 场景 | 命令 | 预期 |
|------|------|------|------|
| TC-S10 | 按 domain 过滤 | `python hooks/index.py --root ./articles search --domain "Electron 桌面开发"`（依赖 TC-S01、TC-S03） | 入参 domain 先 slug 化再比对，仅返回 `domain="electron-桌面开发"` 的记录，不含 TC-S03 的后端架构记录 |
| TC-S11 | 按 tag 过滤（大小写不敏感） | `... search --tag "性能优化"` / `... search --tag "electron"` | 两者均命中 TC-S01 记录（tag 比对统一转小写）；未命中时返回 `[]` |
| TC-S12 | 按 keyword 过滤 + 多条件与逻辑 | `... search --keyword "Electron"`；再 `... search --domain "后端架构" --keyword "Electron"` | keyword 仅在 `title` 内做**大小写不敏感包含**匹配；多条件为「与」关系，第二条返回 `[]` |

### 5.4 `edit_distance` 边界（TC-S13~S14）

| 编号 | 场景 | 输入（`from hooks.index import edit_distance`） | 预期 |
|------|------|------|------|
| TC-S13 | 距离取值边界 | `("abc","abc")` / `("abc","abd")` / `("abc","abde")` / `("abc","abcde")` / `("abc","xyzw")` | 依次返回 `0 / 1 / 2 / 2 / 4`；阈值 `SOFT_DISTANCE=2` ⇒ 前四者判软重复，最后一者不判 |
| TC-S14 | 空串与单侧为空 | `("","")` / `("","abc")` / `("abc","")` | 依次返回 `0 / 3 / 3`；**已知边界**：`dedup` 省略 `--slug` 时以空串参与比对，若索引中存在长度 ≤2 的 slug 会被误判为软重复 —— 调用方 MUST 显式传 `--slug` |

---

## 汇总

| 类别 | 用例数 | 说明 |
|------|--------|------|
| 占位符/profile | 8 | TC-P01~P08 |
| 去AI化引擎 | 10 | TC-W01~W10 |
| 去AI化引擎委派 | 6 | TC-D01~D06：委派三态 / 时机 / 事实保真 / 对称检测 |
| 产品植入 | 5 | TC-R01~R05 |
| 模式与边界 | 5 | TC-M01~M05 |
| **脚本调用（`hooks/index.py`）** | **14** | TC-S01~S14：add 字段完整性 4 / dedup 三档 5 / search 过滤 3 / edit_distance 边界 2 |
| **合计** | **48** | 覆盖零~H 全能力组（含 D' 委派）+ 脚本层


---

## 三点五、文末安装指引要素（TC-I01~TC-I02）

> 依据 SKILL.md §文末要素 第 3 条（tri-xxx 技能安装指引，`{{TRI_INSTALL_NOTE}}`）与 §内置默认值表推演。

| 编号 | 场景 | 输入 | 预期 |
|------|------|------|------|
| TC-I01 | 已配置安装指引 | profile 中 `TRI_INSTALL_NOTE` 非空 | 文末输出安装指引段：含安装地址 `https://skillhub.cn/`，且含至少一条 `skillhub install <技能名>` 命令示例；语气自然无广告腔 |
| TC-I02 | 未配置安装指引 | profile 中 `TRI_INSTALL_NOTE` 为空 | 文末整段跳过（绝不输出占位符 `{{TRI_INSTALL_NOTE}}`，也不输出无内容的空段）；其余两条文末要素照常 |
