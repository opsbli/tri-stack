# 维度档位画廊（合订本）

> 本节由同目录下多个单页条目合订而成，保留全部原始内容与原条目名作为二级标题锚点。按命中条目读取对应小节（grep 模式：`^## <条目名>`），无需通篇加载。

## density

Information density per slide.

#### Options

| Option | Content/Slide | Whitespace | Best For |
|--------|---------------|------------|----------|
| `minimal` | One focus point | Maximum | Executive briefings, keynotes, emotional impact |
| `balanced` | 2-3 key points | Standard | General presentations, mixed audiences |
| `dense` | Multiple data points | Compact | Data-heavy, technical reviews, detailed analysis |

#### Rendering Guidelines

##### minimal

- ONE main idea per slide
- Large visuals dominate
- Minimal text (headline + 1-2 lines max)
- Generous margins (15%+ from edges)
- Maximum breathing room between elements
- Let single element carry full weight

**Principles**:
- "One slide, one message"
- Visual > text
- Empty space is intentional
- Every element must earn its space

##### balanced

- 2-3 key points per slide
- Standard margins (10% from edges)
- Balanced text/visual ratio
- Clear hierarchy with supporting details
- Comfortable reading experience

**Principles**:
- Primary point + supporting context
- Visuals complement text
- Structured but not crowded
- Good for diverse audiences

##### dense

- Multiple data points acceptable
- Compact margins (5-8% from edges)
- Information-rich layouts
- Charts, tables, detailed annotations
- Assume engaged, attentive audience

**Principles**:
- Data speaks louder than decoration
- Annotations explain insights
- White space is strategic
- Every pixel serves a purpose

#### Audience → Density Mapping

| Audience | Recommended Density |
|----------|-------------------|
| Executives | minimal |
| Beginners | minimal to balanced |
| General | balanced |
| Intermediate | balanced |
| Experts | balanced to dense |

#### Slide Type → Density Guidelines

| Slide Type | Recommended Density |
|------------|-------------------|
| Cover/Title | minimal |
| Section break | minimal |
| Quote/Impact | minimal |
| Agenda/Overview | balanced |
| Content/Analysis | balanced or dense |
| Summary/Takeaway | balanced |
| Data/Metrics | dense |

#### Content Guidelines Per Density

##### minimal

| Element | Guideline |
|---------|-----------|
| Headlines | Large (40-60pt equivalent) |
| Body text | Minimal or none |
| Bullet points | 0-2 max |
| Visual elements | 1 dominant element |
| Charts/Data | 1 key stat only |

##### balanced

| Element | Guideline |
|---------|-----------|
| Headlines | Medium-large (32-48pt equivalent) |
| Body text | 2-4 lines |
| Bullet points | 2-4 |
| Visual elements | 1-2 elements |
| Charts/Data | Simple charts OK |

##### dense

| Element | Guideline |
|---------|-----------|
| Headlines | Medium (24-36pt equivalent) |
| Body text | Multiple paragraphs OK |
| Bullet points | 4-6+ |
| Visual elements | Multiple allowed |
| Charts/Data | Complex charts, tables OK |

#### Combination Notes

| Density | Works Best With | Avoid With |
|---------|-----------------|------------|
| minimal | neutral mood, geometric typography | dense data content |
| balanced | any mood/typography | extremes (too sparse or too packed) |
| dense | cool mood, technical typography | handwritten typography, organic texture |

## mood

Color temperature and palette style.

#### Options

| Option | Color Temperature | Palette Style | Best For |
|--------|-------------------|---------------|----------|
| `professional` | Cool-neutral | Navy, gold, structured grays | Business, investor, corporate |
| `warm` | Warm | Earth tones, oranges, natural colors | Education, friendly, approachable |
| `macaron` | Warm | Pastel blocks (blue, mint, lavender, peach) on cream | Educational diagrams, knowledge sharing |
| `cool` | Cool | Blues, grays, cyan, teal | Technical, data, analytical |
| `vibrant` | Varied | High saturation, bold colors | Marketing, creative, attention-grabbing |
| `dark` | Dark | Deep backgrounds with bright accents | Entertainment, gaming, atmospheric |
| `neutral` | Neutral | Minimal color, grayscale focus | Executive, minimal, sophisticated |

#### Palette Specifications

##### professional

```
Background: #FFFFFF (Pure White)
Primary Text: #1E3A5F (Navy)
Secondary Text: #4A5568 (Dark Gray)
Accent 1: #C9A227 (Gold)
Accent 2: #3D5A80 (Light Navy)
```

##### warm

```
Background: #FAF8F0 (Warm Off-White)
Primary Text: #2C3E50 (Deep Charcoal)
Secondary Text: #4A4A4A (Deep Brown)
Accent 1: #F4A261 (Soft Orange)
Accent 2: #E9C46A (Mustard Yellow)
Accent 3: #87A96B (Sage Green)
```

##### macaron

```
Background: #F5F0E8 (Warm Cream)
Primary Text: #2D2D2D (Deep Charcoal)
Muted Text: #6B6B6B (Warm Gray)
Macaron Blue: #A8D8EA (Sky Blue)
Macaron Mint: #B5E5CF (Mint Green)
Macaron Lavender: #D5C6E0 (Lavender)
Macaron Peach: #FFD5C2 (Peach)
Accent: #E8655A (Coral Red)
```

##### cool

```
Background: #FAF8F5 (Blueprint Off-White)
Primary Text: #334155 (Deep Slate)
Secondary Text: #64748B (Slate Gray)
Accent 1: #2563EB (Engineering Blue)
Accent 2: #1E3A5F (Navy Blue)
Accent 3: #BFDBFE (Light Blue)
```

##### vibrant

```
Background: #FFFFFF or #1A1A2E (Light or Dark)
Primary Text: #1A1A2E or #FFFFFF
Accent 1: #E94560 (Coral Red)
Accent 2: #0F3460 (Deep Blue)
Accent 3: #16C79A (Teal Green)
Accent 4: #F9B208 (Golden Yellow)
```

##### dark

```
Background: #0D1117 (Deep Black)
Primary Text: #E6EDF3 (Soft White)
Secondary Text: #8B949E (Muted Gray)
Accent 1: #58A6FF (Bright Blue)
Accent 2: #7EE787 (Bright Green)
Accent 3: #FF7B72 (Coral)
```

##### neutral

```
Background: #FFFFFF (Pure White)
Primary Text: #18181B (Near Black)
Secondary Text: #71717A (Medium Gray)
Accent 1: #18181B (Black)
Accent 2: #A1A1AA (Light Gray)
```

#### Rendering Guidelines

##### professional

- Restrained use of accent colors
- Gold for emphasis only
- Clean, institutional feel
- Balanced contrast

##### warm

- Generous use of warm tones
- Natural, approachable colors
- Soft transitions between colors
- Welcoming atmosphere

##### macaron

- Soft pastel color blocks as distinct information zones
- Each zone uses one macaron color (blue, mint, lavender, peach)
- Coral Red accent used sparingly for emphasis
- Warm cream background maintains friendly, approachable feel

##### cool

- Blue-dominant palette
- Technical precision in color use
- High contrast for clarity
- Analytical, trustworthy feel

##### vibrant

- Bold color combinations
- High saturation throughout
- Dynamic color contrasts
- Energetic visual presence

##### dark

- Deep backgrounds dominate
- Accent colors pop against dark
- Glowing/luminous effects
- Cinematic atmosphere

##### neutral

- Minimal color usage
- Typography carries weight
- Grayscale hierarchy
- Maximum sophistication

#### Combination Notes

| Mood | Works Best With | Avoid With |
|------|-----------------|------------|
| professional | clean texture, geometric typography | organic texture, handwritten |
| warm | organic texture, humanist typography | pixel texture, minimal density |
| macaron | organic texture, handwritten typography | pixel texture, dark mood |
| cool | grid texture, technical typography | paper texture, handwritten |
| vibrant | pixel/organic texture, editorial typography | neutral mood overlaps |
| dark | clean/pixel texture, technical typography | paper texture |
| neutral | clean texture, geometric typography | organic texture, vibrant elements |

## presets

Maps 16 preset styles to their dimension combinations.

#### Mapping Table

| Preset | Texture | Mood | Typography | Density |
|--------|---------|------|------------|---------|
| blueprint | grid | cool | technical | balanced |
| chalkboard | organic | warm | handwritten | balanced |
| corporate | clean | professional | geometric | balanced |
| minimal | clean | neutral | geometric | minimal |
| sketch-notes | organic | warm | handwritten | balanced |
| hand-drawn-edu | organic | macaron | handwritten | balanced |
| watercolor | organic | warm | humanist | minimal |
| dark-atmospheric | clean | dark | editorial | balanced |
| notion | clean | neutral | geometric | dense |
| bold-editorial | clean | vibrant | editorial | balanced |
| editorial-infographic | clean | cool | editorial | dense |
| fantasy-animation | organic | vibrant | handwritten | minimal |
| intuition-machine | clean | cool | technical | dense |
| pixel-art | pixel | vibrant | technical | balanced |
| scientific | clean | cool | technical | dense |
| vector-illustration | clean | vibrant | humanist | balanced |
| vintage | paper | warm | editorial | balanced |

#### Preset Details

##### blueprint
- **Dimensions**: grid + cool + technical + balanced
- **Feel**: Engineering precision, analytical clarity
- **Auto-select**: architecture, system, data, analysis, technical

##### chalkboard
- **Dimensions**: organic + warm + handwritten + balanced
- **Feel**: Classroom warmth, educational
- **Auto-select**: classroom, teaching, school, chalkboard

##### corporate
- **Dimensions**: clean + professional + geometric + balanced
- **Feel**: Business credibility, institutional trust
- **Auto-select**: investor, quarterly, business, corporate

##### minimal
- **Dimensions**: clean + neutral + geometric + minimal
- **Feel**: Maximum sophistication, executive focus
- **Auto-select**: executive, minimal, clean, simple

##### sketch-notes
- **Dimensions**: organic + warm + handwritten + balanced
- **Feel**: Friendly learning, approachable education
- **Auto-select**: tutorial, learn, education, guide, beginner

##### hand-drawn-edu
- **Dimensions**: organic + macaron + handwritten + balanced
- **Feel**: Hand-drawn educational infographic, macaron pastel zones
- **Auto-select**: hand-drawn, infographic, diagram, process, onboarding

##### watercolor
- **Dimensions**: organic + warm + humanist + minimal
- **Feel**: Artistic, natural, lifestyle
- **Auto-select**: lifestyle, wellness, travel, artistic

##### dark-atmospheric
- **Dimensions**: clean + dark + editorial + balanced
- **Feel**: Cinematic, entertainment
- **Auto-select**: entertainment, music, gaming, atmospheric

##### notion
- **Dimensions**: clean + neutral + geometric + dense
- **Feel**: SaaS professional, data-forward
- **Auto-select**: saas, product, dashboard, metrics

##### bold-editorial
- **Dimensions**: clean + vibrant + editorial + balanced
- **Feel**: Magazine impact, keynote drama
- **Auto-select**: launch, marketing, keynote, magazine

##### editorial-infographic
- **Dimensions**: clean + cool + editorial + dense
- **Feel**: Publication quality, informative
- **Auto-select**: explainer, journalism, science communication

##### fantasy-animation
- **Dimensions**: organic + vibrant + handwritten + minimal
- **Feel**: Magical, storytelling
- **Auto-select**: story, fantasy, animation, magical

##### intuition-machine
- **Dimensions**: clean + cool + technical + dense
- **Feel**: Technical briefing, bilingual documentation
- **Auto-select**: briefing, academic, research, bilingual

##### pixel-art
- **Dimensions**: pixel + vibrant + technical + balanced
- **Feel**: Retro gaming, developer culture
- **Auto-select**: gaming, retro, pixel, developer

##### scientific
- **Dimensions**: clean + cool + technical + dense
- **Feel**: Academic precision, research quality
- **Auto-select**: biology, chemistry, medical, scientific

##### vector-illustration
- **Dimensions**: clean + vibrant + humanist + balanced
- **Feel**: Flat design, friendly creative
- **Auto-select**: creative, children, kids, cute

##### vintage
- **Dimensions**: paper + warm + editorial + balanced
- **Feel**: Historical, heritage storytelling
- **Auto-select**: history, heritage, vintage, expedition

#### Building Custom Combinations

When user selects "Custom dimensions", combine any:

- **Texture** (5): clean, grid, organic, pixel, paper
- **Mood** (6): professional, warm, cool, vibrant, dark, neutral
- **Typography** (5): geometric, humanist, handwritten, editorial, technical
- **Density** (3): minimal, balanced, dense

Total possible combinations: 5 × 7 × 5 × 3 = **525 unique styles**

#### Recommended Combinations (Beyond Presets)

| Custom Name | Texture | Mood | Typography | Density | Use Case |
|-------------|---------|------|------------|---------|----------|
| tech-minimal | clean | neutral | technical | minimal | Developer keynotes |
| warm-editorial | paper | warm | editorial | balanced | Heritage brands |
| dark-technical | grid | dark | technical | dense | Security, DevOps |
| playful-clean | clean | vibrant | humanist | balanced | Startups, apps |

## texture

Visual texture and background treatment.

#### Options

| Option | Background | Visual Elements | Best For |
|--------|------------|-----------------|----------|
| `clean` | Pure solid color, no texture | Clean lines, geometric shapes | Executive, minimal, corporate |
| `grid` | Subtle grid overlay | Grid lines, schematics, technical diagrams | Technical, architecture, engineering |
| `organic` | Soft textures, hand-drawn feel | Brush strokes, watercolor, sketchy lines | Creative, educational, friendly |
| `pixel` | Chunky pixels, 8-bit aesthetic | Pixel art, retro game elements | Gaming, developer, nostalgic |
| `paper` | Aged/textured paper | Vintage elements, stamps, weathering | Historical, heritage, storytelling |

#### Rendering Guidelines

##### clean

- Solid background colors with no visible texture
- Crisp, sharp edges on all elements
- Digital precision and clarity
- Maximum contrast for readability

##### grid

- Light grid overlay (5-10% opacity)
- Engineering paper or blueprint feel
- Alignment guides visible but subtle
- Technical drawing aesthetic

##### organic

- Paper grain or canvas texture
- Imperfect edges, natural variations
- Hand-painted color fills
- Casual, approachable feel

##### pixel

- Visible pixel grid (chunky, not fine)
- 8-bit color palette aesthetic
- Aliased edges (no smoothing)
- Retro game UI elements

##### paper

- Aged paper texture (subtle creases, discoloration)
- Vintage printing artifacts
- Sepia or warm tones
- Historical document feel

#### Combination Notes

| Texture | Works Best With | Avoid With |
|---------|-----------------|------------|
| clean | professional, neutral moods | handwritten typography |
| grid | cool, professional moods | handwritten, vibrant moods |
| organic | warm, macaron, vibrant moods | technical typography |
| pixel | vibrant, dark moods | editorial typography |
| paper | warm moods | geometric typography, minimal density |

## typography

Headline and body text styling.

#### Options

| Option | Headline Style | Body Style | Best For |
|--------|----------------|------------|----------|
| `geometric` | Modern sans-serif, clean angles | Clean sans-serif | Corporate, tech, modern |
| `humanist` | Friendly sans-serif, warm curves | Readable sans-serif | Education, general audiences |
| `handwritten` | Marker/brush, organic feel | Casual script or print | Creative, sketch, friendly |
| `editorial` | Bold serif/sans mix, magazine style | Classic serif | Keynote, magazine, premium |
| `technical` | Monospace accents, precise | Clean sans-serif | Developer, data, engineering |

#### Rendering Guidelines

##### geometric

**Headlines**: Modern geometric sans-serif with clean angles and consistent stroke width. Think Futura, Avenir, or Proxima Nova. Bold to semi-bold weight. Perfect circles in O, G characters.

**Body**: Clean sans-serif optimized for readability. Regular weight. Consistent x-height. Sufficient letter spacing.

**Characteristics**:
- Mathematical precision in letterforms
- Consistent stroke widths
- Perfect geometry in curves
- Modern, authoritative presence

##### humanist

**Headlines**: Friendly sans-serif with subtle stroke variations. Think Frutiger, Open Sans, or Myriad. Medium to semi-bold weight. Warm, approachable letterforms.

**Body**: Readable humanist sans-serif. Comfortable line height. Slight calligraphic influence.

**Characteristics**:
- Warm, approachable feel
- Subtle stroke contrast
- Open counters for readability
- Natural, human touch

##### handwritten

**Headlines**: Bold hand-written marker or brush lettering. Thick strokes with organic edges. Slightly uneven baseline. Render as actual hand-drawn letters.

**Body**: Clear handwritten style mimicking notes. Casual but legible. Natural variation in letter forms.

**Characteristics**:
- Organic, imperfect letterforms
- Visible brush/pen character
- Casual, personal feel
- NOT computer fonts - actual drawn letters

##### editorial

**Headlines**: Bold serif or high-contrast sans-serif. Magazine cover style. Dramatic scale contrast. Think Playfair Display, Didot, or bold condensed sans.

**Body**: Classic serif for extended reading. Elegant, refined letterforms. Traditional publishing quality.

**Characteristics**:
- High contrast (thick/thin strokes)
- Dramatic headlines
- Sophisticated presence
- Premium, publication quality

##### technical

**Headlines**: Clean sans-serif with monospace accents for data/code. Precise, engineered appearance. Think SF Mono for code, Inter for headers.

**Body**: Clean sans-serif optimized for technical content. Fixed-width for numbers and code.

**Characteristics**:
- Monospace for data elements
- Precise alignment
- Clear number distinction (0 vs O, 1 vs l)
- Engineering precision

#### Font Rendering Instructions

Since image generators cannot use font names, describe visual characteristics:

| Option | Headline Description | Body Description |
|--------|---------------------|------------------|
| geometric | "bold geometric sans-serif with perfect circular O shapes" | "clean modern sans-serif" |
| humanist | "friendly rounded sans-serif with warm letterforms" | "readable humanist sans-serif" |
| handwritten | "bold hand-drawn marker lettering with organic strokes" | "casual handwritten notes style" |
| editorial | "dramatic high-contrast serif with thick-thin stroke variation" | "elegant classic serif" |
| technical | "precise sans-serif with monospace numbers" | "technical sans-serif, fixed-width for code" |

#### Combination Notes

| Typography | Works Best With | Avoid With |
|------------|-----------------|------------|
| geometric | clean texture, professional/neutral mood | organic texture |
| humanist | organic/clean texture, warm mood | pixel texture |
| handwritten | organic/paper texture, warm/vibrant mood | grid texture, professional mood |
| editorial | clean texture, vibrant/professional mood | pixel texture |
| technical | grid/clean texture, cool/dark mood | paper texture, warm mood |
