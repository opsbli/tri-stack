> 本篇是该场景的完整操作规范（由原分散文档合并而来，保留全部原始条款与数值）。
> 公共规则（用户输入工具、后端选择、提示词文件先行、批处理、确认门、参考图）统一见 `../../common/`，本篇不重复。
> 场景专属的 Gallery 已合订为同名录文件（如 `palettes.md`），读取时按"命中条目名"定位二级标题锚点，无需通篇加载。

# 文章配图与视觉素材

Analyze articles, identify illustration positions, generate images with Type × Style × Palette consistency.

## Batch Generation Policy

After every prompt file for the run has been saved and verified, generate images in batches by default.

Priority order:

1. Use the chosen backend's native batch / multi-task interface if it exists. Each task must keep its own prompt file, output path, aspect ratio, and direct reference images.
2. If no native batch interface exists but the runtime can issue parallel tool calls, dispatch up to `generation_batch_size` images at a time. Default: `4`. An explicit user request in the current message, such as `--batch-size 4` or "并行4张一起生成", overrides EXTEND.md.
3. If neither native batch nor parallel tool calls are available, generate sequentially.

Rules:

- Never start the first batch until all prompt files for that batch exist on disk.
- Retry failed items once without regenerating successful items.
- Do not use subagents merely to parallelize image rendering. Use subagents only for separate prompt iteration or creative exploration.

## Confirmation Policy

Default behavior: **confirm before generation**.

- Treat explicit skill invocation, a file path, matched signals/presets, and `EXTEND.md` defaults as **recommendation inputs only**. None of them authorizes skipping confirmation.
- Do **not** start Step 4 or later until the user completes Step 3.
- Skip confirmation only when the current request explicitly says to do so, for example: "直接生成", "不用确认", "跳过确认", "按默认出图", or equivalent wording.
- If confirmation is skipped explicitly, state the assumed type / density / style / palette / language / backend in the next user-facing update before generating.

## Reference Images

Users may supply reference images via `--ref <files...>` or by providing file paths / pasting images in conversation. Refs guide style, palette, composition, or subject for specific illustrations.

Full detection, storage, and processing rules are in [references/workflow.md](workflow.md) (Step 1.0 saves to `references/NN-ref-{slug}.{ext}`; Step 5.3 processes per-illustration usage `direct | style | palette`). When the chosen backend supports batch input, `direct`-usage entries in each prompt file's `references:` frontmatter should be propagated into its batch payload so backends can pass them through (e.g. `ImageEngine` accepts `ref` per task).

## Three Dimensions

| Dimension | Controls | Examples |
|-----------|----------|----------|
| **Type** | Information structure | infographic, scene, flowchart, comparison, framework, timeline |
| **Style** | Rendering approach | notion, warm, minimal, blueprint, watercolor, elegant |
| **Palette** | Color scheme (optional) | macaron, warm, neon — overrides style's default colors |

Combine freely: `--type infographic --style vector-illustration --palette macaron`

Or use presets: `--preset edu-visual` → type + style + palette in one flag. See [Style Presets](style-presets.md).

## Types

| Type | Best For |
|------|----------|
| `infographic` | Data, metrics, technical |
| `scene` | Narratives, emotional |
| `flowchart` | Processes, workflows |
| `comparison` | Side-by-side, options |
| `framework` | Models, architecture |
| `timeline` | History, evolution |

## Styles

See [references/styles.md](styles-overview.md) for Core Styles, full gallery, and Type × Style compatibility.

## Workflow

```
- [ ] Step 1: Pre-check (EXTEND.md, references, config)
- [ ] Step 2: Analyze content
- [ ] Step 3: Confirm settings (AskUserQuestion)
- [ ] Step 4: Generate outline
- [ ] Step 5: Generate images
- [ ] Step 6: Finalize
```

### Step 1: Pre-check

**1.5 Load Preferences (EXTEND.md) ⛔ BLOCKING**

Check EXTEND.md in priority order — the first one found wins:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.tri-image/image-engine/EXTEND.md` | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/image-engine/image-engine/EXTEND.md` | XDG |
| 3 | `$HOME/.tri-image/image-engine/EXTEND.md` | User home |

| Result | Action |
|--------|--------|
| Found | Read, parse, display summary |
| Not found | ⛔ Run [first-time-setup](../../common/preferences-schema.md) |

Full procedures: [references/workflow.md](references/workflow.md#step-1-pre-check)

### Step 2: Analyze

| Analysis | Output |
|----------|--------|
| Content type | Technical / Tutorial / Methodology / Narrative |
| Purpose | information / visualization / imagination |
| Core arguments | 2-5 main points |
| Positions | Where illustrations add value |

**CRITICAL**: Metaphors → visualize underlying concept, NOT literal image.

Full procedures: [references/workflow.md](references/workflow.md#step-2-setup--analyze)

### Step 3: Confirm Settings ⚠️

**Hard gate**: this step is mandatory per the [Confirmation Policy](#confirmation-policy) — Steps 4+ cannot start until the user confirms here (or explicitly opts out with "直接生成" / equivalent wording in the current request).

**ONE AskUserQuestion, max 4 Qs. Q1-Q2 REQUIRED. Q3 required unless preset chosen.**

| Q | Options |
|---|---------|
| **Q1: Preset or Type** | [Recommended preset], [alt preset], or manual: infographic, scene, flowchart, comparison, framework, timeline, mixed |
| **Q2: Density** | minimal (1-2), balanced (3-5), per-section (Recommended), rich (6+) |
| **Q3: Style** | [Recommended], minimal-flat, sci-fi, hand-drawn, editorial, scene, poster, Other — **skip if preset chosen** |
| Q4: Palette | Default (style colors), macaron, warm, neon — **skip if preset includes palette or preferred_palette set** |
| Q5: Language | When article language ≠ EXTEND.md setting |

Full procedures: [references/workflow.md](references/workflow.md#step-3-confirm-settings-)

### Step 4: Generate Outline

Save `outline.md` with frontmatter (type, density, style, palette, image_count) and entries:

```yaml
## Illustration 1
**Position**: [section/paragraph]
**Purpose**: [why]
**Visual Content**: [what]
**Filename**: 01-infographic-concept-name.png
```

Full template: [references/workflow.md](references/workflow.md#step-4-generate-outline)

### Step 5: Generate Images

⛔ **BLOCKING: Prompt files MUST be saved before ANY image generation.** This is a hard requirement regardless of which backend is chosen — the prompt file is the reproducibility record.

1. For each illustration, create a prompt file per [references/prompt-construction.md](prompt-construction.md)
2. Save to `prompts/NN-{type}-{slug}.md` with YAML frontmatter
3. Prompts **MUST** use type-specific templates with structured sections (ZONES / LABELS / COLORS / STYLE / ASPECT)
4. LABELS **MUST** include article-specific data: actual numbers, terms, metrics, quotes
5. **DO NOT** pass ad-hoc inline prompts to `--prompt` without saving prompt files first
6. Select the backend via the `## Image Generation Tools` rule at the top: use whatever is available; if multiple, ask the user once. Do this once per session before any generation.
   - **`codex-imagegen` invocation**: when the rule resolves to `codex-imagegen`, see [references/codex-imagegen.md](../../common/image-backend-rules.md#coderef-调用契约) for the invocation contract (preferred `ImageEngine --provider codex-cli` path, runtime wrapper discovery, parameter notes, stdout schema, batch semantics).
7. **Execution strategy**: Generate in batches per the `## Batch Generation Policy`: backend native batch first, runtime parallel tool calls second, sequential only as fallback. Default batch size is 4 unless EXTEND.md or the current request overrides it.
8. Process references (`direct`/`style`/`palette`) per prompt frontmatter
9. Apply watermark if EXTEND.md enabled
10. Generate from saved prompt files; retry once on failure

Full procedures: [references/workflow.md](references/workflow.md#step-5-generate-images)

### Step 6: Finalize

Insert `![description]({relative-path}/NN-{type}-{slug}.png)` after paragraphs. Path computed relative to article file based on output directory setting.

```
Article Illustration Complete!
Article: [path] | Type: [type] | Density: [level] | Style: [style] | Palette: [palette or default]
Images: X/N generated
```

## Output Directory

Output directory is determined by `default_output_dir` in EXTEND.md (set during first-time setup):

| `default_output_dir` | Output Path | Markdown Insert Path |
|----------------------|-------------|----------------------|
| `imgs-subdir` (default) | `{article-dir}/imgs/` | `imgs/NN-{type}-{slug}.png` |
| `same-dir` | `{article-dir}/` | `NN-{type}-{slug}.png` |
| `illustrations-subdir` | `{article-dir}/illustrations/` | `illustrations/NN-{type}-{slug}.png` |
| `independent` | `illustrations/{topic-slug}/` | `illustrations/{topic-slug}/NN-{type}-{slug}.png` (relative to cwd) |

All auxiliary files (outline, prompts) are saved inside the output directory:

```
{output-dir}/
├── outline.md
├── prompts/
│   └── NN-{type}-{slug}.md
└── NN-{type}-{slug}.png
```

When input is **pasted content** (no file path), always uses `illustrations/{topic-slug}/` with `source-{slug}.{ext}` saved alongside.

**Slug**: 2-4 words, kebab-case. **Conflict**: append `-YYYYMMDD-HHMMSS`.

## Modification

| Action | Steps |
|--------|-------|
| Edit | Update prompt → Regenerate → Update reference |
| Add | Position → Prompt → Generate → Update outline → Insert |
| Delete | Delete files → Remove reference → Update outline |

Text correction policy:

- If any rendered text (labels, captions, etc.) is misspelled, garbled, hard to read, or visually weak, do not patch the bitmap with code.
- For text-correction regenerations, write a new prompt file and a new output path so the flawed candidate is preserved for comparison.
- Post-processing is limited to crop, resize, compression, or format conversion that does not alter text or the main composition.

## References

| File | Content |
|------|---------|
| [references/workflow.md](workflow.md) | Detailed procedures |
| [references/usage.md](usage.md) | Command syntax |
| [references/styles.md](styles-overview.md) | Style gallery + Palette gallery |
| [references/style-presets.md](style-presets.md) | Preset shortcuts (type + style + palette) |
| [references/prompt-construction.md](prompt-construction.md) | Prompt templates |
| [references/config/first-time-setup.md](../../common/preferences-schema.md) | First-time setup |

## Changing Preferences

EXTEND.md lives at the first matching path listed in Step 1.5. Three ways to change it:

- **Edit directly** — open EXTEND.md and change fields. Full schema: `references/config/preferences-schema.md`.
- **Reconfigure interactively** — delete EXTEND.md (or ask "reconfigure image-engine preferences" / "重新配置"). The next run re-triggers first-time setup.
- **Common one-line edits**:
  - `preferred_image_backend: auto` — default; runtime-native tool wins, falls back to the only installed backend, asks only if multiple non-native are present.
  - `preferred_image_backend: codex-imagegen` — pin to Codex's built-in.
  - `preferred_image_backend: ImageEngine` — pin to the ImageEngine skill.
  - `preferred_image_backend: ask` — confirm backend every run.
  - `generation_batch_size: 4` — default number of images to render concurrently when the runtime supports parallel generation calls.
  - `preferred_type: infographic`, `preferred_style: notion`, `preferred_palette: macaron`, `language: zh`.
  - `default_output_dir: imgs-subdir` — where to write generated images relative to the article.
