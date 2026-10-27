# Translation Audit Checklist

Use this checklist when translating GH AW concepts into the Codex-native topology skill. Mark a source section as:

- `translated`: present in `SKILL.md`, `topology-method.md`, `report-shape.md`, or the helper script;
- `adapted`: intentionally changed for Codex/local use;
- `dropped`: intentionally excluded because it is GH Actions, GitHub issue, Go-only, or too host-specific;
- `open`: not translated yet and needs review.

## Semantic Function Refactoring

| Upstream section | Status | Skill destination / decision |
| --- | --- | --- |
| Frontmatter: schedule, permissions, sandbox, engine | dropped | GH Actions runtime is not part of a Codex skill. |
| Imports: `shared/go-source-analysis.md`, `shared/otlp.md` | adapted | Source analysis kept; OTLP omitted for local skill. |
| Safe outputs: close/create issue | adapted | Became authority boundary: proposal is not execution permission. |
| Tools: cli-proxy, github, edit | adapted | Use local read-only tools; edits are forbidden during study. |
| Mission: collect functions, cluster, outliers, duplicates | translated | `SKILL.md` workflow; `topology-method.md` sections 2-5. |
| Constraint: only `.go`, skip `_test.go`, focus `pkg/` | adapted | Language/repo-aware scope; tests treated as topology evidence. |
| Serena configuration | adapted | Optional semantic provider; not required. |
| Close existing refactor issues | dropped | Not useful for local skill. Future integration may use duplicate-report checks. |
| Discover source files | translated | Shape facts and snapshot helper. |
| Collect function names per file | translated | Shape facts, symbol hints, purpose map. |
| Semantic clustering by names/data/purpose | translated | Concept clusters. |
| File organization rules | adapted | Clear responsibility per module, respecting local doctrine. |
| Outlier detection | translated | `misplaced_symbol`, `mixed_responsibility`. |
| Duplicate detection with Serena | adapted | Semantic duplicate detection with optional LSP/MCP; text fallback. |
| Deep reasoning criteria | translated | Finding rules and skip rules. |
| Extract common function/move/create utility/generics/interface | adapted | Candidate moves; minimality pressure added before abstraction. |
| Refactoring report template | adapted | `report-shape.md`. |
| Priority ranking | translated | Report finding order and proposed move order. |
| Implementation checklist | adapted | Verification and move order only; execution remains separate. |
| Analysis metadata | translated | `report-shape.md` includes an Analysis Metadata block. |
| Operational guidelines: security/efficiency/accuracy | translated | Core rule and authority boundaries. |
| Issue creation guidance | dropped | Replaced by local report/proposal. |
| High-value analysis / what to report / what to skip | translated | `topology-method.md` finding and skip rules. |
| Serena tool usage guide | adapted | Optional provider note; raw tool examples not copied. |
| Success criteria | adapted | Proposal quality gate and validation expectations. |

## Daily File Diet

| Upstream section | Status | Skill destination / decision |
| --- | --- | --- |
| Frontmatter: schedule, credits, permissions, engine | dropped | GH Actions runtime is not part of the skill. |
| Skip-if-issue-open and daily issue imports | adapted | Duplicate output discipline becomes "avoid duplicate active reports." |
| Bash tool for largest Go file | translated | Snapshot helper and shape facts collect largest files. |
| Mission: monitor oversized files | translated | `oversized_file` and file diet trigger terms. |
| Current context: repo/date/workspace | adapted | Local scope and baseline. |
| Identify largest Go source file | adapted | Largest or topology-relevant files in current scope. |
| Healthy size threshold: 800 lines | adapted | Default warning signal, not universal rule. |
| Analyze file structure with Serena | adapted | Optional semantic provider plus manual code reading. |
| Logical boundaries | translated | Purpose map, concept clusters, proposed splits. |
| Suggested file splits | translated | Proposal shape and report shape. |
| Test coverage check | translated | Test topology and verification plan. |
| Markdown issue formatting | adapted | `report-shape.md` local report. |
| Current state metrics | translated | Report summary and findings. |
| Full file analysis details | translated | Report findings and evidence detail. |
| Proposed file splits | translated | Candidate move / proposed move order. |
| Shared utilities | adapted | Allowed only if minimality pressure passes. |
| Interface abstractions | adapted | Treat as high-risk overbuild unless clearly needed. |
| Test coverage plan | translated | Verification and test impact. |
| Implementation guidelines | adapted | Execution guidance retained as proposed move order, not automatic edits. |
| Acceptance criteria | adapted | Proposal quality gate; commands must be repo-specific. |
| Output requirements | adapted | No issue creation; report "no material topology finding" when below threshold/no issue. |
| Important guidelines | translated | Specific, actionable, repo-pattern-aware, tests included. |
| Serena configuration | adapted | Optional provider only. |

## Architecture Guardian

| Upstream section | Status | Skill destination / decision |
| --- | --- | --- |
| Frontmatter: schedule, permissions, engine, experiments | dropped | GH Actions runtime and experiment metadata are not part of the skill. |
| Imports: skip-if issue, daily issue, OTLP | adapted | Duplicate-output and safe-report discipline retained; issue/telemetry details dropped. |
| Threshold config from `.architecture.yml` | adapted | Local project policy wins; defaults are only signals. |
| Changed Go/JS file discovery | adapted | Current user scope, changed files, or target paths drive selection. |
| File line count checks | translated | `oversized_file`, shape facts, report metadata. |
| Function line checks | translated | `oversized_function`, shape facts, report metadata. |
| Export count checks | translated | `excess_exports`, public API/import risk. |
| Go import cycle checks | translated | `import_cycle`, `import_direction_risk`. |
| Severity classification: blocker/warning/info | adapted | Report finding order and severity wording; not a universal policy gate. |
| Noop when nothing changed/found | translated | Report "no material topology finding" with checked scope. |
| Issue body template | adapted | `report-shape.md` and compact finding fields. |
| Violation-classifier sub-agent | adapted | Threshold classification can be local analysis or helper output. |

## Duplicate Code Detector

| Upstream section | Status | Skill destination / decision |
| --- | --- | --- |
| Frontmatter: schedule, permissions, engine, network | dropped | Runtime config is not part of the skill. |
| Serena activation | adapted | Optional semantic/LSP/AST provider; text fallback remains valid. |
| Changed file analysis | adapted | Scope-aware source selection; tests/config/generated files skipped by default. |
| Symbol-level analysis | translated | Concept clusters and duplicate semantics. |
| Pattern search | translated | Cheap deterministic gates and duplicate-structure signals. |
| Duplicate types: exact, structural, functional, copy-paste | translated | `duplicate_semantics`, `duplicate_structure`, `scattered_helper`. |
| Significance threshold: >10 lines or 3+ patterns | adapted | Use as a rough default; local context can lower/raise threshold. |
| One issue per distinct pattern | adapted | One local finding per distinct duplicate pattern. |
| Skip boilerplate, tests, configs, idioms | translated | Finding skip rules. |
| Issue template | adapted | Report finding evidence, impact, recommendation, and metadata. |
| Security/efficiency/accuracy guidelines | translated | Read-only evidence, bounded scope, verify before reporting. |
| Tool usage sequence | adapted | Optional provider order, not mandatory Serena. |

## Secondary Structural Inputs

| Upstream file/section | Status | Skill destination / decision |
| --- | --- | --- |
| `refactoring-cadence.md`: file length, complexity, growth, TODO churn | adapted | Trend signals in shape facts and `structural_trend`; health score not copied as policy. |
| `refactoring-cadence.md`: cache-memory baseline | adapted | Use git history/project metrics when helpful; no GH AW cache dependency. |
| `repo-tree-map.md`: file count, size, extension distribution, largest files | translated | Shape facts and snapshot helper behavior. |
| `repo-tree-map.md`: ASCII visualization and GitHub discussion | dropped/adapted | Diagram style dropped; tree facts retained. |
| `go-pattern-detector.md`: ast-grep prefilter | adapted | Cheap pattern gate before deeper review. |
| `go-pattern-detector.md`: `json:"-"` rule | dropped | Specific Go lint rule is not topology doctrine. |

## Reviewed But Not Vendored

| Upstream file | Decision |
| --- | --- |
| `repository-quality-improver.md` | Broad SDLC quality report; overlaps with shape facts but too general for a topology skill. |
| `code-simplifier.md` | Implementation/PR workflow for simplification; useful downstream, not topology study input. |
| `dead-code-remover.md` | Safe deletion workflow; topology-adjacent only when dead symbols affect placement. |
| `daily-architecture-diagram.md` | Output is architecture visualization, not refactor placement method. |
| `daily-sentrux-report.md` | External metric system; not required for portable Codex skill behavior. |
| `typist.md` | Type-safety and duplicate-type analysis; possibly useful later, but narrower than current topology source set. |
| `sergo.md` | Generic Serena Go expert strategy; covered by optional semantic-provider guidance. |

## Shared Files

| Upstream file | Status | Skill destination / decision |
| --- | --- | --- |
| `shared-go-source-analysis.md` | adapted | Semantic tools first when available; shell for cheap discovery. |
| `shared-mcp-serena-go.md` | adapted | Serena/LSP is optional and language-agnostic in the skill. |
| `shared-reporting.md` | translated | `report-shape.md` keeps overview, findings, details, next actions. |
| `shared-skip-if-issue-open.md` | adapted | Avoid duplicate study output; no GitHub issue dependency. |
| `shared-daily-issue-base.md` | dropped/adapted | Issue-safe-output details dropped; safe-output discipline retained. |
| `shared-safe-output-app.md` | dropped/adapted | Credentials dropped; authority boundary retained. |

## Future Refinement Items

- Decide whether the snapshot helper should produce a compact metadata JSON schema for later Lorchestre ingestion.
- Review whether GH AW's generic/interface suggestions should be softened further after practical use.
