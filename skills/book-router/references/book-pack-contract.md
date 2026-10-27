# Book Pack Contract

Use this contract when adding a new book to the local routing system.

## Registry

Each book must have one entry in [library/registry.json](library/registry.json).

Required fields:

- `id`
- `alias`
- `title`
- `author`
- `status`
- `description`
- `domains`
- `strengths`
- `pick_when`
- `avoid_when`
- `manifest_path`

Status values:

- `planned`: the book is known but no usable source is ready
- `raw-source-present`: the source file exists, but no routing artifacts are ready
- `index-ready`: cleaned markdown and a structural index exist, but semantic cards do not
- `routing-ready`: cards and index artifacts exist and may be used for routing

## Book Manifest

Each book lives at `books/<book-id>/book.json`.

Required fields:

- `schema_version`
- `id`
- `title`
- `author`
- `status`
- `description`
- `strengths`
- `pick_when`
- `avoid_when`
- `artifacts`
- `routing_notes`

Required `artifacts` fields for an `index-ready` book:

- `cleaned_markdown`
- `index`

Required `artifacts` fields for a `routing-ready` book:

- `cleaned_markdown`
- `index`
- `cards`

Recommended `artifacts` fields when local tooling exists:

- `query_script`
- `validator`

Optional `artifacts` fields:

- `raw_markdown`

Useful `routing_notes` fields:

- `primary_entrypoints`
- `query_examples`
- `preferred_lookup_order`
- `limitations`

## Writing Rules

- Use lowercase hyphenated ids such as `fowler-refactoring`.
- Use one canonical prompt-facing alias per book, such as `Fowler Refactoring`
  or `DDIA`.
- Display books as `book:<alias> | <Full Title> | <Author>` when citing them
  in prompts, evidence records, or routing output.
- Keep descriptions decision-oriented, not marketing-oriented.
- Write `pick_when` as concrete routing cues.
- Write `avoid_when` so the model knows when another book should win.
- Keep file paths repo-relative.

## Minimal Manifest Skeleton

```json
{
  "schema_version": 1,
  "id": "book-id",
  "title": "Book Title",
  "author": "Author Name",
  "status": "raw-source-present",
  "description": "What the book is best used for.",
  "strengths": [],
  "pick_when": [],
  "avoid_when": [],
  "artifacts": {},
  "routing_notes": {
    "primary_entrypoints": [],
    "query_examples": [],
    "preferred_lookup_order": ["cards", "index", "cleaned_markdown"],
    "limitations": []
  }
}
```
