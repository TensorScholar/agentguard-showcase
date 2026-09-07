#!/usr/bin/env bash
# Replay prevention: consume a receipt once, then reject reuse.
# Authorization uses the AgentGuard CLI. Consumption uses AgentGuard's
# protected execution API because verify-execution is a non-consuming preflight.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/lib.sh
. "${SCRIPT_DIR}/../../scripts/lib.sh"

agentguard_require
make_workspace "agentguard-replay"

POLICY="${SCRIPT_DIR}/../refund-agent/policy.yaml"
REQUEST="${SCRIPT_DIR}/../refund-agent/request_valid.json"
RECEIPT="${WORKSPACE}/receipt.json"
GRANT="${WORKSPACE}/grant.json"
LEDGER="${WORKSPACE}/audit.sqlite"
RESULT="${WORKSPACE}/replay-result.json"

printf '\n%sAgentGuard Showcase — Replay prevention%s\n\n' "${BOLD}${BLUE}" "${RESET}"
printf 'Expected second-use reason: decision_receipt.replayed\n\n'

printf '%s[1/4] init + authorize + bounded grant%s\n' "${BOLD}" "${RESET}"
ag init --output "${WORKSPACE}" --force >/dev/null
ag authorize \
  "${REQUEST}" \
  "${POLICY}" \
  --key "${WORKSPACE}/decision-private.pem" \
  --ledger "${LEDGER}" \
  --output "${RECEIPT}"
ag broker-demo \
  "${REQUEST}" \
  "${RECEIPT}" \
  --decision-key "${WORKSPACE}/decision-private.pem" \
  --broker-key "${WORKSPACE}/broker-private.pem" \
  --ledger "${LEDGER}" \
  --output "${GRANT}"
printf '%sauthorization material issued%s\n\n' "${GREEN}" "${RESET}"

printf '%s[2/4] verify-execution remains non-consuming%s\n' "${BOLD}" "${RESET}"
ag verify-execution \
  "${REQUEST}" \
  "${RECEIPT}" \
  "${POLICY}" \
  --grant "${GRANT}" \
  --public-key "${WORKSPACE}/decision-public.pem" \
  --broker-public-key "${WORKSPACE}/broker-public.pem" \
  --ledger "${LEDGER}"
printf '%spreflight does not claim the receipt%s\n\n' "${GREEN}" "${RESET}"

printf '%s[3/4] first protected use, then replay%s\n' "${BOLD}" "${RESET}"
"${AGENTGUARD_PYTHON}" "${SCRIPT_DIR}/protected_consume.py" \
  --request "${REQUEST}" \
  --receipt "${RECEIPT}" \
  --policy "${POLICY}" \
  --grant "${GRANT}" \
  --decision-key "${WORKSPACE}/decision-private.pem" \
  --public-key "${WORKSPACE}/decision-public.pem" \
  --broker-public-key "${WORKSPACE}/broker-public.pem" \
  --ledger "${LEDGER}" | tee "${RESULT}"

printf '\n%s[4/4] assert replay reason%s\n' "${BOLD}" "${RESET}"
require_reason "$(cat "${RESULT}")" "decision_receipt.replayed"

printf '\n%sReplay prevention%s\n' "${BOLD}" "${RESET}"
printf '  first protected use          PASS\n'
printf '  second use rejected          PASS (%s)\n' "decision_receipt.replayed"
printf '\nThe executor is AgentGuard'\''s in-process fake executor.\n'
printf 'This proves receipt consumption on the protected path, not a live provider call.\n'
