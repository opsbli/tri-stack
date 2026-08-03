## Knowledge base (full model: `ARCHITECTURE.md`)
**Artifacts** are global, foldered by **kind** — `signals/` (feedback, ideas, observations) and
`docs/` (durable knowledge: analyses, decisions, learnings). Committed work starts as a backlog
line in the owning domain's `README`; promote to a `task` kind only once that outgrows the
README. `domain:` is a frontmatter field (a list), never a folder. **Domains**
(`domains/*/`) are agent loops whose `README` holds the loop's **state** — goal/context, current
focus, a `## Timeline`, and **links** to its artifacts (it points to them, never contains them).
Body = main text + optional append-only `## Timeline`. Each folder's `README` is its schema.

**Reuse before creating** (earn the structure, don't pre-build):
- **Kind** — start with just `signal` + `doc`. Add a new kind only if it has its own status
  machine **and** queryable fields **and** body shape. Otherwise it's a `doc` or a `signal`.
- **Domain** — default to a `domain:` tag on an existing one; spin up a new domain only when
  it's a separable workstream with its own cadence/owner (use the `new-loop` skill).

- **`LOG.md`** — global feed; **append ONE line right before the commit/PR that ships major
  work** (`## YYYY-MM-DD · title · #tags` + `What:`/`Refs:`). Detail → each artifact's `## Timeline`.

Kinds (now): signal + doc.
Domains (now): {{LIST_YOUR_LOOPS — or "none yet; run new-loop to create the first"}}.
