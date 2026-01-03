#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Cleaning build artifacts in $ROOT_DIR"

find . -maxdepth 1 -type d \( -name "dist" -o -name "build" \) -print0 | xargs -0 -r rm -rf
find . -maxdepth 2 -type d -name "*.egg-info" -print0 | xargs -0 -r rm -rf
