# 统一输出契约（公共层 · 落盘结构）

> 合并前各场景各有 7 种互不一致的落盘约定（`cover-image/` `infographic/` `slide-deck/` `comic/` `image-cards/` `illustrations/` `{input}/diagram/`），维护与取用都很痛。合并后**统一到单一根**，场景只决定子目录名。

## 根路径（向后兼容，未变更）

```
.tribro/multimedia/image/<命名>/
```

**根与既有契约完全一致**（既有调用方无需改动）。唯一新增的是 `<命名>` 的取值规范：

```
<命名> = <scene>-<slug>
```

`scene` 取值：`cover` · `diagram` · `infographic` · `illustration` · `cards` · `slides` · `comic`
`<slug>`：**2–4 个词、kebab-case**，取自主题；冲突时追加 `-YYYYMMDD-HHMMSS`。

> 变更前后对照：旧 `image/<命名>/` → 新 `image/cover-ai-agent-trends/`。`design.md`、`result.md` 仍在 `<命名>/` 一级，位置不变。

## 通用布局（各场景共有）

```
.tribro/multimedia/image/<scene>-<slug>/
├── source-{slug}.{ext}     # 源内容（粘贴或文件路径）
├── refs/                   # 参考图（仅当使用参考图时）
│   ├── ref-NN-{slug}.{ext}
│   └── ref-NN-{slug}.md    # 仅后端不支持参考图时生成
├── prompts/                # 提示词文件（可复现记录，硬要求）
│   └── NN-{type}-{slug}.md
├── design.md               # 9 维设计方案（tri-mm 契约要求的确认门载体）
├── result.md               # 产物清单 + 参数 + 核对结果
└── <产物>                  # 见下表
```

## 各场景特有产物

| scene | 特有文件 |
|---|---|
| `cover` | `cover.png` |
| `diagram` | `<name>.svg` + `<name>@2x.png`（可由 `--scale` 改倍数） |
| `infographic` | `analysis.md`、`structured-content.md`、`infographic.png` |
| `illustration` | `outline.md`、`NN-{type}-{slug}.png`（含回写 Markdown 的相对路径） |
| `cards` | `analysis.md`、`outline.md`、`outline-strategy-{a,b,c}.md`（详模式）、`NN-{type}-{slug}.png` |
| `slides` | `outline.md`、`NN-slide-{slug}.png`、`{slug}.pptx`、`{slug}.pdf` |
| `comic` | `analysis.md`、`storyboard.md`、`characters/characters.{md,png}`、`NN-{cover\|page}-{slug}.png`、`{slug}.pdf` |

## 备份铁律（全场景）

写任何文件前若同名文件已存在，MUST 先改名 `<name>-backup-YYYYMMDD-HHMMSS.<ext>`，**NEVER 直接覆盖**。这保护用户手改内容并支持回滚。

## 完成判据产物

每次执行 MUST 落 `result.md`，至少含：产物路径清单、本次采用的参数（场景/比例/语言/风格/后端）、逐项核对快照 `任务要点` 的结果。未完成协作 invariants，缺 `result.md` 即判未完成。
