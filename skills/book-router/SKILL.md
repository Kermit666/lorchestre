---
name: book-router
description: Route engineering questions into indexed programming books and exact source sections, then apply the selected source's engineering philosophy and reasoning to concrete project decisions while preserving canonical IDs and prose anchors for later work. Use when you need to diagnose or name code smells, plan or review refactoring, evaluate architecture, dependencies, testing strategy, data or state flow, reliability, or engineering tradeoffs, choose or query an indexed book, or maintain the local book registry and manifests.
---

# Book Router

Book Router does more than retrieve or label engineering knowledge. Use the
cards and index to route the question to the most relevant source, then read
the applicable prose deeply enough to understand the reasoning behind its
guidance.

For a material decision, translate that reasoning into project-specific
judgment and concrete consequences. Treat the selected book as an engineering
lens, not as authority: current code, evidence, constraints, and user intent
determine whether and how its philosophy applies.

## Location First

If paths are unclear, read [references/location-map.md](references/location-map.md).

The installed pack is self-contained. Run its bundled query commands from the
Book Router skill root; do not assume a separate repository or external book
checkout exists:

```bash
python3 scripts/query_book_router.py --list-books
python3 scripts/query_book_router.py "<query>" --json
```

When a book is already selected, use the canonical selector form:

```bash
python3 scripts/query_book_router.py "book:<alias> | <query>" --json
```

When invoking it directly, use the bundled wrapper from this skill root:

```bash
python3 scripts/query_book_router.py "<query>" --json
```

## Use The Book List When Useful

Use the book list when you need to see available books, verify an alias, or
check whether a better source exists:

```bash
python3 scripts/query_book_router.py --list-books
```

- Registry entries define the canonical book reference:
  `book:<alias> | <Full Title> | <Author>`.
- Prefer books whose `status` is `routing-ready`, then `index-ready`, then `raw-source-present`.
- Match the task against `domains`, `strengths`, `pick_when`, and `avoid_when`.
- Pick one primary book first. Add a secondary book only when it clearly complements the first one.
- When the choice is unclear, run the bundled query tool before opening book
  artifacts manually.
- Treat the router as scored guidance, not a hard gate. If another book keeps a strong share of the top score, it is reasonable to inspect both.

## Reading Depth

For any architecture, refactoring, testing-strategy, domain-modeling, data,
resilience, or dependency-composition decision, read
[references/reading-depth.md](references/reading-depth.md).

- Cards-only is `Depth 1`: useful for routing, incomplete for decision backing.
- Cards plus index is `Depth 2`: useful for orientation.
- Actual `book.md` prose is `Depth 3`: required for important claims.
- Compare two books at prose level when the router marks a close call or the
  decision has high architectural impact.

## Query A Ready Book

After choosing a book, open its manifest from `manifest_path`.

- Use the book manifest to find the source markdown and generated artifacts.
- Query the book's `cards` artifact first when the task is about routing, smells, refactorings, or fast retrieval.
- Open the `index` artifact when you need structure, chapter anchors, or broader section context.
- Open the cleaned markdown when the decision matters. Use the query result's
  `read_next` field when present; otherwise use the card or index
  `source_anchor`.
- If the routed range feels too narrow, rerun with `--read-context N`,
  `--read-before N`, `--read-after N`, or `--read-next-lines N` to inspect more
  prose around the top result.
- Prefer the manifest's `query_script` when it exists.

Read [references/deep-reading-workflow.md](references/deep-reading-workflow.md)
before using a book result as decision backing.

## Add A New Book Pack

When a new book should join the system:

1. Read [references/book-pack-contract.md](references/book-pack-contract.md).
2. Create `references/books/<book-id>/book.json`.
3. Add the book to [references/library/registry.json](references/library/registry.json).
4. Keep the book description decision-oriented: what the book is best for, when to pick it, and when not to.
5. Mark the book `index-ready` when its cleaned source and index are real.
6. Mark the book `routing-ready` only after its cleaned source, index, cards, and validator path are real.

## Selection Rules

- Select the book with the clearest fit and most useful reasoning for the task,
  not the one with the broadest philosophy.
- Apply the reasoning behind its guidance to the project rather than
  mechanically copying its prescriptions.
- Prefer cards first, index second, prose third for retrieval. Prefer prose
  before conclusions.
- Keep routing knowledge in the registry and per-book manifests, not hardcoded in this skill file.
- Respect score closeness. A high runner-up score means "also worth checking," not "wrong."
- If no `book.md` section was read, label the result as card-level guidance only.
- Explain how the guidance affects the current decision and what it does not
  prove. Do not replace project-specific judgment with a generic book summary.
- When a material finding has an honest canonical match, preserve its ID,
  routing query, prose anchors, fit, related remedy or refactoring IDs, and
  safety conditions so later planning and implementation can reopen the
  evidence. Do not force book labels onto ordinary defects with no useful
  match.
- Record book evidence using
  [references/book-evidence-record.md](references/book-evidence-record.md) when
  a decision is meaningful enough to revisit.

Read [references/selection-workflow.md](references/selection-workflow.md) when the choice between books is unclear.
