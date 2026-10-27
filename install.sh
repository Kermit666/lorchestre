#!/usr/bin/env bash
# Install Lorchestre for Claude Code, Codex, or both, by copying files into
# your home directory. Rerun after pulling to update. Existing files with the
# same names are overwritten; your books in book-router are kept.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${1:-}"
case "$target" in
  claude|codex|both) ;;
  *) echo "usage: $0 claude|codex|both" >&2; exit 1 ;;
esac

skills=(book-router topology-study dead-code-safety)

# Copy a companion skill, keeping any books the user already added.
copy_skill() {
  local name="$1" dest="$2/$1"
  mkdir -p "$dest"
  if command -v rsync >/dev/null; then
    rsync -a --exclude 'references/books/' --exclude 'references/library/registry.json' \
      "$repo/skills/$name/" "$dest/"
  else
    tar -C "$repo/skills/$name" --exclude './references/books' \
      --exclude './references/library/registry.json' -cf - . | tar -C "$dest" -xf -
  fi
  local registry="references/library/registry.json"
  if [ -f "$repo/skills/$name/$registry" ] && [ ! -f "$dest/$registry" ]; then
    cp "$repo/skills/$name/$registry" "$dest/$registry"
  fi
}

if [ "$target" = claude ] || [ "$target" = both ]; then
  claude_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
  mkdir -p "$claude_dir/skills/lorchestre" "$claude_dir/agents"
  cp "$repo/claude/skills/lorchestre/SKILL.md" "$claude_dir/skills/lorchestre/SKILL.md"
  cp "$repo"/claude/agents/lorchestre-*.md "$claude_dir/agents/"
  for s in "${skills[@]}"; do copy_skill "$s" "$claude_dir/skills"; done
  echo "Claude Code: installed into $claude_dir. Start a new session and run /lorchestre."
fi

if [ "$target" = codex ] || [ "$target" = both ]; then
  mkdir -p "$HOME/.agents/skills/lorchestre/agents" "$HOME/.codex/agents"
  cp "$repo/codex/skills/lorchestre/SKILL.md" "$HOME/.agents/skills/lorchestre/SKILL.md"
  cp "$repo/codex/skills/lorchestre/agents/openai.yaml" "$HOME/.agents/skills/lorchestre/agents/openai.yaml"
  cp "$repo"/codex/agents/lorchestre-*.toml "$HOME/.codex/agents/"
  for s in "${skills[@]}"; do copy_skill "$s" "$HOME/.agents/skills"; done
  echo "Codex: installed into ~/.agents/skills and ~/.codex/agents. Start a new session and run \$lorchestre."
  if ! grep -q '^\[agents\]' "$HOME/.codex/config.toml" 2>/dev/null; then
    echo "Tip: add this to ~/.codex/config.toml so the Lead can spawn Study Subagents:"
    printf '  [agents]\n  max_depth = 2\n  max_threads = 16\n'
  fi
fi
