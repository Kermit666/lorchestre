# Location Map

Use this when an agent needs to find the Book Router folders, scripts, and
artifacts without guessing. The installed pack is self-contained; do not
assume an external repository checkout.

## Root

All paths below are relative to this skill's root.

## Core Paths

```text
SKILL.md
references/library/registry.json
references/books/<book-id>/book.json
references/books/<book-id>/cards.json
references/books/<book-id>/index.json
references/books/<book-id>/book.md
scripts/query_book_router.py
scripts/query_book_cards.py
```

The skill-local query wrapper is:

```text
scripts/query_book_router.py
```

## Query Commands

From the Book Router skill root:

```bash
python3 scripts/query_book_router.py --list-books
python3 scripts/query_book_router.py "<query>" --json
python3 scripts/query_book_router.py "book:<alias> | <query>" --json
python3 scripts/query_book_router.py "book:<alias> | <query>" --read-context 80
```

The bundled wrapper also resolves the installed registry and policy:

```bash
python3 scripts/query_book_router.py --list-books
python3 scripts/query_book_router.py "<query>" --json
python3 scripts/query_book_router.py "book:<alias> | <query>" --json
```

## Artifact Resolution

The registry points to a book manifest:

```text
references/library/registry.json
  -> manifest_path
```

The manifest points to book artifacts:

```text
artifacts.cleaned_markdown -> book.md
artifacts.cards            -> cards.json
artifacts.index            -> index.json
```

Cards and index entries contain source line ranges. Some `source_anchor.input_path`
values point to generated cleaned markdown, but the same line ranges are synced
into the skill-local `book.md` listed by `artifacts.cleaned_markdown`.

When a query result includes `read_next`, open that `book_path` and line range.
When it does not, read the card or index source anchor manually and map the line
range to the manifest's `cleaned_markdown` artifact.
