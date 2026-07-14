#!/usr/bin/env bash
# Install the lettucemeet-cli skill for AI agent integration.
#
# Copies the skill to ~/.agents/skills/lettucemeet-cli/ so agents
# (Pi, Claude Code, Codex, etc.) can discover and use it automatically.
#
# Usage:
#   bash scripts/install-skill.sh          # install (copy)
#   bash scripts/install-skill.sh --link   # install (symlink)
#   bash scripts/install-skill.sh --uninstall  # remove

set -euo pipefail

SKILL_SOURCE="$(cd "$(dirname "$0")/.." && pwd)/.agents/skills/lettucemeet-cli"
SKILL_DEST="$HOME/.agents/skills/lettucemeet-cli"

MODE="${1:-copy}"

case "$MODE" in
  --uninstall)
    if [ -L "$SKILL_DEST" ] || [ -d "$SKILL_DEST" ]; then
      rm -rf "$SKILL_DEST"
      echo "Uninstalled lettucemeet-cli skill from $SKILL_DEST"
    else
      echo "Skill not installed."
    fi
    exit 0
    ;;
  --link)
    mkdir -p "$HOME/.agents/skills"
    ln -sfn "$SKILL_SOURCE" "$SKILL_DEST"
    echo "Installed lettucemeet-cli skill (symlink) -> $SKILL_DEST"
    echo "  links to $SKILL_SOURCE"
    ;;
  copy)
    mkdir -p "$HOME/.agents/skills"
    cp -r "$SKILL_SOURCE" "$SKILL_DEST"
    echo "Installed lettucemeet-cli skill (copy) -> $SKILL_DEST"
    ;;
  *)
    echo "Usage: $0 [--link|--uninstall]"
    echo ""
    echo "  (default)  Copy skill to ~/.agents/skills/"
    echo "  --link     Symlink skill (stays updated with repo)"
    echo "  --uninstall  Remove installed skill"
    exit 1
    ;;
esac
