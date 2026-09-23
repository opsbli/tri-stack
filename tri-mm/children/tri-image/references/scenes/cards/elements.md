# 构成元素画廊（合订本）

> 本节由同目录下多个单页条目合订而成，保留全部原始内容与原条目名作为二级标题锚点。按命中条目读取对应小节（grep 模式：`^## <条目名>`），无需通篇加载。

## canvas

Core canvas specifications and layout grids for Xiaohongshu infographics.

#### Aspect Ratios

| Name | Ratio | Pixels | Note |
|------|-------|--------|------|
| portrait-3-4 | 3:4 | 1242×1660 | Highest traffic on XHS (recommended) |
| square | 1:1 | 1242×1242 | Second recommended |
| portrait-2-3 | 2:3 | 1242×1863 | Taller format |

**Default**: portrait-3-4 for maximum engagement.

#### Safe Zones

Avoid placing critical content in these areas:

| Zone | Position | Reason |
|------|----------|--------|
| bottom-overlay | Bottom 10% | Title bar overlay on mobile |
| top-right | Top-right corner | Like/share button overlay |
| bottom-right | Bottom-right corner | Watermark position |

```
┌─────────────────────────────┐
│                 [like/share]│  ← top-right: avoid
│                             │
│                             │
│      ✓ SAFE CONTENT AREA    │
│                             │
│                             │
│  [title bar overlay area]   │  ← bottom 10%: avoid key info
└─────────────────────────────┘
```

#### Grid Layouts

##### Density-Based Layouts

| Layout | Info Density | Whitespace | Points/Image | Best For |
|--------|--------------|------------|--------------|----------|
| sparse | Low | 60-70% | 1-2 | Covers, quotes, impactful statements |
| balanced | Medium | 40-50% | 3-4 | Standard content, tutorials |
| dense | High | 20-30% | 5-8 | Knowledge cards, cheat sheets |

##### Structure-Based Layouts

| Layout | Structure | Items | Best For |
|--------|-----------|-------|----------|
| list | Vertical enumeration | 4-7 | Rankings, checklists, step guides |
| comparison | Left vs Right | 2 sections | Before/after, pros/cons |
| flow | Connected nodes | 3-6 steps | Processes, timelines, workflows |
| mindmap | Center radial | 4-8 branches | Concept maps, brainstorming, topic overview |
| quadrant | 4-section grid | 4 sections | SWOT analysis, priority matrix, classification |

#### Layout by Position

| Position | Recommended Layout | Why |
|----------|-------------------|-----|
| Cover | sparse | Maximum visual impact, clear title |
| Setup | balanced | Context without overwhelming |
| Core | balanced/dense/list | Based on content density |
| Payoff | balanced/list | Clear takeaways |
| Ending | sparse | Clean CTA, memorable close |

#### Grid Cells

For multi-element compositions:

| Name | Cells | Use Case |
|------|-------|----------|
| single | 1 | Hero image, maximum impact |
| dual | 2 | Before/after, comparison |
| triptych | 3 | Steps, process flow |
| quad | 4 | Product showcase |
| six-grid | 6 | Checklist, collection |
| nine-grid | 9 | Multi-image gallery |

#### Visual Balance

##### Sparse Layout
- Single focal point centered
- Breathing room on all sides
- Symmetrical composition

##### Balanced Layout
- Top-weighted title
- Evenly distributed content below
- Clear visual hierarchy

##### Dense Layout
- Organized grid structure
- Clear section boundaries
- Compact but readable spacing

##### List Layout
- Left-aligned items
- Clear number/bullet hierarchy
- Consistent item format

##### Comparison Layout
- Symmetrical left/right
- Clear visual contrast
- Divider between sections

##### Flow Layout
- Directional flow (top→bottom or left→right)
- Connected nodes with arrows
- Clear progression indicators

##### Mindmap Layout
- Central topic node
- Radial branches outward
- Hierarchical sub-branches
- Organic curved connections

##### Quadrant Layout
- 4-section grid (2×2)
- Clear axis labels
- Each quadrant with distinct content
- Optional circular variant for cycles

## decorations

Visual embellishments and decorative elements for Xiaohongshu infographics.

#### Emphasis Marks (强调标记)

Elements to draw attention to specific content.

| Name | Description | Use Case |
|------|-------------|----------|
| red-arrow | Red arrow pointing to target | Product features, key points |
| circle-mark | Circle highlight annotation | Highlighting details |
| underline | Straight or wavy underline | Text emphasis |
| star-burst | Starburst explosion effect | Special offers, wow factor |
| checkmark | Checkmark/tick symbol | Completed items, pros |
| cross-mark | X mark symbol | Cons, things to avoid |
| exclamation | Exclamation point decoration | Important warnings |
| question | Question mark decoration | FAQ, curiosity |
| numbering | Circled numbers | Steps, rankings |
| bracket | Bracket highlighting | Grouping, emphasis |

#### Backgrounds (背景)

Base layer treatments.

| Name | Description | Use Case |
|------|-------------|----------|
| solid-saturated | High-saturation solid color | Bold, energetic |
| solid-pastel | Soft pastel solid color | Cute, gentle |
| gradient-linear | Linear color gradient | Modern, dynamic |
| gradient-radial | Radial color gradient | Spotlight effect |
| frosted-glass | Frosted glass blur effect | Layered compositions |
| paper-texture | Paper or craft texture | Handmade aesthetic |
| fabric-texture | Fabric/cloth texture | Cozy, tactile |
| chalkboard | Blackboard texture | Educational content |
| grid | Subtle grid pattern | Structured, organized |
| dots | Polka dot pattern | Playful, retro |

#### Doodles & Emoji (涂鸦)

Hand-drawn decorative elements.

| Name | Description | Use Case |
|------|-------------|----------|
| hand-drawn-lines | Sketchy hand-drawn lines | Connections, borders |
| stars-sparkles | Stars and sparkle effects | Magic, excellence |
| flowers | Floral decorations | Beauty, feminine |
| hearts | Heart symbols | Love, favorites |
| clouds | Cloud shapes | Dreamy, thoughts |
| arrows-curvy | Curved directional arrows | Flow, direction |
| squiggles | Wavy squiggle lines | Energy, movement |
| confetti | Scattered confetti | Celebration |
| leaves | Leaf decorations | Nature, fresh |
| bubbles | Circular bubble shapes | Playful, light |

#### Emoji Integration

| Category | Examples | Use Case |
|----------|----------|----------|
| Reactions | 🥹 😍 🤯 | Emotional emphasis |
| Objects | ✨ 💡 🎯 | Visual markers |
| Actions | 👇 👆 ➡️ | Directional cues |
| Nature | 🌸 🌿 ☀️ | Thematic decoration |

#### Frames (边框)

Container and border treatments.

| Name | Description | Use Case |
|------|-------------|----------|
| polaroid | Instant photo frame | Photo showcase |
| film-strip | Film negative border | Cinematic, retro |
| phone-screenshot | Mobile device mockup | App/screen content |
| torn-paper | Torn paper edge effect | Scrapbook aesthetic |
| rounded-rect | Rounded rectangle border | Clean containers |
| decorative | Ornate decorative border | Premium, elegant |
| tape-corners | Washi tape corners | Crafty, casual |
| stamp-border | Stamp perforated edge | Vintage, postal |

#### Dividers (分隔线)

Section separators.

| Name | Description | Use Case |
|------|-------------|----------|
| line-simple | Simple horizontal line | Clean separation |
| line-dashed | Dashed line | Subtle division |
| line-wavy | Wavy line | Playful separation |
| dots-row | Row of dots | Decorative division |
| ornamental | Decorative flourish | Elegant separation |

#### Stickers (贴纸)

Pre-composed decorative elements.

| Name | Description | Use Case |
|------|-------------|----------|
| badge-new | "NEW" badge | New products |
| badge-hot | "HOT" badge | Trending items |
| badge-sale | Sale/discount badge | Promotions |
| seal-quality | Quality seal | Recommendations |
| ribbon-award | Award ribbon | Best picks |
| tag-price | Price tag shape | Pricing info |

#### Style-Specific Decorations

##### Cute Style
- Hearts, stars, sparkles
- Ribbon decorations, sticker-style
- Cute character elements

##### Notion Style
- Simple line doodles
- Geometric shapes, stick figures
- Maximum whitespace, minimal decoration

##### Warm Style
- Sun rays, coffee cups, cozy items
- Warm lighting effects
- Friendly, inviting decorations

##### Fresh Style
- Plant leaves, clouds, water drops
- Simple geometric shapes
- Open, breathing composition

##### Bold Style
- Exclamation marks, arrows
- Warning icons, strong shapes
- High contrast elements

##### Pop Style
- Bold shapes, speech bubbles
- Comic-style effects, starburst
- Dynamic, energetic decorations

##### Retro Style
- Halftone dots, vintage badges
- Classic icons, tape effects
- Aged texture overlays

##### Chalkboard Style
- Chalk dust effects
- Hand-drawn doodles
- Mathematical formulas, simple icons

##### Screen-Print Style
- Bold silhouettes, geometric shapes
- Halftone dot patterns, print grain
- No doodles — negative space does the work
- Stencil-cut edges, color block boundaries
- Vintage poster border treatments

## image-effects

Visual effects applied to image elements in Xiaohongshu infographics.

#### AI Cutout (抠图)

Subject extraction styles for product/figure isolation.

| Name | Description | Use Case |
|------|-------------|----------|
| clean | Sharp edges, precise boundaries | Product photography, tech items |
| soft | Soft transition, feathered edges | Portrait cutout, organic subjects |
| stylized | Hand-drawn edge treatment | Artistic compositions |

#### Stroke Effects (描边)

Border treatments for cutout elements.

| Name | Description | Use Case |
|------|-------------|----------|
| white-solid | White solid line border | Classic sticker feel, high contrast |
| colored-solid | Colored solid line border | Playful vibe, brand colors |
| dashed | Dashed/dotted border | Handmade aesthetic, casual |
| double | Double-layer stroke | Emphasis effect, premium feel |
| glow | Soft outer glow | Dreamy, soft aesthetic |
| shadow | Drop shadow effect | Depth, floating element |

**Stroke Width Guidelines**:
- Thin: 2-4px - Subtle, elegant
- Medium: 5-8px - Standard visibility
- Thick: 10-15px - Bold emphasis

#### Filters (滤镜)

Color grading and mood presets popular on XHS.

| Name | Chinese | Description | Mood |
|------|---------|-------------|------|
| clear-glow | 清透感 | Transparent, radiant, luminous | Fresh, youthful |
| film-grain | 胶片感 | Vintage film aesthetic, grain texture | Nostalgic, artistic |
| cream-skin | 奶油肌 | Smooth, creamy complexion tones | Soft, flattering |
| japanese-magazine | 日杂感 | Lifestyle magazine aesthetic | Curated, aspirational |
| high-saturation | 高饱和 | Vibrant, punchy colors | Energetic, eye-catching |
| muted-tones | 莫兰迪 | Morandi-style desaturated palette | Sophisticated, calm |
| warm-tone | 暖色调 | Golden hour warmth | Cozy, inviting |
| cool-tone | 冷色调 | Blue-shifted coolness | Modern, clean |

#### Texture Overlays

Additional texture effects.

| Name | Description | Use Case |
|------|-------------|----------|
| paper | Paper or fabric texture | Handmade feel |
| noise | Fine grain noise | Analog aesthetic |
| halftone | Dot pattern | Retro print style |
| scratch | Light scratch marks | Vintage wear |

#### Blending Modes

For layered compositions.

| Mode | Effect | Use Case |
|------|--------|----------|
| multiply | Darken, merge | Shadow effects |
| screen | Lighten, glow | Light effects |
| overlay | Contrast boost | Vibrant compositions |
| soft-light | Subtle blending | Natural layering |

#### Effect Combinations

Common effect stacks for different styles:

##### Cute Style
- Filter: clear-glow or cream-skin
- Stroke: white-solid (medium)
- Texture: none

##### Notion Style
- Filter: none or muted-tones
- Stroke: white-solid (thin) or none
- Texture: paper (subtle)

##### Retro Style
- Filter: film-grain
- Stroke: double or dashed
- Texture: halftone, scratch

##### Bold Style
- Filter: high-saturation
- Stroke: colored-solid (thick)
- Texture: none

## typography

Text styling elements for Xiaohongshu infographics.

#### Decorated Text (花字)

Stylized text treatments for emphasis and visual appeal.

| Name | Description | Use Case |
|------|-------------|----------|
| gradient | Gradient color fill | Title emphasis, modern feel |
| stroke-text | Outlined text with stroke | Cover headlines, high visibility |
| shadow-3d | 3D shadow/extrusion effect | Key terms, depth |
| highlight | Highlighter marker effect | Critical information, key points |
| neon | Neon glow effect | Tech content, night aesthetic |
| handwritten | Authentic handwritten style | Personal touch, casual |
| bubble | Rounded, inflated letterforms | Cute, playful content |
| brush | Brush stroke texture | Artistic, dynamic |

#### Tags & Labels (标签)

Structured text containers.

| Name | Description | Use Case |
|------|-------------|----------|
| black-white | Black background, white text | Brand names, prices, categories |
| white-black | White background, black text | Clean labels, minimal style |
| bubble | Speech bubble style | Dialogue, annotations, callouts |
| pointer | Arrow pointer with label | Product callouts, pointing to features |
| ribbon | Ribbon/banner shape | Special offers, highlights |
| stamp | Stamp/seal style | Authenticity, recommendations |
| pill | Rounded pill shape | Tags, categories, keywords |

#### Text Hierarchy

Recommended text sizing for visual hierarchy.

| Level | Role | Relative Size | Style |
|-------|------|---------------|-------|
| H1 | Main title | 100% | Bold, decorated |
| H2 | Section header | 70-80% | Semi-bold |
| H3 | Subsection | 50-60% | Medium weight |
| Body | Content text | 40-50% | Regular |
| Caption | Small notes | 30-35% | Light |

#### Text Direction

| Direction | Description | Use Case |
|-----------|-------------|----------|
| horizontal | Standard left-to-right | Default for most content |
| vertical | Top-to-bottom columns | Magazine style, traditional Chinese |
| curved | Text following a curve | Decorative, around shapes |
| diagonal | Angled text | Dynamic compositions |

#### Text Effects

| Effect | Description | Use Case |
|--------|-------------|----------|
| shadow | Drop shadow behind text | Readability on busy backgrounds |
| outline | Outline around letterforms | High contrast visibility |
| glow | Soft glow around text | Dreamy, emphasis |
| underline-wavy | Wavy underline decoration | Playful emphasis |
| strikethrough | Crossed out text | Before/after, corrections |

#### Language Considerations

##### Chinese Text (中文)
- Punctuation: 「」（）、。！？
- Spacing: No spaces between characters
- Line height: 1.5-1.8x for readability

##### Mixed Text
- English in Chinese context: Maintain consistent baseline
- Numbers: Use consistent number style (lining vs old-style)

#### Style-Specific Typography

##### Cute Style
- Rounded, bubbly hand lettering
- Soft shadows, playful decorations
- Pink/pastel color accents

##### Notion Style
- Clean hand-drawn lettering
- Simple sans-serif labels
- Minimal decoration

##### Bold Style
- Impactful hand lettering with shadows
- High contrast colors
- Strong outlines

##### Chalkboard Style
- Chalk texture on all text
- Visible imperfections
- Multi-color chalk variety
