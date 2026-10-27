# GH AW Dead Code Source Map

Pinned upstream: `github/gh-aw@v0.82.2`

Pinned tag hash checked: `0b1173e7d380fb68a9d6749af62e49ca050eefc1`

Primary upstream files:

- `DEADCODE.md`
- `.github/workflows/dead-code-remover.md`
- `docs/src/content/docs/blog/2026-05-28-agent-of-the-day.md`

Local raw snapshots live under `references/upstream-gh-aw-v0.82.2/`. See `upstream-sources.md` for exact filenames, line counts, and SHA-256 hashes.

## Translation Matrix

### Dead Code Removal Agent

Keep:

- Static analyzer output is only the first candidate source.
- Small batches, normally up to five candidates.
- Known false-positive skip lists.
- Caller/reference checks before deletion.
- Special runtime-entrypoint checks.
- Exclusive-test checks.
- Build/vet/test verification expectations.
- No-op outcome when no safe candidate exists.

Adapt:

- Go-only `deadcode` becomes language-aware analyzer selection.
- Deletion/PR workflow becomes read-only candidate classification and cleanup handoff.
- Hardcoded GH AW paths such as WASM/console checks become generic runtime-entrypoint gates.
- Cache of processed functions becomes optional "do not repeat accepted/rejected candidates" study memory.
- PR body becomes StudyReport or SubstudyReport sections.

Drop:

- GitHub Actions schedule, permissions, network, safe-output config, and GitHub PR creation.
- Automatic deletion inside the skill.
- `git checkout -- .` recovery behavior; project writes and recovery belong to the caller's execution authority.
- GH AW-specific function skip list as universal policy.

### Dead Code Removal Guide

Keep:

- Include all production binaries/tool packages in analyzer scope.
- Production-entrypoint dead-code tools do not count tests as liveness.
- Test callers are a major safety gate.
- Shared test infrastructure should be kept even when production analyzers flag it.
- Platform-specific entrypoints can create false positives.
- Constants and embedded resources may need rescue before file deletion.
- Tiny candidates can be left alone when deletion churn outweighs value.

Adapt:

- GH AW's Go-specific examples become general test-infrastructure, platform-entrypoint, and churn/value gates.
- Batch phase tables become the report's proposed deletion batch and keep/defer sections.

Drop:

- GH AW-specific phase history, completed phase tables, and exact function names.

### Blog / Agent Of The Day

Keep:

- Dead-code cleanup works best when the feedback loop is mechanical.
- Verification is the safety backbone.
- Review remains a separate step after automated cleanup.

Adapt:

- PR-as-output becomes report or cleanup handoff.

Drop:

- Milestone/run narrative details.

### Reviewed But Not Vendored

- `docs/src/content/docs/reference/serena.md`: confirms semantic tools can find unused exports; covered by LSP/reference guidance.
- `scratchpad/token-budget-guidelines.md`: repeats small batch, truncated output, and early no-op guidance; covered by method and report shape.

## Concepts That Must Survive

- Analyzer signal != proof.
- Candidate != authorization.
- Test-only caller != live production use, but it is often test infrastructure and must be checked before any deletion proposal.
- Public/runtime/dynamic entrypoint risk must be resolved or deferred.
- Small deletion batches are safer than broad cleanup.
- Verification must be named before execution.
