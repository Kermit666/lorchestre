---
name: book-router-creator
description: "Add a new programming book to the local `book-router` system end to end: source intake, raw markdown staging, cleaned markdown, structural index, semantic cards, validators, registry and manifest updates, and synced skill-pack artifacts. Use when you need to onboard a new book from PDF, EPUB, or markdown into the repo's routing library."
---

# Book Router Creator

## Start With The Pipeline

Read [references/pipeline-workflow.md](references/pipeline-workflow.md) first.

- Use this skill for full book onboarding, not for querying an already indexed book.
- Keep the raw source separate from cleaned derivatives.
- Promote the book through the normal status ladder:
  `planned` -> `raw-source-present` -> `index-ready` -> `routing-ready`

## Scaffold First

Start by scaffolding the pack and registry entry:

```bash
python3 skills/book-router-creator/scripts/init_book_pack.py \
  --book-id my-book-id \
  --title "Book Title" \
  --author "Author Name" \
  --description "What the book is best used for." \
  --raw-markdown path/to/raw_source.md
```

- This creates the skill-local `book.json` and updates the `book-router` registry.
- Fill `domains`, `strengths`, `pick_when`, `avoid_when`, and routing note fields as concrete decision cues, not marketing copy.

## Build In Phases

1. Stage the raw source.
2. Write a cleaner script and generate `generated/<book>_cleaned.md`.
3. Build a structural index and generate `generated/<book>_index.json`.
4. Build semantic cards plus a validator and generate `generated/<book>_cards.json`.
5. Sync the generated artifacts into `skills/book-router/references/books/<book-id>/`.
6. Update the manifest and registry statuses as each phase becomes real.

Read [references/deliverables.md](references/deliverables.md) before adding scripts or artifacts.

## Use Existing Packs As Patterns

Compare against the existing packs when naming files or shaping outputs:

- `skills/book-router/references/books/fowler-refactoring/`
- `skills/book-router/references/books/clean-code/`

Keep the new book's ontology honest to the book. Reuse patterns, but do not force Fowler-style smells or Clean Code-style heuristics onto a book that has a different shape.

## Validation Rules

- Do not mark a book `index-ready` until the cleaned markdown and index both exist.
- Do not mark a book `routing-ready` until cards, validators, and sync paths all work.
- Always run the book-specific validator after generating cards.
- Re-run the `book-router` skill validator after syncing artifacts.

## Keep It Reusable

- Prefer file names that generalize: `clean_<book>_markdown.py`, `build_<book>_index.py`, `build_<book>_cards.py`, `validate_<book>_cards.py`.
- Keep curated semantics in `data/`, generated artifacts in `generated/`, and skill-consumable copies under `skills/book-router/references/books/<book-id>/`.
- Keep routing knowledge in manifests, semantics files, validators, and eval cases, not buried in the skill text.
