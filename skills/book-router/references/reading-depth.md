# Reading Depth

Use this file to decide how much of a routed book to read before making a claim.

## Depth 0: Registry Only

Use only for inventory, rough book selection, or explaining which books exist.

Do not use for engineering decisions.

## Depth 1: Cards Only

Cards are routing hints. They are useful for:

- finding likely concepts;
- naming candidate smells or patterns;
- identifying related cards;
- deciding what to read next.

Cards-only guidance is incomplete for non-trivial decisions.

## Depth 2: Cards Plus Index

Use when you need chapter structure, section anchors, or a broader map of a
book before choosing what to read.

This is still orientation, not final decision backing.

## Depth 3: Book Prose Read

Required before making important claims about:

- refactor-first versus implement-directly;
- architecture boundaries;
- domain modeling or vocabulary;
- dependency composition;
- data consistency or dataflow;
- resilience or rollout;
- testing strategy for risky structure changes.

Depth 3 means the agent opened the relevant `book.md` section and summarized
how the prose affects the current decision.

## Depth 4: Cross-Book Prose Comparison

Use when:

- the router reports a close call;
- two books offer different but plausible lenses;
- the decision could move ownership boundaries;
- the phase would introduce a new architecture pattern.

At Depth 4, read the relevant prose from both books and state which lens is
primary for the current move.

## Reporting Rule

If no `book.md` section was read, say `card-level guidance only`.

If the task requires Depth 3 and only Depth 1 or 2 was reached, do not present
the result as book-backed decision evidence.
