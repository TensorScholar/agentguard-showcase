"""Post-authorization argument mutation.

Threat: after a receipt is issued for $85, an attacker (or a compromised
orchestrator) presents the same receipt with $850 arguments.

Expected: execution.arguments_digest_mismatch, executor never called.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.policy import evaluate_policy
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

SECRET = b"reference-kernel-demo-key-not-for-production"


@dataclass
class AttackResult:
    name: str
    blocked: bool
    reason_code: str
    executor_calls: int


def run() -> AttackResult:
    store = ReplayStore()
    args_valid = {"order_id": "ord_123", "amount_minor": 8500, "currency": "USD"}
    decision = evaluate_policy(
        action="refund.create",
        arguments=args_valid,
        principal="support-agent-v3",
        max_amount_minor=10_000,
    )
    assert decision.effect == "allow"
    receipt = make_receipt(
        principal="support-agent-v3",
        action="refund.create",
        arguments_digest=arguments_digest(args_valid),
        policy_revision=decision.policy_revision,
        max_amount_minor=decision.max_amount_minor or 10_000,
    )
    sig = sign_receipt(receipt, SECRET)
    mutated = {"order_id": "ord_123", "amount_minor": 85000, "currency": "USD"}
    calls = []
    result = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=mutated,
        replay_store=store,
        executor=lambda a: calls.append(a),
    )
    return AttackResult(
        name="argument_mutation",
        blocked=not result.allowed and result.reason_code == "execution.arguments_digest_mismatch",
        reason_code=result.reason_code,
        executor_calls=len(calls),
    )
