# Lorchestre

Lorchestre turns a Claude Code or Codex session into a small team for long
coding campaigns: big refactors, deep bug hunts, architecture work. It is
prompt text only, a skill and three agents, with no runtime or server.

- **Coordinator** (the skill, your session): talks with you, owns the mission,
  and routes the work. It stays out of technical digging so its context lasts
  the whole campaign.
- **Lead**: studies the code deeply, makes the design calls, and plans the
  work, including whether to split it into parallel slices.
- **Worker**: implements one plain mission, verifies it, and reports.
- **Study Subagent**: answers one bounded research question for the Lead,
  read-only.

## What it does

- **Campaign memory in your project.** Each campaign lives in
  `.lorchestre/campaigns/<id>/`: the mission, the Lead's study, execution
  reports. A campaign survives across sessions, and several can run at once.
- **Never touches your working tree.** Every campaign that changes code works
  on its own `lorchestre/` branch in a git worktree under `.worktrees/`. When
  the result passes its checks it lands on your current branch, and the
  temporary branch and worktree are deleted. Nothing is ever pushed.
- **Parallel Workers for big refactors.** The Lead can split the work into
  slices that run side by side, then they are merged and tested once together.
- **Cheaper agents for simple work.** The Lead runs at your session's level;
  mechanical work can go to lighter agents, never above your level. No model
  is named anywhere, so it follows whatever you run.
- **Supervised or autonomous.** Supervised asks before changing your project;
  autonomous runs to the end, for example overnight.

## Install

```sh
git clone https://github.com/Kermit666/lorchestre.git
cd lorchestre
./install.sh claude   # or: codex, both
```

Then start a new session and run `/lorchestre <what you want>` in Claude Code,
or `$lorchestre <what you want>` in Codex.

For Codex, add this to `~/.codex/config.toml` so the Lead can spawn Study
Subagents (the default allows only one level) and more agents can run at once:

```toml
[agents]
max_depth = 2
max_threads = 16
```

For headless Claude Code runs (`claude -p`), set
`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`, or background agents are stopped 10
minutes after the turn ends.

## Companion skills

The Lead uses these when they help; it works without them.

- **book-router**: routes a design question to the right section of an
  indexed programming book and applies that book's reasoning. **No books are
  included**, because they are copyrighted; see the
  [recommended books](skills/book-router/README.md#recommended-books) and how
  to add the ones you own.
- **topology-study**: studies module boundaries, dependency direction,
  oversized files, and duplicated code before a refactor.
- **dead-code-safety**: read-only dead-code analysis with false-positive
  checks before anything is deleted.

topology-study and dead-code-safety adapt methods from
[GitHub Agentic Workflows](https://github.com/github/gh-aw) (MIT license,
included next to the copied files).

## Layout

```text
claude/   the skill and agents for Claude Code
codex/    the same for Codex (TOML agents, ~/.agents skill)
skills/   companion skills, shared by both hosts
docs/host-wording.md   the only sentences that differ between the two hosts
```

The Claude and Codex versions are the same text apart from the lines listed
in `docs/host-wording.md`. When you change one, change the other the same way.
