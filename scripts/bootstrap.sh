#!/usr/bin/env bash
# Locate or install a local AgentGuard CLI for showcase evaluation.
# Does not modify the core repository source tree.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
. "${SCRIPT_DIR}/lib.sh"

INSTALL=0
for arg in "$@"; do
  case "${arg}" in
    --install) INSTALL=1 ;;
    --keep-workspace) ;;
    -h|--help)
      cat <<'EOF'
Usage: ./scripts/bootstrap.sh [--install]

Discover a local AgentGuard installation for this showcase.

  --install   If the sibling core checkout exists, create ./.venv in this
              repository and install the core in editable mode. Does not
              modify AgentGuard source files.

This script never assumes that `pip install agentguard` from PyPI is the
AgentGuard project used by these demos.
EOF
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "${arg}" >&2
      exit 2
      ;;
  esac
done

CORE_CANDIDATE="$(cd "${SHOWCASE_ROOT}/.." && pwd)/agentguard"
PYTHON_BIN="${PYTHON:-python3}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  printf 'Python is required (3.11+). PYTHON=%s was not found.\n' "${PYTHON_BIN}" >&2
  exit 1
fi

if agentguard_discover && ag --version >/dev/null 2>&1; then
  printf 'AgentGuard is already available.\n'
  agentguard_require
  exit 0
fi

if [[ ! -d "${CORE_CANDIDATE}" || ! -f "${CORE_CANDIDATE}/pyproject.toml" ]]; then
  cat >&2 <<EOF
Could not find the sibling AgentGuard core checkout at:
  ${CORE_CANDIDATE}

Clone or place the core repository next to this showcase, then rerun:

  ./scripts/bootstrap.sh --install
EOF
  exit 1
fi

if [[ "${INSTALL}" -ne 1 ]]; then
  cat >&2 <<EOF
Found sibling core checkout:
  ${CORE_CANDIDATE}

No AgentGuard executable is on PATH. Install a local evaluator environment:

  ./scripts/bootstrap.sh --install

or:

  python3 -m venv .venv
  .venv/bin/pip install -e "${CORE_CANDIDATE}"
  export AGENTGUARD="\$PWD/.venv/bin/agentguard"
EOF
  exit 1
fi

VENV="${SHOWCASE_ROOT}/.venv"
if [[ ! -x "${VENV}/bin/python" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV}"
fi
"${VENV}/bin/python" -m pip install --upgrade pip
"${VENV}/bin/python" -m pip install -e "${CORE_CANDIDATE}"

export AGENTGUARD="${VENV}/bin/agentguard"
agentguard_require
printf '\nExport this in your shell if needed:\n  export AGENTGUARD=%s\n' "${AGENTGUARD}"
