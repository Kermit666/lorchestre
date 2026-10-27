---
name: dead-code-safety
description: Read-only dead-code analysis and safe deletion candidate classification. Use when you need to inspect unreachable code, unused functions/classes/files/exports, test-only callers, stale stubs, unused public API, dead-code cleanup opportunities, deletion risk, false-positive gates, or cleanup verification needs.
---

# Dead Code Safety

## Core Rule

Use this skill for read-only dead-code study first. Produce evidence-backed candidates, confidence, risks, and later verification needs. Do not edit project files.

Dead-code evidence is not deletion authorization. Follow the caller's authority model before any cleanup execution.

## Workflow

1. Scope the study.
   - Use user-named paths when present.
   - Identify source roots, test roots, public package/API boundaries, generated/vendor paths, and runtime entrypoint areas.
   - Keep out-of-scope paths explicit.
2. Gather candidate signals.
   - Prefer language analyzers when locally available.
   - Use `rg`, LSP/reference tools, imports/exports, tests, docs, config, and build metadata as supporting evidence.
   - Run `scripts/reference_probe.py` when a quick text-reference categorization would help.
3. Classify each candidate.
   - Candidate types include no-callers, test-only callers, unused export, unreachable branch, stale stub, empty shell file, obsolete config/doc reference, and duplicate dead wrapper.
   - Confidence classes: `high_delete_candidate`, `needs_investigation`, `keep_or_defer`, `false_positive`.
   - Treat test-only callers as investigation evidence, not automatic delete proof; shared test infrastructure should normally be kept.
4. Apply false-positive gates.
   - Check public API, framework hooks, reflection/dynamic dispatch, config/CLI routes, generated code, build tags, serialization names, dependency injection, plugin systems, migrations, scripts, docs, and tests.
   - Treat static analyzer output as a signal, not proof.
5. Propose small deletion batches.
   - Keep high-confidence batches small, normally up to five symbols/files.
   - Separate medium-risk candidates from executable cleanup.
   - Include exclusive tests only when they test only the candidate and nothing broader.
6. Prepare cleanup handoff.
   - Include exact symbols/files, evidence, risk, verification commands, and stop conditions.
   - If deletion might be destructive, public, or scope-expanding, mark it as requiring explicit execution authorization.

## References

- Read `references/dead-code-method.md` for the full safety method.
- Read `references/language-adapters.md` for language-specific analyzer ideas.
- Read `references/report-shape.md` when producing a dead-code report or cleanup handoff.
- Read `references/gh-aw-source-map.md` when explaining provenance or keep/adapt/drop choices.
- Read `references/upstream-sources.md` before opening raw GH AW snapshots.

## Reference Probe

Use the helper for local read-only reference categorization. `<skill-dir>` is this skill's own directory (the folder containing this
`SKILL.md`). Run the command from the project root.

```bash
python3 <skill-dir>/scripts/reference_probe.py --root . --symbol MySymbol --format markdown
```

The helper is a text-reference probe only. It cannot prove reachability, dynamic use, or safe deletion by itself.
