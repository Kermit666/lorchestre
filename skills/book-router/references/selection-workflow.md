# Selection Workflow

Use this flow when more than one book may fit.

If you want a deterministic first pass, run `python3 scripts/query_book_router.py "<query>"` before doing the manual shortlist.
Treat the output as a soft ranking: the top book is the first stop, not an exclusive answer.
If you need to see all available books or verify aliases, run
`python3 scripts/query_book_router.py --list-books`.

## 1. Classify The Need

Translate the task into one or two dominant needs:

- smell detection
- refactoring selection
- naming/style judgment
- testing discipline
- architectural tradeoffs
- framework-specific guidance

## 2. Shortlist Books

Start from `python3 scripts/query_book_router.py --list-books` for the
canonical book references. Use [library/registry.json](library/registry.json)
only when you need the raw routing fields.

- Keep books whose `domains` and `pick_when` match the need.
- Drop books whose `avoid_when` directly matches the task.
- Prefer `routing-ready` books over `index-ready` books, and `index-ready` books over `raw-source-present` books.

## 3. Pick The Primary Book

Choose the book with the most direct operational value:

- mechanical move selection beats general philosophy
- precise routing artifacts beat raw prose
- narrow relevance beats broad relevance
- if the runner-up score stays close, keep it available as a parallel lens instead of forcing a single-book choice

## 4. Retrieve In Layers

Inside the chosen book:

1. query `cards`
2. inspect `index`
3. read the cleaned markdown section

## 5. Add A Secondary Book Only If Needed

Use a second book only when it contributes a clearly different lens, not just a weaker duplicate.
