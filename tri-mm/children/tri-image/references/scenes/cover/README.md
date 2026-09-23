> 本篇是该场景的完整操作规范（由原分散文档合并而来，保留全部原始条款与数值）。
> 公共规则（用户输入工具、后端选择、提示词文件先行、批处理、确认门、参考图）统一见 `../../common/`，本篇不重复。
> 场景专属的 Gallery 已合订为同名录文件（如 `palettes.md`），读取时按"命中条目名"定位二级标题锚点，无需通篇加载。

# 封面图

Generate elegant cover images for articles with 5-dimensional customization.

## Confirmation Policy

Default behavior: **confirm before generation**.

- Treat explicit skill invocation, a file path, matched keywords/presets, `EXTEND.md` defaults, and any documented auto-selection as **recommendation inputs only**. None of them authorizes skipping confirmation.
- Do **not** start Step 3 or Step 4 until the user confirms the dimensions / aspect / language / backend choices.
- Skip confirmation only when the current request explicitly says to do so, for example: `--quick`, "直接生成", "不用确认", "跳过确认", "按默认出图", or equivalent wording. `quick_mode: true` in `EXTEND.md` counts as a standing explicit opt-out — set it only when you want every run to skip Step 2.
- If confirmation is skipped explicitly, state the assumed dimensions / aspect / language / backend in the next user-facing update before generating.

## Options

| Option | Description |
|--------|-------------|
| `--type <name>` | hero, conceptual, typography, metaphor, scene, minimal |
| `--palette <name>` | warm, elegant, cool, dark, earth, vivid, pastel, mono, retro, duotone, macaron |
| `--rendering <name>` | flat-vector, hand-drawn, painterly, digital, pixel, chalk, screen-print |
| `--style <name>` | Preset shorthand (see [Style Presets](style-presets.md)) |
| `--text <level>` | none, title-only, title-subtitle, text-rich |
| `--mood <level>` | subtle, balanced, bold |
| `--font <name>` | clean, handwritten, serif, display |
| `--aspect <ratio>` | 16:9 (default), 2.35:1, 4:3, 3:2, 1:1, 3:4 |
| `--lang <code>` | Title language (en, zh, ja, etc.) |
| `--no-title` | Alias for `--text none` |
| `--quick` | Skip confirmation, use auto-selection |
| `--ref <files...>` | Reference images for style/composition guidance |

## Five Dimensions

| Dimension | Values | Default |
|-----------|--------|---------|
| **Type** | hero, conceptual, typography, metaphor, scene, minimal | auto |
| **Palette** | warm, elegant, cool, dark, earth, vivid, pastel, mono, retro, duotone, macaron | auto |
| **Rendering** | flat-vector, hand-drawn, painterly, digital, pixel, chalk, screen-print | auto |
| **Text** | none, title-only, title-subtitle, text-rich | title-only |
| **Mood** | subtle, balanced, bold | balanced |
| **Font** | clean, handwritten, serif, display | clean |

Auto-selection rules: [references/auto-selection.md](auto-selection.md)

## Galleries

**Types**: hero, conceptual, typography, metaphor, scene, minimal
→ Details: [references/types.md](types.md)

**Palettes**: warm, elegant, cool, dark, earth, vivid, pastel, mono, retro, duotone, macaron
→ Details: [references/palettes/](palettes.md)

**Renderings**: flat-vector, hand-drawn, painterly, digital, pixel, chalk, screen-print
→ Details: [references/renderings/](renderings.md)

**Text Levels**: none (pure visual) | title-only (default) | title-subtitle | text-rich (with tags)
→ Details: [references/dimensions/text.md](dimensions.md#text)

**Mood Levels**: subtle (low contrast) | balanced (default) | bold (high contrast)
→ Details: [references/dimensions/mood.md](dimensions.md#mood)

**Fonts**: clean (sans-serif) | handwritten | serif | display (bold decorative)
→ Details: [references/dimensions/font.md](dimensions.md#font)

## File Structure

Output directory per `default_output_dir` preference:
- `same-dir`: `{article-dir}/`
- `imgs-subdir`: `{article-dir}/imgs/`
- `independent` (default): `cover-image/{topic-slug}/`

```
<output-dir>/
├── source-{slug}.{ext}    # Source files
├── refs/                  # Reference images (if provided)
│   ├── ref-01-{slug}.{ext}
│   └── ref-01-{slug}.md   # Description file
├── prompts/cover.md       # Generation prompt
└── cover.png              # Output image
```

**Slug**: 2-4 words, kebab-case. Conflict: append `-YYYYMMDD-HHMMSS`

## Workflow

### Progress Checklist

```
Cover Image Progress:
- [ ] Step 0: Check preferences (EXTEND.md) ⛔ BLOCKING
- [ ] Step 1: Analyze content + save refs + determine output dir
- [ ] Step 2: Confirm options (6 dimensions) ⚠️ unless --quick
- [ ] Step 3: Create prompt
- [ ] Step 4: Generate image
- [ ] Step 5: Completion report
```

### Flow

```
Input → [Step 0: Preferences] ─┬─ Found → Continue
                               └─ Not found → First-Time Setup ⛔ BLOCKING → Save EXTEND.md → Continue
        ↓
Analyze + Save Refs → [Output Dir] → [Confirm: 6 Dimensions] → Prompt → Generate → Complete
                                              ↓
                                     (skip if --quick or all specified)
```

### Step 0: Load Preferences ⛔ BLOCKING

Check EXTEND.md in priority order — the first one found wins:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.tri-image/image-engine/EXTEND.md` | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/image-engine/image-engine/EXTEND.md` | XDG |
| 3 | `$HOME/.tri-image/image-engine/EXTEND.md` | User home |

| Result | Action |
|--------|--------|
| Found | Load, display summary → Continue |
| Not found | ⛔ Run first-time setup ([references/config/first-time-setup.md](../../common/preferences-schema.md)) → Save → Continue |

**CRITICAL**: If not found, complete setup BEFORE any other steps or questions.

### Step 1: Analyze Content

1. **Save reference images** (if provided) → [references/workflow/reference-images.md](reference-images.md)
2. **Save source content** (if pasted, save to `source.md`)
3. **Analyze content**: topic, tone, keywords, visual metaphors
4. **Deep analyze references** ⚠️: Extract specific, concrete elements (see reference-images.md)
5. **Detect language**: Compare source, user input, EXTEND.md preference
6. **Determine output directory**: Per File Structure rules

**⚠️ People in Reference Images:**

If reference images contain **people** who should appear in the cover:

- **Model supports `--ref`** (default): Copy image to `refs/`, pass via `--ref` at generation. No description file needed — the model sees the face directly.
- **Model does NOT support `--ref`** (Jimeng, Seedream 3.0): Create `refs/ref-NN-{slug}.md` with per-character description (hair, glasses, skin tone, clothing). Embed as MUST/REQUIRED instructions in prompt text.

See [reference-images.md](reference-images.md) for full decision table.

### Step 2: Confirm Options ⚠️

**Hard gate**: this step is mandatory per the [Confirmation Policy](#confirmation-policy) — Steps 3–4 cannot start until the user confirms here (or explicitly opts out with `--quick` / `quick_mode: true` / equivalent wording in the current request).

**MUST use `AskUserQuestion` tool** to present options as interactive selection — NOT plain text tables. Present up to 4 questions in a single `AskUserQuestion` call (Type, Palette, Rendering, Font + Settings). Each question shows the recommended option first with reason, followed by alternatives.

Full confirmation flow and question format: [references/workflow/confirm-options.md](confirm-options.md)

| Condition | Skipped | Still Asked |
|-----------|---------|-------------|
| `--quick` or `quick_mode: true` | 6 dimensions | Aspect ratio (unless `--aspect`) |
| All 6 + `--aspect` specified | All | None |

### Step 3: Create Prompt

Save to `prompts/cover.md`. Template: [references/workflow/prompt-template.md](prompt-template.md)

**CRITICAL - References in Frontmatter**:
- Files saved to `refs/` → Add to frontmatter `references` list
- Style extracted verbally (no file) → Omit `references`, describe in body
- Before writing → Verify: `test -f refs/ref-NN-{slug}.{ext}`

**Reference elements in body** MUST be detailed, prefixed with "MUST"/"REQUIRED", with integration approach.

### Step 4: Generate Image

1. **Backup existing** `cover.png` if regenerating
2. **Select backend** via the `## Image Generation Tools` rule at the top: use whatever is available; if multiple, ask the user once. Do this once per session before any generation.
3. **Write the full final prompt** to `prompts/01-cover-[slug].md` (hard requirement) BEFORE invoking the backend.
4. **Process references** from prompt frontmatter:
   - `direct` usage → pass via `--ref` (use ref-capable backend)
   - `style`/`palette` → extract traits, append to prompt
5. **Generate**: Call the chosen backend with the prompt file, output path, aspect ratio.
   - **`codex-imagegen`**: see [references/codex-imagegen.md](../../common/image-backend-rules.md#coderef-调用契约) for the invocation contract (preferred `ImageEngine --provider codex-cli` path, runtime wrapper discovery, parameter notes, stdout schema, batch semantics).
   - **Codex `imagegen` (native)** or other runtime-native tools / `ImageEngine` skill: per the rule in `## Image Generation Tools` above.
6. On failure: auto-retry once

### Step 5: Completion Report

```
Cover Generated!

Topic: [topic]
Type: [type] | Palette: [palette] | Rendering: [rendering]
Text: [text] | Mood: [mood] | Font: [font] | Aspect: [ratio]
Title: [title or "visual only"]
Language: [lang] | Watermark: [enabled/disabled]
References: [N images or "extracted style" or "none"]
Location: [directory path]

Files:
✓ source-{slug}.{ext}
✓ prompts/cover.md
✓ cover.png
```

## Image Modification

| Action | Steps |
|--------|-------|
| **Regenerate** | Backup → Update prompt file FIRST → Regenerate |
| **Change dimension** | Backup → Confirm new value → Update prompt → Regenerate |

Text correction policy:

- If the title/subtitle is misspelled, garbled, hard to read, or visually weak, do not patch the bitmap with code.
- For text-correction regenerations, write a new prompt file and a new output path so the flawed candidate is preserved for comparison.
- Post-processing is limited to crop, resize, compression, or format conversion that does not alter text or the main composition.

## Composition Principles

- **Whitespace**: 40-60% breathing room
- **Visual anchor**: Main element centered or offset left
- **Characters**: Simplified silhouettes; NO realistic humans
- **Title**: Use exact title from user/source; never invent

## Changing Preferences

EXTEND.md lives at the path noted in **Step 0**. Three ways to change it:

- **Edit directly** — open EXTEND.md and change fields. Full schema: [references/config/preferences-schema.md](../../common/preferences-schema.md).
- **Reconfigure interactively** — delete EXTEND.md (or ask "reconfigure image-engine preferences" / "重新配置"). The next run re-triggers first-time setup.
- **Common one-line edits**:
  - `preferred_image_backend: auto` — default; runtime-native tool wins, falls back to the only installed backend, asks only if multiple non-native are present.
  - `preferred_image_backend: codex-imagegen` — pin to Codex's built-in.
  - `preferred_image_backend: ImageEngine` — pin to the ImageEngine skill.
  - `preferred_image_backend: ask` — confirm backend every run.
  - `watermark.enabled: true`, `preferred_type`, `preferred_palette`, `preferred_rendering`, `default_aspect`, `quick_mode: true`, `language` — shift the auto-selection defaults and confirmation flow.

## References

**Dimensions**: [text.md](dimensions.md#text) | [mood.md](dimensions.md#mood) | [font.md](dimensions.md#font)
**Palettes**: [references/palettes/](palettes.md)
**Renderings**: [references/renderings/](renderings.md)
**Types**: [references/types.md](types.md)
**Auto-Selection**: [references/auto-selection.md](auto-selection.md)
**Style Presets**: [references/style-presets.md](style-presets.md)
**Compatibility**: [references/compatibility.md](compatibility.md)
**Visual Elements**: [references/visual-elements.md](visual-elements.md)
**Workflow**: [confirm-options.md](confirm-options.md) | [prompt-template.md](prompt-template.md) | [reference-images.md](reference-images.md)
**Config**: [preferences-schema.md](../../common/preferences-schema.md) | [first-time-setup.md](../../common/preferences-schema.md) | [watermark-guide.md](../../common/watermark-guide.md)
