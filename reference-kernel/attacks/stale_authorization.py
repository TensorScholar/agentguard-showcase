"""Stale authorization: expired receipt presented after its TTL.

Threat: a legitimate receipt is captured and presented after expiry
(e.g. delayed queue redelivery, attacker-held receipt replayed late).

Expected: execution.receipt_expired, executor never called — even though
the signature is valid, the digest matches, and the receipt was never
consumed. Expiry is checked before digest and consumption so a stale
receipt cannot burn a single-use slot or reach the executor.

Boundary: TTL enforcement assumes trustworthy local time. Clock skew or
an attacker-controlled clock is out of scope for this kernel.
"""

from __future__ import annotations

import time

from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

from .argument_mutation import SECRET
from .framework import ScenarioResult, register, ScenarioSpec

EXPECTED = ("execution.receipt_expired",)


def run() -> ScenarioResult:
    store = ReplayStore()
    args = {"order_id": "ord_stale_1", "amount_minor": 2000, "currency": "USD"}
    receipt = make_receipt(
        principal="support-agent-v3",
        action="refund.create",
        arguments_digest=arguments_digest(args),
        policy_revision="ref-1",
        max_amount_minor=10_000,
        ttl_seconds=60,
        issued_at=time.time() - 3600,  # issued one hour ago, TTL 60s
    )
    sig = sign_receipt(receipt, SECRET)
    calls: list = []
    result = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=args,
        replay_store=store,
        executor=lambda a: calls.append(a),
    )
    blocked = (not result.allowed) and result.reason_code in EXPECTED
    return ScenarioResult(
        name="stale_authorization",
        threat="expired receipt presented after TTL",
        blocked=blocked,
        reason_code=result.reason_code,
        executor_calls=len(calls),
        expected_reason_codes=EXPECTED,
        notes="Signature valid, digest matches, never consumed — expiry still fails closed.",
    )


register(
    ScenarioSpec(
        name="stale_authorization",
        threat="expired receipt presented after TTL",
        expected_reason_codes=EXPECTED,
        run=run,
    )
)
