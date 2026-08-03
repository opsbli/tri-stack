# Knowledge-base bootstrap (read only when the substrate is missing)

`tri-loop`'s Step 1 reads this **only when** the knowledge base isn't set up yet
(no `ARCHITECTURE.md` + `LOG.md` at the repo root, or `CLAUDE.md` doesn't reference
the structure). It's a **one-time, idempotent** setup: create only what's missing,
never clobber an existing file. Once done, future `tri-loop` runs skip straight to
creating the loop.

The model these files instantiate is in `ARCHITECTURE.md` (sibling of this file).
Read it once if you haven't.

---

## Procedure

Run from the **knowledge-base repo root** (where loops read/write — usually the repo
that holds `CLAUDE.md`, not an app code repo).

1. **`ARCHITECTURE.md`** — if absent at root, copy it verbatim from `templates/architecture.md`.
2. **`LOG.md`** — if absent at root, copy it verbatim from `templates/log.md`.
3. **`signals/`, `docs/`, `domains/`** — for each folder that's missing, create it and
   write its `README.md` from the verbatim blocks below (these READMEs *are* the schema):
   - `signals/README.md` ← `templates/signals-readme.md`
   - `docs/README.md` ← `templates/docs-readme.md`
   - `domains/README.md` ← `templates/domains-readme.md`
4. **`CLAUDE.md`** —
   - If it exists but has no "Knowledge base" section → **append** the
     `templates/claude-kb-section.md` block (don't touch the rest).
   - If it doesn't exist → offer to scaffold one from `templates/claude-template.md`
     (the user fills its `{{PLACEHOLDER}}`s).
5. Do **not** pre-create `tasks/` or any other kind — those are earned later (see
   `ARCHITECTURE.md` → "Earning a new kind").

Then return to `tri-loop` Step 2 (scaffold the loop).

---

## Files referenced

| Target file | Source template |
|---|---|
| `ARCHITECTURE.md` | `templates/architecture.md` |
| `LOG.md` | `templates/log.md` |
| `signals/README.md` | `templates/signals-readme.md` |
| `docs/README.md` | `templates/docs-readme.md` |
| `domains/README.md` | `templates/domains-readme.md` |
| `CLAUDE.md` (new) | `templates/claude-template.md` |
| `CLAUDE.md` (append section) | `templates/claude-kb-section.md` |

All copies are **verbatim** — do not modify template content during bootstrap.
