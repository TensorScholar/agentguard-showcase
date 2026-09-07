"""Tests for v4 scenarios: stale authorization and privilege escalation."""

from __future__ import annotations

import time
from dataclasses import replace

from core.credential import issue_credential, sign_credential
from core.digest import arguments_digest
from core.executor_boundary import execute_protected
from core.policy import evaluate_policy
from core.receipt import make_receipt, sign_receipt
from core.replay import ReplayStore

SECRET = b"test-secret-key"


def _receipt(args, **kw):
    return make_receipt(
        principal="agent",
        action="refund.create",
        arguments_digest=arguments_digest(args),
        policy_revision="1",
        max_amount_minor=10_000,
        **kw,
    )


def test_expired_receipt_fails_closed_even_with_valid_signature():
    args = {"amount_minor": 2000, "order_id": "stale"}
    receipt = _receipt(args, ttl_seconds=60, issued_at=time.time() - 3600)
    sig = sign_receipt(receipt, SECRET)
    calls = []
    result = execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=args,
        replay_store=ReplayStore(),
        executor=lambda a: calls.append(a),
    )
    assert result.allowed is False
    assert result.reason_code == "execution.receipt_expired"
    assert calls == []


def test_expiry_checked_before_consumption():
    """A stale receipt must not burn its single-use slot."""
    args = {"amount_minor": 2000, "order_id": "stale2"}
    receipt = _receipt(args, ttl_seconds=60, issued_at=time.time() - 3600)
    sig = sign_receipt(receipt, SECRET)
    store = ReplayStore()
    execute_protected(
        receipt=receipt,
        receipt_signature=sig,
        secret=SECRET,
        live_arguments=args,
        replay_store=store,
        executor=lambda a: None,
    )
    assert not store.is_consumed(receipt.receipt_id)


def test_escalated_action_denied_at_policy():
    d = evaluate_policy(
        action="wire.transfer",
        arguments={"amount_minor": 100},
        principal="agent",
        allowed_actions={"refund.create"},
    )
    assert d.effect == "deny"
    assert d.reason_code == "policy.unknown_action"


def test_forged_audience_rejected_at_gate():
    args = {"amount_minor": 1000, "order_id": "esc"}
    receipt = _receipt(args, audience="payments.internal")
    rsig = sign_receipt(receipt, SECRET)
    cred, _ = issue_credential(receipt, SECRET)
    forged = replace(cred, audience="treasury.internal")
    result = execute_protected(
        receipt=receipt,
        receipt_signature=rsig,
        secret=SECRET,
        live_arguments=args,
        replay_store=ReplayStore(),
        credential=forged,
        credential_signature=sign_credential(forged, SECRET),
    )
    assert result.allowed is False
    assert result.reason_code == "credential.audience_mismatch"


def test_attack_registry_covers_required_scenarios():
    from attacks import REQUIRED_SCENARIOS

    assert set(REQUIRED_SCENARIOS) == {
        "argument_mutation",
        "replay_attack",
        "credential_mismatch",
        "stale_authorization",
        "privilege_escalation_attempt",
        "prompt_injection_scenario",
    }


def test_concurrent_double_consume_blocks_one():
    """Same-process concurrent presentation: exactly one execution wins."""
    import threading

    from core.executor_boundary import execute_protected

    args = {"amount_minor": 1000, "order_id": "race"}
    receipt = _receipt(args)
    sig = sign_receipt(receipt, SECRET)
    store = ReplayStore()
    wins: list = []
    lock = threading.Lock()

    def attempt():
        res = execute_protected(
            receipt=receipt,
            receipt_signature=sig,
            secret=SECRET,
            live_arguments=args,
            replay_store=store,
            executor=lambda a: None,
        )
        if res.allowed:
            with lock:
                wins.append(1)

    threads = [threading.Thread(target=attempt) for _ in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(wins) == 1
