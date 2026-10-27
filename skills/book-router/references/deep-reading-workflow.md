# Deep Reading Workflow

Use this before turning a routed book result into decision backing.

## 1. Route The Question

From the Book Router skill root:

```bash
python3 scripts/query_book_router.py "<decision question>" --json
```

If the caller already selected the book, keep the question explicit:

```bash
python3 scripts/query_book_router.py "book:<alias> | <decision question>" --json
```

If the output marks a close call, keep the runner-up available as a secondary
lens.

## 2. Inspect The Routed Hits

Use cards to answer:

- what concept or smell is likely relevant;
- which related cards might matter;
- which exact book section should be read next.

Do not stop at this step for non-trivial decisions.

## 3. Read The `read_next` Section

When query output includes `read_next`, open:

```text
read_next.book_path
read_next.start_line
read_next.end_line
```

For long sections, read enough surrounding prose to understand motivation,
mechanics, caveats, and fit to the current code. Do not quote long passages in
final answers; summarize the relevant guidance.

If the routed range feels too narrow, rerun the query with one of:

```bash
--read-context N      # routed range plus N lines before and after
--read-before N       # N lines before plus the routed range
--read-after N        # routed range plus N lines after
--read-next-lines N   # only the N lines immediately after the routed range
```

## 4. Fall Back To Manual Anchor Lookup

If `read_next` is absent, open the selected book's `cards.json` or `index.json`
and find the result id. Use its `source_anchor.start_line` and
`source_anchor.end_line`, then read the manifest's `artifacts.cleaned_markdown`
file at that range.

Example:

```bash
jq '.cards[] | select(.id=="refactoring/move-function") | .source_anchor' \
  references/books/fowler-refactoring/cards.json

sed -n '3497,3646p' \
  references/books/fowler-refactoring/book.md
```

## 5. Record The Evidence

Use [book-evidence-record.md](book-evidence-record.md) for decisions that will
affect a plan, phase, architecture document, or implementation strategy.

The record should separate:

- card/index routing;
- book prose actually read;
- interpretation for this codebase;
- tradeoff or uncertainty.
