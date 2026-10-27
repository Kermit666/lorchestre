# Upstream GH AW Source Snapshots

These files are raw pinned snapshots from `github/gh-aw@v0.82.2`, tag hash `0b1173e7d380fb68a9d6749af62e49ca050eefc1`.

Use them for audit, refinement, or provenance checks. Do not load them during ordinary topology studies unless exact upstream wording matters.

| Local file | Upstream path | Lines | SHA-256 |
| --- | --- | ---: | --- |
| `upstream-gh-aw-v0.82.2/semantic-function-refactor.md` | `.github/workflows/semantic-function-refactor.md` | 478 | `ed8f3765d09616d659dae86e6a3b8294afd462dc5bfe1102318e28339626f531` |
| `upstream-gh-aw-v0.82.2/daily-file-diet.md` | `.github/workflows/daily-file-diet.md` | 295 | `5e7ba8a7fafc0bed7a6779d4e00ebc01c19a35164d6bd4c23792e7e2ad93f460` |
| `upstream-gh-aw-v0.82.2/architecture-guardian.md` | `.github/workflows/architecture-guardian.md` | 343 | `800ec4a0ea1a69728c7df5bbab02782f9df7f575e4859a339f40c3169db3af5e` |
| `upstream-gh-aw-v0.82.2/duplicate-code-detector.md` | `.github/workflows/duplicate-code-detector.md` | 278 | `158820fd22f1f98d0bf78f32ddab55ab13e78385de5d7d73be1f44529b2947f1` |
| `upstream-gh-aw-v0.82.2/refactoring-cadence.md` | `.github/workflows/refactoring-cadence.md` | 385 | `827fe553468cba929e39602be7d25eb6b3fa6978a3cc4d6f37eb70c1faba68e5` |
| `upstream-gh-aw-v0.82.2/repo-tree-map.md` | `.github/workflows/repo-tree-map.md` | 156 | `8f18aa98248a765a7b2e9f7f4f8fe1ac3aa38afd8d022469afa8777340143891` |
| `upstream-gh-aw-v0.82.2/go-pattern-detector.md` | `.github/workflows/go-pattern-detector.md` | 181 | `0519b3ca0072169b77e5be58ea68d2a62cd31ff437b64217d460f28a960e3073` |
| `upstream-gh-aw-v0.82.2/shared-go-source-analysis.md` | `.github/workflows/shared/go-source-analysis.md` | 20 | `0ca54b6f476e58f54b85ccd3de63a2ecb5faf02199029c8984dd252d539efe50` |
| `upstream-gh-aw-v0.82.2/shared-mcp-serena-go.md` | `.github/workflows/shared/mcp/serena-go.md` | 30 | `3033ad8df2bfe614f842f4b21794bdac929339bfcb7fb6f78fc0d53a266d75d4` |
| `upstream-gh-aw-v0.82.2/shared-reporting.md` | `.github/workflows/shared/reporting.md` | 15 | `fb9ec1cc7986043bb6ab8f1e6062bd59729d3996c50afb8c2262f0cfa874f903` |
| `upstream-gh-aw-v0.82.2/shared-skip-if-issue-open.md` | `.github/workflows/shared/skip-if-issue-open.md` | 24 | `7aa38ac87a3182bd16d6d0b9839fd9deb47459ca96d03f7d069545ddf303e8d4` |
| `upstream-gh-aw-v0.82.2/shared-daily-issue-base.md` | `.github/workflows/shared/daily-issue-base.md` | 44 | `f2b2247a95221efd499fec9f0779f2c3b75cba5e3b48b0a159dd08c2ff9e163a` |
| `upstream-gh-aw-v0.82.2/shared-safe-output-app.md` | `.github/workflows/shared/safe-output-app.md` | 30 | `545954a3ef1e94853877d52e7a516581e52e77b3443362573e0b9c1a7cf1ffa2` |

## Why These Files

- `semantic-function-refactor.md`: main symbol clustering, outlier, duplicate, and scattered-helper method.
- `daily-file-diet.md`: large-file threshold, split-boundary, test-coverage, and incremental-refactor method.
- `architecture-guardian.md`: deterministic structural gate for oversized files/functions, excess exports, and import cycles.
- `duplicate-code-detector.md`: semantic duplicate and structural duplicate triage, with thresholds for meaningful duplication.
- `refactoring-cadence.md`: trend-aware health signals for file length, complexity, file growth, and TODO/FIXME churn.
- `repo-tree-map.md`: repository shape facts, tree/size distribution, file counts, and largest-file discovery.
- `go-pattern-detector.md`: cheap AST scan before deeper agent review; retained as a gating pattern, not a topology smell by itself.
- `shared-go-source-analysis.md`: tool setup pattern for source discovery and semantic-first analysis.
- `shared-mcp-serena-go.md`: optional Serena/LSP capability statement and constraints.
- `shared-reporting.md`: concise report formatting pattern.
- `shared-skip-if-issue-open.md`, `shared-daily-issue-base.md`, `shared-safe-output-app.md`: safe-output and duplicate-output discipline translated into local non-mutating study boundaries.
