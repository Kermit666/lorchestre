# Topology Report Shape

Use this shape when the user wants a reusable report or refactor proposal.

## Compact Report

```markdown
## Topology Summary

- Scope:
- Overall read:
- Biggest topology pressure:
- Recommended route:

## Findings

### 1. <finding title>

- Type:
- Evidence:
- Why it matters:
- Candidate move:
- Behavior risk:
- Public API/import risk:
- Test impact:
- Verification:
- Confidence:

## Proposed Move Order

1. <smallest safe move>
2. <next move only if still needed>

## Not Recommended

- <refactor idea rejected and why>

## Open Questions

- <only questions that block route choice>

## Analysis Metadata

- Source files inspected:
- Symbols or modules cataloged:
- Largest files considered:
- Function/export/import-cycle checks:
- Duplicate or pattern gates used:
- Optional providers used:
- Provider degraded/skipped notes:
- Analysis date or repo state:
```

## Finding Rules

- Cite concrete files and symbols.
- State whether each finding is fact, interpretation, or proposal.
- Distinguish threshold/pattern signals from confirmed topology findings.
- Prefer a few material findings over many low-value notes.
- Include "not recommended" when a tempting refactor would overbuild the design.
- If no material finding exists, say what was checked and why no move is useful.

## Proposal Quality Gate

A proposal is usable only when it includes:

- a target path/symbol list;
- a current owner and proposed owner;
- expected navigation or ownership benefit;
- behavior risk and import/API risk;
- verification plan;
- smallest safe first step.

If any item is missing, keep it as a study observation, not an execution proposal.
