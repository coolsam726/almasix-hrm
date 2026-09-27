#!/usr/bin/env bash
# Install Almasix HRM against sibling Almasix, Conduit, and Orbit checkouts.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ALMASIX="$(cd "$ROOT/../almasix" && pwd)"
CONDUIT="$(cd "$ROOT/../almasix-conduit" && pwd)"
ORBIT="$(cd "$ROOT/../almasix-orbit" && pwd)"

if [[ ! -f "$ALMASIX/pyproject.toml" ]]; then
  echo "error: expected Almasix checkout at $ALMASIX" >&2
  exit 1
fi
if [[ ! -f "$CONDUIT/pyproject.toml" ]]; then
  echo "error: expected Almasix Conduit checkout at $CONDUIT" >&2
  exit 1
fi
if [[ ! -f "$ORBIT/packages/combined/pyproject.toml" ]]; then
  echo "error: missing combined Orbit package at $ORBIT/packages/combined" >&2
  exit 1
fi

ln -sfn "$ORBIT/packages/combined/src/almasix/orbit" "$ALMASIX/src/almasix/orbit"
if ! grep -q '^src/almasix/orbit$' "$ALMASIX/.gitignore" 2>/dev/null; then
  printf '\n# Local Orbit checkout (symlink for IDE / editable apps)\nsrc/almasix/orbit\n' \
    >> "$ALMASIX/.gitignore"
fi

cd "$ROOT"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip setuptools wheel
pip install -e "${ALMASIX}[conduit]"
pip install -e "$CONDUIT"
pip install -e "$ORBIT/packages/combined"
pip install -e ".[dev]"
echo "OK — run: source .venv/bin/activate && smith migrate --seed && smith serve"
echo "Login: ada@northwind.test / secret"
