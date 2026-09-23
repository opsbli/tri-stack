# 本地补丁层（tri-skills）

## 为什么需要它

本仓库的 skill 是从 **skillhub 平台**同步来的（作者 `TrisighT` / `user_989eb8f0`，平台共 92 个 skill）。
同步方式有两种，**两者都会整树替换 skill 目录**：

| 方式 | 命令 | 影响 |
|---|---|---|
| 版本门自动升级 | `python <skill>/scripts/check_update.py`（D 态触发） | 整树替换该 skill 目录 |
| 手动升级 | `skillhub upgrade <slug>` | 同上 |

⇒ **直接改仓库里的 skill 文件，下次同步就会丢。** 所以本地修正必须表达成
「记录 + 可重放」，而不是一次性编辑。本目录就是那个记录。

## 目录结构

```
ops/patches/
├── README.md                       本文件
├── manifest.json                   补丁清单（声明式，唯一事实源）
├── payload/
│   └── version-check-spec.md       校正版版本检查规范（分发到各 skill 的 references/）
└── apply.py                        幂等重放器
```

## 用法

```bash
python ops/patches/apply.py             # 应用（幂等，可反复跑）
python ops/patches/apply.py --dry-run   # 只报告将发生什么
python ops/patches/apply.py --json      # 机器可读输出
```

**推荐时机**：每次 `skillhub upgrade` 之后立即重放一次。

## 实测踩过的三个坑（都会导致补丁层静默失效）

### 坑 1 · 行尾混用导致字节级匹配不命中

**本仓库行尾本就混用**：多数 `.md` 的 **git blob 本身就是 CRLF**
（实测 `README.md` blob 含 203 行 CR、`CONTRIBUTING.md` 含 133 行 CR，无 `.gitattributes`，
`core.autocrlf=true`——作者在 Windows 上开发）；而本补丁层新写入的 spec 是 LF。

⇒ 若按**字节**匹配 `old`/`new`（LF 书写），遇到 CRLF 文件会**静默不命中**，表现为
`应用 0｜已应用 0`（`f6-gate-fill-empty-block` 首次就是这样失败的）。

**处置**：`op_replace_text` 改为**行尾无关**——匹配前归一化为 LF，写回时恢复原行尾风格。
`op_sync_spec` 亦改为按**归一化文本**比对，避免在 CRLF 检出上反复产生无意义改写。

> 早期版本的 README 把根因写成「`write_text` 在 Windows 下把 `\n` 翻成 `\r\n`」——
> **该归因有误**，CRLF 是仓库原生状态。真实问题是「仓库行尾混用 + 字节级匹配」的组合。

### 坑 2 · 「已应用」标记不能用短串

早期版本拿 `new`（如「。」或空串）当已应用标记，结果把 **515 个无关文件**误计为「已应用」，
产出虚高数字。**必须用专属长标记**（`already_marker`），否则计数不可信。

### 坑 3 · 幂等性必须实测

`sync_spec` 首版用字节哈希比对，因行尾差异永不相等，**每次运行都报「写入 42」**，
幂等形同虚设。判据：**连续运行两次，第二次应报 `写入 0｜跳过 N`**。

## 当前补丁清单

| id | 类型 | 作用 |
|---|---|---|
| `spec-per-skill` | sync_spec | 为每个引用 `version-check-spec.md` 的 skill 部署校正版自带 spec（当前 42 个） |
| `f2-pointer` | replace_text | 版本门真源指针 `tri-forge/references/version-check-spec.md` → `references/version-check-spec.md` |
| `f3-clause-inline` | replace_text | 移除「；发布前 MUST 通过 python tri-forge/scripts/sync_registry.py --check。」 |
| `f3-clause-sentence` | replace_text | 移除「。发布前 MUST 通过 …」句首变体 |
| `f3-standalone-line` | replace_text | 移除独立的「- 发布前 MUST 通过 …」行 |
| `f3-gate-cmd-check` | replace_text | 移除 version-gate.md 的 `sync_registry.py --check` 命令行 |
| `f3-gate-cmd-apply` | replace_text | 移除 version-gate.md 的 `sync_registry.py --apply` 命令行 |
| `f5-gate-charter` | replace_text | `tri-intent/references/version-gate.md`：「唯一真源」→「家族设计总纲」 |
| `f5-humanize-wording` | replace_text | `tri-humanize/SKILL.md`：去掉与事实相反的「家族级单一事实源，NEVER 内联/自带 fork」 |

## 每项补丁的依据

### spec-per-skill + f2-pointer（真源形态）

**事实**：
- 上游 29 个顶层 SKILL.md 有 22 个指向 `tri-forge/references/version-check-spec.md`（**断链**），
  另 7 个用相对路径 `references/version-check-spec.md`（可用）
- `tri-forge` 在**任何可达源**都不存在：本地磁盘 / git 全历史 / 原作者 GitHub（与本地同 commit `71e44af`）/
  平台 `/api/v1/skills` 与 `/api/v1/download` 双 404；**作者名下 92/92 个 skill 全量枚举，`forge` 零命中**
- 上游自身对真源形态**三向矛盾**：4437B spec 写「不依赖任何外部 skill」（支持自带）；
  `tri-humanize/SKILL.md:219` 写「家族级单一事实源，NEVER 内联/自带 fork」（反对自带）；8 个 skill 实际各带一份

**裁定（用户 2026-09-23）**：**自带为主 + 总纲定位**
- 每个 skill 自带 `references/version-check-spec.md` → 满足家族「支持独立安装」要求
- `tri-intent/references/version-gate.md` 重定位为**家族设计总纲**（设计原则、端点配置真源、
  四处版本同步点、junction 单源例外、P1–P4 阻断定义）
- 两份文件互相注明管辖范围；`scripts/check_update.py` 为**可执行真源**

### payload 的校正内容

`payload/version-check-spec.md` 以上游 4437B 变体为底本（无错字、来自最新一批 skill），
按**与 `scripts/check_update.py` 实际行为的逐条比对**校正：

| 上游 spec 原述 | 实际实现 | 校正 |
|---|---|---|
| `--platform <平台>`，取值 `trae\|workbuddy\|qwen\|codex` | **无此参数** | 删除，改为实际存在的 `--skill-dir` / `--json` / `--dry-run` / `--ttl-min` |
| 退出码 `20` / `21` / `22` 三种 BLOCK | **只有 20**，P2/P3/P4 通过 `block_code` 区分 | 合并为单一的 `20` + `block_code` 说明 |
| 未提 `64` | 存在 `64`（参数/环境错误） | 补充 |
| 缓存文件 `<cache-dir>/.version_cache.json` | `~/.cache/<slug>/update-state.json` | 修正 |
| 「本文件是 **tri-forge 家族** …唯一事实源」 | 家族名不是 tri-forge | 改为「本 skill 自带」+ 总纲指引 |
| 未提端点解析 | 读 `~/.skillhub/metadata.json` 取 origin | 补充第 3、5 条 |
| `--simulate-*` 表把预期退出码与场景错位配对 | 4 类注入参数各自独立 | 改为「参数 / 取值 / 场景」三列，不断言退出码 |

## 尚未纳入补丁层的残留（F4）

仓库仍有 **19 个 .md / 42 处** 提及 `tri-forge`，均为**描述性或历史性**引用，不影响运行：

| 类别 | 文件 | 处理建议 |
|---|---|---|
| CHANGELOG 历史记录 | `tri-coding` / `tri-humanize` / `tri-intent` / `tri-jobhunt` / `tri-sdlc` 的 CHANGELOG | **不改**（追加型历史） |
| 路由/协作说明 | `tri-intent/doing/I21-distill.md`（13）、`doing/SKILL.md`（3）、`SKILL.md`（2）、`version-gate.md`（1） | 建议加注「本仓库未随包分发」，待定 |
| 测试用例 / README | `tri-guard` / `tri-jobhunt` 的 tests 与 README、`tri-checklist` / `tri-god` / `tri-learn` / `tri-jobhunt` 的 SKILL.md | 视上下文加注 |

## ⚠️ 本目录未纳入 git

`.workbuddy/` 在 `.gitignore:6` 中被忽略，故**本补丁层不进 git**。

| 场景 | 是否存活 |
|---|---|
| `skillhub upgrade` 整树替换 skill 目录 | ✅ 存活（不在 skill 目录内） |
| 重新 clone 本仓库 | ❌ 丢失 |

若希望「重新 clone 也存活」，需把本目录迁到版本化路径（如仓库根 `patches/`）。
**待裁决。**
