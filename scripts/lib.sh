# Shared helpers for AgentGuard showcase demos.
# Sourced by demo runners; not executed directly.

set -euo pipefail

if [[ -n "${SHOWCASE_LIB_LOADED:-}" ]]; then
  return 0
fi
SHOWCASE_LIB_LOADED=1

_SHOWCASE_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHOWCASE_ROOT="$(cd "${_SHOWCASE_LIB_DIR}/.." && pwd)"

KEEP_WORKSPACE=0
NO_COLOR="${NO_COLOR:-}"

for _arg in "$@"; do
  case "${_arg}" in
    --keep-workspace) KEEP_WORKSPACE=1 ;;
  esac
done
unset _arg

if [[ -z "${NO_COLOR}" && -t 1 ]]; then
  BOLD="$(printf '\033[1m')"
  GREEN="$(printf '\033[0;32m')"
  YELLOW="$(printf '\033[0;33m')"
  RED="$(printf '\033[0;31m')"
  BLUE="$(printf '\033[0;34m')"
  RESET="$(printf '\033[0m')"
else
  BOLD=""
  GREEN=""
  YELLOW=""
  RED=""
  BLUE=""
  RESET=""
fi

agentguard_missing() {
  cat >&2 <<'EOF'
AgentGuard CLI was not found.

This showcase is a consumer of the private AgentGuard core. It does not
vendor the authorization engine, cryptography, or ledger implementation.

Expected local evaluator layout:

  <parent>/
    agentguard/              # core checkout with a working install
    agentguard-showcase/     # this repository

Then either:

  export AGENTGUARD=/path/to/agentguard/.venv/bin/agentguard

or, from this repository:

  ./scripts/bootstrap.sh --install

The public `pip install agentguard` name is not assumed to be this project.
EOF
  return 1
}

agentguard_discover() {
  AGENTGUARD_BIN=""
  AGENTGUARD_PYTHON="${PYTHON:-python3}"
  AGENTGUARD_MODULE=0

  local candidate
  if [[ -n "${AGENTGUARD:-}" ]]; then
    if [[ -x "${AGENTGUARD}" ]]; then
      AGENTGUARD_BIN="${AGENTGUARD}"
    elif command -v "${AGENTGUARD}" >/dev/null 2>&1; then
      AGENTGUARD_BIN="$(command -v "${AGENTGUARD}")"
    else
      printf 'AGENTGUARD is set but is not executable: %s\n' "${AGENTGUARD}" >&2
      return 1
    fi
  elif command -v agentguard >/dev/null 2>&1; then
    AGENTGUARD_BIN="$(command -v agentguard)"
  else
    candidate="$(cd "${SHOWCASE_ROOT}/.." && pwd)/agentguard/.venv/bin/agentguard"
    if [[ -x "${candidate}" ]]; then
      AGENTGUARD_BIN="${candidate}"
    elif [[ -x "${SHOWCASE_ROOT}/.venv/bin/agentguard" ]]; then
      AGENTGUARD_BIN="${SHOWCASE_ROOT}/.venv/bin/agentguard"
    elif "${AGENTGUARD_PYTHON}" -c "import agentguard, sys; sys.exit(0)" >/dev/null 2>&1; then
      AGENTGUARD_MODULE=1
    else
      return 1
    fi
  fi

  if [[ -n "${AGENTGUARD_BIN}" ]]; then
    local bindir
    bindir="$(cd "$(dirname "${AGENTGUARD_BIN}")" && pwd)"
    AGENTGUARD_BIN="${bindir}/$(basename "${AGENTGUARD_BIN}")"
    if [[ -x "${bindir}/python" ]]; then
      AGENTGUARD_PYTHON="${bindir}/python"
    fi
  fi
}

ag() {
  if [[ -n "${AGENTGUARD_BIN:-}" ]]; then
    "${AGENTGUARD_BIN}" "$@"
  else
    "${AGENTGUARD_PYTHON}" -m agentguard "$@"
  fi
}

agentguard_require() {
  if ! agentguard_discover; then
    agentguard_missing
    return 1
  fi
  local version
  version="$(ag --version 2>/dev/null || true)"
  if [[ -z "${version}" ]]; then
    printf 'AgentGuard was located but --version failed.\n' >&2
    agentguard_missing
    return 1
  fi
  printf '%sCLI:%s %s\n' "${BOLD}" "${RESET}" "${version}"
  if [[ -n "${AGENTGUARD_BIN}" ]]; then
    printf '%sPath:%s %s\n' "${BOLD}" "${RESET}" "${AGENTGUARD_BIN}"
  else
    printf '%sPath:%s %s -m agentguard\n' "${BOLD}" "${RESET}" "${AGENTGUARD_PYTHON}"
  fi
}

make_workspace() {
  local prefix="${1:-agentguard-showcase}"
  # AgentGuard refuses paths with symlink components. On macOS /tmp and /var
  # are symlinks, so workspaces stay inside this repository (gitignored).
  local root="${SHOWCASE_ROOT}/.showcase-workspaces"
  mkdir -p "${root}"
  WORKSPACE="$(mktemp -d "${root}/${prefix}.XXXXXX")"
  showcase_cleanup() {
    if [[ "${KEEP_WORKSPACE}" -eq 1 ]]; then
      printf '%sWorkspace preserved:%s %s\n' "${YELLOW}" "${RESET}" "${WORKSPACE}"
    else
      rm -rf "${WORKSPACE}"
    fi
  }
  trap showcase_cleanup EXIT
}

require_reason() {
  local output="$1"
  local reason="$2"
  if printf '%s' "${output}" | grep -Fq "${reason}"; then
    return 0
  fi
  printf '%sExpected reason code not observed: %s%s\n' "${RED}" "${reason}" "${RESET}" >&2
  printf '%sAgentGuard output:%s\n%s\n' "${BOLD}" "${RESET}" "${output}" >&2
  return 1
}

require_status() {
  local status="$1"
  local expected="$2"
  local context="$3"
  if [[ "${status}" -eq "${expected}" ]]; then
    return 0
  fi
  printf '%s%s: expected exit %s, got %s%s\n' "${RED}" "${context}" "${expected}" "${status}" "${RESET}" >&2
  return 1
}
