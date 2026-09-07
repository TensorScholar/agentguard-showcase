#!/usr/bin/env bash
# MCP posture: protected configuration passes, bypass configuration fails closed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/lib.sh
. "${SCRIPT_DIR}/../../scripts/lib.sh"

agentguard_require

PROTECTED="${SCRIPT_DIR}/protected.json"
BYPASS="${SCRIPT_DIR}/bypass.json"
ASSERT="${SCRIPT_DIR}/assert_posture.py"

printf '\n%sAgentGuard Showcase — MCP posture%s\n\n' "${BOLD}${BLUE}" "${RESET}"
printf 'This demo audits MCP client configuration. It does not make MCP servers invulnerable.\n\n'

printf '%s[1/2] protected configuration%s\n' "${BOLD}" "${RESET}"
PROTECTED_JSON="$(ag mcp-posture --config "${PROTECTED}" --format json --fail-on-bypass)"
printf '%s\n' "${PROTECTED_JSON}"
printf '%s' "${PROTECTED_JSON}" | "${AGENTGUARD_PYTHON}" "${ASSERT}" protected
printf '%sprotected posture exit 0%s\n\n' "${GREEN}" "${RESET}"

printf '%s[2/2] bypass / unmediated configuration%s\n' "${BOLD}" "${RESET}"
set +e
BYPASS_JSON="$(ag mcp-posture --config "${BYPASS}" --format json --fail-on-bypass 2>&1)"
BYPASS_STATUS=$?
set -e
printf '%s\n' "${BYPASS_JSON}"
if [[ "${BYPASS_STATUS}" -eq 0 ]]; then
  printf '%sFAILURE: bypass configuration was accepted%s\n' "${RED}" "${RESET}" >&2
  exit 1
fi
printf '%s' "${BYPASS_JSON}" | "${AGENTGUARD_PYTHON}" "${ASSERT}" bypass
require_reason "${BYPASS_JSON}" "mcp.direct_connection_bypasses_agentguard"
require_reason "${BYPASS_JSON}" "mcp.parallel_direct_bypass"

printf '\n%sMCP posture%s\n' "${BOLD}" "${RESET}"
printf '  protected configuration      PASS\n'
printf '  bypass configuration         PASS (exit %s)\n' "${BYPASS_STATUS}"
printf '  reasons                      mcp.direct_connection_bypasses_agentguard,\n'
printf '                               mcp.parallel_direct_bypass\n'
