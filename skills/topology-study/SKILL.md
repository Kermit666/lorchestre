---
name: topology-study
description: Study repository topology and refactor placement using GitHub Agentic Workflows-inspired continuous refactoring methods. Use when you need to inspect code organization, module boundaries, ownership, dependency direction, oversized files/functions, excess exports, import cycles, misplaced functions/classes, scattered helpers, near-duplicate functionality, test topology, public API/import risk, "file diet", semantic function clustering, architecture-guardian signals, or topology-sensitive refactor proposals.
---

# Topology Study

## Core Rule

Use this skill for read-only topology analysis first. A topology report or proposal does not authorize execution; follow the caller's authority model before any implementation.

The method is adapted from GitHub Agentic Workflows continuous-refactoring examples, especially semantic function clustering, daily file diet, architecture guardian, and duplicate-code detection. The GH AW output model is GitHub issues; this skill's output model is a local topology report or refactor proposal.

## Workflow

1. Scope the study.
   - Use the user-named paths when present.
   - If no path is named, start from changed files, active feature area, or likely source roots.
   - Keep out-of-scope paths explicit.
2. Gather shape facts before interpreting.
   - Use `rg`, `find`, `git`, language tools, and existing tests/docs.
   - Run `scripts/topology_snapshot.py` when a quick file/symbol/import/test-peer inventory would help.
   - Check file size, function size, export count, import cycles, and duplicate-pattern signals when they are relevant to the scope.
   - Treat semantic tools such as Serena/LSP as optional providers, not requirements.
3. Infer purpose.
   - Name each important file/folder's apparent responsibility in one short phrase.
   - Identify public entrypoints, exports, import hubs, test peers, and ownership clues.
4. Cluster concepts.
   - Group symbols by name pattern, domain noun, shared data type, caller/callee relation, and behavior purpose.
   - Compare clusters with current file/module placement.
5. Record topology findings only when evidence is concrete.
   - Good findings include oversized files, mixed responsibilities, misplaced symbols, scattered helpers, duplicate or near-duplicate logic, import-direction risk, public API risk, and awkward test topology.
   - Skip minor naming taste, isolated tiny helpers, acceptable language idioms, and unproven "could be cleaner" observations.
6. Propose small moves.
   - Prefer one concept move/split at a time.
   - Preserve behavior and public imports unless the user explicitly wants a breaking reorganization.
   - Include verification before and after each proposed move.
7. Separate authority.
   - Provider signal is not a smell.
   - Agent analysis is not approval.
   - A proposed move is not permission to execute it.

## References

- Read `references/topology-method.md` for the full adapted method when doing a broad study or proposal.
- Read `references/report-shape.md` when the output should be structured or reusable by another agent.
- Read `references/gh-aw-source-map.md` when explaining provenance or the keep/adapt/drop decisions.
- Read `references/translation-audit.md` when refining the skill section by section against upstream GH AW.
- Read `references/upstream-sources.md` before opening raw upstream snapshots. Do not load raw upstream files during ordinary topology studies unless the user asks for provenance-level detail.

## Snapshot Helper

Use the helper only for local read-only evidence. `<skill-dir>` is this skill's own directory (the folder containing this
`SKILL.md`). Run the command from the project root.

```bash
python3 <skill-dir>/scripts/topology_snapshot.py --root . --paths src test --format markdown
```

If the helper misses a language-specific detail, continue with normal code reading. The helper is a fact collector, not an architecture judge.
