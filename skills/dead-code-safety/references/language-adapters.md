# Language Adapters

Use these as starting points. Prefer project-local tools and documented commands over global assumptions.

## Go

Candidate tools:

```bash
deadcode ./...
go list ./...
go test ./...
go vet ./...
```

Useful checks:

- include all binaries and tool packages, not only the main package;
- remember `deadcode` analyzes production binary entrypoints; tests compile into separate binaries and need explicit test-caller checks;
- inspect build tags and platform-specific files;
- search non-test callers with `rg '\bSymbol\b' --glob '*.go'`;
- search test callers with `rg '\bSymbol\b' --glob '*_test.go'`;
- check CLI/WASM/plugin/registry entrypoints;
- check constants, `//go:embed`, `init`, exported symbols, and generated files.
- if touching WASM/platform-specific areas, include platform builds such as `GOARCH=wasm GOOS=js go build ./...` or the local equivalent.

GH AW's original workflow and `DEADCODE.md` guide used `deadcode` plus caller, test-caller, WASM, console stub, constants, embed, build, vet, fmt, and test checks. Adapt those checks to the local repository instead of copying paths literally.

## JavaScript / TypeScript

Candidate tools:

```bash
npx --no-install knip
npx --no-install ts-prune
npx --no-install tsc --noEmit
npx --no-install eslint .
```

Useful checks:

- package `exports`, bin entries, scripts, framework routes, dynamic imports, and plugin registries;
- Storybook, tests, fixtures, generated files, build artifacts, and public package APIs;
- string-dispatched handlers and dependency injection containers;
- type-only exports that may be part of public API.

Prefer `--no-install` forms to avoid network/dependency changes during study.

## Python

Candidate tools:

```bash
python -m vulture .
python -m pyflakes .
python -m pytest
```

Useful checks:

- decorators, framework registration, CLI entrypoints, import side effects, plugin discovery, migrations, fixtures, and dynamic imports;
- package `__all__`, setup/pyproject entrypoints, notebooks, docs examples, and scripts.

## Rust

Candidate tools:

```bash
cargo check
cargo test
cargo clippy -- -W dead_code
```

Useful checks:

- features, target-specific modules, public crate API, macros, proc macros, examples, benches, and integration tests.

## Generic Fallback

When no language analyzer is available:

```bash
rg --files
rg -n 'candidate_name'
git grep -n 'candidate_name'
```

Then inspect:

- imports/exports;
- call/reference sites;
- test-only use;
- runtime/config/docs references;
- public API boundaries;
- verification available after deletion.

Generic text search is weak evidence. Use it to prioritize reading, not to prove deletion.
