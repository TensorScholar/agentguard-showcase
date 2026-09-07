"""Replay of a consumed decision receipt.

Threat: a valid receipt is used once, then presented again on the same
durable state boundary.

Expected: first call allowed, second call decision_receipt.replayed,
executor called exactly once.
"""

from __future__ import annotations

from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

from .argument_mutation import SECRET, AttackResult


def run() -> AttackResult:
    store = ReplayStore()
    args = {"order_id": "ord_9", "amount_minor": 1000, "currency": "USD"}
    receipt = make_receipt(
        principal="support-agent-v3",
        action="refund.create",
        arguments_digest=arguments_digest(args),
        policy_revision="ref-1",
        max_amount_minor=10_000,
    )
    sig = sign_receipt(receipt, SECRET)
    calls: list = []

    def ex(a):
        calls.append(a)

    first = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=args,
        replay_store=store,
        executor=ex,
    )
    second = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=args,
        replay_store=store,
        executor=ex,
    )
    blocked = (
        first.allowed
        and not second.allowed
        and second.reason_code == "decision_receipt.replayed"
        and len(calls) == 1
    )
    return AttackResult(
        name="replay_attack",
        blocked=blocked,
        reason_code=second.reason_code,
        executor_calls=len(calls),
    )
