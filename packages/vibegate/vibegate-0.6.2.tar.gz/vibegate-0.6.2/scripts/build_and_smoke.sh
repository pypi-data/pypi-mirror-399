#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

"$ROOT_DIR/scripts/clean_build.sh"

echo "Building wheel and sdist"
python3 -m build

echo "Running twine check"
python3 -m twine check dist/*

VENV_DIR="$ROOT_DIR/.venv-smoke"
if [ -d "$VENV_DIR" ]; then
  rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"

WHEEL_PATH=$(python3 - <<'PY'
from pathlib import Path
import sys

dist = Path("dist")
wheels = sorted(dist.glob("*.whl"), key=lambda p: p.stat().st_mtime, reverse=True)
if not wheels:
    print("No wheel found in dist/", file=sys.stderr)
    sys.exit(1)
print(wheels[0])
PY
)

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install "$WHEEL_PATH"

"$VENV_DIR/bin/vibegate" --help
"$VENV_DIR/bin/vibegate" version

set +e
"$VENV_DIR/bin/vibegate" doctor .
doctor_status=$?
set -e
if [ $doctor_status -ne 0 ]; then
  echo "vibegate doctor reported issues (missing tools or version drift). See output above."
  exit $doctor_status
fi
