#!/usr/bin/env bash
# Install skills from this hub into one or more Agent Skills directories.
# Default: symlink into ~/.agents/skills, shared by Codex and Cursor.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"

TARGET="shared"
MODE="link" # link | copy
ONLY=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [options]

Options:
  --target shared|cursor|claude|codex|all|DIR
                                      Install destination (default: shared)
  --mode link|copy                   Symlink (default) or copy
  --only id1,id2                     Only install these skill ids
  --dry-run                          Print actions without changing files
  -h, --help                         Show help

Destinations:
  shared  -> ~/.agents/skills (Codex + Cursor)
  codex   -> ~/.agents/skills
  cursor  -> ~/.cursor/skills
  claude  -> ~/.claude/skills
  all     -> ~/.agents/skills + ~/.claude/skills
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:?}"; shift 2 ;;
    --mode) MODE="${2:?}"; shift 2 ;;
    --only) ONLY="${2:?}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

case "$TARGET" in
  shared|codex) DESTS=("${HOME}/.agents/skills") ;;
  cursor)       DESTS=("${HOME}/.cursor/skills") ;;
  claude)       DESTS=("${HOME}/.claude/skills") ;;
  all)          DESTS=("${HOME}/.agents/skills" "${HOME}/.claude/skills") ;;
  *)            DESTS=("$TARGET") ;;
esac

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "Missing $SKILLS_DIR — run: git submodule update --init --recursive" >&2
  exit 1
fi

should_install() {
  local id="$1"
  [[ -z "$ONLY" ]] && return 0
  [[ ",${ONLY}," == *",${id},"* ]]
}

install_one() {
  local id="$1"
  local dest="$2"
  local src="$SKILLS_DIR/$id"
  local dst="$dest/$id"

  if [[ ! -e "$src" ]]; then
    echo "skip  $id (submodule missing; run sync/init first)"
    return 0
  fi

  if ! should_install "$id"; then
    return 0
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "would $MODE  $src -> $dst"
    return 0
  fi

  if [[ -e "$dst" || -L "$dst" ]]; then
    rm -rf "$dst"
  fi

  case "$MODE" in
    link)
      ln -s "$src" "$dst"
      echo "linked  $id -> $dst"
      ;;
    copy)
      cp -a "$src" "$dst"
      echo "copied  $id -> $dst"
      ;;
    *)
      echo "Invalid --mode: $MODE" >&2
      exit 1
      ;;
  esac
}

shopt -s nullglob
found=0
for dest in "${DESTS[@]}"; do
  if [[ "$DRY_RUN" -eq 0 ]]; then
    mkdir -p "$dest"
  fi
  for src in "$SKILLS_DIR"/*/; do
    id="$(basename "$src")"
    install_one "$id" "$dest"
    found=1
  done
done
shopt -u nullglob

if [[ "$found" -eq 0 ]]; then
  echo "No skills under $SKILLS_DIR. Initialize submodules first:" >&2
  echo "  git submodule update --init --recursive" >&2
  exit 1
fi

echo
echo "Done. Destination(s): ${DESTS[*]}"
echo "Restart / reload your agent so skills are picked up."
