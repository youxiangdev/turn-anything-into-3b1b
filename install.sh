#!/bin/bash
# Install the turn-anything-into-3b1b skills for Claude Code and Codex.
#
# From the web (downloads into ~/.turn-anything-into-3b1b, then links the skills):
#   curl -fsSL https://raw.githubusercontent.com/youxiangdev/turn-anything-into-3b1b/main/install.sh | bash
#   Options go after "bash -s --", for example:  ... | bash -s -- --no-codex
#
# From a checkout of the repository:
#   ./install.sh             link into ~/.claude/skills, and into Codex's skills folder when Codex is installed
#   ./install.sh --codex     link into Codex's skills folder even when Codex was not found
#   ./install.sh --no-codex  Claude Code only
#   ./install.sh --update    fetch the newest version first (a git checkout only), then link
#   ./install.sh --remove    remove the links this script made
#   ./install.sh --list      show what is linked, without changing anything
#   ./install.sh --adopt DIR copy a skill folder made elsewhere into skills/, then link everything
#
# Only symlinks are created or removed. Anything already present under a skill's name that is
# not a link into this folder is left alone and reported.

set -u
REPO="youxiangdev/turn-anything-into-3b1b"
BRANCH="main"
HOME_DIR="${TURN_ANYTHING_HOME:-$HOME/.turn-anything-into-3b1b}"

# ---- started from the web: there is no checkout beside this script, so get one and hand over ----
SELF="${BASH_SOURCE[0]:-}"
KIT=""
if [ -n "$SELF" ] && [ -f "$SELF" ]; then
  KIT="$(cd "$(dirname "$SELF")" && pwd -P)"
fi
if [ -z "$KIT" ] || [ ! -d "$KIT/skills" ]; then
  case " $* " in
    *" --remove "*|*" --list "*)
      [ -f "$HOME_DIR/install.sh" ] || { echo "Nothing is installed in $HOME_DIR."; exit 0; } ;;
    *)
      if [ -d "$HOME_DIR/.git" ]; then
        echo "Updating $HOME_DIR"
        git -C "$HOME_DIR" pull --ff-only --quiet || { echo "Could not update $HOME_DIR; using the copy that is there." >&2; }
      elif [ -e "$HOME_DIR" ] && [ -n "$(ls -A "$HOME_DIR" 2>/dev/null)" ] && [ ! -f "$HOME_DIR/install.sh" ]; then
        echo "$HOME_DIR exists and is not this kit. Move it away, or set TURN_ANYTHING_HOME to another folder." >&2; exit 1
      elif command -v git >/dev/null 2>&1; then
        echo "Downloading into $HOME_DIR"
        rm -rf "$HOME_DIR.tmp"
        git clone --depth 1 --branch "$BRANCH" --quiet "https://github.com/$REPO.git" "$HOME_DIR.tmp" || { echo "Download failed." >&2; exit 1; }
        rm -rf "$HOME_DIR" && mv "$HOME_DIR.tmp" "$HOME_DIR"
      else
        echo "Downloading into $HOME_DIR (no git here, so it will not update by itself; run this command again to update)"
        rm -rf "$HOME_DIR.tmp" && mkdir -p "$HOME_DIR.tmp"
        curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH" | tar -xz --strip-components 1 -C "$HOME_DIR.tmp" \
          || { echo "Download failed." >&2; rm -rf "$HOME_DIR.tmp"; exit 1; }
        rm -rf "$HOME_DIR" && mv "$HOME_DIR.tmp" "$HOME_DIR"
      fi ;;
  esac
  exec bash "$HOME_DIR/install.sh" "$@"
fi

# ---- from here on: KIT is a checkout ----
MODE=install
CODEX=auto
UPDATE=0
ADOPT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --codex) CODEX=1 ;;
    --no-codex) CODEX=0 ;;
    --update) UPDATE=1 ;;
    --remove) MODE=remove ;;
    --list) MODE=list ;;
    --adopt) shift; ADOPT="${1:-}"; [ -n "$ADOPT" ] || { echo "--adopt needs a folder" >&2; exit 2; } ;;
    -h|--help) sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ "$UPDATE" = 1 ]; then
  if [ -d "$KIT/.git" ]; then git -C "$KIT" pull --ff-only || exit 1
  else echo "$KIT is not a git checkout; download it again to update" >&2; exit 2; fi
fi

if [ -n "$ADOPT" ]; then
  [ -f "$ADOPT/SKILL.md" ] || { echo "$ADOPT has no SKILL.md, so it is not a skill folder" >&2; exit 2; }
  from="$(cd "$ADOPT" && pwd -P)"
  name="$(basename "$from")"
  case "$from/" in "$KIT"/*) echo "$from is already inside this folder" >&2; exit 2 ;; esac
  [ -e "$KIT/skills/$name" ] && { echo "skills/$name already exists here; remove or rename it first" >&2; exit 2; }
  cp -R "$from" "$KIT/skills/$name" && echo "copied     $from -> skills/$name"
  echo "The original was left where it is. If it sits in a skills folder, remove it there"
  echo "and run ./install.sh again so that the copy in this folder is the one in use."
fi

# Codex reads ~/.codex/skills where that folder exists, and ~/.agents/skills otherwise.
if [ "$CODEX" = auto ]; then
  if [ -d "$HOME/.codex" ] || [ -d "$HOME/.agents/skills" ] || command -v codex >/dev/null 2>&1; then CODEX=1; else CODEX=0; fi
fi
DESTS=("$HOME/.claude/skills")
if [ "$CODEX" = 1 ]; then
  if [ -d "$HOME/.codex/skills" ]; then DESTS+=("$HOME/.codex/skills"); else DESTS+=("$HOME/.agents/skills"); fi
fi

status=0
for dest in "${DESTS[@]}"; do
  echo "$dest"
  [ "$MODE" = install ] && mkdir -p "$dest"
  for skill in "$KIT"/skills/*/; do
    [ -f "$skill/SKILL.md" ] || continue
    name="$(basename "$skill")"
    src="$KIT/skills/$name"
    link="$dest/$name"
    current=""
    [ -L "$link" ] && current="$(readlink "$link")"
    case "$MODE" in
      list)
        if [ "$current" = "$src" ]; then echo "  linked     $name"
        elif [ -e "$link" ] || [ -L "$link" ]; then echo "  other      $name (something else is installed under this name)"
        else echo "  not linked $name"; fi ;;
      remove)
        if [ "$current" = "$src" ]; then rm "$link" && echo "  removed    $name"
        elif [ -e "$link" ] || [ -L "$link" ]; then echo "  skipped    $name (not a link made by this script)"
        else echo "  not linked $name"; fi ;;
      install)
        if [ "$current" = "$src" ]; then echo "  ok         $name"
        elif [ -e "$link" ] || [ -L "$link" ]; then
          echo "  SKIPPED    $name: $link already exists and is not a link into this folder"; status=1
        else ln -s "$src" "$link" && echo "  linked     $name"; fi ;;
    esac
  done
done

case "$MODE" in
  install)
    echo
    if [ "$status" = 0 ]; then echo "Done. Start a new session and type:  /deep-dive <a paper, a link, a repository or a topic>"
    else echo "Some skills were skipped because another skill already uses their name. Rename or remove those, then run this again."; fi
    command -v python3 >/dev/null 2>&1 || echo "Note: python3 was not found. The skills' scripts need it."
    command -v node >/dev/null 2>&1 || echo "Note: node was not found. The explainer's script outline needs it."
    ;;
  remove)
    [ "$KIT" = "$HOME_DIR" ] && echo && echo "The links are gone. To delete the download too, remove the folder $HOME_DIR" ;;
esac
exit $status
