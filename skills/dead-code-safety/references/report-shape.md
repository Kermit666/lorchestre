# Dead Code Report Shape

Use this shape for dead-code reports or cleanup handoffs.

## Compact Report

```markdown
## Dead Code Summary

- Scope:
- Languages/tools checked:
- Overall read:
- Recommended next route:

## High-Confidence Delete Candidates

### 1. <symbol or file>

- Type:
- Location:
- Evidence:
- Reference summary:
- Test caller summary:
- False-positive gates checked:
- Exclusive tests:
- Public API/runtime risk:
- Required verification:
- Confidence:
- Suggested batch:

## Needs Investigation

- `<symbol/file>` - missing evidence or unresolved risk.

## Keep Or Defer

- `<symbol/file>` - why deletion is not currently safe.

## Proposed Deletion Batch

1. <smallest safe deletion>
2. <next deletion only if verification remains green>

## Execution Stop Conditions

- <condition that should stop deletion and return for planning or more study>

## Analysis Metadata

- Candidate tools used:
- Files/symbols inspected:
- Public/runtime gates checked:
- Commands run:
- Evidence files, if any:
- Analysis date or repo state:
```

## Finding Rules

- Cite concrete files, symbols, commands, and reference checks.
- Separate analyzer signal from confirmed evidence.
- Do not promote unresolved dynamic/public API risk to high confidence.
- Do not promote test-only callers to high confidence unless exclusive-test and shared-helper risk has been checked.
- Include "keep or defer" when a tempting deletion would be unsafe.
- If no material candidates exist, say what was checked and why no cleanup is useful.

## Cleanup Handoff Gate

A candidate is ready for cleanup planning only when it includes:

- exact file/symbol target;
- confidence class;
- checked false-positive gates;
- test caller and exclusive-test assessment;
- expected behavior preservation;
- verification commands;
- deletion batch boundary;
- stop conditions.
