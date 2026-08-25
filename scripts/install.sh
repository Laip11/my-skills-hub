#!/usr/bin/env bash
# Install skills from this hub into a local agent skills directory.
# Default: symlink into ~/.cursor/skills (does NOT merge into one skill).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"

TARGET="cursor"
MODE="link" # link | copy
ONLY=""
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: ./scripts/install.sh [options]

Options:
  --target cursor|claude|codex|DIR   Install destination (default: cursor)
  --mode link|copy                   Symlink (default) or copy
  --only id1,id2                     Only install these skill ids
  --dry-run                          Print actions without changing files
  -h, --help                         Show help

Destinations:
  cursor  -> ~/.cursor/skills
  claude  -> ~/.claude/skills
  codex   -> ~/.codex/skills
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
  cursor) DEST="${HOME}/.cursor/skills" ;;
  claude) DEST="${HOME}/.claude/skills" ;;
  codex)  DEST="${HOME}/.codex/skills" ;;
  *)      DEST="$TARGET" ;;
esac

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "Missing $SKILLS_DIR — run: git submodule update --init --recursive" >&2
  exit 1
fi

mkdir -p "$DEST"

should_install() {
  local id="$1"
  [[ -z "$ONLY" ]] && return 0
  [[ ",${ONLY}," == *",${id},"* ]]
}

install_one() {
  local id="$1"
  local src="$SKILLS_DIR/$id"
  local dst="$DEST/$id"

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
for src in "$SKILLS_DIR"/*/; do
  id="$(basename "$src")"
  install_one "$id"
  found=1
done
shopt -u nullglob

if [[ "$found" -eq 0 ]]; then
  echo "No skills under $SKILLS_DIR. Initialize submodules first:" >&2
  echo "  git submodule update --init --recursive" >&2
  exit 1
fi

echo
echo "Done. Destination: $DEST"
echo "Restart / reload your agent so skills are picked up."
