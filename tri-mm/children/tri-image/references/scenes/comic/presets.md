# 体裁预设画廊（合订本）

> 本节由同目录下多个单页条目合订而成，保留全部原始内容与原条目名作为二级标题锚点。按命中条目读取对应小节（grep 模式：`^## <条目名>`），无需通篇加载。

## concept-story

概念故事预设 - Narrative comics that visualize abstract concepts through character-driven stories

#### Base Configuration

| Dimension | Value |
|-----------|-------|
| Art Style | manga |
| Tone | warm |
| Layout | standard (default) |

Equivalent to: `--art manga --tone warm`

#### Unique Rules

This preset includes special rules beyond the art+tone combination. When `--style concept-story` is used, ALL rules below must be applied.

##### Concept Visualization System (CRITICAL)

Each major abstract concept SHOULD have a recurring visual symbol/metaphor:

| Concept Type | Visualization Approach |
|-------------|----------------------|
| Psychological need | Tangible object character holds or discovers (e.g., glowing energy ball = competence) |
| Management principle | Environmental metaphor character navigates (e.g., ship wheel = autonomy) |
| Growth/development | Living organic symbol that transforms (e.g., seed → flowering plant = relatedness) |
| Abstract framework | Spatial structure characters can enter or observe |
| Emotional state | Color/lighting shift in the scene atmosphere |

**Unlike ohmsha**: Dialogue panels are allowed and expected. The goal is to COMBINE visual metaphors WITH dialogue, not replace dialogue entirely.

**Pattern**: "Dialogue introduces idea" → "Visual metaphor illustrates it" → "Character reacts/applies it"

##### Visual Symbol Continuity

Symbols must persist across the story:

| Stage | Treatment |
|-------|-----------|
| Introduction | Symbol appears with soft glow effect when concept is first mentioned |
| Recurrence | Same symbol reappears in background or character interaction when concept is referenced |
| Resolution | ALL symbols gather in the final composition, showing integration of learned concepts |

**Storyboard requirement**: Include a Symbol Mapping Table defining concept → visual symbol before panel breakdown.

##### Character Archetypes (Flexible)

Create original characters based on content domain. No fixed defaults:

| Role | Archetype | Visual Cues |
|------|-----------|------------|
| Protagonist | Learner/worker facing a challenge | Modern professional or student, relatable, starts with constrained posture |
| Mentor | Experienced guide who teaches through experience | Slightly older, calm demeanor, warm color accents |
| Catalyst | Person or event that triggers transformation | Can be a colleague, situation, challenge, or opportunity |

**IMPORTANT**: Characters are created fresh each time based on the source content's domain (business, psychology, education, etc.). No default character set.

##### Narrative Arc Structure

Enforce a five-stage growth arc:

| Act | Structure | Visual Tone |
|-----|-----------|------------|
| Opening | Protagonist stuck in routine, faces frustration | Muted warm tones, tight framing, constrained compositions |
| Inciting moment | Mentor appears or opportunity arrives | Brightness increases, panels open up |
| Learning | Concepts introduced through visual metaphors | Rich warm palette, symbols introduced one by one |
| Turning point | Protagonist applies knowledge, faces test | Contrast increases, dynamic compositions |
| Transformation | Growth demonstrated, new understanding visible | Full warm palette, expansive composition, all symbols present |

##### Dialogue + Action Balance

- Dialogue is encouraged and expected (unlike ohmsha's NO talking heads rule)
- Every page should combine at least one dialogue panel with at least one visual/action panel
- Avoid pure "lecture" pages where a character explains for 4+ panels straight
- When a character explains a concept verbally, the NEXT panel should visualize it

**Wrong approach**: Four consecutive panels of mentor lecturing at protagonist
**Right approach**: Mentor introduces concept → visual metaphor panel → protagonist reacts → applies understanding

##### Scene Atmosphere Rules

| Scene Type | Atmosphere |
|------------|-----------|
| Problem/frustration | Cool muted tones over warm base, tight framing, cluttered environment |
| Mentoring moment | Golden hour lighting, open composition, warm indoor glow |
| Concept visualization | Soft glow effects, clean simplified backgrounds, symbol spotlight |
| Growth/transformation | Warm light expanding outward, character posture opening up |
| Resolution | Full warm palette, spacious composition, all visual symbols visible |

##### Ending Requirements

Final page MUST include:

1. Protagonist demonstrating transformed understanding (not just being told)
2. Visual callback showing contrast with opening state (e.g., wilted plant → thriving plant)
3. All concept symbols visible together in the composition
4. A forward-looking element suggesting ongoing growth (not a closed ending)

##### Page Title Convention

Every page MUST have a narrative title:

**Wrong**: "Chapter 3: Self-Determination Theory"
**Right**: "The Day Xiao Ming Found His Own Engine"

#### Quality Markers

- ✓ Each major concept has a recurring visual symbol
- ✓ Dialogue and visual metaphors work together (not one replacing the other)
- ✓ Clear growth arc from problem to transformation
- ✓ Original characters suited to the content domain
- ✓ Warm, professional atmosphere throughout
- ✓ Visual symbols recur and accumulate through the story
- ✓ Final page integrates all concept symbols with transformation callback

#### Best For

Psychology concepts, business/management principles, motivation theory, personal development,
self-help content, leadership frameworks, coaching narratives, soft skill education,
abstract concept explanation through character-driven stories

## four-panel

四格漫画预设 - Minimalist four-panel business allegory comics

#### Base Configuration

| Dimension | Value |
|-----------|-------|
| Art Style | minimalist |
| Tone | neutral |
| Layout | four-panel (default) |
| Aspect | 4:3 (landscape) |

Equivalent to: `--art minimalist --tone neutral --layout four-panel --aspect 4:3`

#### Unique Rules

This preset includes special rules beyond the art+tone combination. When `--style four-panel` is used, ALL rules below must be applied.

##### 起承转合 Narrative Structure (CRITICAL)

Every comic MUST follow the four-panel 起承转合 structure:

| Panel | Role | Requirements |
|-------|------|-------------|
| 1 (起 Setup) | Introduce the situation | Show character(s) in a recognizable context. Establish the "normal" state or problem |
| 2 (承 Development) | Build on the setup | Add complication, show an attempt, or introduce the concept. Stakes become clearer |
| 3 (转 Turn) | The twist or key insight | **Most important panel.** Show the unexpected reversal, contrast, or "aha" moment that makes the allegory work |
| 4 (合 Conclusion) | Resolution and takeaway | Show the result, consequence, or lesson learned. Can be a visual punchline or summary |

**CRITICAL**: Do NOT deviate from exactly 4 panels. No 5th panel, no title panel, no footer panel within the image.

##### Single-Page Story Rule (CRITICAL)

- The entire story is told in ONE page with exactly 4 panels
- Page count: always 1 (plus optional cover)
- No multi-page four-panel stories — if content requires more, create multiple separate four-panel comics
- Storyboard structure: Cover (optional) + 1 page

##### Accent Color System

- The image is primarily black-and-white line art
- Use exactly 1-2 spot colors per strip (default: orange `#FF6B35`)
- Rules:
  - Key concept label or object: filled with accent color or outlined in accent
  - Panel 3 (转 Turn) should have the strongest color emphasis
  - Characters remain B&W — color is for concepts/objects/labels only
  - Consistent accent color across all 4 panels (do not switch colors between panels)

##### Character Design Rules

- Simplified stick-figure-like characters
- Distinguish characters through simple props: ties, glasses, hats, briefcases, aprons
- No detailed faces — dot eyes, line mouth at most
- Characters should be generic enough to represent archetypes (the manager, the employee, the customer)
- Maximum 2-3 characters per strip

##### Text in Panels

- Chinese text for dialogue and labels (or match source language)
- Keep text minimal — 1-2 short lines per panel maximum
- Key concept terms can be highlighted with accent color background
- No narrator boxes — dialogue and labels only
- Speech bubbles: simple rectangles or ovals, thin black outline

##### Optional Title & Caption

- A brief descriptive title above the 4 panels
- An optional one-line caption/moral below the panels
- These are part of the page composition, not separate panels

##### Character Archetypes (Flexible)

Create simple stick-figure characters based on content. No fixed defaults:

| Role | Archetype | Visual Cues |
|------|-----------|------------|
| Protagonist | Worker/employee facing a situation | Simple figure, minimal distinguishing feature (glasses, tie) |
| Authority | Boss/manager/expert | Slightly larger figure, or prop like pointer/clipboard |
| Object | The concept itself | Labeled object, icon, or highlighted text with accent color |

##### Prompt Template

When generating image prompts for four-panel comics, include these keywords:

> A minimalist, clean line art digital comic strip in a four-panel grid layout (2×2). The style is simplified cartoon illustration with clear black outlines and a minimal color palette of black, white, and specific spot [accent color] for key concepts.

Each panel description should specify:
- Panel position (Top Left / Top Right / Bottom Left / Bottom Right)
- Character poses and gestures (simple, stick-figure style)
- Dialogue text in Chinese (hand-drawn style)
- Any accent-colored elements (concept labels, key objects)

#### Quality Markers

- ✓ Exactly 4 panels in strict 2×2 grid
- ✓ 起承转合 narrative arc clearly present
- ✓ 90%+ black-and-white with strategic spot color
- ✓ Simplified stick-figure characters
- ✓ Key concept visually highlighted with accent color
- ✓ Text is minimal and in Chinese (or source language)
- ✓ Single complete story in one page
- ✓ Panel 3 delivers a clear "turn" or insight

#### Best For

Business allegory, management fables, short insights, workplace parables, concept contrasts, social media educational content, quick-read comics

## ohmsha

Ohmsha预设 - Educational manga with visual metaphors

#### Base Configuration

| Dimension | Value |
|-----------|-------|
| Art Style | manga |
| Tone | neutral |
| Layout | webtoon (default) |

Equivalent to: `--art manga --tone neutral`

#### Unique Rules

This preset includes special rules beyond the art+tone combination. When `--style ohmsha` is used, ALL rules below must be applied.

##### Visual Metaphor Requirements (CRITICAL)

Every technical concept MUST be visualized as a metaphor:

| Concept Type | Visualization Approach |
|-------------|----------------------|
| Algorithm | Gadget/machine that demonstrates the process |
| Data structure | Physical space characters can enter/explore |
| Mathematical formula | Transformation visible in environment |
| Abstract process | Tangible flow of particles/objects |

**Wrong approach**: Character points at blackboard explaining
**Right approach**: Character uses "Concept Visualizer" gadget, steps into metaphorical space

##### Visual Metaphor Examples

| Concept | Wrong (Talking Head) | Right (Visual Metaphor) |
|---------|---------------------|------------------------|
| Attention mechanism | Character points at formula on blackboard | "Attention Flashlight" gadget illuminates key words in dark room |
| Gradient descent | "The algorithm minimizes loss" | Character rides ball rolling down mountain valley |
| Neural network | Diagram with arrows | Living network of glowing creatures passing messages |
| Overfitting | "The model memorized the data" | Character wearing clothes that fit only one specific pose |

##### Character Roles (Required)

**DEFAULT: Use Doraemon characters** unless user explicitly specifies `--characters` or has character presets in EXTEND.md.

| Role | Default Character | Visual | Traits |
|------|-------------------|--------|--------|
| Student (Role A) | 大雄 (Nobita) | Boy, 10yo, round glasses, black hair, yellow shirt, navy shorts | Confused, asks basic but crucial questions, represents reader |
| Mentor (Role B) | 哆啦A梦 (Doraemon) | Blue robot cat, white belly, 4D pocket, red nose, golden bell | Knowledgeable, patient, uses gadgets as technical metaphors |
| Challenge (Role C) | 胖虎 (Gian) | Stocky boy, small eyes, orange shirt | Represents misunderstanding, or "noise" in the data |
| Support (Role D) | 静香 (Shizuka) | Cute girl, black short hair, pink dress | Asks clarifying questions, provides alternative perspectives |

**IMPORTANT**: These Doraemon characters ARE the default for ohmsha preset. Generate character definitions using these exact characters unless user requests otherwise.

To use custom characters: `--characters "Student:小明,Mentor:教授"` or define in EXTEND.md.

##### Page Title Convention

Every page MUST have a narrative title (not section header):

**Wrong**: "Chapter 1: Introduction to Transformers"
**Right**: "The Day Nobita Couldn't Understand Anyone"

##### Gadget Reveal Pattern

When introducing a concept:

1. Student expresses confusion with visual indicator (？, spiral eyes)
2. Mentor dramatically produces gadget with sparkle effects
3. Gadget name announced in bold with explanation
4. Demonstration begins - student enters metaphorical space

##### Ending Requirements

Final page MUST include:

1. Student demonstrating understanding (applying the concept)
2. Callback to opening problem (now resolved)
3. Mentor's satisfied expression
4. Optional: hint at next topic

##### NO Talking Heads Rule

**Critical**: Characters must DO things, not just explain.

Every panel should show:
- Action being performed
- Metaphor being demonstrated
- Character interaction with concept-space
- NOT: two characters facing each other talking

##### Special Visual Elements

| Element | Usage |
|---------|-------|
| Gadget reveals | Dramatic unveiling with sparkle effects |
| Concept spaces | Rounded borders, glowing edges for "imagination mode" |
| Information displays | Holographic UI style for technical details |
| Aha moments | Radial lines, light burst effects |
| Confusion | Spiral eyes, question marks floating above head |

#### Quality Markers

- ✓ Every concept is a visual metaphor
- ✓ Characters are DOING things, not just talking
- ✓ Clear student/mentor dynamic
- ✓ Gadgets and props drive the explanation
- ✓ Expressive manga-style emotions
- ✓ Information density through visual design, not text walls
- ✓ Narrative page titles

#### Reference

For complete guidelines, see `references/ohmsha-guide.md`

## shoujo

少女预设 - Classic shoujo manga with romantic aesthetics

#### Base Configuration

| Dimension | Value |
|-----------|-------|
| Art Style | manga |
| Tone | romantic |
| Layout | standard (default) |

Equivalent to: `--art manga --tone romantic`

#### Unique Rules

This preset includes special rules beyond the art+tone combination. When `--style shoujo` is used, ALL rules below must be applied.

##### Decorative Elements (Required)

Every emotional moment must include decorative elements:

| Emotion | Required Decorations |
|---------|---------------------|
| Love | Floating hearts, sparkles, rose petals |
| Longing | Feathers, bubbles, distant sparkles |
| Joy | Flowers blooming, light bursts, stars |
| Sadness | Falling petals, fading sparkles |
| Shyness | Soft sparkles, floating bubbles |
| Realization | Radiating lines with sparkles |

##### Eye Detail Requirements

Eyes are critical in shoujo style:

| Aspect | Treatment |
|--------|-----------|
| Size | Larger than standard manga (1.2x) |
| Highlights | Multiple (3-5), placed for emotion |
| Reflection | Scene reflection in emotional moments |
| Sparkle | Built-in sparkle effects |
| Tears | Crystalline, detailed teardrops |

##### Character Beauty Standards

| Feature | Treatment |
|---------|-----------|
| Hair | Flowing, detailed strands, shine highlights |
| Skin | Porcelain, soft blush on cheeks |
| Lips | Soft, slightly glossy |
| Hands | Elegant, expressive gestures |
| Posture | Graceful, elegant poses |

##### Background Effects

**Abstract backgrounds** for emotional moments:

| Moment Type | Background |
|-------------|-----------|
| Love confession | Soft gradient + floating flowers |
| Shock | Screen tone speed lines + sparkles |
| Memory | Dreamy blur + scattered petals |
| Realization | Radial lines + light burst |
| Intimate | Soft focus + floating elements |

##### Panel Flow

- Overlap panels for intimate moments
- Break panel borders for emotional impact
- Float decorative elements between panels
- Use screen tone gradients for mood
- Irregular panel shapes for drama

##### Emotional Beat Timing

Slow down pacing for emotional impact:

| Scene Type | Panel Treatment |
|------------|-----------------|
| Confession | Multiple small panels, then splash |
| Eye contact | Close-up sequence |
| Touch | Slow-motion panel breakdown |
| Realization | Build-up panels then impact |

##### Color Palette Application

| Scene Type | Palette |
|------------|---------|
| Romantic | Pink, lavender, rose gold |
| Happy | Soft yellow, peach, sky blue |
| Sad | Pale blue, silver, gray lavender |
| Dramatic | Deep rose, purple, contrast |

##### Screen Tone Usage

| Mood | Tone Pattern |
|------|-------------|
| Neutral | Clean, minimal |
| Romantic | Soft gradient overlays |
| Dramatic | Heavy contrast tones |
| Dreamy | Soft dot patterns |

#### Quality Markers

- ✓ Large, sparkling detailed eyes
- ✓ Decorative elements in emotional moments
- ✓ Flowing, beautiful character designs
- ✓ Soft, pastel color palette
- ✓ Elegant panel compositions
- ✓ Screen tone mood effects
- ✓ Romantic atmosphere throughout
- ✓ Beautiful, expressive poses

#### Best For

Romance stories, coming-of-age, friendship narratives, school life, emotional drama, love stories

## wuxia

武侠预设 - Hong Kong martial arts comic style

#### Base Configuration

| Dimension | Value |
|-----------|-------|
| Art Style | ink-brush |
| Tone | action |
| Layout | splash (default) |

Equivalent to: `--art ink-brush --tone action`

#### Unique Rules

This preset includes special rules beyond the art+tone combination. When `--style wuxia` is used, ALL rules below must be applied.

##### Qi/Energy Effects (Required)

Martial arts power must be visible through qi effects:

| Effect Type | Visual Treatment |
|-------------|-----------------|
| Internal qi | Glowing aura around character |
| External qi | Visible energy projection |
| Qi clash | Radiating impact waves |
| Qi absorption | Flowing particles toward character |
| Hidden power | Subtle glow in eyes/fists |

##### Energy Colors

| Qi Type | Color |
|---------|-------|
| Righteous | Blue (#4299E1), Gold (#FFD700) |
| Fierce | Red (#DC2626), Orange (#EA580C) |
| Evil | Purple (#7C3AED), Green (#16A34A) |
| Pure | White, Silver |
| Ancient | Gold with particles |

##### Combat Visual Language

**Impact moments** must include:

1. Speed lines radiating from impact point
2. Flying debris (stone, wood, cloth)
3. Shockwave rings
4. Dust/energy clouds
5. Hair and clothing blown back

##### Movement Depiction

| Speed Level | Visual Treatment |
|-------------|-----------------|
| Normal | Standard pose |
| Fast | Motion blur, speed lines |
| Lightning | Afterimages, multiple positions |
| Teleport | Fade effect, particle trail |

##### Environmental Integration

Backgrounds must support action:

| Environment | Combat Enhancement |
|-------------|-------------------|
| Mountains | Crumbling peaks from impacts |
| Forest | Exploding trees, flying leaves |
| Water | Dramatic splashes, walking on water |
| Temple | Breaking pillars, flying tiles |
| Cliff | Dramatic falls, wind effects |

##### Character Pose Guidelines

- Dynamic warrior stances with weight distribution
- Flowing robes and hair showing movement
- Muscle tension visible in action
- Feet planted or in dynamic motion
- Traditional martial arts postures

##### Weapon Effects

| Weapon | Visual Treatment |
|--------|-----------------|
| Sword | Trailing light arc, blade glow |
| Palm | Qi projection, wind effect |
| Staff | Spinning blur, impact ripples |
| Whip | Flowing energy trail |

##### Atmospheric Elements

Always include:
- Floating particles (leaves, petals, dust)
- Ink wash mist for depth
- Wind direction indicators
- Dramatic sky/weather when appropriate

#### Quality Markers

- ✓ Dynamic action poses with sense of motion
- ✓ Ink brush aesthetic in line work
- ✓ Visible qi/energy effects
- ✓ High contrast dramatic lighting
- ✓ Atmospheric backgrounds with Chinese elements
- ✓ Flowing fabric and hair movement
- ✓ Impactful combat moments
- ✓ Speed lines and impact effects

#### Best For

Martial arts stories, Chinese historical fiction, wuxia/xianxia adaptations, action-heavy narratives
