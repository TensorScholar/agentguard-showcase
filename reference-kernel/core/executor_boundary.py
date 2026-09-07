"""Execution gate.

The only path that may produce a side effect on a protected action.

Order of checks is load-bearing:
1. Receipt signature
2. Receipt expiry
3. Live arguments digest vs receipt digest
4. Credential bound to this receipt (audience, ceiling, signature)
5. Single-use consumption
6. Only then the executor is invoked
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .credential import Credential, verify_credential_against_receipt
from .digest import arguments_digest
from .receipt import DecisionReceipt, verify_receipt
from .replay import ReplayError, ReplayStore


@dataclass
class ExecutionResult:
    allowed: bool
    reason_code: str
    executor_called: bool = False


def execute_protected(
    *,
    receipt: DecisionReceipt,
    receipt_signature: str,
    secret: bytes,
    live_arguments: dict[str, Any],
    replay_store: ReplayStore,
    credential: Credential | None = None,
    credential_signature: str | None = None,
    executor: Callable[[dict[str, Any]], None] | None = None,
) -> ExecutionResult:
    if not verify_receipt(receipt, receipt_signature, secret):
        return ExecutionResult(allowed=False, reason_code="execution.invalid_signature")

    if receipt.is_expired():
        return ExecutionResult(allowed=False, reason_code="execution.receipt_expired")

    live_digest = arguments_digest(live_arguments)
    if live_digest != receipt.arguments_digest:
        return ExecutionResult(allowed=False, reason_code="execution.arguments_digest_mismatch")

    amount = int(live_arguments.get("amount_minor", 0))
    if amount > receipt.max_amount_minor:
        return ExecutionResult(allowed=False, reason_code="execution.amount_exceeds_receipt")

    if credential is not None:
        if credential_signature is None:
            return ExecutionResult(allowed=False, reason_code="credential.missing_signature")
        cred_fail = verify_credential_against_receipt(
            credential, credential_signature, secret, receipt
        )
        if cred_fail is not None:
            return ExecutionResult(allowed=False, reason_code=cred_fail)
        if amount > credential.max_amount_minor:
            return ExecutionResult(allowed=False, reason_code="credential.amount_exceeds_ceiling")

    if receipt.single_use:
        if replay_store.is_consumed(receipt.receipt_id):
            return ExecutionResult(allowed=False, reason_code="decision_receipt.replayed")
        try:
            replay_store.consume(receipt.receipt_id)
        except ReplayError:
            return ExecutionResult(allowed=False, reason_code="decision_receipt.replayed")

    if executor is not None:
        executor(live_arguments)

    return ExecutionResult(allowed=True, reason_code="execution.allowed", executor_called=True)
