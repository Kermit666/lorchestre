# Upstream GH AW Source Snapshots

These files are raw pinned snapshots from `github/gh-aw@v0.82.2`, tag hash `0b1173e7d380fb68a9d6749af62e49ca050eefc1`.

Use them for audit, refinement, or provenance checks. Do not load them during ordinary dead-code studies unless exact upstream wording matters.

| Local file | Upstream path | Lines | SHA-256 |
| --- | --- | ---: | --- |
| `upstream-gh-aw-v0.82.2/DEADCODE.md` | `DEADCODE.md` | 218 | `096d8815fb14fc0558f80d54c82af7fb35a3eb7a0cf12fc360f629fbafcfaf1b` |
| `upstream-gh-aw-v0.82.2/dead-code-remover.md` | `.github/workflows/dead-code-remover.md` | 236 | `ff80358a7c5db70ee13ed27a27a20828153b10e6ad77f14666bd35ce164d426a` |
| `upstream-gh-aw-v0.82.2/dead-code-agent-blog.md` | `docs/src/content/docs/blog/2026-05-28-agent-of-the-day.md` | 55 | `d4864ddaf6b66b7221e96a159e1fc05cf895e506260b83c6785092a70dc88d4f` |

## Why These Files

- `DEADCODE.md`: manual dead-code cleanup guide: analyzer scope, test-caller caveats, platform false positives, constant/embed rescue, phase checklist.
- `dead-code-remover.md`: main safety workflow: analyzer, candidate selection, caller checks, runtime gates, exclusive tests, verification, and small PR shape.
- `dead-code-agent-blog.md`: rationale for why dead-code cleanup is a good automation target: mechanical feedback and reviewable cleanup.
