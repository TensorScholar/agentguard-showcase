#!/usr/bin/env python3
"""AgentGuard quickstart: authorize $85, execute $85 (allowed), replay it (blocked).

Run from the repository root:  python3 examples/quickstart.py
Stdlib only. Educational kernel; no payment processor is contacted.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "reference-kernel"))

from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.policy import evaluate_policy
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

SECRET = b"quickstart-demo-key-not-for-production"


def main() -> None:
    args = {"order_id": "ord_demo", "amount_minor": 8500, "currency": "USD"}
    decision = evaluate_policy(
        action="refund.create", arguments=args,
        principal="demo-agent", max_amount_minor=10_000,
    )
    print(f"policy: {decision.effect} ({decision.reason_code})")

    receipt = make_receipt(
        principal="demo-agent", action="refund.create",
        arguments_digest=arguments_digest(args),
        policy_revision=decision.policy_revision,
        max_amount_minor=decision.max_amount_minor or 10_000,
    )
    sig = sign_receipt(receipt, SECRET)
    store = ReplayStore()
    calls: list = []

    first = execute_protected(receipt=receipt, receipt_signature=sig, secret=SECRET,
                              live_arguments=args, replay_store=store,
                              executor=lambda a: calls.append(a))
    print(f"first execution: allowed={first.allowed} ({first.reason_code}), executor_calls={len(calls)}")

    mutated = {**args, "amount_minor": 85000}
    second = execute_protected(receipt=receipt, receipt_signature=sig, secret=SECRET,
                               live_arguments=mutated, replay_store=ReplayStore(),
                               executor=lambda a: calls.append(a))
    print(f"mutated replay: allowed={second.allowed} ({second.reason_code}), executor_calls={len(calls)}")
    print("No payment processor was contacted. See experiments/ for the full 6-scenario suite.")


if __name__ == "__main__":
    main()
