#!/usr/bin/env bash
# Refund mutation demo: authorize $85, then reject a mutated $850 execution.
# All PASS/DENY results come from the AgentGuard CLI.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/lib.sh
. "${SCRIPT_DIR}/../../scripts/lib.sh"

agentguard_require
make_workspace "agentguard-refund"

POLICY="${SCRIPT_DIR}/policy.yaml"
VALID="${SCRIPT_DIR}/request_valid.json"
MUTATED="${SCRIPT_DIR}/request_mutated.json"
RECEIPT="${WORKSPACE}/receipt.json"
GRANT="${WORKSPACE}/grant.json"
LEDGER="${WORKSPACE}/audit.sqlite"

printf '\n%sAgentGuard Showcase — Refund mutation%s\n\n' "${BOLD}${BLUE}" "${RESET}"
printf 'Authorized intent:  $85.00  (amount_minor=8500)\n'
printf 'Mutated execution:  $850.00 (amount_minor=85000)\n'
printf 'Expected reason:    execution.arguments_digest_mismatch\n\n'

printf '%s[1/5] init%s\n' "${BOLD}" "${RESET}"
ag init --output "${WORKSPACE}" --force >/dev/null
printf '%sinitialized workspace%s\n\n' "${GREEN}" "${RESET}"

printf '%s[2/5] authorize valid $85 intent%s\n' "${BOLD}" "${RESET}"
ag authorize \
  "${VALID}" \
  "${POLICY}" \
  --key "${WORKSPACE}/decision-private.pem" \
  --ledger "${LEDGER}" \
  --output "${RECEIPT}"
printf '%sdecision receipt issued%s\n\n' "${GREEN}" "${RESET}"

printf '%s[3/5] broker-demo bounded grant%s\n' "${BOLD}" "${RESET}"
ag broker-demo \
  "${VALID}" \
  "${RECEIPT}" \
  --decision-key "${WORKSPACE}/decision-private.pem" \
  --broker-key "${WORKSPACE}/broker-private.pem" \
  --ledger "${LEDGER}" \
  --output "${GRANT}"
printf '%scredential grant issued (development broker adapter)%s\n\n' "${GREEN}" "${RESET}"

printf '%s[4/5] verify-execution for the authorized $85 action%s\n' "${BOLD}" "${RESET}"
VERIFY_OUT="$(
  ag verify-execution \
    "${VALID}" \
    "${RECEIPT}" \
    "${POLICY}" \
    --grant "${GRANT}" \
    --public-key "${WORKSPACE}/decision-public.pem" \
    --broker-public-key "${WORKSPACE}/broker-public.pem" \
    --ledger "${LEDGER}"
)"
printf '%s\n' "${VERIFY_OUT}"
if ! printf '%s' "${VERIFY_OUT}" | grep -Fq "Execution authority verified"; then
  printf '%sverify-execution did not report execution authority verification%s\n' "${RED}" "${RESET}" >&2
  exit 1
fi
printf '%sexecution authority verified (preflight; nonce not consumed)%s\n\n' "${GREEN}" "${RESET}"

printf '%s[5/5] verify-execution for mutated $850 arguments%s\n' "${BOLD}" "${RESET}"
set +e
MUTATION_OUT="$(
  ag verify-execution \
    "${MUTATED}" \
    "${RECEIPT}" \
    "${POLICY}" \
    --grant "${GRANT}" \
    --public-key "${WORKSPACE}/decision-public.pem" \
    --broker-public-key "${WORKSPACE}/broker-public.pem" \
    --ledger "${LEDGER}" 2>&1
)"
MUTATION_STATUS=$?
set -e

if [[ "${MUTATION_STATUS}" -eq 0 ]]; then
  printf '%sFAILURE: mutated $850 execution was accepted%s\n' "${RED}" "${RESET}" >&2
  printf '%s\n' "${MUTATION_OUT}" >&2
  exit 1
fi
require_reason "${MUTATION_OUT}" "execution.arguments_digest_mismatch"
printf 'AgentGuard rejection:\n'
printf '%s\n' "${MUTATION_OUT}" | grep -E 'Error: |reason' || true
printf 'exit code: %s\n' "${MUTATION_STATUS}"

printf '\n%sRefund mutation%s\n' "${BOLD}" "${RESET}"
printf '  legitimate $85 preflight     PASS\n'
printf '  mutated $850 intercepted     PASS (%s)\n' "execution.arguments_digest_mismatch"
printf '  AgentGuard exit code         %s\n' "${MUTATION_STATUS}"
printf '\nThis step proves execution-authority verification, not that a payment processor was contacted.\n'
printf 'On a protected execution path, dispatch would be blocked for this mutated action.\n'
