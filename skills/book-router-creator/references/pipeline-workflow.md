# Pipeline Workflow

Use this when onboarding a new book into `skills/book-router`.

## 1. Decide The Book's Role

Before touching files, answer:

- What kind of problems should this book win?
- What should it lose to?
- Is it mainly mechanical, stylistic, architectural, or language-specific?
- What is the smallest useful first delivery: `raw-source-present`, `index-ready`, or `routing-ready`?

Write those answers into the registry entry and the manifest.

## 2. Stage The Source

Prefer this separation:

- raw source: OCR dump, extracted markdown, or a manually acquired markdown file
- cleaned source: token-efficient, AI-oriented derivative

Rules:

- Do not hand-edit the raw source into shape.
- If the user only has a PDF, first extract it to a raw text or markdown file.
- Keep noisy conversion artifacts out of the skill-local book pack until the cleaner is working.

## 3. Build The Cleaner

Create `scripts/clean_<book>_markdown.py`.

The cleaner should:

- preserve the real book body
- strip ads, cover pages, legal clutter, TOCs if redundant, page scaffolding, and OCR junk
- keep optional high-signal extras only when they help routing
- emit `generated/<book>_cleaned.md`

Validate by checking that the important chapters and internal catalogs still survive.

## 4. Build The Structural Index

Create `scripts/build_<book>_index.py`.

The index should:

- parse the cleaned markdown, not the raw source
- identify the book's actual structural units
- produce stable ids
- capture lookup terms and route hints
- emit `generated/<book>_index.json`

Do not force every book into Fowler's smell/refactoring model. Use the book's own structure.

## 5. Build The Semantic Layer

Create:

- `data/<book>_semantics.json`
- `scripts/build_<book>_cards.py`
- `scripts/validate_<book>_cards.py`

The semantic layer should:

- turn structural entries into decision-oriented cards
- add curated lookup phrases, code-shape cues, and relationships
- include a validation or evaluation set
- emit `generated/<book>_cards.json`

## 6. Sync Into The Book Router Pack

Create or update:

- `skills/book-router/references/books/<book-id>/book.md`
- `skills/book-router/references/books/<book-id>/index.json`
- `skills/book-router/references/books/<book-id>/cards.json`
- `skills/book-router/references/books/<book-id>/book.json`

Use:

```bash
python3 skills/book-router/scripts/sync_book_pack.py --manifest ...
```

## 7. Promote Status Carefully

- `raw-source-present`: raw source or raw markdown exists
- `index-ready`: cleaned markdown + index synced and usable
- `routing-ready`: cards + validator + sync path all work

Update both:

- `skills/book-router/references/library/registry.json`
- `skills/book-router/references/books/<book-id>/book.json`

## 8. Validate End To End

At minimum, re-run:

- the new book's validator
- `skills/book-router/scripts/sync_book_pack.py` if artifacts changed
- the `book-router` skill validator

If the new book changes routing behavior in a meaningful way, expand the router-level evaluation set too.
