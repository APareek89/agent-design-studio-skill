#!/usr/bin/env sh
# Install the self-contained skill folder into one or more hosts' Agent Skills directories.
#
#   scripts/install_skill.sh claude                 # personal install for Claude Code
#   scripts/install_skill.sh claude codex cursor    # several hosts at once
#   scripts/install_skill.sh --project claude       # project-level folder in the current repo
#   scripts/install_skill.sh --dir /path/to/skills  # any other location
#   scripts/install_skill.sh --list                 # show the folders this script uses
#
# The script copies skills/agent-design-studio into <dir>/agent-design-studio and
# backs up an existing copy as agent-design-studio.bak-<timestamp>. It installs
# nothing else, runs nothing, and needs no network. Host folders follow each
# tool's Agent Skills documentation as of November 2026; if your version uses
# another folder, pass --dir.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SRC="$HERE/skills/agent-design-studio"
NAME="agent-design-studio"
PROJECT=0
TARGETS=""
CUSTOM=""

personal_dir() {
  case "$1" in
    claude)   echo "$HOME/.claude/skills" ;;
    codex)    echo "$HOME/.codex/skills" ;;
    copilot)  echo "$HOME/.copilot/skills" ;;
    cursor)   echo "$HOME/.cursor/skills" ;;
    gemini)   echo "$HOME/.gemini/skills" ;;
    opencode) echo "$HOME/.config/opencode/skills" ;;
    agents)   echo "$HOME/.agents/skills" ;;
    *) return 1 ;;
  esac
}

project_dir() {
  case "$1" in
    claude)   echo ".claude/skills" ;;
    codex)    echo ".codex/skills" ;;
    copilot)  echo ".github/skills" ;;
    cursor)   echo ".cursor/skills" ;;
    gemini)   echo ".gemini/skills" ;;
    opencode) echo ".opencode/skills" ;;
    agents)   echo ".agents/skills" ;;
    *) return 1 ;;
  esac
}

invoke_hint() {
  case "$1" in
    claude)  echo "In Claude Code type: /agent-design-studio  (or ask: Use the agent-design-studio skill with this brief ...)" ;;
    codex)   echo "In Codex type: \$agent-design-studio followed by your brief" ;;
    *)       echo "Ask the assistant to use the agent-design-studio skill with your brief" ;;
  esac
}

usage() { sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --project) PROJECT=1 ;;
    --dir) shift; CUSTOM="${1:-}"; [ -n "$CUSTOM" ] || { echo "--dir needs a path" >&2; exit 2; } ;;
    --list)
      for h in claude codex copilot cursor gemini opencode agents; do
        printf '%-9s personal: %-32s project: %s\n' "$h" "$(personal_dir "$h")" "$(project_dir "$h")"
      done; exit 0 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "Unknown option $1" >&2; usage >&2; exit 2 ;;
    *) TARGETS="$TARGETS $1" ;;
  esac
  shift
done

[ -f "$SRC/SKILL.md" ] || { echo "Skill source not found at $SRC" >&2; exit 1; }
if [ -z "$TARGETS" ] && [ -z "$CUSTOM" ]; then usage >&2; exit 2; fi

install_into() {
  dir="$1"; label="$2"
  mkdir -p "$dir"
  dest="$dir/$NAME"
  if [ -e "$dest" ]; then
    backup="$dest.bak-$(date +%Y%m%d%H%M%S)"
    mv "$dest" "$backup"
    echo "Backed up existing install to $backup"
  fi
  cp -R "$SRC" "$dest"
  find "$dest" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
  echo "Installed $NAME for $label at $dest"
}

if [ -n "$CUSTOM" ]; then install_into "$CUSTOM" "custom"; fi
for host in $TARGETS; do
  if [ "$PROJECT" -eq 1 ]; then dir=$(project_dir "$host") || { echo "Unknown host $host" >&2; exit 2; }
  else dir=$(personal_dir "$host") || { echo "Unknown host $host" >&2; exit 2; }; fi
  install_into "$dir" "$host"
  invoke_hint "$host"
done
echo "PDF output needs: python3 -m pip install -r $SRC/requirements-pdf.txt"
