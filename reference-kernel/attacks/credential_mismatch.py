"""Credential that exceeds or detaches from the receipt.

Threat: a credential is presented whose audience or amount ceiling is
not dominated by the authorizing receipt.

Expected: fail closed with credential.* reason, executor never called.
"""

from __future__ import annotations

from dataclasses import replace

from core.credential import issue_credential, sign_credential
from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

from .argument_mutation import SECRET, AttackResult


def run() -> AttackResult:
    store = ReplayStore()
    args = {"order_id": "ord_7", "amount_minor": 5000, "currency": "USD"}
    receipt = make_receipt(
        principal="support-agent-v3",
        action="refund.create",
        arguments_digest=arguments_digest(args),
        policy_revision="ref-1",
        max_amount_minor=10_000,
        audience="payments.internal",
    )
    rsig = sign_receipt(receipt, SECRET)
    cred, _csig = issue_credential(receipt, SECRET)
    # Attacker widens the ceiling after issuance
    forged = replace(cred, max_amount_minor=1_000_000)
    forged_sig = sign_credential(forged, SECRET)
    calls: list = []
    result = execute_protected(
        receipt=receipt,
        receipt_signature=rsig,
        secret=SECRET,
        live_arguments=args,
        replay_store=store,
        credential=forged,
        credential_signature=forged_sig,
        executor=lambda a: calls.append(a),
    )
    return AttackResult(
        name="credential_mismatch",
        blocked=not result.allowed
        and result.reason_code == "credential.ceiling_exceeds_receipt"
        and len(calls) == 0,
        reason_code=result.reason_code,
        executor_calls=len(calls),
    )
