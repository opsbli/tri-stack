# 分类型布局细则（合订本）

> 逐类给出布局算法与排布规则；按命中的图类型读取对应小节（grep：`^## <类型名>`）。

## architecture


#### Flow Direction

Choose one primary direction:
- **Left-to-Right (LTR):** Best for data pipelines, request flows. Users/clients on left, data stores on right.
- **Top-to-Bottom (TTB):** Best for layered architectures. Clients at top, infrastructure at bottom.

#### Layout Algorithm

1. **Identify layers:** Group components by role (clients, gateways, services, data, infrastructure)
2. **Assign columns (LTR) or rows (TTB):** One layer per column/row
3. **Within each layer:** Stack components vertically (LTR) or horizontally (TTB), 40px gap minimum
4. **Region boundaries:** Draw around groups that share infrastructure (e.g., "AWS us-east-1", "Kubernetes Cluster")
5. **Connectors:** Route arrows between layers. For buses/queues between layers, place a thin connector bar in the gap.

#### Typical Layer Structure (LTR)

```
Col 1 (x=40)     Col 2 (x=250)     Col 3 (x=460)     Col 4 (x=670)
┌──────────┐     ┌──────────┐      ┌──────────┐      ┌──────────┐
│  Client   │────▶│ Gateway  │─────▶│ Services │─────▶│ Database │
│  Layer    │     │  Layer   │      │  Layer   │      │  Layer   │
└──────────┘     └──────────┘      └──────────┘      └──────────┘
```

Column spacing: 200-220px between column starts. Adjust if components are wider.

#### Typical Layer Structure (TTB)

```
Row 1 (y=60):   [ Browser ]  [ Mobile App ]  [ API Client ]
Row 2 (y=160):  [         Load Balancer / API Gateway       ]
Row 3 (y=280):  [ Auth Svc ]  [ User Svc ]  [ Order Svc ]
Row 4 (y=400):  [  Redis  ]   [ PostgreSQL ]  [ S3 Bucket ]
```

Row spacing: 120-140px between row starts.

#### Connection Routing

- Prefer straight horizontal or vertical lines
- For connections that would cross components, use two-segment (L-shaped) paths:
  ```svg
  <path d="M x1,y1 L midX,y1 L midX,y2" fill="none" stroke="#64748b" marker-end="url(#arrow)"/>
  ```
- For busy diagrams, use `stroke-opacity="0.6"` on less important connections
- Label important connections with a text element near the midpoint

#### Message Bus / Event Bus Pattern

When services communicate through a shared bus, draw it as a horizontal bar between the service layer:

```
Services:  [ Svc A ]    [ Svc B ]    [ Svc C ]
              │              │            │
Bus:     ════╪══════════════╪════════════╪═══════
              │              │            │
Data:    [ DB A ]        [ DB B ]     [ Cache ]
```

Use the Connector color (orange) for the bus bar.

#### Multi-Region / Multi-Cloud

Nest region boundaries:
- Outer boundary: Cloud provider (AWS, GCP)
- Inner boundary: Region or VPC
- Innermost: Availability zones or subnets

Use different dash patterns to distinguish nesting levels:
- Outer: `stroke-dasharray="12,4"`
- Middle: `stroke-dasharray="8,4"`
- Inner: `stroke-dasharray="4,4"`

## flowchart


#### Shape Vocabulary

| Shape | Meaning | SVG Element |
|-------|---------|-------------|
| Rounded rect (large radius) | Start / End | `<rect rx="25">` |
| Rectangle | Process / Action | `<rect rx="6">` |
| Diamond | Decision | `<polygon>` rotated 45° |
| Parallelogram | Input / Output | `<polygon>` with skew |
| Cylinder | Data store | Ellipse + rect combo |

#### Flow Direction

Primary flow: **top to bottom**. Branch flows go left/right from decisions.

#### Layout Algorithm

1. **Identify the main path** (happy path / most common flow) — this runs straight down the center
2. **Branch from decisions:** "Yes" continues down center, "No" branches right (or left if space is tight)
3. **Merge paths:** Route branches back to the main path using L-shaped connectors
4. **Loop-backs:** Route upward on the far left/right side of the diagram with curved paths

#### Spacing

- Step-to-step vertical gap: 60-80px (enough for arrow + optional label)
- Decision diamond height: 70px (point to point)
- Decision diamond width: 100px (point to point)
- Branch horizontal offset: 200px from center
- Merge connector clearance: 20px from any box

#### Decision Labels

Place "Yes" / "No" (or "True" / "False", "是" / "否") labels directly on the exit arrows, 10px from the diamond edge:

```svg
<!-- Decision diamond at center (400, 200) -->
<!-- Yes: downward -->
<line x1="400" y1="235" x2="400" y2="300" stroke="#64748b" marker-end="url(#arrow)"/>
<text x="412" y="260" fill="#34d399" font-size="8">Yes</text>

<!-- No: rightward -->
<line x1="450" y1="200" x2="550" y2="200" stroke="#64748b" marker-end="url(#arrow)"/>
<text x="480" y="193" fill="#fb7185" font-size="8">No</text>
```

#### Coloring Strategy

- **Start/End nodes:** Highlight color (blue)
- **Process steps:** Primary (cyan) or Secondary (emerald)
- **Decision diamonds:** Accent (amber) — they draw the eye naturally
- **Error/exception paths:** Alert (rose) dashed arrows
- **Happy path arrows:** Slightly brighter than branch arrows (`stroke-opacity` difference)

#### Complex Flowcharts

For flowcharts with 10+ steps:
- Group related steps into swim lanes (vertical columns with header bars)
- Add a "phase" row header at the top of each swim lane
- Use the region boundary pattern from Architecture for swim lanes

## sequence


#### Core Elements

| Element | Visual | Description |
|---------|--------|-------------|
| Actor/Participant | Box at top + dashed vertical lifeline | Each entity in the interaction |
| Sync message | Solid arrow → | Request or call |
| Async message | Open arrowhead → | Fire-and-forget |
| Return message | Dashed arrow ← | Response |
| Activation bar | Narrow filled rect on lifeline | Entity is processing |
| Self-message | Arrow looping back to same lifeline | Internal processing |
| Note | Rounded rect with folded corner | Annotation |
| Alt/Opt frame | Dashed boundary with label tab | Conditional block |
| Loop frame | Dashed boundary with "loop" tab | Repetition |

#### Layout Algorithm

1. **Place actors** horizontally across the top, evenly spaced (150-200px apart)
2. **Draw lifelines** as vertical dashed lines from each actor box downward
3. **Place messages** as horizontal arrows between lifelines, top to bottom in time order
4. **Vertical spacing** between messages: 40-50px
5. **Activation bars:** 10px wide, centered on lifeline, spanning from incoming to outgoing message

#### Actor Box

```svg
<!-- Actor box -->
<rect x="X" y="20" width="130" height="45" rx="6" fill="#0f172a"/>
<rect x="X" y="20" width="130" height="45" rx="6" fill="rgba(8,51,68,0.4)" stroke="#22d3ee" stroke-width="1.5"/>
<text x="CX" y="47" fill="white" font-size="11" font-weight="600" text-anchor="middle">Actor Name</text>

<!-- Lifeline -->
<line x1="CX" y1="65" x2="CX" y2="BOTTOM" stroke="#334155" stroke-width="1" stroke-dasharray="6,4"/>
```

#### Message Arrows

```svg
<!-- Sync message (solid arrow) -->
<line x1="FROM_CX" y1="Y" x2="TO_CX" y2="Y" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arrow)"/>
<text x="MID_X" y="Y-8" fill="#e2e8f0" font-size="9" text-anchor="middle">methodCall()</text>

<!-- Return message (dashed arrow, reversed direction) -->
<line x1="TO_CX" y1="Y" x2="FROM_CX" y2="Y" stroke="#64748b" stroke-width="1" stroke-dasharray="6,3" marker-end="url(#arrow)"/>
<text x="MID_X" y="Y-8" fill="#94a3b8" font-size="8" text-anchor="middle" font-style="italic">response</text>

<!-- Self-message (loop arrow) -->
<path d="M CX,Y L CX+40,Y L CX+40,Y+25 L CX,Y+25" fill="none" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arrow)"/>
<text x="CX+45" y="Y+15" fill="#e2e8f0" font-size="8">process()</text>
```

#### Activation Bar

```svg
<rect x="CX-5" y="START_Y" width="10" height="H" rx="2" fill="rgba(8,51,68,0.6)" stroke="#22d3ee" stroke-width="1"/>
```

#### Conditional / Loop Frames

```svg
<!-- Frame boundary -->
<rect x="X" y="Y" width="W" height="H" rx="4" fill="none" stroke="#64748b" stroke-width="1" stroke-dasharray="4,3"/>
<!-- Frame label tab -->
<rect x="X" y="Y" width="50" height="18" rx="4" fill="rgba(30,41,59,0.8)" stroke="#64748b" stroke-width="1"/>
<text x="X+25" y="Y+13" fill="#94a3b8" font-size="8" font-weight="600" text-anchor="middle">alt</text>
<!-- Condition text -->
<text x="X+60" y="Y+13" fill="#94a3b8" font-size="8" font-style="italic">[condition]</text>
<!-- Divider line for else -->
<line x1="X" y1="MID_Y" x2="X+W" y2="MID_Y" stroke="#64748b" stroke-width="1" stroke-dasharray="4,3"/>
<text x="X+10" y="MID_Y+13" fill="#94a3b8" font-size="8" font-style="italic">[else]</text>
```

#### Numbering

For complex sequences (8+ messages), number each message:

```svg
<circle cx="FROM_CX-15" cy="Y" r="8" fill="rgba(59,130,246,0.3)" stroke="#60a5fa" stroke-width="1"/>
<text x="FROM_CX-15" y="Y+3" fill="#60a5fa" font-size="7" font-weight="600" text-anchor="middle">1</text>
```

#### Color Assignment

Assign each actor a distinct color from the palette. Use that color for:
- Actor box stroke
- Activation bar on that lifeline
- Outgoing arrows from that actor (optional, for visual clarity in complex diagrams)

## structural


Covers: class diagrams, ER diagrams, component diagrams, package diagrams, org charts.

#### Class Diagram

##### Class Box (3-compartment)

```svg
<g transform="translate(X, Y)">
  <!-- Mask -->
  <rect width="180" height="120" rx="6" fill="#0f172a"/>
  <!-- Box -->
  <rect width="180" height="120" rx="6" fill="rgba(8,51,68,0.4)" stroke="#22d3ee" stroke-width="1.5"/>
  <!-- Class name compartment -->
  <text x="90" y="24" fill="white" font-size="11" font-weight="700" text-anchor="middle">ClassName</text>
  <!-- Divider 1 -->
  <line x1="0" y1="35" x2="180" y2="35" stroke="#22d3ee" stroke-width="0.5" stroke-opacity="0.5"/>
  <!-- Attributes -->
  <text x="10" y="52" fill="#94a3b8" font-size="8">- id: int</text>
  <text x="10" y="64" fill="#94a3b8" font-size="8">- name: string</text>
  <!-- Divider 2 -->
  <line x1="0" y1="75" x2="180" y2="75" stroke="#22d3ee" stroke-width="0.5" stroke-opacity="0.5"/>
  <!-- Methods -->
  <text x="10" y="92" fill="#94a3b8" font-size="8">+ getName(): string</text>
  <text x="10" y="104" fill="#94a3b8" font-size="8">+ setName(s: string)</text>
</g>
```

For abstract classes, italicize the class name. For interfaces, add `«interface»` above the name in smaller font.

##### Relationship Lines

| Relationship | Line Style | Arrow/End |
|-------------|------------|-----------|
| Inheritance | Solid | Empty triangle (▷) pointing to parent |
| Implementation | Dashed | Empty triangle pointing to interface |
| Composition | Solid | Filled diamond (◆) at owner end |
| Aggregation | Solid | Empty diamond (◇) at owner end |
| Dependency | Dashed | Open arrowhead at dependency target |
| Association | Solid | Open arrowhead or none |

**Markers:**

```svg
<!-- Inheritance triangle -->
<marker id="inherit" markerWidth="12" markerHeight="10" refX="12" refY="5" orient="auto">
  <polygon points="0 0, 12 5, 0 10" fill="#0f172a" stroke="#94a3b8" stroke-width="1.5"/>
</marker>

<!-- Composition diamond -->
<marker id="composition" markerWidth="12" markerHeight="8" refX="0" refY="4" orient="auto">
  <polygon points="0 4, 6 0, 12 4, 6 8" fill="#94a3b8"/>
</marker>

<!-- Aggregation diamond -->
<marker id="aggregation" markerWidth="12" markerHeight="8" refX="0" refY="4" orient="auto">
  <polygon points="0 4, 6 0, 12 4, 6 8" fill="#0f172a" stroke="#94a3b8" stroke-width="1.5"/>
</marker>
```

##### Cardinality Labels

Place at each end of the relationship line, offset 5-8px from the box edge:

```svg
<text x="X" y="Y" fill="#94a3b8" font-size="8">1..*</text>
```

#### ER Diagram

Similar to class diagrams but:
- Use 2-compartment boxes (entity name + attributes)
- Mark primary keys with `PK` prefix and bold
- Mark foreign keys with `FK` prefix
- Relationship lines use crow's foot notation:

```svg
<!-- One end (single line) -->
<line x1="X1" y1="Y" x2="X1+15" y2="Y" stroke="#94a3b8" stroke-width="1.5"/>
<!-- Many end (crow's foot) -->
<line x1="X2-15" y1="Y-6" x2="X2" y2="Y" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="X2-15" y1="Y+6" x2="X2" y2="Y" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="X2-15" y1="Y" x2="X2" y2="Y" stroke="#94a3b8" stroke-width="1.5"/>
```

#### Org Chart

- Top-down tree layout
- Root at top center
- Each level evenly spaced (100-120px vertical gap)
- Siblings evenly distributed horizontally
- Connection lines: vertical from parent bottom center to horizontal bar, then vertical down to each child top center
- Use color to indicate departments or hierarchy levels

#### Layout Tips

- Start by counting the widest level to determine total diagram width
- Center the tree horizontally in the viewBox
- For deep trees (5+ levels), consider horizontal layout instead
