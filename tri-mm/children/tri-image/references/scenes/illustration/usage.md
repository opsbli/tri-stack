# Usage

## Command Syntax

```bash
# Auto-select type and style based on content
/image-engine path/to/article.md

# Specify type
/image-engine path/to/article.md --type infographic

# Specify style
/image-engine path/to/article.md --style blueprint

# Combine type and style
/image-engine path/to/article.md --type flowchart --style notion

# Specify density
/image-engine path/to/article.md --density rich

# Generate up to 4 images in parallel after prompts are saved
/image-engine path/to/article.md --batch-size 4

# Direct content input (paste mode)
/image-engine
[paste content]
```

## Options

| Option | Description |
|--------|-------------|
| `--type <name>` | Illustration type (see Type Gallery in SKILL.md) |
| `--style <name>` | Visual style (see references/styles.md) |
| `--preset <name>` | Shorthand for type + style combo (see [references/style-presets.md](style-presets.md)) |
| `--density <level>` | Image count: minimal / balanced / rich |
| `--batch-size <n>` | Temporary generation batch size for this run. Default: `generation_batch_size` from EXTEND.md, otherwise 4. Clamp to 1-8. |

## Input Modes

| Mode | Trigger | Output Directory |
|------|---------|------------------|
| File path | `path/to/article.md` | Use `default_output_dir` preference, or ask if not set |
| Paste content | No path argument | `illustrations/{topic-slug}/` |

## Output Directory Options

| Value | Path |
|-------|------|
| `same-dir` | `{article-dir}/` |
| `illustrations-subdir` | `{article-dir}/illustrations/` |
| `independent` | `illustrations/{topic-slug}/` |

Configure in EXTEND.md: `default_output_dir: illustrations-subdir`

## Examples

**Technical article with data**:
```bash
/image-engine api-design.md --type infographic --style blueprint
```

**Same thing with preset**:
```bash
/image-engine api-design.md --preset tech-explainer
```

**Personal story**:
```bash
/image-engine journey.md --preset storytelling
```

**Tutorial with steps**:
```bash
/image-engine how-to-deploy.md --preset tutorial --density rich
```

**Opinion article with poster style**:
```bash
/image-engine opinion.md --preset opinion-piece
```

**Preset with override**:
```bash
/image-engine article.md --preset tech-explainer --style notion
```
