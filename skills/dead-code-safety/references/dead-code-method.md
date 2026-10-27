# Dead Code Safety Method

Use this method when a repo area may contain unreachable, unused, stale, or safely removable code.

## 1. Scope And Baseline

Define:

- target paths;
- language and package boundaries;
- source roots;
- test roots;
- public API/export surface;
- runtime entrypoints;
- generated/vendor/out-of-scope paths;
- current user goal: discovery, study-only, planning support, or execution support.

Start with local doctrine when available: `AGENTS.md`, package docs, route/config files, build scripts, tests, release notes, and public API docs.

## 2. Candidate Signals

Collect signals before judgment:

- static dead-code analyzer results;
- compiler/linter unused-symbol output;
- LSP/reference search results;
- imports/exports and package manifests;
- call sites and test-only call sites;
- test infrastructure and shared helper usage;
- generated or build-tag-specific variants;
- docs/config/CLI/runtime references;
- recent churn or deprecation notes;
- empty shell files, stale wrappers, and obsolete stubs.

Use deterministic tools first. Use semantic tools or manual code reading to confirm the meaning of each candidate.

## 3. Candidate Types

Common useful types:

- `no_callers`: analyzer and reference search find no callers.
- `test_only_callers`: only tests reference the symbol.
- `shared_test_infrastructure`: production-file helper appears dead to production entrypoints but is used broadly by tests.
- `unused_export`: exported/public symbol appears unused inside the repo.
- `dead_wrapper`: wrapper only delegates to a live replacement and has no distinct behavior.
- `stale_stub`: placeholder or compatibility stub with no live entrypoint.
- `empty_shell`: file/package exists only as an empty organizational shell.
- `unreachable_branch`: branch is impossible under current config or type constraints.
- `obsolete_config_doc`: config/doc route mentions removed or inactive code.

## 4. False-Positive Gates

Do not record a deletion candidate as high-confidence until these are checked when relevant:

- Public API or package export used by downstream consumers.
- CLI command, route, job, plugin, migration, fixture, script, or framework convention.
- Reflection, dynamic import, string-based dispatch, serialization tags, dependency injection, or registry wiring.
- Build tags, platform-specific files, generated code, embedded resources, constants, and init side effects.
- Tests that encode broader behavior, not only the candidate symbol.
- Test callers: a static analyzer may ignore test binaries; direct test callers often mean the code is test infrastructure or supports important behavioral tests.
- Documentation examples that still define supported behavior.
- Monorepo package boundaries where references may live outside the current package.
- Deliberate reserved compatibility surface.

If a gate is unresolved, classify as `needs_investigation`, not delete-ready.

## 5. Confidence Classes

Use these classes:

- `high_delete_candidate`: analyzer signal plus reference checks plus false-positive gates support deletion.
- `needs_investigation`: plausible dead code, but public/dynamic/runtime/test evidence is incomplete.
- `keep_or_defer`: code may be unused locally but has plausible external, compatibility, or strategic value.
- `false_positive`: candidate is demonstrably live.

Name uncertainty explicitly. Do not hide weak evidence behind confident wording.

Default test-caller rule:

- No production callers and no test callers can become high-confidence after other gates pass.
- Test-only callers should start as `needs_investigation`.
- Promote test-only candidates only when the tests are exclusive to the candidate and do not function as shared test infrastructure.
- Classify widely used test helpers as `keep_or_defer`, even when production-entrypoint analyzers mark them dead.

## 6. Batch Rules

Prefer small batches:

- normally up to five high-confidence symbols/files;
- one conceptual area per batch;
- no mixed public API and private cleanup unless explicitly authorized;
- no dependency, security, or product behavior change hidden inside cleanup.
- skip tiny isolated candidates when deletion churn is not worth the verification cost.

Keep medium-risk candidates in a separate "investigate later" list.

## 7. Cleanup Handoff

A deletion proposal is useful only when it includes:

- exact file and symbol list;
- evidence source and reference summary;
- false-positive gates checked;
- tests that are exclusive to the candidate, if any;
- public API/runtime risk;
- required verification commands;
- smallest safe deletion order;
- stop conditions for execution.

This handoff does not authorize deletion. Follow the caller's authority model before any cleanup execution.
