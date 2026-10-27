# Host wording

The Claude Code files (`claude/`) and the Codex files (`codex/`) are full
copies of the same prompts. The Codex text was made from the final Claude text
by swapping only the sentences below; everything else is identical. Edit both
variants together: change a shared sentence in both trees, and keep the meaning
of a sentence listed here aligned. Check with `diff` (for the Codex agents,
compare against the `developer_instructions` text).

Packaging also differs. Claude agents are Markdown with YAML frontmatter
(`name: lorchestre-<role>`, `description`, `model: inherit`, and
`disallowedTools: Agent` for the Worker and Study Subagent). Codex agents are
TOML with only `name = "lorchestre_<role>"`, `description`, and
`developer_instructions`, and no model or effort key, so the user's Codex
configuration applies. Codex has no tools key, so "Do not spawn additional
agents" in the Worker and Study Subagent text is the only guard there. The Codex
skill also has `agents/openai.yaml` (`display_name: "Lorchestre"`, a
`default_prompt` naming `$lorchestre`).

## General swaps

| Claude Code | Codex | Why |
| --- | --- | --- |
| "Claude Code" (host name) | "Codex" | host name |
| conversation, agent | thread, child | Codex terms |
| `lorchestre-lead`, `lorchestre-worker`, `lorchestre-study-subagent` | `lorchestre_lead`, `lorchestre_worker`, `lorchestre_study_subagent` | Codex agent names use underscores; file names stay hyphenated |
| `/lorchestre` | `$lorchestre` | invocation syntax |
| "with the `Skill` tool, which loads its instructions" | "Read ... instructions" | how each host loads a skill |
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` | `agents.max_depth` | how each host controls nesting depth |

## Coordinator (`SKILL.md`)

| Claude Code | Codex | Why |
| --- | --- | --- |
| description: "Claude Code development work ... invokes /lorchestre or asks Claude Code" | "Codex development work ... invokes $lorchestre or asks Codex" | host name, invocation |
| "in the current Claude Code conversation. Use Claude Code's native agents" | "in the current Codex thread. Use Codex's native agents" | host name and term |
| "through Claude Code's native agent nesting" | "through Codex's native subagent system" | host mechanism |
| "Rely on Claude Code's native agent visibility" | "Rely on Codex's native subagent visibility" | host name |
| "Inherit the current Claude Code permissions" | "Inherit the current Codex permissions" | host name |
| "selection in the current conversation" | "selection in the current thread" | host term |
| "never broadens Claude Code's native permissions" | "never broadens Codex's native permissions" | host name |
| "Return to the same Lead agent with `SendMessage`" | "Return to the same Lead thread" | how a child is continued |
| "everything stays in one place, cleanup is easy, and sandboxed hosts allow it." | "everything stays in one place, cleanup is easy, and the session's sandbox, which children share, allows it." | Codex children share the parent's sandbox; a worktree outside the writable roots would block the Worker |
| "Use the exact custom agent names. Put the complete assignment in the `Agent` tool prompt" | "Use the exact custom agent names, and always name the agent type when you spawn: without it the child inherits this whole thread. Put the complete assignment in the native spawn call" | spawn mechanism; an unnamed Codex spawn forks the whole parent thread |
| "Continue an existing agent with `SendMessage` ...; it keeps its full context. ... Agents may run in the background. ... wait for that agent to finish" | "Continue an existing child with a follow-up message ...; it keeps its thread. ... Children run alongside you. ... wait for that child to finish ... Close children you no longer need: open ones count against Codex's limit on concurrent agents (6 by default, 4 with the newer agent tools)." | continuation mechanism; Codex caps open children until they are closed |
| "when the current Claude Code surface supports progress updates" | "when the current Codex surface supports progress updates" | host name |
| "If the Lead reports that Lead -> Study nesting was unavailable ... needs the `Agent` tool available to sub-agents (nesting is on by default; a `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` of 1 turns it off) ... another Claude Code process" | "If the current Codex configuration prevents Lead -> Study nesting ... `agents.max_depth = 2` enables the intended nested route; the default allows only one level ... another Codex process" | each host controls nesting differently; Codex allows one level by default |
| "To choose a lighter agent, set the `model` field when you spawn it; leaving it empty runs the agent at your own level. Only pick a model you know is lighter than yours; if unsure, leave it empty." | "The user has asked that simpler work run lighter: when you spawn a child for it, lower `reasoning_effort`, or set `model` to a lighter one from the models the spawn tool lists; leaving both empty runs the child at your own level. If unsure whether a model is lighter than yours, keep your model and only lower the effort; if the spawn tool shows no model or effort fields, spawn normally and let the user's `[agents]` settings decide." | how each host spawns a lighter agent: Claude Code takes a per-spawn `model`; Codex children also take `reasoning_effort`, may not expose either field, and fall back to the user's `[agents]` settings |

## Lead

| Claude Code | Codex | Why |
| --- | --- | --- |
| "Inherit Claude Code's permissions" | "Inherit native Codex permissions" | host name |
| "Use the `lorchestre-study-subagent` agent for bounded slices" | "Use `lorchestre_study_subagent` for bounded slices" | agent name form |
| "Launch each Study Subagent with the `Agent` tool and put the complete assignment in its prompt:" | "Spawn each Study Subagent by naming its agent type, so it does not inherit your whole thread, and put the complete assignment in the spawn call:" | spawn mechanism |
| "continue the same Study Subagent with `SendMessage`, which keeps its context" | "continue the same Study Subagent with a follow-up message; it keeps its thread" | continuation mechanism |
| "Study Subagents may run in the background." | "Study Subagents run alongside you." | host term |
| (none) | "Close a Study Subagent once its report is used; open children count against Codex's limit on concurrent agents." | Codex concurrent-agent cap |
| "If the `Agent` tool is unavailable ... another Claude Code process" | "If native nesting is unavailable ... another Codex process" | spawn mechanism, host name |
| "Invoke a selected skill with the `Skill` tool, which loads its instructions, before using it." | "Read a selected skill's instructions before using it." | skill loading |
| "To choose a lighter agent, set the `model` field when you spawn it; leaving it empty runs the agent at your own level. Only pick a model you know is lighter than yours; if unsure, leave it empty." | "The user has asked that simpler work run lighter: when you spawn a child for it, lower `reasoning_effort`, or set `model` to a lighter one from the models the spawn tool lists; leaving both empty runs the child at your own level. If unsure whether a model is lighter than yours, keep your model and only lower the effort; if the spawn tool shows no model or effort fields, spawn normally and let the user's `[agents]` settings decide." | how each host spawns a lighter agent: Claude Code takes a per-spawn `model`; Codex children also take `reasoning_effort`, may not expose either field, and fall back to the user's `[agents]` settings |

## Worker

| Claude Code | Codex | Why |
| --- | --- | --- |
| "Inherit Claude Code's permissions" | "Inherit native Codex permissions" | host name |
| "Follow the applicable `CLAUDE.md` instructions, read any applicable `AGENTS.md` files, and use relevant installed skills through the `Skill` tool." | "Read applicable `AGENTS.md` files and use relevant installed skills." | host instruction files, skill loading |
| "Git and Claude Code retain those." | "Git and Codex retain those." | host name |

## Study Subagent

| Claude Code | Codex | Why |
| --- | --- | --- |
| "Inherit Claude Code's permissions" | "Inherit native Codex permissions" | host name |
| "Invoke them with the `Skill` tool, which loads their instructions, before using them." | "Read their instructions before using them." | skill loading |
