# GH AW Topology Source Map

Pinned upstream: `github/gh-aw@v0.82.2`

Pinned tag hash checked: `0b1173e7d380fb68a9d6749af62e49ca050eefc1`

Primary upstream files:

- `.github/workflows/semantic-function-refactor.md`
- `.github/workflows/daily-file-diet.md`
- `.github/workflows/architecture-guardian.md`
- `.github/workflows/duplicate-code-detector.md`
- `.github/workflows/refactoring-cadence.md`
- `.github/workflows/repo-tree-map.md`
- `.github/workflows/go-pattern-detector.md`
- `.github/workflows/shared/go-source-analysis.md`
- `.github/workflows/shared/mcp/serena-go.md`
- `.github/workflows/shared/reporting.md`
- `.github/workflows/shared/skip-if-issue-open.md`
- `.github/workflows/shared/daily-issue-base.md`
- `.github/workflows/shared/safe-output-app.md`

Local raw snapshots live under `references/upstream-gh-aw-v0.82.2/`. See `upstream-sources.md` for exact filenames, line counts, and SHA-256 hashes.

Reference docs:

- https://github.github.com/gh-aw/introduction/how-they-work/
- https://github.github.com/gh-aw/reference/workflow-structure/
- https://github.github.com/gh-aw/reference/safe-outputs/
- https://github.github.com/gh-aw/reference/tools/
- https://github.github.com/gh-aw/blog/2026-01-13-meet-the-workflows-continuous-refactoring/

## Translation Matrix

### Semantic Function Refactoring

Keep:

- Discover source files.
- Inventory symbols per file.
- Infer file purpose.
- Cluster symbols by naming pattern, semantic purpose, operated data, and shared behavior.
- Detect outlier symbols that do not match file purpose.
- Detect exact, near, and functional duplicates.
- Detect scattered helper concepts.
- Prefer high-impact actionable findings over trivial similarities.
- Require concrete paths, symbols, examples, recommendations, and analysis metadata.

Adapt:

- Go-only `.go`, `_test.go`, and `pkg/` assumptions become language- and repo-aware source/test scope selection.
- Serena is an optional semantic provider. Use LSP/MCP/AST tools when available, but degrade to text and code reading.
- GitHub issue report becomes a local topology report or refactor proposal.
- "One file per feature" becomes "one clear responsibility per file/module unless the local architecture says otherwise."
- Generics/interfaces suggestions require minimality review; do not propose architecture solely to reduce similarity.

Drop:

- Closing existing `[refactor]` issues.
- GitHub issue creation as the default output.
- GitHub Actions schedule and permissions as skill behavior.
- Any requirement to use Go/gopls/Serena.

### Daily File Diet

Keep:

- Find large files.
- Apply size as a signal, not a verdict.
- Inspect internal responsibilities before proposing a split.
- Identify logical boundaries, related function groups, duplicate patterns, complexity hotspots, and coupling.
- Check source/test topology and missing coverage.
- Propose file splits with responsibilities, moved symbols, risk, and verification.
- Preserve behavior and public API during refactors.
- Prefer incremental splits and frequent verification.

Adapt:

- The `800` line threshold becomes a default warning signal unless project policy defines another threshold.
- "Largest Go file" becomes "largest or most topology-relevant file in scope."
- Test-to-source ratio is a rough clue; actual verification needs depend on behavior and risk.
- Issue template becomes report sections for current state, findings, proposed moves, and verification.

Drop:

- Daily schedule and issue gating.
- `make test-unit`, `make lint`, and `make build` as universal commands.
- Hard target that every resulting file must be under 500 lines.

### Architecture Guardian

Keep:

- Deterministic pre-scan before agent interpretation.
- Configurable thresholds for file lines, function lines, and public export count.
- Import-cycle detection as a blocker-level architecture signal.
- Severity grouping: blocker, warning, info.
- No-op discipline when no relevant source files changed or no violations exist.

Adapt:

- Daily changed-file window becomes current user scope, changed files, or target paths.
- Go/JavaScript-only checks become language-aware equivalents where local tooling exists.
- `.architecture.yml` thresholds become local policy if present; otherwise use project conventions and clear caveats.
- Issue format becomes topology report metadata and finding severity.

Drop:

- GitHub Actions schedule and issue creation.
- Hardcoded Go/JS implementation details when studying other languages.
- Treating thresholds alone as proof of bad design.

### Duplicate Code Detector

Keep:

- Significant duplication thresholding before reporting.
- Separate exact, structural, functional, and copy-paste duplication.
- Compare changed/current scope against broader codebase.
- Exclude tests, generated files, workflow/config boilerplate, and language idioms unless the user scope says otherwise.
- Require concrete examples, locations, impact, and practical refactoring recommendations.

Adapt:

- Serena remains optional; use LSP/AST/search/manual review as available.
- GitHub issue-per-pattern becomes one local finding per distinct duplicate pattern.
- Go/CJS file restrictions become repo-aware source selection.

Drop:

- Mandatory safe-output calls and GitHub issue limits.
- Automatic assignment to Copilot.

### Secondary Structural Inputs

Keep:

- `refactoring-cadence.md`: file length, complexity, file growth, and TODO/FIXME churn as trend signals.
- `repo-tree-map.md`: repository tree, directory size, file count, extension distribution, largest-file inventory.
- `go-pattern-detector.md`: cheap AST/pattern scanning before expensive agent review.

Adapt:

- Trend/cache-memory concepts become optional local context from git history or project metrics.
- ASCII tree output becomes plain shape facts unless the user asks for a diagram.
- Pattern detector findings are candidate gates that need human/agent interpretation.

Drop:

- Health-score formula as a universal truth.
- Emoji-heavy report style and GitHub discussion output.
- The specific `json:"-"` rule as topology doctrine.

### Shared GH AW Files

Keep:

- Read-only first.
- Use semantic tools before raw grep when available.
- Keep important summaries visible and details structured.
- Safe-output mindset: analysis requests an action; another authority applies it.

Adapt:

- `skip-if-issue-open` becomes "avoid duplicate reports if prior local findings are active."
- `safe-output-app` becomes "do not execute moves just because the study found them."
- Reporting guidance becomes concise local reports rather than GitHub issue formatting.

Drop:

- GitHub App credentials, issue labels, issue expiration, and GH safe-output config.

## Concepts That Must Survive

- Shape facts before judgment.
- File/module purpose before move recommendations.
- Concept clusters before outlier claims.
- Test and public API topology before execution.
- Threshold and pattern signals before deeper semantic interpretation.
- Concrete evidence, not vibe.
- Small move proposals, not broad rewrite pressure.
- Provider signal != finding.
- Analysis != approval.
- Proposal != execution permission.
