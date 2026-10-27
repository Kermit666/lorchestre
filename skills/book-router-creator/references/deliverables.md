# Deliverables

Use this as the completion checklist for a new book.

## Required Files For A Routing-Ready Book

- raw source file or markdown source
- `scripts/clean_<book>_markdown.py`
- `generated/<book>_cleaned.md`
- `scripts/build_<book>_index.py`
- `generated/<book>_index.json`
- `data/<book>_semantics.json`
- `scripts/build_<book>_cards.py`
- `generated/<book>_cards.json`
- `scripts/validate_<book>_cards.py`
- `skills/book-router/references/books/<book-id>/book.json`
- `skills/book-router/references/books/<book-id>/book.md`
- `skills/book-router/references/books/<book-id>/index.json`
- `skills/book-router/references/books/<book-id>/cards.json`
- `skills/book-router/references/library/registry.json`

## Recommended Naming Pattern

- cleaner: `clean_<book>_markdown.py`
- index builder: `build_<book>_index.py`
- card builder: `build_<book>_cards.py`
- validator: `validate_<book>_cards.py`
- semantics file: `<book>_semantics.json`
- eval cases: `<book>_eval_cases.json`

## Minimum Quality Gates

- the cleaned markdown still contains the real book body
- the structural index reflects the book's real organization
- stable ids are reused consistently across generated layers
- semantic cards are decision-oriented, not just copied prose
- validators fail loudly when inventory or routing drifts
- skill-local pack paths match the manifest

## Registry And Manifest Questions

Every new book should answer:

- `description`: what is this book best for?
- `strengths`: what kind of help does it give better than the others?
- `pick_when`: what language should trigger it?
- `avoid_when`: when should another book win?
- `primary_entrypoints`: what are the best first concepts to search?
- `query_examples`: what real developer phrasing should route here?
- `limitations`: where does the book stop being the right tool?

## Good Final State

A strong onboarding result lets another agent:

1. see the book in the registry
2. open the manifest
3. inspect `book.md`, `index.json`, and `cards.json`
4. query the book without knowing the implementation history
