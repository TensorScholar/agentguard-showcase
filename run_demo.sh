#!/usr/bin/env bash
# Run the three AgentGuard demonstrations and print a summary.
# PASS is printed only when the underlying real demo exited 0.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib.sh
. "${SCRIPT_DIR}/scripts/lib.sh"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Usage: ./run_demo.sh [--keep-workspace]

Runs:
  1. demos/refund-agent
  2. demos/replay-prevention
  3. demos/mcp-security

PASS is printed only when that demo exited 0 after checking real AgentGuard output.
EOF
  exit 0
fi

agentguard_require

pass() { printf '%sPASS%s' "${GREEN}" "${RESET}"; }
fail() { printf '%sFAIL%s' "${RED}" "${RESET}"; }

run_one() {
  local name="$1"
  local script="$2"
  shift 2
  local status=0
  printf '\n%s======== %s ========%s\n' "${BOLD}" "${name}" "${RESET}"
  "${script}" "$@" || status=$?
  return "${status}"
}

REFUND_STATUS=0
REPLAY_STATUS=0
MCP_STATUS=0

set +e
run_one "Refund mutation" "${SCRIPT_DIR}/demos/refund-agent/run.sh" "$@"
REFUND_STATUS=$?
run_one "Replay prevention" "${SCRIPT_DIR}/demos/replay-prevention/run.sh" "$@"
REPLAY_STATUS=$?
run_one "MCP bypass detection" "${SCRIPT_DIR}/demos/mcp-security/run.sh" "$@"
MCP_STATUS=$?
set -e

OVERALL="PASS"
OVERALL_STATUS=0
if [[ "${REFUND_STATUS}" -ne 0 || "${REPLAY_STATUS}" -ne 0 || "${MCP_STATUS}" -ne 0 ]]; then
  OVERALL="FAIL"
  OVERALL_STATUS=1
fi

refund_label="$(pass)"; [[ "${REFUND_STATUS}" -eq 0 ]] || refund_label="$(fail)"
replay_label="$(pass)"; [[ "${REPLAY_STATUS}" -eq 0 ]] || replay_label="$(fail)"
mcp_label="$(pass)"; [[ "${MCP_STATUS}" -eq 0 ]] || mcp_label="$(fail)"
if [[ "${OVERALL}" == "PASS" ]]; then
  overall_label="$(pass)"
else
  overall_label="$(fail)"
fi

printf '\n%sAgentGuard Reference Demos%s\n\n' "${BOLD}" "${RESET}"
printf 'Refund mutation         %s\n' "${refund_label}"
printf 'Replay prevention       %s\n' "${replay_label}"
printf 'MCP bypass detection    %s\n' "${mcp_label}"
printf '\nOverall                 %s\n' "${overall_label}"

exit "${OVERALL_STATUS}"
