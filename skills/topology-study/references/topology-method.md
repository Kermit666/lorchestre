# Topology Analysis Method

Use this method when a repo area may need organization, placement, ownership, or refactor-topology study.

## 1. Scope And Baseline

Define:

- target paths;
- source roots;
- test roots;
- out-of-scope paths;
- current user goal;
- whether the task is study-only, planning, or implementation support.

Start with existing local doctrine when available: `AGENTS.md`, package config, architecture docs, tests, public exports, and nearby conventions.

## 2. Shape Facts

Collect facts before interpretation:

- file tree and folder clusters;
- line counts and largest files;
- function-length and export-count hotspots;
- symbols per file;
- imports, exports, and public entrypoints;
- import cycles or layering/dependency violations;
- test peers and missing/awkward tests;
- repeated basenames or duplicated helper names;
- exact, near, semantic, or structural duplicates;
- repository tree, directory depth, and package/module size distribution;
- changed/hot files when git history is relevant.

Use deterministic commands first for cheap facts. Use LSP/MCP/AST tools for deeper symbol/reference data when available.

## 3. Purpose Map

For each important file/folder, write:

```text
path -> current apparent purpose -> evidence -> confidence
```

Keep purpose descriptions short. A file with several unrelated purpose phrases is already a possible finding.

## 4. Concept Clusters

Cluster by:

- prefixes/suffixes such as parse, validate, create, render, load, save, normalize;
- shared domain nouns;
- operated data types;
- caller/callee groups;
- import/export relation;
- test file grouping;
- repeated helper behavior.

Then compare clusters against physical placement.

Cheap deterministic gates are useful before deep review:

- threshold checks can flag files, functions, export counts, and import cycles;
- AST/pattern scans can flag candidate anti-patterns or repeated structures;
- tree/size maps can reveal concentration and directory-depth pressure;
- trend data can identify files growing quickly enough to deserve attention.

Treat these as candidate signals. Confirm each one by reading code purpose, ownership, callers, and tests before recording a finding.

## 5. Finding Types

Record only evidence-backed findings:

- `oversized_file`: file is large and has separable responsibilities.
- `oversized_function`: function has grown beyond a local or configured threshold and contains separable phases.
- `excess_exports`: module exports too many public identifiers for one clear responsibility.
- `import_cycle`: packages/modules form a cycle or dependency knot that blocks clean ownership.
- `mixed_responsibility`: file/folder purpose map contains unrelated concerns.
- `misplaced_symbol`: symbol purpose fits another owner better.
- `scattered_helper`: similar helper concept appears in several unrelated places.
- `duplicate_semantics`: exact, near, or functional duplicate behavior.
- `duplicate_structure`: repeated control-flow/type/module shapes create drift risk even when text differs.
- `import_direction_risk`: dependency direction fights ownership or layering.
- `public_api_surface`: proposed move touches exports/import paths.
- `test_topology_gap`: test peer is missing, awkward, or blocks safe movement.
- `structural_trend`: recent growth or repeated churn concentrates in one topology area.
- `over_split`: too many files/layers obscure one small concept.

Skip:

- tiny isolated helpers;
- naming taste without placement impact;
- language idioms;
- pattern-scan hits that are valid in context;
- similarity that is intentionally local and simpler than abstraction;
- broad rewrites without a concrete move boundary.

## 6. Proposal Shape

For every proposed move or split, include:

- current owner;
- proposed owner;
- symbols/files affected;
- why the placement improves navigation or ownership;
- behavior risk;
- public API/import risk;
- test impact;
- smallest safe move order;
- verification commands or checks.

Prefer one concept per proposal. If a proposal needs many independent moves, split it.

## 7. Minimality Pressure

Topology improvement can overbuild. Challenge proposals that introduce:

- a shared utility for one caller;
- an interface with one implementation;
- new layering only to make a diagram look clean;
- a generic abstraction for two small cases;
- file splits that make navigation worse.

Do not let concern for proposal size erase safety, tests, public API constraints, or explicit user scope.

## 8. Authority Boundaries

Use this separation:

```text
snapshot fact -> possible signal -> interpreted finding -> proposal -> authorized execution
```

Do not collapse these. A topology study can recommend; it does not authorize edits by itself.
