# Book Evidence Record

Use this shape in campaign notes, decision logs, or phase readiness gates.

```text
Decision question:

Routing command:

Primary book: book:<alias> | <Full Title> | <Author>

Secondary book, if any: book:<alias> | <Full Title> | <Author>

Routed card/index hits:
- id:
- title:
- why it was considered:
- fit and confidence:

Related remedy/refactoring hits:
- id:
- why it may help:

Book prose actually read:
- book_path:
- start_line:
- end_line:
- section title:

Reading depth:
- Depth 1 / Depth 2 / Depth 3 / Depth 4

Interpretation:
- what the book section says that matters here:
- how it maps to the current code:
- what it does not prove:

Decision impact:
- chosen move:
- tradeoff:
- later/deferred alternative:
- implementation safety conditions:
```

Do not mark a meaningful decision as book-backed when the record only contains
cards or index entries. Do not force a canonical label when no routed finding
honestly matches the observed code; record the issue as direct project evidence
instead.
