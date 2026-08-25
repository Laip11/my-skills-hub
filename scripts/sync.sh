#!/usr/bin/env bash
# Pull latest commits for all skill submodules (keeps them independent).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .gitmodules ]]; then
  echo "No .gitmodules yet. Add submodules first." >&2
  exit 1
fi

echo "Initializing / updating submodules..."
git submodule update --init --recursive

echo "Fetching latest from each upstream (remote tracking branch)..."
git submodule update --remote --merge

echo
echo "Submodule status:"
git submodule status

echo
echo "Tip: commit the updated submodule pointers if you want to pin new versions:"
echo "  git add skills && git commit -m 'chore: bump skill submodules'"
