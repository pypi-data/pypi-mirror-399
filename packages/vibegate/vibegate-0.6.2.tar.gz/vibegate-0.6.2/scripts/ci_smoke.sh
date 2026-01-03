#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
VENV_ROOT=""
if [ -n "${RUNNER_TEMP:-}" ]; then
  VENV_ROOT=$(mktemp -d "${RUNNER_TEMP%/}/vibegate-smoke-XXXXXX")
else
  VENV_ROOT=$(mktemp -d)
fi
VENV_DIR="${VENV_ROOT}/venv"

cleanup() {
  if [ -n "${VENV_ROOT}" ] && [ -d "${VENV_ROOT}" ]; then
    rm -rf "${VENV_ROOT}"
  fi
}
trap cleanup EXIT

cd "${REPO_ROOT}"
rm -rf "${REPO_ROOT}/dist"

python -m venv "${VENV_DIR}"
if [ -d "${VENV_DIR}/bin" ]; then
  VENV_BIN="${VENV_DIR}/bin"
else
  VENV_BIN="${VENV_DIR}/Scripts"
fi

"${VENV_BIN}/python" -m pip install -U pip
"${VENV_BIN}/python" -m pip install build
"${VENV_BIN}/python" scripts/sync_schemas.py --check
"${VENV_BIN}/python" scripts/sync_schemas.py
"${VENV_BIN}/python" -m build
"${VENV_BIN}/python" -m pip install "${REPO_ROOT}/dist/"*.whl

"${VENV_BIN}/vibegate" --version
"${VENV_BIN}/python" -m vibegate --version
"${VENV_BIN}/vibegate" doctor .
"${VENV_BIN}/vibegate" check .
